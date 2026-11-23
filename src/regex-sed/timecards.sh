#!/usr/bin/env bash
# DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo XDG_DATA_HOME. Consulta README.md.
#
# El programa es timecards.sed. Este script solo escribe una "cinta" de una línea (id de ejecución, semana ISO, una semilla
# aleatoria de 16 bits, si la salida estándar es una terminal y la bandera TRACE) y ejecuta UN comando sed sobre ella.
# La salida estándar de sed es la pantalla; su fd 3 es el SQL que genera, canalizado a sqlite3. Ni bucle,
# ni aritmética, ni decisiones aquí: todo eso son coincidencias de regex dentro de timecards.sed.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
db=${XDG_DATA_HOME:-$HOME/.local/share}/RegexSed/demo-timecards.db
mkdir -p "$(dirname "$db")"
exec 4>&1
tty=$(set +e; tty -s <&4; echo $?)

set +e
printf 'run:%s wk:%s rng:%s tty:%s trace:%s\n' "$(date +%s)-$$" "$(date +%G-W%V)" \
    "$(head -c2 /dev/urandom | basenc --base2msbf)" "$tty" "${TRACE:-0}" |
    sed -nEu -f "$here/timecards.sed" 3>&1 1>&4 | sqlite3 "$db"
st=("${PIPESTATUS[@]}")

# Que sed termine con 1 es el objetivo (el programa "falla" después de hacer todo el trabajo); sqlite3 debe tener éxito.
exit $(( st[1] == 1 && st[2] == 0 ? 0 : 3 ))
