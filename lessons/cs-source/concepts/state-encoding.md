---
title: "Cómo representar el estado"
chapter: 2
order: 30
---
Todo estado debe quedar escrito en algún medio. Un número puede ser marcas de conteo (unario), cifras (decimales o binarias) o incluso un solo entero enorme que codifica todo un programa (numeración de Gödel). La elección de *representación* determina qué resulta fácil. Las marcas de conteo son fáciles de reescribir con buscar y reemplazar, pero ocupan mucho. En [[entry:regex-sed]] todo el estado del programa es una línea de texto. Los números son filas de marcas que las sustituciones alargan y acortan. Las cláusulas `PIC` de COBOL también son una representación: la máscara de un campo determina su tamaño, redondeo y rango.

- **Úsala cuando:** tu medio no tenga números o variables y debas decidir cómo se representa "una cuenta".
- **Evita el sistema unario para números grandes:** un millón requiere un millón de marcas.

**Lee más:**

- [Sistema de numeración unario](https://en.wikipedia.org/wiki/Unary_numeral_system) (Wikipedia)
- [Numeración de Gödel](https://en.wikipedia.org/wiki/G%C3%B6del_numbering) (Wikipedia)
