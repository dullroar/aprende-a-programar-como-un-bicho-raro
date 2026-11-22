# Guías de estudio

*Trazas, predicciones y evidencia para lectores avanzados de* ¡Aprende a programar como un bicho raro!

**BICHO** significa **Bicho raro, Interpreta, Camino indirecto, Hallazgos y Octetos**. La B es recursiva. El resto te da algo que trazar: qué se ejecuta, dónde aparece el resultado y qué trata el programa como datos sin que nadie lo note.

Muchos capítulos de lenguajes emparejan un programa idiomático con uno raro. Estas guías dan el paso siguiente. Para cada familia de lenguajes y cada idea, una guía te pide **identificar la máquina, trazar una ejecución fija, predecir antes de ejecutar y probar la afirmación con evidencia**. Las escribimos para un lector avanzado de licenciatura o de posgrado. No enseñan qué es un bucle. Enseñan por qué *esta* máquina parecida a un bucle tiene consecuencias particulares.

Las guías están escritas a mano. Empezaron con una guía de estudio de COBOL de Ken Astl, coautor del libro. Conservan su método.

## Cómo funciona cada guía

Cada guía tiene las mismas once secciones, así que encuentras cada cosa siempre en el mismo lugar:

1. **Para qué sirve esta guía**: de tres a seis resultados de aprendizaje, y lo que queda fuera del ámbito de la guía.
2. **Antes de empezar**: el modelo de seguridad (datos ficticios marcados con **DEMO ONLY**, revisión del código y una ejecución en el entorno aislado), la regla de predicción y el vocabulario.
3. **El reto compartido**: la [especificación de la tarjeta de horas](../introduccion.md#qué-hace-el-reto) y cómo se comportan las entradas de esta guía. Una ejecución conforme conserva la **primera tarjeta que lleva el total a más de 40**, así que un total de exactamente 40 continúa. Comprueba por separado la parada, el almacenamiento y la salida.
4. **La máquina que hay que identificar**: lo que se repite, dónde vive el estado, lo que hace avanzar el paso siguiente, qué lo detiene y qué efectos se confirman.
5. **Traza una ejecución**: una ejecución fija, normalmente con las horas 15, 19, 12, con el estado decisivo antes y después de cada paso.
6. **Compara los diseños ordinarios y los raros**: por representación, observabilidad, pruebas, depuración, portabilidad y costo, no por número de líneas.
7. **Qué demuestran los ejercicios**: enlaces a los ejercicios verificados, cada uno con la predicción que haces primero.
8. **Modos de fallo, costos y límites**: afirmaciones concretas sobre el comportamiento. Se marcan como **garantizado**, **permitido por la implementación** o **aprovechado por accidente**, con evidencia para cada una (consulta [Tres tipos de conocimiento](../introduccion.md#tres-tipos-de-conocimiento)).
9. **Conexiones a lo largo del repositorio**: otras guías y capítulos del libro.
10. **Autoevaluación**: una pregunta de traza, una de explicación, una de transferencia y una de evidencia.
11. **Lecturas adicionales**: breves y comentadas.

**Cómo se comprobaron las trazas.** Una traza solo sirve si es verdadera. En la mayoría de las guías se ejecutó una copia de trabajo de la entrada real en el entorno aislado. Los números aleatorios iban fijados (por ejemplo `SEED=1105`, `DICE="5 9 2 0 0"`, `-Dtc_seed=230`, `--hours "15 19 12 10 10"`). Se añadieron unas líneas de bitácora para mostrar el estado. Una guía lo dice cuando una traza solo se leyó del código fuente, como en las entradas de WPF, que solo funcionan en Windows.

## Guías por familia de lenguajes

| Guía | Entradas | Qué plantea |
| --- | --- | --- |
| [C#, LINQ, XAML y adaptaciones](lenguajes/csharp-linq-xaml-y-adaptaciones.md) | `ModernChallenge1`, `LinqChallenge1`, `LinqChallenge2`, `xaml` y las adaptaciones a Go, Java, Kotlin, Python y Rust | ¿Qué hace cada ranura del encabezado `for`, cuándo se ejecuta una consulta y quién es dueño del hilo? |
| [COBOL](lenguajes/cobol.md) | `cobol`, `cobol-weird` | ¿Dónde guarda un programa "lo que pasa después" y "cuándo parar"? |
| [Haskell](lenguajes/haskell.md) | `haskell`, `haskell-weird` | ¿Quién ejerce la demanda de trabajo y qué pasa cuando se mueve un punto donde se debe forzar? |
| [Forth](lenguajes/forth.md) | `forth`, `forth-weird` | ¿Qué puede servir de contador de programa y qué puede servir de memoria? |
| [Make y CMake](lenguajes/make-y-cmake.md) | `make-gnu`, `cmake` | Cuando la herramienta decide qué se ejecuta después, ¿dónde vive el estado del programa? |
| [Motores de regex y sed](lenguajes/motores-de-regex-y-sed.md) | `regex-perl`, `regex-pcre2`, `regex-pcre2grep`, `regex-dotnet`, `regex-sed` | ¿Qué motores conservan los efectos después de un fallo y cuáles necesitan una coincidencia exitosa? |
| [APL](lenguajes/apl.md) | `apl`, `apl-weird` | ¿Qué reemplaza al bucle cuando el programa trabaja con arreglos completos o con su propio código fuente? |
| [JavaScript](lenguajes/javascript.md) | `javascript`, `javascript-weird`, `javascript-events` | ¿Quién es dueño del paso siguiente: el encabezado del bucle, el consumidor o el bucle de eventos? |
| [Common Lisp](lenguajes/common-lisp.md) | `lisp`, `lisp-weird` | ¿Pueden las reglas de despacho del sistema de objetos servir de bucle y de regla de parada? |
| [m4](lenguajes/m4.md) | `m4` | ¿Qué deciden las comillas, el orden de expansión y el reescaneo? |
| [Tcl](lenguajes/tcl.md) | `tcl`, `tcl-weird` | Si el código es solo una cadena de texto, ¿quién puede escribirlo y qué motor se ejecuta después? |
| [ed y Ex](lenguajes/ed-y-ex.md) | `ed-weird`, `ex-weird` | Cuando el programa es un búfer que se edita, ¿cuáles son las direcciones, los registros y el contador de programa? |
| [tar](lenguajes/tar.md) | `tar-gnu`, `tar-gnu-weird` | Un archivo comprimido es un dato. ¿Qué le da un efecto y qué hace seguro leerlo? |

## Guías de conceptos

| Guía | Capítulos del libro | Pregunta central |
| --- | --- | --- |
| [Lectura de programas adversariales](conceptos/lectura-de-programas-adversariales.md) | [1](../informatica/01-lectura-de-un-programa-adversarial.md) | ¿Qué puede causar este programa antes de que lo ejecute? |
| [Estado y control más allá de las variables](conceptos/estado-y-control-mas-alla-de-las-variables.md) | [2](../informatica/02-que-cuenta-como-maquina.md), [3](../informatica/03-flujo-de-control-y-continuaciones.md), [6](../informatica/06-estado-mas-alla-de-las-variables.md) | ¿Dónde se guardan el paso siguiente y el estado recordado? |
| [Evaluación, demanda y pereza](conceptos/evaluacion-demanda-y-pereza.md) | [4](../informatica/04-evaluacion-y-demanda.md) | ¿Quién exige el trabajo y cuándo? |
| [Lenguajes formales y máquinas raras](conceptos/lenguajes-formales-y-maquinas-raras.md) | [5](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md) | ¿Cuándo se convierte una notación en un sustrato ejecutable? |
| [Efectos, errores y confirmación](conceptos/efectos-errores-y-confirmacion.md) | [7](../informatica/07-efectos-errores-y-confirmacion.md) | ¿Qué efectos sobreviven a un fallo y qué se confirma de verdad? |
| [Portabilidad, abstracción y costo](conceptos/portabilidad-abstraccion-y-costo.md) | [8](../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md) | ¿Qué está prometido, qué depende del anfitrión y qué es un precipicio de rendimiento? |
| [Eventos, funciones de devolución de llamada y control reactivo](conceptos/eventos-retrollamadas-y-control-reactivo.md) | [10](../informatica/10-eventos-retrollamadas-y-flujo-de-control-reactivo.md) | ¿Quién es dueño del turno siguiente y qué cambia la reentrada? |
| [Diseño comparativo de máquinas](conceptos/diseno-comparativo-de-maquinas.md) | [9](../informatica/09-casos-de-estudio-comparativos.md), [patrones](../patrones.md) | ¿Qué hace de bucle, de estado, de reloj, de decisión y de confirmación? |

`find` y AWK no tienen una guía propia. Aparecen en las guías sobre [lectura de programas adversariales](conceptos/lectura-de-programas-adversariales.md), [estado y control](conceptos/estado-y-control-mas-alla-de-las-variables.md) y [diseño comparativo de máquinas](conceptos/diseno-comparativo-de-maquinas.md).

## Rutas sugeridas

- **Desde un lenguaje que conoces.** Abre su guía, traza la ejecución fija, haz tus predicciones y ejecuta el ejercicio enlazado. Vuelve después a la página del libro con el mismo nombre.
- **Desde una idea.** Empieza con una guía de conceptos. Sus tablas de traza comparan varios lenguajes a la vez, y cada fila enlaza a la guía que la comprobó.
- **En orden.** Lee primero [Lectura de programas adversariales](conceptos/lectura-de-programas-adversariales.md). Es el modelo de seguridad de todo lo demás.

Vuelve a las [lecciones](../README.md) y al [reto](../../README.md).
