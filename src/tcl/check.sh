#!/usr/bin/env bash
# Comprueba las reglas del reto para la entrada de Tcl. Usa una carpeta de datos desechable.
# Define TCLSH=/ruta/a/tclsh si no está en tu PATH. Necesita Tcl 8.6 y su paquete sqlite3.
# La ventana de Tk se prueba solo si hay Xvfb (o una pantalla); si no, ese paso se omite y lo avisa.
set -euo pipefail
cd "$(dirname "$0")"
data=$(mktemp -d); trap 'rm -rf "$data"' EXIT
export XDG_DATA_HOME=$data
db=$data/Tcl/demo-timecards.db
tclsh=${TCLSH:-tclsh}
run() { "$tclsh" timecards.tcl "$@"; }

# 1. Estático: el aviso está ahí, nada toca una red, el reto es un único bucle while en
#    "draw", y todo expr lleva llaves (un expr sin llaves es más lento y un clásico agujero de inyección).
grep -q 'DEMO ONLY' timecards.tcl || { echo "FAIL: no DEMO ONLY marker in timecards.tcl"; exit 1; }
if grep -Eqi 'http|socket|curl|wget|exec ' timecards.tcl; then echo "FAIL: network or process text in timecards.tcl"; exit 1; fi
sed -n '/^proc timecards::draw/,/^}/p' timecards.tcl | grep -q 'while {\$total <= \$limit}' || { echo "FAIL: draw has no while loop on the limit"; exit 1; }
if grep -E '(^|[^a-z])expr [^{]' timecards.tcl | grep -v '^ *#' | grep -q .; then echo "FAIL: unbraced expr"; exit 1; fi
cat > "$data/complete.tcl" <<'EOF'
set f [open timecards.tcl]; set src [read $f]; close $f
if {![info complete $src]} {puts "incomplete script"; exit 1}
EOF
"$tclsh" "$data/complete.tcl" || { echo "FAIL: timecards.tcl is not a complete Tcl script"; exit 1; }

# 2. Prueba unitaria de draw en un solo proceso (carga el archivo con source: main solo corre si es el script):
#    2000 repartos, y cada uno debe cumplir todas las reglas del reto.
"$tclsh" <<'EOF' || { echo "FAIL: draw broke a rule"; exit 1; }
source timecards.tcl
set cats {Meetings Coding Debugging Learning}
for {set i 0} {$i < 2000} {incr i} {
    set cards [timecards::draw]
    set sum 0
    set n 0
    foreach card $cards {
        dict with card {
            if {$hours < 10 || $hours > 19} {error "hours $hours out of range"}
            if {$sum > 40} {error "kept going after passing 40"}
            incr sum $hours
            if {$total != $sum} {error "running total $total, wanted $sum"}
            if {$category ne [lindex $cats [expr {$n % 4}]]} {error "category $category at $n"}
        }
        incr n
    }
    if {$sum <= 40} {error "stopped at $sum"}
    if {[llength $cards] < 3 || [llength $cards] > 5} {error "[llength $cards] cards"}
}
EOF

# 3. La ventana de Tk, sin pantalla: necesita Xvfb (preferible, para no tocar una pantalla real) o un DISPLAY.
if command -v xvfb-run >/dev/null && command -v Xvfb >/dev/null; then
    runner=(xvfb-run -a)
elif [[ -n ${DISPLAY:-} ]]; then
    runner=()
else
    runner=(skip)
fi
if [[ ${runner[0]:-} == skip ]]; then
    echo "gui: SKIPPED (no Xvfb and no DISPLAY)"
else
    out=$(timeout 60 "${runner[@]}" "$tclsh" timecards.tcl --gui --seconds 1) || { echo "FAIL: --gui run failed or hung"; exit 1; }
    grep -q '^# committed' <<<"$out" || { echo "FAIL: --gui run printed no summary"; exit 1; }
    echo "gui: ok"
fi
rm -rf "$data/Tcl"

