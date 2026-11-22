# ed y Ex

Entradas: [`src/ed-weird`](../../src/ed-weird/README.md) (el búfer es la máquina) y [`src/ex-weird`](../../src/ex-weird/README.md) (un programa que puedes editar). `ed` es el editor de líneas original de Unix, de 1969 a 1971. Le indicas qué líneas (una *dirección*) y qué hacer con ellas (un *comando*). No tiene pantalla. Todo lo que hace a un archivo, lo hace a un **búfer** de líneas en memoria, un comando a la vez. Los comandos son tan generales que el programa de este libro no contiene nada más. `ex` es su descendiente más grande: el lenguaje de comandos de `vi`. Añade registros, marcas, `@` y la barra.

Para un recorrido avanzado de lectura con trazas y experimentos, consulta la [guía de estudio de ed y Ex](../guias-de-estudio/lenguajes/ed-y-ex.md).

## Qué hace especial a ed

| Característica | Qué enseña |
| --- | --- |
| Direcciones: `3`, `.`, `$`, `.-1`, `/re/` | Se llega a una línea por número, posición o patrón. Una dirección es una referencia a los datos, como un puntero o un índice. |
| `s/re/text/` | La sustitución es una reescritura condicional. Si el patrón coincide, el texto cambia. Si no, no pasa nada. |
| `g/re/command-list` | El comando global marca cada línea que coincide y luego ejecuta los comandos para cada una, en orden. Es el único bucle de ed. |
| `t`, `m`, `j`, `d` | Copiar, mover, unir y borrar líneas completas: la forma en que ed construye y deshace datos. |
| Sin aritmética ni variables | Los números deben escribirse como texto. En la entrada son filas de marcas. |

## El búfer es la máquina

### Contempla la monstruosidad

```bash
sandbox/container/run-image.sh src/ed-weird
```

Setenta líneas de comandos de ed. Un lanzador que proporciona cinco dígitos aleatorios y guarda la respuesta. Todo el cómputo consiste en que el editor cambia texto.

### ¿Cómo demonios funciona eso?

- **El orden de las categorías es el direccionamiento.** `1s/^/Meetings /` coloca un nombre en la línea 1 y `2s/^/Coding /` en la línea 2.
- **Una tabla de reescritura hace la búsqueda.** Hay diez reglas: `g/x7$/s/7$/xxxxxxx/` y nueve más. Un dígito se convierte en esa cantidad de marcas.
- **Un marcador inicia el registro.** `Start 0|` aporta el total cero encima de la primera tarjeta. Después de la pasada, `g/^Start /d` elimina ese marcador de la salida.
- **Sumar es escribir marcas una al lado de otra.** `-t.` copia la línea anterior (el total acumulado), `-,.j` la une a la tarjeta y un `s` junta ambos grupos de marcas.
- **Un `s` fallido es un `if`.** Dentro de un comando global no hace nada ni detiene la lista. Así, cada sustitución significa "si la línea tiene esta forma, reescríbela".
- **La regla de parada es una expresión regular.** `x\{41,\}` significa "41 o más marcas". La barra antes de las marcas se convierte en un signo de exclamación. La siguiente tarjeta ve el signo y se convierte en una línea `Dead`.

