<!-- GENERADO por lessons/book/build.py a partir de lessons/cs-source/ y del frontmatter de las entradas. No lo edites; edita las fuentes y ejecuta build.py. -->

# Cómo leer un programa adversarial

Para una lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre la lectura de programas adversariales](../guias-de-estudio/conceptos/lectura-de-programas-adversariales.md).

Los programas de este libro son *adversariales* a propósito: se comportan como lo haría un atacante. Hacen cosas que el código no debería hacer: ejecutar código durante una coincidencia de una expresión regular, llamar a métodos durante el análisis sintáctico de un archivo de marcado y reescribir sus propios destinos de salto. Puedes estudiarlos con seguridad por la forma en que este repositorio los maneja. Cada entrada escribe datos ficticios marcados con **DEMO ONLY** y se ejecuta en un [entorno aislado](../../SANDBOX-SETUP.md) (*sandbox*) que limita el acceso al sistema anfitrión. Durante la revisión, el código se trata como no confiable hasta que alguien lo lee y lo entiende.

Este capítulo presenta el modelo de seguridad del lector. Propone dos hábitos. Primero, **lee el programa raro al lado de su versión ordinaria**: [`cobol`](../../src/cobol/README.md) junto a [`cobol-weird`](../../src/cobol-weird/README.md) y [`haskell`](../../src/haskell/README.md) junto a [`haskell-weird`](../../src/haskell-weird/README.md). La diferencia te muestra el costo exacto de la pirueta. Segundo, **pregunta qué clase de promesa respalda cada truco**: comportamiento garantizado, permitido por la implementación o aprovechado por accidente (consulta la [introducción](../introduccion.md#tres-tipos-de-conocimiento)). Los temas que siguen son las ideas de seguridad y revisión que sustentan esos hábitos. Entre ellas está la que ilustran las entradas de tar: la autoridad proviene del comando que ejecuta un programa y no de los datos que lee ([Capacidad y autoridad](01-lectura-de-un-programa-adversarial.md#capacidad-y-autoridad)).

## Modelo de amenazas

Un modelo de amenazas responde cuatro preguntas sencillas. ¿Qué protegemos? ¿Quién podría atacarlo? ¿Cómo podría hacerlo? ¿Qué haremos al respecto? Existe porque nadie puede defenderse de "todo". Te defiendes de una lista, y esa lista es el modelo de amenazas. Los equipos lo usan para decidir dónde gastar el tiempo de revisión y qué protecciones añadir. Este repositorio da la vuelta a la pregunta habitual. El código es lo que *no* es de fiar (una solicitud de cambios de un desconocido), y lo que protegemos es la máquina de quien revisa. Por eso [`CONTRIBUTING.md`](../../CONTRIBUTING.md) pide un script de comprobación que se ejecute en un sistema desechable y sin red.

- **Úsalo cuando:** vayas a ejecutar, instalar o revisar código que no escribiste, o cuando diseñes cualquier cosa que acepte entrada de datos.
- **Evítalo cuando:** lo trates como un documento que se escribe una sola vez. Un modelo de amenazas que nadie actualiza describe un sistema que ya no existe.

**Dos ejemplos de este repositorio, donde el modelo de amenazas tuvo que cambiar:**

- **"Es solo marcado."** La entrada de XAML ([`xaml`](../../src/xaml/README.md)) inspiró directamente un segundo proyecto, [xaml-write-and-run](https://github.com/dullroar/xaml-write-and-run). Ese proyecto construye la forma de un canal de comando y control solo con archivos `.xaml`: un archivo escribe el siguiente en el disco, un objeto posterior del mismo documento lo carga y lo ejecuta, y la cadena se extiende sola. Una variante descarga sus siguientes instrucciones de la web. Se apoya en un camino de ataque muy conocido (el clásico gadget de deserialización `ObjectDataProvider`), que los defensores ya conocen y vigilan. Esa es la lección. Incluso en un camino bien vigilado, "es solo marcado" es un falso consuelo: un analizador sintáctico de confianza que lee marcado influido por un atacante está ejecutando un programa, así que tu modelo de amenazas debe tratar el marcado como código.
- **"Es solo una expresión regular."** La entrada de Perl ([`regex-perl`](../../src/regex-perl/README.md)) es una única coincidencia de patrón. Dentro de esa coincidencia, unos bloques de código Perl cargan los datos, escriben en una base de datos e imprimen, y luego la coincidencia devuelve falso a propósito. Si tu modelo de amenazas solo se preocupa de que una expresión regular se ejecute despacio (mira [Denegación de servicio mediante expresiones regulares](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#denegación-de-servicio-mediante-expresiones-regulares)), actualízalo. Una expresión regular también puede ejecutar código, y un patrón merece el mismo cuidado que cualquier otro programa que aceptes.

**Más información:**

- [Modelo de amenazas](https://en.wikipedia.org/wiki/Threat_model) (Wikipedia)
- [RFC 3552, sección 3: el modelo de amenazas de Internet](https://www.rfc-editor.org/rfc/rfc3552), un ejemplo breve y práctico del IETF
- [Modelado de amenazas](https://owasp.org/www-community/Threat_Modeling) (OWASP), una guía paso a paso

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`regex-perl`](../../src/regex-perl/README.md) | Perl, Regular expressions | demuestra | Que Perl puede ejecutar código durante una coincidencia de una expresión regular. |
| [`tar-gnu`](../../src/tar-gnu/README.md) | GNU tar, SQLite | demuestra | Que un archivo tar puede ser un programa serializado: tar lee los miembros en orden y solo el comando que indica el operador les da un efecto. |
| [`xaml`](../../src/xaml/README.md) | XAML, C# | demuestra | Que un analizador sintáctico de marcado puede ejecutar un programa mientras describe una interfaz de usuario. |

## Ejecución de código arbitrario

La ejecución de código arbitrario ocurre cuando un atacante hace que un programa ejecute instrucciones que su autor nunca previó. Suele ocurrir por accidente: un desbordamiento de búfer, una cadena de texto inyectada o un formato de archivo más potente de lo que se creía. Aquí importa porque muchas entradas del repositorio hacen lo mismo *a propósito, en un lugar seguro*. El `ObjectDataProvider` de XAML llama a métodos durante el análisis del archivo. La construcción `(?{ ... })` de Perl ejecuta código en mitad de una coincidencia. El gancho `unknown` de Tcl ejecuta código guardado en una fila de la base de datos. El mecanismo siempre es el mismo: **se leen datos como código**.

- **Usa esta idea cuando:** revises cualquier función que "evalúe" algo: `eval`, plantillas, deserializadores, expansores de macros o cargadores de complementos.
- **Evita la técnica cuando:** la entrada de datos venga de alguien en quien no confías. Si necesitas puntos de extensión, ofrece una interfaz pequeña y declarada (una API de complementos o un lenguaje de expresiones mínimo) en lugar de un `eval` general.

**Lee más:**

- [Ejecución de código arbitrario](https://en.wikipedia.org/wiki/Arbitrary_code_execution) (Wikipedia)
- [Inyección de código](https://en.wikipedia.org/wiki/Code_injection) (Wikipedia)
- [Inyección de código](https://owasp.org/www-community/attacks/Code_Injection) (OWASP), con ejemplos y defensas
- [`eval()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval) (MDN), cuya advertencia empieza con "¡Nunca uses eval() directo!"

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`regex-perl`](../../src/regex-perl/README.md) | Perl, Regular expressions | demuestra | Que Perl puede ejecutar código durante una coincidencia de una expresión regular. |
| [`tar-gnu`](../../src/tar-gnu/README.md) | GNU tar, SQLite | demuestra | Que un archivo tar puede ser un programa serializado: tar lee los miembros en orden y solo el comando que indica el operador les da un efecto. |
| [`tcl-weird`](../../src/tcl-weird/README.md) | Tcl, SQLite | demuestra | Que el código Tcl se compone solo de cadenas de texto. Por eso puede residir en una base de datos, recuperarse, definirse y ejecutarse bajo demanda. Los disparadores de SQLite determinan el flujo de control. |
| [`xaml`](../../src/xaml/README.md) | XAML, C# | demuestra | Que un analizador sintáctico de marcado puede ejecutar un programa mientras describe una interfaz de usuario. |

## Entorno aislado

Un entorno aislado (*sandbox*) es un espacio que limita el acceso al sistema anfitrión. Allí puedes ejecutar código en el que no confías. El código recibe un espacio pequeño y cercado: poca memoria, sin red y sin acceso a tus archivos. Existe porque "lee primero cada línea" no funciona a gran escala y porque un programa astuto puede ocultar lo que hace. Aquí todas las entradas se ejecutan en uno. El entorno aislado de Linux no tiene red, usa un sistema de solo lectura y ejecuta el código con un usuario sin privilegios. Las entradas de Windows usan Windows Sandbox. Consulta [`SANDBOX-SETUP.md`](../../SANDBOX-SETUP.md).

- **Úsalo cuando:** ejecutes código que no escribiste o código que procese una entrada de datos que no escribiste.
- **Evita confiar a ciegas:** los entornos aislados tienen bichos que permiten escapar y no pueden proteger los datos que les das o que sacas de ellos. Usa el entorno como una capa entre varias (*defensa en profundidad*) y lee el código de todos modos.

**Lee más:**

- [Entorno aislado (seguridad informática)](https://en.wikipedia.org/wiki/Sandbox_(computer_security)) (Wikipedia)
- [Virtualización a nivel del sistema operativo](https://en.wikipedia.org/wiki/Operating-system-level_virtualization), la idea detrás de los contenedores (Wikipedia)

**En este repositorio:**

**Se aplica a todas las entradas** (40). Cada entrada documenta un comando para un contenedor de Linux o para Windows Sandbox. Si una entrada incluye un script de comprobación, consulta su README para saber cómo ejecutar las comprobaciones.

## Principio de mínimo privilegio

El principio de mínimo privilegio dice que cada parte de un sistema debe recibir solo los permisos que necesita. Existe porque todo programa tiene bichos. Si alguien aprovecha un bicho, el daño se limita a lo que esa parte tenía permiso de hacer. En este repositorio, los contenedores de ejecución funcionan con el usuario sin privilegios `nobody`, sin red y con un sistema de archivos de solo lectura. Si una entrada se porta mal, casi no tiene *con qué* hacerlo.

- **Úsalo cuando:** siempre. Es la regla predeterminada para cuentas, servicios, contenedores, tokens de API y permisos de archivo.
- **Evita su modo de fallo:** si una tarea sufre un fallo por falta de un permiso, concede justo ese permiso. No lo "arregles" ejecutándola como root.

**Lee más:**

- [Principio de mínimo privilegio](https://en.wikipedia.org/wiki/Principle_of_least_privilege) (Wikipedia)
- [RFC 4949: glosario de seguridad en Internet](https://www.rfc-editor.org/rfc/rfc4949), que define el término (busca "least privilege" en la página)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`tar-gnu`](../../src/tar-gnu/README.md) | GNU tar, SQLite | demuestra | Que un archivo tar puede ser un programa serializado: tar lee los miembros en orden y solo el comando que indica el operador les da un efecto. |

## Revisión de código

En una revisión de código, otra persona lee tu código antes de que se acepte. Existe porque las pruebas solo comprueban lo que se te ocurrió probar. Un lector puede notar algo que se te pasó. Aquí la revisión tiene una forma concreta: el README debe incluir la sección **Cómo funciona el truco** en lenguaje claro. Los revisores (personas y asistentes de IA) deben explicar el código en palabras sencillas y hacer una lista de todo lo que puede tocar. Si el revisor no puede seguir la entrada, esta no se integra, por ingeniosa que sea.

- **Úsala cuando:** hagas cualquier cambio, sobre todo si el código es inusual.
- **Evita depender solo de ella:** el cansancio hace que se pasen cosas por alto y los caracteres invisibles escapan a la vista. Combina la revisión con controles automáticos como `sandbox/scope-check.sh`.

**Lee más:**

- [Revisión de código](https://en.wikipedia.org/wiki/Code_review) (Wikipedia)

**En este repositorio:**

**Se aplica a todas las entradas** (40). El README de cada entrada tiene una sección Cómo funciona el truco. Es la explicación en lenguaje claro que el revisor contrasta con el código. El control rechaza toda entrada nueva que carezca de esa sección.

## Trojan Source: caracteres que no puedes ver

Trojan Source es un ataque contra la persona que revisa. Unicode incluye caracteres que no puedes ver: espacios de ancho cero y controles "bidireccionales" que cambian el orden visual del texto. Un código puede *parecer* inofensivo para una persona y *significar* otra cosa para el compilador. Investigadores de Cambridge describieron el ataque en 2021 (CVE-2021-42574). Este repositorio se defiende de forma sencilla: `sandbox/scope-check.sh` rechaza los caracteres ocultos y los que cambian la dirección en una solicitud de cambios. El Unicode visible no da problemas. APL necesita `⍴` y `⍳`.

- **Usa la defensa cuando:** aceptes código de otras personas. Busca caracteres invisibles de forma automática.
- **Evita corregir de más:** no prohíbas todo el texto que no sea ASCII. Prohíbe los caracteres que no tienen forma visible.

**Más información:**

- [Trojan Source](https://en.wikipedia.org/wiki/Trojan_Source) (Wikipedia)
- [Texto bidireccional](https://en.wikipedia.org/wiki/Bidirectional_text) (Wikipedia)
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629), la codificación que transporta todo este texto

**En este repositorio:**

**Practícalo:** [F2. Trojan Source: oculta un carácter y luego encuéntralo (verificado)](../exercises.md#f2-trojan-source-oculta-un-carácter-y-luego-encuéntralo-verificado). Ninguna entrada demuestra esta idea, así que el ejercicio es el ejemplo.

## Especificación frente a implementación

La especificación de un lenguaje dice qué *significan* los programas. Una implementación es un programa concreto que intenta seguirla. Pueden diferir y en esa diferencia vive este libro. Cada lección etiqueta un truco como **garantizado** (la especificación lo promete) o **permitido por la implementación** (un compilador o una plataforma lo permite). La tercera etiqueta es **aprovechado por accidente** (hoy funciona y nadie lo prometió). El IETF dio a los ingenieros un vocabulario útil para la misma idea: MUST, SHOULD y MAY, definidos en el RFC 2119. Una especificación que usa esas palabras con cuidado te dice con exactitud cuánto puedes confiar en ella.

- **Úsala cuando:** vayas a depender de un comportamiento. Pregunta cuál de las tres clases de promesa lo respalda.
- **Evítala cuando:** necesites evidencia de rendimiento. Una ejecución en una máquina solo demuestra lo que sucedió allí.

**Lee más:**

- [Especificación de lenguajes de programación](https://en.wikipedia.org/wiki/Programming_language_specification) (Wikipedia)
- [RFC 2119: palabras clave para el uso en los RFC](https://www.rfc-editor.org/rfc/rfc2119), dos páginas que fijan el significado de MUST, SHOULD y MAY
- [Comportamiento indefinido, no especificado y definido por la implementación](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#comportamiento-indefinido-no-especificado-y-definido-por-la-implementación) y [Ley de Hyrum](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#ley-de-hyrum) en "Fugas de abstracción y dependencia de la implementación"

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`ed-weird`](../../src/ed-weird/README.md) | ed, SQLite | demuestra | Que un editor de líneas es una máquina de reescritura: las líneas son los datos, las direcciones son el programa y una sustitución fallida dentro de un comando global es un "si". |
| [`ex-weird`](../../src/ex-weird/README.md) | Ex, SQLite | demuestra | Que los registros de un editor pueden contener un programa: una línea de texto se copia en un registro y se ejecuta con @, y las marcas y las direcciones de línea del propio editor hacen la aritmética. |

## Capacidad y autoridad

Quién puede hacer qué es una cuestión de **autoridad**, además de datos. Un archivo que por sí solo no puede hacer nada gana poder cuando algo con autoridad acepta actuar sobre él. La antigua regla de la **seguridad basada en capacidades** dice que solo debes tener la autoridad que necesitas. Esa autoridad debe venir de lo que te entregaron y no de lo que puedes nombrar.

[`tar-gnu`](../../src/tar-gnu/README.md) lo muestra en una línea. Un archivo de almacenamiento no puede registrar su propio gancho. `tar -xf` escribe archivos y no ejecuta nada. `tar --to-command=...` inicia un programa por cada miembro. La autoridad para ejecutar algo está en el comando que escribió el *operador*, así que ese comando es la frontera de confianza. [`ed-weird`](../../src/ed-weird/README.md) y [`ex-weird`](../../src/ex-weird/README.md) hacen una elección similar con los editores. GNU ed permite escapar al intérprete de comandos (*shell*) con `!` dentro de una lista de comandos global. Ex también tiene `!` y comandos para archivos. Ambos programas los evitan y sus scripts de comprobación lo hacen cumplir. La razón no es que los comandos sean malos. Un programa que puede ejecutar un intérprete de comandos puede hacer cualquier cosa. Si no puede ejecutarlo, es mucho más fácil razonar sobre el programa. Consulta también [Entorno aislado](01-lectura-de-un-programa-adversarial.md#entorno-aislado) y [Principio de mínimo privilegio](01-lectura-de-un-programa-adversarial.md#principio-de-mínimo-privilegio).

- **Úsala cuando:** diseñes una interfaz que ejecute algo en nombre de otra persona. Pregunta qué autoridad tiene quien hace cada llamada y no concedas más a quien la recibe.
- **Evítala cuando:** tomes "solo son datos" como motivo para dejar de pensar. Los datos son inertes hasta que un consumidor con autoridad actúa sobre ellos.

**Lee más:**

- [Seguridad basada en capacidades](https://en.wikipedia.org/wiki/Capability-based_security) (Wikipedia)
- [Principio de mínimo privilegio](https://en.wikipedia.org/wiki/Principle_of_least_privilege) (Wikipedia)
- [Problema del delegado confundido](https://en.wikipedia.org/wiki/Confused_deputy_problem) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`ed-weird`](../../src/ed-weird/README.md) | ed, SQLite | demuestra | Que un editor de líneas es una máquina de reescritura: las líneas son los datos, las direcciones son el programa y una sustitución fallida dentro de un comando global es un "si". |
| [`ex-weird`](../../src/ex-weird/README.md) | Ex, SQLite | demuestra | Que los registros de un editor pueden contener un programa: una línea de texto se copia en un registro y se ejecuta con @, y las marcas y las direcciones de línea del propio editor hacen la aritmética. |
| [`tar-gnu`](../../src/tar-gnu/README.md) | GNU tar, SQLite | demuestra | Que un archivo tar puede ser un programa serializado: tar lee los miembros en orden y solo el comando que indica el operador les da un efecto. |
