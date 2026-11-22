<!-- GENERADO por lessons/book/build.py a partir de lessons/cs-source/ y del frontmatter de las entradas. No lo edites; edita las fuentes y ejecuta build.py. -->

# Casos de estudio comparativos

Para una lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre diseño comparativo de máquinas](../guias-de-estudio/conceptos/diseno-comparativo-de-maquinas.md).

El [reto compartido](../introduccion.md#what-the-challenge-does) pide tarjetas ficticias hasta incluir la primera tarjeta con la que el total pasa de 40. También pide un registro local de esas tarjetas y un resultado que el lector pueda ver. Algunas entradas imprimen en una terminal. Otras abren una ventana. Consulta [en qué se distinguen las entradas](../introduccion.md#where-entries-differ) para ver los datos fijos de LINQ, el techo de cuatro pasadas de XAML y las variantes de persistencia. Cada sección pregunta qué cumple un **papel** en particular, desde lo que se repite.

Las tablas se generan a partir de los metadatos al inicio del README de cada entrada. Puedes comprobar la clasificación en el README y en el código fuente ejecutable. La evaluación describe qué impulsa el cómputo principal. Por ejemplo, en el `for` de C#, `Sum()` consume de inmediato una proyección diferida de LINQ incluida en el bucle cada vez que se comprueba la condición. La tabla final presenta una lista de todas las entradas con su tipo, su estrategia de evaluación y el grado de garantía más débil que requieren.

## Un bucle ordinario, usado en un lugar inusual

El bucle sigue siendo un bucle. Lo que cambia es *dónde* ocurre el trabajo. En las entradas de C#, Java y Go el bucle tiene un cuerpo vacío, y las tres cláusulas del encabezado `for` lo hacen todo. En [`cmake`](../../src/cmake/README.md), una condición `while()` ejecuta una regex y sus capturas son los registros. En [`cobol`](../../src/cobol/README.md), la condición es un hecho con nombre sobre los datos (`OVER-FORTY`) y `PERFORM ... UNTIL` repite hasta que se cumple. Forth, Lisp y Tcl usan sus palabras de bucle habituales. Léelas junto a las demás: muestran qué permanece igual cuando el bucle es honesto. [`javascript`](../../src/javascript/README.md) es el `for` sin cuerpo del original en Node.js: tres cláusulas, un literal de objeto para el estado y un temporizador para la animación.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`ModernChallenge1`](../../src/ModernChallenge1/README.md) | C# | Tres espacios para expresiones | Campos de un objeto anónimo | eager | garantizado |
| [`cmake`](../../src/cmake/README.md) | CMake | Una máquina de registros | `CMAKE_MATCH_1`..`5`, reconstruido en cada pasada | eager | aprovechado por accidente |
| [`cobol`](../../src/cobol/README.md) | COBOL | Ordinario: un bucle estructurado `PERFORM ... UNTIL` que pide a los datos la regla de parada | `WS-TOTAL` y su nombre de nivel 88 `OVER-FORTY` | eager | garantizado |
| [`lisp`](../../src/lisp/README.md) | Common Lisp | Ordinario: un `LOOP` que, en cada pasada, ejecuta sus cláusulas en orden | Variables que posee `LOOP`, como `total` | eager | garantizado |
| [`forth`](../../src/forth/README.md) | Forth | Ordinario: una máquina de pila con un solo bucle `begin ... until` | Las variables `total` y `cards` junto con la pila de datos | eager | garantizado |
| [`GoChallenge1`](../../src/GoChallenge1/README.md) | Go | Tres posiciones de expresión, con funciones auxiliares en ellas | Campos de una estructura anónima | eager | garantizado |
| [`JavaChallenge1`](../../src/JavaChallenge1/README.md) | Java | Tres posiciones de expresión | Campos de una clase anónima | eager | garantizado |
| [`javascript`](../../src/javascript/README.md) | JavaScript, SQLite | Tres espacios para expresiones | Propiedades de un objeto literal | eager | garantizado |
| [`tcl`](../../src/tcl/README.md) | Tcl | Convencional: un bucle `while` que primero sortea y después guarda | Diccionarios y variables Tcl que se guardan en un solo `db transaction` | eager | permitido por la implementación |

## Una secuencia perezosa que alguien sigue pidiendo

No hay bucle. Hay una secuencia que alguien sigue pidiendo, y el programa se detiene cuando se deja de pedir. [`haskell`](../../src/haskell/README.md) describe las tarjetas como una lista perezosa infinita y toma un prefijo con `span`. [`haskell-weird`](../../src/haskell-weird/README.md) pone los efectos dentro de la lista, así que leerla hace el trabajo. LINQ construye una canalización diferida que un operador final voraz fuerza. `generateSequence` de Kotlin, `successors` de Rust y `iter(step, False)` de Python dan una forma parecida en otros lenguajes. La diferencia entre las entradas es *quién fuerza la secuencia* y *cuándo*. [`javascript-weird`](../../src/javascript-weird/README.md) no tiene sentencia de bucle: tres clausuras (*closures*) fabrican tarjetas, y una canalización de iteradores demanda una tarjeta a la vez hasta que la máquina dice que terminó.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`haskell`](../../src/haskell/README.md) | Haskell | Ordinario: una lista perezosa que un solo `span` lee hasta que la prueba falla | Las partes sin evaluar de las listas, leídas bajo demanda | lazy | garantizado |
| [`haskell-weird`](../../src/haskell-weird/README.md) | Haskell | Un reductor de grafos perezoso | Thunks: qué partes de una lista se han demandado | lazy | permitido por la implementación |
| [`javascript-weird`](../../src/javascript-weird/README.md) | JavaScript, SQLite | Una máquina de estados basada en una clausura, avanzada por un iterador perezoso | Variables capturadas por clausuras: el número del generador; de la máquina, la cantidad de tarjetas, el total y la bandera de parada | lazy | garantizado |
| [`KotlinChallenge1`](../../src/KotlinChallenge1/README.md) | Kotlin | Una secuencia perezosa de la que el `for` vacío demanda (pull) un valor a la vez | Propiedades de una expresión de objeto, la semilla de la secuencia | lazy | garantizado |
| [`LinqChallenge1`](../../src/LinqChallenge1/README.md) | C#, LINQ | Una cadena perezosa de etapas de LINQ que un único `Aggregate` final demanda | Dentro de los enumeradores de las etapas y en la base de datos | deferred | garantizado |
| [`LinqChallenge2`](../../src/LinqChallenge2/README.md) | C#, LINQ | Una consulta perezosa cuyo `Single()` final demanda su evaluación | Una suma acumulada hasta el día actual recalculada en cada `where`, y la base de datos; sin variable acumuladora | deferred | garantizado |
| [`PythonChallenge1`](../../src/PythonChallenge1/README.md) | Python | Una función que `iter` llama hasta que devuelve el valor centinela `False` | Atributos de un objeto de estado que se pasa a la lambda | lazy | garantizado |
| [`RustChallenge1`](../../src/RustChallenge1/README.md) | Rust | Una cadena de valores desde `successors`, que se detiene en `None` | Un nuevo `DemoBatch` inmutable en cada paso; nada se muta | lazy | garantizado |

