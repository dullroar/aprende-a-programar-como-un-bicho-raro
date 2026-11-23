# Imagen de contenedor para la entrada de ed. Ejecútala con: sandbox/container/run-image.sh src/ed-weird
# Todo el cálculo es GNU ed leyendo timecards.ed. La base añade ed y sqlite3 sobre un Ubuntu mínimo.
# check.sh es para tu propia máquina; la imagen ejecuta la demostración.
FROM cc-rt-ed:local
COPY timecards.ed timecards.sh /app/
ENV CC_RUN="sh /app/timecards.sh"
