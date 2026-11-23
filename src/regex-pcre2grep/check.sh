#!/usr/bin/env bash
# Comprueba las reglas del reto de regex para la pista de pcre2grep. Usa un directorio de datos desechable.
# Necesita un pcre2grep compilado con scripts de llamadas de retorno (consulta README.md); define PCRE2GREP para apuntar a él.
set -euo pipefail
cd "$(dirname "$0")"
data=$(mktemp -d); trap 'rm -rf "$data"' EXIT
export XDG_DATA_HOME=$data
db=$data/RegexPcre2grep/demo-timecards.db
here=$PWD

# 1. El anfitrión no tiene palabras clave de bucle, ejecuta exactamente un pcre2grep, y las llamadas de retorno solo pueden ejecutar una
#    lista permitida de programas (nunca un intérprete de comandos ni un intérprete de lenguaje).
code=$(grep -Ev '^\s*(#|$)' timecards.sh)
if grep -Eqw 'for|foreach|while|until|goto|select' <<<"$code"; then
    echo "FAIL: loop keyword found in timecards.sh"; exit 1
fi
[[ $(grep -c '"\$PCRE2GREP" "\$(cat' <<<"$code") -eq 1 ]] || { echo "FAIL: expected exactly one pcre2grep run"; exit 1; }
progs=$(grep -o '(?C{/[^|}]*' timecards.sh | sed 's/(?C{//' | sort -u | paste -sd' ')
[[ $progs == "/bin/sleep /usr/bin/sqlite3 /usr/bin/test" ]] || { echo "FAIL: callouts run unexpected programs: $progs"; exit 1; }

# 2. Un pcre2grep sin soporte de llamadas de retorno debe rechazarse con un error claro (solo se puede probar si hay uno instalado).
if [[ -x /usr/bin/pcre2grep ]] && ! /usr/bin/pcre2grep --help 2>&1 | grep -q 'All callout scripts'; then
    rc=0; PCRE2GREP=/usr/bin/pcre2grep ./timecards.sh >/dev/null 2>&1 || rc=$?
    [[ $rc -eq 2 ]] || { echo "FAIL: callout-less pcre2grep was not refused (exit $rc)"; exit 1; }
fi

# 3. Ejecútalo muchas veces; cada ejecución debe imprimir un conjunto de registros sensato, y las filas de SQLite deben coincidir con él.
for i in $(seq 1 25); do
    out=$("$here/timecards.sh" 2>"$data/err")
    run=$(sed -nE 's/^# DEMO ONLY run ([0-9]+)$/\1/p' <<<"$out")
    [[ -n $run ]] || { echo "FAIL run $i: no run id"; echo "$out"; exit 1; }
    grep -q '^# the match now returns false, on purpose$' <<<"$out" || { echo "FAIL run $i: no false-return line"; echo "$out"; exit 1; }
    commit=$(grep '^# committed' <<<"$out")
    total=$(sed -E 's/.*total=([0-9]+).*/\1/' <<<"$commit")
    entries=$(sed -E 's/.*entries=([0-9]+).*/\1/' <<<"$commit")
    rows=$(grep -cE '^(Meetings|Coding|Debugging|Learning)	' <<<"$out" || true)
    [[ $rows -eq $entries ]] || { echo "FAIL run $i: $rows rows but entries=$entries"; exit 1; }
    awk -F'\t' '/^(Meetings|Coding|Debugging|Learning)\t/ && ($2 < 10 || $2 > 19) { bad = 1 } END { exit bad }' <<<"$out" || { echo "FAIL run $i: hours out of 10-19"; exit 1; }
    # Regla de parada: el total antes de la última tarjeta es 40 o menos (exactamente 40 continúa), y la última tarjeta lo llevó a más de 40. Una ejecución tiene de 3 a 5 tarjetas.
    before_last=$(awk -F'\t' '/^(Meetings|Coding|Debugging|Learning)\t/ { prev = s; s += $2 } END { print prev + 0 }' <<<"$out")
    (( before_last <= 40 && total > 40 && entries >= 3 && entries <= 5 )) || { echo "FAIL run $i: stop rule wrong (total before the last card = $before_last, total = $total, entries = $entries)"; exit 1; }
    # La regla de parada se anuncia en stderr (una restricción CHECK con nombre) exactamente cuando el total terminó en más de 40, y nada más lo hace.
    stops=$(grep -c 'CHECK constraint failed: stop rule fired: total exceeds 40' "$data/err" || true)
    others=$(grep -vc 'CHECK constraint failed: stop rule fired: total exceeds 40' "$data/err" || true)
    (( total > 40 ? stops == 1 : stops == 0 )) || { echo "FAIL run $i: expected stop-rule stderr line $(( total > 40 )) time(s), saw $stops"; exit 1; }
    [[ $others -eq 0 ]] || { echo "FAIL run $i: unexpected stderr:"; cat "$data/err"; exit 1; }
    # Las filas están realmente en SQLite y coinciden con lo que se imprimió.
    db_row=$(sqlite3 "$db" "select count(*) || ' ' || coalesce(sum(hours),0) || ' ' || coalesce(max(running_total),0) || ' ' || coalesce(min(demo_only),0) || coalesce(max(demo_only),0) from demo_timecards where run_id = $run")
    [[ $db_row == "$entries $total $total 11" ]] || { echo "FAIL run $i: db says '$db_row', output says '$entries $total $total 11'"; exit 1; }
done
[[ $(sqlite3 "$db" 'select count(*) from runs') -eq 25 ]] || { echo "FAIL: expected 25 runs in the db"; exit 1; }
[[ $(sqlite3 "$db" 'select count(*) from stop_rule') -eq 0 ]] || { echo "FAIL: stop_rule probe rows were left behind"; exit 1; }

# 4. Exactamente 40 continúa. Cuatro tarjetas de 10 horas suman exactamente 40, así que se debe sacar una quinta tarjeta: Meetings otra vez, total 50.
#    Una copia del script con todas las tarjetas de 10 horas hace que esa sea la única ejecución posible (directorio de datos aparte, para no alterar las comprobaciones anteriores).
sed 's/10+abs(random())%10 AS h/10 AS h/' timecards.sh > "$data/fixed.sh"
! grep -q 'abs(random())' "$data/fixed.sh" || { echo "FAIL: the exactly-40 test could not rewrite the draw in timecards.sh"; exit 1; }
out=$(XDG_DATA_HOME=$data/fixed bash "$data/fixed.sh" 2>/dev/null)
mapfile -t rows < <(grep -E '^(Meetings|Coding|Debugging|Learning)	' <<<"$out")
(( ${#rows[@]} == 5 )) || { echo "FAIL: all-10 cards must give five rows (exactly 40 continues)"; echo "$out"; exit 1; }
[[ ${rows[3]} == Learning* && ${rows[4]} == Meetings*$'\t'10$'\t'50$'\t'* ]] || { echo "FAIL: the fourth card must be Learning and the fifth Meetings with total 50"; echo "$out"; exit 1; }

# 5. La restricción CHECK de demo_only es real: una fila que no sea de demostración debe rechazarse.
if sqlite3 "$db" "insert into demo_timecards(run_id,category,hours,running_total,demo_only) values(1,'x',10,10,0)" 2>/dev/null; then
    echo "FAIL: db accepted a non-demo row"; exit 1
fi
echo "OK: one pcre2grep; 25 runs, each stopped when it should, wrote to SQLite, and returned false; exactly 40 continued to a fifth card"
