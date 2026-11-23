#!/bin/sh
# Dispone la carga cuyo archivo es el reloj. Con los ajustes por defecto (-b 1 --checkpoint=1) tar escribe
# un registro de 512 bytes por punto de control, así que el número de ticks es el número de bloques de 512 bytes del archivo:
#     bloques = suma sobre los miembros de (1 cabecera + ceil(tamaño / 512) de datos) + 2 bloques de fin de archivo.
#   sh layout.sh [--ticks N] [--members M] DIR      escribe DIR/m01 ... y DIR/list (los nombres de los miembros, en orden)
set -eu
ticks=64 members=1
while [ $# -gt 1 ]; do
    case $1 in --ticks) ticks=$2; shift 2 ;; --members) members=$2; shift 2 ;; *) echo "usage: layout.sh [--ticks N] [--members M] DIR" >&2; exit 2 ;; esac
done
dir=${1:?usage: layout.sh [--ticks N] [--members M] DIR}
case $ticks$members in *[!0-9]*) echo "numbers only" >&2; exit 2 ;; esac
data=$(( ticks - 2 - members ))
[ "$members" -ge 1 ] && [ "$data" -ge 0 ] || { echo "layout: $ticks ticks cannot hold $members member(s)" >&2; exit 2; }
mkdir -p "$dir"; : > "$dir/list"
i=1; each=$(( data / members )); rest=$(( data - each * members ))
while [ "$i" -le "$members" ]; do
    d=$each; [ "$i" -eq "$members" ] && d=$(( each + rest ))
    name=$(printf 'm%02d' "$i")
    head -c $(( d * 512 )) /dev/zero > "$dir/$name"
    echo "$name" >> "$dir/list"
    i=$(( i + 1 ))
done
