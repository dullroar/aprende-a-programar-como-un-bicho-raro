# Imagen de contenedor para la entrada COBOL. Ejecútala con: sandbox/container/run-image.sh src/cobol
# Etapa de compilación: cobc de GnuCOBOL compila el programa (a través de C) en un binario. Etapa de ejecución: ese
# binario sobre una base con sqlite3 y la biblioteca de ejecución de GnuCOBOL (libcob), sin compilador.
FROM code-challenge-sandbox:local AS build
USER root
WORKDIR /build
COPY timecards.cob .
RUN cobc -x -o timecards timecards.cob

FROM cc-rt-cobol:local
COPY --from=build /build/timecards /app/timecards
ENV CC_RUN=/app/timecards
