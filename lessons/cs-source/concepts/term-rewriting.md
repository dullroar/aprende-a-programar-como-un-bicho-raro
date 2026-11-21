---
title: "Reescritura de términos y de cadenas de texto"
chapter: 5
order: 40
---
Reescribir significa reemplazar partes de una estructura según unas reglas, una y otra vez, hasta que ya no se aplica ninguna. Un *término* es un árbol, como una expresión aritmética. Una *cadena de texto* es el caso especial en que la estructura es una línea de texto. Existe porque muchos tipos de cómputo son en realidad simplificación: el álgebra, el cálculo lambda, un compilador que optimiza, un filtro de texto que corrige la ortografía. Importan dos propiedades. ¿Siempre se detiene (*terminación*)? ¿Todos los órdenes de reescritura dan la misma respuesta (*confluencia*)? En este repositorio [[entry:regex-sed]] y [[entry:m4]] son sistemas de reescritura, y la respuesta es simplemente el texto que queda.

- **Úsalo cuando:** simplifiques, normalices o traduzcas estructuras con reglas claras.
- **Evítalo cuando:** el orden de las reglas importe pero no esté escrito, o cuando la terminación no sea evidente.

**Más información:**

- [Reescritura](https://en.wikipedia.org/wiki/Rewriting) (Wikipedia)
- [Confluencia (reescritura abstracta)](https://en.wikipedia.org/wiki/Confluence_(abstract_rewriting)) (Wikipedia)
- [[markov-algorithm]] en "¿Qué cuenta como una máquina?"
