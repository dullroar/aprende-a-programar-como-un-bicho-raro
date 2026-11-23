# Imagen de contenedor para la entrada Forth más rara. Ejecútala con: sandbox/container/run-image.sh src/forth-weird
# Gforth interpreta el script; la base tiene gforth y sqlite3 (la entrada envía SQL a sqlite3
# a través de sh), y ningún compilador ni gestor de paquetes.
FROM cc-rt-gforth:local
COPY timecards.fs /app/timecards.fs
ENV CC_RUN="gforth /app/timecards.fs"
