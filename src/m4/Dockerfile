# Imagen de contenedor para la entrada m4. Ejecútala con: sandbox/container/run-image.sh src/m4
# No hay nada que compilar: m4 interpreta el archivo. La base de ejecución trae GNU m4 y sqlite3, y sh para el
# único syscmd de la entrada; no hay compilador ni gestor de paquetes.
FROM cc-rt-m4:local
COPY timecards.m4 /app/timecards.m4
ENV CC_RUN="m4 /app/timecards.m4"
