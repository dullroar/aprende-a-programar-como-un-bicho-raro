# Guía de estudio de lenguajes formales y máquinas raras

## Para qué sirve esta guía

Una notación se crea para un trabajo. Una expresión regular busca texto, un Makefile ordena una compilación, XAML describe una ventana, `ed` edita un búfer y tar empaqueta archivos. La sorpresa recurrente del repositorio es que cada una de ellas también resulta ser una computadora. Esta guía pregunta: **¿cuándo se convierte una notación en un sustrato ejecutable y cuánta máquina necesita cada una?**

Cuando termines, deberías poder:

1. Ubicar una notación en la jerarquía de Chomsky. Decir qué poder extra convierte un buscador en una computadora: una pila, un contador, bloques de código, callouts, un bucle de reescritura o un reinicio.
2. Explicar por qué una coincidencia de una expresión regular siempre termina y un bucle de sustituciones puede no terminar. Explicar por qué eso importa para lo que pueden afirmar las entradas.
3. Describir el *sustrato* de cada entrada: cuál es su alfabeto, cuáles son sus reglas y qué hace de memoria.
4. Explicar "máquina rara" (*weird machine*): la computación que un procesador de entradas realiza más allá de lo que sus autores previeron. Explicar "seguridad basada en teoría de lenguajes" con un ejemplo de las entradas. Decir qué debería hacer quien defiende.
5. Decir qué no puede hacer cada máquina, con evidencia: el antiguo techo de cuatro nombres, la repetición contada que falta, el `Match` fallido de .NET que no expone nada.
6. Etiquetar afirmaciones como garantizado, permitido por la implementación o aprovechado por accidente.

**Límites del alcance.** La guía trata de la *relación entre una notación y la máquina que puede expresar*. No es un curso de teoría de autómatas: nombra los niveles y los usa. Su capítulo de origen es [Lenguajes formales como sustratos computacionales](../../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md).

## Antes de empezar

