# Plan de estudios

*Un curso de 16 semanas basado en* ¡Aprende a programar como un bicho raro!

Este plan de estudios convierte el repositorio en un semestre. Enseña informática mediante un recorrido por lenguajes e implementaciones. La mayoría son antiguos, extraños o ambas cosas. Las ideas son el tema. Los lenguajes son la evidencia.

**BICHO** significa **Bicho raro, Interpreta, Camino indirecto, Hallazgos y Octetos**. La B es recursiva. Las cinco letras también dan al curso sus cinco fases.

## Para quién es este curso

- Estudiantes avanzados de licenciatura y estudiantes de posgrado.
- Programadores autodidactas que escriben código que funciona y quieren la teoría que hay debajo.
- Lectores curiosos a quienes les gustan los acertijos.

Necesitas un lenguaje que conozcas bien, una terminal y un entorno de ejecución de contenedores. No necesitas un título universitario. No necesitas instalar COBOL, APL ni Forth. El [entorno aislado (*sandbox*)](../SANDBOX-SETUP.md) los incluye.

## Lo que podrás hacer

1. Nombra la máquina dentro de un programa: lo que se repite, dónde vive el estado, lo que hace avanzar el paso siguiente, qué lo detiene y qué confirma.
2. Lee un programa desconocido y haz una lista de lo que puede causar antes de ejecutarlo.
3. Predice una traza y luego pon a prueba la predicción con una ejecución.
4. Etiqueta una afirmación como **garantizado**, **permitido por la implementación** o **aprovechado por accidente**, y da la evidencia.
5. Resuelve un problema bajo una restricción y compara los diseños por algo más que el número de líneas.
6. Di qué problema de su época resolvió un lenguaje y cuáles de sus ideas sigues usando.

## El semestre como algoritmo

El curso sigue las reglas que enseña. Ninguna variable contador lo controla. La fase es el estado, como en los programas que leerás. Una revisión al final decide si se detiene. Si no la supera, la segunda pasada vuelve a empezar en W.

```mermaid
flowchart TD
    accTitle: El semestre como un algoritmo raro
    accDescr: Un diagrama de flujo. El curso empieza con el puntero de fase en B, Bicho raro. Un recuadro alrededor de las cinco fases indica que cada semana repite un ciclo: identifica la máquina, traza una ejecución, predice, ejecuta y prueba. Dentro del recuadro, el puntero pasa de B a I, a C, a H y a O. B cubre las semanas 1 y 2. I (Interpreta) cubre las semanas de 3 a 6. C (Camino indirecto) cubre las semanas de 7 a 10. H (Hallazgos) cubre las semanas de 11 a 13. O (Octetos) cubre las semanas 14 y 15. Después de O, la semana 16 es una decisión que pregunta si un desconocido puede reproducir tu afirmación a partir de tu evidencia. Si la respuesta es sí, el curso guarda el resultado con una confirmación (*commit*) de Git, un registro fijo del cambio en el historial, y termina. Si la respuesta es no y esta fue la primera pasada, una flecha vuelve a B, y lees tu propio programa como un adversario. Si la respuesta es no después de la segunda pasada, el curso termina y informas qué falta. Se permite como máximo una pasada más.
    S(["Inicio: fase = B"]) --> W
    subgraph weeks["Cada semana: identifica, traza, predice, ejecuta, demuestra"]
        W["B: Bicho raro, semanas 1 a 2<br/>¿Qué puede causarlo?"] --> E["I: Interpreta, semanas 3 a 6<br/>¿Qué lo hace avanzar?"] --> I["C: Camino indirecto, semanas 7 a 10<br/>¿Quién demanda el trabajo?"] --> R["H: Hallazgos, semanas 11 a 13<br/>¿Qué sobrevive al fallo?"] --> D["O: Octetos, semanas 14 a 15<br/>¿Cuándo es el código solo datos?"]
    end
    D --> C{{"Repaso de la semana 16: ¿puede un desconocido<br/>reproducir tu afirmación?"}}
    C -- "sí" --> X(["Confirma y detente"])
    C -- "no, primera pasada:<br/>lee tu propio trabajo<br/>como el adversario" --> W
    C -- "no, segunda pasada" --> G(["Detente e informa la brecha"])
```

