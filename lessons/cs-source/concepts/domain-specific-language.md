---
title: "Lenguajes específicos de dominio"
chapter: 5
order: 70
---
Un lenguaje específico de dominio (DSL) es un lenguaje pequeño para una clase de tarea. SQL sirve para consultas, las expresiones regulares para patrones, Make para compilaciones, AWK para registros y la sintaxis de consultas de LINQ para colecciones. Una herramienta que habla con el vocabulario del problema es más breve, más fácil de leer y a menudo más segura que el código de propósito general. Hay un peligro clásico. Los usuarios piden variables, luego condiciones y después bucles. Sin querer, el DSL acaba convertido en un lenguaje de propósito general, con menos herramientas y peores mensajes de error. Quienes programan lo llaman el *efecto de plataforma interna*. La mayoría de las entradas de aquí son DSL que cruzaron esa línea. Por eso fue divertido escribirlas.

- **Úsalos cuando:** el dominio tenga un vocabulario estable y lo usen muchas personas.
- **Evítalos cuando:** una biblioteca en un lenguaje común haga lo mismo. Si tu DSL necesita bucles, vuelve a considerar la posibilidad de integrarlo en un lenguaje de propósito general.

**Lee más:**

- [Lenguaje específico de dominio](https://en.wikipedia.org/wiki/Domain-specific_language) (Wikipedia)
- [Efecto de plataforma interna](https://en.wikipedia.org/wiki/Inner-platform_effect) (Wikipedia)