El [README](../../src/ed-weird/README.md#cómo-funciona-el-truco) contiene la tabla completa.

**Un sistema de reescritura con otro control.** [`regex-sed`](regex.md#gnu-sed) también reescribe texto, pero sed tiene un comando de rama. Puede ejecutar un bucle hasta que ninguna regla se aplique. ed no puede. Su única repetición es `g` y su única elección es una sustitución que puede no encontrar coincidencia.

### ¿Qué acabamos de aprender?

- **Los números pueden ser texto.** Las marcas unarias hacen que la suma sea una concatenación. El precio es la longitud de la cadena de texto.
- **Una guarda es una condición.** "Reescribe solo si hay coincidencia" es `if` en un lenguaje que carece de ella.
- **Los datos pueden llevar el control.** Una barra o un signo de exclamación en una línea indica si la máquina sigue en ejecución. El estado viaja con los datos.
- **Las normas y las implementaciones difieren.** busybox ed es un `ed` y no puede ejecutar este programa: no tiene `g`, `t`, `j`, `#` ni coincidencia vacía.
- **Un obstáculo es un resultado.** Se rechaza `g` anidado. Una línea vacía es un comando. Conservamos una prueba para cada caso.

Etiquetas: los comandos `s`, `g`, `t`, `j`, `d` y `0a` están en POSIX. Que un `s` fallido dentro de `g` sea silencioso es conocimiento **aprovechado por accidente**: GNU ed 1.20.1 lo hace y su manual no lo dice. Los comentarios `#` son una extensión de GNU.

### Haz esto en producción y estás despedido

- **El sistema unario no escala.** Un millón es un millón de caracteres.
- **El programa depende de las posiciones.** Una línea de más entre una tarjeta y su libro de cuentas arruina todos los totales.
- **Nadie puede depurar diez reglas de reescritura a simple vista.** La entrada tiene una prueba que la compara con un modelo breve.

Usos legítimos: `ed` y `ex` en scripts para hacer ediciones exactas y automatizables (`ed -s file < commands`). Por ejemplo, un paso de compilación que debe cambiar una línea de un archivo de configuración.

### Ahora rómpelo tú

Consulta el [ejercicio B18](../exercises.md#b18-ed-mueve-la-regla-de-parada-y-rompe-la-limpieza-verificado).

## Un programa que puedes editar

### Contempla la monstruosidad

```bash
sandbox/container/run-image.sh src/ex-weird
```

Un script de unas 100 líneas, en su mayoría una tabla de sesenta líneas numeradas. El programa en sí es **una línea de texto**.

### ¿Cómo demonios funciona eso?

- **Una marca es un registro.** `k t` pone una marca en una línea. `'t+17k t` la mueve diecisiete líneas hacia abajo. Eso es `t = t + 17`.
- **La cinta es la recta numérica.** Sesenta líneas, cada una `total instruction`. La posición de la marca *es* el total acumulado; el texto de la línea expresa ese total en cifras.
- **El programa escribe su propio comando.** Una sustitución convierte la tarjeta `Meetings 7` en el texto `'t+17k t`. El programa copia ese texto en un registro y lo ejecuta con `@d`.
- **El bucle es un registro que se ejecuta a sí mismo.** El programa copia la línea numerada de la cinta al final del búfer. Elimina las cifras y el espacio siguiente con `$s/^[0-9]* //` y copia solo la instrucción al registro `n`. Con un total de exactamente 40 o menos es `@a`, que es el programa otra vez. Con más de 40 es una comilla, que indica un comentario, así que no se ejecuta nada.
- **Nada en el programa dice 40.** El límite es donde `@a` se detiene en la cinta.

El [README](../../src/ex-weird/README.md#cómo-funciona-el-truco) tiene la tabla de pasos, la comparación con la entrada de ed y los cinco puntos en los que nvi y Vim discrepan.

### ¿Qué acabamos de aprender?

- **El código es texto, así que se puede construir.** Un programa puede escribir un comando como cadena de texto y ejecutarlo. Eso es `eval`.
- **El estado del editor es estado.** La línea actual, las marcas y los registros son memoria fuera del texto del búfer.
- **Una tabla de saltos es dato.** El siguiente paso se busca por dirección en una tabla; la tabla contiene la regla de parada.
- **No hay un solo Ex.** nvi y Vim discrepan en el orden de los registros, los comandos globales anidados, la impresión, los errores y los rangos inversos. El programa se escribió teniendo en cuenta los cinco.
- **El procesamiento por lotes no es interactivo.** Los mismos comandos deben ser correctos al primer intento, sin nadie que los observe.

Etiquetas: POSIX para Ex establece como **garantizado** el comportamiento de los comandos `@`, `k`, `ya`, `t`, `j`, `s`, la barra y el comentario `"`. La evidencia es la especificación. Que el programa se ejecute igual en nvi 1.81.6 y Vim 9.1 es **permitido por la implementación**: la comprobación cubrió esas dos implementaciones.

### Haz esto en producción y estás despedido

- **Un registro que ejecuta datos es `eval`.** Si la cinta viniera de un desconocido, ese desconocido escribiría tu programa. Aquí la cinta es fija y se comprueban los dígitos antes de que se acerquen a un comando.
- **Las marcas son frágiles.** Una marca en una línea eliminada desaparece, al igual que tu contador.
- **El script depende de la versión de Ex que tengas.** Un script que funciona en una puede no funcionar en la otra. Prueba con ambas.

Usos legítimos: `ex -s` en scripts para hacer ediciones exactas y registros como un pequeño sistema de macros para ediciones repetidas en `vi`.

### Ahora rómpelo tú

Mira el [ejercicio B19](../exercises.md#b19-ex-mueve-el-límite-en-la-cinta-y-corta-el-bucle-verificado).

<!-- BEGIN GENERATED program-flow:languages/editors.md -->
## Cómo corre cada programa

Cada imagen de abajo es la sección `## Flujo del programa` del README de una entrada, copiada aquí por la compilación. Muestra cómo ese programa hace el trabajo: lo que el lenguaje, el entorno de ejecución o la herramienta hacen en realidad. [La introducción](../introduccion.md#qué-hace-el-reto) muestra qué pide el reto y en qué se distinguen las entradas.

### Flujo del programa de `ed-weird`

Desde [`ed-weird`](../../src/ed-weird/README.md) ([sección original](../../src/ed-weird/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: ed-weird: un comando global sobre un búfer de texto
    accDescr: Un diagrama de flujo. El lanzador entrega a ed cinco dígitos aleatorios como un búfer de cinco líneas. El script añade una categoría a cada línea según su dirección de línea, reescribe cada dígito como horas y una serie de marcas con una tabla de sustituciones, y añade una línea de registro encima de la primera tarjeta. Luego un comando global visita cada línea de tarjeta en el orden del búfer. Para cada tarjeta, copia el registro de arriba, une las líneas y fusiona las marcas, lo que suma las horas. Después, unas sustituciones condicionadas cambian la barra del registro por un signo de exclamación cuando hay 41 marcas o más, y convierten en tarjeta muerta cualquier tarjeta posterior. Cuando se han visitado todas las tarjetas, ed borra las líneas muertas y la de inicio, reescribe las marcas en decimal e imprime las filas. El lanzador las carga en SQLite.
    A["Lanzador: cinco dígitos aleatorios se convierten en el búfer de ed, una línea por tarjeta"] --> B["Tablas de reescritura: las direcciones de línea añaden categorías; un dígito se convierte en horas como marcas"]
    B --> C["Añade una línea de libro mayor encima de la primera tarjeta"]
    C --> D{{"g: ¿hay otra línea de tarjeta que visitar?"}}
    D -->|sí| E["Copia el registro de arriba, une, fusiona las marcas: sumar es escribir marcas una al lado de otra"]
    E --> F["Sustituciones con guarda: 41 o más marcas convierten la barra en !, una tarjeta después de ! pasa a ser Dead"]
    F --> D
    D -->|no| G["Elimina las líneas Dead y Start, pasa las marcas a decimal, imprime las filas"]
    G --> H["El lanzador carga las filas en SQLite"]
```

**Qué muestra:** `ed` tiene un solo bucle (el comando global `g`) y no tiene `if`. Una sustitución que no encuentra nada que reemplazar no hace nada; por eso cada sustitución con guarda significa "si la línea tiene este patrón, reescríbela". El estado es texto: marcas que se añaden al escribirlas una junto a otra.

**Por qué importa este mecanismo:** la regla de parada es una expresión regular sobre el registro (41 marcas o más) y se ejecuta *después* de escribir la tarjeta, así que la tarjeta del cruce se conserva. `!`, que la regla escribe, es un estado que leen las tarjetas posteriores. Es toda la memoria de "estamos por encima".

### Flujo del programa de `ex-weird`

Desde [`ex-weird`](../../src/ex-weird/README.md) ([sección original](../../src/ex-weird/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: ex-weird: un registro que guarda el comando que lo ejecuta de nuevo
    accDescr: Un diagrama de flujo. El lanzador entrega a Ex cinco dígitos como tarjetas. El script añade bajo las tarjetas una cinta de sesenta líneas y el programa como una sola línea de texto, que copia en el registro a. Ejecutar el registro a inicia el bucle. El dígito de la primera tarjeta se reescribe como un comando que baja la marca t por la cinta, y ejecutarlo suma las horas. El programa imprime la fila con el total de la línea de la cinta que está bajo la marca. Copia la instrucción de esa línea de la cinta en el registro n y borra la tarjeta usada. Después, ejecutar el registro n hace lo que dice la línea de la cinta. Si el total no pasa de 40, la línea indica ejecutar de nuevo el registro a. Si pasa de 40, la línea es un comentario, así que no se ejecuta nada y el script termina.
    A["El lanzador da cinco dígitos; el script añade una cinta de 60 líneas y el programa como una sola línea, copiada en el registro a"] --> B["Ejecuta @a: reescribe el dígito de la primera tarjeta como un comando, 't+17 k t"]
    B --> C["Ejecuta ese comando: la marca t baja por la cinta y esa es la suma"]
    C --> D["Imprime la fila: la tarjeta y el total en la línea de la cinta bajo la marca t"]
    D --> E["Copia la instrucción de esa línea de la cinta en el registro n y elimina la tarjeta usada"]
    E --> F{{"Ejecución @n: ¿qué dice la línea de la cinta?"}}
    F -->|"@a: el total no pasa de 40"| B
    F -->|"una comilla: un comentario, el total pasa de 40"| G["No se ejecuta nada: el script termina y el lanzador carga las filas"]
```

**Qué muestra:** Ex guarda el estado fuera del texto, en marcas. También puede ejecutar un registro como comando. La posición de la marca `t` en una cinta *es* el total acumulado. La línea de la cinta que está debajo contiene la siguiente instrucción: `@a` (que significa "da otra vuelta") o una comilla, que Ex lee como comentario.

**Por qué importa este mecanismo:** este es código que se modifica a sí mismo. El programa escribe el comando que hace su aritmética, y la regla de parada es el lugar de la cinta donde `@a` se convierte en un comentario. Nada en el programa dice "40" en ninguna parte, salvo en cómo está dispuesta la cinta.
<!-- END GENERATED program-flow:languages/editors.md -->

## La informática detrás de esta página

<!-- BEGIN GENERATED concepts:languages/editors.md -->
Las ideas de ciencias de la computación detrás de esta página: [Especificación frente a implementación](../informatica/01-lectura-de-un-programa-adversarial.md#especificación-frente-a-implementación), [Capacidad y autoridad](../informatica/01-lectura-de-un-programa-adversarial.md#capacidad-y-autoridad), [Sistemas de transición y máquinas de estados](../informatica/02-que-cuenta-como-maquina.md#sistemas-de-transición-y-máquinas-de-estados), [Cómo representar el estado](../informatica/02-que-cuenta-como-maquina.md#cómo-representar-el-estado), [Máquinas de registros y máquinas de contadores](../informatica/02-que-cuenta-como-maquina.md#máquinas-de-registros-y-máquinas-de-contadores), [Algoritmos de Markov](../informatica/02-que-cuenta-como-maquina.md#algoritmos-de-markov), [Semántica operacional](../informatica/02-que-cuenta-como-maquina.md#semántica-operacional), [Cálculo frente a orquestación](../informatica/02-que-cuenta-como-maquina.md#cálculo-frente-a-orquestación), [El contador de programa](../informatica/03-flujo-de-control-y-continuaciones.md#el-contador-de-programa), [Código automodificable](../informatica/03-flujo-de-control-y-continuaciones.md#código-automodificable), [Expresiones regulares](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#expresiones-regulares), [Reescritura de términos y de cadenas de texto](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#reescritura-de-términos-y-de-cadenas-de-texto), [Máquinas raras](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#máquinas-raras), [Intérpretes y máquinas virtuales](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#intérpretes-y-máquinas-virtuales), [Estado](../informatica/06-estado-mas-alla-de-las-variables.md#estado), [Homoiconicidad: código como datos](../informatica/06-estado-mas-alla-de-las-variables.md#homoiconicidad-código-como-datos), [Reflexión y metaprogramación](../informatica/06-estado-mas-alla-de-las-variables.md#reflexión-y-metaprogramación), [Portabilidad](../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#portabilidad), [Ley de Hyrum](../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#ley-de-hyrum).
<!-- END GENERATED concepts:languages/editors.md -->
