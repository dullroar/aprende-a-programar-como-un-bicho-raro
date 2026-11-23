#!/usr/bin/env tclsh
# DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite desechable bajo
# XDG_DATA_HOME. Nada de aquí toca un sistema real de registro de horas.
#
# Ejecuta:  tclsh timecards.tcl            (texto)
#       tclsh timecards.tcl --gui      (la ventana también se construye a partir de filas; --seconds N la cierra)
#
# El desafío: suma tarjetas de 10 a 19 horas hasta que el total acumulado pase de 40.
#
# LA ACROBACIA.  Este archivo no define ningún bucle de Tcl ni ningún proc de Tcl que reparta o
# imprima una tarjeta. El programa son filas de una tabla de SQLite, y un INSERT lo arranca:
#
#   * el bucle es un disparador recursivo de SQLite: insertar una tarjeta activa el
#     disparador, que inserta la siguiente tarjeta, hasta que el total pasa de 40;
#   * cada número, nombre y línea impresa sale de procs de Tcl que viven como
#     TEXT en una tabla, traídos bajo demanda por un manejador `unknown`;
#   * SQL llama a esos procs mediante un comando de Tcl registrado como función de SQL;
#   * con --gui, hasta los widgets de la ventana son filas.
#
# El Tcl de abajo solo instala esos tres enganches, le entrega el programa a SQLite
# y ejecuta el INSERT.

package require sqlite3

set dir [expr {[info exists ::env(XDG_DATA_HOME)] && $::env(XDG_DATA_HOME) ne ""
    ? $::env(XDG_DATA_HOME) : [file join $::env(HOME) .local share]}]
file mkdir [file join $dir TclWeird]
sqlite3 db [file join $dir TclWeird demo-timecards.db]

# Enganche 1: una función de SQL, tcl(command, args...), que ejecuta un comando de Tcl.
proc call {command args} {
    $command {*}$args
}
db function tcl call

# Enganche 2: Tcl llama a `unknown` para cualquier comando que no exista. El nuestro busca
# el nombre en la tabla tcl_code, lo define como un proc a partir de la fila y
# reintenta la llamada. La base de datos es la ruta de la biblioteca.
set loaded {}
rename unknown _unknown
proc unknown {name args} {
    if {[db exists {SELECT 1 FROM tcl_code WHERE name = $name}]} {
        db eval {SELECT params, body FROM tcl_code WHERE name = $name} {}
        proc $name $params $body
        lappend ::loaded $name
        return [uplevel 1 [list $name {*}$args]]
    }
    tailcall _unknown $name {*}$args
}

