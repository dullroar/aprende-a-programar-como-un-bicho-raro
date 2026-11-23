⍝ ──────────────────────────────────────────────────────────────────────────
⍝ DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo
⍝ XDG_DATA_HOME. Nada de aquí toca un sistema real de reporte de horas.
⍝
⍝ Ejecuta:  apl --script -f timecards.apl
⍝
⍝ LA PROEZA: el anfitrión define exactamente una función, Card0.  Cada otra tarjeta
⍝ es una función que la tarjeta anterior *escribió*: lee su propio código con
⍝ ⎕CR, cambia un encabezado y cuatro líneas de "gen" (número de tarjeta, categoría, horas,
⍝ total acumulado), entrega la copia a ⎕FX y la llama.  La regla "sigue mientras
⍝ el total sea 40 o menos" es una compresión (/) sobre el texto de código del hijo:
⍝ cuando el total pasa de 40 el hijo tiene cero líneas, ⎕FX no define
⍝ nada, y no hay nada que llamar.  Sin ⍣, sin →, sin bucle, sin `if`.
⍝ El estado no está en variables, está en el texto del programa.
⍝ ──────────────────────────────────────────────────────────────────────────

⎕IO←0
⎕RL←+/⎕TS×1 12 372 8928 535680 32140800 1894248000    ⍝ GNU APL siempre empieza en 16807

Categories←'Reuniones' 'Programación' 'Depuración' 'Aprendizaje'
NL←⎕UCS 10
TAB←⎕UCS 9
RunId←1↓∊'-',¨⍕¨⎕TS

Date←⎕FIO[24] 'date +%G-W%V'
Week←¯1↓⎕UCS ⎕FIO[8] Date
_←⎕FIO[25] Date

Sqlite←'w' ⎕FIO[24] 'd=${XDG_DATA_HOME:-$HOME/.local/share}/AplWeird; mkdir -p "$d"; exec sqlite3 "$d/demo-timecards.db"'
_←('CREATE TABLE IF NOT EXISTS demo_timecards(id INTEGER PRIMARY KEY,run_id TEXT,category TEXT,hours INTEGER,running_total INTEGER,iso_week TEXT,created_at TEXT,demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));BEGIN;',NL) ⎕FIO[23] Sqlite
Insert←'INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week,created_at) VALUES(''%s'',''%s'',%d,%d,''%s'',datetime(''now''));',NL
Show←'%s',TAB,'%d',TAB,'%d',TAB,'%s',TAB,'DEMO ONLY',NL

⍝ Nombres locales que cada copia declara en su encabezado, para que las N, C, H, T de un hijo no
⍝ pisen las de su padre.
Locals←';N;C;H;T;D;Alive;Kid;Genes'

_←('# DEMO ONLY run %s',NL) RunId ⎕FIO[22] 1

⍝ ── La única función que el anfitrión escribe ────────────────────────────
⍝ Las líneas 1-4 son los genes (se reemplazan en cada copia); de la línea 5 en adelante está
⍝ el cuerpo, que cada copia hereda sin cambios.
∇Card0;N;C;H;T;D;Alive;Kid;Genes
N←0
C←0
H←10+?10
T←H
_←(Show (⊃Categories[C]) H T Week) ⎕FIO[22] 1
_←(Insert RunId (⊃Categories[C]) H T Week) ⎕FIO[22] Sqlite
D←10+?10                                         ⍝ horas de la siguiente tarjeta, sorteadas ahora
Genes←('N←',⍕N+1) ('C←',⍕4|C+1) ('H←',⍕D) ('T←',⍕T+D)
Alive←40≥T                                       ⍝ 1 hasta que el total pasa de 40
Kid←⎕FX Alive/(⊂'Card',(⍕N+1),Locals),Genes,5↓⊂[1]⎕CR 'Card',⍕N
⍎Alive/'Card',⍕N+1
∇

Card0

⍝ ── Lo que escribió el programa ──────────────────────────────────────────
⍝ ⎕NL 3 lista cada función del espacio de trabajo.  Card0 es nuestra; el resto se
⍝ escribió en tiempo de ejecución, y la línea 3 de cada una son las horas con que nació.
Names←⊂[1]⎕NL 3
Mine←{'Card'≡4↑⍵}¨Names
Last←↑⌽Mine/Names
Total←⍎2↓(⎕CR Last~' ')[4;]~' '                  ⍝ el gen T←41 de la última tarjeta
_←{(('# %s ⇐ %s',NL) (⍵~' ') ((⎕CR ⍵~' ')[3;]~' ')) ⎕FIO[22] 1}¨Mine/Names
_←('COMMIT;',NL) ⎕FIO[23] Sqlite
_←⎕FIO[25] Sqlite
_←(('# committed total=%d entries=%d DEMO ONLY',NL,'# the host wrote Card0 and nothing else; each later card was written by the one before it',NL) Total (≢Mine/Names)) ⎕FIO[22] 1
)OFF
