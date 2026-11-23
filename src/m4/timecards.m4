dnl DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite desechable bajo
dnl XDG_DATA_HOME. Nada de aquí toca un sistema real de registro de horas.
dnl
dnl Ejecuta:  m4 timecards.m4
dnl
dnl El reto: sumar tarjetas de 10 a 19 horas (Reuniones, Programación, Depuración,
dnl Aprendizaje, en ronda) hasta que el total acumulado pase de 40.  m4 no tiene
dnl instrucción de bucle ni variables: tiene macros, y lo que una macro expande
dnl se vuelve a escanear.  Así que el bucle es una macro que termina llamándose a sí misma,
dnl y la regla de parada es el ifelse que decide si lo hace.
dnl
dnl Este archivo usa GNU m4 (1.4.x o posterior).  Funciones solo de GNU, cada una marcada
dnl donde se usa: esyscmd (captura la salida de un comando), format, y
dnl eval de 32 bits.  Cada macro de aquí empieza con tc_ para que ninguna
dnl choque con una palabra del texto SQL, que m4 expandiría con mucho gusto.
dnl
dnl ---- 1. Haz que m4 sea seguro para nuestro texto -----------------------
dnl Por defecto # inicia un comentario, y un comentario se copia sin
dnl expandir macros: eso se comería nuestras líneas "# DEMO ONLY".  Y ' es la
dnl comilla de cierre, que las cadenas SQL necesitan.  Arregla ambas antes que nada.
changecom()dnl
changequote([, ])dnl
dnl Todo lo que hay hasta el divert(0) de abajo son definiciones; manda cualquier salida
dnl suelta (como el salto de línea tras cada define) a la desviación -1, o sea, a ninguna parte.
divert(-1)

dnl ---- 2. Estado: las macros son las variables ---------------------------
define([tc_n], 0)
define([tc_total], 0)

dnl Una semilla del SO: 3 bytes aleatorios como número decimal.  [GNU: esyscmd]
dnl Escalada para que quepa en el eval de 32 bits de m4, y nunca 0.  ifdef te deja fijarla
dnl (y la semana) desde la línea de comandos: m4 -Dtc_seed=12345 -Dtc_week=2026-W01 timecards.m4
ifdef([tc_seed], [],
  [define([tc_seed], eval(esyscmd([od -An -N3 -tu4 /dev/urandom | tr -d ' \n']) * 127 + 1))])
define([tc_run], esyscmd([date +%s | tr -d '\n'])-tc_seed)
ifdef([tc_week], [], [define([tc_week], esyscmd([date +%G-W%V | tr -d '\n']))])
define([tc_tab], format([%c], 9))   dnl [GNU: format]

dnl ---- 3. Un generador de números aleatorios, en aritmética de m4 ----------
dnl Park-Miller "estándar mínimo": seed = 16807 * seed mod (2^31 - 1).
dnl El truco de Schrage mantiene cada valor intermedio dentro de 32 bits, que es
dnl todo lo que tiene eval: 16807 * 127773 + 2836 = 2^31 - 1.
define([tc_next],
  [define([tc_seed], eval(16807 * (tc_seed % 127773) - 2836 * (tc_seed / 127773)))dnl
ifelse(eval(tc_seed < 0), 1, [define([tc_seed], eval(tc_seed + 2147483647))])])

dnl ---- 4. Ayudantes para armar texto --------------------------------------
dnl tc_category(N): la categoría de la tarjeta N.  ifelse es "si arg1 = arg2 entonces arg3",
dnl y después continúa en grupos de TRES (arg1 otra vez, arg2, arg3),
dnl con un último argumento suelto como el else.  Así que lo que se prueba tiene que
dnl repetirse en cada grupo: tc_pick recibe el número como $1 y lo repite.
define([tc_pick],
  [ifelse($1, 0, [Reuniones], $1, 1, [Programación], $1, 2, [Depuración], [Aprendizaje])])
define([tc_category], [tc_pick(eval(($1 - 1) % 4))])

dnl Los [] en los cuerpos de abajo son comillas vacías: separan un $1 del
dnl nombre de macro que sigue, que si no se pegaría en una sola palabra.
define([tc_row], [$1[]tc_tab[]$2[]tc_tab[]$3[]tc_tab[]tc_week[]tc_tab[]DEMO ONLY])
define([tc_insert],
  [INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week,created_at) VALUES('tc_run','$1',$2,$3,'tc_week',datetime('now'));
])

dnl El script SQL es una macro que crece: defn devuelve el texto de una macro,
dnl entre comillas, así que añadir es "redefínete como tú misma más algo".
define([tc_sql], [BEGIN;
CREATE TABLE IF NOT EXISTS demo_timecards(id INTEGER PRIMARY KEY,run_id TEXT,category TEXT,hours INTEGER,running_total INTEGER,iso_week TEXT,created_at TEXT,demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));
])
define([tc_append], [define([tc_sql], defn([tc_sql])[$1])])

dnl ---- 5. El reto ------------------------------------------------------
dnl Una tarjeta: saca, suma, recuerda el INSERT, imprime la fila, y luego para
dnl o se expande otra vez.  El texto que devuelve una macro se reescanea,
dnl así que la última palabra de tc_card es lo que la vuelve un bucle.
define([tc_card],
  [tc_next()dnl
define([tc_hours], eval(10 + tc_seed / 1024 % 10))dnl
define([tc_n], incr(tc_n))dnl
define([tc_total], eval(tc_total + tc_hours))dnl
tc_append(tc_insert(tc_category(tc_n), tc_hours, tc_total))dnl
tc_row(tc_category(tc_n), tc_hours, tc_total)
ifelse(eval(tc_total > 40), 1, [], [tc_card()])])

dnl ---- 6. Ejecútalo -------------------------------------------------------
divert(0)dnl
# DEMO ONLY run tc_run
tc_card()dnl
# committed total=tc_total entries=tc_n DEMO ONLY
# no loop statement: [tc_card] expands itself again until ifelse says stop, and m4 is the whole program
divert(-1)

dnl Guardar: entrega el script terminado a sqlite3 por medio del intérprete de comandos.  El intérprete
dnl solo elige la carpeta y ejecuta sqlite3; cada byte del SQL lo hizo m4.
dnl El terminador va entre comillas para que el intérprete deje en paz el SQL.  [syscmd es POSIX]
syscmd([d="${XDG_DATA_HOME:-$HOME/.local/share}/M4"; mkdir -p "$d" && sqlite3 "$d/demo-timecards.db" <<'END_OF_DEMO_SQL'
]defn([tc_sql])[COMMIT;
END_OF_DEMO_SQL
])
ifelse(sysval, 0, [], [errprint([sqlite3 failed
])m4exit(1)])
