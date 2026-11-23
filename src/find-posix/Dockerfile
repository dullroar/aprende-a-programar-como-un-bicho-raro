# Imagen de contenedor para la entrada portátil de find. Ejecútala con: sandbox/container/run-image.sh src/find-posix
# Todo el programa es un solo `find` (GNU findutils, de la base Ubuntu) más printf, mkdir, mktemp y date
# (coreutils); la base añade solo sqlite3. check.sh, build-line.py y las otras implementaciones de find
# (bfs, busybox) son para tu propia máquina; la imagen ejecuta solo la demostración.
FROM cc-rt-sqlite:local
COPY timecards.sh /app/
ENV CC_RUN="sh /app/timecards.sh"
