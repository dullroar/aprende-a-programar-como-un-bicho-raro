      * SOLO DEMO (DEMO ONLY). Tarjetas de horas ficticias, escritas en
      * un archivo SQLite temporal bajo XDG_DATA_HOME. Nada aquí toca
      * un sistema real de registro de horas.
      *
      * Ejecuta:  cobc -xj timecards.cob
      *
      * El reto: suma tarjetas de 10-19 horas (Reuniones, Programación,
      * Depuración, Aprendizaje, sin parar) hasta que el total
      * acumulado pase de 40. Es una sentencia de la PROCEDURE DIVISION:
      * PERFORM DRAW-CARD UNTIL OVER-FORTY, y la regla de parada no es
      * código: OVER-FORTY es una condición de nivel 88 declarada en
      * el total, en la DATA DIVISION.
      *
      * El formato es el fijo tradicional, heredado de las tarjetas
      * perforadas: las columnas 1-6 eran un número de secuencia (en
      * blanco aquí), un * en la columna 7 marca un comentario y el
      * código va en las columnas 8-72. División, sección y párrafo
      * empiezan en la 8 ("área A"); sentencias en la 12 ("área B").
       IDENTIFICATION DIVISION.
       PROGRAM-ID. TIMECARDS.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
      * El script SQL es un archivo secuencial COBOL normal, un registro
      * por línea. ASSIGN TO un ítem de datos hace que su nombre se
      * decida al ejecutar, según WS-SQL-PATH al hacer OPEN.
           SELECT SQL-SCRIPT ASSIGN TO WS-SQL-PATH
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD  SQL-SCRIPT.
       01  SQL-LINE                PIC X(400).

       WORKING-STORAGE SECTION.
      * ---- la regla de parada, como dato ---------------------------
      * PIC 99 son exactamente dos dígitos decimales. El nivel 88 le da
      * nombre a un rango de valores de WS-TOTAL; UNTIL OVER-FORTY solo
      * pregunta si el total está ahora dentro de ese rango.
       01  WS-TOTAL                PIC 99 VALUE 0.
           88  OVER-FORTY          VALUE 41 THRU 99.
      * Guardar 10.0-19.99 en PIC 99 descarta la fracción: da 10..19.
       01  WS-HOURS                PIC 99.
       01  WS-ENTRIES              PIC 9 VALUE 0.

      * ---- las categorías: cuatro FILLER, vistos como tabla --------
      * REDEFINES pone otra descripción sobre los mismos 52 bytes.
       01  CATEGORY-NAMES.
           05  FILLER              PIC X(13) VALUE "Reuniones".
           05  FILLER              PIC X(13) VALUE "Programación".
           05  FILLER              PIC X(13) VALUE "Depuración".
           05  FILLER              PIC X(13) VALUE "Aprendizaje".
       01  CATEGORY-TABLE REDEFINES CATEGORY-NAMES.
           05  CATEGORY            PIC X(13) OCCURS 4 TIMES.
       01  WS-CAT-IX               PIC 9.

      * ---- id de ejecución y semilla aleatoria --------------------
      * CURRENT-DATE tiene 21 caracteres: YYYYMMDDhhmmssff y luego el
      * desfase UTC. ff son centésimas de segundo.
       01  WS-NOW                  PIC X(21).
       01  WS-PID                  PIC 9(9).
       01  WS-PID-TEXT             PIC Z(8)9.
       01  WS-RUN-ID               PIC X(30).
       01  WS-SEED                 PIC 9(9).
       01  WS-IGNORED              USAGE COMP-2.

      * ---- la semana ISO-8601, con aritmética de fechas ----------
       01  WS-TODAY                PIC 9(8).
       01  WS-DAY                  PIC 9(7).
       01  WS-THURSDAY             PIC 9(7).
       01  WS-ISO-YEAR             PIC 9(4).
       01  WS-ISO-WEEK             PIC 99.
       01  WS-WEEK                 PIC X(8).

      * ---- archivos e intérprete de comandos ----------------------
       01  WS-HOME                 PIC X(300).
       01  WS-BASE                 PIC X(300).
       01  WS-DIR                  PIC X(320).
       01  WS-DB-PATH              PIC X(360).
       01  WS-SQL-PATH             PIC X(360).
       01  WS-CMD                  PIC X(1200).
       01  WS-LINE                 PIC X(400).
       01  WS-TAB                  PIC X VALUE X"09".

       PROCEDURE DIVISION.
       MAIN-PARAGRAPH.
           PERFORM SET-UP
           PERFORM OPEN-SCRIPT
           DISPLAY "# DEMO ONLY run " FUNCTION TRIM(WS-RUN-ID)

      * ---- todo el reto -----------------------------------------
           PERFORM DRAW-CARD UNTIL OVER-FORTY

           PERFORM COMMIT-SCRIPT
           DISPLAY "# committed total=" WS-TOTAL
               " entries=" WS-ENTRIES " DEMO ONLY"
           DISPLAY "# PERFORM UNTIL an 88-level: the stop rule is"
               " declared in the DATA DIVISION"
           MOVE 0 TO RETURN-CODE
           STOP RUN.

      * Una tarjeta: elige la categoría, saca las horas, lleva los
      * totales, muestra la fila y agrega su INSERT al script.
       DRAW-CARD.
           COMPUTE WS-CAT-IX = FUNCTION MOD(WS-ENTRIES, 4) + 1
           COMPUTE WS-HOURS = 10 + FUNCTION RANDOM * 10
           ADD WS-HOURS TO WS-TOTAL
           ADD 1 TO WS-ENTRIES
           DISPLAY FUNCTION TRIM(CATEGORY(WS-CAT-IX)) WS-TAB
               WS-HOURS WS-TAB WS-TOTAL WS-TAB WS-WEEK WS-TAB
               "DEMO ONLY"
      * Es seguro solo porque cada valor es un número calculado aquí o
      * una de cuatro palabras fijas. No copies este patrón.
           MOVE SPACES TO WS-LINE
           STRING "INSERT INTO demo_timecards(run_id,category,hours,"
               "running_total,iso_week,created_at) VALUES('"
               FUNCTION TRIM(WS-RUN-ID) "','"
               FUNCTION TRIM(CATEGORY(WS-CAT-IX)) "',"
               WS-HOURS "," WS-TOTAL ",'" WS-WEEK
               "',datetime('now'));"
               DELIMITED BY SIZE INTO WS-LINE
           WRITE SQL-LINE FROM WS-LINE.

       SET-UP.
           MOVE FUNCTION CURRENT-DATE TO WS-NOW
           CALL "C$GETPID" RETURNING WS-PID
           MOVE WS-PID TO WS-PID-TEXT
      * El id es la marca de tiempo más el id del proceso, así que
      * dos ejecuciones en la misma centésima tienen ids distintos.
           MOVE SPACES TO WS-RUN-ID
           STRING WS-NOW(1:16) "-" FUNCTION TRIM(WS-PID-TEXT)
               DELIMITED BY SIZE INTO WS-RUN-ID
      * RANDOM con argumento siembra el generador; las llamadas
      * siguientes sin argumento continúan la secuencia.
           COMPUTE WS-SEED = FUNCTION MOD(
               FUNCTION NUMVAL(WS-NOW(9:8)) * 7919 + WS-PID,
               999999937)
           COMPUTE WS-IGNORED = FUNCTION RANDOM(WS-SEED)
           PERFORM WORK-OUT-WEEK
           ACCEPT WS-BASE FROM ENVIRONMENT "XDG_DATA_HOME"
           IF WS-BASE = SPACES
               ACCEPT WS-HOME FROM ENVIRONMENT "HOME"
               STRING FUNCTION TRIM(WS-HOME) "/.local/share"
                   DELIMITED BY SIZE INTO WS-BASE
           END-IF
           STRING FUNCTION TRIM(WS-BASE) "/Cobol"
               DELIMITED BY SIZE INTO WS-DIR
           STRING FUNCTION TRIM(WS-DIR) "/demo-timecards.db"
               DELIMITED BY SIZE INTO WS-DB-PATH
           STRING FUNCTION TRIM(WS-DIR) "/run-"
               FUNCTION TRIM(WS-RUN-ID) ".sql"
               DELIMITED BY SIZE INTO WS-SQL-PATH.

      * INTEGER-OF-DATE cuenta días desde 1601-01-01 (día 1), que fue
      * lunes, así que MOD(día - 1, 7) es 0 en lunes. Una semana ISO
      * pertenece al año en que cae su jueves, y la semana 1 es la
      * semana que contiene el primer jueves del año.
       WORK-OUT-WEEK.
           MOVE WS-NOW(1:8) TO WS-TODAY
           COMPUTE WS-DAY = FUNCTION INTEGER-OF-DATE(WS-TODAY)
           COMPUTE WS-THURSDAY =
               WS-DAY - FUNCTION MOD(WS-DAY - 1, 7) + 3
           COMPUTE WS-ISO-YEAR =
               FUNCTION DATE-OF-INTEGER(WS-THURSDAY) / 10000
           COMPUTE WS-ISO-WEEK = (WS-THURSDAY -
               FUNCTION INTEGER-OF-DATE(WS-ISO-YEAR * 10000 + 101))
               / 7 + 1
           STRING WS-ISO-YEAR "-W" WS-ISO-WEEK
               DELIMITED BY SIZE INTO WS-WEEK.

      * El intérprete de comandos se usa dos veces: para crear aquí la
      * carpeta de datos y para pasarle a sqlite3 el script terminado en
      * COMMIT-SCRIPT. La regla DEMO ONLY vive en la tabla:
      * CHECK(demo_only=1) impide guardar una fila que no sea demo.
       OPEN-SCRIPT.
           MOVE SPACES TO WS-CMD
           STRING "mkdir -p '" FUNCTION TRIM(WS-DIR) "'"
               DELIMITED BY SIZE INTO WS-CMD
           CALL "SYSTEM" USING WS-CMD
           OPEN OUTPUT SQL-SCRIPT
           MOVE SPACES TO WS-LINE
           STRING "CREATE TABLE IF NOT EXISTS demo_timecards("
               "id INTEGER PRIMARY KEY,run_id TEXT,category TEXT,"
               "hours INTEGER,running_total INTEGER,iso_week TEXT,"
               "created_at TEXT,demo_only INTEGER NOT NULL DEFAULT 1 "
               "CHECK(demo_only=1));"
               DELIMITED BY SIZE INTO WS-LINE
           WRITE SQL-LINE FROM WS-LINE
           WRITE SQL-LINE FROM "BEGIN;".

      * El script se borra solo si sqlite3 tuvo éxito, así que una
      * ejecución fallida lo deja para que lo mires.
       COMMIT-SCRIPT.
           WRITE SQL-LINE FROM "COMMIT;"
           CLOSE SQL-SCRIPT
           MOVE SPACES TO WS-CMD
           STRING "sqlite3 -bail '" FUNCTION TRIM(WS-DB-PATH)
               "' < '" FUNCTION TRIM(WS-SQL-PATH)
               "' && rm -f '" FUNCTION TRIM(WS-SQL-PATH) "'"
               DELIMITED BY SIZE INTO WS-CMD
           CALL "SYSTEM" USING WS-CMD
           IF RETURN-CODE NOT = 0
               DISPLAY "sqlite3 failed; the script is still at "
                   FUNCTION TRIM(WS-SQL-PATH) UPON SYSERR
               MOVE 1 TO RETURN-CODE
               STOP RUN
           END-IF.
