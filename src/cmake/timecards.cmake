# DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo XDG_DATA_HOME. Mira README.md.
#
# Ejecútalo con:  cmake -P timecards.cmake        (agrega -DPOP=1 para hacerlo en una ventana nueva de Windows Terminal)
#
#     for ( seed ; test ; iterate ) ;
#
# Todo el programa es UN while() sin cuerpo. Su condición es una coincidencia de regex (MATCHES), y una coincidencia exitosa
# deja sus capturas en CMAKE_MATCH_1..5. Esas son variables comunes, y while() vuelve a expandir su condición en
# cada vuelta, así que cada vuelta arma su cadena de texto y su patrón con las capturas de la vuelta anterior. Esa es
# la máquina: los registros son el estado, la tabla de consulta de las horas está en la cadena de texto, la regla de parada es un
# literal de 41 caracteres, y el bucle termina cuando la coincidencia dice que no. No hay function(), macro(), math(),
# list(GET) ni cmake_language() en el bucle, y nada en su cuerpo, porque no tiene.
#
# El anfitrión solo siembra los registros (una cinta de dígitos al azar) antes del bucle y reporta después.
cmake_minimum_required(VERSION 3.19)

if(POP)
  # Sin puntos y coma en ningún lugar de esta línea de comandos: wt.exe los trata como su propio separador de subcomandos.
  execute_process(COMMAND wt.exe -w new new-tab --title "DEMO ONLY"
                          wsl.exe -d $ENV{WSL_DISTRO_NAME} --cd ${CMAKE_CURRENT_LIST_DIR}
                          -e ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_LIST_FILE})
  return()
endif()

# ---- semilla: los registros, y una cinta de dígitos al azar (un dígito = las horas de una tarjeta menos diez) ---
string(RANDOM LENGTH 1 ALPHABET 0123456789 first_digit)
string(RANDOM LENGTH 8 ALPHABET 0123456789 more_digits)
set(CMAKE_MATCH_1 "")                  # total hasta ahora, en unario (una tira de x)
set(CMAKE_MATCH_2 "${first_digit}")    # el dígito espiado en la vuelta anterior: la tarjeta de esta vuelta
set(CMAKE_MATCH_3 "${more_digits}")    # el resto de la cinta
set(CMAKE_MATCH_4 "")                  # tarjetas terminadas, en unario, separadas por guiones
set(CMAKE_MATCH_5 "")                  # horas de la tarjeta agregada en la vuelta anterior, en unario

# ---- la única sentencia -----------------------------------------------------------------------------------------------
# 1.ª prueba: NOT (el total hasta ahora + la última tarjeta son 41 x o más): la regla de parada, "exactamente 40 continúa". Va primero porque una coincidencia
#           que falla borra los registros y una que tiene éxito los reescribe, así que la coincidencia principal debe correr al final. OJO: AND no
#           se detiene en la primera prueba falsa: en la última vuelta la 2.ª prueba aún corre, y así la última tarjeta llega al registro (4).
# 2.ª prueba: arma "<total>|<tape>|<log>||0:<10 x's>|1:<11 x's>|...|9:<19 x's>|" con los registros de la vuelta anterior, y luego
#           la compara con un patrón que espía el siguiente dígito de la cinta (grupos 2,3), conserva el registro (4) y
#           busca las horas de esta tarjeta en la tabla con el dígito que el patrón empalma de la vuelta anterior (5).
while(NOT "${CMAKE_MATCH_1}${CMAKE_MATCH_5}" MATCHES "^xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      AND "${CMAKE_MATCH_1}${CMAKE_MATCH_5}|${CMAKE_MATCH_3}|${CMAKE_MATCH_4}${CMAKE_MATCH_5}-||\
0:xxxxxxxxxx|\
1:xxxxxxxxxxx|\
2:xxxxxxxxxxxx|\
3:xxxxxxxxxxxxx|\
4:xxxxxxxxxxxxxx|\
5:xxxxxxxxxxxxxxx|\
6:xxxxxxxxxxxxxxxx|\
7:xxxxxxxxxxxxxxxxx|\
8:xxxxxxxxxxxxxxxxxx|\
9:xxxxxxxxxxxxxxxxxxx|"
          MATCHES "^(x*)\\|([0-9])([0-9]*)\\|([^|]*)\\|.*\\|${CMAKE_MATCH_2}:(x*)\\|")
endwhile()

# ---- reporte: las tarjetas están en el registro, en unario; las longitudes son horas ------------------------------
string(REGEX MATCHALL "x+" cards "${CMAKE_MATCH_4}")
list(LENGTH cards n)
set(categories Meetings Coding Debugging Learning Meetings)   # una quinta tarjeta (cuatro 10 = exactamente 40) da la vuelta a Meetings
list(SUBLIST categories 0 ${n} categories)                  # ZIP_LISTS llega hasta la lista más larga
set(acc "")
set(rows "")
foreach(unary category IN ZIP_LISTS cards categories)
  string(APPEND acc "${unary}")
  string(LENGTH "${unary}" hours)
  string(LENGTH "${acc}" running)
  list(APPEND rows "${category}\t${hours}\t${running}")
