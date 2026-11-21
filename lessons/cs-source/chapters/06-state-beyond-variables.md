---
title: "Estado más allá de las variables"
---
Para una lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre el estado y el control más allá de las variables](../guias-de-estudio/conceptos/estado-y-control-mas-alla-de-las-variables.md).

Si un lenguaje no tiene variables o si no se te permite usarlas, ¿dónde puede guardar un programa lo que recuerda? Este capítulo reúne las respuestas. Una pila de marcas. Una línea de texto que las sustituciones reescriben. Qué archivos existen en el disco. Las capturas que deja una expresión regular. El texto fuente de las funciones. Una tabla temporal de procedimientos. La profundidad de recursión de un disparador. Un montón de caracteres `x`.

Ninguno de estos mecanismos parece un "estado" como lo parece una variable, pero todos lo son. En los conceptos que siguen verás dónde puede esconderse: en la pila de llamadas, en la pila como estructura de datos, en el ámbito y en la vinculación. También en las clausuras (*closure*, una función junto con su entorno), en el código como datos, en la reflexión, en los grafos de dependencias y en los disparadores de bases de datos. También en la serialización: cómo escribir un programa o un estado como bytes y qué hace falta para volver a leerlo y ejecutarlo. El primer concepto es el propio estado. La lección es un hábito: para cada programa, pregunta *¿dónde vive?* Encontrarás una tabla con las respuestas de las entradas en [Por objetivo](../objetivos.md).
