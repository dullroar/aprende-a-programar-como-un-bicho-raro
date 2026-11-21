---
title: "El contador de programa"
chapter: 3
order: 30
---
El contador de programa es un registro que guarda la dirección de la siguiente instrucción. Tras cada paso avanza una posición, salvo que un salto le asigne otra. Existe porque una máquina necesita saber "¿dónde estoy?". Todo intérprete tiene uno, aunque lleve otro nombre. En [[entry:forth-weird]] ese papel lo cumple `>in`, la posición de lectura del intérprete de texto en la línea actual. El programa *mueve `>in` hacia atrás* para repetirse. En [[entry:cobol-weird]] es el destino de un `GO TO`.

- **Usa esta idea cuando:** depures o escribas un intérprete, un depurador o una máquina virtual. En esos casos tiene sentido consultar el valor que responde a "¿dónde estoy?".
- **Evítalo cuando:** el código común de una aplicación necesite acceder directamente al contador.

**Lee más:**

- [Contador de programa](https://en.wikipedia.org/wiki/Program_counter) (Wikipedia)
- [Intérprete (informática)](https://en.wikipedia.org/wiki/Interpreter_(computing)) (Wikipedia)
