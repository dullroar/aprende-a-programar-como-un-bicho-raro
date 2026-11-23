# Imagen de contenedor para la entrada de clausuras en Node.js. Ejecútala con: sandbox/container/run-image.sh src/javascript-weird
# El programa son dos archivos: core.mjs (tres clausuras, sin E/S) y timecards.mjs (la base de datos, el reloj, la pantalla).
# Node 24 trae node:sqlite y los ayudantes de iteradores incorporados; no hay npm ni ningún paquete.
# Añade --tty al comando run-image.sh para ver pulsar la línea DEMO ONLY. check.sh y check.mjs son para tu propia máquina.
FROM cc-rt-node:local
COPY core.mjs timecards.mjs /app/
ENV CC_RUN="node /app/timecards.mjs"
