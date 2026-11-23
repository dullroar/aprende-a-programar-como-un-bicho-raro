# Imagen de contenedor para la entrada de regex en Perl. Ejecútala con: sandbox/container/run-image.sh src/regex-perl
# Perl y sus módulos estándar vienen en la base de Ubuntu; la base solo añade sqlite3.
FROM cc-rt-sqlite:local
COPY timecards.pl /app/timecards.pl
ENV CC_RUN="perl /app/timecards.pl"
