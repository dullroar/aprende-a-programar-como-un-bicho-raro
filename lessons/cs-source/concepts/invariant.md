---
title: "Invariantes"
chapter: 2
order: 40
---
Una invariante es un hecho que sigue siendo cierto en cada paso. No puedes probar todos los estados posibles de un programa. Pero *sí* puedes demostrar dos cosas: el hecho es cierto al inicio y cada paso lo mantiene cierto. Entonces lo es para siempre. En este repositorio, una regla de la base de datos como `CHECK(demo_only=1)` es una invariante de los datos. No puede existir una fila ajena a la demostración. Cada `check.sh` intenta romper la invariante para demostrar que la regla se cumple. Las invariantes de bucle funcionan igual: "el total hasta ahora equivale a la suma de las tarjetas que ya sacaste".

- **Úsala cuando:** diseñes un bucle, un esquema de datos, un algoritmo concurrente o una aserción.
- **Evítala cuando:** no puedas comprobar la afirmación o sea demasiado débil para servir.

**Lee más:**

- [Invariante (informática)](https://en.wikipedia.org/wiki/Invariant_(computer_science)) (Wikipedia)
- [Invariante de bucle](https://en.wikipedia.org/wiki/Loop_invariant) (Wikipedia)
