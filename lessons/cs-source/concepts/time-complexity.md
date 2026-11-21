---
title: "Precipicios de rendimiento y complejidad temporal"
chapter: 8
order: 60
---
La complejidad temporal describe cómo crece el tiempo de ejecución con el tamaño de la entrada de datos: lineal (n), cuadrática (n²), exponencial (2ⁿ). Existe porque las pruebas pequeñas esconden problemas grandes. Una función que tarda un milisegundo con diez elementos puede tardar un año con sesenta. En este repositorio el precipicio se usa a propósito. [[entry:regex-sed]] tiene una expresión regular con retroceso catastrófico, ajustada para tardar unos 50 milisegundos por cuadro, como *reloj*. Es un buen truco en una demostración, y un buen ejemplo de por qué no puedes usar la velocidad como temporizador en software real: otra máquina, otra versión, otra respuesta.

- **Úsalo cuando:** antes de publicar código que maneje entradas de datos grandes u hostiles, pregúntate cuál es el peor caso.
- **Evítalo cuando:** necesites un reloj o una garantía de tiempo transcurrido.

**Más información:**

- [Complejidad temporal](https://en.wikipedia.org/wiki/Time_complexity) (Wikipedia)
- [Notación de O grande](https://en.wikipedia.org/wiki/Big_O_notation) (Wikipedia)
- [Teoría de la complejidad computacional](https://en.wikipedia.org/wiki/Computational_complexity_theory) (Wikipedia)
