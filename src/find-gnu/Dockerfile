# Imagen de contenedor para la entrada GNU find. Ejecútala con: sandbox/container/run-image.sh src/find-gnu
# Todo el programa es un solo `find` de GNU (findutils, de la base Ubuntu) más mkdir y mktemp (coreutils);
# la base añade solo sqlite3. check.sh y build-line.py son para tu propia máquina; la imagen ejecuta la demostración.
FROM cc-rt-sqlite:local
COPY timecards.sh /app/
ENV CC_RUN="sh /app/timecards.sh"
