#!/usr/bin/env tclsh
# DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo
# XDG_DATA_HOME. Nada de aquí toca un sistema real de registro de horas.
#
# Ejecuta:  tclsh timecards.tcl            (texto)
#           tclsh timecards.tcl --gui     (además, una ventana de Tk; añade --seconds N para que se cierre sola)
#
# El reto: suma tarjetas de 10 a 19 horas (Reuniones, Programación, Depuración,
# Aprendizaje, una tras otra) hasta que el total acumulado pase de 40.  En Tcl eso
# es un bucle while en el procedimiento "draw".  Todo lo demás es cañería: una tarjeta
# es un diccionario, la base de datos es un comando de Tcl, la ventana es opcional.

package require Tcl 8.6
package require sqlite3

namespace eval timecards {
    variable categories {Reuniones Programación Depuración Aprendizaje}
    variable minHours 10
    variable maxHours 19
    variable limit 40
}

# ---------------------------------------------------------------- el reto

# Un número aleatorio de horas, de minHours a maxHours.
proc timecards::randomHours {} {
    variable minHours
    variable maxHours
    expr {$minHours + int(rand() * ($maxHours - $minHours + 1))}
}

# Reparte tarjetas hasta que el total acumulado supere el límite, y devuélvelas como una
# lista de diccionarios. La tarjeta que cruza la línea se conserva, porque la prueba
# se hace antes de sacar la siguiente tarjeta, no después.
proc timecards::draw {} {
    variable categories
    variable limit
    set cards {}
    set total 0
    while {$total <= $limit} {
        set hours [randomHours]
        incr total $hours
        set category [lindex $categories [expr {[llength $cards] % [llength $categories]}]]
        lappend cards [dict create category $category hours $hours total $total]
    }
    return $cards
}

# ---------------------------------------------------------------- el calendario

# La semana ISO-8601 de ahora mismo, p. ej. 2026-W46. clock conoce %G y %V.
proc timecards::isoWeek {} {
    clock format [clock seconds] -format %G-W%V
}

# ---------------------------------------------------------------- SQLite

proc timecards::dataDir {} {
    if {[info exists ::env(XDG_DATA_HOME)] && $::env(XDG_DATA_HOME) ne ""} {
        set base $::env(XDG_DATA_HOME)
    } else {
        set base [file join $::env(HOME) .local share]
    }
    file join $base Tcl
}

# Guarda cada tarjeta en una sola transacción. La regla DEMO ONLY vive en la tabla:
# CHECK(demo_only=1) significa que no se puede guardar una fila que no sea de demostración.
#
# En "db eval {... $runId ...}" las variables de Tcl son *parámetros enlazados*, no texto
# pegado en el SQL, así que entrecomillar nunca es problema nuestro. "dict with" convierte
# las claves de una tarjeta (category, hours, total) en variables locales para enlazarlas.
proc timecards::save {runId week cards} {
    set dir [dataDir]
    file mkdir $dir
    sqlite3 [namespace current]::db [file join $dir demo-timecards.db]
    try {
        db eval {
            CREATE TABLE IF NOT EXISTS demo_timecards(
                id INTEGER PRIMARY KEY, run_id TEXT, category TEXT, hours INTEGER,
                running_total INTEGER, iso_week TEXT, created_at TEXT,
                demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1))
        }
        db transaction {
            foreach card $cards {
                dict with card {
                    db eval {
                        INSERT INTO demo_timecards
                            (run_id, category, hours, running_total, iso_week, created_at)
                        VALUES ($runId, $category, $hours, $total, $week, datetime('now'))
                    }
                }
            }
        }
    } finally {
        db close
    }
}

# ---------------------------------------------------------------- pantalla

proc timecards::row {card week} {
    dict with card {
        join [list $category $hours $total $week {DEMO ONLY}] \t
    }
}

# Una ventana opcional de Tk: una tabla con las tarjetas y el total. Tk solo se
# carga cuando se pide, así que la versión de texto corre en una máquina sin pantalla.
proc timecards::showWindow {cards week seconds} {
    package require Tk
    wm title . "Timecards - DEMO ONLY"
    ttk::treeview .cards -columns {category hours total week} -show headings -height 6
    foreach column {category hours total week} {
        .cards heading $column -text [string totitle $column]
        .cards column $column -width 110 -anchor center
    }
    foreach card $cards {
        dict with card {
            .cards insert {} end -values [list $category $hours $total $week]
        }
    }
    ttk::label .note -text "DEMO ONLY: [llength $cards] cards, total [dict get [lindex $cards end] total]"
    pack .cards -fill both -expand 1 -padx 8 -pady 8
    pack .note -pady {0 8}
    if {$seconds > 0} {
        after [expr {$seconds * 1000}] {set ::timecards::closed 1}
        bind . <Destroy> {set ::timecards::closed 1}
        vwait ::timecards::closed
    } else {
        tkwait window .
    }
    # Un tclsh que ha cargado Tk no termina al final del script mientras
    # exista la ventana principal, así que ciérrala explícitamente.
    catch {destroy .}
}

# ---------------------------------------------------------------- principal

proc timecards::main {argv} {
    set gui 0
    set seconds 0
    while {[llength $argv]} {
        set argv [lassign $argv option]
        switch -- $option {
            --gui {set gui 1}
            --seconds {set argv [lassign $argv seconds]}
            default {puts stderr "usage: timecards.tcl ?--gui ?--seconds N??"; exit 2}
        }
    }

    expr {srand([clock microseconds] ^ [pid])}
    set runId [clock seconds]-[pid]
    set week [isoWeek]
    set cards [draw]

    save $runId $week $cards
    puts "# DEMO ONLY run $runId"
    foreach card $cards {
        puts [row $card $week]
    }
    puts "# committed total=[dict get [lindex $cards end] total] entries=[llength $cards] DEMO ONLY"
    puts "# one while loop, cards as dicts, and db eval binding Tcl variables as SQL parameters"
    if {$gui} {
        showWindow $cards $week $seconds
    }
}

# Ejecuta main solo cuando este archivo es el script, no cuando se carga con source para probar.
if {[info exists argv0] && [file normalize $argv0] eq [file normalize [info script]]} {
    timecards::main $argv
}
