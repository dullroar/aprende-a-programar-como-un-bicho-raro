# Guía de estudio de lectura de programas adversariales

## Para qué sirve esta guía

Esta guía enseña un hábito de lectura. Los programas del libro son *adversariales a propósito*. Una regex ejecuta código Perl. Un archivo de marcado llama a métodos mientras se analiza. Un archivo tar lleva un programa. Una fila de una tabla contiene código fuente Tcl. `find` cava el directorio que está recorriendo. La pregunta central es: **¿qué puede causar este programa antes de que lo ejecute?** El hábito consiste en responderla a partir del código fuente y del ejecutor, y en saber cuál de los dos estás leyendo.

Cuando termines, deberías poder:

1. Escribir, para cualquier programa desconocido, la *autoridad* con la que se ejecutará: archivos, procesos, red y entorno.
2. Separar cuatro actos que a menudo se confunden: escribir datos, leerlos de vuelta, interpretarlos y ejecutarlos. Decir qué acto realiza cada entrada.
3. Encontrar el *intérprete* de un formato de datos en un programa: el componente que convierte bytes en efectos.
4. Nombrar la frontera de confianza en `xaml`, `tar-gnu`, `tcl-weird`, `regex-perl` y `find-gnu`. Decir qué la rompería.
5. Explicar por qué leer el programa junto a su hermano corriente muestra el costo de la acrobacia.
6. Etiquetar cada afirmación que hagas sobre un programa como comportamiento garantizado, permitido por la implementación o aprovechado por accidente, y decir qué evidencia la respalda.

**Límites del alcance.** Esta guía trata de *leer y ejecutar con seguridad*. No es un curso de seguridad: no enseña desarrollo de exploits, modelado de amenazas a fondo ni el funcionamiento interno de un entorno aislado (*sandbox*). Su capítulo de origen es [Cómo leer un programa adversarial](../../informatica/01-lectura-de-un-programa-adversarial.md). Para los detalles de cada entrada, sigue los enlaces a las guías de lenguaje.

## Antes de empezar

**Modelo de seguridad.** Las tarjetas son datos ficticios marcados con **DEMO ONLY**. Los ejemplos usan almacenamiento local temporal y no tienen conexión con ningún sistema real de reporte de horas. Eso es una promesa sobre los *datos*. No es una promesa sobre el *código*, que inicia procesos, ejecuta intérpretes de comandos y analiza su propia entrada de datos. Por eso cada entrada se trata como no confiable hasta que alguien la ha leído y entendido, y se ejecuta primero en el entorno aislado. Desde la raíz del repositorio, con [`SANDBOX-SETUP.md`](../../../SANDBOX-SETUP.md) hecho:

```bash
sandbox/container/run-image.sh src/tar-gnu
```