## Operaciones sobre arreglos completos en lugar de pasos

Hazlo con todos a la vez y luego corta. [`apl`](../../src/apl/README.md) genera cinco valores aleatorios (una cota que nunca puede quedarse corta), calcula una suma acumulada y conserva el prefijo cuyo total no pasa de 40, más la tarjeta que sí pasa. No hay bucle ni contador. El costo es que el programa calcula más de lo necesario y el lector tiene que pensar en arreglos.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`apl`](../../src/apl/README.md) | APL | Ordinario: una máquina de arreglos que saca cinco tarjetas a la vez y decide después | Arreglos y nada oculto | eager | permitido por la implementación |

## Texto que se reescribe y se vuelve a leer

El programa es texto y repetir es reescribirlo. [`regex-sed`](../../src/regex-sed/README.md) conserva una línea de texto y aplica sustituciones hasta que ninguna coincide. [`m4`](../../src/m4/README.md) define una macro cuyo texto de reemplazo contiene la propia macro, así que la salida se escanea otra vez, y otra. [`make-gnu`](../../src/make-gnu/README.md) rehace un makefile que incluye, y luego *empieza de nuevo* con el nuevo. En los tres, lo que se repite es la lectura de una entrada reescrita, y el estado es lo que diga ahora el texto (o el conjunto de archivos). [`ed-weird`](../../src/ed-weird/README.md) reescribe líneas con sustituciones protegidas, y une líneas para que las marcas se añadan una junto a otra. No tiene una rama al estilo de `sed`: su única repetición es un comando global.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`ed-weird`](../../src/ed-weird/README.md) | ed, SQLite | Una máquina que reescribe cadenas de texto con direcciones de línea | El búfer del editor: una línea por tarjeta y marcas (x) que se añaden al unir líneas | rewriting | aprovechado por accidente |
| [`make-gnu`](../../src/make-gnu/README.md) | GNU Make | Un grafo de dependencias que puede reiniciarse solo | Qué archivos `.tc-N.mk` existen y `MAKE_RESTARTS` | declarative | aprovechado por accidente |
| [`regex-sed`](../../src/regex-sed/README.md) | GNU sed, Regular expressions | Un sistema de reescritura de cadenas de texto (un algoritmo de Markov) | Una línea de texto, reescrita hasta que ninguna regla se aplique | rewriting | aprovechado por accidente |
| [`m4`](../../src/m4/README.md) | m4 | Una máquina que reescanea texto | El flujo de entrada de datos: todo el texto de macros sin leer | rewriting | permitido por la implementación |

