---
title: "Reproducibilidad y compilaciones deterministas"
chapter: 8
order: 80
---
Un resultado es **reproducible** si la misma entrada de datos da la misma respuesta cada vez y en cualquier máquina. Una compilación es **determinista** si las mismas fuentes producen los mismos bytes. Ambas propiedades dependen de anotar todo lo que forma parte de la entrada: la semilla, el orden de los elementos, las versiones de las herramientas y la hora. De lo que olvides anotar saldrá la diferencia.

La compilación del libro que lees funciona así: ordena cada lista, nada consulta el reloj y un archivo de metadatos fija la fecha de compilación. Por eso las mismas fuentes dan los mismos bytes. Las entradas aplican la idea de cuatro maneras. [[entry:tar-gnu]] escribe un archivo tar con formato, orden, hora y propietario fijos. La misma semilla produce el mismo archivo byte por byte, como comprueba `cmp`. En [[entry:tar-gnu-weird]], la ejecución es función de una semilla y de la disposición del archivo. [[entry:javascript]] y [[entry:javascript-weird]] repiten una ejecución con `SEED=42`. No puedes fijar una semilla para `Math.random`, pero sí para una pequeña clausura (*closure*) que captura un número. Cada entrada dice qué significa "lo mismo": los bytes, la estructura o el comportamiento (consulta [[serialization-deserialization-pickling]]).

- **Úsala cuando:** debas depurar, probar o auditar un resultado más tarde. Explicita la entrada de datos y registra la semilla.
- **Evita confundirla** con el determinismo de *todo*. Una ejecución es reproducible en los aspectos que indicaste. Los demás quedan fuera, como la fecha asociada a un número de semana cerca de Año Nuevo.

**Lee más:**

- [Compilaciones reproducibles](https://en.wikipedia.org/wiki/Reproducible_builds) (Wikipedia)
- [Algoritmo determinista](https://en.wikipedia.org/wiki/Deterministic_algorithm) (Wikipedia)
