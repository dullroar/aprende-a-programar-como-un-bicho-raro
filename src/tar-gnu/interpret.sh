#!/bin/sh
# El intérprete que ejecuta: el único lugar donde se activa --to-command de tar.
#
#   sh interpret.sh --execute ARCHIVE
#
# Hay que pedirlo dos veces (la opción Y el archivo): leer un archivo y ejecutarlo son actos distintos.
# Primero el inspector pasivo examina todo el archivo. Solo un veredicto limpio llega a tar. Luego tar recorre
# los miembros en orden y entrega cada miembro regular a dispatch.sh. No se extrae nada a disco.
set -u
here=$(cd "$(dirname "$0")" && pwd)
[ "${1:-}" = --execute ] && [ $# -eq 2 ] || { echo "usage: interpret.sh --execute ARCHIVE   (this RUNS the archive; use inspect.sh to just read it)" >&2; exit 2; }
ar=$2
data=${XDG_DATA_HOME:-$HOME/.local/share}/TarGnu
mkdir -p "$data"
export TARPROG_DB=${TARPROG_DB:-$data/demo-timecards.db}
sh "$here/inspect.sh" "$ar" > /dev/null || { echo "interpret: the inspector found records it would refuse; nothing was run" >&2; exit 4; }
scratch=$(mktemp -d); trap 'rm -rf "$scratch"' EXIT
echo "# EXECUTING $ar: tar --to-command=dispatch.sh (the operator's choice, not the archive's)"
tar -C "$scratch" --to-command="sh $here/dispatch.sh" -xf "$ar"
