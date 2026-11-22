# Problemas de bloqueo

Lo que cada enfoque **no** ha resuelto, medido frente a una línea base.

## La línea base: el reto moderno en C#

[`ModernChallenge1`](../src/ModernChallenge1/README.md) es el reto exitoso de referencia. Dentro de un solo `for` sin cuerpo hace **todo** esto:

| Capacidad | En `ModernChallenge1` |
| --- | --- |
| Horas aleatorias (de 10 a 19) | `Random.Shared.Next(10, 20)` en el iterador |
| Total acumulado y regla de parada | LINQ `Sum() <= 40d` en la condición |
| Persistencia | EF Core con SQLite, `SaveChanges` |
| Concurrencia | Un `Thread` en segundo plano más un `Mutex` |
| Una interfaz de usuario real | Una ventana WPF creada a partir de XAML en tiempo de ejecución |
| Animación | Un `DoubleAnimation` de desvanecimiento |
| Una sentencia | Exactamente un `for`, con el cuerpo vacío |

La comparación no es "quién es mejor". Es "¿qué partes de esa lista no puede alcanzar todavía este enfoque?". Cada brecha de abajo es un reto abierto para los ejercicios.

## Matriz de capacidades

`yes` = hecho dentro del propio truco; `host` = hecho, pero por el script anfitrión o un auxiliar, no por el truco; `no` = no hecho. Los datos salen del README de cada entrada. Las celdas casi vacías se anotan en la lista por entrada en lugar de adivinarlas.

| Entrada | Aleatorio | Persistencia | Ventana / pulso | Hilo | Fallar a propósito / una sentencia |
| --- | --- | --- | --- | --- | --- |
| C# `ModernChallenge1` | sí | sí | sí | sí | un `for` |
| LINQ 1 / 2 | **no** (cinco días fijos de 8 horas por semana) | sí | sí | no | una sentencia |
| XAML | **no** (`Random(42)`, igual en cada ejecución) | sí (`strict`: solo XML) | sí | sí | sin bucle (desenrollado x4) |
| `regex-perl` | sí | sí | pulso en la terminal | no | una coincidencia, devuelve false |
| `regex-pcre2` | sí | archivo TSV | terminal pulse | no | una coincidencia, devuelve false |
| `regex-pcre2grep` | sí | sí (sin transacción) | terminal pulse | no | devuelve false; el anfitrión no es nothing |
| `regex-dotnet` | **no** (el anfitrión da la semilla) | **no** | **no** | no | **debe devolver true** |
| `regex-sed` | LFSR de juguete | sí | pulso de la terminal | no | sale con 1 a propósito |
| `make-gnu` | sí | anfitrión (`sqlite3`) | brillo de la terminal | no | el reinicio es el bucle |
| `cmake` | anfitrión (cinta de dígitos) | anfitrión | brillo de la terminal | no | el anfitrión informa |
| Java / Kotlin / Python / Go / Rust | sí | sí | sí (ventana o página) | sí | uno `for`/iterador; Go necesita funciones auxiliares |
| `lisp`, `lisp-weird` | sí | mediante la tubería `sqlite3` | solo terminal | no | `or` detiene la cadena de métodos; una sola sentencia no es la regla |
| `m4` | sí (Park-Miller propio; el anfitrión aporta la semilla) | anfitrión (`syscmd` + `sqlite3`) | solo terminal | no | la autoexpansión termina cuando `ifelse` lo indica |
| `tcl`, `tcl-weird` | sí | sí (paquete `sqlite3` dentro del proceso) | ventana Tk opcional (`--gui`) | no | el disparador recursivo se detiene con un `INSERT ... SELECT` vacío |
| `awk` | sí (`rand`, con semilla tomada del anfitrión) | mediante tubería `sqlite3` | solo terminal | no | un `while`; no es una entrada de una sola sentencia |
| `awk-weird` | sí (los dados son `RT` a partir de `/dev/urandom`) | mediante una tubería de `sqlite3` | solo en la terminal | no | `t > 40 { exit }`; **solo gawk** |
| `find-posix` | sí (nombres `mktemp -d`; el último carácter elige las horas) | mediante tubería `sqlite3` | solo en la terminal | no | un `find`; el recorrido termina cuando se acaba el árbol. No se ejecuta en BSD ni en macOS |
| `find-gnu` | sí (los mismos dados) | mediante `sqlite3` en el fd 3 | solo en la terminal | no | un GNU `find`; `-O0` y `-O3` deben coincidir. **Solo GNU find** |
| `apl`, `apl-weird`, `cobol`, `cobol-weird`, `forth`, `forth-weird`, `haskell`, `haskell-weird` | sí | mediante `sqlite3` en una tubería o un script | solo en la terminal | no | una sola sentencia no es la regla |

