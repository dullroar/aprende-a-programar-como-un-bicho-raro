# Por objetivo

Tres objetivos sostienen todo en [¡Aprende a programar como un bicho raro!](README.md). Cada uno responde de otra forma a la pregunta "¿por qué alguien haría esto?"

## Enseña computación, no solo trucos computacionales

Un truco es "esta fórmula mágica hace que el bucle se detenga". La computación es "esta es la máquina que se ejecuta y aquí vive su estado".

Cada entrada rara te obliga a nombrar la máquina que se esconde dentro de un lenguaje. Cuando puedes nombrarla, el truco es solo un programa para esa máquina.

<!-- BEGIN GENERATED machines -->
| Language / tool | The machine it really is | Where the program's state lives | Lesson |
| --- | --- | --- | --- |
| .NET regex | A counter built from a stack | Balancing-group capture stacks | [regex](lenguajes/regex.md#net-grupos-de-equilibrio) |
| APL | Ordinary: an array machine that draws five cards at once and decides afterwards | Arrays, and nothing hidden | [apl](lenguajes/apl.md) |
| APL | An array machine, with code that is also an array | Arrays, and the source text of functions | [apl](lenguajes/apl.md#funciones-que-se-modifican-a-sí-mismas-apl-weird) |
| AWK | Ordinary: a `while` loop in `BEGIN`, with a pipe to sqlite3 as the output | Arrays and parameter-local variables | [awk](lenguajes/awk.md) |
| AWK | A record-processing loop that you can aim at any byte stream | The input stream and the record separator `RS` | [awk](lenguajes/awk.md#registros-a-partir-de-un-flujo-de-bytes-aleatorios-awk-weird) |
| C# `for` | Three expression slots | Fields of one anonymous object | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#el-original-modernchallenge1) |
| CMake | A register machine | `CMAKE_MATCH_1`..`5`, rebuilt every pass | [make-cmake](lenguajes/make-cmake.md#cmake) |
| COBOL | Ordinary: a structured `PERFORM ... UNTIL` loop that asks the data for the stop rule | `WS-TOTAL` and its 88-level name `OVER-FORTY` | [cobol](lenguajes/cobol.md) |
| COBOL | A program whose jump targets are mutable | The target of one `GO TO` | [cobol](lenguajes/cobol.md#alter) |
| Common Lisp | Ordinary: one `LOOP` that runs its clauses in order on every pass | Variables the `LOOP` owns, such as `total` | [lisp](lenguajes/lisp.md) |
| Common Lisp | A method dispatcher with a pluggable combination rule | The class precedence list, and each method's return value | [lisp](lenguajes/lisp.md#combinación-de-métodos-como-flujo-de-control) |
| ed | A string-rewriting machine with line addresses | The editor buffer: one line per card, and marks (x) that are added by joining lines | [editors](lenguajes/editores.md#el-búfer-es-la-máquina) |
| Ex | A register machine whose registers are editor marks, and whose program is a register that runs itself | The marks (where we are on a tape of numbered lines), the first line of the buffer (the next card), and registers a, d and n | [editors](lenguajes/editores.md#un-programa-que-puedes-editar) |
| Forth | Ordinary: a stack machine with one `begin ... until` loop | The variables `total` and `cards`, and the data stack | [forth](lenguajes/forth.md) |
| Forth | A stack machine with a movable instruction pointer | The data stack and the parse position `>in` | [forth](lenguajes/forth.md) |
| GNU find | A tree walk that grows the tree it is walking, with find itself reading the depth and the clock | The path from the start directory to the directory being visited; its depth is the running total | [find](lenguajes/find.md) |
| GNU Make | A dependency graph that can restart itself | Which `.tc-N.mk` files exist, and `MAKE_RESTARTS` | [make-cmake](lenguajes/make-cmake.md#gnu-make) |
| GNU sed | A string-rewriting system (a Markov algorithm) | One line of text, rewritten until no rule applies | [regex](lenguajes/regex.md#gnu-sed) |
| GNU tar | A tape reader (tar) feeding a five-word interpreter | The archive's members, which are the program, plus one SQLite row that says whether the run has halted or faulted | [tar](lenguajes/tar.md#un-programa-que-es-un-archivo) |
| GNU tar | A finite-state machine, driven by a logical clock that tar supplies | One SQLite row (the machine's registers) and the number of records tar has written | [tar](lenguajes/tar.md#el-archivo-es-el-reloj) |
| Go | Three expression slots, with helper functions in the slots | Fields of one anonymous struct | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| Haskell | Ordinary: a lazy list that one `span` reads until the test fails | The unevaluated parts of the lists, read on demand | [haskell](lenguajes/haskell.md) |
| Haskell | A lazy graph reducer | Thunks: which parts of a list have been demanded | [haskell](lenguajes/haskell.md#la-es-perezosa-como-flujo-de-control) |
| Java | Three expression slots | Fields of one anonymous class | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| JavaScript | Three expression slots | Properties of one object literal | [javascript](lenguajes/javascript.md#el-for-sin-cuerpo-en-node) |
| JavaScript | A set of listeners on one EventEmitter, which together are a state machine | The running total and the card count, held in one object that only the listeners touch | [javascript](lenguajes/javascript.md#escuchadores-de-eventos-hasta-el-fondo) |
| JavaScript | A closure-backed state machine, pulled by a lazy iterator | Variables captured by closures: the generator's number, and the machine's card count, total and stop flag | [javascript](lenguajes/javascript.md#clausuras-hasta-el-fondo) |
| Kotlin | A lazy sequence that the empty `for` pulls | Properties of one object expression, the seed of the sequence | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| LINQ | A lazy chain of LINQ stages that one final `Aggregate` demands | Inside the stages' enumerators, and in the database | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#la-ejecución-diferida-y-el-truco-de-convertir-void-en-valor) |
| LINQ | A lazy query that its closing `Single()` demands | A prefix sum recomputed in each `where`, and the database; no accumulator variable | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#la-ejecución-diferida-y-el-truco-de-convertir-void-en-valor) |
| m4 | A text-rescanning machine | The input stream: whatever macro text has not been read yet | [m4](lenguajes/m4.md#un-bucle-hecho-de-reescaneo) |
| PCRE2 | A backtracking search with hooks | A C struct that never rewinds | [regex](lenguajes/regex.md#pcre2-los-callouts-como-conjunto-de-instrucciones) |
| pcre2grep | A backtracking search that runs one program per callout | SQLite rows, and the exit code of each callout | [regex](lenguajes/regex.md#pcre2grep-códigos-de-salida-como-flujo-de-control) |
| Perl | A backtracking search with hooks | `local` variables that unwind (effects do not) | [regex](lenguajes/regex.md#perl-código-dentro-de-la-coincidencia) |
| POSIX find | A tree walk that grows the tree it is walking | The path from the start directory to the directory being visited | [find](lenguajes/find.md) |
| Python | A function that `iter` calls until it returns the sentinel `False` | Attributes of one state object passed to the lambda | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| Rust | A chain of values from `successors`, which stops at `None` | A new immutable `DemoBatch` for every step; nothing is mutated | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| Tcl | Ordinary: a `while` loop that draws first and saves afterwards | Dicts and Tcl variables, saved in one `db transaction` | [tcl](lenguajes/tcl.md) |
| Tcl | A string-command interpreter whose command lookup can be hooked | A TEMP table of proc source, and the depth of trigger recursion | [tcl](lenguajes/tcl.md#sqlite-como-programa) |
| XAML | An object-graph constructor that runs methods as it parses | Document order, plus "carrier" arrays | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#xaml) |
<!-- END GENERATED machines -->

Cuando hayas visto cuatro lugares distintos para responder "¿dónde estoy en el programa?", dejarás de tratar la pila de llamadas y el contador del bucle como leyes de la naturaleza. Ese es el primer objetivo: separar el *flujo de control*, el *estado*, el *orden de evaluación* y los *efectos secundarios*, que la mayoría de los lenguajes sueldan en una sola pieza, y verlos separarse.

Consulta [patrones](patrones.md) para ver el mismo material organizado por mecanismo.

## Distintas formas de resolver problemas, limitadas solo por la imaginación

El lema del repositorio es **NO HAY BLOQUEOS, SOLO FALTA IMAGINACIÓN.** Las mismas diez líneas de requisitos ya se resolvieron con un bucle sin cuerpo, una regex que devuelve falso a propósito, un Makefile que se vuelve a ejecutar solo, una lista cuyos elementos escriben en una base de datos cuando los miras y una función que escribe a su sucesora.

Tres hábitos que puedes llevarte de ahí:

- **Pregunta dónde se permite que ocurra el trabajo.** La regla era una sola sentencia, así que las cláusulas del bucle, una canalización LINQ, un analizador sintáctico, un iterador y el retroceso de un motor de expresiones regulares se convirtieron en lugares donde hacer el trabajo. ¿Qué partes de tu pila habitual son "así se hace y punto" y cuáles son realmente obligatorias?
- **Compara lo raro con lo común.** [`apl`](../src/apl/README.md) usa cinco tiradas y un *take-while*; [`apl-weird`](../src/apl-weird/README.md) usa una función que se copia y se reescribe a sí misma. [`haskell`](../src/haskell/README.md) usa un solo `span`; [`haskell-weird`](../src/haskell-weird/README.md) pone los efectos dentro de la lista. [`lisp`](../src/lisp/README.md) es un solo `LOOP`; [`lisp-weird`](../src/lisp-weird/README.md) no tiene ningún bucle y deja que una jerarquía de clases haga la cuenta. [`tcl`](../src/tcl/README.md) es un `while`; [`tcl-weird`](../src/tcl-weird/README.md) guarda su código en una tabla de una base de datos. Cada par muestra qué gana cada enfoque y cuál es su costo.
- **Documenta los límites con honestidad.** [`RETO.md`](../RETO.md) dice: "Una limitación bien demostrada es más interesante que esquivarla con trampas." La página de [problemas de bloqueo](problemas-bloqueantes.md) se construye a partir de esos límites.

Piensa fuera de lo convencional y luego anota dónde resultó que lo convencional sostenía la estructura. Consulta [problemas superados](problemas-superados.md).

## Entiende tu lenguaje (o tus lenguajes): fortalezas y debilidades

No sabes para qué sirve una característica hasta que sabes qué pasa cuando la fuerzas.

| Lenguaje | Fortaleza que revela la versión rara | Debilidad que revela |
| --- | --- | --- |
| APL | El pensamiento con arreglos reemplaza la mayoría de los bucles; el código son datos | Difícil de leer, de teclear y de escribir en una pizarra (consulta [APL](lenguajes/apl.md)) |
| AWK | El bucle de registros y las reglas de patrón-acción hacen que el análisis sintáctico y el filtrado sean muy breves | El subconjunto portable es pequeño y el estándar no incluye las expresiones regulares `RS` y `RT`, que son extensiones de gawk |
| C# | Rico en expresiones: LINQ, los tipos anónimos, la reflexión y XAML en tiempo de ejecución pueden convivir en un mismo encabezado `for` | `void` no se compone; `DbContext` no es seguro para hilos; en el nivel superior se requieren sentencias, no expresiones |
| CMake | `while()` vuelve a expandir su condición, y `MATCHES` deja capturas en variables | Su expresión regular no admite repetición contada, anticipación (*lookahead*) ni referencias inversas |
| COBOL | Aritmética decimal y cláusulas *picture* de campo que hacen el redondeo y las comprobaciones de rango como datos | Un flujo de control que `ALTER` puede volver ilegible; columnas fijas; un vocabulario difícil de extender |
| Common Lisp | El lector, las macros y el sistema de objetos son programables, así que el flujo de control se puede reconstruir a partir de tipos | El resultado es invisible: nada en el código dice "bucle", y las herramientas solo muestran llamadas a funciones genéricas |
| Forth | Minúsculo y con control total: puedes acceder a la posición de análisis del propio intérprete | Sin barandillas de protección: los efectos sobre la pila existen solo por convención |
| GNU Make | El seguimiento de dependencias y el reinicio vienen incluidos | Es una herramienta de compilación: no tiene enteros ni E/S real, y la granularidad de las marcas de tiempo importa |
| Haskell | La evaluación perezosa convierte "cuánto leer" en la regla de parada | La evaluación perezosa hace que "¿cuándo se ejecuta esto?" forme parte del significado cuando hay efectos |
| m4 | Las comillas dan evaluación perezosa en un lenguaje que no tiene nada más; son ideales para generar texto | Todo es texto global: no hay ámbito ni tipos, y un solo paréntesis que falte causa recursión infinita |
| Motores de expresiones regulares | El retroceso es una búsqueda general; los callouts y los bloques de código lo convierten en un programa | Precipicios de rendimiento; diferencias entre motores; el fallo descarta las capturas (en .NET) |
| Tcl | Todo es un comando de cadena de texto, así que el código se puede cargar, enganchar y generar desde cualquier lugar (incluso desde una fila de una base de datos) | Dos niveles de comillas y cadenas de texto en todas las capas: los errores aparecen tarde |
| XAML | Un formato declarativo, así que las herramientas pueden leerlo y escribirlo | El analizador sintáctico puede ejecutar métodos arbitrarios, algo que los formatos declarativos no están pensados para hacer |

Las páginas de lenguajes también etiquetan los comportamientos como **garantizado**, **permitido por la implementación** o **aprovechado por accidente**, como se explica en la [introducción](introduccion.md#tres-tipos-de-conocimiento). Una fortaleza en la que confías es tan sólida como la etiqueta que la acompaña.

Continúa con la [informática detrás de todo](informatica/README.md): las mismas ideas, un concepto a la vez, con un párrafo sobre por qué existe cada uno y cuándo usarlo. Después consulta los [lenguajes](lenguajes/README.md).