# 4. Ejecútalo muchas veces de verdad; cada ejecución debe imprimir un conjunto de registros coherente, y las filas de SQLite deben coincidir.
cats=(Meetings Coding Debugging Learning)
for i in $(seq 1 25); do
    out=$(run)
    run_id=$(sed -nE 's/^# DEMO ONLY run (.+)$/\1/p' <<<"$out")
    [[ -n $run_id ]] || { echo "FAIL run $i: no run id"; echo "$out"; exit 1; }
    commit=$(grep '^# committed' <<<"$out" || true)
    [[ -n $commit ]] || { echo "FAIL run $i: no committed line"; echo "$out"; exit 1; }
    total=$(sed -E 's/.*total=([0-9]+).*/\1/' <<<"$commit")
    entries=$(sed -E 's/.*entries=([0-9]+).*/\1/' <<<"$commit")
    mapfile -t rows < <(grep -E '^(Meetings|Coding|Debugging|Learning)	' <<<"$out" || true)
    [[ ${#rows[@]} -eq $entries ]] || { echo "FAIL run $i: ${#rows[@]} rows but entries=$entries"; exit 1; }
    sum=0; n=0
    for row in "${rows[@]}"; do
        IFS=$'\t' read -r cat hours running week mark <<<"$row"
        [[ $cat == "${cats[n % 4]}" ]] || { echo "FAIL run $i: row $n is $cat, wanted ${cats[n % 4]}"; exit 1; }
        (( hours >= 10 && hours <= 19 )) || { echo "FAIL run $i: hours $hours out of 10-19"; exit 1; }
        (( sum <= 40 )) || { echo "FAIL run $i: kept going after the total passed 40"; exit 1; }
        sum=$(( sum + hours )); n=$(( n + 1 ))
        (( running == sum )) || { echo "FAIL run $i: running total $running, wanted $sum"; exit 1; }
        [[ $week =~ ^[0-9]{4}-W[0-9]{2}$ ]] || { echo "FAIL run $i: bad ISO week '$week'"; exit 1; }
        [[ $mark == "DEMO ONLY" ]] || { echo "FAIL run $i: row not marked DEMO ONLY"; exit 1; }
    done
    (( sum == total && sum > 40 )) || { echo "FAIL run $i: stopped at $sum (summary says $total); must stop once over 40"; exit 1; }
    db_row=$(sqlite3 "$db" "select count(*) || ' ' || coalesce(sum(hours),0) || ' ' || coalesce(min(demo_only),0) || coalesce(max(demo_only),0) from demo_timecards where run_id = '$run_id'")
    [[ $db_row == "$entries $total 11" ]] || { echo "FAIL run $i: db says '$db_row', output says '$entries $total 11'"; exit 1; }
    db_rows=$(sqlite3 -separator $'\t' "$db" "select category, hours, running_total, iso_week from demo_timecards where run_id = '$run_id' order by id")
    [[ $db_rows == "$(printf '%s\n' "${rows[@]}" | cut -f1-4)" ]] || { echo "FAIL run $i: db rows differ from the printed rows"; exit 1; }
done
[[ $(sqlite3 "$db" 'select count(distinct run_id) from demo_timecards') -eq 25 ]] || { echo "FAIL: expected 25 distinct runs in the db"; exit 1; }
[[ $(sqlite3 "$db" 'select count(distinct hours) from demo_timecards') -ge 6 ]] || { echo "FAIL: hours do not look random"; exit 1; }

# 3. La restricción CHECK de demo_only es real: una fila que no sea de demostración debe ser rechazada.
if sqlite3 "$db" "insert into demo_timecards(run_id,category,hours,running_total,demo_only) values('x','x',1,1,0)" 2>/dev/null; then
    echo "FAIL: db accepted a non-demo row"; exit 1
fi
echo "OK: 2000 deals obey every rule; 25 real runs stopped when they should, committed to SQLite, all marked DEMO ONLY"
