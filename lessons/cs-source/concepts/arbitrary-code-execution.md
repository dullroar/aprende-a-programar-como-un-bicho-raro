---
title: "Ejecución de código arbitrario"
chapter: 1
order: 20
---
La ejecución de código arbitrario ocurre cuando un atacante hace que un programa ejecute instrucciones que su autor nunca previó. Suele ocurrir por accidente: un desbordamiento de búfer, una cadena de texto inyectada o un formato de archivo más potente de lo que se creía. Aquí importa porque muchas entradas del repositorio hacen lo mismo *a propósito, en un lugar seguro*. El `ObjectDataProvider` de XAML llama a métodos durante el análisis del archivo. La construcción `(?{ ... })` de Perl ejecuta código en mitad de una coincidencia. El gancho `unknown` de Tcl ejecuta código guardado en una fila de la base de datos. El mecanismo siempre es el mismo: **se leen datos como código**.

- **Usa esta idea cuando:** revises cualquier función que "evalúe" algo: `eval`, plantillas, deserializadores, expansores de macros o cargadores de complementos.
- **Evita la técnica cuando:** la entrada de datos venga de alguien en quien no confías. Si necesitas puntos de extensión, ofrece una interfaz pequeña y declarada (una API de complementos o un lenguaje de expresiones mínimo) en lugar de un `eval` general.

**Lee más:**

- [Ejecución de código arbitrario](https://en.wikipedia.org/wiki/Arbitrary_code_execution) (Wikipedia)
- [Inyección de código](https://en.wikipedia.org/wiki/Code_injection) (Wikipedia)
- [Inyección de código](https://owasp.org/www-community/attacks/Code_Injection) (OWASP), con ejemplos y defensas
- [`eval()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval) (MDN), cuya advertencia empieza con "¡Nunca uses eval() directo!"
