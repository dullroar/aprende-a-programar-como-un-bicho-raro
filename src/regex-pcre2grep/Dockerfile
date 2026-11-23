# Imagen de contenedor para la entrada de pcre2grep. Ejecútala con: sandbox/container/run-image.sh src/regex-pcre2grep
# El pcre2grep de Ubuntu se compila sin scripts de llamadas de retorno, así que la imagen de herramientas compila uno a partir de una
# versión de PCRE2 fijada por SHA-256 (consulta sandbox/linux/Dockerfile); esta imagen solo toma ese binario estático.
FROM code-challenge-sandbox:local AS build

FROM cc-rt-sqlite:local
COPY --from=build /opt/pcre2/bin/pcre2grep /usr/local/bin/pcre2grep
COPY timecards.sh /app/timecards.sh
ENV CC_RUN="bash /app/timecards.sh"
