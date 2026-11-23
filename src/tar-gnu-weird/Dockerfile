# Imagen de contenedor para la entrada del reloj de puntos de control de tar. Ejecútala con: sandbox/container/run-image.sh src/tar-gnu-weird
# GNU tar (de la base Ubuntu) escribe un archivo, y sus puntos de control ejecutan tick.sh. La base solo añade sqlite3.
# check.sh es para tu propia máquina; la imagen ejecuta la demo.
FROM cc-rt-sqlite:local
COPY machine.sql tick.sql tick.sh layout.sh run-clock.sh timecards.sh /app/
ENV CC_RUN="sh /app/timecards.sh"
