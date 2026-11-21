---
title: "Optimizadores"
chapter: 8
order: 40
---
Un compilador optimizador reescribe tu programa para que se ejecute más rápido o use menos memoria. Debe conservar el *comportamiento observable* que define el lenguaje (la regla "como si"). Así puedes escribir código claro y aun así obtener código rápido. La fuga está en que todo lo que el lenguaje no considera observable puede desaparecer. En [[entry:regex-pcre2]], los callouts solo tienen efecto si el motor pasa por ellos. El optimizador puede saltárselos. Por eso el programa compila el patrón con `PCRE2_NO_AUTO_POSSESS`, `PCRE2_NO_START_OPTIMIZE` y `PCRE2_NO_DOTSTAR_ANCHOR`. Tampoco usa el JIT, que no admite callouts.

- **Úsalo cuando:** trabajes con código puro. Confía en el optimizador y mide antes de optimizar a mano.
- **Evítalo cuando:** la corrección dependa de efectos que el lenguaje puede descartar.

**Lee más:**

- [Compilador optimizador](https://en.wikipedia.org/wiki/Optimizing_compiler) (Wikipedia)
- [Regla "como si"](https://en.wikipedia.org/wiki/As-if_rule) (Wikipedia)
- [Eliminación de código muerto](https://en.wikipedia.org/wiki/Dead-code_elimination) (Wikipedia)
