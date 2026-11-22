<!-- GENERADO por lessons/book/build.py a partir de lessons/cs-source/ y del frontmatter de las entradas. No lo edites; edita las fuentes y ejecuta build.py. -->

# Fugas de abstracción y dependencia de la implementación

Para una lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre portabilidad, abstracción y costo](../guias-de-estudio/conceptos/portabilidad-abstraccion-y-costo.md).

Toda abstracción oculta algo y tarde o temprano lo que oculta sale a la luz. De esos momentos trata este capítulo. El estándar de un lenguaje promete unas cosas, permite otras e ignora el resto. Un optimizador puede omitir código que, según el lenguaje, nadie puede observar. Una expresión regular que acaba rápido en todas las pruebas puede tardar un año con una mala entrada de datos. Una característica que nadie prometió puede ser la que todos usan.

Estas ideas explican las tres etiquetas que usa cada lección. **Garantizado** significa que la especificación lo promete. **Permitido por la implementación** significa que una implementación lo permite. **Aprovechado por accidente** significa que funciona y nadie lo prometió. Los conceptos que siguen te dan el vocabulario: abstracciones con fugas, comportamiento indefinido y no especificado, portabilidad, optimizadores, ley de Hyrum, complejidad temporal y ReDoS (denegación de servicio por expresiones regulares). También incluyen la reproducibilidad: anotar toda entrada de datos para que las mismas fuentes den el mismo resultado.

## Abstracciones con fugas

Una abstracción oculta detalles para que puedas pensar a un nivel más alto. Una abstracción *con fugas* deja ver lo que oculta cuando algo falla o cuando importa la velocidad. En 2002 Joel Spolsky acuñó la "ley de las abstracciones con fugas": toda abstracción no trivial deja escapar algo, al menos un poco. Este libro es una colección de fugas que buscamos a propósito. La "búsqueda de coincidencias de texto" deja entrever el costo del retroceso. Una "dependencia" de una herramienta de compilación deja ver las marcas de tiempo de los archivos. La "consulta" de LINQ deja ver los límites de su proveedor de SQL. Puedes seguir usando la abstracción. Solo necesitas conocer la capa que tiene debajo.

- **Úsala cuando:** aprendas a manejar una herramienta. Pregúntate "¿qué tiene debajo y cuándo se dejará ver?".
- **Evita depender de una fuga cuando:** de ella dependa la corrección y no puedas documentarla.

**Lee más:**

