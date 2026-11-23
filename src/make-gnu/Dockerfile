# Imagen de contenedor para la entrada de GNU Make. Ejecútala con: sandbox/container/run-image.sh src/make-gnu
# Make es el programa (se vuelve a ejecutar a sí mismo como bucle), así que se queda; la base trae make y sqlite3
# y nada más. El Makefile se ejecuta desde una carpeta privada que empieza sin ningún otro archivo.
FROM cc-rt-make:local
COPY Makefile /app/Makefile
ENV CC_RUN=make CC_WORKDIR=/work/run CC_COPY_APP=1
