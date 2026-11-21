---
title: "Evaluación inmediata"
chapter: 4
order: 20
---
La evaluación inmediata calcula un valor en cuanto el código lo pide. Es la opción predeterminada en la mayoría de los lenguajes. Su ventaja es la sencillez: el costo y el orden son fáciles de predecir y los efectos ocurren justo donde los escribiste. [[entry:apl]] evalúa de inmediato en un sentido fuerte: cada primitiva trabaja sobre un arreglo entero a la vez. La entrada saca cinco números, un límite que nunca se queda corto aunque a menudo necesite menos. "Saca de sobra y recorta" sustituye al bucle que decide cuándo parar.

- **Úsala cuando:** necesites un orden predecible de los efectos o sepas con certeza que se usará el resultado.
- **Evítala cuando:** el trabajo pueda desperdiciarse o la fuente sea enorme o infinita.

**Lee más:**

- [Evaluación inmediata](https://en.wikipedia.org/wiki/Eager_evaluation) (Wikipedia)
- [[lazy-evaluation]], la idea opuesta
