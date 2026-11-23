#!/bin/sh
# Lo que tar ejecuta en cada punto de control. Aplica una transición (tick.sql) y nada más.
# tar fija TAR_CHECKPOINT (1, 2, 3, ...) e ignora nuestro estado de salida, así que un fallo aquí no puede detener el archivo:
# solo puede dejar la máquina donde estaba.
set -u
case ${TAR_CHECKPOINT-} in ''|*[!0-9]*) echo "tick: TAR_CHECKPOINT is not a number" >&2; exit 1 ;; esac
exec sqlite3 -bail -cmd ".parameter init" -cmd ".parameter set @t $TAR_CHECKPOINT" "${TICK_DB:?}" < "${TICK_SQL:?}"