La W es recursiva. En la primera pasada lees programas de otras personas. En la segunda pasada lees tus propios programas.

El bucle tiene un límite. Una segunda revisión fallida termina el curso con un informe escrito de la brecha. Una afirmación fallida, reportada con honestidad, es un resultado.

## Cómo funciona cada semana

Una semana tiene los mismos cuatro pasos. Vienen de las [guías de estudio](../lessons/study-guides/README.md).

1. **Identifica la máquina.** Lee la guía y el comienzo del capítulo del libro. Encuentra el bucle, el estado, el reloj, la decisión y la confirmación.
2. **Traza una ejecución.** Sigue a mano la ejecución fija de la guía. Escribe el estado antes y después de cada paso.
3. **Predice y luego ejecuta.** Escribe tu predicción en el archivo de registro y guárdala con una confirmación (*commit*) de Git, un punto fijo en el historial del proyecto. Luego ejecuta el ejercicio verificado en el entorno aislado (*sandbox*), un espacio separado donde el código no afecta a tu sistema. La hora de la confirmación demuestra el orden. Compara las dos.
4. **Demuestra.** Responde la pregunta de evidencia de la guía. Una afirmación necesita una prueba que pueda fallar.

Todos los programas usan datos ficticios de **DEMO ONLY**. Lee primero el código fuente. Ejecútalo solo en el entorno aislado (*sandbox*), un espacio separado de tu sistema donde el programa no puede dañar nada. Consulta [Ejecutar cosas con seguridad](../lessons/exercises.md#running-things-safely).

### Cuánto debes hacer

El conjunto completo es demasiado para la mayoría de las semanas, así que el trabajo se organiza en tres niveles.

- **Obligatorio (unas 6 horas).** La guía en negrita de la columna Read, los cuatro pasos y el primer ejercicio de la columna Do.
- **Elige una (unas 2 horas más).** Un segundo ejercicio de la columna Do, o una segunda guía de la columna Read.
- **Profundización opcional.** El resto del capítulo, el capítulo del libro sobre el lenguaje de la semana y el código fuente.

### El registro

Cada semana añade una entrada a la bitácora de predicciones. Usa las mismas cuatro filas cada vez.

| Antes de la ejecución (haz primero la confirmación (*commit*) de Git: un registro guardado de tus cambios) | Después de la ejecución | Evidencia |
| --- | --- | --- |
| Máquina: ¿qué ejecuta el bucle? | Traza observada | El comando y la línea de código fuente |
| Estado: ¿dónde vive? | Cómo cambió el estado | Grado de garantía, con la especificación o la implementación nombrada |
| Regla de parada | Resultado, o el fallo | Control negativo: un cambio que debe romper la afirmación |
| Punto de confirmación | Efectos que persistieron | Confirmación (*commit*) de Git del repositorio, versiones de las herramientas y pasos para reproducir |

## Semana a semana

Los enlaces llevan a los capítulos del libro, a las guías de estudio y a los ejercicios. Este plan de estudios no cambia ninguno de ellos. Los números de capítulo son los del libro impreso, donde la Intro es el cap. 1. La primera guía en negrita es la obligatoria.

| Semana | Pregunta | Lee | Haz |
| --- | --- | --- | --- |
| | **B: Bicho raro** | | |
| 1 | ¿Qué puede causar un programa antes de que yo lo ejecute? | [Cap. 4](../lessons/cs/01-reading-an-adversarial-program.md), **[guía](../lessons/study-guides/concepts/reading-adversarial-programs.md)** | [A1](../lessons/exercises.md#a1-read-the-rows-verified), [F2](../lessons/exercises.md#f2-trojan-source-hide-a-character-then-find-it-verified) |
| 2 | ¿Qué cuenta como una máquina? COBOL: un salto es el bucle. | [Cap. 5](../lessons/cs/02-what-counts-as-a-machine.md), **[guía de COBOL](../lessons/study-guides/languages/cobol.md)** | [B1](../lessons/exercises.md#b1-cobol-predict-then-break-alter-verified) |
| | **I: Interpreta** | | |
| 3 | ¿Dónde está el contador de programa? Forth: la posición de análisis. | [Cap. 6](../lessons/cs/03-control-flow-and-continuations.md), **[Guía de Forth](../lessons/study-guides/languages/forth.md)** | [B3](../lessons/exercises.md#b3-forth-move-the-anchor-verified) |
| 4 | ¿Quién elige el siguiente paso? Make y CMake: un grafo de dependencias. | **[Guía de Make y CMake](../lessons/study-guides/languages/make-and-cmake.md)** | [B4](../lessons/exercises.md#b4-make-remove-the-no-op-and-override-the-clock-verified), [B5](../lessons/exercises.md#b5-cmake-mutate-the-literal-verified) |
| 5 | ¿Dónde vive el estado? ed y Ex: un búfer de texto. | [Cap. 9](../lessons/cs/06-state-beyond-variables.md), **[guía de ed y Ex](../lessons/study-guides/languages/ed-and-ex.md)**, [guía de estado](../lessons/study-guides/concepts/state-and-control-beyond-variables.md) | [B18](../lessons/exercises.md#b18-ed-move-the-stop-rule-and-break-the-cleanup-verified), [B19](../lessons/exercises.md#b19-ex-move-the-limit-on-the-tape-and-cut-the-loop-verified), [C3](../lessons/exercises.md#c3-a-loop-whose-state-is-not-a-variable-verified) |
| 6 | ¿Qué reemplaza al bucle? APL: arreglos completos. | **[Guía de APL](../lessons/study-guides/languages/apl.md)** | [B6](../lessons/exercises.md#b6-apl-the-off-by-one-rewrite-verified), [C1](../lessons/exercises.md#c1-weird-next-to-boring-verified) |
| | **C: Camino indirecto** | | |
| 7 | ¿Quién demanda el trabajo? Haskell: pereza. | [Cap. 7](../lessons/cs/04-evaluation-and-demand.md), **[guía de la demanda](../lessons/study-guides/concepts/evaluation-demand-and-laziness.md)**, [guía de Haskell](../lessons/study-guides/languages/haskell.md) | [B2](../lessons/exercises.md#b2-haskell-break-the-laziness-verified) |
| 8 | ¿Pueden las reglas de despacho ser un bucle? Lisp. **Examen parcial.** | **[Guía de Lisp](../lessons/study-guides/languages/common-lisp.md)** | [B10](../lessons/exercises.md#b10-lisp-swap-the-method-combination-verified) |
| 9 | ¿Qué recuerda una clausura (*closure*: función que conserva las variables del lugar donde se creó)? JavaScript. | **[Guía de JavaScript](../lessons/study-guides/languages/javascript.md)** | [B20](../lessons/exercises.md#b20-javascript-read-the-clauses-move-the-limit-and-fail-the-structure-check-verified), [B21](../lessons/exercises.md#b21-javascript-weirder-move-the-stop-rule-in-a-closure-and-watch-the-demand-verified) |
| 10 | ¿De quién es el siguiente turno? Eventos y retrollamadas (*callbacks*: funciones que se ejecutan cuando ocurre un evento). | [Cap. 13](../lessons/cs/10-events-callbacks-and-reactive-control-flow.md), **[guía de eventos](../lessons/study-guides/concepts/events-callbacks-and-reactive-control.md)** | [B22](../lessons/exercises.md#b22-javascript-event-driven-predict-the-trace-then-remove-the-boundary-verified) |
| | **H: Hallazgos** | | |
| 11 | ¿Qué se confirma de verdad? Efectos, errores y consultas. | [Cap. 10](../lessons/cs/07-effects-errors-and-commitment.md), **[guía de efectos](../lessons/study-guides/concepts/effects-errors-and-commitment.md)**, [guía de C# y LINQ](../lessons/study-guides/languages/csharp-linq-xaml-and-ports.md) | [B7](../lessons/exercises.md#b7-linq-enumerate-twice-verified) |
| 12 | ¿Qué sobrevive a una coincidencia fallida? Regex y sed. | **[Guía de regex y sed](../lessons/study-guides/languages/regex-engines-and-sed.md)** | [B8](../lessons/exercises.md#b8-regex-what-survives-a-failed-match-verified), [B9](../lessons/exercises.md#b9-sed-watch-a-computation-verified) |
| 13 | ¿Qué promete la especificación? AWK y find. | [Cap. 11](../lessons/cs/08-abstraction-leaks-and-implementation-dependence.md), **[guía de portabilidad](../lessons/study-guides/concepts/portability-abstraction-and-cost.md)** | [B13](../lessons/exercises.md#b13-awk-the-missing-rt-verified), [B15](../lessons/exercises.md#b15-gnu-find-move-the-stop-rule-read-the-profile-verified) |
| | **O: Octetos** | | |
| 14 | ¿Cuándo es una notación una máquina? Lenguajes formales y m4. | [Cap. 8](../lessons/cs/05-formal-languages-as-computational-substrates.md), **[guía de lenguajes formales](../lessons/study-guides/concepts/formal-languages-and-weird-machines.md)**, [guía de m4](../lessons/study-guides/languages/m4.md) | [B11](../lessons/exercises.md#b11-m4-quote-the-recursion-verified) |
| 15 | ¿Cuándo son los datos un programa? Tcl y tar. | Cap. 12, solo las secciones 12.11 y 12.12: [dónde vive el programa](../lessons/cs/09-comparative-case-studies.md#where-does-the-program-live-and-what-makes-the-next-step-run) y [ponerlo por escrito](../lessons/cs/09-comparative-case-studies.md#writing-a-program-down-reading-it-back-running-it), **[guía de Tcl](../lessons/study-guides/languages/tcl.md)**, [guía de tar](../lessons/study-guides/languages/tar.md) | [B12](../lessons/exercises.md#b12-tcl-edit-the-program-in-the-database-verified), [B16](../lessons/exercises.md#b16-tar-read-the-program-then-run-it-verified) |
| 16 | ¿Puede un desconocido reproducir tu afirmación? Proyecto final. | **[Guía comparativa](../lessons/study-guides/concepts/comparative-machine-design.md)** | Uno de [D](../lessons/exercises.md#d-port-the-challenge-verified-reference-answer-in-awk) o [F1](../lessons/exercises.md#f1-test-a-claim-of-your-choice) |

## Lenguajes antiguos, problemas reales

Un lenguaje histórico no es una curiosidad. Cada uno resolvió un problema de su época. Los problemas cambiaron de forma. No desaparecieron.

| Lenguaje | Época | Problema de la época | Idea que conservas |
| --- | --- | --- | --- |
| [Lisp](https://en.wikipedia.org/wiki/Lisp_(programming_language)) | 1958 | La investigación en IA necesitaba procesar símbolos y listas, no solo números. | El código son datos. Recolección de basura. |
| [COBOL](https://en.wikipedia.org/wiki/COBOL) | 1959 | Las empresas necesitaban programas que los auditores pudieran leer en muchas marcas de computadoras. | Datos declarados como un contrato. Aritmética decimal exacta. |
| [APL](https://en.wikipedia.org/wiki/APL_(programming_language)) | Década de 1960 | Los matemáticos necesitaban una sola notación para las operaciones sobre arreglos completos. | Piensa en arreglos, no en bucles. |
| [ed](https://en.wikipedia.org/wiki/Ed_(software)) | 1969 | Las terminales imprimían en papel, así que los usuarios editaban texto sin ver una pantalla. | Los comandos como un lenguaje pequeño. Un comando fallido como condición. |
| [Forth](https://en.wikipedia.org/wiki/Forth_(programming_language)) | alrededor de 1970 | Las computadoras pequeñas que controlaban instrumentos tenían muy poca memoria. | Una pila y un diccionario bastan para un lenguaje. |
| [sed](https://en.wikipedia.org/wiki/Sed) y [AWK](https://en.wikipedia.org/wiki/AWK) | década de 1970 | Había demasiados archivos para editarlos a mano, así que las canalizaciones filtraban flujos. | Patrón y acción. El bucle implícito. |
| [m4](https://en.wikipedia.org/wiki/M4_(computer_language)) | Década de 1970 | Un solo texto fuente tenía que producir código para muchos destinos. | La expansión y el reescaneo son cómputo. |
| [Make](https://en.wikipedia.org/wiki/Make_(software)) | 1976 | Reconstruir a mano después de cada cambio era lento y propenso a errores. | Declara las dependencias. Deja que la herramienta elija el orden. |
| [tar](https://en.wikipedia.org/wiki/Tar_(computing)) | finales de la década de 1970 | Las unidades de cinta leían y escribían mejor en secuencia, y buscar posiciones era lento. | Serialización. Un archivo empaquetado puede llevar efectos cuando algo lo interpreta. |
| [Tcl](https://en.wikipedia.org/wiki/Tcl) | 1988 | Los autores de herramientas necesitaban un lenguaje de comandos para integrar en sus programas. | Todo es una cadena de texto. El código es dato. |
| [Haskell](https://en.wikipedia.org/wiki/Haskell) | 1990 | Los investigadores tenían muchos lenguajes funcionales perezosos y necesitaban un estándar compartido. | Pereza. Pureza. La demanda impulsa la evaluación. |
| [JavaScript](https://en.wikipedia.org/wiki/JavaScript) | 1995 | Los navegadores necesitaban programas pequeños que reaccionan a los eventos del usuario. | El bucle de eventos. Clausuras (*closures*: funciones que recuerdan las variables de su entorno). Retrollamadas (*callbacks*: funciones que pasas a otra función para que las llame más tarde). |

## Cómo pensar sobre los programas adversariales

Un programa adversarial se escribe para sorprender a su lector. Trata todo programa como si pudiera serlo.

- **Pregunta qué puede causar, no qué dice.** Los nombres, los comentarios y el texto del README son afirmaciones. El código fuente es la evidencia.
- **Separa leer de ejecutar.** Lee primero. Usa un inspector pasivo antes de usar un *intérprete*. Las entradas de tar muestran los dos papeles.
- **Trata el texto como entrada de datos que lleva una intención.** Un carácter oculto, un nombre de archivo o un miembro de un archivo comprimido pueden cambiar lo que hace un programa. El ejercicio F2 muestra cómo.
- **Etiqueta cada afirmación.** ¿Qué etiqueta recibe: *garantizado* por una especificación, *permitido por la implementación* o *aprovechado por accidente*? Da la evidencia de la etiqueta.
- **Sigue la confirmación.** Averigua qué efectos sobreviven a un fallo. Averigua qué se confirma de verdad.
- **Prueba el límite.** El reto compartido conserva la primera tarjeta con la que el total pasa de 40. Un total de exactamente 40 continúa. Los límites esconden bichos.
- **Cambia de lado.** Escribe el programa como su autor. Después léelo como su revisor.

## Cómo pensar de otra manera sobre la resolución de problemas

- **Usa una restricción como herramienta de diseño.** Quita el bucle, la variable o el reloj. Luego pregunta qué cosa cumple ese papel. Práctica: [C2](../lessons/exercises.md#c2-make-the-constraint-real-verified). Consulta [Problemas superados](../lessons/problems-overcome.md).
- **Hazle cinco preguntas a cada máquina.** ¿Qué hace de bucle, de estado, de reloj, de decisión y de confirmación? Consulta [Por patrón de solución](../lessons/patterns.md).
- **Cambia la representación.** El texto, los arreglos, los grafos y los archivos comprimidos hacen que cada uno facilite un problema distinto. Elige el sustrato antes de elegir el algoritmo.
- **Compara lo raro con lo aburrido.** Juzga el par por representación, pruebas, depuración, portabilidad y costo. No juzgues por el número de líneas. Práctica: [C1](../lessons/exercises.md#c1-weird-next-to-boring-verified). Consulta [Lo raro junto a lo aburrido](../lessons/intro.md#weird-next-to-boring).
- **Aprende de la escasez.** Los diseñadores antiguos tenían poca memoria y una cinta lenta. Sus límites los obligaron a tener ideas claras.
- **Sabe cuándo dejar de ser raro.** Cada diseño raro tiene un costo. Indica cuándo lo usarías y cuándo lo evitarías.

## Evaluación

| Parte | Cuándo | Peso |
| --- | --- | --- |
| Registro de predicciones: una predicción, una ejecución y una respuesta con evidencia cada semana | Semanas de 1 a 15 | 30% |
| Examen parcial: haz la traza y la predicción de una entrada que no has visto, y luego prueba la predicción | Semana 8 | 20% |
| Proyecto final: porta el reto a un lenguaje nuevo, o demuestra una afirmación del README con una prueba que pueda fallar | Semana 16 | 40 % |
| Revisión por pares: lee el proyecto final de un compañero como un adversario e informa qué puede causar | Semana 16 | 10% |

### Rúbrica

Puntúa cada dimensión de 0 a 2: 0 es ausente, 1 es parcial y 2 es completa. La última columna indica dónde se aplica cada dimensión. L es el registro de predicciones, C es el proyecto final y P es la revisión por pares.

| Dimensión | Una puntuación de 2 requiere | Se usa en |
| --- | --- | --- |
| Traza y predicción | Una traza a mano y una predicción registrada antes de la ejecución. El informe indica dónde difirió la ejecución. | L, C |
| Evidencia | Cada afirmación cita un comando o una línea de código fuente. Un control negativo muestra que la afirmación puede fallar. | L, C, P |
| Grado de garantía | Garantizado, permitido por la implementación o aprovechado por accidente, con la especificación o la implementación nombrada. | L, C, P |
| Mecanismo | Las cinco preguntas tienen respuesta: qué hace de bucle, qué hace de estado, qué hace de reloj, qué hace de decisión y qué hace de confirmación. | L, C |
| Reproducibilidad | Una persona ajena puede seguir los pasos y obtener el mismo resultado. Las versiones y las entradas de datos están fijadas. | C, P |
| Ventajas y desventajas | El informe dice qué costo tiene el diseño y cuándo evitarlo. Compara por algo más que el número de líneas. | C |
| Seguridad | Primero se leyó el código fuente. Todas las ejecuciones se hicieron en el entorno aislado (*sandbox*), un espacio separado del sistema real, con datos DEMO ONLY. | L, C, P |

La bitácora de predicciones usa las cuatro dimensiones marcadas con L, de 2 puntos cada una, así que una entrada vale 8 puntos. El proyecto final usa todas las dimensiones, las siete. La revisión entre pares se califica según el informe del revisor, con las dimensiones marcadas con P. El informe también nombra una cosa que el programa del compañero de clase puede causar y que el autor no indicó.

Los lectores autodidactas pueden mantener el mismo orden y quitar los pesos. Sustituye la revisión por pares por una publicación a un amigo o a un foro. Pídeles que encuentren lo que tu programa puede causar.

## Ámbito

Este documento es un plan. No cambia el [libro](../lessons/README.md), las [guías de estudio](../lessons/study-guides/README.md), el [reto](../CHALLENGE.md), los ejercicios ni las soluciones. El código fuente y los programas de ejemplo están en el [README del repositorio](../README.md).
