---
title: "Funciones de primera clase y de orden superior"
chapter: 4
order: 85
---
Un lenguaje tiene **funciones de primera clase** cuando una función es un valor. Puedes guardarla, pasarla como argumento, devolverla desde otra función y almacenarla en una estructura de datos. Una **función de orden superior** recibe una función, devuelve una función o hace ambas cosas. `map`, `filter` y `reduce` reciben funciones. Una función que construye otra ya configurada, como una fábrica de contadores, devuelve una función.

La idea existe porque permite separar *qué hacer con cada elemento* de *cómo recorrer los elementos*. El recorrido puede usar evaluación perezosa o inmediata, ir en paralelo o detenerse antes. El código que dice qué hacer queda igual. [[entry:haskell]] describe las tarjetas con `zipWith3` y `scanl1`. [[entry:LinqChallenge1]] encadena `Select` y `Aggregate`. [[entry:RustChallenge1]] dirige un bucle con iteradores y clausuras (*closure*), funciones que conservan acceso a su entorno. [[entry:javascript-weird]] sigue la misma forma de principio a fin: una canalización de llamadas a `map` que reciben clausuras y que termina con `toArray`, seguida de un `reduce` sobre la lista completa.

El precio es que hay que leer el código de otro modo. Cuando el recorrido queda oculto en una llamada de biblioteca, no ves en qué orden ni cuántas veces se ejecutan las funciones de devolución de llamada (*callback*). Tampoco ves si el recorrido se detiene antes de terminar. Eso importa cuando la función de devolución de llamada tiene un efecto. `reduce` no puede detenerse antes, pero `some` sí. El `map` perezoso de un iterador procesa un valor a la vez. El `map` de un arreglo termina cada etapa antes de que empiece la siguiente ([[entry:javascript-weird]] muestra ambos órdenes).

- **Úsalas cuando:** el trabajo de cada elemento sea independiente del recorrido o quieras reutilizar un recorrido con muchas funciones de devolución de llamada.
- **Evítalas cuando:** la función de devolución de llamada tenga efectos ocultos y el orden importe. Anota el orden o usa un bucle sencillo y explica por qué.

**Lee más:**

- [Función de primera clase](https://en.wikipedia.org/wiki/First-class_function) (Wikipedia)
- [Función de orden superior](https://en.wikipedia.org/wiki/Higher-order_function) (Wikipedia)
- [Funciones](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions) (MDN)
