---
title: "Transparencia referencial"
chapter: 4
order: 70
---
Una expresión es referencialmente transparente si puedes reemplazarla por su valor y el programa no cambia. `2 + 3` lo es. `readLine()` no lo es, porque da una respuesta distinta cada vez. Esta es la regla de las funciones *puras*: son fáciles de probar, guardar en caché, ejecutar en paralelo y reordenar. Los efectos rompen esta propiedad. De eso se trata [[entry:haskell-weird]]: oculta la entrada de datos y la salida dentro de una lista que parece contener solo datos. Cuando se permita romper la regla, el código debe decirlo bien claro.

```mermaid
flowchart LR
    accTitle: Puedes sustituir una expresión pura por su valor, pero no una lectura del reloj
    accDescr: Dos grupos paralelos de llamadas. A la izquierda, evaluar 2 más 3 da 5 y volver a evaluar da 5. El valor es el mismo y la sustitución es segura. A la derecha, llamar a now en el instante t0 da 10:00:00 y llamarlo en el instante t1 da 10:00:01. El resultado depende del momento de evaluación. Sustituir la llamada por una constante cambia el comportamiento. Las horas del reloj son ilustrativas.
    subgraph CLOCK["Llamada que depende del tiempo"]
        direction LR
        B2["now() en t₁"] --> W2["10:00:01"]
        B1["now() en t₀"] --> W1["10:00:00"]
        W1 --> NO["Depende del momento: una constante cambia el comportamiento"]
        W2 --> NO
    end
    subgraph STABLE["Expresión sustituible"]
        direction LR
        A2["Vuelve a evaluar 2 + 3"] --> V2["5"]
        A1["Evalúa 2 + 3"] --> V1["5"]
        V1 --> OK["Mismo valor: sustitución segura"]
        V2 --> OK
    end
```

Puedes sustituir el lado izquierdo por `5` en cualquier parte. No puedes hacer lo mismo con el lado derecho: el valor de la llamada depende de *cuándo* se ejecuta y las horas del ejemplo son ilustrativas. Esto trata de la transparencia referencial, que aquí equivale a la repetibilidad. No trata de [[idempotence]]. Una función que lee el reloj no cambia nada, así que no es "no idempotente". Solo le falta repetibilidad. [[idempotence]] trata de lo que una operación le hace al estado.

- **Úsala cuando:** sea posible. Mantén un núcleo puro grande y lleva los efectos a los bordes.
- **Evita fingir transparencia:** los números aleatorios, los relojes, los archivos y las redes no son transparentes.

**Lee más:**

- [Transparencia referencial](https://en.wikipedia.org/wiki/Referential_transparency) (Wikipedia)
- [Función pura](https://en.wikipedia.org/wiki/Pure_function) (Wikipedia)
- [Programación funcional](https://en.wikipedia.org/wiki/Functional_programming) (Wikipedia)
