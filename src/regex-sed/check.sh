#!/usr/bin/env bash
# Comprueba las reglas del reto de expresiones regulares para la pista de sed. Usa un directorio de datos desechable.
set -euo pipefail
cd "$(dirname "$0")"
data=$(mktemp -d); trap 'rm -rf "$data"' EXIT
export XDG_DATA_HOME=$data
db=$data/RegexSed/demo-timecards.db
fail() { echo "FAIL: $*"; exit 1; }

# 1. El anfitrión ejecuta exactamente un comando sed y no tiene bucles ni condicionales.
host=$(grep -Ev '^\s*(#|$)' timecards.sh)
[[ $(grep -cE '(^|[|])\s*sed ' <<<"$host") -eq 1 ]] || fail "expected exactly one sed command in timecards.sh"
if grep -Eqw 'for|while|until|select|if|case' <<<"$host"; then fail "loop or if keyword in timecards.sh"; fi

# 2. El script de sed nunca invoca el intérprete ni lee archivos: sin comandos e/r/R/W y sin la bandera s///e,
#    y los únicos archivos que escribe son fd 3 (el SQL) y stderr (el rastro).
script=$(grep -Ev '^\s*(#|$)' timecards.sed)
if grep -Eq '^(/([^/\\]|\\.)*/|[0-9$]+)?!?\s*[erRW]( |$)' <<<"$script"; then fail "e/r/R/W command in timecards.sed"; fi
flags=$(sed -nE 's#^s/(\\.|[^/\\])*/(\\.|[^/\\])*/([a-zA-Z0-9]*).*#\3#p' <<<"$script")
if grep -q e <<<"$flags"; then fail "s///e flag in timecards.sed"; fi
targets=$(grep -oE '/w /[^ ]+$' <<<"$script" | sort -u | tr '\n' ' ')
[[ $targets == '/w /dev/fd/3 /w /dev/stderr ' ]] || fail "unexpected w targets: $targets"

# 3. sed mismo termina con 1 (la jugada de "devolver falso") y con 2 si la cinta está mal formada.
rc=0; echo 'run:t wk:2026-W01 rng:1011001110100101 tty:1 trace:0' | sed -nE -f timecards.sed 3>/dev/null >/dev/null || rc=$?
[[ $rc -eq 1 ]] || fail "sed exited $rc, expected 1"
rc=0; echo 'not a tape' | sed -nE -f timecards.sed 3>/dev/null 2>/dev/null || rc=$?
[[ $rc -eq 2 ]] || fail "malformed tape: sed exited $rc, expected 2"

# 4. El registro de desplazamiento es determinista: la misma semilla da las mismas tarjetas de horas.
a=$(echo 'run:t wk:w rng:0110100110010110 tty:1 trace:0' | sed -nE -f timecards.sed 3>/dev/null || true)
b=$(echo 'run:t wk:w rng:0110100110010110 tty:1 trace:0' | sed -nE -f timecards.sed 3>/dev/null || true)
[[ -n $a && $a == "$b" ]] || fail "same seed, different output"

# 4b. Exactamente 40 continúa. Cuatro tarjetas de 10 horas suman exactamente 40, así que debe seguir una quinta: Reuniones otra vez, total 50. Una copia del script
#     cuyo sorteo siempre da el dígito 0 (10 horas) hace que esa sea la única ejecución posible.
sed 's/rng:\\1\\2 d:\\1\//rng:\\1\\2 d:0000\//' timecards.sed > "$data/tens.sed"
cmp -s timecards.sed "$data/tens.sed" && fail "the exactly-40 test could not rewrite the draw in timecards.sed"
tens=$(echo 'run:t wk:w rng:0110100110010110 tty:1 trace:0' | sed -nE -f "$data/tens.sed" 3>/dev/null | grep -E '^(Reuniones|Programación|Depuración|Aprendizaje)	' | cut -f1-3 | tr '\t' ' ' | paste -sd, || true)
[[ $tens == "Reuniones 10 10,Programación 10 20,Depuración 10 30,Aprendizaje 10 40,Reuniones 10 50" ]] || fail "all-10 cards must give five rows ending at 50 (exactly 40 continues); got: $tens"

# 5. Ejecuta lo real varias veces. Cada ejecución debe parar justo cuando toca, y cada total acumulado
#    debe igualar al anterior más las horas (la aritmética de marcas de sed), y SQLite debe coincidir con la salida estándar.
hours_seen=""
for i in $(seq 1 25); do
    out=$(./timecards.sh) || fail "run $i: timecards.sh exited $?"
    run=$(sed -nE 's/^# DEMO ONLY run (.+)$/\1/p' <<<"$out")
    [[ -n $run ]] || fail "run $i: no run id"
    grep -q '^# sed now exits with status 1 (failure), on purpose$' <<<"$out" || fail "run $i: no false-return line"
    commit=$(grep '^# committed' <<<"$out")
    total=$(sed -E 's/.*total=([0-9]+).*/\1/' <<<"$commit")
    entries=$(sed -E 's/.*entries=([0-9]+).*/\1/' <<<"$commit")
    awk -F'\t' -v total="$total" -v entries="$entries" '
        /^(Reuniones|Programación|Depuración|Aprendizaje)\t/ {
            n++; if ($2 < 10 || $2 > 19) { print "hours out of range: " $0; exit 1 }
            if ($3 != prev + $2) { print "bad running total: " $0; exit 1 }
            if (prev > 40) { print "kept going after 40: " $0; exit 1 }
            prev = $3
        }
        END { if (n != entries || prev != total) { print "summary disagrees with rows"; exit 1 }
              if (n < 3 || n > 5 || prev <= 40) { print "a run has 3 to 5 cards and ends over 40; this one has " n " cards, total " prev; exit 1 } }' <<<"$out" || fail "run $i"
    hours_seen+=$(awk -F'\t' '/^(Meetings|Coding|Debugging|Learning)\t/ { printf "%s ", $2 }' <<<"$out")
    db_row=$(sqlite3 "$db" "select count(*) || ' ' || coalesce(max(running_total),0) || ' ' || min(demo_only) || max(demo_only) from demo_timecards where run_id = '$run'")
    [[ $db_row == "$entries $total 11" ]] || fail "run $i: db says '$db_row', output says '$entries $total 11'"
done
[[ $(sqlite3 "$db" 'select count(distinct run_id) from demo_timecards') -eq 25 ]] || fail "expected 25 distinct runs in the db"
distinct=$(tr ' ' '\n' <<<"$hours_seen" | grep . | sort -u | wc -l)
(( distinct >= 6 )) || fail "only $distinct distinct hour values across 25 runs; the shift register looks stuck"

# 6. La restricción CHECK de demo_only es real.
if sqlite3 "$db" "insert into demo_timecards(run_id,category,hours,running_total,demo_only) values('x','x',10,10,0)" 2>/dev/null; then
    fail "db accepted a non-demo row"
fi
echo "OK: one sed command, no shell-outs; 25 runs stopped when they should, added up in tally marks, committed to SQLite, and exited 1; exactly 40 continued to a fifth card"
