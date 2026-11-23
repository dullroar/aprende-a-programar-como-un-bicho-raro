#!/usr/bin/env bash
# Comprueba las reglas del reto para la entrada de APL rara. Usa un directorio de datos desechable.
set -euo pipefail
cd "$(dirname "$0")"
data=$(mktemp -d); trap 'rm -rf "$data"' EXIT
export XDG_DATA_HOME=$data
db=$data/AplWeird/demo-timecards.db
run() { timeout 30 "${APL:-apl}" --script -f timecards.apl; }   # timeout: una regla de parada rota recurre para siempre

# 1. Estático: la restricción es real. Sin operador de potencia, sin flecha de salto, sin primitivas de tipo bucle fuera de los comentarios;
#    el anfitrión define solo Card0 (un bloque ∇ ... ∇), y el resto de la cadena lo escribe ⎕FX en tiempo de ejecución.
code=$(grep -Ev '^\s*⍝' timecards.apl)
grep -q 'DEMO ONLY' timecards.apl || { echo "FAIL: no DEMO ONLY marker in timecards.apl"; exit 1; }
if grep -q '[⍣→]' <<<"$code"; then echo "FAIL: ⍣ or → found in timecards.apl"; exit 1; fi
[[ $(grep -c '^∇' <<<"$code") -eq 2 ]] || { echo "FAIL: expected exactly one ∇ ... ∇ definition (Card0)"; exit 1; }
[[ $(grep -c '⎕FX' <<<"$code") -eq 1 ]] || { echo "FAIL: expected exactly one ⎕FX (inside Card0)"; exit 1; }
if grep -Eqi 'http|socket|curl|wget' timecards.apl; then echo "FAIL: network-looking text in timecards.apl"; exit 1; fi

# 2. Ejecútalo muchas veces; cada ejecución debe imprimir un conjunto de registros sensato, y las filas de SQLite deben coincidir.
cats=(Reuniones Programación Depuración Aprendizaje)
for i in $(seq 1 25); do
    out=$(run)
    run_id=$(sed -nE 's/^# DEMO ONLY run (.+)$/\1/p' <<<"$out")
    [[ -n $run_id ]] || { echo "FAIL run $i: no run id"; echo "$out"; exit 1; }
    grep -q '^# the host wrote Card0 and nothing else' <<<"$out" || { echo "FAIL run $i: no stunt note"; echo "$out"; exit 1; }
    (( $(grep -c '^# Card[0-9] ⇐' <<<"$out") == $(sed -E 's/.*entries=([0-9]+).*/\1/' <<<"$(grep '^# committed' <<<"$out")") )) || { echo "FAIL run $i: the number of Card functions does not match entries"; echo "$out"; exit 1; }
    commit=$(grep '^# committed' <<<"$out" || true)
    [[ -n $commit ]] || { echo "FAIL run $i: no committed line"; echo "$out"; exit 1; }
    total=$(sed -E 's/.*total=([0-9]+).*/\1/' <<<"$commit")
    entries=$(sed -E 's/.*entries=([0-9]+).*/\1/' <<<"$commit")
    mapfile -t rows < <(grep -E '^(Reuniones|Programación|Depuración|Aprendizaje)	' <<<"$out" || true)
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
done
[[ $(sqlite3 "$db" 'select count(distinct run_id) from demo_timecards') -eq 25 ]] || { echo "FAIL: expected 25 distinct runs in the db"; exit 1; }
[[ $(sqlite3 "$db" 'select count(distinct hours) from demo_timecards') -ge 6 ]] || { echo "FAIL: hours do not look random"; exit 1; }

# 3. La restricción CHECK de demo_only es real: una fila que no sea demo debe ser rechazada.
if sqlite3 "$db" "insert into demo_timecards(run_id,category,hours,running_total,demo_only) values('x','x',1,1,0)" 2>/dev/null; then
    echo "FAIL: db accepted a non-demo row"; exit 1
fi
echo "OK: 25 runs, each stopped when it should, committed to SQLite, all marked DEMO ONLY"
