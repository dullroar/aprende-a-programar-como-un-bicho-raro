# Forth

Entradas: [`src/forth`](../../src/forth/README.md) (un `begin ... until`) y [`src/forth-weird`](../../src/forth-weird/README.md) (sin palabra de bucle ni variable).

Para un recorrido avanzado de lectura con trazas y experimentos, consulta la [guía de estudio de Forth](../guias-de-estudio/lenguajes/forth.md).

## Qué hace especial a Forth

Forth casi no tiene sintaxis: el intérprete lee una palabra delimitada por espacios, la busca y la ejecuta. Las palabras pasan valores en una **pila**, y cada definición lleva un comentario de pila como `( hours -- )`. El lenguaje es lo bastante pequeño para que puedas acceder al propio intérprete.

| Característica | Dónde | Qué enseña |
| --- | --- | --- |
| Un switch es un arreglo de funciones | [`forth/timecards.fs` L34-36](../../src/forth/timecards.fs#L34-L36): `create categories ' meetings , ...` y `: category$ ( n -- c-addr u ) 4 mod cells categories + @ execute ;` | `'` ("tick") da el token de ejecución de una palabra; los tokens son datos. |
| La redirección de salida como característica | [L68](../../src/forth/timecards.fs#L68): `: >sqlite ( xt -- ) sqlite outfile-execute ;` | `outfile-execute` redirige toda la salida a una tubería durante ese tiempo. `.schema` y `.insert` son palabras ordinarias que imprimen texto, y la tubería convierte el texto en SQL. |
| Una palabra de bucle | [L108](../../src/forth/timecards.fs#L108): `: run ( -- ) begin card over-40? until ;` | `until` consume una bandera y repite hasta que sea verdadera. |

## La posición de análisis sintáctico como contador de programa

### Contempla la monstruosidad

```bash
sandbox/container/run-image.sh src/forth-weird
```

El bucle de todo el programa ocupa una línea en el nivel superior ([L101](../../src/forth-weird/timecards.fs#L101)):

```forth
0 0 >in @ step rewind?                                     \ <== THE LOOP  ( n total anchor )
```

### ¿Cómo demonios funciona eso?

El intérprete de texto es un bucle que nunca ves. `>in` guarda *hasta dónde ha leído la línea actual*; `>in @` lee ese valor y `>in !` lo establece. Establécelo a un valor anterior y el intérprete vuelve a leer las mismas palabras.

- `0 0` es el estado inicial (tarjeta 0, total 0). `>in @` apila la posición como **ancla**: el lugar al que volverá el salto.
- `step` ([L88](../../src/forth-weird/timecards.fs#L88)) es `>r card r>`: guarda el ancla en la pila de retorno, ejecuta una tarjeta y la restaura.
- `rewind?` ([L92-94](../../src/forth-weird/timecards.fs#L92-L94)) termina con `over >in @ - and >in @ + >in !`. Una bandera de Forth es **-1** (todos los bits activados) para verdadero y **0** para falso. Así funciona como máscara de bits. `anchor - >in` es la distancia hacia atrás; `and` con la bandera conserva la distancia si es verdadera y la pone en cero si es falsa. Al sumarla a `>in` se obtiene el ancla o "quedarse aquí". No hay `if`. El salto es aritmético.

La memoria es la pila de datos: no hay ni un solo `variable` en el archivo. El contador de programa es `>in`.

### ¿Qué acabamos de aprender?

- **La posición de un intérprete puede ser un contador de programa.** Si puedes leerla y escribirla, tienes goto.
- **Los booleanos como máscaras de bits** son un viejo truco respetable. Explican por qué el valor verdadero de Forth es -1.
- **El estado en una pila** es un modelo completo de memoria. (Compara [el salto mutable de COBOL](cobol.md#alter), [el estado de existencia de archivos de Make](make-cmake.md#gnu-make) y [los registros de CMake](make-cmake.md#cmake).)

Etiquetas: los efectos de pila y las banderas son comportamiento **garantizado** por Forth estándar. La existencia de la manipulación de `>in` es un comportamiento **garantizado** en ISO Forth. Pero su efecto en una definición frente al nivel superior es **permitido por la implementación**. `outfile-execute`, `open-pipe` y `utime` son extensiones de Gforth (**permitido por la implementación**).

### Haz esto en producción y estás despedido

- **Solo funciona en el nivel superior o en texto procesado con `evaluate` o `included`.** `>in` es la posición de análisis de la línea actual de entrada de datos. Compila el bucle *dentro* de una palabra y no habrá ninguna línea que rebobinar.
- **Mover un token lo rompe sin aviso.** Si `0 0` se mueve *después* de `>in @` (`>in @ 0 0 step rewind?`), el ancla queda antes del estado. Por eso, cada rebobinado apila un nuevo `0 0`: el total vuelve a cero en cada pasada y el programa nunca se detiene (verificado: cientos de filas, sin línea `# committed`). Un programa que parece correcto y un bucle desbocado. Mover `0 0` a la línea anterior no causa daño, porque el ancla sigue después de él.
- **Ninguna herramienta lo entenderá.** Los analizadores, trazadores y humanos suponen que la posición de análisis no es estado.
- **Portabilidad.** Palabras específicas de Gforth; `3dup` no está en Gforth 0.7.3, así que el archivo la define con `2 pick` tres veces ([L37](../../src/forth-weird/timecards.fs#L37)).

Usos legítimos: intérpretes, depuradores y palabras de análisis sintáctico, donde la tarea es manipular el flujo de entrada de datos.

### Ahora rómpelo tú

Consulta los [ejercicios](../exercises.md#b3-forth-mueve-el-ancla-verificado).

## Peculiaridades

- **Las palabras de control solo funcionan dentro de definiciones** en Forth estándar. Escribir `begin ... until` en el nivel superior es un error, por eso `run` es una palabra. La versión rara hace trampa en el otro sentido.
- **Las cadenas de texto `s"` pueden ser temporales**: algunos intérpretes devuelven un búfer que la siguiente sobrescribe, por eso las palabras de categoría son definiciones.
- **`random` es `0..n-1`**, por eso `10 random 10 +` da de 10 a 19.
- **`close-pipe` devuelve el estado de salida**; `close-sqlite` convierte un estado distinto de cero en una interrupción para que un `sqlite3` fallido no se ignore.
- **Los comentarios de pila son el sistema de tipos.** Nada hace cumplir `( n total -- n' total' )`; es una convención.

## Lo raro junto a lo aburrido

[`forth`](../../src/forth/README.md) es un programa de pila limpio: palabras pequeñas, un bucle. [`forth-weird`](../../src/forth-weird/README.md) reemplaza cada `variable` y palabra de control por la posición en la pila y un analizador sintáctico rebobinado. El primero es lo que escriben los programadores de Forth; el segundo es lo que Forth *permite*.

## ¿En qué circunstancias esta idea terrible se volvería razonable?

Cuando escribes el intérprete, una palabra de análisis sintáctico o un depurador. Rebobinar el analizador sintáctico es una acrobacia en un bucle; es una herramienta para quien implementa un lenguaje.

<!-- BEGIN GENERATED program-flow:languages/forth.md -->
## Cómo corre cada programa

Cada imagen de abajo es la sección `## Flujo del programa` del README de una entrada, copiada aquí por la compilación. Muestra cómo ese programa hace el trabajo: lo que el lenguaje, el entorno de ejecución o la herramienta hacen en realidad. [La introducción](../introduccion.md#qué-hace-el-reto) muestra qué pide el reto y en qué se distinguen las entradas.

### Flujo del programa de `forth`

Desde [`forth`](../../src/forth/README.md) ([sección original](../../src/forth/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: forth: un solo bucle begin until sobre una palabra llamada card
    accDescr: Un diagrama de flujo. La palabra main hace la preparación: abre una tubería a sqlite3 y escribe el esquema. La palabra run es un bucle begin until. Cada pasada ejecuta card, que extrae las horas, las suma a la variable total, incrementa el conteo de tarjetas, imprime la fila y envía el INSERT por la tubería. Después, over-40? deja una bandera en la pila y until la consume. Si la bandera es falsa, el bucle se repite. Si es verdadera, run termina, y main confirma la transacción, cierra la tubería e informa.
    A["main: abre la tubería a sqlite3, escribe el esquema"] --> B["run: begin"]
    B --> C["card: extraer horas, sumar al total, incrementar tarjetas"]
    C --> D["Imprime la fila; envía el INSERT por la tubería"]
    D --> E{{"over-40? deja una bandera; until la consume"}}
    E -->|false| B
    E -->|true| F["main: confirma la transacción, cierra la tubería, informa"]
```

**Qué muestra:** Forth tiene un solo bucle ordinario, `begin ... until`. El cuerpo del bucle ejecuta `card` y después `over-40?` deja una bandera (un valor booleano) en la pila para que `until` la tome. El estado vive en dos variables, `total` y `cards`, y la pila de datos lleva valores entre palabras.

**Por qué importa este mecanismo:** la regla de parada es una bandera, no una condición en el encabezado del bucle. La bandera se calcula después de la tarjeta, así que la tarjeta con la que el total pasa del límite se conserva. El hermano raro [`forth-weird`](../../src/forth-weird/README.md) no tiene `begin` ni `until`.

### Flujo del programa de `forth-weird`

Desde [`forth-weird`](../../src/forth-weird/README.md) ([sección original](../../src/forth-weird/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: forth-weird: el intérprete de texto vuelve a leer las mismas palabras
    accDescr: Un diagrama de flujo. El intérprete de texto de Forth lee una línea: cero cero, luego at-in fetch, luego step y luego rewind-question. Cero cero apila el número de tarjeta y el total. At-in fetch apila la posición de análisis, que es el ancla. La palabra step ejecuta una tarjeta con el ancla guardada en la pila de retorno. La palabra rewind-question crea una bandera: menos uno mientras el total no pasa de 40 y cero en cualquier otro caso. Combina la bandera con la distancia de regreso al ancla y suma el resultado a la posición de análisis. Si la bandera era verdadera, la posición de análisis vuelve al ancla y el intérprete lee step otra vez. Si era falsa, la posición de análisis no cambia y el intérprete sigue con drop, commit y report.
    A["El intérprete lee: 0 0 #gt;in @ — la pila contiene n, el total y el ancla"] --> B["El intérprete lee la palabra step: ejecuta una tarjeta y mantiene el ancla en la pila de retorno"]
    B --> C["El intérprete lee rewind?: la bandera es -1 mientras el total no pasa de 40; en otro caso, es 0"]
    C --> D["Distancia de vuelta al ancla Y bandera, sumada a la posición de análisis #gt;in"]
    D --> E{{"¿Volvió la posición de análisis al ancla?"}}
    E -->|"sí: la bandera valía -1"| B
    E -->|"no: la bandera era 0"| F["El intérprete sigue leyendo: suelta el ancla, confirma la transacción e informa"]
```

**Qué muestra:** el bucle es el intérprete de texto, el bucle que nunca ves y el salto es un cambio en `>in`, el número que indica hasta dónde ha leído. Asignar un valor anterior a `>in` hace que el intérprete lea otra vez las mismas palabras. No existe `if`: una bandera de Forth es `-1` o `0`, así que `AND` convierte la distancia en sí misma o en nada.

**Por qué importa este mecanismo:** el contador de programa es una variable, y un programa puede reescribirla. El estado son dos números en la pila de datos, y sobreviven al retroceso porque nada más los toca. Esto funciona porque las palabras se leen de una línea de entrada, y no funciona igual dentro de una definición. Para el bucle ordinario, consulta [`forth`](../../src/forth/README.md).
<!-- END GENERATED program-flow:languages/forth.md -->

## Informática detrás de esta página

<!-- BEGIN GENERATED concepts:languages/forth.md -->
Las ideas de ciencias de la computación detrás de esta página: [Máquinas de pila](../informatica/02-que-cuenta-como-maquina.md#máquinas-de-pila), [Máquinas de registros y máquinas de contadores](../informatica/02-que-cuenta-como-maquina.md#máquinas-de-registros-y-máquinas-de-contadores), [Flujo de control](../informatica/03-flujo-de-control-y-continuaciones.md#flujo-de-control), [El contador de programa](../informatica/03-flujo-de-control-y-continuaciones.md#el-contador-de-programa), [Análisis sintáctico](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#análisis-sintáctico), [Estado](../informatica/06-estado-mas-alla-de-las-variables.md#estado), [La pila como estructura de datos](../informatica/06-estado-mas-alla-de-las-variables.md#la-pila-como-estructura-de-datos), [Reflexión y metaprogramación](../informatica/06-estado-mas-alla-de-las-variables.md#reflexión-y-metaprogramación), [Transacciones](../informatica/07-efectos-errores-y-confirmacion.md#transacciones).
<!-- END GENERATED concepts:languages/forth.md -->
