# Imagen de contenedor para la entrada de AWK "rara". Ejecútala con: sandbox/container/run-image.sh src/awk-weird
# No hay nada que compilar: gawk interpreta el script (necesita GNU awk: RT y un RS de expresión regular).
# La base de ejecución tiene gawk y sqlite3, y no tiene compilador ni gestor de paquetes.
FROM cc-rt-awk:local
COPY timecards.awk /app/timecards.awk
ENV CC_RUN="gawk -f /app/timecards.awk"
