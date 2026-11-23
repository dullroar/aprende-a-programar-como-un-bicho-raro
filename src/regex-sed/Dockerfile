# Imagen de contenedor para la entrada de regex con sed. Ejecútala con: sandbox/container/run-image.sh src/regex-sed
# GNU sed, bash y coreutils vienen en la base de Ubuntu; la base solo añade sqlite3.
FROM cc-rt-sqlite:local
COPY timecards.sh timecards.sed /app/
ENV CC_RUN="bash /app/timecards.sh"
