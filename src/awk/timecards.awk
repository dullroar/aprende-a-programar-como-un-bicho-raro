#!/usr/bin/awk -f
# DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo
# XDG_DATA_HOME. Nada de esto toca un sistema real de registro de horas.
#
# Run:  awk -f timecards.awk
#
# El desafío: suma tarjetas de 10 a 19 horas (Meetings, Coding, Debugging,
# Learning, una tras otra) hasta que el total acumulado pase de 40.  awk POSIX
# portátil: corre sin cambios con gawk, mawk, el one-true-awk y el
# awk de busybox.  No hay archivo de entrada, así que todo el programa es la
# regla BEGIN; la versión rara (../awk-weird) deja que el bucle principal de awk haga el trabajo.

# El texto de la primera línea de salida de un comando.
function command_line(command,    line) {
    line = ""
    command | getline line
    close(command)
    return line
}

# TEXT como una sola palabra de shell.  split() sobre la comilla evita las reglas de
# escape de la cadena de reemplazo de awk, que difieren entre implementaciones.
function shell_quote(text,    parts, n, i, quoted) {
    n = split(text, parts, "'")
    quoted = parts[1]
    for (i = 2; i <= n; i++)
        quoted = quoted "'\\''" parts[i]
    return "'" quoted "'"
}

# TEXT como literal de cadena SQL: duplicar las comillas es toda la regla.
function sql_quote(text) {
    gsub(/'/, "''", text)
    return "'" text "'"
}

# 10..19.  rand() está en [0,1), así que int() de eso por 10 da 0..9.
function random_hours() {
    return HOURS_MIN + int(rand() * (HOURS_MAX - HOURS_MIN + 1))
}

# Una fila separada por tabuladores.  Asignar a un campo reconstruye $0 unido con OFS,
# así que print sin argumentos imprime el registro terminado.
function print_row(name, worked, running, iso) {
    $0 = ""
    $1 = name
    $2 = worked
    $3 = running
    $4 = iso
    $5 = "DEMO ONLY"
    print
}

function sql_insert(run_id, name, worked, running, iso) {
    return sprintf("INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week,created_at) " \
                   "VALUES(%s,%s,%d,%d,%s,datetime('now'));",
                   sql_quote(run_id), sql_quote(name), worked, running, sql_quote(iso))
}

BEGIN {
    HOURS_MIN = 10
    HOURS_MAX = 19
    LIMIT = 40
    total = 0
    cards = 0
    OFS = "\t"
    split("Meetings Coding Debugging Learning", CATEGORY, " ")

    # Una semilla del sistema operativo, y un id de ejecución hecho con el reloj y la semilla.
    seed = command_line("od -An -N4 -tu4 /dev/urandom") + 0
    srand(seed)
    run = command_line("date +%s") "-" seed
    week = command_line("date +%G-W%V")

    # Dónde vive la base de datos temporal.
    dir = ENVIRON["XDG_DATA_HOME"]
    if (dir == "")
        dir = ENVIRON["HOME"] "/.local/share"
    dir = dir "/Awk"
    system("mkdir -p " shell_quote(dir))
    sqlite = "sqlite3 " shell_quote(dir "/demo-timecards.db")

    # La regla DEMO ONLY vive en la tabla: CHECK(demo_only=1).
    print "BEGIN;" | sqlite
    print "CREATE TABLE IF NOT EXISTS demo_timecards(id INTEGER PRIMARY KEY,run_id TEXT," \
          "category TEXT,hours INTEGER,running_total INTEGER,iso_week TEXT,created_at TEXT," \
          "demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));" | sqlite

    print "# DEMO ONLY run " run

    # El desafío.  La prueba se hace antes de cada sorteo, así que la tarjeta que
    # cruza la línea es la última que se suma.
    while (total <= LIMIT) {
        hours = random_hours()
        total += hours
        category = CATEGORY[cards++ % 4 + 1]
        print_row(category, hours, total, week)
        print sql_insert(run, category, hours, total, week) | sqlite
    }

    print "COMMIT;" | sqlite
    if (close(sqlite) != 0) {
        print "sqlite3 reported an error" > "/dev/stderr"
        exit 1
    }
    print "# committed total=" total " entries=" cards " DEMO ONLY"
    print "# a BEGIN-only awk program: arrays, a pipe to sqlite3, and fields rebuilding each row"
}
