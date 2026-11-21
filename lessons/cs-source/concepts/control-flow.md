---
title: "Flujo de control"
chapter: 3
order: 10
---
El flujo de control es el orden en que se ejecutan los pasos de un programa. Los pasos pueden ejecutarse en secuencia, tomar una rama, repetirse, llamar y retornar o saltar. Es una idea aparte porque "¿qué pasa después?" es una pregunta distinta de "¿cuáles son los datos?". La mayoría de los lenguajes sueldan el flujo de control a dos piezas: el *contador de programa* y la *pila de llamadas*. Las entradas de este repositorio lo sueltan y lo guardan en otro sitio. En COBOL vive en el destino de un `GO TO`. En Forth vive en la posición de lectura del intérprete de texto. En Make vive en qué archivos existen. Verlo cambiar de sitio es la mejor forma de entender que puedes nombrarlo.

- **Úsalo cuando:** te preguntes, sobre cualquier programa, "¿dónde vive lo que decide qué se ejecuta después?".
- **Evítalo cuando:** el mecanismo oculte el flujo de control a las herramientas de depuración. Un depurador muestra la pila de llamadas. No muestra una línea de texto reescrita.

**Lee más:**

- [Flujo de control](https://en.wikipedia.org/wiki/Control_flow) (Wikipedia)
- [Grafo de flujo de control](https://en.wikipedia.org/wiki/Control-flow_graph) (Wikipedia)
