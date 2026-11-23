# Imagen de contenedor para la entrada de Common Lisp. Ejecútala con: sandbox/container/run-image.sh src/lisp-weird
# Nada que compilar: SBCL ejecuta el script. La base de ejecución tiene sbcl y sqlite3 (la entrada envía SQL
# a sqlite3), y no tiene compilador ni gestor de paquetes.
FROM cc-rt-sbcl:local
COPY timecards.lisp /app/timecards.lisp
ENV CC_RUN="sbcl --script /app/timecards.lisp"
