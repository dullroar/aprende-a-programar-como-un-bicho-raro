# Guía de estudio de portabilidad, abstracción y costo

## Para qué sirve esta guía

Toda abstracción oculta algo. Tarde o temprano, lo oculto aparece. Un estándar de lenguaje promete cierto comportamiento, permite más y no dice nada del resto. Esta guía pregunta: **¿qué se promete, qué depende del anfitrión y qué es un precipicio de rendimiento?** El libro etiqueta cada lección con una de tres etiquetas, y esta guía te enseña a *elegir* la etiqueta según la evidencia que puedas producir.

Cuando termines, deberías poder:

1. Definir el comportamiento garantizado, el permitido por la implementación y el aprovechado por accidente, y dar un ejemplo de cada uno tomado de las entradas.
2. Decir qué evidencia respalda cada etiqueta: una especificación, una implementación probada, una observación.
3. Predecir qué ocurre cuando un programa que depende de una implementación se ejecuta en otra, y decir si el fallo será ruidoso o silencioso.
4. Reconocer un precipicio de rendimiento (retroceso, volver a enumerar, copias repetidas) y decir qué entrada lo dispara.
5. Explicar qué puede demostrar una comprobación de reproducibilidad y qué no.
6. Aplicar la ley de Hyrum a una función que nadie prometió y decir qué dejarías por escrito.

**Límites del alcance.** La guía trata de *afirmaciones*: cómo formularlas y comprobarlas. No enseña el funcionamiento interno de los compiladores ni la teoría de la complejidad. Su capítulo de origen es [Fugas de abstracción y dependencia de la implementación](../../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md).

## Antes de empezar

