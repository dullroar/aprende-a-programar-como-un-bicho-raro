---
title: "Goto y programación estructurada"
chapter: 3
order: 20
---
`GOTO` salta a cualquier otro lugar del programa. En 1966 Böhm y Jacopini demostraron que nunca lo *necesitas*: la secuencia, la selección y los bucles bastan para cualquier cómputo. En 1968 Edsger Dijkstra escribió la famosa carta *Consideraciones sobre el daño que causa la sentencia Go To*. La programación estructurada se impuso porque puedes razonar sobre un bloque con una sola entrada y una sola salida. `ALTER` de COBOL va en la dirección contraria: cambia el destino de un `GO TO` *mientras el programa se ejecuta*. [[entry:cobol-weird]] lo usa como bucle. Más tarde retiraron esa sentencia del estándar de COBOL. GnuCOBOL todavía la ejecuta.

- **Usa `goto` cuando:** haya una razón de peso, como una única salida limpia para manejar errores en C o su uso en código generado y máquinas de estados.
- **Evítalo cuando:** un destino calculado o modificado durante la ejecución dificulte la lectura del código.

**Lee más:**

- [Goto](https://en.wikipedia.org/wiki/Goto) (Wikipedia)
- [Teorema de la programación estructurada](https://en.wikipedia.org/wiki/Structured_program_theorem) (Wikipedia)
- [Considerado perjudicial](https://en.wikipedia.org/wiki/Considered_harmful) (Wikipedia)
