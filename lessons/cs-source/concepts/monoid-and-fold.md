---
title: "Monoides y plegados"
chapter: 4
order: 100
---
Un **monoide** es un tipo con una operación de combinación *asociativa* y un valor *neutro*. Los enteros con `+` y `0` forman un monoide. También lo forman las cadenas de texto con la concatenación y `""`. Un **plegado** (también llamado `reduce` o `Aggregate`) reduce una lista a un solo valor. Parte de un valor inicial y combina los elementos uno por uno.

Si la operación es asociativa, da igual cómo agrupes los elementos: `(a + b) + c = a + (b + c)`. Eso permite repartir un plegado entre hilos o reanudarlo desde un resultado parcial. Si hay un valor neutro, el plegado de una lista vacía tiene un resultado razonable: el valor inicial.

Un **barrido** (`scanl` en Haskell) es un plegado que conserva cada resultado parcial: `scanl (+) 0 [10,12,15]` es `[0,10,22,37]`. Un total acumulado es un barrido. [[entry:haskell]] usa `scanl1` para obtener cada total acumulado de las horas de las tarjetas. Luego usa `span` para tomar tarjetas hasta la que hace que el total pase de 40. Un plegado solo da el último total y no puede indicar dónde detenerse. En JavaScript, `reduce` es un plegado. No puede detenerse antes por sí solo, porque debe recorrer todo el arreglo (no tiene `break`). Para detenerse hace falta `some`, `find`, un generador u otra herramienta. [[entry:javascript-weird]] muestra cada opción.

Una operación asociativa difiere de una conmutativa. `"ab" + "c"` no es `"c" + "ab"`. Los plegados sobre monoides no conmutativos dependen del orden.

- **Úsalo cuando:** acumules un resultado y quieras saber si puedes dividirlo, combinarlo o reiniciar el cálculo.
- **Evítalo cuando:** necesites el primer elemento que pase una prueba. Un plegado que no se puede detener antes de tiempo hace trabajo de más o hace demasiado trabajo que no sirve.

**Lee más:**

- [Monoide](https://en.wikipedia.org/wiki/Monoid) (Wikipedia)
- [Plegado (función de orden superior)](https://en.wikipedia.org/wiki/Fold_(higher-order_function)) (Wikipedia)
- [Suma acumulada](https://en.wikipedia.org/wiki/Prefix_sum) (Wikipedia)
- [`Array.prototype.reduce()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce) (MDN)
