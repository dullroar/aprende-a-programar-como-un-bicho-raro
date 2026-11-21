---
title: "Especificación frente a implementación"
chapter: 1
order: 70
---
La especificación de un lenguaje dice qué *significan* los programas. Una implementación es un programa concreto que intenta seguirla. Pueden diferir y en esa diferencia vive este libro. Cada lección etiqueta un truco como **garantizado** (la especificación lo promete) o **permitido por la implementación** (un compilador o una plataforma lo permite). La tercera etiqueta es **aprovechado por accidente** (hoy funciona y nadie lo prometió). El IETF dio a los ingenieros un vocabulario útil para la misma idea: MUST, SHOULD y MAY, definidos en el RFC 2119. Una especificación que usa esas palabras con cuidado te dice con exactitud cuánto puedes confiar en ella.

- **Úsala cuando:** vayas a depender de un comportamiento. Pregunta cuál de las tres clases de promesa lo respalda.
- **Evítala cuando:** necesites evidencia de rendimiento. Una ejecución en una máquina solo demuestra lo que sucedió allí.

**Lee más:**

- [Especificación de lenguajes de programación](https://en.wikipedia.org/wiki/Programming_language_specification) (Wikipedia)
- [RFC 2119: palabras clave para el uso en los RFC](https://www.rfc-editor.org/rfc/rfc2119), dos páginas que fijan el significado de MUST, SHOULD y MAY
- [[undefined-behavior]] y [[hyrums-law]] en "Fugas de abstracción y dependencia de la implementación"
