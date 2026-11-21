---
title: "Modelo de amenazas"
chapter: 1
order: 10
---
Un modelo de amenazas responde cuatro preguntas sencillas. ¿Qué protegemos? ¿Quién podría atacarlo? ¿Cómo podría hacerlo? ¿Qué haremos al respecto? Existe porque nadie puede defenderse de "todo". Te defiendes de una lista, y esa lista es el modelo de amenazas. Los equipos lo usan para decidir dónde gastar el tiempo de revisión y qué protecciones añadir. Este repositorio da la vuelta a la pregunta habitual. El código es lo que *no* es de fiar (una solicitud de cambios de un desconocido), y lo que protegemos es la máquina de quien revisa. Por eso [`CONTRIBUTING.md`](../../CONTRIBUTING.md) pide un script de comprobación que se ejecute en un sistema desechable y sin red.

- **Úsalo cuando:** vayas a ejecutar, instalar o revisar código que no escribiste, o cuando diseñes cualquier cosa que acepte entrada de datos.
- **Evítalo cuando:** lo trates como un documento que se escribe una sola vez. Un modelo de amenazas que nadie actualiza describe un sistema que ya no existe.

**Dos ejemplos de este repositorio, donde el modelo de amenazas tuvo que cambiar:**

- **"Es solo marcado."** La entrada de XAML ([[entry:xaml]]) inspiró directamente un segundo proyecto, [xaml-write-and-run](https://github.com/dullroar/xaml-write-and-run). Ese proyecto construye la forma de un canal de comando y control solo con archivos `.xaml`: un archivo escribe el siguiente en el disco, un objeto posterior del mismo documento lo carga y lo ejecuta, y la cadena se extiende sola. Una variante descarga sus siguientes instrucciones de la web. Se apoya en un camino de ataque muy conocido (el clásico gadget de deserialización `ObjectDataProvider`), que los defensores ya conocen y vigilan. Esa es la lección. Incluso en un camino bien vigilado, "es solo marcado" es un falso consuelo: un analizador sintáctico de confianza que lee marcado influido por un atacante está ejecutando un programa, así que tu modelo de amenazas debe tratar el marcado como código.
- **"Es solo una expresión regular."** La entrada de Perl ([[entry:regex-perl]]) es una única coincidencia de patrón. Dentro de esa coincidencia, unos bloques de código Perl cargan los datos, escriben en una base de datos e imprimen, y luego la coincidencia devuelve falso a propósito. Si tu modelo de amenazas solo se preocupa de que una expresión regular se ejecute despacio (mira [[redos]]), actualízalo. Una expresión regular también puede ejecutar código, y un patrón merece el mismo cuidado que cualquier otro programa que aceptes.

**Más información:**

- [Modelo de amenazas](https://en.wikipedia.org/wiki/Threat_model) (Wikipedia)
- [RFC 3552, sección 3: el modelo de amenazas de Internet](https://www.rfc-editor.org/rfc/rfc3552), un ejemplo breve y práctico del IETF
- [Modelado de amenazas](https://owasp.org/www-community/Threat_Modeling) (OWASP), una guía paso a paso
