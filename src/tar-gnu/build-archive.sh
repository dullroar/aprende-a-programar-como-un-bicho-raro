#!/bin/sh
# El serializador: escribe program.tar, un archivo tar corriente cuyos miembros son el programa.
#
#   sh build-archive.sh [--seed N] [--hours "h1 h2 h3 h4 h5"] OUT.tar
#
# El archivo dice, en el orden de los miembros, lo que debe hacer el intérprete:
#   000.begin  010.card 011.stop-over  020.card 021.stop-over  ...  050.card 051.stop-over  990.show
# Los dados se tiran AQUÍ, una sola vez, al escribir el programa, con un generador con semilla (Park-Miller).
# La semilla queda registrada dentro de 000.begin, así que la misma semilla produce siempre los mismos bytes.
# --hours fuerza los cinco valores de horas (para pruebas). El archivo tiene cinco ranuras de tarjeta; como mucho se
# necesitan cinco tarjetas (10+10+10+10 es 40, que no supera 40, así que una quinta tarjeta siempre termina el trabajo).
# Aquí nada sabe cuándo parar: eso es trabajo del intérprete, guiado por los miembros stop-over.
set -eu
seed= hours=
while [ $# -gt 1 ]; do
    case $1 in
        --seed) seed=$2; shift 2 ;;
        --hours) hours=$2; shift 2 ;;
        *) echo "usage: build-archive.sh [--seed N] [--hours 'a b c d e'] OUT.tar" >&2; exit 2 ;;
    esac
done
[ $# -eq 1 ] || { echo "usage: build-archive.sh [--seed N] [--hours 'a b c d e'] OUT.tar" >&2; exit 2; }
out=$1
if [ -z "$seed" ]; then seed=$(( $(od -An -N4 -tu4 /dev/urandom | tr -d ' ') % 2147483646 + 1 )); fi
case $seed in ''|*[!0-9]*) echo "seed must be a whole number" >&2; exit 2 ;; esac

stage=$(mktemp -d); trap 'rm -rf "$stage"' EXIT
names=000.begin
printf 'format=tarprog/1\nseed=%s\nlabel=DEMO ONLY\n' "$seed" > "$stage/000.begin"
cats="Meetings Coding Debugging Learning Meetings"
state=$(( seed % 2147483646 + 1 ))
n=0
for c in $cats; do
    n=$((n + 1))
    if [ -n "$hours" ]; then h=$(printf '%s\n' $hours | sed -n "${n}p")
    else state=$(( state * 48271 % 2147483647 )); h=$(( 10 + state % 10 )); fi
    case $h in 1[0-9]) ;; *) echo "hours must be 10..19, got '$h'" >&2; exit 2 ;; esac
    card=0$((n * 10)).card stop=0$((n * 10 + 1)).stop-over
    printf 'category=%s\nhours=%s\n' "$c" "$h" > "$stage/$card"
    printf 'limit=40\n' > "$stage/$stop"
    names="$names $card $stop"
done
: > "$stage/990.show"
names="$names 990.show"
# Un formato, un orden, una hora y un propietario fijos hacen que el mismo programa dé los mismos bytes.
# shellcheck disable=SC2086
tar --format=ustar --mtime=@0 --owner=0 --group=0 --numeric-owner --mode=0644 -cf "$out" -C "$stage" $names