Las entradas de script de Linux comparten una forma de reporte (filas, un total confirmado y una nota de acrobacia) y no abren ventanas. Para ellas, lee "Window / pulse" en esta tabla como "salida de la terminal".

## Muros por enfoque

### C# y LINQ

- **Las entradas de LINQ no sortean horas aleatorias.** Convierten una semana laboral fija de cinco días de 8 horas en 40 horas. La regla de parada sigue siendo un tope sobre el prefijo, pero el requisito de "de 10 a 19 horas aleatorias" no se cumple.
- **Cada llamada a `void` necesita un envoltorio `Func<T>`.** El código legible usaría una sentencia.
- **Cierta evaluación inmediata es inevitable.** `Aggregate` es de evaluación inmediata por definición, y `SaveChanges()` se llama una vez, de forma inmediata, en el punto donde `Repeat(...)` evalúa su argumento.
- **Los acumuladores mutables** (`list.Add`) son un atajo, no pureza de LINQ.
- **La sintaxis de consulta no puede expresar** `Aggregate`, `Repeat`, `ToList`, `Sum`, `Single` o `AsEnumerable` ([README de LinqChallenge2](../src/LinqChallenge2/README.md)).
- **`DbContext` no es seguro para hilos**; el `Mutex` solo lo disimula.
- **Solo para Windows** (WPF).

### XAML

- Sin bucle: cuatro pasadas desenrolladas y copiadas y pegadas.
- WPF no ramifica por sí mismo; deciden SQL o expresiones `DataTable`.
- `strict.xaml` guarda XML en lugar de una base de datos.
- Los mismos números "aleatorios" en cada ejecución.

### `regex-dotnet`

- **Una expresión regular no puede generar números aleatorios**, así que el anfitrión siembra cinco cadenas de texto unarias.
- **Una regex no puede escribir**, así que no hay efectos secundarios.
- **El movimiento característico es imposible.** Si añades `(?!)`, la coincidencia falla, y una `Match` fallida no expone ninguna captura. La entrada debe devolver true.
- **Sin pulso.** Necesita efectos secundarios durante la coincidencia.
- **Aleatoriedad desenrollada**: la cinta siempre contiene cinco sorteos aunque solo se necesiten tres.
- **El anfitrión sigue informando**, con `Zip` sobre las capturas.

### `regex-pcre2grep`

- El estado no puede vivir en el patrón; el total vive en SQLite y los callouts lo vuelven a leer.
- Sin transacción: cada función auxiliar confirma de inmediato, así que no se puede deshacer nada.
- Los callouts necesitan rutas absolutas de programas.
- Requiere una compilación de `pcre2grep` con soporte de *callout* (la de Ubuntu no lo incluye).
- No es seguro con concurrencia: una ejecución se identifica por `max(id)`.
- Solo se probó con PCRE2 10.49.

### `regex-perl` y `regex-pcre2`

- Perl: los bloques de código necesitan variables de paquete; el año ISO puede diferir cerca del Año Nuevo.
- PCRE2: los *callouts* necesitan el optimizador desactivado y sin JIT; el autor no probó con las banderas quitadas. Todavía se requiere un anfitrión en C.

### `regex-sed`

- **Un RNG de juguete**: un LFSR de 16 bits. La misma semilla genera las mismas tarjetas.
- **sed tiene saltos `b` y `t`**, así que su bucle es "una máquina con un contador de programa", no una sola coincidencia.
- **"Devuelve false" es más débil**: indica el estado de salida del proceso, no la coincidencia.
- **Solo GNU.**
- **La velocidad del pulso depende de la máquina** (calibrada en una sola máquina WSL 2).
- `check.sh` busca `e`/`r`/`R`/`w`, pero un grep no es un entorno aislado (*sandbox*) que limite el acceso al sistema anfitrión.

### GNU Make

- Se necesita un intérprete de comandos (*shell*) para `mkdir -p`, `sqlite3`, `rm` y el no-op `@:`; en Make puro no hay forma de crear un directorio ni un archivo SQLite.
- Solo UTC; el calendario es válido hasta 2134.
- Una ejecución que falla deja `.tc-*.mk` y la siguiente `make` se niega a continuar hasta que `make clean`.
- Solo Linux: la detección del reloj, de la entropía y de la terminal lee `/proc`.
- El cuadro emergente de Windows Terminal necesita `wt.exe`.

