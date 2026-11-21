---
title: "Programación declarativa"
chapter: 5
order: 60
---
La programación declarativa dice *qué* quieres, no *cómo* obtenerlo. SQL, HTML, CSS, Make, las expresiones regulares y la columna de patrones de AWK son declarativos. Una herramienta que conoce la meta puede elegir el método: una base de datos elige el plan de consulta y `make` elige el orden de compilación. La trampa es creer que "declarativo" significa "inofensivo". Cuando una notación declarativa puede nombrar una función y pasarle argumentos, está a un paso de ser un programa. Sirven de ejemplo `ObjectDataProvider` de XAML y `include` de Make. [[entry:xaml]] y [[entry:make-gnu]] muestran adónde lleva ese paso.

- **Úsala cuando:** la tarea sea una consulta, una configuración o una compilación. Deja que la herramienta optimice.
- **Evítala cuando:** no puedas controlar qué puede llamar un archivo no confiable. Comprueba qué llamadas tiene permitidas.

**Lee más:**

- [Programación declarativa](https://en.wikipedia.org/wiki/Declarative_programming) (Wikipedia)
- [Regla de la menor potencia](https://en.wikipedia.org/wiki/Rule_of_least_power) (Wikipedia)
