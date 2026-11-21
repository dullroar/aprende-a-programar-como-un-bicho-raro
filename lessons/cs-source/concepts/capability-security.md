---
title: "Capacidad y autoridad"
chapter: 1
order: 80
---
Quién puede hacer qué es una cuestión de **autoridad**, además de datos. Un archivo que por sí solo no puede hacer nada gana poder cuando algo con autoridad acepta actuar sobre él. La antigua regla de la **seguridad basada en capacidades** dice que solo debes tener la autoridad que necesitas. Esa autoridad debe venir de lo que te entregaron y no de lo que puedes nombrar.

[[entry:tar-gnu]] lo muestra en una línea. Un archivo de almacenamiento no puede registrar su propio gancho. `tar -xf` escribe archivos y no ejecuta nada. `tar --to-command=...` inicia un programa por cada miembro. La autoridad para ejecutar algo está en el comando que escribió el *operador*, así que ese comando es la frontera de confianza. [[entry:ed-weird]] y [[entry:ex-weird]] hacen una elección similar con los editores. GNU ed permite escapar al intérprete de comandos (*shell*) con `!` dentro de una lista de comandos global. Ex también tiene `!` y comandos para archivos. Ambos programas los evitan y sus scripts de comprobación lo hacen cumplir. La razón no es que los comandos sean malos. Un programa que puede ejecutar un intérprete de comandos puede hacer cualquier cosa. Si no puede ejecutarlo, es mucho más fácil razonar sobre el programa. Consulta también [[sandbox]] y [[least-privilege]].

- **Úsala cuando:** diseñes una interfaz que ejecute algo en nombre de otra persona. Pregunta qué autoridad tiene quien hace cada llamada y no concedas más a quien la recibe.
- **Evítala cuando:** tomes "solo son datos" como motivo para dejar de pensar. Los datos son inertes hasta que un consumidor con autoridad actúa sobre ellos.

**Lee más:**

- [Seguridad basada en capacidades](https://en.wikipedia.org/wiki/Capability-based_security) (Wikipedia)
- [Principio de mínimo privilegio](https://en.wikipedia.org/wiki/Principle_of_least_privilege) (Wikipedia)
- [Problema del delegado confundido](https://en.wikipedia.org/wiki/Confused_deputy_problem) (Wikipedia)
