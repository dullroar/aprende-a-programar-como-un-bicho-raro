#!/usr/bin/gawk -f
# SOLO DEMO. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo
# XDG_DATA_HOME. Nada de esto toca un sistema real de registro de horas.
#
# Run:  gawk -f timecards.awk                (the random digits come from /dev/urandom)
#       gawk -f timecards.awk digits.txt     (or from any file: the digits in it ARE the dice)
#
# El reto: suma tarjetas de 10-19 horas hasta que el total acumulado pase de 40.
#
# EL TRUCO.  Aquí abajo no hay ningún bucle ni ningún `if`, ni generador de
# números aleatorios.  La entrada es /dev/urandom, el separador de registros de awk es la expresión
# regular [0-9], así que cada "registro" es un tramo de bytes aleatorios que termina en
# un dígito aleatorio, que gawk nos entrega en RT.  Un dígito es una tirada de dado, un registro es
# una tarjeta, y el propio bucle principal de awk es el bucle.  La regla de parada es un patrón con
# una acción `exit`.  El reto entero, sin la base de datos, cabe en una línea:
#
#   gawk 'BEGIN{RS="[0-9]"; split("Meetings Coding Debugging Learning",C)}
#         {printf "%s\t%d\t%d\n", C[(NR-1)%4+1], h=10+RT, t+=h} t>40{exit}' /dev/urandom
#
# (La línea única no tiene base de datos, ni semana, ni marca DEMO ONLY, ni
# protección contra el último registro vacío de un archivo finito. El programa de abajo tiene las tres.)
#
# Solo GNU awk: RT, una expresión regular como RS, systime() y PROCINFO.

BEGIN {
    # Pregunta primero la hora. RS se aplica a TODAS las lecturas, incluido getline desde un
    # comando: con RS="[0-9]" puesto, "date" daría un registro vacío que termina
    # en el primer dígito del año.
    "date +%G-W%V" | getline week
    close("date +%G-W%V")
    run = systime() "-" PROCINFO["pid"]
    t = n = 0                       # total acumulado y cuenta de tarjetas (awk los iniciaría en 0 de todos modos)

    RS = "[0-9]"                    # un registro termina en un dígito; RT guarda ese dígito
    FS = ","                        # la regla 3 arma un registro separado por comas; FS lo vuelve a dividir
    split("Meetings Coding Debugging Learning", C, " ")

    # Sin archivo en la línea de comandos: añade uno. ARGC += (ARGC < 2) vale 0 o 1, así que no hay `if`.
    ARGV[ARGC] = "/dev/urandom"
    ARGC += (ARGC < 2)

    dir = (ENVIRON["XDG_DATA_HOME"] != "" ? ENVIRON["XDG_DATA_HOME"] : ENVIRON["HOME"] "/.local/share") "/AwkWeird"
    system("mkdir -p '" dir "'")
    sql = "sqlite3 '" dir "/demo-timecards.db'"
    print "BEGIN; CREATE TABLE IF NOT EXISTS demo_timecards(id INTEGER PRIMARY KEY,run_id TEXT," \
          "category TEXT,hours INTEGER,running_total INTEGER,iso_week TEXT,created_at TEXT," \
          "demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));" | sql
    print "# DEMO ONLY run " run
}

# Regla 1: el último registro de un archivo finito no tiene dígito después (RT está vacío). No es una tirada.
RT == "" { next }

# Regla 2: el dado. 10 + un dígito da 10..19, y t es el total acumulado.
# Una asignación es una expresión, así que las horas y la suma son una sola sentencia.
{ t += h = 10 + RT }

# Regla 3: la tarjeta, como un registro separado por comas. Asignar $0 lo vuelve a dividir en campos.
{ $0 = C[n++ % 4 + 1] "," h "," t "," week }

# Regla 4: los mismos campos, como SQL, por una tubería hacia sqlite3.
{ print "INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week,created_at) VALUES('" run "','" $1 "'," $2 "," $3 ",'" $4 "',datetime('now'));" | sql }

# Regla 5: los mismos campos otra vez, para las personas. Fijar OFS y luego $1 = $1 obliga a awk
# a reconstruir $0, ahora unido por tabuladores en lugar de comas.
{ OFS = "\t"; $1 = $1; print $0, "DEMO ONLY" }

# Regla 6: la regla de parada. exit ejecuta END; la tarjeta que cruzó la línea ya se escribió.
t > 40 { exit }

END {
    print "COMMIT;" | sql
    close(sql)
    print "# committed total=" t " entries=" n " DEMO ONLY"
    print "# the loop was awk's main loop over /dev/urandom, RS=[0-9] made each digit a die roll, and t > 40 { exit } stopped it"
}