## Flujo de control que se reescribe a sí mismo

El programa cambia adónde va a continuación. [`cobol-weird`](../../src/cobol-weird/README.md) usa `ALTER` para recablear un `GO TO`. [`forth-weird`](../../src/forth-weird/README.md) mueve `>in`, la posición de análisis del intérprete de texto, hacia atrás para ejecutar de nuevo las mismas palabras. [`apl-weird`](../../src/apl-weird/README.md) lee su propio código fuente con `⎕CR`, lo reescribe y define la función nueva con `⎕FX`: cada paso fabrica a su sucesor. Este es el papel más peligroso del libro. También es la imagen más clara de lo que de verdad es un contador de programa. [`ex-weird`](../../src/ex-weird/README.md) copia una línea de datos de una cinta a un registro y la ejecuta. En la cinta, la instrucción es `@a` (ejecuta el programa otra vez) o un comentario (detente), así que el programa lee su siguiente paso en los datos.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`apl-weird`](../../src/apl-weird/README.md) | APL | Una máquina de arreglos, con código que también es un arreglo | Arreglos y el texto fuente de las funciones | eager | permitido por la implementación |
| [`cobol-weird`](../../src/cobol-weird/README.md) | COBOL | Un programa cuyos destinos de salto son mutables | El destino de un `GO TO` | eager | permitido por la implementación |
| [`ex-weird`](../../src/ex-weird/README.md) | Ex, SQLite | Una máquina de registros cuyos registros son marcas del editor y cuyo programa es un registro que se ejecuta a sí mismo | Las marcas (dónde estamos en una cinta de líneas numeradas), la primera línea del búfer (la siguiente tarjeta) y los registros a, d y n | eager | permitido por la implementación |
| [`forth-weird`](../../src/forth-weird/README.md) | Forth | Una máquina de pila con un puntero de instrucción móvil | La pila de datos y la posición de análisis `>in` | eager | permitido por la implementación |
| [`find-gnu`](../../src/find-gnu/README.md) | find, SQLite | Un recorrido de árbol que hace crecer el árbol que recorre y en el que find mismo lee la profundidad y el reloj | El camino desde el directorio de inicio hasta el directorio que se visita; su profundidad es el total acumulado | declarative | aprovechado por accidente |
| [`find-posix`](../../src/find-posix/README.md) | find, SQLite | Un recorrido de árbol que hace crecer el árbol que recorre | La ruta desde el directorio de inicio hasta el directorio que se visita | declarative | aprovechado por accidente |

## Búsqueda con regex, efectos secundarios y fallo deliberado

[`regex-perl`](../../src/regex-perl/README.md), [`regex-pcre2`](../../src/regex-pcre2/README.md) y [`regex-pcre2grep`](../../src/regex-pcre2grep/README.md) usan una sola coincidencia para activar funciones de devolución de llamada (*callbacks*) o código incrustado. Las acciones construyen el resultado fuera del motor de coincidencias. Cada patrón acaba forzando que la coincidencia falle, y las escrituras ya hechas pueden sobrevivir a ese fallo. Las variables locales de Perl se deshacen con el retroceso, mientras que los callouts de PCRE2 guardan su estado en el anfitrión de C o en ayudantes externos.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`regex-pcre2`](../../src/regex-pcre2/README.md) | C, PCRE2, Regular expressions | Una búsqueda con retroceso y ganchos | Una struct de C que nunca retrocede | search | permitido por la implementación |
| [`regex-pcre2grep`](../../src/regex-pcre2grep/README.md) | PCRE2, Regular expressions | Una búsqueda con retroceso que ejecuta un programa por cada callout | Filas de SQLite y el código de salida de cada callout | search | permitido por la implementación |
| [`regex-perl`](../../src/regex-perl/README.md) | Perl, Regular expressions | Una búsqueda con retroceso y ganchos | Variables `local` que se deshacen (los efectos no) | search | permitido por la implementación |

## Búsqueda con regex que devuelve capturas

[`regex-dotnet`](../../src/regex-dotnet/README.md) gasta fichas de una pila de capturas mientras reconoce horas en unario. Un presupuesto vacío impide empezar otra tarjeta, así que la coincidencia puede tener éxito con el prefijo que incluye la tarjeta que cruza el límite. El anfitrión lee las capturas de esa coincidencia para construir un informe TSV. Una coincidencia fallida no expone capturas, así que la misma cinta con una aserción de fallo al final produce cero tarjetas.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`regex-dotnet`](../../src/regex-dotnet/README.md) | C#, Regular expressions | Un contador construido con una pila | Pilas de captura con grupos de equilibrio | search | garantizado |

