# Problemas superados

Qué se interpuso en el camino de cada enfoque y cómo lo sorteó. Cada fila nace de un obstáculo que alguien encontró de verdad; la mayoría están documentadas en la sección "Gotchas worth knowing" de la entrada.

Las filas están agrupadas por el *tipo* de obstáculo, así que puedes leer un mismo tema en muchos lenguajes. El orden va de afuera hacia adentro: primero la forma del programa, luego dónde vive su estado, luego su flujo de control, luego cuándo se ejecutan las cosas, luego los límites del anfitrión y por último cómo se hace visible el fallo. Dentro de cada grupo, las filas siguen el orden en que se encontraron.

## Meter el programa a presión en una sola sentencia

El reto permite una sola sentencia. Estas filas tratan de encajar un programa completo en la forma que permite un lenguaje.

| Enfoque | El obstáculo | Cómo se superó | Qué enseña |
| --- | --- | --- | --- |
| **C#** (`ModernChallenge1`) | Un inicializador de `for` permite solo una declaración, pero el bucle necesita siete clases de estado | Un solo objeto anónimo con un campo por cada pieza de estado | Los tipos anónimos son un registro a nivel de expresión |
| **C#** | Los métodos `void` (`Add`, `Show`, `Close`) no caben donde se necesita un valor | `new Func<T>(() => { effect(); return value; }).Invoke()` in situ | Puedes elevar las sentencias a expresiones |
| **LINQ** | Una sentencia debe terminar en una invocación, así que `x is var r && ...` no puede enlazar resultados intermedios | Anida llamadas a `Enumerable.Repeat(x, 1)` para convertir un valor de nuevo en una secuencia de un elemento | Conoce qué formas de expresión son válidas como sentencias |
| **Rust** | Sin `;`, `let` ni `return` en `main` | `successors(...)`; `match x { name => ... }` como `let`; proyección de tuplas como operador coma | Iteradores y clausuras (*closures*, funciones que capturan variables de su entorno) como flujo de control |
| **Go** | Un `for` de tres cláusulas no puede contener sentencias | Funciones auxiliares (`Seq`, `After`) en un archivo aparte | El costo de la restricción, explícito |
| **Python** | Sin bucles `;` ni expresiones de sentencia | `iter(<lambda>, False)` más tuplas y `[-1]` | Expresiones que hacen el papel de sentencias |
| **Kotlin** | Sin `for(;;)` | `generateSequence`, que termina en null | Una secuencia es un bucle |
| **JavaScript** (`javascript`) | Después de `let i = ...` en un encabezado `for`, una coma inicia el siguiente *declarador*; no es el operador coma, así que el inicializador no puede ejecutar además sentencias | El objeto de estado pasa por una función flecha que lo termina con el operador coma | Reconoce qué coma tienes |
| **JavaScript** (`javascript-events`) | `emit()` ejecuta sus escuchadores de eventos (*listeners*, funciones que reaccionan a un evento) antes de retornar, así que una cadena de eventos es una recursión con un nivel más por cada tarjeta, y un throw en un escuchador de eventos llega a quien hizo la llamada | `setImmediate` entre tarjetas, así que la pila se desenrolla, y un `try` en cada escuchador de eventos que convierte un throw en un evento `failed` | Identifica qué llamadas retornan antes de que empiece la siguiente |

## ¿Sin variables? Busca otro lugar donde guardar el estado

Algunos lenguajes no tienen variables, o tienen un lugar para ellas que no sirve para la tarea. El estado fue a parar a una pila, un montón de capturas, una línea de texto, una lista de letras o una base de datos.

