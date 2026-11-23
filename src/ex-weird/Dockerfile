# Imagen de contenedor para la entrada de Ex. Ejecútala con: sandbox/container/run-image.sh src/ex-weird
# Todo el cálculo es nvi (un ex/vi POSIX) leyendo timecards.ex. La base añade nvi y sqlite3 sobre un Ubuntu mínimo.
# check.sh es para tu propia máquina; la imagen ejecuta la demostración.
FROM cc-rt-nvi:local
COPY timecards.ex timecards.sh /app/
ENV CC_RUN="sh /app/timecards.sh"
