---
title: "Expresiones regulares"
chapter: 5
order: 20
---
Una expresión regular es un patrón compacto para un conjunto de cadenas de texto. Stephen Kleene describió la idea en la década de 1950. Ken Thompson la incorporó a los editores de texto. De allí llegó a `grep`, `sed`, `awk` y a todos los lenguajes modernos. Existe porque buscar texto es una de las tareas más comunes. Los motores modernos de expresiones regulares añaden funciones como las referencias hacia atrás, las comprobaciones de contexto y las llamadas a código (*callouts*). La mayoría funciona por *retroceso*: prueba un camino y, si falla, retrocede y prueba otro. Ese diseño le da potencia al motor y hace que algunos patrones sean muy lentos. Este repositorio usa cinco motores como cinco computadoras distintas. Consulta [la lección sobre expresiones regulares](../lenguajes/regex.md).

- **Úsalas cuando:** separes texto en unidades, valides un formato simple o busques en registros.
- **Evítalas cuando:** los datos estén anidados o un atacante elija la entrada de datos y el motor use retroceso (consulta [[redos]]).

**Lee más:**

- [Expresión regular](https://en.wikipedia.org/wiki/Regular_expression) (Wikipedia)
- [Construcción de Thompson](https://en.wikipedia.org/wiki/Thompson%27s_construction) (Wikipedia)
- [Estrella de Kleene](https://en.wikipedia.org/wiki/Kleene_star) (Wikipedia)
- [Expresiones regulares](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions) (MDN), una guía práctica de la notación