| Enfoque | El obstáculo | Cómo se superó | Qué enseña |
| --- | --- | --- | --- |
| **XAML** | El lenguaje de marcado no tiene variables | Arreglos "portadores" que se rellenan in situ con llamadas sucesivas a `ObjectDataProvider` | Búferes mutables como variables |
| **Forth** | Los valores de la pila deben compartirse entre la impresión y SQL | `dup .row` conserva una copia; `outfile-execute` dirige la salida a la tubería | La redirección de la salida como característica del lenguaje |
| `forth-weird` | Sin variables ni palabras de bucle | Estado en la pila; `>in` rebobinado como contador de programa; la bandera (-1/0) como máscara | El estado propio del intérprete es accesible |
| **GNU Make** | Sin aritmética, sin bucle, sin `$(shell)` | Números como listas de `x`; reejecución con `include` de makefiles generados | Reiniciar es un bucle |
| **Regex de Perl** | Las sentencias no pueden vivir en un patrón | Bloques de código `(?{ })` y `(??{ })`; variables de paquete con `local` | Estado que reconoce el retroceso |
| **pcre2grep** | No hay variables en el patrón y los callouts no buscan `PATH` | El estado vive en SQLite; rutas absolutas a los programas | Externaliza el estado |
| **Regex de .NET** | Una regex no tiene contador | Grupos de equilibrio: una pila de capturas | Una pila es un contador |
| **sed** | Sin aritmética y sin variables | Marcas de conteo, un registro de desplazamiento codificado como texto, reglas de sustitución | Un algoritmo de Markov calcula |
| **m4** | Una cadena de texto que crece, en un lenguaje sin variables | `defn` devuelve el texto de una macro, así que una macro se redefine como ella misma más otro fragmento | El estado puede ser texto que se reescribe a sí mismo |
| **find** | Sin variables, sin aritmética y sin contador | Los nombres y las rutas guardan el estado: un directorio es una hora, y su nombre es el último dígito o las horas que quedan. Los patrones `-path` cuentan al coincidir con `/0/` tantas veces como haga falta | El sistema de archivos es la memoria |
| `ed-weird` | `ed` no tiene aritmética ni números | Los números son filas de marcas `x`: sumar es unir dos líneas, y las reglas de reescritura convierten las marcas en dígitos | Elige la representación que tus operaciones puedan cambiar |
| `ex-weird` | Ex tampoco tiene aritmética | Una marca es un registro, y una dirección (`'t+17k t`) es la suma. Una cinta de líneas numeradas guarda los totales decimales | El propio estado del editor (marcas, línea actual) es memoria |
| `tar-gnu-weird` | Un comando que tar ejecuta en cada punto de control no tiene memoria entre llamadas | Una fila de SQLite guarda los registros y una transacción es una transición | Guarda el estado de la máquina fuera de la función de devolución de llamada (*callback*), que es una función que pasas a otro programa para que la ejecute más tarde |
| `javascript-weird` | No debería existir ninguna variable que otro código pueda cambiar | Tres clausuras (*closures*, funciones que recuerdan las variables de su entorno): cada una guarda su estado en variables capturadas a las que solo ella puede acceder | Una clausura es estado privado con una función asociada |

## ¿No hay bucle? Construye el flujo de control con otra cosa

Un bucle es solo una forma de repetir. Estas filas convierten un prefijo calculado, un salto reescrito, una compilación que se reinicia o una jerarquía de clases en la repetición.

