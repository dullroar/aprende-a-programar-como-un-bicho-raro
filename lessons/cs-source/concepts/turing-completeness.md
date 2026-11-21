---
title: "Completitud de Turing"
chapter: 2
order: 100
---
Un sistema es Turing completo si puede simular cualquier máquina de Turing (con memoria ilimitada). En palabras sencillas: puede calcular lo que calcula un computador de propósito general. A la gente le gusta encontrar esta propiedad en lugares sorprendentes: Make, sed, m4, hojas de cálculo, incluso software de diapositivas. Ese es el espíritu de este repositorio. Pero la propiedad tiene un precio. Si una notación es Turing completa, no puedes decidir en general qué harán sus programas (teorema de Rice). Por eso la gente de seguridad prefiere entradas de datos que *no* sean potentes. Mira [[langsec]]. La comunidad web llama a esto la *regla del menor poder*: elige el lenguaje menos potente que resuelva el problema.

- **Úsala cuando:** quieras conocer el techo de una notación, o explicar por qué un "lenguaje de configuración" puede ejecutarse para siempre.
- **Evita usarla como elogio:** "es Turing completo" es tantas veces una advertencia como un cumplido.

**Más información:**

- [Completitud de Turing](https://en.wikipedia.org/wiki/Turing_completeness) (Wikipedia)
- [Teorema de Rice](https://en.wikipedia.org/wiki/Rice%27s_theorem) (Wikipedia)
- [Regla del menor poder](https://en.wikipedia.org/wiki/Rule_of_least_power) (Wikipedia)
