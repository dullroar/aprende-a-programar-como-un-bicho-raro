#!/bin/sh
# DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo XDG_DATA_HOME. Mira README.md.
#
# Un solo `find` de GNU es todo el programa: cava el árbol de directorios que recorre, un directorio por hora,
# y escribe SQL en el descriptor de archivo 3 mientras avanza (la profundidad del directorio es el total acumulado, y la
# mtime del propio directorio es la semana ISO). Las líneas de alrededor solo siembran una carpeta temporal, pasan el SQL a
# sqlite3 y limpian. build-line.py es la fuente legible de la expresión larga; check.sh mantiene las dos
# sincronizadas. FIND_O=0..3 elige el nivel del optimizador (por defecto 3); FIND_D=rates imprime el perfil propio de find.
set -eu
dir=${XDG_DATA_HOME:-$HOME/.local/share}/FindGnu
mkdir -p "$dir"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT HUP INT TERM
cd "$work"
mkdir t
{
printf '%s\n' "CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY,started_at TEXT);" \
  "CREATE TABLE IF NOT EXISTS demo_timecards(id INTEGER PRIMARY KEY,run_id INTEGER,category TEXT,hours INTEGER CHECK(hours BETWEEN 10 AND 19),running_total INTEGER,iso_week TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));" \
  "CREATE TABLE IF NOT EXISTS stop_rule(ok INTEGER CONSTRAINT \"stop rule fired: total exceeds 40\" CHECK(ok=1));" \
  "INSERT INTO runs(started_at) VALUES(datetime('now','localtime'));" \
  "SELECT printf('# DEMO ONLY run %d',last_insert_rowid());"
find -O${FIND_O:-3} ${FIND_D:+-D $FIND_D} t -regextype posix-extended \( -path t -exec mktemp -d {}/XXXXXX \; \) -o \( -name '??????' -fprintf /dev/fd/3 "INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week) VALUES((SELECT max(id) FROM runs)," \( \( -regex '(.*/[^/]{6}){5}.*' -fprintf /dev/fd/3 "'Reuniones'," \) -o \( -regex '(.*/[^/]{6}){4}.*' -fprintf /dev/fd/3 "'Aprendizaje'," \) -o \( -regex '(.*/[^/]{6}){3}.*' -fprintf /dev/fd/3 "'Depuración'," \) -o \( -regex '(.*/[^/]{6}){2}.*' -fprintf /dev/fd/3 "'Programación'," \) -o \( -fprintf /dev/fd/3 "'Reuniones'," \) \) \( \( -name '?????[abcdef]' -fprintf /dev/fd/3 "10," -exec mkdir {}/b08 \; \) -o \( -name '?????[ghijkl]' -fprintf /dev/fd/3 "11," -exec mkdir {}/b09 \; \) -o \( -name '?????[mnopqr]' -fprintf /dev/fd/3 "12," -exec mkdir {}/b10 \; \) -o \( -name '?????[stuvwx]' -fprintf /dev/fd/3 "13," -exec mkdir {}/b11 \; \) -o \( -name '?????[yz0123]' -fprintf /dev/fd/3 "14," -exec mkdir {}/b12 \; \) -o \( -name '?????[456789]' -fprintf /dev/fd/3 "15," -exec mkdir {}/b13 \; \) -o \( -name '?????[ABCDEF]' -fprintf /dev/fd/3 "16," -exec mkdir {}/b14 \; \) -o \( -name '?????[GHIJKL]' -fprintf /dev/fd/3 "17," -exec mkdir {}/b15 \; \) -o \( -name '?????[MNOPQR]' -fprintf /dev/fd/3 "18," -exec mkdir {}/b16 \; \) -o \( -name '?????[STUVWX]' -fprintf /dev/fd/3 "19," -exec mkdir {}/b17 \; \) -o \( -name '????[abcdef][YZ]' -fprintf /dev/fd/3 "10," -exec mkdir {}/b08 \; \) -o \( -name '????[ghijkl][YZ]' -fprintf /dev/fd/3 "11," -exec mkdir {}/b09 \; \) -o \( -name '????[mnopqr][YZ]' -fprintf /dev/fd/3 "12," -exec mkdir {}/b10 \; \) -o \( -name '????[stuvwx][YZ]' -fprintf /dev/fd/3 "13," -exec mkdir {}/b11 \; \) -o \( -name '????[yz0123][YZ]' -fprintf /dev/fd/3 "14," -exec mkdir {}/b12 \; \) -o \( -name '????[456789][YZ]' -fprintf /dev/fd/3 "15," -exec mkdir {}/b13 \; \) -o \( -name '????[ABCDEF][YZ]' -fprintf /dev/fd/3 "16," -exec mkdir {}/b14 \; \) -o \( -name '????[GHIJKL][YZ]' -fprintf /dev/fd/3 "17," -exec mkdir {}/b15 \; \) -o \( -name '????[MNOPQR][YZ]' -fprintf /dev/fd/3 "18," -exec mkdir {}/b16 \; \) -o \( -name '????[STUVWX][YZ]' -fprintf /dev/fd/3 "19," -exec mkdir {}/b17 \; \) -o \( -fprintf /dev/fd/3 "10," -exec mkdir {}/b08 \; \) \) \) -o \( -name b00 -fprintf /dev/fd/3 "%d,'%TG-W%TV');\n" \( -regex '([^/]*/){41}.*' -o \( -exec mktemp -d {}/XXXXXX \; \) \) \) -o \( -name 'b??' \( \( -name b17 -exec mkdir {}/b16 \; \) -o \( -name b16 -exec mkdir {}/b15 \; \) -o \( -name b15 -exec mkdir {}/b14 \; \) -o \( -name b14 -exec mkdir {}/b13 \; \) -o \( -name b13 -exec mkdir {}/b12 \; \) -o \( -name b12 -exec mkdir {}/b11 \; \) -o \( -name b11 -exec mkdir {}/b10 \; \) -o \( -name b10 -exec mkdir {}/b09 \; \) -o \( -name b09 -exec mkdir {}/b08 \; \) -o \( -name b08 -exec mkdir {}/b07 \; \) -o \( -name b07 -exec mkdir {}/b06 \; \) -o \( -name b06 -exec mkdir {}/b05 \; \) -o \( -name b05 -exec mkdir {}/b04 \; \) -o \( -name b04 -exec mkdir {}/b03 \; \) -o \( -name b03 -exec mkdir {}/b02 \; \) -o \( -name b02 -exec mkdir {}/b01 \; \) -o \( -name b01 -exec mkdir {}/b00 \; \) \) \) 3>&1 >/dev/null
printf '%s\n' ".mode tabs" \
  "SELECT category,hours,running_total,iso_week,'DEMO ONLY' FROM demo_timecards WHERE run_id=(SELECT max(id) FROM runs) ORDER BY id;" \
  "SELECT printf('# committed total=%d entries=%d DEMO ONLY',max(running_total),count(*)) FROM demo_timecards WHERE run_id=(SELECT max(id) FROM runs);" \
  "INSERT INTO stop_rule SELECT max(running_total)<=40 FROM demo_timecards WHERE run_id=(SELECT max(id) FROM runs);" \
  "DELETE FROM stop_rule;"
} | sqlite3 "$dir/demo-timecards.db" || :