**Modelo de seguridad.** Las tarjetas son datos ficticios marcados con **DEMO ONLY**. Los programas pueden escribir en archivos o bases de datos locales de prueba y pueden iniciar procesos. Lee primero el código fuente y ejecútalo antes en un entorno aislado (*sandbox*) que limita el acceso al sistema anfitrión, por ejemplo `sandbox/container/run-image.sh src/awk-weird`. Trabaja con copias ([Ejecutar cosas con seguridad](../../exercises.md#ejecutar-con-seguridad)). Nunca ejecutes un experimento descontrolado fuera de un límite de tiempo: usa `SANDBOX_TIMEOUT=30`, y no ejecutes `awk-weird` con mawk en `/dev/urandom`.

**Regla de predicción.** Por cada afirmación que hagas, escribe la evidencia que demostraría que es *falsa*. Una afirmación sin esa evidencia es una esperanza.

**Vocabulario.**

| Término | Significado aquí |
| --- | --- |
| Garantizado | Una especificación o una semántica documentada lo promete. |
| Permitido por la implementación | Una implementación, plataforma o versión lo permite. |
| Aprovechado por accidente | Funciona; nadie lo prometió. |
| Ley de Hyrum | Con suficientes usuarios, alguien dependerá de cada comportamiento observable de un sistema. |
| Precipicio de rendimiento | Una entrada en la que el costo pasa de pequeño a enorme. |

## El reto compartido

La [especificación del reto](../../introduccion.md#qué-hace-el-reto) pide tarjetas con una categoría y de 10 a 19 horas enteras. Las categorías se repiten en ciclo: `Meetings`, `Coding`, `Debugging` y `Learning`. Suma las horas de cada tarjeta al total acumulado. Detente cuando el total pasa de 40. Conserva la **primera tarjeta con la que el total pasa de 40**. Un total de exactamente 40 continúa. Cuatro tarjetas de 10 horas necesitan una quinta tarjeta, de la categoría `Meetings`. Las ejecuciones conformes tienen de 3 a 5 tarjetas y un total de 41 a 59 horas.

Para un lector atento a la portabilidad, las entradas esconden dependencias del anfitrión en el reloj, la fuente de aleatoriedad, el almacenamiento y la cadena de herramientas. Averigua cuáles usa de verdad tu entrada. Las semanas fijas de LINQ no necesitan valores aleatorios. Los ejemplos de C con PCRE2 y de expresiones regulares de .NET necesitan una ruta TSV con permiso de escritura. El verificador compartido `lessons/tools/check-demo.sh` comprueba el informe numérico de las ejecuciones que implementan el reto.

## La máquina que hay que identificar

Desde la portabilidad, las cinco preguntas pasan a ser preguntas sobre *dependencias*.

**Qué se repite.** La misma dependencia, muchas veces: la fuente de aleatoriedad y el reloj. La mayoría de las entradas llama a `date +%G-W%V` o a un equivalente, así que la semana ISO es una consulta repetida al anfitrión. La entrada de Make lee `/proc` en lugar de llamar a `date`, y las de COBOL y JavaScript la calculan con aritmética.

**Dónde vive el estado.** En el anfitrión: variables de entorno (`XDG_DATA_HOME`, `HOME`), el reloj, `/dev/urandom`, el sistema de archivos. Una semilla fija (`SEED`, `-Dtc_seed`, `--seed`, `DICE`) pasa la aleatoriedad a quien llama.

**Qué hace avanzar el paso siguiente.** En un programa portable, el lenguaje. En uno que depende del anfitrión, una *función de una sola implementación*. Son estas: el reinicio de GNU Make, el punto de control de GNU tar, `RT` de gawk, `ALTER` de GnuCOBOL, los *callouts* de PCRE2.

**Qué lo detiene.** La regla de parada suele ser portable. Los modos de fallo no: una función ausente puede detener el programa de forma ruidosa o dejar que termine con la respuesta equivocada.

**Qué confirma.** Revisa la dependencia de almacenamiento antes de predecir el fallo. Una entrada que llama al comando `sqlite3` lo necesita en el anfitrión; una biblioteca SQLite enlazada o un simple escritor de TSV tiene otro límite de fallo.

## Traza una ejecución

Aquí van las mismas tres tarjetas, 15, 19 y 12, producidas por *implementaciones distintas del mismo algoritmo*, para mostrar qué promete un nombre y qué no.

| Entrada | Generador | Entrada de datos fijada | Horas |
| --- | --- | --- | --- |
| `javascript`, `javascript-weird`, `javascript-events` | Park-Miller (48271), horas `10 + state % 10` | `SEED=1105` | 15, 19, 12 |
| `tar-gnu-weird` | Park-Miller (48271), misma extracción | `--seed 1105` | 15, 19, 12 |
| `m4` | Park-Miller (16807), truco de Schrage, horas `10 + seed / 1024 % 10` | `-Dtc_seed=230` | 15, 19, 12 |
| `ed-weird`, `ex-weird` | ninguno: el lanzador aporta cinco dígitos | `DICE="5 9 2 0 0"` | 15, 19, 12, 10, 10 |
| `tar-gnu` | el constructor escribe las horas | `--hours "15 19 12 10 10"` | 15, 19, 12 |
| `regex-sed` | un registro de desplazamiento de 16 bits | la semilla del README da 15, 14, 14 | no 15, 19, 12 |

Cada fila se ejecutó en el entorno aislado o en una carpeta de prueba. Dos de ellas se llaman "Park-Miller" y *no* son iguales: el multiplicador difiere (48271 frente a 16807) y también la forma de tomar un dígito del estado. La semilla de m4 que da 15, 19, 12 es 230 y la de JavaScript es 1105. "El mismo generador" es una afirmación sobre un *nombre*. La única promesa portable es la que pruebas: la misma semilla da las mismas tarjetas *en el mismo programa*.

**Dónde falla en silencio la portabilidad.** Tres hechos, tomados de un ejercicio verificado y de los README de las propias entradas:

- Ejecuta `awk-weird` con **mawk** sobre un archivo finito de dígitos: `# committed total=0 entries=0`, sin error, estado de salida 0 (B13). mawk no tiene `RT`, así que omite cada registro.
- Ejecuta el script de ed con **busybox ed**: no puede ejecutarlo, y la comprobación de la entrada lo dice. Ese es el fallo *ruidoso*.
- Ejecuta `tar-gnu` con **tar de BSD o macOS**: no existe `--to-command`, así que falla. También es ruidoso.

**Exactamente 40.** El límite es una prueba de portabilidad de la *especificación*. Una entrada que lo ignoraba coincidía con las demás en 9 999 de 10 000 ejecuciones. Eran cuatro nombres: las entradas de regex y con encabezado `for` hasta que se corrigieron. Una afirmación de "el mismo reto" valía para la mayoría de las ejecuciones y fallaba en el borde. Un conjunto de pruebas que muestrea ejecuciones aleatorias casi nunca lo encuentra. Forzar el borde sí: el `check.sh` de cada entrada corregida ahora construye una variante con todas las tarjetas de 10 horas. `xaml` sigue teniendo el límite de cuatro tarjetas.

## Compara los diseños ordinarios y los raros

| Dimensión | Entradas idiomáticas | Entradas raras |
| --- | --- | --- |
| **Representación** | Funciones estándar del lenguaje | Una función de una sola implementación, o un uso que nadie prometió |
| **Observabilidad** | Los diagnósticos del estándar | Las mediciones del propio README: "probado en GNU tar 1.34 y 1.35" |
| **Pruebas** | Comprueban el resultado | Comprueban el resultado *y* la restricción (palabras prohibidas, una sola cuenta de `ALTER`, una mutación que debe cambiar el comportamiento) |
| **Debugging** | Estándar | La pregunta "¿esto falla con ruido o en silencio?" |
| **Portabilidad** | Amplia | Estrecha; el README dice cuánto |
| **Costo** | Normal | Un precipicio puede ser el propósito |

La clave `assurance` del README de cada entrada registra la dependencia más débil del mecanismo. El código fuente, los manuales y las pruebas respaldan las afirmaciones individuales.

| Recuento de garantías | Entradas |
| --- | --- |
| **17** entradas tienen el grado garantizado | Las versiones portadas, las entradas de LINQ, COBOL simple, Haskell, Forth, Lisp y awk, las entradas de JavaScript y `regex-dotnet`. |
| **16** tienen el grado permitido por la implementación | APL, `awk-weird`, `cobol-weird`, `forth-weird`, `haskell-weird`, `lisp-weird`, `m4`, `regex-perl`, `regex-pcre2`, `regex-pcre2grep`, las dos entradas de tar, Tcl, `tcl-weird` y `ex-weird`. |
| **7** tienen el grado aprovechado por accidente | `cmake`, `ed-weird`, `find-gnu`, `find-posix`, `make-gnu`, `regex-sed` y `xaml`. |

Una versión anterior de `tcl-weird` dependía del orden de evaluación de SQLite. La entrada actual sortea las horas en una tabla.

## Qué demuestran los ejercicios

| Ejercicio | Predice primero | Qué muestra la evidencia |
| --- | --- | --- |
| [B13. AWK: el RT que falta](../../exercises.md#b13-awk-el-rt-que-falta-verificado) | Ejecuta con mawk sobre un archivo finito. | Cero tarjetas, estado de salida 0: un fallo silencioso de código que "parece portable". `RT` es permitido por la implementación. |
| [B4. Make: quita la operación nula y anula el reloj](../../exercises.md#b4-make-quita-la-operación-sin-efecto-y-sobrescribe-el-reloj-verificado), paso 2 | `make NOW=1700000000`: ¿qué semana ISO? | `2023-W46`, que coincide con `date -u`. Un reloj que se puede fijar se puede probar. |
| [B20. JavaScript](../../exercises.md#b20-javascript-lee-las-cláusulas-mueve-el-límite-y-haz-fallar-la-comprobación-de-estructura-verificado), paso 4 | `NOW=2026-12-31` y `NOW=2024-12-30`: ¿qué semana? | `2026-W53` y `2025-W01`. El año ISO puede diferir del año del calendario cerca de Año Nuevo. |
| [B15. GNU find: mueve la regla de parada, lee el perfil](../../exercises.md#b15-gnu-find-mueve-la-regla-de-parada-lee-el-perfil-verificado) | `FIND_D=rates`: ¿qué imprime find? | Una tasa de éxito real para cada prueba; la estimación del propio find está muy lejos. La estimación de un optimizador no es el comportamiento. |
| [B17. tar, más raro: predice el reloj](../../exercises.md#b17-tar-más-raro-predice-el-reloj-verificado) | Predice los tics de `--interval 2`. | `floor(records / K)`. Una regla medida en GNU tar y luego predicha por una simulación. |
| [F. Demuestra una afirmación del README](../../exercises.md#f-demuestra-una-afirmación-del-readme-verificada) | ¿Puedes hacer que la afirmación falle? | Un control negativo separa una afirmación de una observación. |

## Modos de fallo, costos y límites

| Comportamiento | Etiqueta | Por qué |
| --- | --- | --- |
| `Word64` da la vuelta al desbordarse (generador de Haskell) | **garantizado** | Documentado. |
| El error de tamaño de COBOL deja el campo sin cambios | **garantizado** | Especificado. |
| El desbordamiento sin tratar de COBOL descarta el dígito inicial | **permitido por la implementación** | La compilación probada; el estándar no promete ningún resultado utilizable. |
| `ALTER` | **permitido por la implementación** | Eliminado del estándar en 2002; GnuCOBOL todavía lo ejecuta. |
| El `eval` de m4 es de 32 bits | **permitido por la implementación** | GNU m4 1.4.x. `2147483647*4` da `-4` en silencio. |
| Las funciones de devolución de llamada de los puntos de control de GNU tar y su conteo de registros | **permitido por la implementación** | Opciones documentadas de GNU. Los conteos se midieron en 1.34 y 1.35. |
| Listar un archivo tar da una cuenta de tics distinta de la de crearlo | conocimiento **aprovechado por accidente** | Tar omite los datos que no necesita leer. Nadie lo promete. |
| `find -exec` de POSIX sustituye `{}` como argumento completo | **garantizado** dentro de la sintaxis POSIX | POSIX deja sin especificar la sustitución dentro de un argumento más largo, como `{}/b09`; GNU find 4.9, bfs 3.1.2 y busybox 1.36.1 la hacen en la entrada probada. |
| `find-posix` visita un directorio creado mientras el recorrido está en curso | **aprovechado por accidente** | Observado en esas mismas tres implementaciones. POSIX no promete nada sobre el recorrido cuando algo cambia durante él. Esta es la dependencia más débil y determina la etiqueta del README. |
| Los grupos de equilibrio de .NET quitan una captura de otro grupo | **garantizado** dentro de la API documentada de .NET | El motor de .NET lo documenta. La garantía vale para ese motor y no promete portabilidad a otras implementaciones de expresiones regulares. |
| La función de script de *callout* `pcre2grep` | **permitido por la implementación** | Una opción de compilación. El `pcre2grep` propio de Ubuntu no la tiene. |
| El reinicio de Make usado como bucle | **aprovechado por accidente** | Ley de Hyrum: una función usada para algo para lo que no fue hecha. |
| Una expresión regular de sed usada como reloj | **aprovechado por accidente** | Un precipicio de rendimiento; varía según la CPU. |

**Costos que declarar.**

- **Precipicios de rendimiento.** Una expresión regular rápida en todas las pruebas puede tardar un año con una sola entrada de datos mala. La entrada de sed usa un patrón catastrófico como reloj de 50 ms. La expresión regular de CMake no tiene repetición contada, así que escribir "como máximo 40" como cuarenta grupos opcionales retrocedería de forma exponencial al fallar. Volver a enumerar en LINQ multiplica los efectos. m4 copia su script SQL creciente en cada tarjeta. Consulta [Denegación de servicio mediante expresiones regulares](../../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#denegación-de-servicio-mediante-expresiones-regulares) y [Precipicios de rendimiento y complejidad temporal](../../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#precipicios-de-rendimiento-y-complejidad-temporal).
- **La reproducibilidad tiene límites.** Un reloj fijo y una semilla fija hacen repetible una ejecución. No prueban nada sobre otro anfitrión. `NOW` de Make, `NOW` de JavaScript y `SEED` y `SOURCE_DATE_EPOCH` de la compilación del libro fijan cada uno una entrada. El PDF y el EPUB del libro se reproducen byte a byte con las mismas versiones de pandoc y WeasyPrint.
- **Ley de Hyrum.** Si el README no dice qué comportamiento se promete, los usuarios dependerán del observado. Los README nombran lo que midieron; las etiquetas son la disciplina.
- **Dónde es legítimo.** Usar la extensión de una implementación es ingeniería corriente si dejas por escrito que lo hiciste. El riesgo no es la extensión, es el silencio.

## Conexiones a lo largo del repositorio

- **Guías de lenguaje.** [COBOL](../lenguajes/cobol.md), [Make y CMake](../lenguajes/make-y-cmake.md), [Motores de regex y sed](../lenguajes/motores-de-regex-y-sed.md), [m4](../lenguajes/m4.md), [tar](../lenguajes/tar.md) y [ed y Ex](../lenguajes/ed-y-ex.md) dan la evidencia detrás de cada etiqueta.
- **Lectura segura.** [Lectura de programas adversariales](lectura-de-programas-adversariales.md): una función ausente que falla en silencio también es una cuestión de seguridad.
- **Efectos.** [Efectos, errores y confirmación](efectos-errores-y-confirmacion.md) pregunta qué semántica de fallo se promete.
- **La comparación.** [Diseño comparado de máquinas](diseno-comparativo-de-maquinas.md) enumera cada entrada con su etiqueta.
- **En el libro.** [Abstracciones con fugas](../../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#abstracciones-con-fugas), [Comportamiento indefinido, no especificado y definido por la implementación](../../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#comportamiento-indefinido-no-especificado-y-definido-por-la-implementación), [Portabilidad](../../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#portabilidad), [Ley de Hyrum](../../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#ley-de-hyrum) y [Reproducibilidad y compilaciones deterministas](../../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#reproducibilidad-y-compilaciones-deterministas).

## Autoevaluación

Responde cada pregunta con tus propias palabras antes de leer el texto en cursiva. Di qué evidencia respaldaría cada respuesta.

1. **Traza.** `m4 -Dtc_seed=230` y `SEED=1105 node ...` dan las horas 15, 19, 12. ¿Se deduce que los dos programas comparten un generador? *(No. Ambos usan una recurrencia de Park-Miller, pero con multiplicadores distintos y distinta extracción de dígitos. Las semillas se encontraron por separado. Una salida igual con una semilla es una coincidencia de la búsqueda.)*
2. **Explica.** ¿Por qué es mejor un fallo de portabilidad ruidoso que uno silencioso, y cuál da mawk con `awk-weird`? *(Un fallo ruidoso te detiene antes de que confíes en un resultado equivocado. mawk da uno silencioso: cero tarjetas, estado de salida 0.)*
3. **Transfiere.** Dependes de `date +%G-W%V` en un script. ¿Qué etiqueta le das a esa dependencia y qué dejarías por escrito? *(Permitido por la implementación: GNU `date` y los compatibles. Escribe la herramienta, la versión mínima y qué hace el año ISO cerca de Año Nuevo.)*
4. **Evidencia.** Un README dice: "GNU tar cuenta 21 tics al crear un archivo de 21 bloques." Diseña una prueba que pueda fallar. ¿Qué etiqueta se aplica a la afirmación? *(Crea archivos de varios tamaños, factores de bloqueo e intervalos y compara la cuenta de tics de tar con `floor(ceil(blocks / b) / K)`. El control negativo es listar el archivo, que da otra cuenta. La afirmación tiene la etiqueta permitido por la implementación, y el comportamiento al listar es conocimiento aprovechado por accidente.)*

## Lecturas adicionales

- [Portabilidad del software](https://en.wikipedia.org/wiki/Software_portability) (Wikipedia): qué hace que el software se mueva entre plataformas.
- [Comportamiento indefinido](https://en.wikipedia.org/wiki/Undefined_behavior) (Wikipedia): el caso más fuerte de "nadie lo prometió".
- [Ley de Hyrum](https://en.wikipedia.org/wiki/Hyrum%27s_law) (Wikipedia): por qué el comportamiento observable se vuelve un contrato.
- [Compilaciones reproducibles](https://en.wikipedia.org/wiki/Reproducible_builds) (Wikipedia): qué puede demostrar una entrada fija.
- [Denegación de servicio mediante expresiones regulares](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) (OWASP): cómo un precipicio se vuelve un ataque.
