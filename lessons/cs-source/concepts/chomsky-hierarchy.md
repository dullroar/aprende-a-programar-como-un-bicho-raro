---
title: "La jerarquía de Chomsky"
chapter: 5
order: 10
---
En 1956 Noam Chomsky ordenó los lenguajes formales en cuatro clases según su potencia: regulares, libres de contexto, sensibles al contexto y sin restricciones. Cada clase necesita una máquina más potente que la anterior. En orden, son un autómata finito, un autómata con pila (una máquina finita más una pila), una máquina de Turing acotada y una sin límites. La jerarquía responde una pregunta práctica: *¿cuánta máquina necesita esta notación?* Una expresión regular clásica no puede comprobar si los corchetes están balanceados, porque para eso necesita una pila. Los motores reales de expresiones regulares van más allá de la clase clásica. Los grupos de balanceo de .NET en [[entry:regex-dotnet]] le dan al motor una pila de capturas. Esa es exactamente la potencia adicional.

- **Úsala cuando:** elijas una herramienta de análisis sintáctico o te preguntes si basta un patrón.
- **Evita usarla cuando:** necesites hacer el análisis sintáctico de formatos anidados como HTML con una expresión regular simple.

**Lee más:**

- [Jerarquía de Chomsky](https://en.wikipedia.org/wiki/Chomsky_hierarchy) (Wikipedia)
- [Lenguaje formal](https://en.wikipedia.org/wiki/Formal_language) (Wikipedia)
- [Autómata con pila](https://en.wikipedia.org/wiki/Pushdown_automaton) (Wikipedia)
