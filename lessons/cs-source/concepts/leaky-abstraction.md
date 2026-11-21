---
title: "Abstracciones con fugas"
chapter: 8
order: 10
---
Una abstracción oculta detalles para que puedas pensar a un nivel más alto. Una abstracción *con fugas* deja ver lo que oculta cuando algo falla o cuando importa la velocidad. En 2002 Joel Spolsky acuñó la "ley de las abstracciones con fugas": toda abstracción no trivial deja escapar algo, al menos un poco. Este libro es una colección de fugas que buscamos a propósito. La "búsqueda de coincidencias de texto" deja entrever el costo del retroceso. Una "dependencia" de una herramienta de compilación deja ver las marcas de tiempo de los archivos. La "consulta" de LINQ deja ver los límites de su proveedor de SQL. Puedes seguir usando la abstracción. Solo necesitas conocer la capa que tiene debajo.

- **Úsala cuando:** aprendas a manejar una herramienta. Pregúntate "¿qué tiene debajo y cuándo se dejará ver?".
- **Evita depender de una fuga cuando:** de ella dependa la corrección y no puedas documentarla.

**Lee más:**

- [Abstracción con fugas](https://en.wikipedia.org/wiki/Leaky_abstraction) (Wikipedia)
- [Abstracción (informática)](https://en.wikipedia.org/wiki/Abstraction_(computer_science)) (Wikipedia)
