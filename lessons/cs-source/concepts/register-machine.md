---
title: "Máquinas de registros y máquinas de contadores"
chapter: 2
order: 70
---
Una máquina de registros guarda sus valores en unas pocas casillas numeradas que se llaman registros. Los procesadores reales son máquinas de registros. La versión más pequeña, una *máquina de contadores*, solo tiene dos operaciones: sumar uno a un registro o restarle uno y saltar si el resultado es cero. Sirve para razonar. Es lo bastante simple como para demostrar sus propiedades y lo bastante potente como para calcular cualquier cosa (bastan dos contadores). Varias entradas son máquinas de registros disfrazadas. En CMake, de `CMAKE_MATCH_1` a `CMAKE_MATCH_5` son los registros de [[entry:cmake]]. Los grupos de equilibrio de .NET en [[entry:regex-dotnet]] forman un contador.

```mermaid
flowchart TB
    accTitle: Una máquina de registros identifica sus celdas. Una máquina de contadores solo necesita sumar, restar y comprobar si llega a cero
    accDescr: Dos paneles. En la máquina de registros, los registros R1 y R2 contienen 19 y 23. La instrucción ADD R1, R2 guarda el resultado en R1. R1 queda con 42 y R2 conserva 23. En la máquina de contadores, C1 y C2 empiezan en 2 y 0. Un bucle decrementa C1, incrementa C2 y comprueba si C1 vale cero. Si C1 no vale cero, el bucle se ejecuta de nuevo. Cuando C1 llega a cero, C1 vale 0 y C2 vale 2.
    subgraph CNT["Máquina de contadores"]
        direction TB
        c1["C1 = 2, C2 = 0"] --> c2["DEC C1, INC C2"]
        c2 --> c3{{"¿C1 vale cero?"}}
        c3 -->|"no: repite el bucle"| c2
        c3 -->|"sí"| c4["C1 = 0, C2 = 2"]
    end
    subgraph REG["Máquina de registros"]
        direction TB
        r1["R1 = 19, R2 = 23"] -->|"ADD R1, R2 a R1"| r2["R1 = 42, R2 = 23"]
    end
```

A la izquierda, la instrucción nombra sus celdas (`R1` y `R2`). A la derecha, la máquina tiene dos contadores y tres acciones: contar hacia abajo, contar hacia arriba y comprobar si el valor es cero. Pasar la cuenta de `C1` a `C2` requiere una vuelta del bucle por unidad. Por eso una máquina de contadores es lenta a propósito. Muestra con qué poca maquinaria basta.

- **Úsala cuando:** quieras explicar qué *es* un sistema insólito al identificar sus registros.
- **Evítala como estilo de programación:** es un modelo para razonar, no una forma de escribir programas.

**Lee más:**

- [Máquina de registros](https://en.wikipedia.org/wiki/Register_machine) (Wikipedia)
- [Máquina de contadores](https://en.wikipedia.org/wiki/Counter_machine) (Wikipedia)
