---
title: "Contrapresión"
chapter: 10
order: 50
---
La **contrapresión** es la forma en que un consumidor lento le pide a un productor rápido que espere. Una fuente de eventos emite avisos a su propio ritmo. Si el consumidor no puede seguirle el ritmo, la cola crece sin límite hasta agotar la memoria o se descartan eventos. La contrapresión convierte eso en una conversación. Puede usar un búfer acotado, un flujo que pausa su fuente o un mecanismo de *demanda* (*pull*), en el que el consumidor pide un valor cuando está listo.

La demanda es la forma más sencilla de contrapresión y [[entry:javascript-weird]] la usa. No se puede saturar porque no extrae nada hasta que alguien lo pide. [[entry:javascript-events]] no tiene contrapresión ni la necesita. Cada tarjeta espera a la anterior, así que el productor y el consumidor son un solo programa. [[entry:tar-gnu-weird]] muestra qué pasa sin esa señal. tar sigue escribiendo registros y, por tanto, sigue consultando el reloj después de que la máquina termina. Esos pulsos solo cuentan como inactividad, porque no hay forma de pedirle a tar que se detenga.

- **Úsala cuando:** no controles la velocidad del productor.
- **Evítala cuando:** el productor y el consumidor sean un solo programa secuencial. Basta un bucle sencillo.

**Lee más:**

- [Contrapresión](https://en.wikipedia.org/wiki/Back_pressure) (Wikipedia)
