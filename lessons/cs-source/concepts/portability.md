---
title: "Portabilidad"
chapter: 8
order: 30
---
El software es portable si se ejecuta bien en más de un entorno: otro sistema operativo, otra implementación del mismo lenguaje u otra versión. La portabilidad es un objetivo porque tus usuarios no tienen todos tu misma máquina. Las herramientas habituales son un estándar escrito, una capa delgada que cubra las diferencias y pruebas en más de una plataforma. Aquí las entradas ofrecen ejemplos honestos. El subconjunto POSIX de AWK se ejecuta en todas partes. Pero usar una expresión regular como separador de registros es una extensión de gawk. En mawk, [[entry:awk-weird]] lee sin parar. `close()` devuelve valores distintos según la implementación de AWK. El `pcre2grep` de Ubuntu se compila sin scripts de callout.

- **Úsala cuando:** escribas para usuarios cuyo entorno no controlas. Elige un estándar y prueba al menos dos implementaciones.
- **Evita tomarla como dogma:** si un truco requiere una implementación concreta, nómbrala, fija su versión e indícalo en el README.

**Lee más:**

- [Portabilidad del software](https://en.wikipedia.org/wiki/Software_portability) (Wikipedia)
- [POSIX](https://en.wikipedia.org/wiki/POSIX) (Wikipedia)