| Enfoque | El obstáculo | Cómo se superó | Qué enseña |
| --- | --- | --- | --- |
| **XAML** | El marcado no tiene bucle ni `if` | Cuatro pasadas desenrolladas; las expresiones de SQL o de `DataTable` resuelven la bifurcación | Toma prestado un motor de expresiones |
| **APL** | Un bucle con una condición de parada que depende de los datos | Toma cinco (un límite que nunca puede quedar corto), luego toma un prefijo calculado | Calcula la respuesta y luego recórtala |
| `apl-weird` | Una función no puede copiarse a sí misma... | `⎕CR` lee su código fuente y `⎕FX` define la copia reescrita | El código es una matriz de caracteres |
| `apl-weird` | El ámbito dinámico sobrescribe las variables del padre | Cada encabezado generado vuelve a declarar variables locales (`Locals`) | Las reglas de ámbito dan forma a la metaprogramación |
| **COBOL** | La condición del bucle no debe ser una comparación | Un nombre de condición de nivel `88` sobre el total | Las reglas pueden ser datos |
| `cobol-weird` | Sin `IF`, `PERFORM`, `EVALUATE` ni módulo | `ALTER` reconecta un `GO TO`; un desbordamiento de 2 dígitos es la parada | Flujo de control mutable, desbordamiento como decisión |
| **Haskell** | Una regla de parada sin bucle | `span` sobre listas infinitas perezosas | La evaluación perezosa como control |
| **GNU Make** | Una receta que se expande a nada no cuenta como rehacer un archivo | Un `@:` al final: una orden que no hace nada en el intérprete de comandos (*shell*) | Tiempo de expansión frente a tiempo de ejecución |
| `lisp-weird` | Una clase debe existir antes de que otra pueda heredar de ella, y cinco clases y métodos casi idénticos resultan tediosos | Una macro `defcard` escribe cada par, empezando por la cola; el código que construye los nombres se ejecuta en tiempo de compilación dentro de `eval-when` | Las macros son programas que se ejecutan antes que el tuyo |
| `tcl-weird` | SQL no puede llamar a Tcl, y a Tcl no se le puede dar una biblioteca de código que está en una tabla | `db function tcl call` y una anulación de `unknown` que define procedimientos a partir de filas | La ruta de la biblioteca es tuya para redefinirla |
| **find** | Una herramienta de búsqueda no tiene bucle | El recorrido desciende al directorio que `-exec mkdir` acaba de crear; cada directorio crea el siguiente | Un recorrido que cambia su propio árbol es un bucle |
| **find GNU** | La línea portátil deletrea cada dígito del total | `%d` (profundidad) es el total y `%T` es la semana, así que las tablas desaparecen | Usa las mediciones propias de la herramienta como valores |
| `tcl-weird` | Las filas de widget con fragmentos (`pack -fill ...`) fallaban sin una ruta de widget | Cada fila de `ui` es un comando completo que se ejecuta con `uplevel #0` | Una tabla de cadenas de texto, evaluada en el ámbito correcto |
| **tar** | tar debe ejecutar el programa, y el archivo no puede pedirlo | El `--to-command` del operador asocia el intérprete; el recorrido de tar sobre los miembros es el bucle | La autoridad viene de la línea de comandos, no de los datos |
| `ed-weird` | `ed` no tiene `if` ni bucle, y rechaza un comando global dentro de otro comando global | Un comando global es el bucle. Una sustitución que no coincide se omite en silencio dentro de él, así que cada `s` es `if` | Averigua qué hace la herramienta ante un fallo; puede ser un condicional |
| `ex-weird` | Un registro puede ejecutarse a sí mismo, pero el bucle también debe detenerse, y una búsqueda fallida terminaría nvi | La fila de la cinta para cada total contiene la siguiente instrucción: `@a` para continuar, un comentario para detenerse. El límite es un dato | Una tabla de saltos convierte la regla de parada en un dato |
| `javascript-weird` | Un *fold* (`reduce`) no puede detenerse antes de tiempo | La máquina dice `done` después de la tarjeta que cruza el límite, y un consumidor de iterador se detiene ahí. `reduce` recorre la lista ya terminada | Elige la operación que puede detenerse |

## ¿Cuándo se ejecuta realmente? Orden de evaluación

Los valores perezosos, las recetas expandidas, el texto entre comillas y los separadores globales cambian *cuándo* se ejecuta un fragmento de código. Cada una de estas filas fue un bicho antes de ser una lección.

