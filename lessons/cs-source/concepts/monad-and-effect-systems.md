---
title: "Mónadas y sistemas de efectos"
chapter: 7
order: 20
---
Los lenguajes funcionales puros tienen una respuesta ingeniosa a los efectos secundarios: describe el efecto como un *valor* y deja que el entorno de ejecución lo lleve a cabo. En Haskell, una acción `IO` es un valor de ese tipo. Una **mónada** es el patrón que encadena estas acciones en orden ("haz esto y usa el resultado para decidir qué hacer después"). Un *sistema de efectos* va más allá y registra los efectos posibles en el tipo. Así todavía puedes probar las partes puras y razonar sobre ellas. [[entry:haskell-weird]] rompe el patrón a propósito. `unsafeInterleaveIO` deja que la mera *lectura* de un elemento de la lista realice operaciones de entrada de datos y salida. Es justo lo que el sistema de tipos intenta impedir. El programa sigue siendo correcto solo porque no se puede leer la tarjeta *n* antes de la tarjeta *n−1*.

- **Úsalos cuando:** quieras que los efectos se vean en las firmas, en Haskell o en cualquier lenguaje que lleve cuenta de ellos.
- **Evita `unsafePerformIO` y `unsafeInterleaveIO`** salvo en lo más interno de una biblioteca, con un comentario que explique por qué es seguro.

**Lee más:**

- [Mónada (programación funcional)](https://en.wikipedia.org/wiki/Monad_(functional_programming)) (Wikipedia)
- [Sistema de efectos](https://en.wikipedia.org/wiki/Effect_system) (Wikipedia)
- [Haskell](https://en.wikipedia.org/wiki/Haskell) (Wikipedia)
