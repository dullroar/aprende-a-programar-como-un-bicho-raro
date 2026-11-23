# Imagen de contenedor para la entrada Forth. Ejecútala con: sandbox/container/run-image.sh src/forth
# Nada que compilar: Gforth interpreta el script. La base de ejecución tiene gforth y sqlite3 (la
# entrada envía su SQL a sqlite3 por sh), y ningún compilador ni gestor de paquetes.
FROM cc-rt-gforth:local
COPY timecards.fs /app/timecards.fs
ENV CC_RUN="gforth /app/timecards.fs"