# Enganche 3: el programa, como SQL. Las tablas y los disparadores TEMP viven solo mientras dura
# esta conexión, así que el archivo en disco no guarda nada salvo las tarjetas de horas.
# (Tcl dentro de SQL dentro de Tcl: las llaves se anidan y aquí no se sustituye nada.)
db eval {
    PRAGMA recursive_triggers = ON;          -- without this the trigger below fires once

    CREATE TABLE IF NOT EXISTS demo_timecards(
        id INTEGER PRIMARY KEY, run_id TEXT, category TEXT, hours INTEGER,
        running_total INTEGER, iso_week TEXT, created_at TEXT,
        demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));

    CREATE TEMP TABLE tcl_code(name TEXT PRIMARY KEY, params TEXT, body TEXT);
    INSERT INTO tcl_code VALUES
        ('init',     '',
         'expr {srand([clock microseconds] ^ [pid])}'),
        ('runid',    '',
         'set ::runid [clock seconds]-[pid]
          puts "# DEMO ONLY run $::runid"
          set ::runid'),
        ('week',     '',
         'clock format [clock seconds] -format %G-W%V'),
        ('hours',    '',
         'expr {10 + int(rand() * 10)}'),
        ('category', 'n',
         'lindex {Meetings Coding Debugging Learning} [expr {($n - 1) % 4}]'),
        ('born',     'category hours total week',
         'puts [join [list $category $hours $total $week {DEMO ONLY}] \t]
          set ::summary "DEMO ONLY: running total $total"
          if {[llength [info commands .cards]]} {
              .cards insert {} end -values [list $category $hours $total $week]
              update
              after 400
          }');

    -- The window, as data: one Tk command per row, run in order.
    CREATE TEMP TABLE ui(id INTEGER PRIMARY KEY, command TEXT);
    INSERT INTO ui(command) VALUES
        ('ttk::treeview .cards -columns {category hours total week} -show headings -height 6'),
        ('.cards heading category -text Category'),
        ('.cards heading hours -text Hours'),
        ('.cards heading total -text Total'),
        ('.cards heading week -text Week'),
        ('pack .cards -fill both -expand 1 -padx 8 -pady 8'),
        ('ttk::label .note -textvariable ::summary'),
        ('pack .note -pady {0 8}');

    -- One row, where a card's hours wait. The hours are drawn into it once and read from it twice (as the hours and in the total), so no
    -- result depends on how often SQLite chooses to call the random function.
    CREATE TEMP TABLE draw(h INTEGER);
    INSERT INTO draw VALUES (0);

    -- The loop. Each card that is inserted prints itself (born), then inserts
    -- the next one while the total is still 40 or less. The WHERE is the stop rule.
    CREATE TEMP TRIGGER next_card AFTER INSERT ON main.demo_timecards
    BEGIN
        SELECT tcl('born', NEW.category, NEW.hours, NEW.running_total, NEW.iso_week);
        UPDATE draw SET h = tcl('hours') WHERE NEW.running_total <= 40;
        INSERT INTO demo_timecards(run_id, category, hours, running_total, iso_week, created_at)
        SELECT NEW.run_id,
               tcl('category', (SELECT count(*) FROM demo_timecards WHERE run_id = NEW.run_id) + 1),
               h, NEW.running_total + h, NEW.iso_week, datetime('now')
        FROM draw
        WHERE NEW.running_total <= 40;
    END;
}

# --gui: los widgets también son filas. Un SELECT construye la ventana entregando el
# texto de cada fila a uplevel #0, que lo ejecuta como Tcl en el nivel global.
set gui [expr {"--gui" in $argv}]
set seconds [expr {[set at [lsearch $argv --seconds]] >= 0 ? [lindex $argv $at+1] : 0}]
if {$gui} {
    package require Tk
    wm title . "Timecards - DEMO ONLY"
    db eval {
        SELECT tcl('uplevel', '#0', command) FROM ui ORDER BY id
    }
}
# La única sentencia que lo pone en marcha: inserta la tarjeta 1 y el disparador hace el resto.
db eval {SELECT tcl('init')}
db transaction {
    db eval {
        UPDATE draw SET h = tcl('hours');
        INSERT INTO main.demo_timecards(run_id, category, hours, running_total, iso_week, created_at)
        SELECT tcl('runid'), tcl('category', 1), h, h, tcl('week'), datetime('now')
        FROM draw
    }
}

db eval {
    SELECT count(*) AS entries, max(running_total) AS total
    FROM main.demo_timecards WHERE run_id = $::runid
} {
    puts "# committed total=$total entries=$entries DEMO ONLY"
}
puts "# every proc that ran was fetched from SQLite by unknown: [lsort $::loaded]"
puts "# the loop was a recursive trigger, and one INSERT started it"
if {$gui} {
    puts "# the window was built from [db eval {SELECT count(*) FROM ui}] rows of the ui table"
}
if {$gui} {
    if {$seconds > 0} {
        after [expr {$seconds * 1000}] {set done 1}
        vwait done
    } else {
        tkwait window .
    }
    # tclsh sigue vivo cuando termina el script mientras exista la ventana principal de Tk
    catch {destroy .}
}
db close
