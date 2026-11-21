---
title: "Código automodificable"
chapter: 3
order: 80
---
El código automodificable cambia sus propias instrucciones mientras se ejecuta. Las primeras computadoras lo hacían para ahorrar memoria, que era escasa. Hoy la idea sigue viva en los compiladores en tiempo de ejecución, los cargadores de programas y el software malicioso que se oculta. En este repositorio es una forma de trasladar el flujo de control al texto del programa. [[entry:apl-weird]] lee el código fuente de una función con `⎕CR`, lo reescribe y define la nueva versión con `⎕FX`. [[entry:cobol-weird]] cambia un `GO TO` con `ALTER`. [[entry:tcl-weird]] guarda el código fuente del procedimiento en una tabla de la base de datos y lo define bajo demanda.

- **Úsalo cuando:** generes código con un límite claro: escribe el texto, compílalo y ejecútalo. Eso hacen los compiladores JIT (compilación justo a tiempo) y los generadores de código.
- **Evítalo en los programas escritos a mano.** Los depuradores, las cachés y las herramientas de seguridad suponen que el código no cambia (algunos sistemas prohíben que una zona de memoria sea escribible y ejecutable a la vez).

**Lee más:**

- [Código automodificable](https://en.wikipedia.org/wiki/Self-modifying_code) (Wikipedia)
- [Compilación en tiempo de ejecución](https://en.wikipedia.org/wiki/Just-in-time_compilation) (Wikipedia)
