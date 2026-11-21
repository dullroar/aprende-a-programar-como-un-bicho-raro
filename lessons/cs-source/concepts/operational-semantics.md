---
title: "Semántica operacional"
chapter: 2
order: 110
---
La **semántica operacional** explica qué significa un programa al decir cómo se ejecuta: cuál es el *estado* de una máquina y qué efecto tiene *un paso* en él. Así, un lenguaje es un conjunto de reglas como "en este estado, esta construcción lleva la máquina a ese otro estado". Es la forma más directa de responder "¿qué hace esto en realidad?". Es lo que haces cuando lees un programa una transición a la vez.

Puedes describir así cada entrada que nombra su máquina. Tres lo hacen en su propia página. [[entry:tar-gnu-weird]] tiene una fila de registros (las horas trabajadas, el objetivo, el total, la semilla y una bandera de fin). Tiene una transición que se ejecuta una vez por cada punto de control de tar. [[entry:javascript]] consta de las tres cláusulas de un `for`: inicializa una vez y después sigue con prueba, cuerpo, actualización, prueba, cuerpo, actualización. Su README sigue la traza de una tarjeta a través de esos pasos. [[entry:ex-weird]] tiene como estado las marcas y los registros. Cada línea de comandos cambia ese estado.

- **Úsala cuando:** debas explicar o comprobar con exactitud qué hace una construcción extraña. Escribe el estado y el paso. Después ejecútalo a mano.
- **Evítala cuando:** necesites comparar programas por lo que calculan y no por cómo lo calculan. En ese caso, usa una semántica que ignore los pasos.

**Lee más:**

- [Semántica operacional](https://en.wikipedia.org/wiki/Operational_semantics) (Wikipedia)
- [Sistema de transiciones](https://en.wikipedia.org/wiki/Transition_system) (Wikipedia)
