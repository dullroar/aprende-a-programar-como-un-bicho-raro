#!/usr/bin/env bash
# Comprueba las reglas del reto para la entrada de AWK "rara". Usa un directorio de datos desechable.
# Solo GNU awk (RT, RS como expresión regular, systime, PROCINFO). Define GAWK=/ruta/a/gawk si no está en tu PATH.
set -euo pipefail
cd "$(dirname "$0")"
data=$(mktemp -d); trap 'rm -rf "$data"' EXIT
export XDG_DATA_HOME=$data
db=$data/AwkWeird/demo-timecards.db
gawk=${GAWK:-gawk}
run() { "$gawk" -f "${PROGRAM:-timecards.awk}" "$@"; }
rows() { grep -E '^(Meetings|Coding|Debugging|Learning)	' || true; }

# 1. Estático: el truco es real. Sin los comentarios no hay bucle, ni if, ni función, ni
#    función aleatoria; el separador de registros es la clase de dígitos; y la regla de parada es un patrón.
grep -q 'DEMO ONLY' timecards.awk || { echo "FAIL: no DEMO ONLY marker in timecards.awk"; exit 1; }
if grep -Eqi 'http|socket|curl|wget|/inet/' timecards.awk; then echo "FAIL: network-looking text in timecards.awk"; exit 1; fi
code=$(sed -E -e '/^ *#/d' -e 's/  +#.*//' timecards.awk)
forbidden='(^|[^A-Za-z_])(while|for|do|if|function|switch|rand|srand)[ (]'
if grep -Eq "$forbidden" <<<"$code"; then
    echo "FAIL: a loop, if, function or random function appears in the program"; grep -nE "$forbidden" <<<"$code"; exit 1
fi
grep -q 'RS = "\[0-9\]"' <<<"$code" || { echo "FAIL: RS is not the digit class"; exit 1; }
grep -q '^t > 40 { exit }$' <<<"$code" || { echo "FAIL: the stop rule is not a bare pattern with an exit action"; exit 1; }
grep -q '/dev/urandom' <<<"$code" || { echo "FAIL: the default input is not /dev/urandom"; exit 1; }

# 2. Los dados son los dígitos de la entrada. Alimenta archivos de dígitos con formas incómodas (espacios, saltos de línea, nada,
#    letras entre ellos) y compara con un cálculo independiente en bash, tarjeta por tarjeta.
cats=(Meetings Coding Debugging Learning)
expected() {   # dígitos -> las filas como debería imprimirlas el programa, luego una línea de resumen
    local digits=$1 total=0 n=0 d hours i
    for (( i = 0; i < ${#digits} && total <= 40; i++ )); do
        d=${digits:i:1}; hours=$(( 10 + d )); total=$(( total + hours ))
        printf '%s\t%d\t%d\n' "${cats[n % 4]}" "$hours" "$total"; n=$(( n + 1 ))
    done
    printf 'SUMMARY total=%d entries=%d\n' "$total" "$n"
}
# Lo que imprimió el programa, con la misma forma que expected().
shape() { local out=$1; rows <<<"$out" | cut -f1-3; sed -nE 's/^# committed (total=[0-9]+ entries=[0-9]+) DEMO ONLY$/SUMMARY \1/p' <<<"$out"; }
for trial in $(seq 1 30); do
    digits=""; for _ in $(seq 1 12); do digits+=$(( RANDOM % 10 )); done
    case $(( trial % 4 )) in
        0) printf '%s' "$digits" > "$data/in.txt" ;;            # sin ningún separador
        1) printf '%s\n' "$digits" > "$data/in.txt" ;;          # salto de línea final: un último registro vacío
        2) sed 's/./& /g' <<<"$digits" > "$data/in.txt" ;;      # espacios entre ellos
        3) sed 's/./x&\n/g' <<<"$digits" > "$data/in.txt" ;;    # letras y saltos de línea entre ellos
    esac
    want=$(expected "$digits")
    got=$(shape "$(run "$data/in.txt")")
    [[ $got == "$want" ]] || { echo "FAIL: digits $digits (variant $((trial % 4))): output differs from bash"; diff <(echo "$want") <(echo "$got") || true; exit 1; }
done
rm -rf "$data/AwkWeird"
#    Un flujo que se acaba antes de que el total pase de 40 simplemente termina (urandom nunca lo hace). El salto de línea
#    del final crea un último registro vacío, que la regla 1 no debe contar como tarjeta.
printf '1 2\n' > "$data/in.txt"
out=$(run "$data/in.txt")
grep -q '^# committed total=23 entries=2 DEMO ONLY$' <<<"$out" || { echo "FAIL: a short stream did not end cleanly"; echo "$out"; exit 1; }
rm -rf "$data/AwkWeird"

# 3. La línea única del comentario de cabecera es el reto sin la base de datos: ejecútala con un flujo fijo.
oneliner=$(sed -n "/^#   gawk 'BEGIN/,/ \/dev\/urandom\$/p" timecards.awk | sed 's/^# *//' | tr '\n' ' ')
[[ -n $oneliner ]] || { echo "FAIL: no one-liner in the header"; exit 1; }
base=$(sed 's# */dev/urandom *$##; s/^gawk /'"$gawk"' /' <<<"$oneliner")
printf '3 8 2 9 4 1\n' > "$data/fixed.txt"
got=$(eval "$base" '"$data/fixed.txt"')
want=$(expected 382941 | grep -v '^SUMMARY')
[[ $got == "$want" ]] || { echo "FAIL: the header one-liner disagrees with bash"; diff <(echo "$want") <(echo "$got") || true; exit 1; }

# 4. El patrón es la regla de parada: con 5 como dados cada tarjeta es de 15 horas, así que el programa real se detiene en
#    3 tarjetas (45). Mueve el umbral a 80 y el mismo flujo debe dar 6 (90).
printf '5 5 5 5 5 5 5 5 5 5\n' > "$data/fives.txt"
[[ $(run "$data/fives.txt" | rows | wc -l) -eq 3 ]] || { echo "FAIL: a stream of 5s should stop at 3 cards"; exit 1; }
rm -rf "$data/AwkWeird"
sed 's/^t > 40 { exit }$/t > 80 { exit }/' timecards.awk > "$data/eighty.awk"
[[ $(PROGRAM="$data/eighty.awk" run "$data/fives.txt" | rows | wc -l) -eq 6 ]] || { echo "FAIL: moving the pattern to 80 should give 6 cards"; exit 1; }
rm -rf "$data/AwkWeird"

# 5. Ejecútalo muchas veces de verdad, sobre /dev/urandom; cada ejecución debe imprimir un conjunto de registros sensato,
#    y las filas de SQLite deben coincidir con él.
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

# 3. La restricción CHECK de demo_only es real: una fila que no sea demo debe ser rechazada.
if sqlite3 "$db" "insert into demo_timecards(run_id,category,hours,running_total,demo_only) values('x','x',1,1,0)" 2>/dev/null; then
    echo "FAIL: db accepted a non-demo row"; exit 1
fi
echo "OK: digit streams match bash; the header one-liner works; t > 40 { exit } is the stop rule; 25 runs on /dev/urandom stopped when they should, committed to SQLite, all marked DEMO ONLY"
