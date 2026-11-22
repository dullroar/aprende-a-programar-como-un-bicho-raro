# Por objetivo

Tres objetivos sostienen todo en [¡Aprende a programar como un bicho raro!](README.md). Cada uno responde de otra forma a la pregunta "¿por qué alguien haría esto?"

## Enseña computación, no solo trucos computacionales

Un truco es "esta fórmula mágica hace que el bucle se detenga". La computación es "esta es la máquina que se ejecuta y aquí vive su estado".

Cada entrada rara te obliga a nombrar la máquina que se esconde dentro de un lenguaje. Cuando puedes nombrarla, el truco es solo un programa para esa máquina.

<!-- BEGIN GENERATED machines -->
| Lenguaje o herramienta | La máquina que es en realidad | Dónde vive el estado del programa | Lección |
| --- | --- | --- | --- |
| APL | Ordinario: una máquina de arreglos que saca cinco tarjetas a la vez y decide después | Arreglos y nada oculto | [apl](lenguajes/apl.md) |
| APL | Una máquina de arreglos, con código que también es un arreglo | Arreglos y el texto fuente de las funciones | [apl](lenguajes/apl.md#funciones-que-se-modifican-a-sí-mismas-apl-weird) |
| AWK | Ordinario: un bucle `while` en `BEGIN`, con una tubería a sqlite3 como salida | Arreglos y variables locales de parámetro | [awk](lenguajes/awk.md) |
| AWK | Un bucle que procesa registros y que puedes dirigir a cualquier flujo de bytes | El flujo de entrada de datos y el separador de registros `RS` | [awk](lenguajes/awk.md#registros-a-partir-de-un-flujo-de-bytes-aleatorios-awk-weird) |
| C# `for` | Tres espacios para expresiones | Campos de un objeto anónimo | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#el-original-modernchallenge1) |
| CMake | Una máquina de registros | `CMAKE_MATCH_1`..`5`, reconstruido en cada pasada | [make-cmake](lenguajes/make-cmake.md#cmake) |
| COBOL | Ordinario: un bucle estructurado `PERFORM ... UNTIL` que pide a los datos la regla de parada | `WS-TOTAL` y su nombre de nivel 88 `OVER-FORTY` | [cobol](lenguajes/cobol.md) |
| COBOL | Un programa cuyos destinos de salto son mutables | El destino de un `GO TO` | [cobol](lenguajes/cobol.md#alter) |
| Common Lisp | Ordinario: un `LOOP` que, en cada pasada, ejecuta sus cláusulas en orden | Variables que posee `LOOP`, como `total` | [lisp](lenguajes/lisp.md) |
| Common Lisp | Un despachador de métodos con una regla de combinación intercambiable | La lista de precedencia de clases y el valor de retorno de cada método | [lisp](lenguajes/lisp.md#combinación-de-métodos-como-flujo-de-control) |
| ed | Una máquina que reescribe cadenas de texto con direcciones de línea | El búfer del editor: una línea por tarjeta y marcas (x) que se añaden al unir líneas | [editores](lenguajes/editores.md#el-búfer-es-la-máquina) |
| Ex | Una máquina de registros cuyos registros son marcas del editor y cuyo programa es un registro que se ejecuta a sí mismo | Las marcas (dónde estamos en una cinta de líneas numeradas), la primera línea del búfer (la siguiente tarjeta) y los registros a, d y n | [editores](lenguajes/editores.md#un-programa-que-puedes-editar) |
| Forth | Ordinario: una máquina de pila con un solo bucle `begin ... until` | Las variables `total` y `cards` junto con la pila de datos | [forth](lenguajes/forth.md) |
| Forth | Una máquina de pila con un puntero de instrucción móvil | La pila de datos y la posición de análisis `>in` | [forth](lenguajes/forth.md) |
| GNU find | Un recorrido de árbol que hace crecer el árbol que recorre y en el que find mismo lee la profundidad y el reloj | El camino desde el directorio de inicio hasta el directorio que se visita; su profundidad es el total acumulado | [find](lenguajes/find.md) |
| GNU Make | Un grafo de dependencias que puede reiniciarse solo | Qué archivos `.tc-N.mk` existen y `MAKE_RESTARTS` | [make-cmake](lenguajes/make-cmake.md#gnu-make) |
| GNU sed | Un sistema de reescritura de cadenas de texto (un algoritmo de Markov) | Una línea de texto, reescrita hasta que ninguna regla se aplique | [regex](lenguajes/regex.md#gnu-sed) |
| GNU tar | Un lector de cinta (tar) que alimenta a un intérprete de cinco palabras | Los miembros del archivo, que son el programa, más una fila de SQLite que indica si la ejecución se detuvo o falló | [tar](lenguajes/tar.md#un-programa-que-es-un-archivo) |
| GNU tar | Una máquina de estados finitos que avanza con un reloj lógico de tar | Una fila de SQLite (los registros de la máquina) y el número de registros que tar ha escrito | [tar](lenguajes/tar.md#el-archivo-es-el-reloj) |
| Go | Tres posiciones de expresión, con funciones auxiliares en ellas | Campos de una estructura anónima | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| Haskell | Ordinario: una lista perezosa que un solo `span` lee hasta que la prueba falla | Las partes sin evaluar de las listas, leídas bajo demanda | [haskell](lenguajes/haskell.md) |
| Haskell | Un reductor de grafos perezoso | Thunks: qué partes de una lista se han demandado | [haskell](lenguajes/haskell.md#la-es-perezosa-como-flujo-de-control) |
| Java | Tres posiciones de expresión | Campos de una clase anónima | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| JavaScript | Tres espacios para expresiones | Propiedades de un objeto literal | [javascript](lenguajes/javascript.md#el-for-sin-cuerpo-en-node) |
| JavaScript | Un conjunto de escuchadores de eventos en un solo EventEmitter, que juntos son una máquina de estados | El total acumulado y el número de tarjetas, guardados en un objeto que solo tocan los escuchadores de eventos | [javascript](lenguajes/javascript.md#escuchadores-de-eventos-hasta-el-fondo) |
| JavaScript | Una máquina de estados basada en una clausura, avanzada por un iterador perezoso | Variables capturadas por clausuras: el número del generador; de la máquina, la cantidad de tarjetas, el total y la bandera de parada | [javascript](lenguajes/javascript.md#clausuras-hasta-el-fondo) |
| Kotlin | Una secuencia perezosa de la que el `for` vacío demanda (pull) un valor a la vez | Propiedades de una expresión de objeto, la semilla de la secuencia | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| LINQ | Una cadena perezosa de etapas de LINQ que un único `Aggregate` final demanda | Dentro de los enumeradores de las etapas y en la base de datos | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#la-ejecución-diferida-y-el-truco-de-convertir-void-en-valor) |
| LINQ | Una consulta perezosa cuyo `Single()` final demanda su evaluación | Una suma acumulada hasta el día actual recalculada en cada `where`, y la base de datos; sin variable acumuladora | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#la-ejecución-diferida-y-el-truco-de-convertir-void-en-valor) |
| m4 | Una máquina que reescanea texto | El flujo de entrada de datos: todo el texto de macros sin leer | [m4](lenguajes/m4.md#un-bucle-hecho-de-reescaneo) |
| PCRE2 | Una búsqueda con retroceso y ganchos | Una struct de C que nunca retrocede | [regex](lenguajes/regex.md#pcre2-los-callouts-como-conjunto-de-instrucciones) |
| pcre2grep | Una búsqueda con retroceso que ejecuta un programa por cada callout | Filas de SQLite y el código de salida de cada callout | [regex](lenguajes/regex.md#pcre2grep-códigos-de-salida-como-flujo-de-control) |
| Perl | Una búsqueda con retroceso y ganchos | Variables `local` que se deshacen (los efectos no) | [regex](lenguajes/regex.md#perl-código-dentro-de-la-coincidencia) |
| POSIX find | Un recorrido de árbol que hace crecer el árbol que recorre | La ruta desde el directorio de inicio hasta el directorio que se visita | [find](lenguajes/find.md) |
| Python | Una función que `iter` llama hasta que devuelve el valor centinela `False` | Atributos de un objeto de estado que se pasa a la lambda | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| Regex de .NET | Un contador construido con una pila | Pilas de captura con grupos de equilibrio | [regex](lenguajes/regex.md#net-grupos-de-equilibrio) |
| Rust | Una cadena de valores desde `successors`, que se detiene en `None` | Un nuevo `DemoBatch` inmutable en cada paso; nada se muta | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#las-adaptaciones-de-una-sola-sentencia-mismo-truco-distinta-maquinaria) |
| Tcl | Convencional: un bucle `while` que primero sortea y después guarda | Diccionarios y variables Tcl que se guardan en un solo `db transaction` | [tcl](lenguajes/tcl.md) |
| Tcl | Un intérprete de comandos en forma de cadenas de texto que permite interceptar la búsqueda de comandos | Una tabla TEMP con el código fuente de los procedimientos y la profundidad de la recursión de los disparadores | [tcl](lenguajes/tcl.md#sqlite-como-programa) |
| XAML | Un constructor de grafos de objetos que ejecuta métodos durante el análisis sintáctico | El orden del documento y los arreglos "portadores" | [csharp-linq-xaml](lenguajes/csharp-linq-xaml.md#xaml) |
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
