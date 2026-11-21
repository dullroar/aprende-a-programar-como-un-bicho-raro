---
title: "Algoritmos de Markov"
chapter: 2
order: 90
---
Un algoritmo de Markov es una lista ordenada de reglas de búsqueda y reemplazo. Busca la primera regla cuyo patrón aparezca en el texto. Reemplaza esa coincidencia y vuelve al principio de la lista. Detente cuando no se aplique ninguna regla o una regla diga "detente". El matemático ruso Andréi Márkov hijo lo describió en la década de 1950. Puede calcular todo lo que puede calcular una máquina de Turing. Su propósito es mostrar que *reescribir texto es computar*. [[entry:regex-sed]] es justo eso: una línea de texto y un script de sustituciones que la reescriben hasta que no hay coincidencia. Toda la memoria cabe en esa línea.

```mermaid
flowchart TB
    accTitle: Un algoritmo de Markov aplica la primera regla con coincidencia hasta llegar a una regla terminal o quedarse sin coincidencias
    accDescr: Una lista ordenada de reglas encima de una traza. La regla 1 convierte AA en A. La 2 convierte BA en AB. La 3 convierte B en B y se detiene. El texto BAA tiene coincidencias con las reglas 1 y 2. Gana la regla 1 porque va primero y el texto pasa a ser BA. Ahora solo hay coincidencia con la regla 2 y el texto pasa a ser AB. Ya no hay coincidencia con las reglas 1 y 2. Como hay coincidencia con la regla 3 y es terminal, el algoritmo se detiene con AB.
    subgraph RULES["Reglas, siempre desde el principio"]
        direction TB
        R1["1: AA se convierte en A"] ~~~ R2["2: BA se convierte en AB"] ~~~ R3["3: B queda en B y se detiene"]
    end
    S0["Texto: BAA, coincidencia con reglas 1 y 2"] -->|"la regla 1 va primero"| S1["Texto: BA"]
    S1 -->|"regla 2"| S2["Texto: AB"]
    S2 -->|"regla 3: terminal"| H(["Se detiene con AB"])
    RULES ~~~ S0
```

Lo que decide es el orden de las reglas, no la posición en el texto. `BAA` tiene coincidencias con las reglas 1 y 2 y gana la regla 1 porque es la primera. Tras cada reescritura, la búsqueda de una regla vuelve a empezar por la regla 1. La ejecución termina cuando se aplica una regla terminal (aquí, la regla 3) o cuando no hay coincidencia con ninguna regla. Otros sistemas de reescritura, como los de [[term-rewriting]], no siempre eligen las reglas así.

- **Úsalo cuando:** transformes o normalices texto o quieras enseñar que un programa puede ser "solo reglas".
- **Evítalo en programas grandes:** el orden de las reglas *es* el flujo de control. Cuesta razonar sobre él y cuesta predecir la velocidad.

**Lee más:**

- [Algoritmo de Markov](https://en.wikipedia.org/wiki/Markov_algorithm) (Wikipedia)
- [[term-rewriting]] en "Los lenguajes formales como sustratos de cómputo"
