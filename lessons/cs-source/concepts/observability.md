---
title: "Observabilidad"
chapter: 2
order: 50
---
La observabilidad mide cuánto puedes saber del interior de un sistema desde fuera, por sus salidas, registros y trazas. Existe porque no puedes arreglar lo que no ves. Por eso varias entradas tienen una opción para activar la traza. Por ejemplo, `TRACE=1 ./timecards.sh` en [[entry:regex-sed]] imprime todo el estado del programa en cada paso. Pero mirar puede cambiar lo que miras. En un lenguaje con evaluación perezosa, imprimir un valor *fuerza* su evaluación. Así, el mero hecho de mirar provoca el cálculo. Los programadores llaman *heisenbug* al bicho que desaparece cuando vas a verlo.

- **Úsala cuando:** diseñes algo que luego tendrás que depurar. Registra los cambios de estado además de los errores.
- **Evítala cuando:** la observación pueda dejar secretos registrados. Ten en cuenta el costo y cualquier efecto de observar.

**Lee más:**

- [Observabilidad (software)](https://en.wikipedia.org/wiki/Observability_(software)) (Wikipedia)
- [Heisenbug](https://en.wikipedia.org/wiki/Heisenbug) (Wikipedia)