### CMake

- **Sin repetición con contador, anticipación (*lookahead*) ni referencias inversas** en las expresiones regulares de CMake.
- **La salida no puede ocurrir dentro de una condición**, así que el anfitrión imprime, escribe y anima después del bucle.
- Los sorteos aleatorios son una cinta de nueve dígitos generada por el anfitrión.
- El año ISO se corrige a mano.

### COBOL, Forth, Haskell y APL

- `cobol-weird`: `ON SIZE ERROR` sigue siendo un condicional, y la elección de la carpeta de datos depende de un índice de tabla calculado a partir de una longitud. El programa no es independiente de un intérprete de comandos (`CALL "SYSTEM"` para `mkdir` y `sqlite3`).
- `forth-weird`: funciona solo en el nivel superior o en texto procesado con `evaluate`, y el bucle y su estado deben permanecer en una sola línea.
- `haskell-weird`: no se ha pasado por `ormolu` ni por `hlint`; depende del orden de `unsafeInterleaveIO`; ningún paquete de números aleatorios se incluye con GHC.
- `apl-weird`: depende de `⎕IO←0`; una reescritura incorrecta falla al recursar sin fin; `⎕FIO` y `⊃`/`↑` son específicos del intérprete. La entrada directa necesita una compilación fija de GNU APL.
- **Ninguno de estos abre una ventana ni ejecuta un hilo.**

### Lisp, m4, Tcl y AWK

- **Lisp (ambos)**: solo SBCL (`sb-ext:run-program` y similares; la combinación `or` y `defcard` son estándar). No existe ningún formateador. **`lisp-weird`**: el límite está integrado en el diseño (cinco clases manejan "de 10 a 19 horas, para si pasa de 40"; una regla que necesite más tarjetas necesita más clases) y su conteo de métodos usa el MOP.
- **m4**: requiere GNU m4 para `esyscmd` y `format`. El reloj, la entropía y SQLite llegan a través del intérprete de comandos; m4 no tiene E/S propia. `eval` es de 32 bits, así que el generador se construye en torno a ese límite. La recursión se hace más profunda con cada tarjeta: sirve para 3 a 5 tarjetas y no es un patrón para miles. Una comilla que falta provoca una ejecución descontrolada, no un error. No hay `m4-weird`, por diseño.
- **Tcl**: el paquete `sqlite3` es independiente de Tcl. Un `tclsh` que ha cargado Tk no termina al final de un script a menos que el script destruya la ventana, y `DISPLAY=:0` bajo WSL bloquea Tk (las comprobaciones usan Xvfb). **`tcl-weird`**: depende de que SQLite evalúe `tcl('hours')` una sola vez por ejecución del trigger, algo que SQLite no promete (`check.sh` lo detectaría); `unknown` ejecuta lo que haya en la tabla, así que no es un patrón para tablas que otros pueden editar; SQLite limita la recursión de los triggers (1000 de forma predeterminada).
- **AWK**: `close()` de una tubería devuelve valores distintos en awks distintos, y la compilación de one-true-awk que se probó devuelve 0, así que un `sqlite3` que falle pasaría inadvertido allí. **`awk-weird`**: solo gawk (`RT`); mawk se queda ejecutándose para siempre sin avisar o informa de cero tarjetas. Un nombre de directorio que contiene una comilla simple rompe el comando que crea el directorio de datos en el intérprete de comandos, el programa que lee y ejecuta comandos.
- **Ninguno de los cuatro** abre un hilo; solo las entradas de Tcl abren una ventana (`--gui` opcional).

### find

- **`find-posix`**: depende de que find lea un directorio después de visitarlo (POSIX no lo especifica; funciona en GNU find 4.9, bfs 3.1.2 y busybox 1.36.1) y de `{}` dentro de un argumento más largo (`{}/b09`; POSIX tampoco lo especifica). `mktemp` no es POSIX. **No se ejecutó en BSD ni en macOS.** busybox ejecuta `mktemp` dentro del mismo proceso, así que se omiten las pruebas de dados forzados. La línea mide unos 5.7 KB porque find no tiene variables.
- **`find-gnu`**: solo GNU find (`-fprintf`, `%d`, `%T`, `-regex`, `-D`). Se evita `-quit` porque omite el perfil `-D rates`. `/dev/fd/3` debe ser una tubería o find la trunca. 
- **Ninguno** abre una ventana ni un hilo, y ninguno tiene brillo ni pulso.

