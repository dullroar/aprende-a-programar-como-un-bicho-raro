      * SOLO DEMO (DEMO ONLY). Tarjetas de horas ficticias, escritas en
      * un archivo SQLite temporal bajo XDG_DATA_HOME. Nada aquí toca
      * un sistema real de registro de horas.
      *
      * Ejecuta:  cobc -xj timecards.cob
      *
      * El mismo desafío que ../cobol, sin IF, sin PERFORM, sin
      * EVALUATE y sin UNTIL en ningún sitio. El flujo es GO TO y la
      * sentencia ALTER, que reescribe adónde salta un GO TO mientras
      * el programa corre. ALTER quedó obsoleta en 1985 y se borró
      * del estándar en 2002; GnuCOBOL aún la ejecuta, y avisa.
      *
      * - El bucle es un párrafo, NEXT-CARD, con un solo GO TO.
      * - El párrafo de cada categoría hace ALTER de ese GO TO para
      *   apuntar a la categoría siguiente. Ese es el ciclo.
      * - La regla de parada es un campo de dos dígitos, WS-HEADROOM,
      *   que empieza en 59. Se le suman las horas de cada tarjeta y
      *   se desborda (ON SIZE ERROR) justo cuando el total pasa de 40,
      *   porque 59 + 41 = 100 no cabe en PIC 99. El manejador del
      *   error de tamaño hace ALTER de NEXT-CARD a FINISH-RUN.
      *
      * Formato fijo: un * en la columna 7 es un comentario; el código
      * va en las columnas 8-72. Los párrafos corren en orden salvo que
      * un GO TO diga otra cosa, así que se lee de arriba abajo.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. TIMECARDS-WEIRD.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SQL-SCRIPT ASSIGN TO WS-SQL-PATH
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD  SQL-SCRIPT.
       01  SQL-LINE                PIC X(400).

       WORKING-STORAGE SECTION.
      * ---- el cable trampa -----------------------------------------
      * 59 + total cabe en dos dígitos si el total es 40 o menos.
      * La suma que daría 100 o más es un error de tamaño, y un
      * error de tamaño deja el campo como estaba.
       01  WS-HEADROOM             PIC 99 VALUE 59.
       01  WS-TOTAL                PIC 99 VALUE 0.
       01  WS-HOURS                PIC 99.
       01  WS-ENTRIES              PIC 9 VALUE 0.
       01  WS-CATEGORY             PIC X(9).

      * ---- id de ejecución y semilla aleatoria ---------------------
       01  WS-NOW                  PIC X(21).
       01  WS-PID                  PIC 9(9).
       01  WS-PID-TEXT             PIC Z(8)9.
       01  WS-RUN-ID               PIC X(30).
       01  WS-SEED                 PIC 9(9).
       01  WS-IGNORED              USAGE COMP-2.

      * ---- la semana ISO-8601, con aritmética de fechas -------------
       01  WS-TODAY                PIC 9(8).
       01  WS-DAY                  PIC 9(7).
       01  WS-THURSDAY             PIC 9(7).
       01  WS-ISO-YEAR             PIC 9(4).
       01  WS-ISO-WEEK             PIC 99.
       01  WS-WEEK                 PIC X(8).

      * ---- adónde van los datos, elegido sin IF ---------------------
      * La opción 1 es $HOME/.local/share, la 2 es $XDG_DATA_HOME.
      * El subíndice es 1 + MIN(largo de XDG_DATA_HOME, 1): 1 si no
      * está definida, 2 si lo está.
       01  WS-HOME                 PIC X(300).
       01  WS-XDG                  PIC X(300).
       01  WS-XDG-LENGTH           PIC 9(4) VALUE 0.
       01  BASE-CHOICES.
           05  BASE-CHOICE         PIC X(300) OCCURS 2 TIMES.
       01  WS-BASE-IX              PIC 9.
       01  WS-DIR                  PIC X(320).
       01  WS-DB-PATH              PIC X(360).
       01  WS-SQL-PATH             PIC X(360).
       01  WS-CMD                  PIC X(1200).
       01  WS-LINE                 PIC X(400).
       01  WS-TAB                  PIC X VALUE X"09".

       PROCEDURE DIVISION.
       SET-UP.
           MOVE FUNCTION CURRENT-DATE TO WS-NOW
           CALL "C$GETPID" RETURNING WS-PID
           MOVE WS-PID TO WS-PID-TEXT
           MOVE SPACES TO WS-RUN-ID
           STRING WS-NOW(1:16) "-" FUNCTION TRIM(WS-PID-TEXT)
               DELIMITED BY SIZE INTO WS-RUN-ID
           COMPUTE WS-SEED = FUNCTION MOD(
               FUNCTION NUMVAL(WS-NOW(9:8)) * 7919 + WS-PID,
               999999937)
           COMPUTE WS-IGNORED = FUNCTION RANDOM(WS-SEED).

      * Misma aritmética que ../cobol: el día 1 (1601-01-01) fue lunes
      * y una semana ISO pertenece al año en que cae su jueves.
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

       CHOOSE-FOLDER.
           ACCEPT WS-HOME FROM ENVIRONMENT "HOME"
           ACCEPT WS-XDG FROM ENVIRONMENT "XDG_DATA_HOME"
           STRING FUNCTION TRIM(WS-HOME) "/.local/share"
               DELIMITED BY SIZE INTO BASE-CHOICE(1)
           MOVE WS-XDG TO BASE-CHOICE(2)
           INSPECT WS-XDG TALLYING WS-XDG-LENGTH
               FOR CHARACTERS BEFORE INITIAL SPACE
           COMPUTE WS-BASE-IX = 1 + FUNCTION MIN(WS-XDG-LENGTH, 1)
           STRING FUNCTION TRIM(BASE-CHOICE(WS-BASE-IX)) "/CobolWeird"
               DELIMITED BY SIZE INTO WS-DIR
           STRING FUNCTION TRIM(WS-DIR) "/demo-timecards.db"
               DELIMITED BY SIZE INTO WS-DB-PATH
           STRING FUNCTION TRIM(WS-DIR) "/run-"
               FUNCTION TRIM(WS-RUN-ID) ".sql"
               DELIMITED BY SIZE INTO WS-SQL-PATH.

      * El intérprete crea aquí la carpeta y corre sqlite3 al final.
      * CHECK(demo_only=1): no se guarda una fila que no sea demo.
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
           WRITE SQL-LINE FROM "BEGIN;"
           DISPLAY "# DEMO ONLY run " FUNCTION TRIM(WS-RUN-ID).

      * ---- el conmutador --------------------------------------------
      * NEXT-CARD es lo único que ALTER puede cambiar: un párrafo que
      * es exactamente un GO TO. Empieza apuntando a MEETINGS-CARD.
       NEXT-CARD.
           GO TO MEETINGS-CARD.

      * Cada categoría se nombra, recablea NEXT-CARD a la categoría
      * que sigue, y se une a RECORD-CARD. Nada cuenta módulo 4.
       MEETINGS-CARD.
           MOVE "Meetings" TO WS-CATEGORY
           ALTER NEXT-CARD TO PROCEED TO CODING-CARD
           GO TO RECORD-CARD.

       CODING-CARD.
           MOVE "Coding" TO WS-CATEGORY
           ALTER NEXT-CARD TO PROCEED TO DEBUGGING-CARD
           GO TO RECORD-CARD.

       DEBUGGING-CARD.
           MOVE "Debugging" TO WS-CATEGORY
           ALTER NEXT-CARD TO PROCEED TO LEARNING-CARD
           GO TO RECORD-CARD.

       LEARNING-CARD.
           MOVE "Learning" TO WS-CATEGORY
           ALTER NEXT-CARD TO PROCEED TO MEETINGS-CARD
           GO TO RECORD-CARD.

      * Una tarjeta. La última sentencia antes de GO TO NEXT-CARD es el
      * cable trampa: si el margen se desborda, NEXT-CARD se recablea a
      * FINISH-RUN, y así el mismo GO TO ahora termina la ejecución.
       RECORD-CARD.
           COMPUTE WS-HOURS = 10 + FUNCTION RANDOM * 10
           ADD WS-HOURS TO WS-TOTAL
           ADD 1 TO WS-ENTRIES
           DISPLAY FUNCTION TRIM(WS-CATEGORY) WS-TAB
               WS-HOURS WS-TAB WS-TOTAL WS-TAB WS-WEEK WS-TAB
               "DEMO ONLY"
      * Es seguro solo porque cada valor es un número calculado aquí o
      * una de cuatro palabras fijas. No copies este patrón.
           MOVE SPACES TO WS-LINE
           STRING "INSERT INTO demo_timecards(run_id,category,hours,"
               "running_total,iso_week,created_at) VALUES('"
               FUNCTION TRIM(WS-RUN-ID) "','"
               FUNCTION TRIM(WS-CATEGORY) "',"
               WS-HOURS "," WS-TOTAL ",'" WS-WEEK
               "',datetime('now'));"
               DELIMITED BY SIZE INTO WS-LINE
           WRITE SQL-LINE FROM WS-LINE
           ADD WS-HOURS TO WS-HEADROOM
               ON SIZE ERROR
                   ALTER NEXT-CARD TO PROCEED TO FINISH-RUN
           END-ADD
           GO TO NEXT-CARD.

      * Sin IF, un sqlite3 fallido no puede saltarse el resumen; en su
      * lugar el intérprete avisa por stderr y su estado pasa a ser el
      * código de salida del programa (SYSTEM devuelve estado * 256).
       FINISH-RUN.
           WRITE SQL-LINE FROM "COMMIT;"
           CLOSE SQL-SCRIPT
           MOVE SPACES TO WS-CMD
           STRING "sqlite3 -bail '" FUNCTION TRIM(WS-DB-PATH)
               "' < '" FUNCTION TRIM(WS-SQL-PATH)
               "' && rm -f '" FUNCTION TRIM(WS-SQL-PATH)
               "' || { echo 'sqlite3 failed; the script is still at "
               FUNCTION TRIM(WS-SQL-PATH) "' >&2; exit 1; }"
               DELIMITED BY SIZE INTO WS-CMD
           CALL "SYSTEM" USING WS-CMD
           COMPUTE RETURN-CODE = RETURN-CODE / 256
           DISPLAY "# committed total=" WS-TOTAL
               " entries=" WS-ENTRIES " DEMO ONLY"
           DISPLAY "# no IF, no PERFORM: ALTER kept rewiring one GO TO,"
               " and a two-digit field overflowing pulled the plug"
           STOP RUN.
