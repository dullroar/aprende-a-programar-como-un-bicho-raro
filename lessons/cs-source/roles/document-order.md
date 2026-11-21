---
title: "El orden del documento es el programa"
order: 90
---
El orden del documento es el orden del programa. [[entry:xaml]] no tiene código detrás. El analizador sintáctico de XAML construye objetos en el orden en que los lee, y varios de esos objetos llaman a métodos al crearse. Cuatro pasadas desenrolladas reemplazan el bucle, los arreglos "portadores" son las variables y las expresiones de SQL o de `DataTable` toman las decisiones. El programa es el archivo de marcado, y se ejecuta mientras se analiza el archivo. [[entry:tar-gnu]] es la misma idea con una cinta en lugar de un archivo de marcado: los miembros del archivo tar son las instrucciones, y el orden del archivo es el orden del programa.
