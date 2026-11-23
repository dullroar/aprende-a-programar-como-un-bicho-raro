# Imagen de contenedor para la entrada de APL más rara. Ejecútala con: sandbox/container/run-image.sh src/apl-weird
# Ubuntu no empaqueta GNU APL: la imagen de herramientas lo compila desde un tarball de gnu.org fijado por SHA-256
# (mira sandbox/linux/Dockerfile), y esta imagen toma de ella solo el /opt/apl terminado.
FROM code-challenge-sandbox:local AS build

FROM cc-rt-apl:local
COPY --from=build /opt/apl /opt/apl
COPY timecards.apl /app/timecards.apl
ENV CC_RUN="/opt/apl/bin/apl --script -f /app/timecards.apl"
