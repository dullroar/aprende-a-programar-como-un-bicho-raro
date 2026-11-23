#!/usr/bin/env python3
"""Prints the one `find` command that timecards.sh runs (the GNU version).

Same stunt as src/find-posix, with every GNU extra switched on, so the machine is much smaller:
  -printf directives   %d (depth) IS the running total; %TG-W%TV (the new directory's mtime) IS the ISO week
  -fprintf /dev/fd/3   the SQL goes to fd 3, so mktemp's stdout noise needs no comment trick
  -regex               "at least n cards" and "at least 41 levels" are regular expressions
  -O3                  the cost-based optimizer is on; check.sh proves it never changes the answer
This script is the readable source of the long tables; check.sh fails if timecards.sh drifts from it.

The machine. One directory per hour, so the depth of a directory is the hours so far. A card is:
  <R>     six random characters (mktemp): the card's FIRST hour, and its dice
  b<NN>   a countdown, b17 ... b00: one directory per remaining hour
The next card's <R> hangs under the previous card's b00.
"""
DIGITS = "0123456789"
# 60 de los 62 caracteres de mktemp en diez grupos de seis; Y y Z se vuelven a tirar (mira el README de la versión portable)
CLASSES = ["abcdef", "ghijkl", "mnopqr", "stuvwx", "yz0123", "456789", "ABCDEF", "GHIJKL", "MNOPQR", "STUVWX"]
SQL = "/dev/fd/3"


def ex(*words):
    return "-exec " + " ".join(words) + " \\;"


def out(fmt):  # un trozo de SQL, hacia el descriptor 3
    return "-fprintf " + SQL + ' "' + fmt + '"'


def alt(branches):
    return " -o ".join("\\( " + b + " \\)" for b in branches)


def cards(n):  # al menos n nombres de seis caracteres en la ruta: el número de tarjetas
    return "'(.*/[^/]{6}){%d}.*'" % n


MK = ex("mktemp", "-d", "{}/XXXXXX")
HEAD = ("INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week) "
        "VALUES((SELECT max(id) FROM runs),")

# 1. el directorio de inicio: reparte la primera tarjeta
rule_start = "-path t " + MK

# 2. los dados de una tarjeta: abre la fila, nombra la categoría, imprime las horas, cava la cuenta atrás.
#    El directorio de los dados es la hora 1, así que una tarjeta de H horas cava b(H-2) ... b00.
category = alt([
    "-regex " + cards(5) + " " + out("'Reuniones',"),
    "-regex " + cards(4) + " " + out("'Aprendizaje',"),
    "-regex " + cards(3) + " " + out("'Depuración',"),
    "-regex " + cards(2) + " " + out("'Programación',"),
    out("'Reuniones',"),
])


def dice(d, glob):
    return "-name '" + glob + "' " + out("%d," % (10 + d)) + " " + ex("mkdir", "{}/b%02d" % (8 + d))


hours = alt(
    [dice(d, "?" * 5 + "[" + CLASSES[d] + "]") for d in range(10)]              # último carácter
    + [dice(d, "?" * 4 + "[" + CLASSES[d] + "][YZ]") for d in range(10)]        # vuelve a tirar con el carácter anterior
    + [out("10,") + " " + ex("mkdir", "{}/b08")]                                 # vuelve a tirar dos veces
)
rule_dice = "-name '??????' " + out(HEAD) + " \\( " + category + " \\) \\( " + hours + " \\)"

# 3. el final de una tarjeta: la profundidad es el total y la mtime del directorio es la semana. Para cuando la profundidad
#    sea 41 o más (ya no se cava nada, así que a find se le acaba el árbol); si no, reparte la siguiente tarjeta.
#    -quit terminaría find antes, pero entonces find omite su perfil -D rates, así que no se usa.
over_40 = "-regex '([^/]*/){41}.*'"
rule_end = ("-name b00 " + out("%d,'%TG-W%TV');\\n") + " \\( " + over_40 + " -o \\( " + MK + " \\) \\)")

# 4. una cuenta atrás: b17 cava b16, y así sucesivamente
rule_count = "-name 'b??' \\( " + alt(["-name b%02d " % n + ex("mkdir", "{}/b%02d" % (n - 1)) for n in range(17, 0, -1)]) + " \\)"

print("find -O${FIND_O:-3} ${FIND_D:+-D $FIND_D} t -regextype posix-extended \\( " + rule_start + " \\) -o \\( " + rule_dice
      + " \\) -o \\( " + rule_end + " \\) -o \\( " + rule_count + " \\)")
