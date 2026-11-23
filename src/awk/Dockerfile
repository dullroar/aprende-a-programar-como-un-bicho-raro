# Imagen de contenedor para la entrada AWK. Ejecútala con: sandbox/container/run-image.sh src/awk
# Nada que compilar: awk interpreta el script. La base de ejecución tiene gawk, el mawk del sistema y sqlite3;
# la entrada es portátil, así que aquí corre con mawk (la rara necesita gawk). Sin compilador ni gestor de paquetes.
FROM cc-rt-awk:local
COPY timecards.awk /app/timecards.awk
ENV CC_RUN="mawk -f /app/timecards.awk"
