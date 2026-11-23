\ DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite desechable bajo XDG_DATA_HOME.
\ Nada de esto toca un sistema real de registro de horas.
\
\ Ejecuta:  gforth timecards.fs
\
\ El desafío: suma tarjetas de 10 a 19 horas (Meetings, Coding, Debugging, Learning,
\ una tras otra) hasta que el total acumulado pase de 40.  En Forth eso es un
\ BEGIN ... UNTIL en la palabra RUN.  Todo lo demás son palabras pequeñas que
\ hacen una sola cosa, construidas de abajo arriba: cada palabra usa las anteriores.
\
\ Convenciones: toda palabra lleva un comentario de pila ( antes -- después ); un $ final
\ significa "una cadena en la pila como c-addr u"; las palabras que imprimen empiezan con un punto.

require random.fs

\ ---------------------------------------------------------------- estado

variable total                      \ total acumulado de horas
variable cards                      \ tarjetas escritas hasta ahora
variable run-id                     \ permite encontrar en la tabla las filas de esta ejecución
variable week-len                   \ longitud del texto de la semana ISO en WEEK-BUF
create week-buf 16 allot            \ "2026-W46" y su salto de línea caben de sobra
0 value sqlite                      \ id de archivo de la tubería hacia sqlite3

\ ---------------------------------------------------------------- categorías

\ Una palabra mínima por categoría y una tabla con sus tokens de ejecución.
\ ' (tick) convierte un nombre en un xt; EXECUTE lo ejecuta y devuelve la cadena.
: meetings   ( -- c-addr u )  s" Meetings" ;
: coding     ( -- c-addr u )  s" Coding" ;
: debugging  ( -- c-addr u )  s" Debugging" ;
: learning   ( -- c-addr u )  s" Learning" ;

create categories  ' meetings , ' coding , ' debugging , ' learning ,

: category$  ( n -- c-addr u )  4 mod cells categories + @ execute ;

\ ---------------------------------------------------------------- números y texto

: random-hours  ( -- n )  10 random 10 + ;               \ 10 random is 0..9
: u$            ( u -- c-addr u )  0 <# #s #> ;          \ number to text, no padding
: .num          ( n -- )  0 .r ;                         \ print with no leading space
: tab           ( -- )  9 emit ;
: quoted        ( c-addr u -- )  [char] ' emit type [char] ' emit ;
: comma         ( -- )  [char] , emit ;

: week$         ( -- c-addr u )  week-buf week-len @ ;

\ Pide a date(1) la semana ISO-8601 en vez de reimplementar el calendario.
: read-week     ( -- )
  s" date +%G-W%V" r/o open-pipe throw >r
  week-buf 16 r@ read-line throw drop week-len !
  r> close-pipe throw drop ;

\ ---------------------------------------------------------------- SQLite

\ Inicia sqlite3 con una tubería en su stdin.  El shell se usa solo para elegir (y
\ crear) la carpeta desechable.  La regla DEMO ONLY vive en la propia tabla:
\ CHECK(demo_only=1) significa que una fila que no sea de demo no se puede guardar.
: open-sqlite   ( -- )
  s\" d=${XDG_DATA_HOME:-$HOME/.local/share}/Forth; mkdir -p \"$d\"; exec sqlite3 \"$d/demo-timecards.db\""
  w/o open-pipe throw to sqlite ;

: close-sqlite  ( -- )  sqlite close-pipe throw abort" sqlite3 reported an error" ;

\ OUTFILE-EXECUTE ejecuta un xt con toda la salida redirigida a un id de archivo.  Esa
\ palabra es cómo las palabras de impresión comunes (." CR TYPE) se vuelven SQL.
: >sqlite       ( xt -- )  sqlite outfile-execute ;

: .schema       ( -- )
  ." CREATE TABLE IF NOT EXISTS demo_timecards("
  ." id INTEGER PRIMARY KEY,run_id TEXT,category TEXT,hours INTEGER,"
  ." running_total INTEGER,iso_week TEXT,created_at TEXT,"
  ." demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));" cr
  ." BEGIN;" cr ;

: .commit       ( -- )  ." COMMIT;" cr ;

\ Es seguro solo porque cada valor es un número que calculamos o una de cuatro palabras fijas.
: .insert       ( hours -- )
  ." INSERT INTO demo_timecards"
  ." (run_id,category,hours,running_total,iso_week,created_at) VALUES("
  run-id @ u$ quoted comma
  cards @ 1- category$ quoted comma
  .num comma
  total @ .num comma
  week$ quoted comma
  ." datetime('now'));" cr ;

\ ---------------------------------------------------------------- una tarjeta

: .row          ( hours -- )
  cards @ 1- category$ type tab
  .num tab
  total @ .num tab
  week$ type tab
  ." DEMO ONLY" cr ;

: card          ( -- )
  random-hours
  dup total +!  1 cards +!
  dup .row
  ['] .insert >sqlite ;                                  \ .insert consume las horas que quedan en la pila

: over-40?      ( -- flag )  total @ 40 > ;

\ Todo el desafío.  BEGIN ... UNTIL repite hasta que la bandera sea verdadera.
: run           ( -- )  begin card over-40? until ;

\ ---------------------------------------------------------------- principal

: reset         ( -- )  0 total !  0 cards !  utime drop dup seed ! run-id ! ;

: main          ( -- )
  reset  read-week  open-sqlite
  ." # DEMO ONLY run " run-id @ .num cr
  ['] .schema >sqlite
  run
  ['] .commit >sqlite
  close-sqlite
  ." # committed total=" total @ .num ."  entries=" cards @ .num ."  DEMO ONLY" cr
  ." # begin ... until, and an outfile-execute to point the output at SQLite" cr ;

main
bye
