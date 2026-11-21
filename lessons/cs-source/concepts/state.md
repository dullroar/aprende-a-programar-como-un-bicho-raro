---
title: "Estado"
chapter: 6
order: 10
---
El estado es todo lo que un programa recuerda entre un paso y otro. Sin él, no se podría calcular nada. La pregunta interesante es *dónde vive*: en variables, en una pila, en el montón, en un archivo, en una base de datos, en una variable de entorno o en la red. El primer objetivo de este libro es hacer esa pregunta sobre cada programa. Las respuestas aquí sorprenden. El estado vive en el destino de un `GO TO`, en una línea de texto, en los archivos que existen en el disco, en las capturas de una expresión regular, en el texto de las funciones, en el flujo de entrada y en la profundidad de la recursión de los disparadores. Mira la tabla en [Por objetivo](../objetivos.md).

- **Úsalo cuando:** quieras un estado explícito, pequeño y cercano al lugar donde se usa.
- **Evita el estado oculto y el estado global.** Es difícil de probar, de compartir y de razonar.

**Más información:**

- [Estado (informática)](https://en.wikipedia.org/wiki/State_(computer_science)) (Wikipedia)
- [Sistema de archivos](https://en.wikipedia.org/wiki/File_system) (Wikipedia), donde la entrada de Make guarda su estado
- [Variable global](https://en.wikipedia.org/wiki/Global_variable) (Wikipedia)
