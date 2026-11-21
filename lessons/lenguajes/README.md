# Por lenguaje

Cada página explica qué hace especial al lenguaje, con enlaces al repositorio y luego sus rarezas. Los enlaces tienen el aspecto de `file#Lnn`: los números de línea se desplazan, así que también se cita la línea clave.

| Página | Entradas | El truco raro | La lección de fondo |
| --- | --- | --- | --- |
| [APL](apl.md) | `apl`, `apl-weird` | Cinco tiradas y un "take-while"; funciones que fabrican a sus sucesoras | El código como datos, la metaprogramación y una notación pensada para la pizarra |
| [AWK](awk.md) | `awk`, `awk-weird` | Un separador de registros con regex convierte `/dev/urandom` en dados; `t > 40 { exit }` es la regla de parada | Bucles implícitos, patrones como condicionales, dónde termina POSIX awk y dónde empieza gawk |
| [C#, LINQ, XAML](csharp-linq-xaml.md) | `ModernChallenge1`, `LinqChallenge1/2`, `xaml`, además de Java, Kotlin, Python, Go, Rust | Todo dentro de un `for` sin cuerpo; escrituras en la base de datos y animación WPF dentro de una consulta; un analizador sintáctico que ejecuta métodos | Ejecución diferida, fronteras de proveedor, efectos secundarios, afinidad con el hilo de la interfaz |
| [COBOL](cobol.md) | `cobol`, `cobol-weird` | `ALTER` cambia un destino de `GO TO`; un campo que se desborda es la regla de parada | Flujo de control mutable, reglas declaradas en los datos, diseño histórico del entorno de ejecución |
| [Common Lisp](lisp.md) | `lisp`, `lisp-weird` | Una jerarquía de clases es el bucle y la combinación de métodos de `or` es la regla de parada | Combinación de métodos, lista de precedencia de clases, etiquetas del lector, enlace dinámico, el protocolo de metaobjetos |
| [ed y Ex](editores.md) | `ed-weird`, `ex-weird` | Los comandos de `ed` son un sistema de reescritura (un `s` fallido es un `if`); en Ex un registro se ejecuta solo y las marcas hacen la aritmética | Reescritura de texto, código como texto, estado fuera del texto, estándares frente a implementaciones |
| [find](find.md) | `find-posix`, `find-gnu` | El recorrido excava el directorio que está recorriendo; la ruta es la pila de llamadas y los nombres son los contadores | Recorrido de árboles como bucle, patrones de ruta como tablas de consulta, qué reemplazan los extras de GNU, qué deja sin especificar POSIX |
| [Forth](forth.md) | `forth`, `forth-weird` | La posición de análisis del intérprete de texto es el contador de programa | El intérprete es un programa al que puedes meter la mano |
| [Haskell](haskell.md) | `haskell`, `haskell-weird` | Evaluar un elemento de una lista realiza E/S | Evaluación perezosa, orden de evaluación, transparencia referencial, operaciones inseguras |
| [JavaScript](javascript.md) | `javascript`, `javascript-weird`, `javascript-events` | El `for` sin cuerpo del original en Node.js; ningún bucle, de dos maneras: las clausuras recuerdan el estado y un iterador perezoso tira de las tarjetas, o diez escuchadores de eventos en un `EventEmitter` se emiten el paso siguiente unos a otros | Orden de evaluación, clausuras, iteradores y demanda, por qué `reduce` no puede detenerse, `emit()` síncrono frente al bucle de eventos |
| [m4](m4.md) | `m4` | Una macro cuya última palabra es ella misma: volver a escanear es el bucle | Las comillas como evaluación perezosa, el texto como único tipo de datos, aritmética de 32 bits |
| [Make y CMake](make-cmake.md) | `make-gnu`, `cmake` | Rehacer los makefiles se convierte en un bucle; las capturas de regex se convierten en registros | Grafos de dependencias, semántica de reinicio, ámbito, evaluación de condiciones con estado |
| [Regex](regex.md) | `regex-perl`, `regex-pcre2`, `regex-pcre2grep`, `regex-dotnet`, `regex-sed` | Las sustituciones implementan aritmética y estado; coincidencias que devuelven falso después de hacer el trabajo | Sistemas de reescritura de cadenas de texto, retroceso como búsqueda, precipicios de rendimiento |
| [tar](tar.md) | `tar-gnu`, `tar-gnu-weird` | Un archivo tar es el programa (tar recorre los miembros, y el `--to-command` del operador les da sentido); y la disposición del archivo es un reloj (cada registro escrito es un tic) | Serialización frente a ejecución, fronteras de confianza, relojes lógicos, intérpretes que fallan cerrados |
| [Tcl](tcl.md) | `tcl`, `tcl-weird` | El programa es texto en una tabla de SQLite; un disparador recursivo es el bucle | Todo es un comando de cadena de texto, `unknown` como ruta de biblioteca, el código y los datos son una sola cosa |

¿Prefieres empezar por un mecanismo? Consulta los [patrones](../patrones.md). Vuelve al [índice de lecciones](../README.md).
