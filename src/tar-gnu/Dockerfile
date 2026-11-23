# Imagen de contenedor para la entrada de GNU tar. Ejecútala con: sandbox/container/run-image.sh src/tar-gnu
# El programa es un archivo tar; GNU tar (de la base de Ubuntu) lo recorre y llama a dispatch.sh una vez por miembro.
# La base solo añade sqlite3. check.sh es para tu propia máquina; la imagen ejecuta la demo.
FROM cc-rt-sqlite:local
COPY build-archive.sh inspect.sh interpret.sh dispatch.sh timecards.sh /app/
ENV CC_RUN="sh /app/timecards.sh"
