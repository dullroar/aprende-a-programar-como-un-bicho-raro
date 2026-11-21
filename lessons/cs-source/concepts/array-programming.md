---
title: "Programación con arreglos"
chapter: 4
order: 80
---
La programación con arreglos aplica una operación a todo un arreglo de una vez. Los escalares se extienden para ajustarse al arreglo y los bucles explícitos casi desaparecen. Kenneth Iverson inventó APL para esto en los años 1960 y la idea sigue viva en J, K, R, MATLAB y NumPy. Existe porque acorta el código y porque el hardware puede procesar muchos elementos a la vez (SIMD y GPU). [[entry:apl]] muestra el estilo. Cinco extracciones al azar, una suma acumulada `+\` y una selección que se detiene cuando deja de cumplirse la condición sustituyen al bucle. Describe la respuesta completa y luego recórtala.

```mermaid
flowchart TB
    accTitle: La programación con arreglos describe transformaciones en bloque sobre vectores completos y a menudo sustituye al flujo de control explícito
    accDescr: Una canalización de arreglos completos sin bucle. El arreglo de horas es 19, 16, 19, 11. Una suma acumulada da los totales 19, 35, 54, 65. Al comparar cada total con 40 se obtienen las banderas 1, 1, 0, 0. La suma de las banderas da 2. Añade 1 y obtienes 3 tarjetas que conservar. Si tomas 3 elementos del arreglo de horas, obtienes 19, 16, 19.
    H["horas: 19 16 19 11"] -->|"suma acumulada"| T["totales: 19 35 54 65"]
    T -->|"compara cada total con 40"| F["40 como máximo: 1 1 0 0"]
    F -->|"suma las banderas y añade 1"| N["tarjetas que se conservan: 3"]
    N -->|"toma 3 del arreglo de horas"| K["se conservan: 19 16 19"]
```

Lee la imagen de arriba abajo. Cada paso es una operación sobre un arreglo completo. Ningún paso es un bucle. La comparación da una bandera para cada total, todas a la vez. Cada bandera indica si el total cumple la condición. Cuenta las banderas con valor 1 y añade uno. Ese es el número de tarjetas que se conservan, porque también se guarda la tarjeta con la que el total pasa de 40. [[entry:apl]] funciona así. Estos números solo son un ejemplo. La idea no depende de los símbolos de APL.

- **Úsala cuando:** trabajes con números, tablas y señales.
- **Evítala cuando:** el algoritmo deba avanzar un paso tras otro o los arreglos intermedios no quepan en memoria. Recuerda también que una notación densa es difícil para un equipo que no la sabe leer.

**Lee más:**

- [Programación con arreglos](https://en.wikipedia.org/wiki/Array_programming) (Wikipedia)
- [APL (lenguaje de programación)](https://en.wikipedia.org/wiki/APL_(programming_language)) (Wikipedia)
- [Kenneth E. Iverson](https://en.wikipedia.org/wiki/Kenneth_E._Iverson) (Wikipedia)
- [Una instrucción, múltiples datos](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) (Wikipedia)
