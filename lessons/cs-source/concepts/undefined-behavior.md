---
title: "Comportamiento indefinido, no especificado y definido por la implementación"
chapter: 8
order: 20
---
Los estándares usan tres palabras distintas para decir "el estándar no lo dice del todo". **Comportamiento indefinido**: puede pasar cualquier cosa, incluso una caída o un agujero de seguridad. **Comportamiento no especificado**: uno de varios resultados permitidos, y la implementación no tiene que decir cuál. **Comportamiento definido por la implementación**: la implementación debe elegirlo y documentarlo. Las palabras vienen de C y C++, pero la idea vale en todas partes. Existe para dar libertad a los compiladores de optimizar y de ejecutarse en hardware distinto. Las tres etiquetas de este libro (garantizado, permitido por la implementación, aprovechado por accidente) son la misma idea en palabras más amigables. Ejemplos: `ALTER` de COBOL lo conserva GnuCOBOL pero se quitó del estándar, y los significados de `⊃` y `↑` difieren entre GNU APL y Dyalog.

- **Úsalo cuando:** leas un estándar: averigua en qué tipo de "no especificado" te estás apoyando.
- **Evita depender de él.** Herramientas como AddressSanitizer pueden detectar parte del comportamiento indefinido de C y C++ durante la ejecución.

**Más información:**

- [Comportamiento indefinido](https://en.wikipedia.org/wiki/Undefined_behavior) (Wikipedia)
- [Comportamiento no especificado](https://en.wikipedia.org/wiki/Unspecified_behavior) (Wikipedia)
- [AddressSanitizer](https://en.wikipedia.org/wiki/AddressSanitizer) (Wikipedia)
