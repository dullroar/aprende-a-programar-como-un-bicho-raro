# Imagen de contenedor para la entrada de Haskell. Ejecútala con: sandbox/container/run-image.sh src/haskell
# Etapa de compilación: GHC compila el script en un solo binario. Etapa de ejecución: ese binario sobre una base con
# sqlite3 y las dos bibliotecas compartidas que necesita, sin GHC dentro.
FROM code-challenge-sandbox:local AS build
USER root
WORKDIR /build
COPY timecards.hs .
RUN ghc -O1 -o timecards timecards.hs

FROM cc-rt-haskell:local
COPY --from=build /build/timecards /app/timecards
ENV CC_RUN=/app/timecards