## Despacho y disparadores: la regla activa el siguiente paso

La regla activa el siguiente paso. En [`lisp-weird`](../../src/lisp-weird/README.md), una jerarquía de clases es el bucle: cada método llama al siguiente de la lista de precedencia de clases, y la combinación de métodos `or` se detiene en el primer valor verdadero. En [`tcl-weird`](../../src/tcl-weird/README.md), un disparador de SQLite inserta la siguiente tarjeta, lo que vuelve a activar el disparador, y el bucle termina cuando una cláusula `WHERE` no encuentra nada que insertar. En ambos, la repetición es invisible en el código que la inicia. [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) obtiene sus funciones de devolución de llamada (*callbacks*) de GNU tar: cada registro que escribe tar ejecuta una transición de una pequeña máquina de estados, así que el formato del archivo marca el ritmo. [`javascript-events`](../../src/javascript-events/README.md) es el caso más simple: diez escuchadores de eventos sobre un mismo `EventEmitter` son todo el programa, y cada uno emite el evento que espera el siguiente. La siguiente tarjeta se pide con `setImmediate`, así que cada tarjeta es un turno nuevo del bucle de eventos y la pila de llamadas nunca crece.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`lisp-weird`](../../src/lisp-weird/README.md) | Common Lisp | Un despachador de métodos con una regla de combinación intercambiable | La lista de precedencia de clases y el valor de retorno de cada método | eager | permitido por la implementación |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | Una máquina de estados finitos que avanza con un reloj lógico de tar | Una fila de SQLite (los registros de la máquina) y el número de registros que tar ha escrito | eager | permitido por la implementación |
| [`javascript-events`](../../src/javascript-events/README.md) | JavaScript, SQLite | Un conjunto de escuchadores de eventos en un solo EventEmitter, que juntos son una máquina de estados | El total acumulado y el número de tarjetas, guardados en un objeto que solo tocan los escuchadores de eventos | eager | garantizado |
| [`tcl-weird`](../../src/tcl-weird/README.md) | Tcl, SQLite | Un intérprete de comandos en forma de cadenas de texto que permite interceptar la búsqueda de comandos | Una tabla TEMP con el código fuente de los procedimientos y la profundidad de la recursión de los disparadores | eager | permitido por la implementación |

## La entrada de datos es el bucle

La entrada de datos es el bucle. AWK lee un registro a la vez y ejecuta cada regla de patrón y acción sobre él, así que el programa no contiene ningún bucle. [`awk`](../../src/awk/README.md) usa el bucle de la forma habitual. [`awk-weird`](../../src/awk-weird/README.md) fija una expresión regular como separador de registros, así que un flujo de bytes aleatorios se convierte en dados, y un solo patrón (`t > 40 { exit }`) es la regla de parada.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`awk`](../../src/awk/README.md) | AWK | Ordinario: un bucle `while` en `BEGIN`, con una tubería a sqlite3 como salida | Arreglos y variables locales de parámetro | eager | garantizado |
| [`awk-weird`](../../src/awk-weird/README.md) | AWK | Un bucle que procesa registros y que puedes dirigir a cualquier flujo de bytes | El flujo de entrada de datos y el separador de registros `RS` | eager | permitido por la implementación |

## El orden del documento es el programa

El orden del documento es el orden del programa. [`xaml`](../../src/xaml/README.md) no tiene código detrás. El analizador sintáctico de XAML construye objetos en el orden en que los lee, y varios de esos objetos llaman a métodos al crearse. Cuatro pasadas desenrolladas reemplazan el bucle, los arreglos "portadores" son las variables y las expresiones de SQL o de `DataTable` toman las decisiones. El programa es el archivo de marcado, y se ejecuta mientras se analiza el archivo. [`tar-gnu`](../../src/tar-gnu/README.md) es la misma idea con una cinta en lugar de un archivo de marcado: los miembros del archivo tar son las instrucciones, y el orden del archivo es el orden del programa.

**Entradas:**

| Entrada | Lenguaje | La máquina | Dónde vive el estado | Evaluación | Garantía |
| --- | --- | --- | --- | --- | --- |
| [`tar-gnu`](../../src/tar-gnu/README.md) | GNU tar, SQLite | Un lector de cinta (tar) que alimenta a un intérprete de cinco palabras | Los miembros del archivo, que son el programa, más una fila de SQLite que indica si la ejecución se detuvo o falló | eager | permitido por la implementación |
| [`xaml`](../../src/xaml/README.md) | XAML, C# | Un constructor de grafos de objetos que ejecuta métodos durante el análisis sintáctico | El orden del documento y los arreglos "portadores" | declarative | aprovechado por accidente |

