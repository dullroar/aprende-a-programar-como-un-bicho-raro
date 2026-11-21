---
title: "Análisis sintáctico"
chapter: 5
order: 30
---
El análisis sintáctico convierte texto en una estructura según una gramática. Existe porque los programas y los datos llegan como texto plano pero la computadora necesita un árbol. Hay analizadores sintácticos de *descenso recursivo* escritos a mano y otros que se generan. Toda herramienta de XML, JSON o de un lenguaje de programación tiene uno. JSON ilustra cómo se documenta con exactitud la gramática de un formato (RFC 8259). En el análisis sintáctico también se vuelve peligrosa la entrada de datos: ahí está el primer código que toca datos no confiables. Dos entradas muestran analizadores que hacen más que leer. En [[entry:forth-weird]], el intérprete de texto analiza una palabra y la ejecuta enseguida. Así, el programa puede cambiar la posición de lectura del intérprete. En [[entry:xaml]], el analizador sintáctico crea objetos *y llama a métodos* mientras lee el archivo.

- **Úsalo cuando:** aceptes una entrada de datos estructurados. Usa un verdadero analizador sintáctico y una gramática real.
- **Evita los atajos con `split` o una expresión regular:** pueden pasar por alto una estructura anidada. Mantén los efectos separados del análisis sintáctico.

**Lee más:**

- [Análisis sintáctico](https://en.wikipedia.org/wiki/Parsing) (Wikipedia)
- [Analizador sintáctico de descenso recursivo](https://en.wikipedia.org/wiki/Recursive_descent_parser) (Wikipedia)
- [RFC 8259: el formato JSON](https://www.rfc-editor.org/rfc/rfc8259), una gramática breve y precisa
