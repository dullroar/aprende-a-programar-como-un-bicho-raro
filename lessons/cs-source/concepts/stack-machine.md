---
title: "Máquinas de pila"
chapter: 2
order: 60
---
Una máquina de pila guarda sus valores de trabajo en una pila. Una instrucción toma sus entradas de la cima y deja allí su resultado. No hay registros con nombre. Existe porque las instrucciones pueden ser diminutas (`+` no necesita operandos) y un compilador puede generarlas con facilidad. Por eso la JVM, el IL de .NET, WebAssembly, PostScript y Forth usan la idea. En [[entry:forth-weird]] la pila de datos es la *única* memoria: el programa no tiene ningún `variable`.

```mermaid
flowchart TB
    accTitle: Las máquinas de pila calculan al apilar y desapilar valores en la cima de una pila LIFO: lo último en entrar sale primero
    accDescr: Tres vistas de una pila, de arriba abajo, cada una con la base a la izquierda y la cima a la derecha. Al principio la pila contiene 19 con 23 en la cima. La instrucción ADD desapila los dos valores de la cima y apila su suma. La pila queda solo con 42. Luego PUSH 10 pone 10 en la cima. La pila contiene 42 con 10 en la cima. Cada paso solo toca la cima de la pila y ninguna instrucción nombra una posición.
    subgraph S1["Inicio (base a la izquierda, cima a la derecha)"]
        direction LR
        a1["19"] ~~~ a2["23 (cima)"]
    end
    subgraph S2["Después de ADD"]
        direction LR
        b1["42 (cima)"]
    end
    subgraph S3["Después de PUSH 10"]
        direction LR
        c1["42"] ~~~ c2["10 (cima)"]
    end
    S1 -->|"ADD: desapila dos valores y apila la suma"| S2
    S2 -->|"PUSH 10: apila un valor"| S3
```

Lee el dibujo de arriba abajo. `ADD` no dice dónde están sus entradas: desapila los dos valores de la cima y apila un resultado. Una máquina de pila real también tiene otra memoria (la JVM tiene variables locales y un montículo, por ejemplo). La pila solo guarda los valores que necesita la siguiente instrucción.

- **Úsala cuando:** construyas una máquina virtual pequeña o un intérprete, o quieras código compacto.
- **Evítala cuando:** necesites acceso aleatorio a muchos valores. El código que reordena la pila con `dup`, `swap` y `rot` pronto se vuelve ilegible.

**Lee más:**

- [Máquina de pila](https://en.wikipedia.org/wiki/Stack_machine) (Wikipedia)
- [Notación polaca inversa](https://en.wikipedia.org/wiki/Reverse_Polish_notation) (Wikipedia)
- [Forth (lenguaje de programación)](https://en.wikipedia.org/wiki/Forth_(programming_language)) (Wikipedia)