- [Abstracción con fugas](https://en.wikipedia.org/wiki/Leaky_abstraction) (Wikipedia)
- [Abstracción (informática)](https://en.wikipedia.org/wiki/Abstraction_(computer_science)) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | demuestra | Que la disposición física de un archivo puede marcar el ritmo de un programa: los puntos de control de tar son un reloj y cada pulso hace avanzar un paso a una máquina de estados. |

## Comportamiento indefinido, no especificado y definido por la implementación

Los estándares usan tres palabras distintas para decir "el estándar no lo dice del todo". **Comportamiento indefinido**: puede pasar cualquier cosa, incluso una caída o un agujero de seguridad. **Comportamiento no especificado**: uno de varios resultados permitidos, y la implementación no tiene que decir cuál. **Comportamiento definido por la implementación**: la implementación debe elegirlo y documentarlo. Las palabras vienen de C y C++, pero la idea vale en todas partes. Existe para dar libertad a los compiladores de optimizar y de ejecutarse en hardware distinto. Las tres etiquetas de este libro (garantizado, permitido por la implementación, aprovechado por accidente) son la misma idea en palabras más amigables. Ejemplos: `ALTER` de COBOL lo conserva GnuCOBOL pero se quitó del estándar, y los significados de `⊃` y `↑` difieren entre GNU APL y Dyalog.

- **Úsalo cuando:** leas un estándar: averigua en qué tipo de "no especificado" te estás apoyando.
- **Evita depender de él.** Herramientas como AddressSanitizer pueden detectar parte del comportamiento indefinido de C y C++ durante la ejecución.

**Más información:**

- [Comportamiento indefinido](https://en.wikipedia.org/wiki/Undefined_behavior) (Wikipedia)
- [Comportamiento no especificado](https://en.wikipedia.org/wiki/Unspecified_behavior) (Wikipedia)
- [AddressSanitizer](https://en.wikipedia.org/wiki/AddressSanitizer) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`cobol-weird`](../../src/cobol-weird/README.md) | COBOL | demuestra | Que un programa puede reescribir su propio flujo de control y que la programación estructurada facilita trazar esos cambios. |
| [`find-gnu`](../../src/find-gnu/README.md) | find, SQLite | demuestra | Que los extras de GNU para find (profundidad de ruta, marcas de tiempo de los archivos, expresiones regulares y un perfilador integrado) pueden reemplazar una tabla entera de ramas, y que el optimizador de find no tiene nada que reordenar cuando cada rama termina en un efecto secundario. |
| [`find-posix`](../../src/find-posix/README.md) | find, SQLite | demuestra | Que un recorrido de directorios puede ser un bucle y un programa: find cava el árbol que está recorriendo, y la ruta al directorio actual es toda la máquina. |

## Portabilidad

El software es portable si se ejecuta bien en más de un entorno: otro sistema operativo, otra implementación del mismo lenguaje u otra versión. La portabilidad es un objetivo porque tus usuarios no tienen todos tu misma máquina. Las herramientas habituales son un estándar escrito, una capa delgada que cubra las diferencias y pruebas en más de una plataforma. Aquí las entradas ofrecen ejemplos honestos. El subconjunto POSIX de AWK se ejecuta en todas partes. Pero usar una expresión regular como separador de registros es una extensión de gawk. En mawk, [`awk-weird`](../../src/awk-weird/README.md) lee sin parar. `close()` devuelve valores distintos según la implementación de AWK. El `pcre2grep` de Ubuntu se compila sin scripts de callout.

- **Úsala cuando:** escribas para usuarios cuyo entorno no controlas. Elige un estándar y prueba al menos dos implementaciones.
- **Evita tomarla como dogma:** si un truco requiere una implementación concreta, nómbrala, fija su versión e indícalo en el README.

**Lee más:**

- [Portabilidad del software](https://en.wikipedia.org/wiki/Software_portability) (Wikipedia)
- [POSIX](https://en.wikipedia.org/wiki/POSIX) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`awk-weird`](../../src/awk-weird/README.md) | AWK | demuestra | Que una expresión regular como separador de registros convierte un flujo de bytes aleatorios en dados, y que el bucle principal implícito de awk más un patrón es un programa completo. |
| [`ed-weird`](../../src/ed-weird/README.md) | ed, SQLite | demuestra | Que un editor de líneas es una máquina de reescritura: las líneas son los datos, las direcciones son el programa y una sustitución fallida dentro de un comando global es un "si". |
| [`ex-weird`](../../src/ex-weird/README.md) | Ex, SQLite | demuestra | Que los registros de un editor pueden contener un programa: una línea de texto se copia en un registro y se ejecuta con @, y las marcas y las direcciones de línea del propio editor hacen la aritmética. |
| [`find-posix`](../../src/find-posix/README.md) | find, SQLite | demuestra | Que un recorrido de directorios puede ser un bucle y un programa: find cava el árbol que está recorriendo, y la ruta al directorio actual es toda la máquina. |
| [`regex-pcre2grep`](../../src/regex-pcre2grep/README.md) | PCRE2, Regular expressions | demuestra | Que los códigos de salida de un programa pueden dirigir el flujo de control. |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | demuestra | Que la disposición física de un archivo puede marcar el ritmo de un programa: los puntos de control de tar son un reloj y cada pulso hace avanzar un paso a una máquina de estados. |

## Optimizadores

Un compilador optimizador reescribe tu programa para que se ejecute más rápido o use menos memoria. Debe conservar el *comportamiento observable* que define el lenguaje (la regla "como si"). Así puedes escribir código claro y aun así obtener código rápido. La fuga está en que todo lo que el lenguaje no considera observable puede desaparecer. En [`regex-pcre2`](../../src/regex-pcre2/README.md), los callouts solo tienen efecto si el motor pasa por ellos. El optimizador puede saltárselos. Por eso el programa compila el patrón con `PCRE2_NO_AUTO_POSSESS`, `PCRE2_NO_START_OPTIMIZE` y `PCRE2_NO_DOTSTAR_ANCHOR`. Tampoco usa el JIT, que no admite callouts.

- **Úsalo cuando:** trabajes con código puro. Confía en el optimizador y mide antes de optimizar a mano.
- **Evítalo cuando:** la corrección dependa de efectos que el lenguaje puede descartar.

**Lee más:**

- [Compilador optimizador](https://en.wikipedia.org/wiki/Optimizing_compiler) (Wikipedia)
- [Regla "como si"](https://en.wikipedia.org/wiki/As-if_rule) (Wikipedia)
- [Eliminación de código muerto](https://en.wikipedia.org/wiki/Dead-code_elimination) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`find-gnu`](../../src/find-gnu/README.md) | find, SQLite | demuestra | Que los extras de GNU para find (profundidad de ruta, marcas de tiempo de los archivos, expresiones regulares y un perfilador integrado) pueden reemplazar una tabla entera de ramas, y que el optimizador de find no tiene nada que reordenar cuando cada rama termina en un efecto secundario. |
| [`regex-pcre2`](../../src/regex-pcre2/README.md) | C, PCRE2, Regular expressions | demuestra | Que los callouts de regex pueden servir como un conjunto diminuto de instrucciones. |

## Ley de Hyrum

La ley de Hyrum dice que, si una interfaz tiene suficientes usuarios, alguien dependerá de *cada* comportamiento observable, sin importar lo que prometa la documentación. Hyrum Wright, ingeniero de software en Google, formuló esta observación. La ley explica la tercera etiqueta del libro, **aprovechado por accidente**. GNU Make documenta que se reinicia después de rehacer un makefile incluido. Nunca prometió que pudieras usar ese comportamiento como bucle. Cuando no hay coincidencia, `MATCHES` de CMake borra todas las variables `CMAKE_MATCH`. Es un comportamiento observado, sin garantía. Las entradas se apoyan en ambos comportamientos. Los mantenedores también conocen la ley. Go, por ejemplo, cambia al azar el orden de iteración de los mapas para que nadie dependa de él.

- **Úsala cuando:** cambies una biblioteca (alguien depende del comportamiento anterior) o decidas si puedes depender de un comportamiento sin documentar (anótalo y agrega una prueba).
- **Evítala cuando:** el código del que otros dependen necesite un comportamiento que nadie prometió.

**Lee más:**

- [Ley de Hyrum](https://en.wikipedia.org/wiki/Hyrum%27s_law) (Wikipedia)
- [Compatibilidad con versiones anteriores](https://en.wikipedia.org/wiki/Backward_compatibility) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`cmake`](../../src/cmake/README.md) | CMake | demuestra | Que `while()` y una regex pueden formar una pequeña máquina de registros. |
| [`ed-weird`](../../src/ed-weird/README.md) | ed, SQLite | demuestra | Que un editor de líneas es una máquina de reescritura: las líneas son los datos, las direcciones son el programa y una sustitución fallida dentro de un comando global es un "si". |
| [`find-gnu`](../../src/find-gnu/README.md) | find, SQLite | demuestra | Que los extras de GNU para find (profundidad de ruta, marcas de tiempo de los archivos, expresiones regulares y un perfilador integrado) pueden reemplazar una tabla entera de ramas, y que el optimizador de find no tiene nada que reordenar cuando cada rama termina en un efecto secundario. |
| [`find-posix`](../../src/find-posix/README.md) | find, SQLite | demuestra | Que un recorrido de directorios puede ser un bucle y un programa: find cava el árbol que está recorriendo, y la ruta al directorio actual es toda la máquina. |
| [`make-gnu`](../../src/make-gnu/README.md) | GNU Make | demuestra | Que GNU Make puede hacer aritmética y bucles con su propia sintaxis, sin un intérprete de comandos para ninguno de los dos. Un intérprete de comandos es el programa que recibe y ejecuta los comandos que escribes. |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | demuestra | Que la disposición física de un archivo puede marcar el ritmo de un programa: los puntos de control de tar son un reloj y cada pulso hace avanzar un paso a una máquina de estados. |

## Precipicios de rendimiento y complejidad temporal

La complejidad temporal describe cómo crece el tiempo de ejecución con el tamaño de la entrada de datos: lineal (n), cuadrática (n²), exponencial (2ⁿ). Existe porque las pruebas pequeñas esconden problemas grandes. Una función que tarda un milisegundo con diez elementos puede tardar un año con sesenta. En este repositorio el precipicio se usa a propósito. [`regex-sed`](../../src/regex-sed/README.md) tiene una expresión regular con retroceso catastrófico, ajustada para tardar unos 50 milisegundos por cuadro, como *reloj*. Es un buen truco en una demostración, y un buen ejemplo de por qué no puedes usar la velocidad como temporizador en software real: otra máquina, otra versión, otra respuesta.

- **Úsalo cuando:** antes de publicar código que maneje entradas de datos grandes u hostiles, pregúntate cuál es el peor caso.
- **Evítalo cuando:** necesites un reloj o una garantía de tiempo transcurrido.

**Más información:**

- [Complejidad temporal](https://en.wikipedia.org/wiki/Time_complexity) (Wikipedia)
- [Notación de O grande](https://en.wikipedia.org/wiki/Big_O_notation) (Wikipedia)
- [Teoría de la complejidad computacional](https://en.wikipedia.org/wiki/Computational_complexity_theory) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`regex-sed`](../../src/regex-sed/README.md) | GNU sed, Regular expressions | demuestra | Que un programa puede ser una línea de texto que las sustituciones reescriben hasta que ninguna se aplique: un algoritmo de Markov, con una expresión regular de retroceso catastrófico como reloj. |

## Denegación de servicio mediante expresiones regulares

ReDoS (denegación de servicio mediante expresiones regulares) es un ataque que envía una entrada de datos con la que un motor de expresiones regulares con retroceso tarda un tiempo exponencial o muy largo. Un patrón como `(a+)+$` funciona bien con la mayoría de las cadenas de texto y pésimo con una secuencia larga de caracteres `a` seguida de `!`. El ataque existe porque un motor de retroceso prueba todas las formas de hallar una coincidencia antes de rendirse. Esto ha causado interrupciones reales: una expresión regular en una regla de un cortafuegos web tumbó Cloudflare en 2019. Otra, que buscaba espacios en blanco, ralentizó Stack Overflow en 2016. Las medidas de mitigación son sencillas: usa un motor que halle coincidencias en tiempo lineal (RE2, `regex` de Rust o la opción `NonBacktracking` de .NET). Fija un tiempo máximo para hallar una coincidencia y limita la longitud de la entrada.

- **Aplica este conocimiento cuando:** cualquier expresión regular procese datos que tú no controlas.
- **Evítalo cuando:** un patrón con solapamientos tenga cuantificadores anidados o un usuario envíe un patrón sin revisar.

**Lee más:**

- [Denegación de servicio mediante una expresión regular](https://en.wikipedia.org/wiki/Regular_expression_denial_of_service) (Wikipedia)
- [Ataque de complejidad algorítmica](https://en.wikipedia.org/wiki/Algorithmic_complexity_attack) (Wikipedia)
- [Denegación de servicio mediante una expresión regular: ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) (OWASP)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`regex-sed`](../../src/regex-sed/README.md) | GNU sed, Regular expressions | demuestra | Que un programa puede ser una línea de texto que las sustituciones reescriben hasta que ninguna se aplique: un algoritmo de Markov, con una expresión regular de retroceso catastrófico como reloj. |

## Reproducibilidad y compilaciones deterministas

Un resultado es **reproducible** si la misma entrada de datos da la misma respuesta cada vez y en cualquier máquina. Una compilación es **determinista** si las mismas fuentes producen los mismos bytes. Ambas propiedades dependen de anotar todo lo que forma parte de la entrada: la semilla, el orden de los elementos, las versiones de las herramientas y la hora. De lo que olvides anotar saldrá la diferencia.

La compilación del libro que lees funciona así: ordena cada lista, nada consulta el reloj y un archivo de metadatos fija la fecha de compilación. Por eso las mismas fuentes dan los mismos bytes. Las entradas aplican la idea de cuatro maneras. [`tar-gnu`](../../src/tar-gnu/README.md) escribe un archivo tar con formato, orden, hora y propietario fijos. La misma semilla produce el mismo archivo byte por byte, como comprueba `cmp`. En [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md), la ejecución es función de una semilla y de la disposición del archivo. [`javascript`](../../src/javascript/README.md) y [`javascript-weird`](../../src/javascript-weird/README.md) repiten una ejecución con `SEED=42`. No puedes fijar una semilla para `Math.random`, pero sí para una pequeña clausura (*closure*) que captura un número. Cada entrada dice qué significa "lo mismo": los bytes, la estructura o el comportamiento (consulta [Serialización, deserialización y pickling de objetos](06-estado-mas-alla-de-las-variables.md#serialización-deserialización-y-pickling-de-objetos)).

- **Úsala cuando:** debas depurar, probar o auditar un resultado más tarde. Explicita la entrada de datos y registra la semilla.
- **Evita confundirla** con el determinismo de *todo*. Una ejecución es reproducible en los aspectos que indicaste. Los demás quedan fuera, como la fecha asociada a un número de semana cerca de Año Nuevo.

**Lee más:**

- [Compilaciones reproducibles](https://en.wikipedia.org/wiki/Reproducible_builds) (Wikipedia)
- [Algoritmo determinista](https://en.wikipedia.org/wiki/Deterministic_algorithm) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`javascript`](../../src/javascript/README.md) | JavaScript, SQLite | demuestra | Que una sentencia for consta de tres expresiones y un cuerpo vacío, y que el orden de evaluación propio de JavaScript, la veracidad de los valores y el operador coma bastan para ejecutar un programa completo a partir de las tres cláusulas. |
| [`javascript-events`](../../src/javascript-events/README.md) | JavaScript, SQLite | demuestra | Que un programa puede ser un conjunto de escuchadores de eventos, cada uno con una sola tarea pequeña que termina emitiendo el evento que espera el siguiente; y que emit() llama a sus escuchadores de inmediato, así que solo un límite de planificación explícito da un turno al bucle de eventos. |
| [`javascript-weird`](../../src/javascript-weird/README.md) | JavaScript, SQLite | demuestra | Que una clausura es una máquina de estados: una función más las variables junto a las que se creó, que un iterador hace avanzar un paso a la vez, con reduce como el único pliegue que no puede detenerse. |
| [`tar-gnu`](../../src/tar-gnu/README.md) | GNU tar, SQLite | demuestra | Que un archivo tar puede ser un programa serializado: tar lee los miembros en orden y solo el comando que indica el operador les da un efecto. |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | demuestra | Que la disposición física de un archivo puede marcar el ritmo de un programa: los puntos de control de tar son un reloj y cada pulso hace avanzar un paso a una máquina de estados. |
