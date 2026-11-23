# ¡Aprende a programar como un bicho raro!

> **40 retos en 29 lenguajes**
<!-- Keep this line current whenever an entry is added: challenges = the folders in src/; languages = the distinct ids that entries list under `languages:` (the same languages as the book's Index of languages). `python lessons/book/build.py --check` prints both numbers and warns when this line is stale. -->

Una serie de respuestas a un reto de código que se transformó en un conjunto de ejercicios educativos sobre lenguajes de programación y sobre cómo pensar en ellos. **Nuevo: [*¡Aprende a programar como un bicho raro!*](lessons/README.md)**, un conjunto de lecciones basadas en estos ejemplos. El libro se numera desde la v3 (la v4 añade una imagen de cómo se ejecuta cada programa y un capítulo sobre eventos): consulta [qué añadió cada versión](lessons/book/VERSIONS.md).

**BICHO** significa **Bicho raro, Interpreta, Camino indirecto, Hallazgos y Octetos**. La B es recursiva. Al menos los programas tienen una regla de parada.

## Por qué existe

La primera versión fue un [ejercicio de clase de 2008](/docs/My%20Code%20Challenge.pdf), creado para mostrar las nuevas características de C# 3.0 y .NET 3.x. Mantener la regla de una sola sentencia y llevarla a lenguajes nuevos resultó ser una gran forma de aprender. Así descubres qué permiten hacer realmente esos lenguajes cuando vas más allá de lo que cubren los tutoriales. Cada entrada responde la misma pregunta con su propio acento: *¿hasta dónde se puede empujar la maquinaria propia de un lenguaje —sus iteradores, su motor de expresiones regulares, su analizador sintáctico de marcado, su herramienta de compilación— antes de que empiece a comportarse como un programa de propósito general?*

Es una broma con un trabajo serio dentro. Debajo de cada entrada hay una lección real sobre una construcción real del lenguaje —LINQ, XAML, GNU Make, expresiones regulares, iteradores, callouts— que se enseña llevando esa construcción hasta que hace algo que su propia documentación no pensaría en mostrarte. Por eso el README de cada carpeta tiene una sección **Cómo funciona el truco**: léela y habrás aprendido la construcción, no solo visto un truco. La diversión te abre la puerta; el "oh, ASÍ es como funciona en realidad" es lo que te llevas. El plan de estudios completo, con ejercicios, está en **[¡Aprende a programar como un bicho raro!](lessons/introduccion.md)**.

La idea de fondo, la que vale la pena conservar cuando se acaben las bromas: **NO HAY BLOQUEOS, SOLO FALTA IMAGINACIÓN.**

Se ha convertido en un pequeño contagio amistoso. **Ken también se contagió.** Lo que empezó como un programa en C# ha crecido hasta ser una colección escrita por más de una persona, y sigue creciendo.

## Psst, oye, chico

**¡Pruébalo en casa!** **¡No se lo digas al jefe!**

Llevas años escribiendo código limpio: funciones pequeñas, nombres con sentido, pruebas. *Aburrido.* Aquí hay un bucle `for` con el cuerpo vacío que abre una base de datos, inicia un hilo, dibuja una ventana y la muestra y la oculta con un fundido. Todo esto antes de que el primer punto y coma termine de ser raro.

Sabes que quieres escribir código maravillosamente malo. **Claro que sí lo sabes.**

## ¿Quieres aprender de él?

**[¡Aprende a programar como un bicho raro!](lessons/README.md)** *Programas que no deberías escribir. Características del lenguaje que sí deberías entender.* Lecciones por [objetivos](lessons/objetivos.md), por [concepto de ciencias de la computación](lessons/informatica/README.md), por [lenguaje](lessons/lenguajes/README.md) (incluidos [el `ALTER` de COBOL](lessons/lenguajes/cobol.md#alter) y [APL en la pizarra](lessons/lenguajes/apl.md)) y por [patrón de solución](lessons/patrones.md), además de [problemas superados](lessons/problemas-superados.md), [problemas bloqueantes](lessons/problemas-bloqueantes.md) y [ejercicios](lessons/exercises.md) que puedes ejecutar en un contenedor.

¿Quieres un plan para todo un semestre? El **[plan de estudios de 16 semanas](docs/plan-de-estudios.md)** ([PDF](curriculum.pdf), [EPUB](curriculum.epub)) organiza en secuencia los capítulos del libro, las guías de estudio y los ejercicios para estudiantes de los últimos años de grado, estudiantes de posgrado y programadores autodidactas.

## ¿Listo para jugar?

Las reglas, la demo compartida y lo que debes y no debes hacer están en **[`RETO.md`](RETO.md)**. Elige un lenguaje. Elige una restricción. Crea algo terrible que funcione. ¿Quieres enviarlo? Consulta **[`CONTRIBUTING.md`](CONTRIBUTING.md)**.

## Los resultados hasta ahora

**¿Quieres ejecutar una entrada sin confiar en ella?** Cada entrada de Linux (incluidas las de Rust/GTK y Go) tiene su propio **contenedor Docker** diminuto y restringido, que la ejecuta sin red y te muestra lo que hizo. Cada entrada de Windows o con interfaz gráfica se ejecuta en un **Windows Sandbox** desechable, un entorno aislado (*sandbox*) que limita el acceso al sistema anfitrión. Consulta **[`SANDBOX-SETUP.md`](SANDBOX-SETUP.md)** para la configuración única. Después abre el README de la carpeta (enlazado en la tabla de abajo) y busca su sección **Ejecútalo en un contenedor** o **Ejecútalo en Windows Sandbox**, donde está el comando.

Cada entrada compila la misma demo pequeña: inventa algunas horas de tarjetas de tiempo de *Meetings / Coding / Debugging / Learning*, guárdalas en un archivo SQLite local **DEMO ONLY**, detente cuando el total pase de 40 (las dos entradas de LINQ usan en cambio una semana fija de 40 horas, y un total de exactamente 40 continúa en todas las demás entradas excepto `xaml`, que puede repartir como máximo cuatro tarjetas) y muestra el resultado. Nada de esto toca un sistema real de registro de horas. Consulta el [aviso legal](#aviso-legal).

**TODOS ESTOS EJEMPLOS ESTÁN PROBADOS Y FUNCIONAN COMO SE ANUNCIA.** Recuérdalo mientras lees el código.

## Aviso legal

**DEMO ONLY.** Cada registro que escribe cualquiera de estos programas se marca como dato de demostración en un archivo local desechable o en una base de datos SQLite desechable. Nada de eso se conecta a un sistema real de registro de horas, ni debe usarse jamás con uno. Y por favor **no** pruebes nada de esto en el trabajo. Gasta tus propios tokens. :)

| Versión | Por | La proeza | Te enseña | Carpeta |
| --- | --- | --- | --- | --- |
| **APL** | Jim | Cinco tiradas y un *take-while*: ningún bucle en ninguna parte | Que pensar con arreglos puede reemplazar el flujo de control | [`src/apl`](src/apl/README.md) |
| **APL, más raro** | Jim | Cada tarjeta de horas es una función que copia su propio código fuente con `⎕CR`, lo reescribe y define la copia con `⎕FX`; aplicar compress sobre ese código fuente es la regla de parada | Funciones que se replican a sí mismas en lugar de bucles y `if` | [`src/apl-weird`](src/apl-weird/README.md) |
| **AWK** | Jim | Un `while` en un bloque `BEGIN`, escrito para ejecutarse sin cambios en gawk, mawk, one-true-awk y busybox awk | awk POSIX portable y exactamente dónde discrepan las cuatro implementaciones | [`src/awk`](src/awk/README.md) |
| **AWK, más raro** | Jim | gawk lee `/dev/urandom` con `RS="[0-9]"`, así que cada dígito (`RT`) es una tirada de dado y cada registro una tarjeta; `t > 40 { exit }` es la regla de parada, sin bucle, sin `if` ni llamada aleatoria | Un separador de registros con regex, `RT` y el bucle principal implícito de awk | [`src/awk-weird`](src/awk-weird/README.md) |
| **C# (el original)** | Jim | `for` con cuerpo vacío; todo lo demás vive en sus tres cláusulas | XAML en tiempo de ejecución, LINQ, EF Core, animación de WPF | [`src/ModernChallenge1`](src/ModernChallenge1/README.md) |
| **COBOL** | Ken | `PERFORM DRAW-CARD UNTIL OVER-FORTY`: la regla de parada se declara como dato sobre el total, no se codifica en el procedimiento | Una regla de parada declarada como dato y la imagen (*picture*) de un número que hace tu redondeo | [`src/cobol`](src/cobol/README.md) |
| **COBOL, más raro** | Ken | Sin `IF`, `PERFORM` ni `UNTIL`: `ALTER` recablea un `GO TO` en tiempo de ejecución, y que un campo de dos dígitos se desborde es la regla de parada | Por qué ganó la programación estructurada, a través de un flujo de control que se reescribe a sí mismo | [`src/cobol-weird`](src/cobol-weird/README.md) |
| **ed, weirder** | Jim | GNU `ed` calcula todo el programa: las direcciones de línea ordenan las categorías, una tabla de reescritura convierte los dígitos en filas de marcas, un comando global une cada tarjeta con el total anterior y una expresión regular sobre las marcas es la regla de parada | Reescritura de texto, estado en unario y una sustitución fallida como un `if` | [`src/ed-weird`](src/ed-weird/README.md) |
| **Ex, más raro** | Jim | Un programa de una sola línea se copia en un registro y se ejecuta con `@`. Las marcas del editor hacen la aritmética y una cinta de líneas numeradas guarda la regla de parada. Funciona en nvi y Vim | Código como texto, estado fuera del texto y dónde difieren nvi y Vim | [`src/ex-weird`](src/ex-weird/README.md) |
| **Forth** | Jim | Una sola `begin ... until`, y `outfile-execute` dirige la salida a SQLite | Un lenguaje de pila como programa completo | [`src/forth`](src/forth/README.md) |
| **Forth, aún más raro** | Jim | Ninguna palabra de control de flujo y ninguna variable: el estado viaja en la pila de datos mientras el bucle mueve hacia atrás el propio `>in` del intérprete de texto | La posición de análisis como contador de programa | [`src/forth-weird`](src/forth-weird/README.md) |
| **Go** | Ken | El mismo reto, pero sirviendo una página pulsante en tu navegador | El mismo truco, como un servidor web de una sola petición | [`src/GoChallenge1`](src/GoChallenge1/README.md) |
| **GNU tar** | Jim | El programa es un archivo tar: los miembros son instrucciones, tar las recorre y el `--to-command` del operador les da significado. Un inspector pasivo lee el mismo archivo y no ejecuta nada | Serialización frente a ejecución, límites de confianza y un intérprete que falla en modo cerrado | [`src/tar-gnu`](src/tar-gnu/README.md) |
| **GNU tar, más raro** | Jim | Los puntos de control de tar son el reloj: un registro escrito equivale a una hora, y una máquina de estados avanza un paso por tic. La estructura del archivo marca el ritmo | Relojes lógicos, control dirigido por eventos y conteos que dependen de la implementación | [`src/tar-gnu-weird`](src/tar-gnu-weird/README.md) |
| **Haskell** | Jim | Una función pura: horas aleatorias, `scanl1`, `span` | Una lista perezosa y un solo `span` como toda la regla de parada | [`src/haskell`](src/haskell/README.md) |
| **Haskell, más raro** | Jim | Una lista infinita de tarjetas cuyos elementos tienen efectos secundarios: cada total acumulado se lee de la tarjeta anterior, y forzar una celda escribe su fila | E/S perezosa (*lazy IO*) como flujo de control, con el nudo atado mediante `fix` y `fixIO` | [`src/haskell-weird`](src/haskell-weird/README.md) |
| **Java** | Ken | Un solo `for` sin cuerpo; una clase anónima guarda el estado del bucle | El mismo truco del bucle sin cuerpo, al estilo de Java | [`src/JavaChallenge1`](src/JavaChallenge1/README.md) |
| **JavaScript** | Jim | El `for` sin cuerpo del original, en Node.js: un objeto para el estado, `node:sqlite` y un temporizador que hace pulsar la línea DEMO ONLY en una terminal | Las cláusulas `for`, el operador coma y el bucle de eventos | [`src/javascript`](src/javascript/README.md) |
| **JavaScript, más raro** | Jim | Sin sentencia de bucle. Tres clausuras (*closures*: funciones que conservan las variables del lugar donde se crearon) hacen las tarjetas y una canalización de iteradores las demanda una por una. `reduce` suma la lista terminada, porque no puede detenerse antes de tiempo | Clausuras, iteración perezosa y por qué `reduce` no puede detenerse | [`src/javascript-weird`](src/javascript-weird/README.md) |
| **JavaScript, dirigido por eventos** | Jim | Sin sentencia de bucle y sin canalización. Diez escuchadores de eventos en un mismo `EventEmitter` forman todo el programa, y cada uno emite el evento que espera el siguiente. `setImmediate` da un turno al bucle de eventos entre tarjetas, así que la pila de llamadas nunca crece | Eventos, funciones de devolución de llamada (*callbacks*: funciones que pasas a otro código para que las llame después), el bucle de eventos y por qué un `emit()` síncrono no es asíncrono | [`src/javascript-events`](src/javascript-events/README.md) |
| **Kotlin** | Ken | El mismo reto, construido como una secuencia | El mismo truco, con los constructores de secuencias de Kotlin | [`src/KotlinChallenge1`](src/KotlinChallenge1/README.md) |
| **LINQ, cadena fluida** | Jim | Una sola cadena de métodos LINQ es todo el programa | Cadenas de métodos LINQ, de principio a fin | [`src/LinqChallenge1`](src/LinqChallenge1/README.md) |
| **LINQ, expresión de consulta** | Jim | Casi todas las líneas son `from`/`where`/`let`/`select` | Sintaxis de consulta de C#, llevada hasta donde da de sí | [`src/LinqChallenge2`](src/LinqChallenge2/README.md) |
| **Lisp** | Jim | Una sola forma `LOOP` que suma, recopila y se detiene, en Common Lisp | El orden de las cláusulas de `LOOP`, los structs y la aritmética de semanas ISO escrita a mano | [`src/lisp`](src/lisp/README.md) |
| **Lisp, más raro** | Jim | Cada tarjeta es un método de CLOS encadenado a través de una jerarquía de clases; la combinación de métodos integrada `or` se detiene en el primer resultado verdadero | La combinación de métodos como flujo de control | [`src/lisp-weird`](src/lisp-weird/README.md) |
| **m4** | Jim | Una macro cuya última palabra es ella misma: m4 vuelve a examinar su propia salida, y un generador Park-Miller se construye con `eval` de 32 bits | El entrecomillado como evaluación perezosa, en un lenguaje que es solo texto | [`src/m4`](src/m4/README.md) |
| **find, POSIX** | Jim | Un `find` con cuatro primarios y sin variables: el recorrido excava el árbol de directorios que recorre, y la ruta y los nombres son los contadores | Un recorrido de árbol como bucle, patrones de ruta como tablas de consulta y lo que POSIX deja sin especificar | [`src/find-posix`](src/find-posix/README.md) |
| **find, GNU** | Jim | El mismo recorrido que excava, con todos los extras de GNU: `%d` (profundidad) es el total acumulado, `%T` es la semana ISO, `-regex` es la regla de parada, `-fprintf` escribe el SQL en el fd 3 y `-D rates` es find perfilando el programa | Lo que reemplazan los extras de GNU find y un optimizador que no tiene nada que reordenar | [`src/find-gnu`](src/find-gnu/README.md) |
| **Make, CMake** | Jim | Un solo `while()` sin cuerpo; su condición es una máquina de expresiones regulares | `while()` + expresiones regulares como una pequeña máquina de registros | [`src/cmake`](src/cmake/README.md) |
| **Make, GNU** | Jim | Sin `$(shell)`; Make se vuelve a ejecutar a sí mismo como el bucle | Aritmética y bucles con sintaxis Make simple | [`src/make-gnu`](src/make-gnu/README.md) |
| **Python** | Ken | El mismo reto, al estilo de Python | El mismo truco, en un lenguaje sin bucles `;` | [`src/PythonChallenge1`](src/PythonChallenge1/README.md) |
| **RegEx, .NET** | Jim | Solo grupos de equilibrio: sin callouts y sin código en el patrón | Una regex como contador basado en una pila | [`src/regex-dotnet`](src/regex-dotnet/README.md) |
| **RegEx, GNU sed** | Ken | El programa es una línea de texto que se reescribe hasta terminar | Sustituciones de sed como algoritmo de Markov | [`src/regex-sed`](src/regex-sed/README.md) |
| **RegEx, PCRE2** | Jim | Las cadenas de texto de los callouts se convierten en códigos de operación para un despachador de C sin cuerpo | Los callouts de regex como un conjunto mínimo de instrucciones | [`src/regex-pcre2`](src/regex-pcre2/README.md) |
| **RegEx, pcre2grep** | Jim | Sin código personalizado: un `pcre2grep` estándar y una sola línea de comandos | Códigos de salida de programas como flujo de control | [`src/regex-pcre2grep`](src/regex-pcre2grep/README.md) |
| **RegEx, Perl** | Jim | Una sola coincidencia de `=~` lo hace todo y luego devuelve false a propósito | Código ejecutable dentro de una coincidencia de regex en curso | [`src/regex-perl`](src/regex-perl/README.md) |
| **Rust** | Jim | Sin `;`, `let` ni `return` en `main` — una prueba lo exige | Iteradores y clausuras (*closures*: funciones anónimas que capturan variables de su entorno) como flujo de control | [`src/RustChallenge1`](src/RustChallenge1/README.md) |
| **Tcl** | Jim | Un bucle `while` sobre diccionarios, parámetros SQL enlazados directamente desde variables de Tcl y una ventana opcional de Tk que se prueba sin interfaz gráfica | Tcl idiomático: llaves, diccionarios, enlaces con `db eval` y Tk | [`src/tcl`](src/tcl/README.md) |
| **Tcl, más raro** | Jim | El programa es texto en una tabla de SQLite, que obtiene un `unknown` redefinido; un disparador recursivo es el bucle y `INSERT ... WHERE` es la regla de parada | El código como datos y un disparador de base de datos como flujo de control | [`src/tcl-weird`](src/tcl-weird/README.md) |
| **XAML** | Jim | El programa *es* un archivo `.xaml`, ejecutado por el analizador sintáctico que lo carga | XAML como intérprete en tiempo de ejecución, no solo como marcado | [`src/xaml`](src/xaml/README.md) |

Cada celda de "Te enseña" de arriba es una promesa, no solo una etiqueta: abre el README de la carpeta y eso es justo lo que vas a entender al terminar. Para ver el mismo material organizado por [lenguaje](lessons/lenguajes/README.md) y por [mecanismo](lessons/patrones.md), con ejercicios, consulta [Aprende a programar como un bicho raro](lessons/README.md).

## Estructura del repositorio

```text
RETO.md                  # the rules - start here if you want to play
CONTRIBUTING.md               # how to send in an entry, and how it gets reviewed
SANDBOX-SETUP.md              # how to install Docker / Windows Sandbox to run entries safely
lessons/                      # Learn Programming the Weird Way!: lessons, patterns, blockers, exercises
sandbox/                      # where entries get run safely: Docker images, Windows Sandbox, the Actions gate
build.gradle, gradlew*        # root Gradle wrapper: runs the Java, Kotlin, Python, and Go ports
docs/
  curriculum.md               # the 16-week course plan (builds curriculum.pdf and .epub in the root)
  My Code Challenge.pdf       # anonymized source presentation
  stacked-bar-charts.md       # the 2013 no-code-behind blog post that inspired the XAML entry
  images/                     # screenshots used in the subfolder READMEs
src/
  ModernChallenge1/           # C#: the original, modernized for .NET 10
  RustChallenge1/             # Rust + GTK 4 companion for WSL
  xaml/                       # XAML: the program is a .xaml file, run at run time
  regex-perl/                 # Perl: one executable-regex match is the program
  regex-pcre2/                # PCRE2: callout strings as opcodes, a C dispatcher
  regex-pcre2grep/            # pcre2grep: callouts run sqlite3, exit codes steer the match
  regex-dotnet/               # .NET: balancing groups only, and the walls it hits
  regex-sed/                  # GNU sed (Ken): the program is one line of text, rewritten by substitutions
  cobol/                      # COBOL (Ken): PERFORM ... UNTIL, with the stop rule declared as data
  cobol-weird/                # COBOL (Ken): no IF or PERFORM; ALTER rewires a GO TO and an overflow stops it
  LinqChallenge1/             # LINQ: one fluent method-chain expression statement
  LinqChallenge2/             # LINQ: one SQL-like query-expression statement
  make-gnu/                   # GNU Make: no $(shell); Make re-executes itself as the loop
  find-posix/                 # POSIX find: one find; the walk digs the tree it walks, names are counters
  find-gnu/                   # GNU find: the same walk, with %d, %T, -regex, -fprintf and -D rates
  cmake/                      # CMake: one bodiless while(), a regex machine in its condition
  apl/                        # APL: five rolls and one take-while
  apl-weird/                  # APL: functions that copy themselves with ⎕CR and ⎕FX
  haskell/                    # Haskell: one pure function, scanl1 and span
  haskell-weird/              # Haskell: an infinite list of cards whose elements write their own rows
  ed-weird/                   # ed: the buffer is the machine; a failed substitution is the if
  ex-weird/                   # Ex: a register that runs itself; marks are registers (nvi and Vim)
  tar-gnu/                    # GNU tar: the archive is a serialized program; tar --to-command runs it
  tar-gnu-weird/              # GNU tar: checkpoints are the clock of a state machine
  javascript/                 # JavaScript (Node.js): the original's bodiless for
  javascript-weird/           # JavaScript (Node.js): closures and a lazy iterator, no loop statement
  javascript-events/          # JavaScript (Node.js): ten listeners on an EventEmitter, no loop statement
  forth/                      # Forth: one begin ... until and a pipe to SQLite
  forth-weird/                # Forth: no control-flow words; the loop rewinds >in
  lisp/                       # Common Lisp: one LOOP form
  lisp-weird/                 # Common Lisp: a class hierarchy is the loop; the or method combination stops it
  m4/                         # m4: a macro that expands itself until ifelse says stop
  tcl/                        # Tcl: a while loop, dicts, bound SQL parameters, optional Tk window
  tcl-weird/                  # Tcl: the program lives in SQLite; a recursive trigger is the loop
  awk/                        # AWK: portable POSIX awk, one while in BEGIN
  awk-weird/                  # AWK (gawk): RS="[0-9]" over /dev/urandom; each digit is a die roll
  JavaChallenge1/             # Java (Ken): the same bodiless-loop trick, Java style
  KotlinChallenge1/           # Kotlin (Ken): the same challenge, built as a sequence
  PythonChallenge1/           # Python (Ken): the same challenge, Python style
  GoChallenge1/               # Go (Ken): the same challenge, serving a pulsing page in your browser
LICENSE
```

Las adaptaciones de Ken en COBOL, Java, Kotlin, Python y Go también viven aquí, integradas con todo el crédito intacto en el README de cada una.

¿Listo para explorar cualquiera de ellos como lección? Empieza en [Aprende a programar como un bicho raro](lessons/README.md).
