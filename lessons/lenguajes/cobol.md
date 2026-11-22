# COBOL

Entradas: [`src/cobol`](../../src/cobol/README.md) (la idiomática) y [`src/cobol-weird`](../../src/cobol-weird/README.md) (sin `IF` ni `PERFORM`).

Para una ruta de lectura avanzada con trazas y experimentos, consulta la [guía de estudio de COBOL](../guias-de-estudio/lenguajes/cobol.md).

COBOL (1959) se creó para registros, totales e informes y se nota. Lo que lo hace especial es que mueve las reglas y las formas *fuera del procedimiento y hacia la descripción de los datos*. Lo que lo vuelve un campo rico en rarezas es su edad: es lo bastante viejo como para tener una característica, `ALTER`, que el estándar ya eliminó.

## Qué hace especial a COBOL

| Característica | Dónde | Qué enseña |
| --- | --- | --- |
| Una regla de parada declarada como datos | [`cobol/timecards.cob` L41-42](../../src/cobol/timecards.cob#L41-L42): `01 WS-TOTAL PIC 99 VALUE 0.` / `88 OVER-FORTY VALUE 41 THRU 99.` usados por [L93](../../src/cobol/timecards.cob#L93): `PERFORM DRAW-CARD UNTIL OVER-FORTY` | Un *nombre de condición* de nivel `88` es un rango con nombre de valores de un campo. El bucle no contiene ninguna comparación; para cambiar la regla se edita el dato, no el código. |
| La cláusula PICTURE hace el redondeo | [L107](../../src/cobol/timecards.cob#L107): `COMPUTE WS-HOURS = 10 + FUNCTION RANDOM * 10`, en `PIC 99` | Guardar 10.0-19.99 en un campo de dos dígitos descarta la fracción. La forma del campo es la función piso. La aritmética de COBOL es decimal, no de punto flotante binario. |
| Una cadena de texto, vista dos veces | [L48-55](../../src/cobol/timecards.cob#L48-L55): `CATEGORY-TABLE REDEFINES CATEGORY-NAMES` / `PIC X(9) OCCURS 4 TIMES` | `REDEFINES` coloca una segunda descripción sobre los mismos bytes. Una tabla de cadenas de texto también es una sola cadena de texto larga. |
| Archivos cuyos nombres son variables | `SELECT SQL-SCRIPT ASSIGN TO WS-SQL-PATH` | El programa escribe un script SQL como un archivo secuencial por líneas y se lo entrega a `sqlite3`: una transacción o ninguna. |

## ALTER

`ALTER` es el ejemplo perfecto de "una rareza del lenguaje que alguna vez fue una característica". Se declaró obsoleto en 1985 y se eliminó del estándar en 2002. GnuCOBOL todavía lo ejecuta y emite cinco advertencias.

### Contempla la monstruosidad

```bash
sandbox/container/run-image.sh src/cobol-weird
```

De tres a cinco filas de tarjeta de horas y un total confirmado que pasa de 40, a partir de un programa sin `IF`, `PERFORM`, `EVALUATE`, `UNTIL` ni `MOD`.

### ¿Cómo demonios funciona eso?

Los párrafos se ejecutan en el orden en que están escritos, a menos que un `GO TO` los redirija. El bucle es un párrafo que contiene un `GO TO` ([`cobol-weird/timecards.cob` L150-151](../../src/cobol-weird/timecards.cob#L150-L151)):

```cobol
       NEXT-CARD.
           GO TO MEETINGS-CARD.
```

Un párrafo que es exactamente un `GO TO` es lo único que `ALTER` puede cambiar. Cada párrafo de categoría lo reconecta con la categoría siguiente ([L157](../../src/cobol-weird/timecards.cob#L157), [L162](../../src/cobol-weird/timecards.cob#L162), [L167](../../src/cobol-weird/timecards.cob#L167), [L172](../../src/cobol-weird/timecards.cob#L172)): `ALTER NEXT-CARD TO PROCEED TO CODING-CARD`. Nada cuenta módulo 4. "Cuál es la categoría siguiente" existe solo como el destino actual de un salto.

La regla de parada es el desbordamiento. `WS-HEADROOM` es `PIC 99` y empieza en 59 ([L44](../../src/cobol-weird/timecards.cob#L44)). Cada tarjeta suma sus horas ([L196-199](../../src/cobol-weird/timecards.cob#L196-L199)):

```cobol
ADD WS-HOURS TO WS-HEADROOM
    ON SIZE ERROR
        ALTER NEXT-CARD TO PROCEED TO FINISH-RUN
END-ADD
```

59 + total cabe en dos dígitos mientras el total sea 40 o menos. La suma que llega a 100 es un *error de tamaño*: el campo queda sin cambios y `ON SIZE ERROR` reconecta `NEXT-CARD` por última vez. El `GO TO NEXT-CARD` que sigue es la misma sentencia de siempre y ahora termina la ejecución.

### ¿Qué acabamos de aprender?

- **Un destino de salto puede ser estado.** El flujo de control no es solo el contador de programa recorriendo el texto fuente; también puede ser un dato que el programa edita. Compara [el reinicio de Make](make-cmake.md#gnu-make), [los registros de CMake](make-cmake.md#cmake) y [el `>in` de Forth](forth.md): todos guardan el estado de control en un lugar distinto de las variables ordinarias. Consulta los [patrones](../patrones.md#el-estado-de-control-fuera-de-las-variables).
- **El desbordamiento es una decisión.** `ON SIZE ERROR` es un condicional que se dispara porque la aritmética se queda sin dígitos, no por una comparación que alguien escribió.
- **La programación estructurada ganó por una razón** y este programa es esa razón. Mira el paso siguiente.

Etiquetas: `ALTER` es comportamiento **permitido por la implementación** (se eliminó del estándar, pero GnuCOBOL lo conserva). El comportamiento ante un error de tamaño (campo sin cambios) es **garantizado** por el estándar.

### Haz esto en producción y estás despedido

- **No puedes entender un párrafo leyéndolo.** `NEXT-CARD` dice `GO TO MEETINGS-CARD` y, en tiempo de ejecución, casi nunca lo hace. Esa queja es lo que hizo que se eliminara `ALTER`.
- **Los depuradores muestran variables, no destinos de salto.** Nada en los campos de `WS-*` te dice cuál es la categoría siguiente.
- **Portabilidad.** Los compiladores más nuevos podrían no aceptarlo y las banderas de conformidad con el estándar podrían rechazarlo.
- **Optimizadores.** Un compilador que no puede suponer que un `GO TO` es constante tiene poco que hacer con el párrafo.
- **Reentrada.** Reescribir la propia tabla de saltos del código es lo opuesto a la reentrada: dos llamadores comparten un solo `NEXT-CARD`. (Sobre el tema de reescribir el programa, consulta [APL](apl.md#funciones-que-se-modifican-a-sí-mismas-apl-weird).)

Usos legítimos: ninguno en código nuevo. Históricamente, sin embargo, en sistemas por lotes con poca memoria y sensibles al rendimiento, un interruptor fijado una vez y probado con un `GO TO` incondicional costaba menos que probar una bandera en cada pasada. Esa es la respuesta del "mainframe en 1978" a la pregunta recurrente: *era razonable cuando la restricción era real*. Consulta la [introducción](../introduccion.md#la-pregunta-recurrente).

### Ahora rómpelo tú

Consulta los [ejercicios](../exercises.md#b1-cobol-predice-y-luego-rompe-alter-verificado): predice qué pasa si agregas un `DISPLAY` a `NEXT-CARD` o cambias el `59`.

## Rarezas

- **Formato fijo.** Las columnas 1-6 eran un número de secuencia. `*` en la columna 7 es un comentario. Los nombres de divisiones y párrafos empiezan en la columna 8 ("área A") y las sentencias en la columna 12 ("área B"). **No se lee nada más allá de la columna 72**. Una línea larga se trunca en silencio, no se rechaza. `check.sh` rechaza las líneas de más de 72 ([`cobol-weird/check.sh`](../../src/cobol-weird/check.sh)).
- **`STRING` no limpia su destino.** Escribe desde la izquierda y deja los bytes viejos a la derecha, así que los búferes reutilizados necesitan `MOVE SPACES` antes.
- **Las palabras reservadas están en todas partes.** `TAB` está reservada en GnuCOBOL, por eso el carácter de tabulación es `WS-TAB`.
- **`SYSTEM` devuelve el estado de espera sin procesar**: un código de salida de 3 vuelve como 768. [`cobol-weird`](../../src/cobol-weird/README.md#cómo-funciona-el-truco) divide entre 256 para recuperarlo.
- **`ACCEPT ... FROM ENVIRONMENT` deja el campo en blanco** cuando la variable no está definida, en lugar de dejarlo como estaba.
- **La semana ISO hay que construirla a mano.** COBOL tiene funciones de fecha, pero no de semana ISO. `FUNCTION INTEGER-OF-DATE` cuenta desde 1601-01-01 (un lunes) y la regla del jueves son cuatro `COMPUTE`. El README indica que se comprobó con `date +%G-W%V` para 2020-2030.
- **Elegir sin `IF`.** [`cobol-weird` L119](../../src/cobol-weird/timecards.cob#L119): `COMPUTE WS-BASE-IX = 1 + FUNCTION MIN(WS-XDG-LENGTH, 1)` elige una de dos entradas de la tabla solo con datos.
- **`ALTER` necesita un párrafo de una sola `GO TO`.** Pon un `DISPLAY` en `NEXT-CARD` y el compilador lo rechaza.
- **Un error de tamaño deja sin cambios el campo de destino**, así que `WS-HEADROOM` no necesita reinicio. Sin `ON SIZE ERROR`, la suma descartaría en silencio el dígito inicial (99 + 1 = 00).

## Lo raro junto a lo aburrido

[`cobol`](../../src/cobol/README.md) hace el trabajo en un solo `PERFORM ... UNTIL OVER-FORTY` con la regla declarada como datos. [`cobol-weird`](../../src/cobol-weird/README.md) lo hace con saltos reconectados. La primera es más fácil de cambiar y de leer; la segunda muestra lo que el lenguaje le permite a un programa hacerse a sí mismo.

## ¿En qué circunstancias esta idea terrible se volvería razonable?

Rara vez en la forma que se muestra. Sin embargo, la regla de parada de nivel `88` es un buen diseño dondequiera que las reglas de negocio cambien más a menudo que el código. La forma con `ALTER` era razonable cuando la memoria y los ciclos eran la restricción y los ingenieros que mantenían el sistema entendían cada salto. Dejó de serlo cuando crecieron los equipos, las herramientas y los horizontes de mantenimiento.

<!-- BEGIN GENERATED program-flow:languages/cobol.md -->
## How each program runs

Each picture below is the `## Program Flow` section of an entry's README, copied here by the build. It shows how that program makes the work happen: what the language, runtime or tool really does. [The introduction](../introduccion.md#qué-hace-el-reto) shows what the challenge asks for and where entries differ.

### Program flow of `cobol`

From [`cobol`](../../src/cobol/README.md) ([source section](../../src/cobol/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: cobol: PERFORM UNTIL with the stop rule declared as data
    accDescr: A flowchart. Set-up and open-script run once. Then PERFORM DRAW-CARD repeats until the 88-level condition OVER-FORTY, declared on WS-TOTAL, is true. Each pass draws a card, adds its hours to the total, prints the row and writes an INSERT line. When OVER-FORTY is true the loop ends, the script is committed with sqlite3, and the run stops.
    A["SET-UP, OPEN-SCRIPT: seed, ISO week, folder, SQL file"] --> B{{"OVER-FORTY? WS-TOTAL in 41 to 99"}}
    B -->|No| C["DRAW-CARD: category from MOD of WS-ENTRIES, hours, ADD to WS-TOTAL"]
    C --> D["DISPLAY the row, WRITE the INSERT line"]
    D --> B
    B -->|Yes| E["COMMIT-SCRIPT: run sqlite3"]
    E --> F["DISPLAY summary, STOP RUN"]
```

**What this shows:** a conventional structured loop. `PERFORM DRAW-CARD UNTIL OVER-FORTY` tests the condition before every pass, so the test is a real node and the cycle is a real edge.

**Why this mechanism matters:** the stop rule is data, not code. `OVER-FORTY` is an 88-level name for the values 41 to 99 of `WS-TOTAL`, so the loop asks the data whether to go on. The weird sibling [`cobol-weird`](../../src/cobol-weird/README.md) has no such test.

### Program flow of `cobol-weird`

From [`cobol-weird`](../../src/cobol-weird/README.md) ([source section](../../src/cobol-weird/README.md#flujo-del-programa)).

```mermaid
stateDiagram-v2
    accTitle: cobol-weird: the target of one GO TO is the loop
    accDescr: A state diagram. The state is the current target of the single GO TO in the NEXT-CARD paragraph. It starts as Meetings. Each category paragraph rewrites it to the next category with ALTER, so the cycle is Meetings, Coding, Debugging, Learning, and back to Meetings. When the two-digit headroom field overflows, ON SIZE ERROR rewrites the target to FINISH-RUN, which commits the script and stops.
    state "Meetings" as M
    state "Coding" as C
    state "Debugging" as D
    state "Learning" as L
    state "FINISH-RUN" as F
    state "NEXT-CARD's GO TO jumps to" as T {
        [*] --> M
        M --> C : ALTER
        C --> D : ALTER
        D --> L : ALTER
        L --> M : ALTER
    }
    T --> F : ON SIZE ERROR, ALTER
    F --> [*] : COMMIT, sqlite3, STOP RUN
```

**What this shows:** the state of this program is the target of one `GO TO`. Each card, the category paragraph named by the target runs, rewrites the target with `ALTER` to the next category, and falls into `RECORD-CARD`, which jumps back to `NEXT-CARD`. The source text of that `GO TO` never changes. The jump does.

**Why this mechanism matters:** there is no loop condition to draw. The exit is another rewrite: when `WS-HEADROOM` overflows, `ON SIZE ERROR` points the same `GO TO` at `FINISH-RUN`. Compare the plain [`cobol`](../../src/cobol/README.md) entry, where a `PERFORM ... UNTIL` tests a condition.
<!-- END GENERATED program-flow:languages/cobol.md -->

## Las ciencias de la computación detrás de esta página

<!-- BEGIN GENERATED concepts:languages/cobol.md -->
The computer-science ideas behind this page: [Representing state](../informatica/02-que-cuenta-como-maquina.md#representing-state), [Control flow](../informatica/03-flujo-de-control-y-continuaciones.md#control-flow), [Goto and structured programming](../informatica/03-flujo-de-control-y-continuaciones.md#goto-and-structured-programming), [The program counter](../informatica/03-flujo-de-control-y-continuaciones.md#the-program-counter), [Self-modifying code](../informatica/03-flujo-de-control-y-continuaciones.md#self-modifying-code), [Declarative programming](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#declarative-programming), [State](../informatica/06-estado-mas-alla-de-las-variables.md#state), [Exception handling](../informatica/07-efectos-errores-y-confirmacion.md#exception-handling), [Integrity constraints](../informatica/07-efectos-errores-y-confirmacion.md#integrity-constraints), [Undefined, unspecified and implementation-defined behavior](../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#undefined-unspecified-and-implementation-defined-behavior).
<!-- END GENERATED concepts:languages/cobol.md -->