## ¿Dónde vive el programa y qué hace que se ejecute el siguiente paso?

Haz estas dos preguntas sobre cualquier entrada y las raras dejarán de parecer iguales. La primera indica dónde se guardan el programa y su estado. La segunda indica qué hace que se ejecute el siguiente paso.

| Entrada | Dónde viven el programa y su estado | Qué lo hace avanzar |
| --- | --- | --- |
| [`xaml`](../../src/xaml/README.md) | Un documento declarativo que se convierte en objetos | El analizador sintáctico: crea los objetos en el orden del documento |
| [`tar-gnu`](../../src/tar-gnu/README.md) | Miembros serializados del archivo y un contrato (`tarprog/1`) que tar desconoce | El recorrido de tar por los miembros y la opción `--to-command` del operador |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | La estructura del archivo y una fila de registros en SQLite | Los eventos de punto de control de GNU tar: un pulso por cada registro escrito |
| [`ed-weird`](../../src/ed-weird/README.md) | El búfer del editor: líneas y filas de marcas | La edición por direcciones: un comando global y sustituciones que solo se aplican cuando hay coincidencia |
| [`ex-weird`](../../src/ex-weird/README.md) | El búfer, las marcas y los registros del editor y una cinta de líneas numeradas | Ex mismo: un registro que se ejecuta a sí mismo, guiado por una línea de datos |
| [`make-gnu`](../../src/make-gnu/README.md) | Los objetivos, las dependencias y el estado del reinicio | La resolución del grafo de compilación y el reinicio |
| [`find-posix`](../../src/find-posix/README.md) y [`find-gnu`](../../src/find-gnu/README.md) | El árbol de directorios, su profundidad y los nombres | El recorrido del árbol |
| [`haskell-weird`](../../src/haskell-weird/README.md) | Valores perezosos que contienen efectos | La demanda: lo que se fuerza se ejecuta |
| [`tcl-weird`](../../src/tcl-weird/README.md) | Filas de SQL que contienen el código fuente almacenado | La búsqueda de un comando desconocido por parte del intérprete y los disparadores |
| [`javascript`](../../src/javascript/README.md) | Propiedades de un objeto literal en un `for` sin cuerpo | La sentencia `for`: inicializador, condición e iterador |
| [`javascript-weird`](../../src/javascript-weird/README.md) | Variables capturadas por clausuras (*closure*, funciones junto con su entorno léxico) | La demanda del consumidor sobre un iterador: cada `next()` ejecuta un paso |
| [`javascript-events`](../../src/javascript-events/README.md) | Un objeto al que solo acceden los escuchadores de eventos de un `EventEmitter` | Un evento y luego el planificador: cada escuchador de eventos emite el siguiente evento y `setImmediate` da un turno al bucle de eventos entre tarjetas |

## Cómo se escribe un programa, se vuelve a leer y se ejecuta

