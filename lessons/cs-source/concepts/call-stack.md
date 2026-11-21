---
title: "La pila de llamadas"
chapter: 6
order: 20
---
La pila de llamadas es una pila de *marcos*. Cada llamada a una función que sigue activa tiene un marco. Este guarda su dirección de retorno y sus variables locales. Así una función puede llamar a otra y la recursión funciona. Para la mayoría de los programadores, la pila de llamadas *es* la respuesta a "¿en qué parte del programa estoy?". Varias entradas prescinden de ella o la esquivan. Un script de sed no hace llamadas. m4 y Make repiten al volver a leer texto. En [[entry:tcl-weird]], el límite a la recursión de disparadores lo impone la base de datos y no una pila que puedas ver.

```mermaid
flowchart TB
    accTitle: La pila de llamadas registra dónde va la ejecución y qué le falta a cada llamada activa
    accDescr: Dos partes. A la izquierda hay una pila de llamadas con tres marcos. El más reciente está arriba. El marco superior es de saveRow. Contiene su argumento, su variable local y una dirección de retorno a drawCard. Debajo está el de drawCard, con sus variables locales y una dirección de retorno a main. Abajo está el de main, con sus variables locales y una dirección de retorno al entorno de ejecución. A la derecha están los retornos en orden. Primero retorna saveRow y se retira su marco. Luego retorna drawCard. Por último retorna main.
    subgraph STACK["Pila de llamadas"]
        direction TB
        f3["arriba: saveRow(card). Locales: sql. Retorna a drawCard"] ~~~ f2["drawCard(). Locales: hours, category. Retorna a main"] ~~~ f1["abajo: main(). Locales: total, rows. Retorna al entorno de ejecución"]
    end
    subgraph RET["Retornos, en orden"]
        direction TB
        r1["1. retorna saveRow y se retira su marco"] --> r2["2. retorna drawCard y se retira su marco"] --> r3["3. retorna main y la pila queda vacía"]
    end
    STACK ~~~ RET
```

Cada llamada activa tiene su propio marco y el marco más reciente queda arriba. Cuando `saveRow` retorna, se retira su marco. La ejecución sigue en la dirección de retorno que guardaba el marco, dentro de `drawCard`. Los nombres son ejemplos. La estructura exacta de un marco varía entre lenguajes y procesadores. Consulta [[stack-data-structure]] para ver la idea general de una pila.

- **Úsala cuando:** leas una traza de pila o razones sobre la profundidad de la recursión.
- **Evítala cuando:** la profundidad de la recursión no tenga límite. Un desbordamiento de pila termina el programa. En lenguajes sin garantías de seguridad, puede abrir una brecha de seguridad.

**Lee más:**

- [Pila de llamadas](https://en.wikipedia.org/wiki/Call_stack) (Wikipedia)
- [Desbordamiento de búfer en la pila](https://en.wikipedia.org/wiki/Stack_buffer_overflow) (Wikipedia)
- [Llamada de cola](https://en.wikipedia.org/wiki/Tail_call) (Wikipedia)
