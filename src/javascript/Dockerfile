# Imagen de contenedor para la entrada de Node.js. Ejecútala con: sandbox/container/run-image.sh src/javascript
# Todo el programa es un solo archivo, timecards.mjs, ejecutado por Node 24 (node:sqlite viene incluido; no hay npm ni paquetes).
# Añade --tty al comando run-image.sh para ver pulsar la línea DEMO ONLY. check.sh es para tu propia máquina.
FROM cc-rt-node:local
COPY timecards.mjs /app/
ENV CC_RUN="node /app/timecards.mjs"