| Enfoque | El obstáculo | Cómo se superó | Qué enseña |
| --- | --- | --- | --- |
| **LINQ** | Los efectos deben ejecutarse en orden dentro de etapas diferidas | La evaluación de tuplas de izquierda a derecha secuencia `SaveChanges`; un `Aggregate` ansioso final fuerza la cola | Operadores ansiosos frente a diferidos |
| `haskell-weird` | Los efectos deben ejecutarse por celda, en orden, sobre una lista infinita | `fixIO` nudo más `unsafeInterleaveIO` alrededor de cada celda | El orden de evaluación como significado del programa |
| `haskell-weird` | Un `let` perezoso forzó las tarjetas después de que se cerró la tubería | `evaluate (length cards)` antes de la confirmación de la transacción | La pereza muerde dos veces |
| **GNU Make** | La salida de `$(info)` apareció antes del encabezado de SQLite | El informe es una cadena de objetivos *phony* | Make expande una receta antes de ejecutarla |
| **CMake** | Un `MATCHES` fallido borra todos los registros | Pon la prueba de parada primero para que las capturas de la coincidencia principal sobrevivan | Orden de las condiciones con efectos secundarios |
| **m4** | Entrecomillado: un bucle que no debe evaluar su propia llamada antes de tiempo | Pon `[tc_card()]` entre corchetes, para que la llamada solo se expanda después de que `ifelse` la haya elegido | Argumentos evaluados de inmediato, entrecomillado diferido |
| **find** | `*` en `-path` cruza `/`, así que `*/1/b*` coincidió con un `1/b...` anterior de la misma ruta y el dígito se quedó en 2 | Termina cada patrón en un nombre de ancho fijo (de `b00` a `b18`), para que el último segmento esté exactamente donde crees | Ancla el final de un patrón |
| `awk-weird` | `RS` se aplica a cada lectura, así que `getline` desde `date` devolvió una semana vacía | Obtén la semana antes de definir `RS` y luego `close` el comando | El estado global afecta a todos los lectores |
| `tar-gnu-weird` | tar no se detiene cuando se activa la regla de parada y sigue llamando al comando | Una bandera `done` hace que cada tick posterior cambie solo un contador `idle` | Haz inofensivo el trabajo posterior al final, porque no puedes evitar que ocurra |
| `tar-gnu-weird` | Lo que cuenta un punto de control depende del modo (21 al crear, 10 al listar, 21 al extraer el mismo archivo) | Solo se usa la creación, y `check.sh` predice el número de ticks a partir de la disposición | Indica qué cuenta un contador |
| `ex-weird` | nvi ejecuta un registro de varias líneas de la última a la primera; Vim lo ejecuta de la primera a la última | El programa es **una sola línea**, con barras | Cuando dos implementaciones difieren, escribe lo que ambas comparten |
| **JavaScript** | Una animación no debe retrasar ni cambiar el cálculo | El temporizador arranca en la rama falsa de la condición, después de guardar todo y solo en una terminal | Un efecto secundario que va al final no puede perturbar el trabajo |

## El anfitrión tiene límites: portabilidad y detalles de implementación

Ancho de los enteros, precisión de las marcas de tiempo, comportamiento del optimizador, bucles de eventos y diferencias entre implementaciones. Nada de esto forma parte de la parte ingeniosa, y todo puede romperla.