Los ejecutores admitidos son `sandbox/container/run-image.sh <folder>`, `sandbox/run.sh <folder>` y `lessons/tools/run-in-sandbox.sh [-e NAME=VALUE] <folder> <command...>`; en Windows, `sandbox\windows\run.ps1`. Consulta [Ejecutar cosas con seguridad](../../exercises.md#running-things-safely).

Trabaja con una copia en cualquier experimento. La salida es aleatoria, así que compara propiedades, no números.

**Regla de predicción.** Antes de ejecutar nada, escribe qué archivos tocará y qué procesos iniciará. Escribe también qué parte de su *entrada de datos* puede hacer que haga algo que no haría de otro modo. Después ejecútalo y compara.

**Vocabulario.**

| Término | Significado aquí |
| --- | --- |
| Autoridad | Lo que un programa *tiene permitido* hacer: los archivos, procesos y red a los que puede llegar como el usuario que lo ejecutó. |
| Intérprete | El componente que convierte datos en efectos. Un analizador sintáctico puede serlo sin que nadie lo llame así. |
| Frontera de confianza | La línea entre los datos que controlas y los datos sobre los que un atacante puede influir. |
| Inspección pasiva | Leer y comprobar un formato sin ejecutar nada de él. |

## El reto compartido

La [especificación del reto](../../introduccion.md#what-the-challenge-does) pide tarjetas con una categoría y de 10 a 19 horas enteras. Las categorías se repiten en ciclo: `Meetings`, `Coding`, `Debugging` y `Learning`. Suma las horas de cada tarjeta al total acumulado. Detente cuando el total pasa de 40. Conserva la **primera tarjeta con la que el total pasa de 40**. Un total de exactamente 40 continúa. Cuatro tarjetas de 10 horas necesitan una quinta tarjeta, de la categoría `Meetings`. Las ejecuciones conformes tienen de 3 a 5 tarjetas y un total de 41 a 59 horas.

Las dos demostraciones de LINQ usan una semana laboral fija. XAML puede terminar con un total de 40 sin ninguna pasada restante. El almacenamiento y los resúmenes varían según la entrada.

El pequeño resultado esperado te da una forma de poner a prueba tu lectura. El verificador compartido `lessons/tools/check-demo.sh` comprueba la forma de un informe conforme. Cada comprobación individual puede dar evidencia de efectos más allá del informe, como los registros que acepta el intérprete de tar.

## La máquina que hay que identificar

Aquí la máquina no es un programa sino un *lector*, y la identificas con las cinco preguntas aplicadas a *lo que un programa puede causar*.

**Qué se repite.** Pregunta qué repite el programa y *quién inicia cada repetición*. En `regex-perl`, un cuantificador repite un patrón cuyas piezas son código Perl. En `tar-gnu`, tar repite un despachador sobre los miembros del archivo tar. En `xaml`, nada se repite: el analizador sintáctico llega a cada `ObjectDataProvider` una vez. En `find-gnu`, `find` se repite porque `-exec` crea un directorio que `find` visita después.

**Dónde vive el estado.** Pregunta dónde guarda el programa *sus entradas de datos y su memoria*, porque ahí escribe un atacante. En `tcl-weird`, los cuerpos de los procedimientos son filas de una tabla. En `xaml`, el documento. En `tar-gnu`, el archivo tar. En `find-gnu`, la ruta. En todos los casos, quien pueda cambiar ese almacén puede cambiar el programa.

**Qué hace avanzar el paso siguiente.** Pregunta quién decide el paso siguiente. En `tar-gnu` es la línea de comandos del operador (`--to-command`), no el archivo tar. En `tcl-weird` es la búsqueda de un nombre de comando desconocido. En `xaml` es el analizador sintáctico. Un formato que puede nombrar su propio paso siguiente es más peligroso que uno que no puede.

**Qué lo detiene.** Pregunta qué limita el daño. El despachador de `tar-gnu` rechaza los tipos de registro desconocidos y ejecuta exactamente una sentencia SQL por miembro. `tcl-weird` es seguro solo porque su tabla es privada de una conexión. El entorno aislado añade un límite exterior: sin red, raíz de solo lectura y un usuario sin privilegios.

**Qué confirma.** Encuentra el componente con autoridad de escritura y el punto en que ocurre el ejercicio de esa autoridad. En el ejemplo de regex de .NET, el patrón entrega capturas y el anfitrión añade un informe TSV. En las entradas de SQLite, busca el límite de la transacción y el esquema. Una columna `NOT NULL` con `CHECK(demo_only=1)` puede rechazar una inserción normal de una fila que no es de demostración.

## Traza una ejecución

Una traza de lectura no es una traza de programa. Aquí tienes la misma ejecución de tres tarjetas (horas 15, 19, 12) leída como *lo que cada entrada pudo haber hecho*. Solo se usan hechos que verificaron las guías de lenguaje:

| Entrada | Quién ejecutó los datos | Qué pudieron nombrar los datos | Qué hizo en cambio la entrada |
| --- | --- | --- | --- |
| `tar-gnu` | El `--execute` del operador y luego tar | Cualquier nombre de miembro | `inspect.sh` revisó los 12 miembros y no ejecutó nada. El despachador acepta cinco nombres y rechaza el resto. |
| `xaml` | El analizador sintáctico de XAML | Cualquier constructor y método de la lista de tipos | Llama a `Random.Next` y a `Add` de EF Core (leído del código fuente, no ejecutado aquí). |
| `tcl-weird` | `unknown`, desde una tabla | Cualquier texto Tcl | Ejecutó `born`, `category`, `hours`, `init`, `runid`, `week`: los seis procedimientos que el propio programa almacenó. |
| `regex-perl` | Perl, durante una coincidencia | Cualquier código Perl | Inicia `sqlite3` sin intérprete de comandos, con una lista fija de argumentos. |
| `find-gnu` | `find`, mediante `-exec` y `-fprintf` | Cualquier comando | `mkdir`, `mktemp` y `-fprintf` al fd 3. |
| `awk-weird` | `gawk`, que lee un flujo de bytes | Lo que coincida con `RS` | Corta `/dev/urandom` en los dígitos, así que los datos son bytes aleatorios. |

La columna tar de la ejecución verificada: el inspector decodificó 12 miembros (`# 12 member(s); 0 the interpreter would refuse`) y la ejecución imprimió `Meetings 15 15`, `Coding 19 34`, `Debugging 12 46`. El paso que *leyó* el programa fue distinto del paso que lo *ejecutó*, y el segundo necesitó una bandera adicional.

**Traza de un error.** Mientras se preparaba esta guía, un arnés de pruebas ejecutó el script `regex-sed` directamente, desde una copia de trabajo, sin el envoltorio que conecta el descriptor de archivo 3. El script escribe su SQL con `w /dev/fd/3`. Con el fd 3 cerrado, el propio archivo de script de sed había tomado ese descriptor. Por eso `w` abrió el archivo de script y lo sobrescribió con SQL. El autor del programa había leído el código fuente y lo había probado con su envoltorio. El fallo vino de ejecutarlo de una forma que el autor no previó. El script se restauró desde Git, y el README de sed ahora trae una advertencia: ejecútalo solo mediante su envoltorio o con un destino `3>` explícito. Esa es toda la materia en un incidente: la autoridad depende de cómo ejecutas el programa.

**Exactamente 40.** Para leer, el borde es otra prueba de comprensión. Si un programa afirma "un total de exactamente 40 continúa", la *evidencia* es una ejecución en la que continúa. Las antiguas implementaciones de regex con cuatro nombres y de encabezado `for` se detenían demasiado pronto. Las entradas reparadas tienen un quinto nombre, con sorteos forzados o una comprobación fijada a nivel de código fuente para el borde. XAML sigue teniendo cuatro pasadas (consulta la [guía comparativa](diseno-comparativo-de-maquinas.md)). Una afirmación que no puedes demostrar es una afirmación que solo has leído.

## Compara los diseños ordinarios y los raros

Lee el programa raro junto a su hermano ordinario. La diferencia muestra exactamente qué costo tiene la acrobacia y *adónde pasó la autoridad*.

| Par | Diseño ordinario | Diseño raro | Adónde pasó la autoridad |
| --- | --- | --- | --- |
| `cobol` / `cobol-weird` | Una condición con nombre sobre datos | Un salto reescrito | El flujo de control pasó a datos que el programa edita. |
| `haskell` / `haskell-weird` | Una función pura y luego E/S | Efectos dentro de una lista perezosa | El orden de los efectos pasó al consumidor. |
| `tcl` / `tcl-weird` | Un bucle en un procedimiento | Código fuente en filas de una tabla, obtenido por `unknown` | El *código* pasó a una tabla. |
| `tar-gnu` / `tar-gnu-weird` | Miembros como instrucciones | La disposición como reloj | El programa pasó a un archivo tar y luego a su tamaño. |
| `find-posix` / `find-gnu` | Contar con nombres | Los extras de GNU hacen la aritmética | El estado pasó a la ruta del directorio. |

| Dimensión | Qué preguntar |
| --- | --- |
| **Representación** | ¿El programa es texto, un archivo, una tabla, un documento o una disposición? |
| **Observabilidad** | ¿Puedes leerlo *sin ejecutarlo*? `tar-gnu` tiene un inspector. `xaml` no. |
| **Pruebas** | ¿Hace cumplir `check.sh` la restricción propia de la entrada (palabras prohibidas, un recuento de `ALTER`, un `Regex.Match`)? Una restricción sin comprobación es una esperanza. |
| **Debugging** | ¿Un error falla de forma ruidosa (un error de compilación) o de forma silenciosa (una operación sin efecto, una ejecución vacía)? |
| **Portabilidad** | ¿Depende de una función de una sola implementación (GNU `RT`, el `--to-command` de GNU tar)? |
| **Costo** | ¿Qué costo tiene la acrobacia en facilidad de revisión? |

## Qué demuestran los ejercicios

| Ejercicio | Predice primero | Qué muestra la evidencia |
| --- | --- | --- |
| [B16. tar: lee el programa y luego ejecútalo](../../exercises.md#b16-tar-read-the-program-then-run-it-verified) | Añade un miembro que no esté en el conjunto de instrucciones. ¿Cuáles son los estados de salida y aparece un archivo `pwned`? | El inspector lo rechaza (`REFUSE (unknown record type)`, estado de salida 4), el intérprete no ejecuta nada y no aparece ningún archivo. Leer y ejecutar fueron actos distintos, y la frontera de confianza fue la decisión del operador. |
| [B13. AWK: la RT que falta](../../exercises.md#b13-awk-the-missing-rt-verified) | Ejecuta el programa sin modificar con `mawk` sobre un archivo finito. | `# committed total=0 entries=0`, sin error, estado de salida 0. mawk no tiene `RT`, así que omite cada registro. El código "de apariencia portátil" puede fallar *en silencio* en la implementación equivocada. |
| [B14. find: trucar los dados](../../exercises.md#b14-find-rig-the-dice-verified) | Pon un `mktemp` falso primero en `PATH`. ¿Qué cambia? | Los dados están trucados: con el nombre `xxxxxS`, cada tarjeta tiene 19 horas. Un programa que encuentra sus herramientas mediante `PATH` toma lo primero que haya ahí. |
| [F2. Trojan Source](../../exercises.md#f2-trojan-source-hide-a-character-then-find-it-verified) | Un espacio de ancho cero después de `admin`: ¿qué imprime `node`? | `false`. La cadena de texto tiene un carácter que no puedes ver. El escaneo lo encuentra y los bytes lo muestran. |
| [F. Demostrar una afirmación de un README](../../exercises.md#f-prove-a-readme-claim-verified) | ¿Qué prueba fallaría si la afirmación fuera falsa? | Una afirmación es evidencia solo si tiene un control negativo. |

## Modos de fallo, costos y límites

| Afirmación sobre un programa | Etiqueta | Por qué |
| --- | --- | --- |
| Leer un archivo tar con `tar -xf` no ejecuta su contenido | **garantizado** | Un archivo tar es solo datos. Solo el comando que se le asocia le da un efecto. |
| El despachador de `tar-gnu` no pasa ninguna parte de un miembro a un intérprete de comandos | **garantizado** por diseño y probado | La comprobación de la entrada lo hace cumplir. |
| `XamlReader.Load` ejecuta métodos de `ObjectDataProvider` durante el análisis sintáctico | **aprovechado por accidente** | Un lenguaje de interfaz documentado, usado como intérprete. El README de XAML lo clasifica así. |
| El `RT` de GNU `awk` contiene el texto que coincidió con `RS` | **permitido por la implementación** | Solo en gawk. mawk no lo tiene. B13 muestra qué ocurre. |
| `unknown` ejecuta cualquier texto que haya en la tabla | **garantizado** | Tcl documentado. Aquí no entraña riesgo solo porque la tabla es privada. |
| Un script que escribe en `/dev/fd/3` escribe en lo que haya en el fd 3 | **garantizado** | Comportamiento del sistema operativo. La entrada supone que su envoltorio abrió ahí una tubería. |

**Costos que hay que dejar claros.**

- **Un modelo de amenazas que no se actualiza describe un sistema que ya no existe.** "Es solo marcado" y "es solo una regex" son falsos aquí. Consulta [Modelo de amenazas](../../informatica/01-lectura-de-un-programa-adversarial.md#threat-model).
- **La revisión de código no escala a lo ilegible.** El programa de `regex-perl` es una sola línea muy larga. El entorno aislado existe porque "leer cada línea primero" no basta ([Entorno aislado](../../informatica/01-lectura-de-un-programa-adversarial.md#sandbox)).
- **Los caracteres invisibles derrotan a la lectura.** [Trojan Source](../../informatica/01-lectura-de-un-programa-adversarial.md#trojan-source-characters-you-cannot-see) es la razón por la que el repositorio los busca.
- **Un lector hostil también es un riesgo.** Una herramienta que analiza un formato de archivo es un intérprete de ese formato. Trátala como tal.
- **Dónde este hábito es legítimo en todas partes.** Es el hábito ordinario de revisión aplicado a deserializadores, plantillas, cargadores de complementos y `eval`.

## Conexiones a lo largo del repositorio

- **El análisis sintáctico como ejecución.** [C#, LINQ, XAML y adaptaciones](../lenguajes/csharp-linq-xaml-y-adaptaciones.md) muestra el caso de XAML.
- **Autoridad desde el comando.** [tar](../lenguajes/tar.md) es el ejemplo más limpio del repositorio.
- **Código en una tabla.** [Tcl](../lenguajes/tcl.md) y [APL](../lenguajes/apl.md) guardan ambos el código como texto.
- **Código en un patrón.** [Motores de regex y sed](../lenguajes/motores-de-regex-y-sed.md) ejecuta Perl y C dentro de una coincidencia, e incluye el riesgo de `/dev/fd/3`.
- **Estado, control y comparación.** [Estado y control más allá de las variables](estado-y-control-mas-alla-de-las-variables.md), [Efectos, errores y confirmación](efectos-errores-y-confirmacion.md) y [Diseño comparado de máquinas](diseno-comparativo-de-maquinas.md).
- **En el libro.** [Cómo leer un programa adversarial](../../informatica/01-lectura-de-un-programa-adversarial.md), incluidos [Ejecución arbitraria de código](../../informatica/01-lectura-de-un-programa-adversarial.md#arbitrary-code-execution), [Principio de mínimo privilegio](../../informatica/01-lectura-de-un-programa-adversarial.md#principle-of-least-privilege) y [Capacidad y autoridad](../../informatica/01-lectura-de-un-programa-adversarial.md#capability-and-authority).

## Autoevaluación

Responde cada pregunta con tus propias palabras antes de leer el texto en cursiva. Di qué evidencia respaldaría cada respuesta.

1. **Traza.** Para un archivo tar cuyos miembros son `000.begin`, `010.card`, `011.stop-over`, `025.exec`, `990.show`, ¿qué actos ocurren con `inspect.sh` y cuáles con `interpret.sh --execute`? *(El inspector lee y decodifica los cinco y rechaza `025.exec` con estado de salida 4. El intérprete ejecuta primero el inspector, ve el rechazo y no ejecuta nada. No se ejecuta ningún miembro.)*
2. **Explica.** ¿Por qué no hay riesgo en ejecutar `tcl-weird` cuando `unknown` ejecuta como código el texto de una tabla? *(La tabla es una tabla `TEMP`, creada en memoria por el programa a partir de literales, así que nadie más puede escribir en ella. La frontera es la privacidad de esa tabla, no ninguna comprobación del texto.)*
3. **Transfiere.** Te piden revisar un servicio que renderiza plantillas aportadas por usuarios. ¿A qué entradas se parece y cuáles son tus tres primeras preguntas? *(Se parece a `xaml` y a `regex-perl`: un motor de confianza que lee texto influido por un atacante. Pregunta: ¿qué puede llamar el lenguaje de plantillas, quién puede escribir una plantilla y con qué autoridad se ejecuta el renderizador?)*
4. **Evidencia.** Un colega dice: "`tar-gnu` nunca ejecuta nada de un archivo tar que no sea uno de cinco tipos de registro." Diseña una prueba que pueda fallar. ¿Cuál es el control negativo? *(Crea archivos tar con un miembro desconocido y con un cuerpo mal formado, ejecuta `interpret.sh --execute` y comprueba el estado de salida 4 y una base de datos intacta. El control es un archivo tar válido, que debe ejecutarse. La afirmación es un comportamiento garantizado por diseño y probado.)*

## Lecturas adicionales

- [Ejecución arbitraria de código](https://en.wikipedia.org/wiki/Arbitrary_code_execution) (Wikipedia): el problema general del que se defiende este hábito de lectura.
- [Inyección de código](https://owasp.org/www-community/attacks/Code_Injection) (OWASP): cómo el texto se convierte en código, con defensas.
- [Modelo de amenazas](https://en.wikipedia.org/wiki/Threat_model) (Wikipedia): qué escribir antes de decidir en qué confiar.
- [RFC 3552, sección 3: el modelo de amenazas de Internet](https://www.rfc-editor.org/rfc/rfc3552) (IETF): un ejemplo breve y práctico del mundo de los estándares.
