# Imagen de contenedor para la entrada CMake. Ejecútala con: sandbox/container/run-image.sh src/cmake
# CMake es el intérprete del programa, así que se queda; la base solo tiene cmake y sqlite3 (sin compilador ni make).
FROM cc-rt-cmake:local
COPY timecards.cmake /app/timecards.cmake
ENV CC_RUN="cmake -P /app/timecards.cmake"