endforeach()
string(LENGTH "${acc}" total)

# ---- semana ISO. string(TIMESTAMP) conoce %V pero no %G, así que el *año* ISO se corrige a mano -------------
string(TIMESTAMP stamp "%Y %m %V")
string(REPLACE " " ";" stamp "${stamp}")
list(GET stamp 0 year)
list(GET stamp 1 month)
list(GET stamp 2 week)
if(month STREQUAL "12" AND week STREQUAL "01")
  math(EXPR year "${year} + 1")
elseif(month STREQUAL "01" AND week GREATER 51)
  math(EXPR year "${year} - 1")
endif()
set(iso_week "${year}-W${week}")

# ---- SQLite (mismo esquema que las otras entradas) --------------------------------------------------------------
if(DEFINED ENV{XDG_DATA_HOME} AND NOT "$ENV{XDG_DATA_HOME}" STREQUAL "")
  set(data "$ENV{XDG_DATA_HOME}")
else()
  set(data "$ENV{HOME}/.local/share")
endif()
set(dir "${data}/CmakeChallenge")
set(db "${dir}/demo-timecards.db")
file(MAKE_DIRECTORY "${dir}")

file(WRITE "${dir}/.init.sql" [[
CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY,started_at TEXT);
CREATE TABLE IF NOT EXISTS demo_timecards(id INTEGER PRIMARY KEY,run_id INTEGER,category TEXT,hours INTEGER CHECK(hours BETWEEN 10 AND 19),running_total INTEGER,iso_week TEXT,created_at TEXT,demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));
CREATE TABLE IF NOT EXISTS stop_rule(ok INTEGER CONSTRAINT "stop rule fired: total exceeds 40" CHECK(ok=1));
INSERT INTO runs(started_at) VALUES(datetime('now','localtime'));
SELECT printf('# DEMO ONLY run %d',last_insert_rowid());
]])
execute_process(COMMAND sqlite3 -noheader "${db}" INPUT_FILE "${dir}/.init.sql")

set(sql "")
foreach(card IN LISTS rows)
  string(REPLACE "\t" ";" f "${card}")
  list(GET f 0 category)
  list(GET f 1 hours)
  list(GET f 2 running)
  file(APPEND /dev/stdout "${card}\t${iso_week}\tDEMO ONLY\n")
  string(APPEND sql "INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week,created_at) VALUES((SELECT max(id) FROM runs),'${category}',${hours},${running},'${iso_week}',datetime('now','localtime'));\n")
endforeach()
# La regla de parada, atestiguada por SQLite: insertar "total <= 40" en una columna CHECK(ok=1) falla cuando debe parar.
string(APPEND sql "INSERT INTO stop_rule SELECT coalesce((SELECT max(running_total) FROM demo_timecards WHERE run_id=(SELECT max(id) FROM runs)),0)<=40;\nDELETE FROM stop_rule;\n")
file(WRITE "${dir}/.rows.sql" "${sql}")
execute_process(COMMAND sqlite3 "${db}" INPUT_FILE "${dir}/.rows.sql")   # su error de CHECK va a stderr, a propósito
file(REMOVE "${dir}/.init.sql" "${dir}/.rows.sql")

file(APPEND /dev/stdout "# committed total=${total} entries=${n} DEMO ONLY\n")
file(APPEND /dev/stdout "# an empty while() went round ${n} times, once per card\n")

# ---- el resplandor, solo en una terminal real (el realpath de CMake sobre su stdout es /dev/pts/N, no una tubería) ---
file(REAL_PATH /proc/self/fd/1 stdout_path)
if(stdout_path MATCHES "^/dev/(pts|tty)")
  string(ASCII 27 ESC)
  set(ramp 232 234 236 238 240 242 244 246 248 250 252 254 254 252 250 248 246 244 242 240 238 236 234 232 0)
  set(first TRUE)
  foreach(shade IN LISTS ramp)
    set(up "")
    if(NOT first)
      set(up "${ESC}[1A")
    endif()
    set(first FALSE)
    if(shade EQUAL 0)
      file(APPEND /dev/stdout "${up}${ESC}[2K\n")
    else()
      if(shade GREATER 242)
        set(fg 30)
      else()
        set(fg 97)
      endif()
      file(APPEND /dev/stdout "${up}${ESC}[2K${ESC}[48;5;${shade}m${ESC}[${fg}m  DEMO ONLY  ${ESC}[0m\n")
    endif()
    execute_process(COMMAND ${CMAKE_COMMAND} -E sleep 0.06)
  endforeach()
endif()
