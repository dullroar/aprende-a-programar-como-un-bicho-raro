---
title: "Fugas de abstracción y dependencia de la implementación"
---
Para una lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre portabilidad, abstracción y costo](../guias-de-estudio/conceptos/portabilidad-abstraccion-y-costo.md).

Toda abstracción oculta algo y tarde o temprano lo que oculta sale a la luz. De esos momentos trata este capítulo. El estándar de un lenguaje promete unas cosas, permite otras e ignora el resto. Un optimizador puede omitir código que, según el lenguaje, nadie puede observar. Una expresión regular que acaba rápido en todas las pruebas puede tardar un año con una mala entrada de datos. Una característica que nadie prometió puede ser la que todos usan.

Estas ideas explican las tres etiquetas que usa cada lección. **Garantizado** significa que la especificación lo promete. **Permitido por la implementación** significa que una implementación lo permite. **Aprovechado por accidente** significa que funciona y nadie lo prometió. Los conceptos que siguen te dan el vocabulario: abstracciones con fugas, comportamiento indefinido y no especificado, portabilidad, optimizadores, ley de Hyrum, complejidad temporal y ReDoS (denegación de servicio por expresiones regulares). También incluyen la reproducibilidad: anotar toda entrada de datos para que las mismas fuentes den el mismo resultado.
