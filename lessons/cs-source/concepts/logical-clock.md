---
title: "Relojes lógicos y orden de los eventos"
chapter: 3
order: 100
---
Un **reloj lógico** cuenta *eventos* en vez de segundos. Responde "¿qué ocurrió antes que qué?" y "¿cuántos pasos han pasado?" sin preguntar cuánto duró nada. Los sistemas distribuidos usan relojes lógicos porque los relojes reales de distintas máquinas discrepan. Un programa también puede usar uno en una sola máquina para que su comportamiento no dependa de la velocidad.

En [[entry:tar-gnu-weird]], un punto de control de tar equivale a una hora de trabajo. El reloj es el número de registros que tar ha escrito. `check.sh` predice el resultado de una ejecución solo a partir de la disposición del archivo. Da igual si la máquina es más rápida o más lenta. Un archivo más largo da más pulsos y uno más corto atasca el programa. Otro intervalo entre puntos de control cambia el recuento y la comprobación calcula de antemano ese cambio. Hay un detalle que es fácil pasar por alto. `TAR_CHECKPOINT` cuenta *registros* (con `--checkpoint=2` lee 2, 4, 6), mientras que la máquina cuenta *llamadas*. Son dos relojes y la entrada dice cuál usa. [[entry:make-gnu]] tiene un contador similar. `MAKE_RESTARTS` cuenta rondas de compilación en vez de tiempo.

- **Úsalo cuando:** necesites ordenar eventos, repetir una ejecución con el mismo resultado o probar la temporización sin esperar.
- **Evítalo cuando:** necesites la duración real. Un reloj lógico no te puede decir cuánto duró algo.

**Lee más:**

- [Reloj lógico](https://en.wikipedia.org/wiki/Logical_clock) (Wikipedia)
- [Marca de tiempo de Lamport](https://en.wikipedia.org/wiki/Lamport_timestamp) (Wikipedia)
