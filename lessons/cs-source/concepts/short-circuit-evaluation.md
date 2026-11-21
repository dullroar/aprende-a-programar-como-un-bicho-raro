---
title: "Evaluación de cortocircuito"
chapter: 4
order: 40
---
La evaluación de cortocircuito significa que `and` y `or` paran en cuanto se conoce la respuesta. En `a && b`, si `a` es falso, `b` nunca se ejecuta. Sirve para ganar velocidad y para un hábito muy útil: comprueba la condición de protección antes de actuar (`x != null && x.length > 0`). La misma idea puede convertirse en un bucle. En [[entry:lisp-weird]] la combinación de métodos `or` llama a los métodos uno tras otro y se detiene en el primero que devuelve un valor verdadero. La jerarquía de clases se convierte en el bucle y `or` en la regla de parada.

```mermaid
flowchart TB
    accTitle: El cortocircuito es un flujo de control que puede omitir trabajo y efectos secundarios
    accDescr: Dos paneles. En el primero, false AND expensive() evalúa el lado izquierdo, que es false. Si el lado izquierdo es false, el resultado de AND es false sea cual sea el lado derecho. El resultado es false y no se llama a expensive(). En el segundo, true OR expensive() evalúa el lado izquierdo, que es true. Si el lado izquierdo es true, el resultado de OR es true sea cual sea el lado derecho. El resultado es true y no se llama a expensive(). En ambos paneles, la llamada omitida tiene un borde discontinuo y una flecha que nunca se sigue.
    subgraph P1["false AND expensive()"]
        direction TB
        l1["lado izquierdo: false"] --> d1{{"false AND cualquier valor da false"}}
        d1 -->|"respuesta conocida"| r1(["resultado: false"])
        d1 -.->|"se omite"| x1["expensive(): nunca se ejecuta"]
    end
    subgraph P2["true OR expensive()"]
        direction TB
        l2["lado izquierdo: true"] --> d2{{"true OR cualquier valor da true"}}
        d2 -->|"respuesta conocida"| r2(["resultado: true"])
        d2 -.->|"se omite"| x2["expensive(): nunca se ejecuta"]
    end
    P1 ~~~ P2
    classDef skip stroke-dasharray: 5 5
    class x1,x2 skip
```

En ambos paneles, el operando izquierdo determina la respuesta y el derecho se omite. Nada de lo que haría llega a ocurrir, ya sea una consulta lenta, una escritura o la impresión de una línea. Por eso `x != null && x.length > 0` es seguro. También significa que un efecto en el operando derecho no está asegurado. Consulta [[side-effect]].

- **Úsala cuando:** protejas una operación arriesgada o elijas la primera respuesta válida.
- **Evítala cuando:** esperes que un efecto del segundo operando ocurra siempre. Puede no ocurrir y no habrá aviso.

**Lee más:**

- [Evaluación de cortocircuito](https://en.wikipedia.org/wiki/Short-circuit_evaluation) (Wikipedia)
- [Sistema de objetos de Common Lisp](https://en.wikipedia.org/wiki/Common_Lisp_Object_System) (Wikipedia)
- [AND lógico (`&&`)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Logical_AND) (MDN), que explica el cortocircuito en palabras sencillas
