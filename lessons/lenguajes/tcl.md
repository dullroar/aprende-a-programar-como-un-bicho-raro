# Tcl

Entradas: [`src/tcl`](../../src/tcl/README.md) (un bucle `while`, diccionarios y una ventana Tk opcional) y [`src/tcl-weird`](../../src/tcl-weird/README.md) (el programa vive en SQLite).

Para una ruta de lectura avanzada con trazas y experimentos, consulta la [guía de estudio de Tcl](../guias-de-estudio/lenguajes/tcl.md).

## Qué hace especial a Tcl

La regla de Tcl es: "todo es un comando y cada comando recibe sus argumentos como cadenas de texto". No hay palabras clave para `while`, `proc` ni `if`: son comandos. `{...}` es solo una forma de entregar a un comando una cadena de texto sin evaluar. Esto hace que el lenguaje sea pequeño y que dos funciones sean baratas, aunque la mayoría de los lenguajes las considere exóticas: **reescribir cómo se resuelven los comandos desconocidos** y **ejecutar una cadena de texto como código en otro ámbito**.

| Característica | Dónde | Qué enseña |
| --- | --- | --- |
| Las llaves aplazan la evaluación | [`tcl/timecards.tcl` L40](../../src/tcl/timecards.tcl#L40): `while {$total <= $limit} {` | La condición es una cadena de texto entre llaves que se evalúa de nuevo en cada pasada. Escribe `while $total <= $limit` y se sustituye una sola vez y nunca cambia. La misma regla explica por qué `expr` siempre debe ir entre llaves. |
| Los diccionarios son valores | [L44](../../src/tcl/timecards.tcl#L44): `lappend cards [dict create category $category hours $hours total $total]` | Una tarjeta es un diccionario simple; no se necesita una clase. |
| `dict with` desempaqueta en variables | [L86](../../src/tcl/timecards.tcl#L86): `dict with card {` | Las claves de un diccionario se convierten en variables locales para un bloque. |
| `db eval` vincula variables de Tcl como parámetros SQL | [L87-91](../../src/tcl/timecards.tcl#L87-L91): `VALUES ($runId, $category, $hours, $total, $week, ...)` | El `$name` dentro del SQL entre llaves no se pega como texto. SQLite lo recibe como parámetro vinculado, así que las comillas nunca son un problema. |
| `try ... finally` cierra la base de datos | [L77-95](../../src/tcl/timecards.tcl#L77-L95) | La limpieza se realiza incluso si ocurre un error. |
| Tk es un paquete, no un programa | [L110](../../src/tcl/timecards.tcl#L110): `showWindow`, `--gui` y `--seconds N` | Una interfaz gráfica requiere unos pocos comandos y con Xvfb se puede probar sin pantalla. |
| Una guarda del punto de entrada | [L170](../../src/tcl/timecards.tcl#L170): `if {[info exists argv0] && [file normalize $argv0] eq [file normalize [info script]]}` | El archivo puede cargarse con `source` para probarlo sin ejecutarlo. |

## SQLite como programa

### Contempla la monstruosidad

```bash
sandbox/container/run-image.sh src/tcl-weird
```

Abre [`timecards.tcl`](../../src/tcl-weird/timecards.tcl). Se definen exactamente **dos** procedimientos en Tcl y ninguno reparte una tarjeta. El código que lo hace es *texto en una tabla de base de datos* y el bucle es un disparador SQL.

### ¿Cómo demonios funciona eso?

Tres puntos de conexión crean un programa de la nada.

**Punto de conexión 1: SQL puede llamar a Tcl.** [`db function tcl call`](../../src/tcl-weird/timecards.tcl#L28-L34) registra una función SQL `tcl(command, args...)` implementada como un procedimiento Tcl que ejecuta un comando. Desde cualquier sentencia SQL, `SELECT tcl('hours')` ejecuta el comando Tcl `hours` y devuelve su resultado.

**Punto de conexión 2: `unknown` es la ruta de biblioteca.** Cuando se le pide a Tcl ejecutar un comando inexistente, llama a un comando llamado `unknown`. La entrada [lo renombra y reemplaza](../../src/tcl-weird/timecards.tcl#L36-L49): busca el nombre en una tabla TEMP `tcl_code(name, params, body)`. Si hay una fila, define un procedimiento a partir de ella con `proc $name $params $body` y vuelve a intentarlo. Así, `hours`, `category`, `born` y los demás *nunca* se escriben como código fuente Tcl. La primera llamada a `tcl('hours')` no encuentra ese comando y consulta a `unknown`. Este encuentra la fila en SQLite, construye el procedimiento y lo ejecuta. Al final, el programa imprime qué procedimientos salieron de la base de datos:

```text
# every proc that ran was fetched from SQLite by unknown: born category hours init runid week
```

**Punto de conexión 3: el bucle es un disparador recursivo.** El [disparador](../../src/tcl-weird/timecards.tcl#L104-L114):

```sql
CREATE TEMP TRIGGER next_card AFTER INSERT ON main.demo_timecards
BEGIN
    SELECT tcl('born', NEW.category, NEW.hours, NEW.running_total, NEW.iso_week);
    UPDATE draw SET h = tcl('hours') WHERE NEW.running_total <= 40;
    INSERT INTO demo_timecards(...)
    SELECT NEW.run_id, tcl('category', ...), h, NEW.running_total + h, ...
    FROM draw
    WHERE NEW.running_total <= 40;
END;
```

Insertar una tarjeta activa el disparador, que imprime la tarjeta (mediante `tcl('born', ...)`) e inserta la *siguiente*. Esa inserción vuelve a activar el disparador. La `WHERE NEW.running_total <= 40` es la regla de parada: cuando es falsa, el `INSERT ... SELECT` no inserta nada y no se activa otro disparador. Se requiere [`PRAGMA recursive_triggers = ON`](../../src/tcl-weird/timecards.tcl#L55): por defecto, SQLite no permite que un disparador se active a sí mismo. La sentencia que inicia todo es el `INSERT` de la tarjeta 1.

**La ventana también es dato.** Con `--gui`, una tabla TEMP `ui(id, command)` contiene ocho comandos Tk que ejecuta `SELECT tcl('uplevel', '#0', command) FROM ui ORDER BY id`. `uplevel #0` evalúa cada cadena de texto en el nivel global, donde deben estar `.cards` y `.note`. Luego, el `born` de cada tarjeta añade una fila a la vista de árbol y actualiza la pantalla.

### ¿Qué acabamos de aprender?

- **El código y los datos son lo mismo en Tcl.** Un procedimiento se crea a partir de dos cadenas de texto; tú decides de dónde vienen. Aquí es una fila de la base de datos, así que `UPDATE tcl_code SET body = ...` es un parche en caliente.
- **Un disparador de base de datos es una construcción de flujo de control.** Es un manejador de eventos que puede causar el evento que maneja: eso es recursión.
- **Cada punto de conexión es una oportunidad para crear un bucle.** SQLite permite registrar funciones y disparadores; Tcl permite interceptar búsquedas. Cada uno por separado es una función; juntos forman un entorno de ejecución.
- **Las llaves frente a la sustitución** lo deciden todo en Tcl. (Compara [el tiempo de expansión frente al tiempo de ejecución de Make](make-cmake.md#gnu-make) y [el entrecomillado de m4](m4.md).)

Etiquetas: `proc`, `unknown`, `uplevel`, `namespace`, `dict` y `try` tienen la etiqueta **garantizado** en Tcl 8.6. `db function` y la vinculación de variables de `db eval` pertenecen al paquete sqlite3 de Tcl (**permitido por la implementación**: la interfaz es estable, pero no forma parte de Tcl). Los disparadores recursivos necesitan `PRAGMA recursive_triggers`, una característica de SQLite con la etiqueta **garantizado** cuando está activada. Que las horas de cada tarjeta se obtengan exactamente una vez se cumple por construcción: las horas se escriben en una tabla TEMP de una fila y se leen dos veces. Por eso, el resultado no depende de cuántas veces SQLite evalúe una función. (Una versión anterior usaba una subconsulta y dependía de que SQLite llamara a la función una vez por fila. Eso es **aprovechado por accidente**: SQLite no lo promete para funciones no deterministas.)

### Haz esto en producción y estás despedido

- **Tu programa no está en control de versiones.** Está en una tabla TEMP que existe solo para esta conexión. El archivo `.tcl` contiene dos procedimientos y una cadena de texto.
- **`unknown` es global.** Ahora cada comando mal escrito provoca una consulta a la base de datos antes del error. Si otra persona puede escribir en la tabla, también puede escribir en tu programa.
- **Los disparadores son invisibles en las trazas de pila** y el límite de profundidad de recursión de SQLite (`SQLITE_MAX_TRIGGER_DEPTH`, 1000 por defecto) es una restricción oculta.
- **El entrecomillado tiene dos niveles de profundidad:** el Tcl dentro del SQL dentro del Tcl. Una llave suelta rompe la cadena de texto exterior.
- **Un valor usado dos veces debe extraerse una sola vez.** Las horas se usan como horas y dentro del total acumulado. El disparador las guarda en la tabla TEMP `draw` de una fila y las lee de allí. `check.sh` cuenta las llamadas al procedimiento `hours` (una por tarjeta).
- **Particularidad de Tk:** un `tclsh` que ha cargado Tk no termina cuando termina el script. La entrada llama a `destroy .` (un programa Tk normal espera eventos).

Usos legítimos: **cargar código a demanda** (el propio `unknown` de Tcl ya llama a `auto_load` para encontrar en disco la definición de un comando), **funciones SQL que llaman de vuelta al lenguaje anfitrión** (una función estándar de SQLite) y **mantener reglas en una tabla** para que puedan cambiar sin un despliegue. Por la misma razón, los Starkits de Tcl empaquetaban una aplicación entera en un archivo de sistema de archivos virtual: código que viaja con sus datos.

### Ahora rómpelo tú

Mira los [ejercicios](../exercises.md#b12-tcl-edit-the-program-in-the-database-verified).

## Particularidades

- **Triggers reject a qualified table name in `INSERT`.** Inside the trigger, `main.demo_timecards` is an error; the unqualified name is required, while the `AFTER INSERT ON main.demo_timecards` line does qualify, because a TEMP trigger watches a table in the main database.
- **`expr` without braces is both slower and a code-injection hole.** The idiomatic entry braces every `expr`.
- **`dict with` writes back**: assignments to the unpacked variables update the dict.
- **`DISPLAY=:0` under WSL hangs Tk.** Tests use `xvfb-run`; see `check.sh`.

## Weird next to boring

[`tcl`](../../src/tcl/README.md) is a namespaced `while` with dicts and bound SQL parameters: tidy, testable, unit-testable (`draw` is called 2,000 times in its check). [`tcl-weird`](../../src/tcl-weird/README.md) has the same output and none of those properties. The first is how you write Tcl; the second is what Tcl's "everything is a string command" *permits*. Compare [`haskell`](haskell.md#la-es-perezosa-como-flujo-de-control), where effects hide inside a lazy list, and [CMake](make-cmake.md#cmake), where a `while()` condition is the register machine.

## Under what circumstances would this terrible idea become reasonable?

When your code genuinely belongs with your data: a rules engine where rules are rows, a game where scripts live in the save file, a tool that must patch behavior in a running system. Using a recursive trigger as a `while` loop is a stunt; storing procs in a table is a design.

<!-- BEGIN GENERATED program-flow:languages/tcl.md -->
## How each program runs

Each picture below is the `## Program Flow` section of an entry's README, copied here by the build. It shows how that program makes the work happen: what the language, runtime or tool really does. [The introduction](../introduccion.md#what-the-challenge-does) shows what the challenge asks for and where entries differ.

### Program flow of `tcl`

From [`tcl`](../../src/tcl/README.md) ([source section](../../src/tcl/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: tcl: an ordinary while loop in a namespace, then one transaction
    accDescr: A flowchart. The main procedure parses the arguments with a while, lassign and switch loop, seeds the random generator from the clock and the process id, and calls draw. The draw procedure is a while loop. While the total is at or under the limit, it draws hours, adds them to the total with incr, picks the next category, and appends a card as a dict. When the total is over the limit, the save procedure opens SQLite and writes all the cards inside one transaction. Then the program prints the cards. Only if asked does it build a Tk window with a treeview.
    A["main: parse argv, seed rand from the clock and pid"] --> B{{"draw: while total <= limit?"}}
    B -->|yes| C["randomHours, incr total, pick a category, lappend a card as a dict"]
    C --> B
    B -->|no| D["save: db transaction inserts every card with bound parameters"]
    D --> E["Print the cards; build the Tk treeview only if --gui was given"]
```

**What this shows:** the conventional Tcl shape. A `while` is the loop, a dict is the card, and `db transaction` makes the save all-or-nothing. A guard around `main` lets the checks `source` the file and test `draw` in the same process.

**Why this mechanism matters:** the program draws first and saves afterwards, so the card list is complete before the database sees it. Tcl's `while` re-evaluates its test each pass, and the test comes before the draw, so the crossing card is kept. The weird sibling [`tcl-weird`](../../src/tcl-weird/README.md) moves the loop into the database.

### Program flow of `tcl-weird`

From [`tcl-weird`](../../src/tcl-weird/README.md) ([source section](../../src/tcl-weird/README.md#flujo-del-programa)).

```mermaid
sequenceDiagram
    accTitle: tcl-weird: a recursive SQLite trigger calls Tcl procs that are fetched from a table
    accDescr: A sequence diagram. The Tcl host installs three hooks and inserts the first card. Each insert fires a trigger in SQLite. The trigger calls the SQL function tcl, which calls back into Tcl. The first time the Tcl side asks for a command such as born, the command does not exist, so Tcl calls unknown. The unknown handler reads the proc's text from the tcl_code table, defines the proc and retries the call. The call prints the row. The trigger then inserts the next card, but only while the total of the card just inserted is 40 or less. That insert fires the trigger again. When the total is over 40, nothing is inserted, and control returns to the host, which prints the summary.
    participant H as Tcl host
    participant D as SQLite and the next_card trigger
    participant U as unknown handler
    participant T as tcl_code table
    H->>D: INSERT the first card
    loop each INSERT fires the trigger, while the total is 40 or less
        D->>H: SQL function tcl calls the Tcl command born
        H->>U: born does not exist yet, so Tcl calls unknown
        U->>T: look up the proc's params and body
        T-->>U: the text of the proc
        U->>H: define the proc, retry the call
        H-->>D: the row is printed
        D->>D: INSERT the next card: the trigger fires again
    end
    D-->>H: total is over 40, no insert: the trigger chain ends
    H->>H: print the summary
```

**What this shows:** the loop is a trigger that inserts a row and so fires itself, and every number and printed line comes from Tcl code stored as text in a table. The first call of a proc takes the long way, through `unknown` and the table, and later calls find the proc defined.

**Why this mechanism matters:** the database is dispatching, but it is not an event queue. The trigger runs synchronously inside the `INSERT`, and the recursion is the loop. The `WHERE` on the trigger's insert is the stop rule. Control moves between three layers (Tcl, SQL, Tcl) on one call stack.
<!-- END GENERATED program-flow:languages/tcl.md -->

## Computer science behind this page

<!-- BEGIN GENERATED concepts:languages/tcl.md -->
The computer-science ideas behind this page: [Arbitrary code execution](../informatica/01-lectura-de-un-programa-adversarial.md#arbitrary-code-execution), [Control flow](../informatica/03-flujo-de-control-y-continuaciones.md#control-flow), [Recursion](../informatica/03-flujo-de-control-y-continuaciones.md#recursion), [Interpreters and virtual machines](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#interpreters-and-virtual-machines), [State](../informatica/06-estado-mas-alla-de-las-variables.md#state), [Scope and binding](../informatica/06-estado-mas-alla-de-las-variables.md#scope-and-binding), [Homoiconicity: code as data](../informatica/06-estado-mas-alla-de-las-variables.md#homoiconicity-code-as-data), [Reflection and metaprogramming](../informatica/06-estado-mas-alla-de-las-variables.md#reflection-and-metaprogramming), [Database triggers](../informatica/06-estado-mas-alla-de-las-variables.md#database-triggers), [Serialization, deserialization and object pickling](../informatica/06-estado-mas-alla-de-las-variables.md#serialization-deserialization-and-object-pickling), [Transactions](../informatica/07-efectos-errores-y-confirmacion.md#transactions), [Callbacks](../informatica/10-eventos-retrollamadas-y-flujo-de-control-reactivo.md#callbacks).
<!-- END GENERATED concepts:languages/tcl.md -->
