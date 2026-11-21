---
title: "Seguridad basada en teoría de lenguajes"
chapter: 5
order: 100
---
La seguridad basada en teoría de lenguajes (LangSec) es una forma de pensar en la seguridad. Cada formato de entrada de datos es un lenguaje formal: el código que lo lee es el encargado de reconocerlo. Muchos ataques funcionan porque dos analizadores sintácticos leen los mismos bytes de forma distinta. Otros funcionan porque el lenguaje de entrada es tan potente que nadie puede decir qué hará. De ahí el consejo: mantén los formatos simples (consulta [[turing-completeness]]) y termina todo el análisis sintáctico *antes* de actuar. Usa un solo analizador sintáctico bien probado. Este enfoque también critica el viejo "principio de robustez", *sé flexible con lo que aceptas*, porque la flexibilidad da más significados a los mismos bytes. El IETF también ha vuelto a examinar ese principio.

- **Úsala cuando:** diseñes un formato de archivo, un protocolo o una API o revises código que lee una entrada de datos.
- **Evítala cuando:** el diseño exija aceptar una entrada de datos "casi válida" o mezclar el análisis sintáctico con el procesamiento.

**Lee más:**

- [Seguridad basada en teoría de lenguajes](https://en.wikipedia.org/wiki/Language-theoretic_security) (Wikipedia)
- [Principio de robustez](https://en.wikipedia.org/wiki/Robustness_principle) (Wikipedia)
- [RFC 9413: Cómo mantener protocolos robustos](https://www.rfc-editor.org/rfc/rfc9413), la visión moderna del principio según el IETF
