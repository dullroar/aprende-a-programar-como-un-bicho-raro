⍝ ──────────────────────────────────────────────────────────────────────────
⍝ DEMO ONLY. Tarjetas de horas ficticias, escritas en un archivo SQLite temporal bajo
⍝ XDG_DATA_HOME. Nada de aquí toca un sistema real de reporte de horas.
⍝
⍝ Ejecuta:  apl --script -f timecards.apl
⍝
⍝ El reto completo ("suma tarjetas de 10 a 19 horas hasta que el total supere 40") son
⍝ tres expresiones de arreglos.  No hay bucle ni `if`; el resto del
⍝ archivo es tubería: la semilla, una tubería a sqlite3 y la impresión.
⍝ ──────────────────────────────────────────────────────────────────────────

⍝ Notas de estilo: una instrucción por línea (⋄ es para el REPL), nombres en CamelCase
⍝ para lo que definimos, y ninguna suposición sobre ⎕IO (el origen del índice).
⍝ La única primitiva sensible al origen que se usa es ?, que sortea ⎕IO..⎕IO+9 para
⍝ ?10, así que el sorteo de abajo vuelve a restar el origen.

⍝ GNU APL inicia cada sesión con ⎕RL=16807, así que sin esto cada ejecución
⍝ imprimiría las mismas tarjetas "aleatorias".  Mejor mezclamos el reloj en una semilla.
⎕RL←+/⎕TS×1 12 372 8928 535680 32140800 1894248000

Categories←'Reuniones' 'Programación' 'Depuración' 'Aprendizaje'
NL←⎕UCS 10
TAB←⎕UCS 9

⍝ ── El reto ───────────────────────────────────────────────────────────────
⍝ 1. Sortea horas.  Cada tarjeta tiene al menos 10 horas, así que cinco siempre
⍝    superan 40 (5×10=50).  Sortear cinco de antemano es una *cota*, no un conteo de bucle.
⍝    (?5⍴10) da cinco sorteos entre los primeros diez enteros; el ajuste del origen
⍝    y el +10 los convierten en 10..19.
Drawn←(10-⎕IO)+?5⍴10

⍝ 2. Regla de parada.  Los totales acumulados solo crecen, así que "el total sigue ≤ 40"
⍝    es verdadero para un prefijo de las tarjetas y luego falso para siempre.  Cuenta ese
⍝    prefijo (+/40≥+\), suma la única tarjeta que cruza la línea, y toma.
Hours←Drawn↑⍨1++/40≥+\Drawn

⍝ 3. Todo lo demás se deriva de Hours sin más decisiones.
Totals←+\Hours                    ⍝ total acumulado después de cada tarjeta
Kinds←(≢Hours)⍴Categories         ⍝ ⍴ recicla: Reuniones Programación Depuración Aprendizaje Reuniones …

⍝ ── Tubería ──────────────────────────────────────────────────────────────
RunId←1↓∊'-',¨⍕¨⎕TS              ⍝ 2026-11-14-9-37-13-583

⍝ La semana ISO viene de date(1) para que APL no tenga que rederivar calendarios ISO-8601.
⍝ ⎕FIO[24] ejecuta un comando y devuelve un manejador de archivo, ⎕FIO[8] lee una línea
⍝ de él, ⎕FIO[25] lo cierra.  ¯1↓ quita el salto de línea final.
Date←⎕FIO[24] 'date +%G-W%V'
Week←¯1↓⎕UCS ⎕FIO[8] Date
_←⎕FIO[25] Date

⍝ Abre una tubería de escritura a sqlite3.  ⎕FIO[24] con argumento izquierdo 'w' es popen.
⍝ El fragmento de shell solo elige (y crea) el directorio temporal.
Sqlite←'w' ⎕FIO[24] 'd=${XDG_DATA_HOME:-$HOME/.local/share}/Apl; mkdir -p "$d"; exec sqlite3 "$d/demo-timecards.db"'

⍝ La restricción CHECK hace imposible representar "no demo" en esta tabla.
Schema←'CREATE TABLE IF NOT EXISTS demo_timecards(id INTEGER PRIMARY KEY,run_id TEXT,category TEXT,hours INTEGER,running_total INTEGER,iso_week TEXT,created_at TEXT,demo_only INTEGER NOT NULL DEFAULT 1 CHECK(demo_only=1));BEGIN;'
_←(Schema,NL) ⎕FIO[23] Sqlite   ⍝ ⎕FIO[23] escribe una cadena con fwrite

⍝ ⎕FIO[22] es fprintf: una cadena de formato a la izquierda, sus argumentos a la
⍝ derecha.  Los valores aquí son números o nuestras propias palabras fijas, nunca entrada del usuario,
⍝ así que dar formato al SQL con %s es seguro solo en este lugar; no copies el hábito.
Insert←'INSERT INTO demo_timecards(run_id,category,hours,running_total,iso_week,created_at) VALUES(''%s'',''%s'',%d,%d,''%s'',datetime(''now''));',NL
Row←TAB,'%d',TAB,'%d',TAB,'%s',TAB,'DEMO ONLY',NL

⍝ Una dfn por destino; ⍵ es un número de fila.  ⍳≢Hours produce números de fila
⍝ en el origen actual y Kinds[⍵] indexa en ese mismo origen, así que el
⍝ par es a prueba de origen.
SaveRow←{(Insert RunId (⊃Kinds[⍵]) Hours[⍵] Totals[⍵] Week) ⎕FIO[22] Sqlite}
ShowRow←{(('%s',Row) (⊃Kinds[⍵]) Hours[⍵] Totals[⍵] Week) ⎕FIO[22] 1}

_←SaveRow¨⍳≢Hours
_←('COMMIT;',NL) ⎕FIO[23] Sqlite
_←⎕FIO[25] Sqlite                ⍝ cerrar la tubería espera a que sqlite3 termine

⍝ ── Reporte ───────────────────────────────────────────────────────────────
_←(('# DEMO ONLY run %s',NL) RunId) ⎕FIO[22] 1
_←ShowRow¨⍳≢Hours
_←(('# committed total=%d entries=%d DEMO ONLY',NL,'# five rolls and one take-while; the rest were never needed',NL) (⊢/Totals) (≢Hours)) ⎕FIO[22] 1

)OFF
