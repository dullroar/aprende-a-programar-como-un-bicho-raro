---
title: "Sistemas de transición y máquinas de estados"
chapter: 2
order: 20
---
Un sistema de transición es la máquina más simple: un conjunto de *estados* y un conjunto de *movimientos* permitidos entre ellos. Una máquina de estados finitos es el caso con un número fijo y pequeño de estados. Existe porque las máquinas pequeñas se pueden comprobar por completo: puedes listar cada estado y cada movimiento. Los analizadores sintácticos, los protocolos de red, los flujos de interfaz de usuario y el interior de los motores de expresiones regulares se construyen así. Cada entrada de este repositorio se puede dibujar como un sistema de transición si haces dos preguntas: ¿cuál es el estado?, ¿cuál es un paso?

- **Úsalo cuando:** el comportamiento dependa del historial de forma acotada, como en "¿qué vi antes?"
- **Evítalo cuando:** el estado no tenga límite. Una máquina finita no puede contar paréntesis que coinciden a cualquier profundidad. Para eso necesitas una pila (mira [[stack-machine]]). Ten cuidado también con la *explosión de estados*: el número de estados puede crecer más rápido de lo que puedes dibujarlos.

**Más información:**

- [Sistema de transición](https://en.wikipedia.org/wiki/Transition_system) (Wikipedia)
- [Máquina de estados finitos](https://en.wikipedia.org/wiki/Finite-state_machine) (Wikipedia)
