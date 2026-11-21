---
title: "Lenguajes de marcado"
chapter: 5
order: 80
---
Un lenguaje de marcado es texto con anotaciones que describen su estructura: HTML, XML, Markdown y XAML. Permite que personas y herramientas compartan un mismo documento y que el contenido quede separado de la presentación. XAML describe un árbol de objetos de interfaz de usuario y un cargador crea los objetos. Un formato que puede nombrar *tipos* y *métodos* entraña un peligro. En ese caso, cargar un archivo significa ejecutar código que eligió su autor. Esa es la idea detrás de muchos ataques de deserialización. Es justo lo que hace [[entry:xaml]] a propósito. Todo el comportamiento del programa está en un solo archivo de marcado y se ejecuta durante su análisis sintáctico.

- **Úsalo cuando:** describas documentos o datos que deban leer tanto las personas como las herramientas.
- **Evítalo cuando:** un documento no confiable pueda elegir tipos arbitrarios o llamar a métodos arbitrarios. Usa una lista de elementos permitidos.

**Lee más:**

- [Lenguaje de marcado](https://en.wikipedia.org/wiki/Markup_language) (Wikipedia)
- [XAML](https://en.wikipedia.org/wiki/XAML) (Wikipedia)
- [Ataque de entidad externa XML](https://en.wikipedia.org/wiki/XML_external_entity_attack) (Wikipedia)
- [Guía rápida de deserialización](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html) (OWASP), sobre cómo cargar datos con seguridad
