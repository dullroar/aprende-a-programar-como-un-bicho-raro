#!/usr/bin/env python3
"""Prints the one `find` command that timecards.sh runs.

The command is ~6 KB because find has no variables, so every "table" is spelled out as -o branches.
The tables are regular, which is why they are generated here instead of typed. This script is NOT
part of the program: it is the readable source of the program's tables. check.sh regenerates the
line and fails if timecards.sh has drifted from it.

Primaries used, and only these: -path -name -o -exec   (plus the implicit -a and escaped parentheses).
Programs run by -exec, and only these: printf mkdir mktemp date.

The machine, in one paragraph. The walk digs the tree it is walking. One directory = one step:
  <u>   one hour; named by the running total's last digit (1..9,0,1..): a unit counter you read off the name
  b<NN> hours still to go in this card (b18..b00): a countdown you read off the name
  <R>   six random characters from mktemp: the card's dice (the last character picks the hours)
A card is R, then pairs u/bNN down to b00; the next card's R hangs under that b00. The total is the
number of u segments in the path: ten times the count of "0" segments, plus the last u.
"""
S6 = "[!/]" * 6  # exactamente seis caracteres que no son barra: un segmento R
# 60 de los 62 caracteres de mktemp en diez grupos de seis; Y y Z se vuelven a tirar (mira el README)
CLASSES = ["abcdef", "ghijkl", "mnopqr", "stuvwx", "yz0123", "456789", "ABCDEF", "GHIJKL", "MNOPQR", "STUVWX"]
DIGITS = "0123456789"
SUCC = {d: DIGITS[(i + 1) % 10] for i, d in enumerate(DIGITS)}


def ex(*words):
    return "-exec " + " ".join(words) + " \\;"


def q(s):  # entrecomilla para el shell en la línea; el texto SQL tiene comillas simples, así que usa comillas dobles
    return '"' + s + '"' if "'" in s else "'" + s + "'"


def path(p):
    return "-path " + q(p)


def alt(branches):
    return " -o ".join("\\( " + b + " \\)" for b in branches)


def wraps(n):  # al menos n segmentos de ruta llamados exactamente 0 (cada uno es un +10)
    return "*" + "/0/*" * n


def cards(n):  # al menos n segmentos de seis caracteres (cada uno es una tarjeta)
    return "*" + ("/" + S6 + "*") * n


# Un directorio aleatorio nuevo por tarjeta; su ruta va a stdout, así que se imprime como comentario SQL.
NEXT_CARD = ex("printf", q(" -- ")) + " " + ex("mktemp", "-d", "{}/XXXXXX")

HEAD = ("INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week) "
        "VALUES((SELECT max(id) FROM runs),")

# 1. el directorio inicial: aún no ha pasado nada, así que se reparte la primera tarjeta
rule_start = path("t") + " " + NEXT_CARD

# 2. los dados de una tarjeta (nombre de seis caracteres): abre la fila SQL, nombra la categoría (cuántas tarjetas hay
#    por encima de nosotros), y luego cava la primera hora de la tarjeta. El dígito de la hora es el último dígito de la tarjeta anterior + 1.
category = alt([
    path(cards(5)) + " " + ex("printf", q("'Reuniones',")),
    path(cards(4)) + " " + ex("printf", q("'Aprendizaje',")),
    path(cards(3)) + " " + ex("printf", q("'Depuración',")),
    path(cards(2)) + " " + ex("printf", q("'Programación',")),
    ex("printf", q("'Reuniones',")),
])
first_hour = alt(
    [path("*/%s/b00/%s" % (d, S6)) + " " + ex("mkdir", "{}/" + SUCC[d]) for d in DIGITS]
    + [ex("mkdir", "{}/1")]
)
rule_dice = "-name '??????' " + ex("printf", q(HEAD)) + " \\( " + category + " \\) \\( " + first_hour + " \\)"

# 3. una hora (nombre de un carácter). La primera hora de una tarjeta lee los dados: imprime las horas
#    de la tarjeta (10 + número de grupo) y cava la cuenta atrás. Una hora posterior cava la cuenta atrás una unidad menos.
def dice(d, pattern):
    return (path("*/" + pattern + "/?") + " " + ex("printf", q("%d," % (10 + d)))
            + " " + ex("mkdir", "{}/b%02d" % (9 + d)))


hour = alt(
    [dice(d, "[!/]" * 5 + "[" + CLASSES[d] + "]") for d in range(10)]                # último carácter
    + [dice(d, "[!/]" * 4 + "[" + CLASSES[d] + "][YZ]") for d in range(10)]          # nueva tirada con el anterior
    + [path("*/" + S6 + "/?") + " " + ex("printf", q("10,")) + " " + ex("mkdir", "{}/b09")]  # vuelta a tirar dos veces
    + [path("*/b%02d/?" % n) + " " + ex("mkdir", "{}/b%02d" % (n - 1)) for n in range(18, 0, -1)]
)
rule_hour = "-name '?' \\( " + hour + " \\)"

# 4. una cuenta atrás. b00 termina la tarjeta: imprime el total acumulado (decenas, luego unidades, luego la semana ISO
#    de date), se detiene si pasa de 40; si no, reparte la siguiente tarjeta. Cualquier otro bNN cava la siguiente hora.
tens = alt([path(wraps(n)) + " " + ex("printf", q(str(n))) for n in range(5, 0, -1)])
units = alt([path("*/%s/b00" % d) + " " + ex("printf", q("%s," % d)) for d in DIGITS])
week = ex("date", '"+\'%G-W%V\');"')
over_40 = "\\( " + path(wraps(5)) + " -o \\( " + path(wraps(4)) + " " + path("*/[1-9]/b00") + " \\) \\)"
end_of_card = ("\\( -name b00 \\( " + tens + " \\) \\( " + units + " \\) " + week
               + " \\( " + over_40 + " -o \\( " + NEXT_CARD + " \\) \\) \\)")
next_hour = alt([path("*/%s/b??" % d) + " " + ex("mkdir", "{}/" + SUCC[d]) for d in DIGITS])
rule_countdown = end_of_card + " -o \\( -name 'b??' \\( " + next_hour + " \\) \\)"

print("find t \\( " + rule_start + " \\) -o \\( " + rule_dice + " \\) -o \\( " + rule_hour
      + " \\) -o \\( " + rule_countdown + " \\)")
