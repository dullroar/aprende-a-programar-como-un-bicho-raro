#!/bin/sh
# La demo: deja que los puntos de control de un archivo tar sean el reloj. SEED=42 sh timecards.sh repite una ejecución exacta.
exec sh "$(dirname "$0")/run-clock.sh" ${SEED:+--seed "$SEED"}