### tar, ed, Ex y JavaScript

- **`tar-gnu`**: solo GNU tar (`--to-command`, `--occurrence`); probado en las versiones 1.34 y 1.35. Los dados se lanzan cuando se escribe el archivo, y el despachador hace la única suma (en SQL). **No** captura el estado de la ejecución en vivo: una ejecución detenida no se puede reanudar, solo reproducir de nuevo. tar no se detiene cuando falla su comando, así que la detención es propia del intérprete.
- **`tar-gnu-weird`**: una transición, en SQL, hace toda la aritmética, y solo los puntos de control de tar deciden *cuándo*. Lo que cuenta un punto de control depende del modo, así que solo se usa la creación de un archivo. No se ejecuta en tar de BSD ni de macOS.
- **`ed-weird`**: solo GNU ed (busybox ed no puede ejecutarlo). Que un `s` fallido dentro de un comando global sea silencioso es un comportamiento de GNU que su manual no promete. Los totales son filas de marcas, así que el programa no escala más allá de unas pocas docenas. El lanzador aporta los dados, porque `ed` no tiene aleatoriedad.
- **`ex-weird`**: la cinta tiene sesenta líneas de datos, una por cada total posible y nada calcula un límite distinto. Lo ejecutamos en nvi 1.81.6 y en Vim 9.1; no ejecutamos una suite de conformidad. nvi necesita que su carpeta de recuperación tenga permiso de escritura. 
- **`javascript`**: necesita Node 24 o superior para `node:sqlite`. Sin hilos, mutex ni reflexión (el C# los tenía como una cápsula del tiempo de 2008). Las categorías se repiten, mientras que el C# se detenía después de cuatro. El año es el año ISO, mientras que el C# guardaba el año calendario.
- **`javascript-weird`**: la prueba de ciclo de vida depende de una recolección de basura forzada (`WeakRef`) y es la única prueba que depende del motor. `map` con efectos es un truco. Un iterador se agota después de un solo recorrido.
- **`javascript-events`**: requiere Node 24 o posterior, para mantener las tres entradas de Node al paso. `emit()` es síncrono, así que el programa debe planificar cada tarjeta con `setImmediate` o la pila crece con cada tarjeta. Una excepción lanzada en un escuchador de eventos llega a quien llama a `emit()`, así que cada escuchador de eventos captura la suya. Un emisor no tiene contrapresión: este programa es seguro solo porque cada tarjeta espera a la anterior. 

### Las adaptaciones

- Los perfiles de **Windows Sandbox** de Java, Kotlin y Go aún no se han probado en hardware real; Rust no tiene perfil de Windows Sandbox; las adaptaciones con interfaz gráfica no tienen script de comprobación y la compuerta aún no las cubre ([`sandbox/README.md`](../sandbox/README.md)).
- Las operaciones de Go que solo admiten sentencias viven en un archivo auxiliar, que es el costo declarado de esa versión.

## Retos abiertos

Cada uno de estos es un [ejercicio](exercises.md#g-retos-abiertos-sin-verificar-pueden-ser-imposibles):

1. Da a las entradas de LINQ tarjetas aleatorias de 10 a 19 horas, sin salir de una sola sentencia.
2. Haz que `regex-dotnet` falle a propósito sin perder sus capturas.
3. Dale a `regex-dotnet` un efecto secundario (un pulso) por una ruta sin `MatchEvaluator`.
4. Haz que `cmake` produzca su salida desde la condición, o reemplaza la cinta de dígitos del anfitrión.
5. Da a Make una fuente aleatoria y un calendario hechos solo con Make, que no lean `/proc`.
6. Añade un hilo a cualquier entrada de script de Linux.
7. Ejecuta las entradas de Windows en Linux, o añade un perfil de Windows Sandbox para Rust.
8. Haz que `awk-weird` funcione con mawk (o con cualquier awk que no sea GNU): obtén una tirada de dado sin `RT`.
9. Da a m4 su semilla y su semana sin `esyscmd`.
10. Adapta `lisp-weird` a un segundo Common Lisp (ECL o CCL) reemplazando solo las llamadas específicas de SBCL.
11. Ejecuta `check.sh` de `find-posix` en un `find` de BSD o macOS, y anota exactamente qué falla (`{}` en `{}/b09`, `-path`, `mktemp`, `date +%G-W%V`).

> **NO HAY BLOQUEOS, SOLO FALTA IMAGINACIÓN.** La lista de arriba es el presupuesto de imaginación.
