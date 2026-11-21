---
title: "Intérpretes y máquinas virtuales"
chapter: 5
order: 130
---
Un **intérprete** lee un programa como datos y hace lo que este indica, paso a paso. Una **máquina virtual** es un intérprete para un conjunto pequeño y fijo de instrucciones. Ambos se valen del mismo truco: una *representación* (texto, registros o bytes) junto con un *programa que le da comportamiento*. Quita el intérprete y solo quedan los datos.

Varias entradas son intérpretes a pequeña escala. En [[entry:tar-gnu]], el programa está formado por los miembros de un archivo tar. Un despachador de unas 80 líneas da sentido a cuatro tipos de registro. Comprueba cada registro contra una gramática estricta y rechaza los que no reconoce. En [[entry:tcl-weird]], el código fuente Tcl se guarda en filas de SQLite. Una versión redefinida del comando `unknown` lo recupera y lo ejecuta. En [[entry:xaml]], el analizador sintáctico que carga el documento es el intérprete que lo ejecuta. En [[entry:regex-pcre2]], las cadenas de texto de los callouts son códigos de operación y una función de C sin cuerpo actúa como despachador. En [[entry:ex-weird]], Ex es el intérprete y un registro de texto es el programa. El propio programa lo reescribe y lo vuelve a ejecutar. En cada caso, hazte la misma pregunta. ¿Cuál es la representación, cuál es el intérprete y quién decidió ejecutar la primera con el segundo?

- **Úsalos cuando:** sea más fácil modificar un programa como datos que como código o quieras que otros escriban en un lenguaje pequeño y seguro.
- **Evítalos cuando:** los datos vengan de alguien en quien no confías y el intérprete sea de propósito general. Una gramática estricta y un conjunto fijo de instrucciones impiden que un formato de datos se convierta en una vía de entrada.

**Lee más:**

- [Intérprete (informática)](https://en.wikipedia.org/wiki/Interpreter_(computing)) (Wikipedia)
- [Máquina virtual](https://en.wikipedia.org/wiki/Virtual_machine) (Wikipedia)