Cuatro acciones distintas se esconden tras las palabras "el programa es datos". La **serialización** escribe algo como bytes. La **deserialización** vuelve a leer los bytes y recupera las piezas. La **interpretación** les da un significado. La **ejecución** le da un efecto a ese significado. Un formato puede detenerse tras cualquiera de esas acciones. Un consumidor puede combinarlas. Para la seguridad importa *qué autoridad le diste a cada consumidor*. Consulta [Serialización, deserialización y pickling de objetos](06-estado-mas-alla-de-las-variables.md#serialización-deserialización-y-pickling-de-objetos).

| Entrada | Serialización | Deserialización | Interpretación y ejecución | Qué promete al escribir y volver a leer |
| --- | --- | --- | --- | --- |
| [`tar-gnu`](../../src/tar-gnu/README.md) | Un generador escribe los miembros de un archivo en un orden fijo a partir de una semilla | Tar analiza la sintaxis de los miembros. Un inspector pasivo hace lo mismo sin ejecutar nada | Un despachador da significado a cuatro tipos de registros y solo los ejecuta si el operador pasa `--to-command` | La misma semilla da los mismos bytes (comprobado con `cmp`). El inspector y la base de datos coinciden en cada tarjeta. Un archivo en dos bases de datos nuevas da las mismas tarjetas. **No** promete reanudar una ejecución detenida |
| [`xaml`](../../src/xaml/README.md) | Un archivo `.xaml` es un grafo de objetos escrito como marcado | `XamlReader.Load` hace el análisis sintáctico | La misma llamada lo ejecuta: se invocan métodos a medida que se crean los objetos | Ninguna. El análisis sintáctico *es* la ejecución y la entrada nunca vuelve a escribir el documento |
| [`tcl-weird`](../../src/tcl-weird/README.md) | El código fuente Tcl se guarda en filas de SQLite | Un comando `unknown` redefinido recupera una fila | El texto recuperado se define y se evalúa como Tcl | El código fuente vuelve como el texto que se guardó. No conserva la identidad de ningún objeto |
| [`apl-weird`](../../src/apl-weird/README.md) | `⎕CR` escribe una función como matriz de caracteres | `⎕FX` define una función a partir de dicha matriz | Cada función reescribe su código fuente, define la copia y la invoca | `⎕FX` acepta de vuelta la matriz: una propiedad de GNU APL que aprovecha la entrada |
| [`regex-sed`](../../src/regex-sed/README.md) y [`m4`](../../src/m4/README.md) | Ninguna fuera del texto mismo: el estado *es* texto | Ninguna: no hay nada que volver a leer | Las reglas reescriben el texto hasta que ninguna se aplica | El texto es su propia representación. Escribirlo y volverlo a leer lo deja idéntico. Es una analogía y no una serialización en el sentido de los grafos de objetos |

Lee la última columna de arriba abajo. Solo una de las cinco filas promete algo sobre el *comportamiento* tras escribir y volver a leer. Además, dice qué no promete. Así quedan claros los límites: "puedo escribirlo y volver a leerlo" es una afirmación más débil que "hará lo mismo". Ambas son más débiles que "puedo pausarlo y continuar".


## Todas las entradas de un vistazo

| Entrada | Lenguajes | Tipo | Qué hace de bucle | Evaluación | Garantía | Se empareja con |
| --- | --- | --- | --- | --- | --- | --- |
| [`apl`](../../src/apl/README.md) | APL | idiomatic | [Operaciones sobre arreglos completos en lugar de pasos](09-casos-de-estudio-comparativos.md#operaciones-sobre-arreglos-completos-en-lugar-de-pasos) | eager | permitido por la implementación | [`apl-weird`](../../src/apl-weird/README.md) |
| [`apl-weird`](../../src/apl-weird/README.md) | APL | weird | [Flujo de control que se reescribe a sí mismo](09-casos-de-estudio-comparativos.md#flujo-de-control-que-se-reescribe-a-sí-mismo) | eager | permitido por la implementación | [`apl`](../../src/apl/README.md) |
| [`awk`](../../src/awk/README.md) | AWK | idiomatic | [La entrada de datos es el bucle](09-casos-de-estudio-comparativos.md#la-entrada-de-datos-es-el-bucle) | eager | garantizado | [`awk-weird`](../../src/awk-weird/README.md) |
| [`awk-weird`](../../src/awk-weird/README.md) | AWK | weird | [La entrada de datos es el bucle](09-casos-de-estudio-comparativos.md#la-entrada-de-datos-es-el-bucle) | eager | permitido por la implementación | [`awk`](../../src/awk/README.md) |
| [`ModernChallenge1`](../../src/ModernChallenge1/README.md) | C# | weird | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | garantizado | [`JavaChallenge1`](../../src/JavaChallenge1/README.md) |
| [`cmake`](../../src/cmake/README.md) | CMake | weird | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | aprovechado por accidente | [`make-gnu`](../../src/make-gnu/README.md) |
| [`cobol`](../../src/cobol/README.md) | COBOL | idiomatic | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | garantizado | [`cobol-weird`](../../src/cobol-weird/README.md) |
| [`cobol-weird`](../../src/cobol-weird/README.md) | COBOL | weird | [Flujo de control que se reescribe a sí mismo](09-casos-de-estudio-comparativos.md#flujo-de-control-que-se-reescribe-a-sí-mismo) | eager | permitido por la implementación | [`cobol`](../../src/cobol/README.md) |
| [`lisp`](../../src/lisp/README.md) | Common Lisp | idiomatic | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | garantizado | [`lisp-weird`](../../src/lisp-weird/README.md) |
| [`lisp-weird`](../../src/lisp-weird/README.md) | Common Lisp | weird | [Despacho y disparadores: la regla activa el siguiente paso](09-casos-de-estudio-comparativos.md#despacho-y-disparadores-la-regla-activa-el-siguiente-paso) | eager | permitido por la implementación | [`lisp`](../../src/lisp/README.md) |
| [`ed-weird`](../../src/ed-weird/README.md) | ed, SQLite | weird | [Texto que se reescribe y se vuelve a leer](09-casos-de-estudio-comparativos.md#texto-que-se-reescribe-y-se-vuelve-a-leer) | rewriting | aprovechado por accidente | [`ex-weird`](../../src/ex-weird/README.md) |
| [`ex-weird`](../../src/ex-weird/README.md) | Ex, SQLite | weird | [Flujo de control que se reescribe a sí mismo](09-casos-de-estudio-comparativos.md#flujo-de-control-que-se-reescribe-a-sí-mismo) | eager | permitido por la implementación | [`ed-weird`](../../src/ed-weird/README.md) |
| [`forth`](../../src/forth/README.md) | Forth | idiomatic | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | garantizado | [`forth-weird`](../../src/forth-weird/README.md) |
| [`forth-weird`](../../src/forth-weird/README.md) | Forth | weird | [Flujo de control que se reescribe a sí mismo](09-casos-de-estudio-comparativos.md#flujo-de-control-que-se-reescribe-a-sí-mismo) | eager | permitido por la implementación | [`forth`](../../src/forth/README.md) |
| [`find-gnu`](../../src/find-gnu/README.md) | find, SQLite | weird | [Flujo de control que se reescribe a sí mismo](09-casos-de-estudio-comparativos.md#flujo-de-control-que-se-reescribe-a-sí-mismo) | declarative | aprovechado por accidente | [`find-posix`](../../src/find-posix/README.md) |
| [`make-gnu`](../../src/make-gnu/README.md) | GNU Make | weird | [Texto que se reescribe y se vuelve a leer](09-casos-de-estudio-comparativos.md#texto-que-se-reescribe-y-se-vuelve-a-leer) | declarative | aprovechado por accidente | [`cmake`](../../src/cmake/README.md) |
| [`regex-sed`](../../src/regex-sed/README.md) | GNU sed, Regular expressions | weird | [Texto que se reescribe y se vuelve a leer](09-casos-de-estudio-comparativos.md#texto-que-se-reescribe-y-se-vuelve-a-leer) | rewriting | aprovechado por accidente |  |
| [`tar-gnu`](../../src/tar-gnu/README.md) | GNU tar, SQLite | idiomatic | [El orden del documento es el programa](09-casos-de-estudio-comparativos.md#el-orden-del-documento-es-el-programa) | eager | permitido por la implementación | [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | weird | [Despacho y disparadores: la regla activa el siguiente paso](09-casos-de-estudio-comparativos.md#despacho-y-disparadores-la-regla-activa-el-siguiente-paso) | eager | permitido por la implementación | [`tar-gnu`](../../src/tar-gnu/README.md) |
| [`GoChallenge1`](../../src/GoChallenge1/README.md) | Go | port | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | garantizado | [`JavaChallenge1`](../../src/JavaChallenge1/README.md) |
| [`haskell`](../../src/haskell/README.md) | Haskell | idiomatic | [Una secuencia perezosa que alguien sigue pidiendo](09-casos-de-estudio-comparativos.md#una-secuencia-perezosa-que-alguien-sigue-pidiendo) | lazy | garantizado | [`haskell-weird`](../../src/haskell-weird/README.md) |
| [`haskell-weird`](../../src/haskell-weird/README.md) | Haskell | weird | [Una secuencia perezosa que alguien sigue pidiendo](09-casos-de-estudio-comparativos.md#una-secuencia-perezosa-que-alguien-sigue-pidiendo) | lazy | permitido por la implementación | [`haskell`](../../src/haskell/README.md) |
| [`JavaChallenge1`](../../src/JavaChallenge1/README.md) | Java | port | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | garantizado | [`ModernChallenge1`](../../src/ModernChallenge1/README.md) |
| [`javascript`](../../src/javascript/README.md) | JavaScript, SQLite | port | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | garantizado | [`javascript-weird`](../../src/javascript-weird/README.md) |
| [`javascript-events`](../../src/javascript-events/README.md) | JavaScript, SQLite | weird | [Despacho y disparadores: la regla activa el siguiente paso](09-casos-de-estudio-comparativos.md#despacho-y-disparadores-la-regla-activa-el-siguiente-paso) | eager | garantizado | [`javascript`](../../src/javascript/README.md) |
| [`javascript-weird`](../../src/javascript-weird/README.md) | JavaScript, SQLite | weird | [Una secuencia perezosa que alguien sigue pidiendo](09-casos-de-estudio-comparativos.md#una-secuencia-perezosa-que-alguien-sigue-pidiendo) | lazy | garantizado | [`javascript`](../../src/javascript/README.md) |
| [`KotlinChallenge1`](../../src/KotlinChallenge1/README.md) | Kotlin | port | [Una secuencia perezosa que alguien sigue pidiendo](09-casos-de-estudio-comparativos.md#una-secuencia-perezosa-que-alguien-sigue-pidiendo) | lazy | garantizado | [`JavaChallenge1`](../../src/JavaChallenge1/README.md) |
| [`LinqChallenge1`](../../src/LinqChallenge1/README.md) | C#, LINQ | weird | [Una secuencia perezosa que alguien sigue pidiendo](09-casos-de-estudio-comparativos.md#una-secuencia-perezosa-que-alguien-sigue-pidiendo) | deferred | garantizado | [`LinqChallenge2`](../../src/LinqChallenge2/README.md) |
| [`LinqChallenge2`](../../src/LinqChallenge2/README.md) | C#, LINQ | weird | [Una secuencia perezosa que alguien sigue pidiendo](09-casos-de-estudio-comparativos.md#una-secuencia-perezosa-que-alguien-sigue-pidiendo) | deferred | garantizado | [`LinqChallenge1`](../../src/LinqChallenge1/README.md) |
| [`m4`](../../src/m4/README.md) | m4 | weird | [Texto que se reescribe y se vuelve a leer](09-casos-de-estudio-comparativos.md#texto-que-se-reescribe-y-se-vuelve-a-leer) | rewriting | permitido por la implementación |  |
| [`regex-pcre2`](../../src/regex-pcre2/README.md) | C, PCRE2, Regular expressions | weird | [Búsqueda con regex, efectos secundarios y fallo deliberado](09-casos-de-estudio-comparativos.md#búsqueda-con-regex-efectos-secundarios-y-fallo-deliberado) | search | permitido por la implementación | [`regex-perl`](../../src/regex-perl/README.md) |
| [`regex-pcre2grep`](../../src/regex-pcre2grep/README.md) | PCRE2, Regular expressions | weird | [Búsqueda con regex, efectos secundarios y fallo deliberado](09-casos-de-estudio-comparativos.md#búsqueda-con-regex-efectos-secundarios-y-fallo-deliberado) | search | permitido por la implementación | [`regex-pcre2`](../../src/regex-pcre2/README.md) |
| [`regex-perl`](../../src/regex-perl/README.md) | Perl, Regular expressions | weird | [Búsqueda con regex, efectos secundarios y fallo deliberado](09-casos-de-estudio-comparativos.md#búsqueda-con-regex-efectos-secundarios-y-fallo-deliberado) | search | permitido por la implementación | [`regex-pcre2`](../../src/regex-pcre2/README.md) |
| [`find-posix`](../../src/find-posix/README.md) | find, SQLite | weird | [Flujo de control que se reescribe a sí mismo](09-casos-de-estudio-comparativos.md#flujo-de-control-que-se-reescribe-a-sí-mismo) | declarative | aprovechado por accidente | [`find-gnu`](../../src/find-gnu/README.md) |
| [`PythonChallenge1`](../../src/PythonChallenge1/README.md) | Python | port | [Una secuencia perezosa que alguien sigue pidiendo](09-casos-de-estudio-comparativos.md#una-secuencia-perezosa-que-alguien-sigue-pidiendo) | lazy | garantizado | [`JavaChallenge1`](../../src/JavaChallenge1/README.md) |
| [`regex-dotnet`](../../src/regex-dotnet/README.md) | C#, Regular expressions | weird | [Búsqueda con regex que devuelve capturas](09-casos-de-estudio-comparativos.md#búsqueda-con-regex-que-devuelve-capturas) | search | garantizado | [`regex-perl`](../../src/regex-perl/README.md) |
| [`RustChallenge1`](../../src/RustChallenge1/README.md) | Rust | port | [Una secuencia perezosa que alguien sigue pidiendo](09-casos-de-estudio-comparativos.md#una-secuencia-perezosa-que-alguien-sigue-pidiendo) | lazy | garantizado | [`JavaChallenge1`](../../src/JavaChallenge1/README.md) |
| [`tcl`](../../src/tcl/README.md) | Tcl | idiomatic | [Un bucle ordinario, usado en un lugar inusual](09-casos-de-estudio-comparativos.md#un-bucle-ordinario-usado-en-un-lugar-inusual) | eager | permitido por la implementación | [`tcl-weird`](../../src/tcl-weird/README.md) |
| [`tcl-weird`](../../src/tcl-weird/README.md) | Tcl, SQLite | weird | [Despacho y disparadores: la regla activa el siguiente paso](09-casos-de-estudio-comparativos.md#despacho-y-disparadores-la-regla-activa-el-siguiente-paso) | eager | permitido por la implementación | [`tcl`](../../src/tcl/README.md) |
| [`xaml`](../../src/xaml/README.md) | XAML, C# | weird | [El orden del documento es el programa](09-casos-de-estudio-comparativos.md#el-orden-del-documento-es-el-programa) | declarative | aprovechado por accidente | [`ModernChallenge1`](../../src/ModernChallenge1/README.md) |
