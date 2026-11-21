---
title: "Homoiconicidad: código como datos"
chapter: 6
order: 50
---
Un lenguaje es *homoicónico* cuando sus programas se escriben en sus propias estructuras de datos. En Lisp el código es una lista, así que una macro es solo un programa que construye una lista. Tcl toma otro camino con "todo es una cadena de texto". APL trata una función como una matriz de caracteres. En Forth el programa es un flujo de palabras que el intérprete puede leer. La idea simplifica la metaprogramación: si el código es dato, puedes inspeccionarlo, crearlo y cambiarlo con tus herramientas de siempre. [[entry:apl-weird]] lee su propio código fuente con `⎕CR`, lo reescribe y define la copia con `⎕FX`.

- **Úsala cuando:** escribas macros, transformadores de código o lenguajes pequeños.
- **Evítala cuando:** las herramientas deban entender tu código sin ejecutarlo. A los analizadores estáticos y las herramientas de refactorización les cuesta seguir el código que construye código.

**Lee más:**

- [Homoiconicidad](https://en.wikipedia.org/wiki/Homoiconicity) (Wikipedia)
- [Lisp (lenguaje de programación)](https://en.wikipedia.org/wiki/Lisp_(programming_language)) (Wikipedia)
- [Metaprogramación](https://en.wikipedia.org/wiki/Metaprogramming) (Wikipedia)
