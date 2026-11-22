# Haskell

Entradas: [`src/haskell`](../../src/haskell/README.md) (una función pura) y [`src/haskell-weird`](../../src/haskell-weird/README.md) ("Haskell bajo los efectos de las drogas": leer la lista hace el trabajo).

Para una ruta de lectura avanzada con trazas y experimentos, consulta la [guía de estudio de Haskell](../guias-de-estudio/lenguajes/haskell.md).

## Qué hace especial a Haskell

Haskell es **perezoso**: un valor se calcula solo cuando algo lo demanda. La entrada ordinaria usa eso para una regla de parada que no es una condición de bucle, sino *cuánto eliges leer de una lista*.

| Característica | Dónde | Qué enseña |
| --- | --- | --- |
| Listas infinitas como descripciones | [`haskell/timecards.hs` L41](../../src/haskell/timecards.hs#L41): `rolls = map toHours . tail . iterate next` | `iterate` produce un flujo sin fin. Es una receta, no datos. |
| Sumas acumuladas sobre un flujo | [L49](../../src/haskell/timecards.hs#L49): `zipWith3 Card (cycle [minBound ..]) hs (scanl1 (+) hs)` | `scanl1 (+)` es un total acumulado; `cycle [minBound ..]` repite las categorías porque el tipo deriva `Enum` y `Bounded`. |
| La regla de parada es una división | [L56-59](../../src/haskell/timecards.hs#L56-L59): `under ++ take 1 over where (under, over) = span ((<= 40) . runningTotal) (allCards seed)` | `span` lee una tarjeta a la vez y se detiene en la primera que no cumple. `takeWhile` descartaría la tarjeta que cruza el tope; `span` devuelve ambas mitades. |
| La aritmética con desbordamiento circular es una característica | `rolls` usa un LCG de 64 bits sobre `Word64` | "mod 2^64" sale gratis porque `Word64` se desborda de forma circular. |

## La E/S perezosa como flujo de control

### Contempla la monstruosidad

```bash
sandbox/container/run-image.sh src/haskell-weird
```

Una lista infinita de tarjetas. *Forzar la n-ésima celda imprime la tarjeta n y envía su `INSERT` a `sqlite3`.* Nada más escribe una fila. No hay bucle, acumulador, contador ni recursión explícita.

### ¿Cómo demonios funciona eso?

Tres trucos apilados.

1. **Una lista definida en términos de sí misma.** [L53](../../src/haskell-weird/timecards.hs#L53): `rolls seed = map toHours (tail (fix (\xs -> seed : map next xs)))`. `fix f = f (fix f)` le entrega a una función su propio resultado, así que `xs = seed : map next xs`. Funciona porque `map` necesita solo un elemento a la vez.
2. **Un nudo a través de las tarjetas.** [L75-78](../../src/haskell-weird/timecards.hs#L75-L78): `sheet onBirth seed = fixIO $ \cards -> let before = 0 : map runningTotal cards ...`. El total de la tarjeta n es sus horas más el total *leído de la tarjeta n-1, un elemento de la lista en construcción*. `fixIO` es `fix` para IO.
3. **Efectos que esperan a que los pidan.** [L62-64](../../src/haskell-weird/timecards.hs#L62-L64): `lazily = fix $ \self actions -> unsafeInterleaveIO $ case actions of ...`. El `sequence` ordinario ejecuta primero todas las acciones, y eso nunca termina con una lista infinita. `unsafeInterleaveIO` significa "ejecuta esto solo cuando alguien demande su resultado". Cuando `sheet` regresa, nada se ha ejecutado; cada celda es una promesa.

La regla de parada es [`untilOver40` (L82-83)](../../src/haskell-weird/timecards.hs#L82-L83): `under ++ take 1 over`. Leer la tarjeta n ejecuta `onBirth` para la tarjeta n, así que el total de lecturas es igual al total de `INSERT` por construcción.

### ¿Qué acabamos de aprender?

- **El orden de evaluación forma parte del significado de un programa cuando intervienen efectos.** En un programa puro no importa. Pon IO detrás de una celda perezosa y ese orden decide *qué filas existen*.
- **La transparencia referencial es un contrato, y `unsafe...` es el punto donde dejas de respetarlo.**
- **"¿Cuándo se ejecuta esto?" es la misma pregunta** que la ejecución diferida de LINQ (consulta [C#](csharp-linq-xaml.md#la-ejecución-diferida-y-el-truco-de-convertir-void-en-valor)). En ambos casos, una descripción se separa de su ejecución.

Etiquetas: la pereza de `span` es comportamiento **garantizado** por la semántica del lenguaje. El orden de `unsafeInterleaveIO` es comportamiento **permitido por la implementación**: el programa es correcto porque la tarjeta n no puede forzarse antes que la tarjeta n-1, no porque el evaluador prometa un orden.

### Haz esto en producción y estás despedido

- **La historia de guerra del propio README.** El primer borrador contaba con `let entries = length cards`, y el programa imprimió `# committed total=Meetings 12 12 ...` y luego falló con "handle is closed". Como `let` era perezoso, nada forzó las tarjetas hasta que se imprimió el resumen, cuando la tubería ya estaba cerrada. Los efectos de las tarjetas se dispararon *durante la salida de `show`*. La solución: [L144](../../src/haskell-weird/timecards.hs#L144) `entries <- evaluate (length cards)`.
- **`lazily` debe diferir su propia coincidencia de patrón.** Si el `case` se ejecuta antes de `unsafeInterleaveIO`, forzarlo necesita `before`, que necesita `cards`, que todavía no existe: `<<loop>>`.
- **`take 1 over` dispara un efecto más.** Hay que leer la tarjeta que cruza el tope para ver que lo cruza, así que se escribe su fila. La pereza hace visible el error por uno.
- **Pruebas y concurrencia.** Los efectos cuyo momento depende del consumidor no se pueden probar sin el consumidor, y no se pueden compartir de forma segura.

Usos legítimos: la E/S perezosa existe para el flujo continuo (`getContents` sobre una entrada de datos grande), y los mismos peligros explican por qué la gente migró a bibliotecas de flujo continuo. Atar nudos (`fix`) es una técnica respetable para datos autorreferenciales, como estructuras circulares y tablas de memoización.

### Ahora rómpelo tú

Consulta los [ejercicios](../exercises.md#b2-haskell-rompe-la-pereza-verificado): reemplaza `unsafeInterleaveIO` por IO simple o mueve el `evaluate`. Después predice la salida.

## Peculiaridades

- **`takeWhile` no basta**: descarta la tarjeta que cruza el tope. `span` conserva ambas mitades.
- **Funciones parciales.** `head`, `last` y `!!` fallan con una lista vacía; ninguno de los dos programas las usa.
- **`Int` frente a `Integer` frente a `Word64`.** El generador necesita exactamente 64 bits sin signo, así que usa `Word64`, cuyo desbordamiento circular es la característica buscada.
- **GHC no incluye un paquete de números aleatorios.** Ambas entradas construyen a mano un generador congruencial lineal (con las constantes MMIX de Knuth) y usan los bits altos.
- **Sorpresas al estilo de `hGetContents`.** La entrada rara convierte en algoritmo la sorpresa más famosa de la entrada y salida perezosa de Haskell.
- **Herramientas de estilo.** El código fuente está formateado a mano al estilo de Ormolu y compila sin problemas con `-Wall -Wcompat`, pero *no* se ejecutó mediante `ormolu` ni `hlint`.
- **`check.sh` como restricción.** [`haskell-weird/check.sh`](../../src/haskell-weird/check.sh) prohíbe `scanl iterate foldr foldl unfoldr until go mapM forM forever replicateM foldM zipWithM sequence` y exige `fixIO $ \cards ->` y exactamente un `unsafeInterleaveIO`.

## Lo raro junto a lo aburrido

[`haskell`](../../src/haskell/README.md) es una función pura más cómo viaja el dato: es fácil de probar y razonar. [`haskell-weird`](../../src/haskell-weird/README.md) pone los efectos dentro de la estructura de datos. La versión rara revela algo que la idiomática oculta: una lista perezosa es un *programa que espera ser leído*.

## ¿En qué circunstancias esta idea terrible se volvería razonable?

Dentro de una biblioteca que implementa el procesamiento perezoso de flujos y que se ha probado cuidadosamente para comprobar el orden. No en el código de aplicación, donde `evaluate`, la entrada y salida estricta y las bibliotecas de procesamiento de flujos dan los mismos resultados sin sorpresas.

<!-- BEGIN GENERATED program-flow:languages/haskell.md -->
## Cómo corre cada programa

Cada imagen de abajo es la sección `## Flujo del programa` del README de una entrada, copiada aquí por la compilación. Muestra cómo ese programa hace el trabajo: lo que el lenguaje, el entorno de ejecución o la herramienta hacen en realidad. [La introducción](../introduccion.md#qué-hace-el-reto) muestra qué pide el reto y en qué se distinguen las entradas.

### Flujo del programa de `haskell`

Desde [`haskell`](../../src/haskell/README.md) ([sección original](../../src/haskell/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: haskell: listas infinitas que se leen solo hasta donde llega la demanda de span
    accDescr: Un diagrama de flujo de datos y demanda. La función rolls es una lista infinita de horas, creada con iterate. Las categorías forman un ciclo infinito. Una suma acumulada de las horas da los totales. La función zipWith3 une las categorías, las horas y los totales en allCards, una lista infinita de tarjetas, ninguna construida todavía. La función span pide una tarjeta a la vez y se detiene en la primera tarjeta cuyo total pasa de 40. El resultado conserva las tarjetas anteriores y la primera tarjeta con más de 40. Después, la función main pasa los INSERT por una tubería a sqlite3 e imprime las filas.
    A["rolls: una lista infinita de horas, a partir de iterate next seed"] --> C["scanl1 (+): los totales acumulados"]
    A --> D
    B["ciclo de las cuatro categorías: se repite sin fin"] --> D
    C --> D["zipWith3 Card: allCards, una lista infinita de la que todavía no se ha construido nada"]
    D --> E["span (total <= 40): pide una tarjeta a la vez y se detiene en la primera que no cumple la condición"]
    E --> F["under ++ take 1 over: las tarjetas antes de 40 y la que lo cruza"]
    F --> G["main: envía los INSERT a sqlite3 mediante una tubería e imprime las filas"]
```

**Qué muestra:** las listas son descripciones, no datos. No se calcula nada hasta que `span` pide una tarjeta, y `span` deja de pedir en la primera tarjeta que no pasa la prueba. Por eso el programa construye solo unas pocas tarjetas, aunque las listas son infinitas.

**Por qué importa este mecanismo:** la regla de parada no es una condición de bucle. Es *cuánto de una lista eliges leer*. La demanda fluye hacia atrás, desde `span` hasta las listas, mientras que los datos fluyen hacia adelante. Esto es evaluación perezosa como forma de escribir un bucle sin escribir un bucle.

### Flujo del programa de `haskell-weird`

Desde [`haskell-weird`](../../src/haskell-weird/README.md) ([sección original](../../src/haskell-weird/README.md#flujo-del-programa)).

```mermaid
sequenceDiagram
    accTitle: haskell-weird: leer una celda de una lista perezosa ejecuta el efecto de esa tarjeta
    accDescr: Un diagrama de secuencia. El consumidor, span en untilOver40, demanda la siguiente celda de la lista perezosa de tarjetas. La celda necesita las horas del flujo aleatorio y el total acumulado de la tarjeta anterior. Como cada celda está envuelta en unsafeInterleaveIO, el efecto de esa tarjeta se ejecuta ahora, cuando se demanda la celda: imprime la fila y escribe el INSERT en la tubería. Después, la celda devuelve la tarjeta al consumidor. El consumidor comprueba el total acumulado. Mientras el total no pase de 40, demanda la siguiente celda. En la primera tarjeta que pasa de 40, el consumidor deja de demandar, así que ningún efecto posterior se ejecuta nunca, y main confirma la transacción.
    participant S as span, el consumidor
    participant C as la siguiente celda de la lista
    participant R as el flujo aleatorio y la tarjeta anterior
    participant E as onBirth, el efecto de la tarjeta
    loop mientras el total acumulado sea 40 o menos
        S->>C: demanda la siguiente tarjeta
        C->>R: necesitan las horas y el total de la tarjeta anterior
        R-->>C: las horas y el total, ya conocidos
        C->>E: unsafeInterleaveIO ejecuta el efecto ahora
        E-->>E: imprime la fila y escribe el INSERT en la tubería
        C-->>S: la tarjeta
    end
    Note over S: se devuelve y se conserva la primera tarjeta que pasa de 40. No se pide ninguna celda posterior, así que no se ejecuta ningún efecto posterior
    S-->>S: main confirma la transacción e informa
```

**Qué muestra:** los efectos están ligados a la *lectura* de la lista. La lista está construida para que no se ejecute nada al crearla. Cada celda guarda una promesa, y forzar la celda ejecuta el `onBirth` de esa tarjeta. Así, el número de filas impresas es igual al número de `INSERT`, que es igual al número de tarjetas leídas.

**Por qué importa este mecanismo:** este es un flujo de control dirigido por la demanda y con efectos secundarios, y solo es seguro por cómo están enlazadas las celdas. `unsafeInterleaveIO` se llama *unsafe* por una razón: el orden de los efectos ahora depende del orden de la demanda. La misma evaluación perezosa sin efectos aparece en la entrada simple de [`haskell`](../../src/haskell/README.md).
<!-- END GENERATED program-flow:languages/haskell.md -->

## Ciencias de la computación detrás de esta página

<!-- BEGIN GENERATED concepts:languages/haskell.md -->
Las ideas de ciencias de la computación detrás de esta página: [Flujo de control](../informatica/03-flujo-de-control-y-continuaciones.md#flujo-de-control), [Estrategias de evaluación](../informatica/04-evaluacion-y-demanda.md#estrategias-de-evaluación), [Evaluación perezosa](../informatica/04-evaluacion-y-demanda.md#evaluación-perezosa), [Iteradores y generadores](../informatica/04-evaluacion-y-demanda.md#iteradores-y-generadores), [Transparencia referencial](../informatica/04-evaluacion-y-demanda.md#transparencia-referencial), [Funciones de primera clase y de orden superior](../informatica/04-evaluacion-y-demanda.md#funciones-de-primera-clase-y-de-orden-superior), [Monoides y plegados](../informatica/04-evaluacion-y-demanda.md#monoides-y-plegados), [Estado](../informatica/06-estado-mas-alla-de-las-variables.md#estado), [Efectos secundarios](../informatica/07-efectos-errores-y-confirmacion.md#efectos-secundarios), [Mónadas y sistemas de efectos](../informatica/07-efectos-errores-y-confirmacion.md#mónadas-y-sistemas-de-efectos).
<!-- END GENERATED concepts:languages/haskell.md -->