**Modelo de seguridad.** Las tarjetas son datos ficticios marcados con **DEMO ONLY**. Aquí una notación puede causar efectos mediante Perl en un patrón, C en un callout, Tcl leído de una tabla o métodos de .NET invocados por XAML. Lee primero el código fuente y ejecútalo antes en un entorno aislado (*sandbox*) que limita el acceso al sistema anfitrión, por ejemplo `sandbox/container/run-image.sh src/regex-sed`. Trabaja con copias y ejecuta cualquier experimento con sed o con una expresión regular en una carpeta temporal ([Ejecutar cosas con seguridad](../../exercises.md#ejecutar-con-seguridad)).

**Regla de predicción.** Antes de cada ejecución, escribe qué puede *representar* la notación y qué no. Después mira si el programa chocó con ese límite.

**Vocabulario.**

| Término | Significado aquí |
| --- | --- |
| Lenguaje formal | Un conjunto de cadenas de texto definido por reglas estrictas que una máquina puede procesar. |
| Jerarquía de Chomsky | Una escalera de clases de lenguajes según la máquina que necesitan: regular, libre de contexto, sensible al contexto y recursivamente enumerable. |
| Sustrato | La notación junto con su motor, usada como una máquina. |
| Máquina rara | La computación que un procesador de entrada de datos realiza *más allá* de lo que sus autores previeron. |
| Seguridad basada en teoría de lenguajes | La idea de que un lenguaje de entrada de datos más potente de lo que creían sus autores convierte leer la entrada en ejecutar un programa. |

## El reto compartido

La [especificación del reto](../../introduccion.md#qué-hace-el-reto) pide tarjetas con una categoría y de 10 a 19 horas enteras. Las categorías se repiten en ciclo: `Meetings`, `Coding`, `Debugging` y `Learning`. Suma las horas de cada tarjeta al total acumulado. Detente cuando el total pasa de 40. Conserva la **primera tarjeta con la que el total pasa de 40**. Un total de exactamente 40 continúa. Cuatro tarjetas de 10 horas necesitan una quinta tarjeta, de la categoría `Meetings`. Las ejecuciones conformes tienen de 3 a 5 tarjetas y un total de 41 a 59 horas.

Para un lector de lenguajes formales, el reto exige dos capacidades: *contar* (comparar un total con 40) y *repetir con memoria* (llevar el total a la tarjeta siguiente). Una expresión regular pura no tiene ninguna. Cada entrada de esta guía las aporta tomando algo prestado: una pila, marcas de conteo, un reinicio o un anfitrión. El límite es exacto: un total de 40 debe *continuar*, así que la máquina debe distinguir 40 de 41.

## La máquina que hay que identificar

Para cada entrada, pregunta qué hace cada papel.

**Qué se repite.** En un sustrato de *búsqueda* (Perl, PCRE2, pcre2grep, .NET), un cuantificador sobre un patrón: el motor explora caminos. En un sustrato de *reescritura* (sed, m4, ed), un bucle que aplica reglas hasta que ninguna coincide. En un sustrato de *reinicio* (Make), el motor se vuelve a ejecutar a sí mismo. En un sustrato de *análisis sintáctico* (XAML), un recorrido del documento.

**Dónde vive el estado.** En una pila de capturas (.NET: `b` es el presupuesto y `s` es el total), en el propio texto (sed: marcas `#`; ed: marcas `x`). También en capturas reconstruidas en cada pasada (CMake), en el anfitrión (una estructura de C para PCRE2, SQLite para pcre2grep) o en archivos (Make).

**Qué hace avanzar el paso siguiente.** El control propio del motor: el retroceso, el bucle de reescritura, el reinicio o el analizador sintáctico.

**Qué lo detiene.** Un patrón que falla (`(?!)`) o que deja de coincidir (`/ tot:#{41}/`). Una regla que no escribe nada (Make). Un literal de cierta longitud (CMake). Un suministro finito (cuatro nombres, cinco dados).

**Qué confirma.** El patrón de .NET debe devolver una coincidencia exitosa para que su anfitrión obtenga las capturas de las tarjetas para el TSV. Los callouts de PCRE2 escriben el TSV durante la coincidencia y los bloques de código de Perl escriben en SQLite. Esos efectos sobreviven a una coincidencia final fallida.

## Traza una ejecución

Así se ven tres tarjetas, de 15, 19 y 12 horas, en cuatro sustratos. Cada una se verificó ejecutando una copia de prueba.

| Sustrato | Representación del total después de la tarjeta 2 | Prueba de parada en la tarjeta 3 | Qué hace el motor al final |
| --- | --- | --- | --- |
| Regex de .NET | 7 fichas restantes en la pila del presupuesto `b` y 34 en la pila del total `s` | `(?(b)...\|(?!))`: `b` queda vacía tras la tarjeta 3, así que `(?!)` hace fallar la pasada | la coincidencia *tiene éxito*; el anfitrión lee las capturas |
| Callouts de PCRE2 | `total=34` en una estructura de C | el callout `gate` devuelve 1 para `total=46` | `(*COMMIT)` y luego `(*FAIL)`: la coincidencia devuelve "sin coincidencia" después de todo el trabajo |
| sed | `tot:` seguido de 34 marcas `#` en una línea | `/ tot:#{41}/` coincide (43 marcas en la ejecución basada en semilla) | `b done`; sed termina con estado 1 a propósito |
| CMake | `M1`: 15 `x`, `M5`: 19 `x` | `NOT` (46 `x` coinciden con el literal de 41 `x`) | el bucle termina, pero la coincidencia principal ya se ejecutó |

Lee la segunda fila: un patrón de PCRE2 que "falla" es el *éxito* del programa, porque los efectos sobrevivieron. En la primera fila ocurre lo contrario: el patrón debe tener éxito, porque una coincidencia fallida de .NET no expone nada.

**Lo que la notación no puede hacer.** La entrada de .NET no puede generar números aleatorios ni escribir un archivo. Por eso el anfitrión construye una cinta de cinco campos unarios y añade el informe a partir de las colecciones de capturas. La entrada de sed no tiene números en absoluto, así que un generador aleatorio es una cadena de texto de 16 caracteres de `0` y `1`. La regex de CMake no tiene repetición contada, ni anticipación, ni referencias hacia atrás. Por eso la prueba de parada es un literal de 41 `x` y un patrón parametrizado por un registro es la única forma de consultar algo.

**Exactamente 40.** Un sustrato puede expresar "continúa con 40" solo si distingue 40 de 41. Un presupuesto de 41 fichas, un literal de 41 marcas y una línea de cinta para 40 lo logran. Pero el *suministro* es finito en varios: los nombres de categoría en un asunto, una lista `cats:` y las pasadas desenrolladas de XAML. Con cuatro nombres, una ejecución de cuatro tarjetas de 10 horas terminaba con un total de exactamente 40, que el verificador compartido rechaza. La notación era lo bastante potente para *contar* hasta 41 y no lo bastante para *suministrar* un quinto nombre. Las entradas de regex ahora llevan cinco nombres y lo demuestran en sus verificaciones; `xaml`, con cuatro pasadas desenrolladas, aún tiene el límite.

## Compara los diseños ordinarios y los raros

| Dimensión | Notación usada como se pensó | Notación usada como máquina |
| --- | --- | --- |
| **Representación** | Un patrón, un grafo de compilación, un árbol de interfaz | El mismo texto, más los efectos secundarios del motor |
| **Observabilidad** | Coincidencia, compilación, renderizado | El estado está en capturas, marcas o archivos: `TRACE=1` en sed imprime toda la máquina |
| **Pruebas** | Probar con entradas de datos | Una segunda implementación lo predice (la simulación con awk de tar) o una mutación demuestra que la regla es real (el literal de 41 `x` cambiado a 51) |
| **Debugging** | Los diagnósticos propios de la herramienta | Una operación nula silenciosa: un `s` fallido, una coincidencia fallida, una receta que se expande a nada |
| **Portabilidad** | Una notación estándar | Una extensión de un motor: los callouts de PCRE2, el `(?{ })` de Perl, los intervalos `T` y `-E` de GNU sed, el `RT` de gawk |
| **Costo** | Normal | El retroceso puede ser catastrófico; la entrada de sed lo usa como reloj |

**Una coincidencia frente a un bucle de sustituciones.** Una sola coincidencia de regex, con una entrada de datos fija y sin ganchos de código, siempre termina: el motor prueba un número acotado de caminos. Las entradas que usan *búsqueda con retroceso* están explorando y abandonan ramas. Un programa de sed que reescribe una cadena de texto una y otra vez es un modelo distinto: un sistema de reescritura. Un bucle de sustituciones puede ejecutarse para siempre. Por eso la regla de parada de la entrada de sed debe ser real. Por eso los scripts de ed y Ex mantienen una cota (cinco dados, una cinta de 60 líneas).

## Qué demuestran los ejercicios

| Ejercicio | Predice primero | Qué muestra la evidencia |
| --- | --- | --- |
| [B8. Regex: qué sobrevive a una coincidencia fallida](../../exercises.md#b8-regex-qué-sobrevive-a-una-coincidencia-fallida-verificado) | Añade `(?!)` al patrón de .NET. | `match returned: false`, `total=0 entries=0`: la única salida de la notación son sus capturas. |
| [B9. sed: observa una computación](../../exercises.md#b9-sed-observa-un-cálculo-verificado) | ¿Cuántas líneas de estado hay por tarjeta? | Muchas, no una cantidad constante: un sorteo rechazado repite un paso. Una máquina de reescritura muestra todo su estado. |
| [B5. CMake: muta el literal](../../exercises.md#b5-cmake-muta-el-literal-verificado) | Acorta a 31 el literal de 41 `x`. | La regla de parada se mueve: el literal es la regla. |
| [B11. m4: entrecomilla la recursión](../../exercises.md#b11-m4-cita-la-recursión-verificado) | Quita los corchetes. | Una ejecución desbocada: el procesador de macros expande los argumentos antes de llamar a la macro. |
| [B18. ed: mueve la regla de parada y rompe la limpieza](../../exercises.md#b18-ed-mueve-la-regla-de-parada-y-rompe-la-limpieza-verificado) | Cambia `x\{41,\}` por `x\{31,\}`. | La ejecución se detiene tras el primer total que pasa de 30. Un solo contador de repeticiones en una regex es la regla. |
| [C2. Haz real la restricción](../../exercises.md#c2-haz-real-la-restricción-verificada) | Escribe una verificación que prohíba las palabras de bucle en Forth. | Debe quitar primero los comentarios y las cadenas de texto: una verificación de restricciones es en sí un analizador sintáctico. |

## Modos de fallo, costos y límites

| Comportamiento | Etiqueta | Por qué |
| --- | --- | --- |
| Los grupos de equilibrio de .NET sacan de una pila de capturas y meten en otra | **garantizado** | Comportamiento documentado de las regex de .NET. Una pila lleva al motor más allá de los lenguajes regulares. |
| Un `Match` fallido de .NET no expone capturas | **garantizado** | Verificado en B8. |
| Los callouts de PCRE2 llaman al código del anfitrión, y un valor de retorno positivo hace fallar el camino | **garantizado** | API documentada. |
| Los callouts solo se visitan si el optimizador no los omite | **permitido por la implementación** | La entrada fija banderas y evita el JIT; no probó qué omitiría el optimizador sin ellas. |
| Los bloques de código de Perl se ejecutan durante una coincidencia, y `local` se deshace con el retroceso | **garantizado** | Perl documentado. |
| Un `MATCHES` fallido vacía los registros de CMake | **permitido por la implementación** | Observado, no prometido con esas palabras. |
| CMake evalúa los dos operandos de `AND` | **aprovechado por accidente** | Observado, y necesario para registrar la última tarjeta. |
| El `RS` de gawk como expresión regular, con `RT` | **permitido por la implementación** | Solo en gawk. mawk produce cero tarjetas en silencio (B13). |
| Una regex con retroceso en sed tarda unos 50 ms por cuadro | **aprovechado por accidente** | Un precipicio de rendimiento usado como reloj. Varía según la máquina. |
| El `XamlReader` ejecuta métodos `ObjectDataProvider` durante el análisis sintáctico | **aprovechado por accidente** | Un lenguaje de interfaz usado como intérprete. |

**Costos que debes enunciar.**

- **Seguridad basada en teoría de lenguajes.** Si un lenguaje de entrada de datos es más potente de lo que sus autores creían, leer la entrada es ejecutar un programa. El analizador sintáctico de XAML es el caso de este repositorio. La defensa es la *regla del menor poder*. Acepta el lenguaje más débil que haga el trabajo y analízalo antes de actuar sobre él ([Seguridad basada en teoría de lenguajes](../../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#language-theoretic-security)).
- **Una máquina rara está hecha de estados no previstos.** Las entradas lo hacen a propósito, en un entorno aislado, para enseñar. La tarea de quien defiende es encontrar la máquina rara antes que un atacante ([Máquinas raras](../../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#weird-machines)).
- **Límites ocultos.** Una cinta o una lista finita es un límite de diseño que, en la frontera, se comporta como un límite semántico.
- **Dónde es legítimo.** Usar una regex para *tokenizar*, una herramienta de compilación para *generar* fuentes y un procesador de macros para *configurar* es algo corriente. La acrobacia consiste en exigirle a la notación un programa completo.

## Conexiones a lo largo del repositorio

- **Las guías de lenguaje.** [Motores de regex y sed](../lenguajes/motores-de-regex-y-sed.md), [Make y CMake](../lenguajes/make-y-cmake.md), [m4](../lenguajes/m4.md), [ed y Ex](../lenguajes/ed-y-ex.md), [tar](../lenguajes/tar.md) y [C#, LINQ, XAML y adaptaciones](../lenguajes/csharp-linq-xaml-y-adaptaciones.md) trazan cada una un sustrato.
- **Estado y control.** [Estado y control más allá de las variables](estado-y-control-mas-alla-de-las-variables.md) dice dónde guarda cada sustrato su contador de programa.
- **Lectura segura.** [Lectura de programas adversariales](lectura-de-programas-adversariales.md) toma "un lenguaje de entrada de datos es un programa" como su ejemplo principal.
- **Costo.** [Portabilidad, abstracción y costo](portabilidad-abstraccion-y-costo.md) cubre el precipicio del retroceso y las extensiones de las implementaciones.
- **En el libro.** [La jerarquía de Chomsky](../../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#the-chomsky-hierarchy), [Expresiones regulares](../../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#regular-expressions), [Reescritura de términos y de cadenas de texto](../../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#term-and-string-rewriting), [Macros y expansión de texto](../../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#macros-and-text-expansion) y [Automatización de la compilación](../../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#build-automation).

## Autoevaluación

Responde cada pregunta con tus propias palabras antes de leer el texto en cursiva. Di qué evidencia respaldaría cada respuesta.

1. **Traza.** En la entrada de .NET los sorteos son 15, 19, 12 y 17. Indica las fichas del presupuesto que quedan tras cada pasada y di qué pasada termina el bucle. *(26, luego 7 y luego 0. Después de la tercera pasada `b` está vacía, así que la pasada siguiente toma `(?!)` y el bucle termina. El cuarto sorteo se ignora.)*
2. **Explica.** ¿Por qué el patrón de PCRE2 termina en `(*COMMIT)` y `(*FAIL)`, y qué hace cada uno? *(`(*COMMIT)` impide que el motor reintente bucles más cortos, así que el callout `commit` se ejecuta una vez. `(*FAIL)` hace que toda la coincidencia pierda cuando el trabajo ya está hecho, que es la jugada característica.)*
3. **Transfiere.** Nombra un lenguaje de entrada de datos de un sistema que uses que sea más potente de lo que parece y di cómo aplicarías la regla del menor poder. *(Por ejemplo un lenguaje de plantillas, una fórmula de hoja de cálculo o un formato de configuración con `include`. Reemplázalo por un formato declarado más débil o analízalo con una gramática estricta antes de actuar.)*
4. **Evidencia.** Un revisor dice: "El patrón de .NET no puede escribir una fila por sí mismo." Diseña una prueba que pueda fallar. *(Verifica que `Program.cs` tenga exactamente un `Regex.Match` y ningún `MatchEvaluator` ni `Replace`. Verifica que toda escritura de archivos esté en el código del anfitrión después de la coincidencia, que es lo que hace el `check.sh` de la entrada. El control negativo es una copia con un `MatchEvaluator`, que la verificación debe rechazar.)*

## Lecturas adicionales

- [Jerarquía de Chomsky](https://en.wikipedia.org/wiki/Chomsky_hierarchy) (Wikipedia): la escalera de clases de lenguajes.
- [Autómata de pila](https://en.wikipedia.org/wiki/Pushdown_automaton) (Wikipedia): la máquina que una pila añade a un lenguaje regular.
- [Máquina rara](https://en.wikipedia.org/wiki/Weird_machine) (Wikipedia): computación no prevista en el manejo de entrada de datos.
- [Regla del menor poder](https://en.wikipedia.org/wiki/Rule_of_least_power) (Wikipedia): por qué un lenguaje de entrada de datos más débil es más seguro.
- [Algoritmo de Markov](https://en.wikipedia.org/wiki/Markov_algorithm) (Wikipedia): el modelo formal detrás de la máquina de buscar y reemplazar de sed.
