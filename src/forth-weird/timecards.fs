\ DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite desechable bajo XDG_DATA_HOME.
\ Nada de esto toca un sistema real de registro de horas.
\
\ Ejecuta:  gforth timecards.fs
\
\ EL TRUCO: este programa es una máquina de dos registros.
\   * La memoria es la pila de datos.  No hay ni una VARIABLE en el archivo.
\   * El contador de programa es >IN, la posición de lectura del intérprete de texto.
\ No hay BEGIN, UNTIL, WHILE, IF, DO, CASE ni recursión en ningún sitio.  El
\ "bucle" es una línea de texto fuente que el intérprete lee, y que se
\ lee OTRA VEZ porque REWIND? mueve >IN hacia atrás.  Entre pasadas el total
\ acumulado, el número de tarjeta y el destino del rebobinado viven en la pila, intactos.
\
\ La única línea que debes leer es la marcada  <== THE LOOP  cerca del final.

require random.fs

0 value run-id                      \ identifica las filas de esta ejecución en la tabla
0 value sqlite                      \ id de archivo de la tubería hacia sqlite3
create week-buf 16 allot            \ el texto de la semana ISO, fijado una vez y nunca cambiado

\ ---------------------------------------------------------------- tuberías

: meetings   ( -- c-addr u )  s" Reuniones" ;
: coding     ( -- c-addr u )  s" Programación" ;
: debugging  ( -- c-addr u )  s" Depuración" ;
: learning   ( -- c-addr u )  s" Aprendizaje" ;
create categories  ' meetings , ' coding , ' debugging , ' learning ,
: category$  ( n -- c-addr u )  4 mod cells categories + @ execute ;

: random-hours  ( -- n )  10 random 10 + ;
: u$            ( u -- c-addr u )  0 <# #s #> ;
: .num          ( n -- )  0 .r ;
: tab           ( -- )  9 emit ;
: quoted        ( c-addr u -- )  [char] ' emit type [char] ' emit ;
: comma         ( -- )  [char] , emit ;
: 3dup          ( a b c -- a b c a b c )  2 pick 2 pick 2 pick ;

: read-week     ( -- )
  s" date +%G-W%V" r/o open-pipe throw >r
  week-buf 16 r@ read-line throw 2drop
  r> close-pipe throw drop ;
\ %G-W%V siempre mide ocho caracteres (2026-W46), así que no hay que recordar ninguna longitud.
: week$         ( -- c-addr u )  week-buf 8 ;

: open-sqlite   ( -- )
  s\" d=${XDG_DATA_HOME:-$HOME/.local/share}/ForthWeird; mkdir -p \"$d\"; exec sqlite3 \"$d/demo-timecards.db\""
  w/o open-pipe throw to sqlite ;
: close-sqlite  ( -- )  sqlite close-pipe throw abort" sqlite3 reported an error" ;
: >sqlite       ( xt -- )  sqlite outfile-execute ;

: .schema       ( -- )
  ." CREATE TABLE IF NOT EXISTS demo_timecards("
  ." id INTEGER PRIMARY KEY,run_id TEXT,category TEXT,hours INTEGER,"
  ." running_total INTEGER,iso_week TEXT,created_at TEXT,"
  ." demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));" cr
  ." BEGIN;" cr ;
: .commit       ( -- )  ." COMMIT;" cr ;

\ n es la posición de la tarjeta (elige la categoría), h sus horas, t el total tras ella.
: .insert       ( n h t -- )
  ." INSERT INTO demo_timecards"
  ." (run_id,category,hours,running_total,iso_week,created_at) VALUES("
  run-id u$ quoted comma
  2 pick category$ quoted comma
  swap .num comma
  .num comma
  week$ quoted comma
  ." datetime('now'));" cr
  drop ;                                                  \ la n que quedó debajo
: .row          ( n h t -- )
  >r swap category$ type tab
  .num tab
  r> .num tab
  week$ type tab
  ." DEMO ONLY" cr ;

\ ---------------------------------------------------------------- la máquina

\ Una tarjeta.  El estado de entrada es ( n total ); el de salida es ( n+1 total' ).
: card          ( n total -- n' total' )
  random-hours tuck +                                     ( n h t )
  3dup .row
  3dup ['] .insert >sqlite
  >r drop 1+ r> ;                                         ( n+1 t )

\ Ejecuta una tarjeta mientras el ancla viaja debajo de ella en la pila de retorno.
: step          ( n total anchor -- n' total' anchor )  >r card r> ;

\ El salto.  Si el total sigue en 40 o menos, devuelve >IN a ANCHOR; si no,
\ déjalo quieto.  Sin ramas: la bandera (-1 o 0) enmascara la distancia a recorrer.
: rewind?        ( n total anchor -- n total anchor )
  over 41 <                                               ( ... flag )
  over >in @ - and  >in @ + >in ! ;

\ ---------------------------------------------------------------- principal

utime drop dup seed ! to run-id   read-week   open-sqlite
." # DEMO ONLY run " run-id .num cr
' .schema >sqlite
0 0 >in @ step rewind?                                     \ <== THE LOOP  ( n total anchor )
drop                                                      \ el ancla ya cumplió su trabajo
' .commit >sqlite   close-sqlite
swap ." # committed total=" over .num ."  entries=" .num ."  DEMO ONLY" cr
drop
." # no loop word anywhere: the text interpreter was rewound until the total passed 40" cr
bye
