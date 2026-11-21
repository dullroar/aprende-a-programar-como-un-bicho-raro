---
title: "El corte: cómo fijar una elección"
chapter: 7
order: 70
---
El *corte* es una idea de Prolog: una vez que el programa pasa por ese punto, conserva las opciones elegidas hasta allí y descarta las demás. Sirve para ganar velocidad y determinismo: no quieres que la búsqueda explore alternativas o repita trabajo que ya das por resuelto. Los motores de expresiones regulares tienen las mismas herramientas: `(*COMMIT)` de PCRE, grupos atómicos y cuantificadores posesivos. [[entry:regex-pcre2]] y las entradas afines terminan el patrón con `(*COMMIT)(*FAIL)`. Sin `(*COMMIT)` el motor volvería a probar con bucles más cortos y ejecutaría el finalizador más de una vez. Quienes programan en Prolog distinguen los cortes "verdes" (solo ganan velocidad) de los cortes "rojos" (cambian la respuesta).

```mermaid
flowchart TB
    accTitle: El corte cambia el espacio de búsqueda: las alternativas descartadas dejan de considerarse
    accDescr: Árbol de búsqueda con un corte. Al inicio hay dos opciones, A y B. La búsqueda toma A y llega al corte, que la compromete con A. La opción B tiene un borde discontinuo y está marcada como podada. El corte la eliminó, pero el retroceso simple la habría probado más tarde. Tras el corte, la búsqueda aún puede probar las alternativas posteriores, A1 y luego A2. A1 no tiene salida y A2 tiene éxito. Si A2 también fallara, la búsqueda entera fallaría sin llegar a probar B.
    S(["Inicio: dos opciones"]) -->|"1. Prueba A"| A["A"]
    A --> C{{"CORTE: conserva A"}}
    C --> A1["A1: sin salida"]
    C --> A2(["A2: éxito"])
    S -.->|"Se corta B"| B["B: podada, sin probar"]
    classDef pruned stroke-dasharray: 5 5
    class B pruned
```

Compara este dibujo con el retroceso simple. En ese caso, la búsqueda probaría `B` si fallara `A`. Aquí el corte conserva primero `A` y poda `B`. La búsqueda aún puede probar las alternativas que vienen *después* del corte (`A1` y luego `A2`). Si todas fallan, falla toda la búsqueda. No vuelve a `B`. Eso significa que "el corte cambia el espacio de búsqueda". El corte de Prolog también descarta las opciones elegidas antes en la misma cláusula. El dibujo muestra solo el caso más sencillo.

- **Úsalo cuando:** sepas que un fallo posterior nunca debe llevar a otro intento.
- **Evítalo cuando:** no sepas qué tipo de corte tienes. Un corte rojo esconde un cambio de lógica en un truco para ganar velocidad.

**Lee más:**

- [Corte (programación lógica)](https://en.wikipedia.org/wiki/Cut_(logic_programming)) (Wikipedia)
- [Prolog](https://en.wikipedia.org/wiki/Prolog) (Wikipedia)
