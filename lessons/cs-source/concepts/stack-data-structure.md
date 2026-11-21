---
title: "La pila como estructura de datos"
chapter: 6
order: 30
---
Una pila es un montón donde solo agregas y retiras elementos por la cima: el último en entrar es el primero en salir. Sirve cuando hay anidamiento: deshacer acciones, evaluar expresiones, emparejar delimitadores y aplicar retroceso. En este repositorio la pila aparece en dos lugares insólitos. En [[entry:forth-weird]] la pila de datos es la única memoria. En [[entry:regex-dotnet]] los *grupos de equilibrio* apilan una captura al ver una marca de apertura y la desapilan al ver una de cierre. Una pila de marcas sirve de contador, así que una expresión regular puede comparar dos recuentos.

```mermaid
flowchart TB
    accTitle: En una pila sale primero lo último que entró. Solo puedes apilar o desapilar por la cima
    accDescr: Tres vistas de una pila, de arriba abajo, cada una con la base a la izquierda y la cima a la derecha. Al principio la pila solo contiene A. Tras apilar B y luego C, contiene A, B y C, con C en la cima. Al desapilar dos veces, sale C primero y B después. Solo queda A. Lo último que se apila siempre es lo primero que vuelve a salir.
    subgraph T1["Inicio (base a la izquierda, cima a la derecha)"]
        direction LR
        a1["A (cima)"]
    end
    subgraph T2["Tras apilar dos veces"]
        direction LR
        b1["A"] ~~~ b2["B"] ~~~ b3["C (cima)"]
    end
    subgraph T3["Tras desapilar dos veces"]
        direction LR
        c1["A (cima)"]
    end
    T1 -->|"apila B y luego C"| T2
    T2 -->|"al desapilar sale C y luego B"| T3
```

Solo puedes acceder a la cima. Apilar agrega un elemento en la cima y desapilar lo retira de allí. Así, el último en entrar es el primero en salir. [[call-stack]] usa esta estructura con marcos como elementos. Las listas para deshacer acciones, la comprobación de pares de delimitadores y la pila de datos de [[entry:forth-weird]] son otros usos.

- **Úsala cuando:** el problema tenga elementos anidados o debas deshacer acciones en orden inverso.
- **Evítala cuando:** necesites acceso aleatorio o que el primero en entrar sea el primero en salir. Usa un arreglo o una cola.

**Lee más:**

- [Pila (tipo abstracto de datos)](https://en.wikipedia.org/wiki/Stack_(abstract_data_type)) (Wikipedia)
- [Autómata de pila](https://en.wikipedia.org/wiki/Pushdown_automaton) (Wikipedia)