| Enfoque | El obstáculo | Cómo se superó | Qué enseña |
| --- | --- | --- | --- |
| **GNU Make** | Las marcas de tiempo imprecisas de WSL hicieron que un archivo de estado reescrito pareciera no haber cambiado | Un archivo nuevo por pasada: "falta" frente a "presente" no deja lugar a dudas | No confíes en mtime para el estado |
| **GNU Make / CMake** | `wt.exe` trata `;` como su propio separador de subcomandos | Las líneas de comando no contienen `;` | Conoce las reglas de separadores del anfitrión |
| **CMake** | Sin cuantificador `{n}`, *lookahead* ni referencia inversa | Prueba literal de 41-`x`; el sujeto y el patrón se reconstruyen a partir de las capturas del último paso | Trabaja dentro de los límites de la regex más débil |
| **PCRE2** | El optimizador puede omitir los callouts; el JIT no los admite | `PCRE2_NO_AUTO_POSSESS`, `_NO_START_OPTIMIZE`, `_NO_DOTSTAR_ANCHOR`; sin JIT | Conoce lo que el optimizador puede omitir |
| **sed** | Un temporizador sin reloj | Una expresión regular con retroceso catastrófico, calibrada para unos 50 ms por cuadro | Los precipicios de rendimiento son un recurso |
| **Lisp** | SBCL no tiene una función de semana ISO, y una escrita a mano puede ser incorrecta cerca del Año Nuevo | La aritmética del calendario se escribió a mano y se comprobó con `date(1)` en 22 fechas límite, y después con `isocalendar` de Python en 1 139 fechas | Verifica un algoritmo con un oráculo independiente |
| **m4** | `eval` es de 32 bits, así que el `16807 * seed` de un generador se desborda sin avisar (`2147483647*4` es `-4`) | Park-Miller con el truco de Schrage mantiene cada valor intermedio en 32 bits; verificado contra Python en 20 000 valores generados | Conoce el ancho de tus enteros |
| **m4** | `ifelse` con ocho argumentos emitió la advertencia "excess arguments": después del primer grupo continúa de tres en tres | `tc_pick` repite el valor bajo prueba en cada grupo | Lee las reglas de aridad, no solo el ejemplo |
| **Tcl** | Un `tclsh` que cargó Tk nunca termina al final del script | Termina con `catch {destroy .}` | Los bucles de eventos sobreviven a los scripts |
| `tcl-weird` | Un trigger no puede usar un nombre de tabla calificado en `INSERT` | El nombre sin calificar dentro del trigger | Conoce qué permite calificar cada cláusula SQL |
| **AWK** | `--lint` marca los parámetros de función que tienen el mismo nombre que una variable global | Cámbiales el nombre; los parámetros adicionales son las variables locales | En awk el ámbito se maneja por convención |
| **AWK** | `close()` devuelve valores distintos en cada awk (el estado, el estado x 256, siempre 0) | La entrada solo comprueba que el valor sea distinto de cero; los README lo dicen, después de probar los cuatro awk | Prueba cada implementación que afirmas admitir |
| `awk-weird` | mawk no tiene `RT`, así que el programa lee sin parar | Está documentado como exclusivo de gawk; nunca lo ejecutes sin un límite de memoria y un tiempo máximo | Un fallo que parece portable es el peor de todos |
| **find** | `mktemp -d` imprime la ruta que creó, y la ruta cae en medio del SQL | La línea imprime ` -- ` primero, así que la ruta se convierte en un comentario SQL | Haz que el ruido forme parte del lenguaje |
| **find** | Los dados que crea el primero de varios candidatos en reclamar un directorio imprimen `mkdir` errores para los perdedores | Un dado por tarjeta; 62 caracteres no se dividen entre diez, así que `Y` y `Z` se vuelven a tirar sobre el carácter anterior | Prefiere un diseño que no pueda fallar con ruido |
| **find GNU** | `-quit` detiene find antes de que imprima el perfil `-D rates` | Elimina `-quit`; la regla de parada ya no explora nada más y find agota el árbol | Una salida anticipada puede omitir el informe de fin de ejecución |
| `ed-weird` | busybox `ed` no tiene comentarios `g`, `t`, `j` ni `#` y no puede sustituir en `^` | La comprobación afirma que no puede ejecutar el programa, y el README indica solo GNU ed | Un estándar no hace iguales a dos implementaciones |
| `ex-weird` | nvi no se inicia si no puede escribir `/var/tmp/vi.recover`, y la raíz del entorno aislado (*sandbox*, que limita el acceso al sistema anfitrión) es de solo lectura | Las imágenes del entorno aislado enlazan esa carpeta a `/tmp` | Lo que una herramienta necesita para iniciarse forma parte de su interfaz |
| `ex-weird` | nvi escribe sus mensajes, y una nota sobre la falta de terminal, en la salida estándar | El lanzador descarta esa única línea conocida y falla con cualquier otra línea que no sea una fila de tarjeta | Revisa cada línea que imprime una herramienta |
| **JavaScript** | `randomInt` lo exporta `node:crypto`, y el `crypto` global es Web Crypto | `crypto.getRandomValues` para la semilla predeterminada | Mismo nombre, objeto distinto |
| **JavaScript** | `mkdirSync(path, { recursive: true })` bajo `/proc` nunca regresó (Node 24.15, Linux) | La prueba de error usa un archivo simple como carpeta padre | Una prueba negativa no debe colgarse |

