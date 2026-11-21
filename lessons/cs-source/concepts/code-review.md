---
title: "Revisión de código"
chapter: 1
order: 50
applies-to: all
applies-because: "El README de cada entrada tiene una sección Cómo funciona el truco. Es la explicación en lenguaje claro que el revisor contrasta con el código. El control rechaza toda entrada nueva que carezca de esa sección."
---
En una revisión de código, otra persona lee tu código antes de que se acepte. Existe porque las pruebas solo comprueban lo que se te ocurrió probar. Un lector puede notar algo que se te pasó. Aquí la revisión tiene una forma concreta: el README debe incluir la sección **Cómo funciona el truco** en lenguaje claro. Los revisores (personas y asistentes de IA) deben explicar el código en palabras sencillas y hacer una lista de todo lo que puede tocar. Si el revisor no puede seguir la entrada, esta no se integra, por ingeniosa que sea.

- **Úsala cuando:** hagas cualquier cambio, sobre todo si el código es inusual.
- **Evita depender solo de ella:** el cansancio hace que se pasen cosas por alto y los caracteres invisibles escapan a la vista. Combina la revisión con controles automáticos como `sandbox/scope-check.sh`.

**Lee más:**

- [Revisión de código](https://en.wikipedia.org/wiki/Code_review) (Wikipedia)
