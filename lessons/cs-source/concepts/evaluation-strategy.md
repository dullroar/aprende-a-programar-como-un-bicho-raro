---
title: "Estrategias de evaluación"
chapter: 4
order: 10
---
Una estrategia de evaluación responde a una pregunta: ¿*cuándo* se calcula un argumento? ¿Antes de la llamada (llamada por valor, también llamada evaluación inmediata)? ¿La primera vez que hace falta, para luego guardar el resultado (llamada por necesidad, también llamada evaluación perezosa)? ¿Cada vez que se usa (llamada por nombre)? La respuesta cambia el significado de un programa en cuanto hay efectos o datos infinitos. `f(g(x))` se ve igual en todos los lenguajes. Su comportamiento cambia. Todo este capítulo trata esa diferencia: [[entry:haskell]] usa evaluación perezosa, [[entry:apl]] usa evaluación inmediata y LINQ usa ejecución *diferida*.

- **Úsala cuando:** leas un lenguaje que no conoces. Averigua primero cuál es su estrategia predeterminada.
- **Evita suponer** que tus hábitos de un lenguaje se aplican en otro.

**Lee más:**

- [Estrategia de evaluación](https://en.wikipedia.org/wiki/Evaluation_strategy) (Wikipedia)
- [Llamada por necesidad](https://en.wikipedia.org/wiki/Call-by-need) (Wikipedia)
- [Llamada por nombre](https://en.wikipedia.org/wiki/Call-by-name) (Wikipedia)
