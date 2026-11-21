---
title: "Funtores y mapeo"
chapter: 4
order: 90
---
Un **funtor** es un tipo de contenedor con un `map` que aplica una función a los valores que contiene *sin cambiar la forma del contenedor*. Para que sea un funtor, `map` debe cumplir dos leyes:

- **Identidad:** `map(id, xs) = xs`. Aplicar una función que no cambia nada deja todo igual.
- **Composición:** `map(g ∘ f, xs) = map(g, map(f, xs))`. Aplicar dos funciones en una pasada equivale a aplicarlas una tras otra.

En Haskell las listas, `Maybe` y las funciones mismas son funtores (`fmap`). `Array.prototype.map` de JavaScript, `Select` de LINQ y un `Sequence.map` de Kotlin *parecen* funcionar así. Que cada uno cumpla las leyes depende de lo que haga la función. Si la función tiene un efecto secundario o lee un contador, la segunda ley falla en la práctica: los efectos ocurren en distinto orden. `[1,2,3].map(f).map(g)` ejecuta `f` tres veces y luego `g` tres veces. Una secuencia perezosa los intercala: `f(1), g(1), f(2), g(2), …`. Con funciones puras no puedes ver la diferencia. Con efectos sí. [[entry:javascript-weird]] guarda una fila dentro de un `map`. Así, el orden de evaluación perezosa define el programa y su script de comprobación muestra ambos órdenes.

La evaluación perezosa también varía. `map` de Python y un `Select` de LINQ son perezosos y no ejecutan nada hasta que alguien lo pide. `Array.prototype.map` de JavaScript usa evaluación inmediata y construye todo el resultado de una vez. `fmap` de Haskell aplicado a una lista vuelve a ser perezoso. El tipo de `map` es el mismo en todos los casos. La *evaluación* cambia.

- **Úsalo cuando:** quieras cambiar cada valor de una estructura y conservar la estructura. También cuando quieras una regla para saber cuándo puedes intercambiar dos canalizaciones.
- **Evítalo cuando:** la función tenga efectos. Usa un bucle o una operación que tenga en cuenta los efectos. Dilo para que el lector sepa que el orden importa.

**Lee más:**

- [Funtor](https://en.wikipedia.org/wiki/Functor) (Wikipedia)
- [`Array.prototype.map()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map) (MDN)
