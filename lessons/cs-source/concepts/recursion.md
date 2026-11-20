---
title: "Recursión"
chapter: 3
order: 40
---
Una definición recursiva se usa a sí misma. Una función se llama a sí misma sobre un problema más pequeño, hasta que el problema es tan pequeño que la respuesta es obvia. La recursión existe porque muchas cosas son anidadas por naturaleza: árboles, carpetas, gramáticas, expresiones aritméticas. Los bucles y la recursión son igual de potentes, y los lenguajes funcionales usan recursión en lugar de bucles. Varias entradas de aquí son recursivas sin parecerlo. En [[entry:m4]], una macro cuyo texto de reemplazo se contiene a sí mismo se lee de nuevo, lo que produce un bucle. En [[entry:tcl-weird]], un disparador de base de datos inserta una fila, lo que activa de nuevo el mismo disparador. La regla de parada es una consulta que no encuentra nada.

```mermaid
flowchart LR
    accTitle: La recursión avanza hacia un caso base y luego retrocede con los resultados acumulados
    accDescr: Dos columnas para la suma de 3. La columna izquierda, leída hacia abajo, muestra las llamadas que avanzan hacia adentro. La suma de 3 llama a la suma de 2, que llama a la suma de 1, que llama a la suma de 0. La suma de 0 es el caso base y devuelve 0 sin llamar a nada. La columna derecha, leída hacia arriba, muestra los resultados que vuelven hacia afuera. La suma de 1 es 1 más 0, que es 1. La suma de 2 es 2 más 1, que es 3. La suma de 3 es 3 más 3, que es 6.
    subgraph DOWN["Las llamadas bajan"]
        direction TB
        n3["sum(3)"] -->|llama a| n2["sum(2)"] -->|llama a| n1["sum(1)"] -->|llama a| n0(["sum(0): caso base"])
    end
    subgraph UP["Los resultados suben de vuelta"]
        direction BT
        u0["sum(0) = 0"] -->|devuelve| u1["sum(1) = 1 + 0 = 1"] -->|devuelve| u2["sum(2) = 2 + 1 = 3"] -->|devuelve| u3["sum(3) = 3 + 3 = 6"]
    end
    DOWN --> UP
```

Al bajar, cada llamada pasa un problema más pequeño a la siguiente llamada. El caso base, `sum(0)`, es la única llamada que responde sin volver a llamar. Sin él, las llamadas nunca se detienen. Al subir, cada llamada termina el trabajo que tenía pendiente. [[call-stack]] muestra dónde se guardan esas llamadas en espera.

- **Úsala cuando:** los datos están anidados, o el problema se divide en copias más pequeñas de sí mismo.
- **Evítala cuando:** la profundidad no tiene límite y el lenguaje no elimina las llamadas de cola. La *pila* (*stack*) puede agotarse. Conoce siempre la regla de parada y sabe qué pasa si nunca se activa.

**Lee más:**

- [Recursión (informática)](https://en.wikipedia.org/wiki/Recursion_(computer_science)) (Wikipedia)
- [Llamada final](https://en.wikipedia.org/wiki/Tail_call) (Wikipedia)
- [Recursión](https://developer.mozilla.org/en-US/docs/Glossary/Recursion) (glosario de MDN)