## Cómo hacer visible el fallo y hacer cumplir las reglas

Una acrobacia solo es una lección si puedes saber cuándo falla y si una prueba puede intentar romper sus reglas.

| Enfoque | El obstáculo | Cómo se superó | Qué enseña |
| --- | --- | --- | --- |
| **PCRE2** | Un error de callout podría confundirse con "sin coincidencia" | Devuelve `PCRE2_ERROR_CALLOUT`, no `-1` | Haz que un fallo se distinga del éxito por fallo |
| **sed** | La semilla de solo ceros dejaría atascado el registro | Se reemplazó dentro del script | Trata como casos especiales tus puntos fijos |
| `lisp-weird` | La nota de cierre decía primero "6 métodos", al contar el método `:around` | Cuenta solo los métodos cuyos calificadores son `(or)` | La introspección informa de lo que pides, no de lo que querías decir |
| `awk-weird` | Un archivo finito deja un último registro vacío, que se contaría como una tarjeta | `RT == "" { next }` | Protege el borde de un flujo |
| **Todas las entradas de script** | Datos reales podrían filtrarse en una demo | `CHECK(demo_only=1)` hace imposible representar una fila que no sea de demo, y `check.sh` intenta violarlo | Aplica las invariantes en el esquema |
| **Todas las entradas de script** | Demostrar que la restricción es real | Cada `check.sh` busca con grep construcciones prohibidas en el código fuente y se ejecuta 25 veces; Rust tiene una prueba que busca `;` | Una prueba es lo que convierte una acrobacia en una lección |
| **tar** | tar continúa después de que un comando falla, así que a un registro defectuoso lo seguirían registros buenos | El despachador de WPF escribe `faulted` en la base de datos y rechaza todos los miembros posteriores. Un inspector pasivo examina primero todo el archivo comprimido | Falla en modo cerrado y no dependas de que el anfitrión se detenga |
| **tar** | Demostrar que un archivo tar hostil es inerte | Archivos canario, programas sustitutos que fallan si alguien los llama y un archivo tar con `$(touch ...)` como horas | Prueba la ausencia de un efecto con algo que lo mostraría |
| **JavaScript** | Demostrar que el cuerpo del bucle está realmente vacío y que nada oculta el programa | Un escáner pequeño deja en blanco los comentarios y las cadenas de texto, y luego exige un solo `for` con dos puntos y coma y un cuerpo vacío. Debe rechazar seis mutantes | Una prueba de una restricción necesita mutantes que la rompan |

## Patrones en la superación de obstáculos

- **El obstáculo suele ser "el lenguaje no tiene X".** La respuesta casi siempre es "busca dónde el lenguaje ya hace X con otro nombre": una pila, una pila de capturas, un archivo que se vuelve a crear.
- **Se permite que el anfitrión sea pequeño, no que esté ausente.** Muchas entradas necesitan un poco de ayuda (inicializar los dígitos aleatorios, crear un directorio, imprimir las filas). La letra pequeña honesta de cada README dice exactamente cuánta.
- **Los bichos en estas entradas son instructivos.** El error de una unidad (*off-by-one*) en la reescritura de APL, el `let` perezoso de Haskell, las marcas de tiempo gruesas de Make y el `-1` engañoso de PCRE2 son el mejor material del repositorio.

Lo que *todavía* sigue atascado: [problemas bloqueantes](problemas-bloqueantes.md).
