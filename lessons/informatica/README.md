<!-- GENERADO por lessons/book/build.py a partir de lessons/cs-source/ y del frontmatter de las entradas. No lo edites; edita las fuentes y ejecuta build.py. -->

# Por concepto de ciencias de la computación

La mayoría de los libros de informática te enseñan *un lenguaje*. Esta parte te enseña las *ideas* que comparten los lenguajes. Para cada idea hay una explicación breve y sencilla. Verás por qué existe, por qué se usa y cuándo conviene usarla. También verás cuándo no conviene. Luego verás qué entradas de este repositorio usan esa idea y podrás leer el código.

Las ideas se organizan en ocho grupos. Cada grupo se apoya en los anteriores. Las preguntas van desde "¿Qué es una máquina?" hasta "¿Qué pasa cuando se filtran las reglas de la máquina?". Un noveno grupo pone las entradas lado a lado para que veas que programas muy distintos desempeñan el mismo papel. Un décimo grupo vuelve al flujo de control con otra respuesta a "¿Qué se ejecuta después?": un evento. Lee los grupos en orden o salta a un concepto en el índice al final de esta página.

Los primeros enlaces de cada concepto llevan a Wikipedia. Los demás solo llevan a fuentes antiguas, estables y de libre reutilización, como los RFC del IETF, OWASP y MDN. Si quieres contribuir al libro, etiqueta tu propia entrada. Consulta [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

Las dos partes siguientes examinan el mismo material desde otras perspectivas. [Por lenguaje](../lenguajes/README.md) recorre los lenguajes uno por uno. [Por patrones de solución](../patrones.md) recorre los mecanismos.

## Los capítulos

- [Cómo leer un programa adversarial](01-lectura-de-un-programa-adversarial.md)
  - Modelo de amenazas
  - Ejecución de código arbitrario
  - Entorno aislado
  - Principio de mínimo privilegio
  - Revisión de código
  - Trojan Source: caracteres que no puedes ver
  - Especificación frente a implementación
  - Capacidad y autoridad
- [¿Qué cuenta como máquina?](02-que-cuenta-como-maquina.md)
  - Modelos de cómputo
  - Sistemas de transición y máquinas de estados
  - Cómo representar el estado
  - Invariantes
  - Observabilidad
  - Máquinas de pila
  - Máquinas de registros y máquinas de contadores
  - Máquinas de Turing
  - Algoritmos de Markov
  - Completitud de Turing
  - Semántica operacional
  - Cálculo frente a orquestación
- [Flujo de control y continuaciones](03-flujo-de-control-y-continuaciones.md)
  - Flujo de control
  - Goto y programación estructurada
  - El contador de programa
  - Recursión
  - Iteración de punto fijo
  - Corrutinas
  - Continuaciones
  - Código automodificable
  - Relojes lógicos y orden de los eventos
- [Evaluación y demanda](04-evaluacion-y-demanda.md)
  - Estrategias de evaluación
  - Evaluación inmediata
  - Evaluación perezosa
  - Evaluación de cortocircuito
  - Ejecución diferida
  - Iteradores y generadores
  - Transparencia referencial
  - Programación con arreglos
  - Funciones de primera clase y de orden superior
  - Funtores y mapeo
  - Monoides y plegados
  - Programación por flujo de datos
- [Los lenguajes formales como sustratos de cómputo](05-lenguajes-formales-como-sustratos-de-computacion.md)
  - La jerarquía de Chomsky
  - Expresiones regulares
  - Análisis sintáctico
  - Reescritura de términos y de cadenas de texto
  - Macros y expansión de texto
  - Programación declarativa
  - Lenguajes específicos de dominio
  - Lenguajes de marcado
  - Automatización de la compilación
  - Seguridad basada en teoría de lenguajes
  - Máquinas raras
  - Teoría de categorías
  - Intérpretes y máquinas virtuales
- [Estado más allá de las variables](06-estado-mas-alla-de-las-variables.md)
  - Estado
  - La pila de llamadas
  - La pila como estructura de datos
  - Ámbito y enlace de nombres
  - Clausuras y entornos léxicos
  - Homoiconicidad: código como datos
  - Reflexión y metaprogramación
  - Grafos de dependencias
  - Disparadores de base de datos
  - Serialización, deserialización y pickling de objetos
- [Efectos, errores y confirmación](07-efectos-errores-y-confirmacion.md)
  - Efectos secundarios
  - Mónadas y sistemas de efectos
  - Manejo de excepciones
  - Estado de salida
  - Restricciones de integridad
  - Retroceso
  - El corte: cómo fijar una elección
  - Transacciones
  - Idempotencia
  - Seguridad entre hilos y afinidad de hilo
- [Fugas de abstracción y dependencia de la implementación](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md)
  - Abstracciones con fugas
  - Comportamiento indefinido, no especificado y definido por la implementación
  - Portabilidad
  - Optimizadores
  - Ley de Hyrum
  - Precipicios de rendimiento y complejidad temporal
  - Denegación de servicio mediante expresiones regulares
  - Reproducibilidad y compilaciones deterministas
- [Casos de estudio comparativos](09-casos-de-estudio-comparativos.md)
  - Un bucle ordinario, usado en un lugar inusual
  - Una secuencia perezosa que alguien sigue pidiendo
  - Operaciones sobre arreglos completos en lugar de pasos
  - Texto que se reescribe y se vuelve a leer
  - Flujo de control que se reescribe a sí mismo
  - Búsqueda con regex, efectos secundarios y fallo deliberado
  - Búsqueda con regex que devuelve capturas
  - Despacho y disparadores: la regla activa el siguiente paso
  - La entrada de datos es el bucle
  - El orden del documento es el programa
- [Eventos, funciones de devolución de llamada y flujo de control reactivo](10-eventos-retrollamadas-y-flujo-de-control-reactivo.md)
  - Programación dirigida por eventos
  - Funciones de devolución de llamada
  - Publicación y suscripción
  - El bucle de eventos y la planificación de turnos
  - Contrapresión

## Índice de conceptos

| Concepto | Capítulo | Entradas que lo usan |
| --- | --- | --- |
| [Abstracciones con fugas](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#abstracciones-con-fugas) | Fugas de abstracción y dependencia de la implementación | `tar-gnu-weird` |
| [Algoritmos de Markov](02-que-cuenta-como-maquina.md#algoritmos-de-markov) | ¿Qué cuenta como máquina? | `ed-weird`, `regex-sed` |
| [Análisis sintáctico](05-lenguajes-formales-como-sustratos-de-computacion.md#análisis-sintáctico) | Los lenguajes formales como sustratos de cómputo | `forth-weird`, `regex-dotnet`, `tar-gnu`, `xaml` |
| [Automatización de la compilación](05-lenguajes-formales-como-sustratos-de-computacion.md#automatización-de-la-compilación) | Los lenguajes formales como sustratos de cómputo | `cmake`, `make-gnu` |
| [Capacidad y autoridad](01-lectura-de-un-programa-adversarial.md#capacidad-y-autoridad) | Cómo leer un programa adversarial | `ed-weird`, `ex-weird`, `tar-gnu` |
| [Clausuras y entornos léxicos](06-estado-mas-alla-de-las-variables.md#clausuras-y-entornos-léxicos) | Estado más allá de las variables | `JavaChallenge1` (analogía), `javascript`, `javascript-weird`, `ModernChallenge1`, `RustChallenge1` |
| [Completitud de Turing](02-que-cuenta-como-maquina.md#completitud-de-turing) | ¿Qué cuenta como máquina? | `m4`, `make-gnu`, `regex-sed` |
| [Comportamiento indefinido, no especificado y definido por la implementación](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#comportamiento-indefinido-no-especificado-y-definido-por-la-implementación) | Fugas de abstracción y dependencia de la implementación | `cobol-weird`, `find-gnu`, `find-posix` |
| [Continuaciones](03-flujo-de-control-y-continuaciones.md#continuaciones) | Flujo de control y continuaciones | `cobol-weird` (analogía), `forth-weird` (analogía), `javascript-weird` (contraejemplo), `make-gnu` (analogía), `tar-gnu` (contraejemplo) |
| [Contrapresión](10-eventos-retrollamadas-y-flujo-de-control-reactivo.md#contrapresión) | Eventos, funciones de devolución de llamada y flujo de control reactivo | `javascript-events` (contraejemplo), `javascript-weird` (analogía), `tar-gnu-weird` (analogía) |
| [Corrutinas](03-flujo-de-control-y-continuaciones.md#corrutinas) | Flujo de control y continuaciones | `javascript-events` (contraejemplo), `javascript-weird` (analogía), `KotlinChallenge1` (analogía), `PythonChallenge1` (analogía), `RustChallenge1` (analogía) |
| [Cálculo frente a orquestación](02-que-cuenta-como-maquina.md#cálculo-frente-a-orquestación) | ¿Qué cuenta como máquina? | `ed-weird`, `ex-weird`, `javascript-weird`, `regex-pcre2`, `tar-gnu`, `tar-gnu-weird`, `xaml` |
| [Código automodificable](03-flujo-de-control-y-continuaciones.md#código-automodificable) | Flujo de control y continuaciones | `apl-weird`, `cobol-weird`, `ex-weird` |
| [Cómo representar el estado](02-que-cuenta-como-maquina.md#cómo-representar-el-estado) | ¿Qué cuenta como máquina? | `cobol`, `ed-weird`, `ex-weird`, `find-gnu`, `find-posix`, `regex-sed`, `tar-gnu`, `tar-gnu-weird` |
| [Denegación de servicio mediante expresiones regulares](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#denegación-de-servicio-mediante-expresiones-regulares) | Fugas de abstracción y dependencia de la implementación | `regex-sed` |
| [Disparadores de base de datos](06-estado-mas-alla-de-las-variables.md#disparadores-de-base-de-datos) | Estado más allá de las variables | `tcl-weird` |
| [Efectos secundarios](07-efectos-errores-y-confirmacion.md#efectos-secundarios) | Efectos, errores y confirmación | `find-gnu`, `find-posix`, `GoChallenge1`, `haskell-weird`, `JavaChallenge1`, `javascript`, `javascript-events`, `javascript-weird`, `KotlinChallenge1`, `LinqChallenge1`, `LinqChallenge2`, `ModernChallenge1`, `PythonChallenge1`, `regex-pcre2`, `regex-pcre2grep`, `regex-perl`, `RustChallenge1`, `tar-gnu-weird`, `xaml` |
| [Ejecución de código arbitrario](01-lectura-de-un-programa-adversarial.md#ejecución-de-código-arbitrario) | Cómo leer un programa adversarial | `regex-perl`, `tar-gnu`, `tcl-weird`, `xaml` |
| [Ejecución diferida](04-evaluacion-y-demanda.md#ejecución-diferida) | Evaluación y demanda | `javascript-events`, `javascript-weird`, `LinqChallenge1`, `LinqChallenge2`, `ModernChallenge1` |
| [El bucle de eventos y la planificación de turnos](10-eventos-retrollamadas-y-flujo-de-control-reactivo.md#el-bucle-de-eventos-y-la-planificación-de-turnos) | Eventos, funciones de devolución de llamada y flujo de control reactivo | `javascript`, `javascript-events`, `javascript-weird`, `LinqChallenge1`, `ModernChallenge1`, `PythonChallenge1`, `RustChallenge1` |
| [El contador de programa](03-flujo-de-control-y-continuaciones.md#el-contador-de-programa) | Flujo de control y continuaciones | `cobol-weird`, `ex-weird`, `forth-weird` |
| [El corte: cómo fijar una elección](07-efectos-errores-y-confirmacion.md#el-corte-cómo-fijar-una-elección) | Efectos, errores y confirmación | `regex-pcre2`, `regex-pcre2grep`, `regex-perl` |
| [Entorno aislado](01-lectura-de-un-programa-adversarial.md#entorno-aislado) | Cómo leer un programa adversarial | todas las entradas |
| [Especificación frente a implementación](01-lectura-de-un-programa-adversarial.md#especificación-frente-a-implementación) | Cómo leer un programa adversarial | `ed-weird`, `ex-weird` |
| [Estado](06-estado-mas-alla-de-las-variables.md#estado) | Estado más allá de las variables | `apl-weird`, `awk-weird`, `cmake`, `cobol-weird`, `ed-weird`, `ex-weird`, `forth-weird`, `haskell-weird`, `javascript`, `javascript-events`, `javascript-weird`, `lisp-weird`, `m4`, `make-gnu`, `regex-dotnet`, `regex-pcre2`, `regex-perl`, `regex-sed`, `tar-gnu-weird`, `tcl-weird`, `xaml` |
| [Estado de salida](07-efectos-errores-y-confirmacion.md#estado-de-salida) | Efectos, errores y confirmación | `regex-pcre2grep`, `regex-sed`, `tar-gnu`, `tar-gnu-weird` |
| [Estrategias de evaluación](04-evaluacion-y-demanda.md#estrategias-de-evaluación) | Evaluación y demanda | `haskell`, `haskell-weird`, `PythonChallenge1` |
| [Evaluación de cortocircuito](04-evaluacion-y-demanda.md#evaluación-de-cortocircuito) | Evaluación y demanda | `find-gnu`, `find-posix`, `javascript`, `javascript-weird`, `lisp-weird` |
| [Evaluación inmediata](04-evaluacion-y-demanda.md#evaluación-inmediata) | Evaluación y demanda | `apl`, `apl-weird`, `javascript`, `javascript-weird`, `ModernChallenge1` |
| [Evaluación perezosa](04-evaluacion-y-demanda.md#evaluación-perezosa) | Evaluación y demanda | `haskell`, `haskell-weird`, `javascript-weird`, `KotlinChallenge1`, `LinqChallenge1`, `LinqChallenge2`, `m4`, `RustChallenge1` |
| [Expresiones regulares](05-lenguajes-formales-como-sustratos-de-computacion.md#expresiones-regulares) | Los lenguajes formales como sustratos de cómputo | `awk`, `awk-weird`, `cmake`, `ed-weird`, `find-gnu`, `regex-dotnet`, `regex-pcre2`, `regex-pcre2grep`, `regex-perl`, `regex-sed` |
| [Flujo de control](03-flujo-de-control-y-continuaciones.md#flujo-de-control) | Flujo de control y continuaciones | `apl-weird`, `awk`, `awk-weird`, `cmake`, `cobol`, `cobol-weird`, `find-gnu`, `find-posix`, `forth`, `forth-weird`, `GoChallenge1`, `haskell-weird`, `JavaChallenge1`, `javascript`, `javascript-events`, `LinqChallenge1`, `lisp`, `lisp-weird`, `make-gnu`, `ModernChallenge1`, `tcl-weird` |
| [Funciones de devolución de llamada](10-eventos-retrollamadas-y-flujo-de-control-reactivo.md#funciones-de-devolución-de-llamada) | Eventos, funciones de devolución de llamada y flujo de control reactivo | `javascript`, `javascript-events`, `javascript-weird`, `regex-pcre2`, `regex-pcre2grep` (analogía), `tar-gnu-weird`, `tcl-weird` |
| [Funciones de primera clase y de orden superior](04-evaluacion-y-demanda.md#funciones-de-primera-clase-y-de-orden-superior) | Evaluación y demanda | `haskell`, `javascript`, `javascript-weird`, `LinqChallenge1`, `RustChallenge1` |
| [Funtores y mapeo](04-evaluacion-y-demanda.md#funtores-y-mapeo) | Evaluación y demanda | `javascript-weird`, `LinqChallenge1` (analogía) |
| [Goto y programación estructurada](03-flujo-de-control-y-continuaciones.md#goto-y-programación-estructurada) | Flujo de control y continuaciones | `cobol-weird` |
| [Grafos de dependencias](06-estado-mas-alla-de-las-variables.md#grafos-de-dependencias) | Estado más allá de las variables | `make-gnu` |
| [Homoiconicidad: código como datos](06-estado-mas-alla-de-las-variables.md#homoiconicidad-código-como-datos) | Estado más allá de las variables | `apl-weird`, `ex-weird`, `lisp`, `lisp-weird`, `tcl-weird` |
| [Idempotencia](07-efectos-errores-y-confirmacion.md#idempotencia) | Efectos, errores y confirmación | `tar-gnu` |
| [Intérpretes y máquinas virtuales](05-lenguajes-formales-como-sustratos-de-computacion.md#intérpretes-y-máquinas-virtuales) | Los lenguajes formales como sustratos de cómputo | `ex-weird`, `regex-pcre2`, `tar-gnu`, `tcl-weird`, `xaml` |
| [Invariantes](02-que-cuenta-como-maquina.md#invariantes) | ¿Qué cuenta como máquina? | `javascript`, `javascript-events`, `javascript-weird`, `tar-gnu-weird` |
| [Iteración de punto fijo](03-flujo-de-control-y-continuaciones.md#iteración-de-punto-fijo) | Flujo de control y continuaciones | `m4`, `make-gnu`, `regex-sed` |
| [Iteradores y generadores](04-evaluacion-y-demanda.md#iteradores-y-generadores) | Evaluación y demanda | `haskell`, `javascript-weird`, `KotlinChallenge1`, `PythonChallenge1`, `RustChallenge1` |
| [La jerarquía de Chomsky](05-lenguajes-formales-como-sustratos-de-computacion.md#la-jerarquía-de-chomsky) | Los lenguajes formales como sustratos de cómputo | `regex-dotnet` |
| [La pila como estructura de datos](06-estado-mas-alla-de-las-variables.md#la-pila-como-estructura-de-datos) | Estado más allá de las variables | `forth`, `forth-weird`, `regex-dotnet` |
| [La pila de llamadas](06-estado-mas-alla-de-las-variables.md#la-pila-de-llamadas) | Estado más allá de las variables | `find-gnu`, `find-posix`, `javascript-events` |
| [Lenguajes de marcado](05-lenguajes-formales-como-sustratos-de-computacion.md#lenguajes-de-marcado) | Los lenguajes formales como sustratos de cómputo | `ModernChallenge1`, `xaml` |
| [Lenguajes específicos de dominio](05-lenguajes-formales-como-sustratos-de-computacion.md#lenguajes-específicos-de-dominio) | Los lenguajes formales como sustratos de cómputo | `awk`, `cmake`, `find-gnu`, `find-posix`, `LinqChallenge2`, `lisp`, `regex-pcre2`, `tar-gnu` |
| [Ley de Hyrum](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#ley-de-hyrum) | Fugas de abstracción y dependencia de la implementación | `cmake`, `ed-weird`, `find-gnu`, `find-posix`, `make-gnu`, `tar-gnu-weird` |
| [Macros y expansión de texto](05-lenguajes-formales-como-sustratos-de-computacion.md#macros-y-expansión-de-texto) | Los lenguajes formales como sustratos de cómputo | `lisp`, `lisp-weird`, `m4` |
| [Manejo de excepciones](07-efectos-errores-y-confirmacion.md#manejo-de-excepciones) | Efectos, errores y confirmación | `cobol-weird`, `javascript-events` |
| [Modelo de amenazas](01-lectura-de-un-programa-adversarial.md#modelo-de-amenazas) | Cómo leer un programa adversarial | `regex-perl`, `tar-gnu`, `xaml` |
| [Modelos de cómputo](02-que-cuenta-como-maquina.md#modelos-de-cómputo) | ¿Qué cuenta como máquina? | toda entrada que nombra su máquina |
| [Monoides y plegados](04-evaluacion-y-demanda.md#monoides-y-plegados) | Evaluación y demanda | `haskell`, `javascript`, `javascript-weird`, `LinqChallenge1`, `lisp` (analogía) |
| [Máquinas de pila](02-que-cuenta-como-maquina.md#máquinas-de-pila) | ¿Qué cuenta como máquina? | `forth`, `forth-weird` |
| [Máquinas de registros y máquinas de contadores](02-que-cuenta-como-maquina.md#máquinas-de-registros-y-máquinas-de-contadores) | ¿Qué cuenta como máquina? | `cmake`, `ex-weird`, `forth-weird`, `regex-dotnet` |
| [Máquinas de Turing](02-que-cuenta-como-maquina.md#máquinas-de-turing) | ¿Qué cuenta como máquina? | `m4` (analogía), `regex-sed` (analogía) |
| [Máquinas raras](05-lenguajes-formales-como-sustratos-de-computacion.md#máquinas-raras) | Los lenguajes formales como sustratos de cómputo | `ed-weird`, `ex-weird`, `find-gnu`, `find-posix`, `xaml` |
| [Mónadas y sistemas de efectos](07-efectos-errores-y-confirmacion.md#mónadas-y-sistemas-de-efectos) | Efectos, errores y confirmación | `haskell-weird` |
| [Observabilidad](02-que-cuenta-como-maquina.md#observabilidad) | ¿Qué cuenta como máquina? | `find-gnu`, `javascript-events`, `tar-gnu`, `tar-gnu-weird` |
| [Optimizadores](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#optimizadores) | Fugas de abstracción y dependencia de la implementación | `find-gnu`, `regex-pcre2` |
| [Portabilidad](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#portabilidad) | Fugas de abstracción y dependencia de la implementación | `awk-weird`, `ed-weird`, `ex-weird`, `find-posix`, `regex-pcre2grep`, `tar-gnu-weird` |
| [Precipicios de rendimiento y complejidad temporal](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#precipicios-de-rendimiento-y-complejidad-temporal) | Fugas de abstracción y dependencia de la implementación | `regex-sed` |
| [Principio de mínimo privilegio](01-lectura-de-un-programa-adversarial.md#principio-de-mínimo-privilegio) | Cómo leer un programa adversarial | `tar-gnu` |
| [Programación con arreglos](04-evaluacion-y-demanda.md#programación-con-arreglos) | Evaluación y demanda | `apl`, `apl-weird` |
| [Programación declarativa](05-lenguajes-formales-como-sustratos-de-computacion.md#programación-declarativa) | Los lenguajes formales como sustratos de cómputo | `awk`, `awk-weird`, `cobol`, `LinqChallenge2`, `make-gnu`, `xaml` |
| [Programación dirigida por eventos](10-eventos-retrollamadas-y-flujo-de-control-reactivo.md#programación-dirigida-por-eventos) | Eventos, funciones de devolución de llamada y flujo de control reactivo | `javascript`, `javascript-events`, `javascript-weird`, `LinqChallenge1` (contraejemplo), `ModernChallenge1` (contraejemplo), `PythonChallenge1` (contraejemplo), `RustChallenge1` (contraejemplo), `tar-gnu-weird`, `xaml` (contraejemplo) |
| [Programación por flujo de datos](04-evaluacion-y-demanda.md#programación-por-flujo-de-datos) | Evaluación y demanda | `javascript-weird`, `LinqChallenge1`, `LinqChallenge2`, `make-gnu` (analogía) |
| [Publicación y suscripción](10-eventos-retrollamadas-y-flujo-de-control-reactivo.md#publicación-y-suscripción) | Eventos, funciones de devolución de llamada y flujo de control reactivo | `javascript-events`, `tar-gnu-weird` (analogía), `tcl-weird` (analogía) |
| [Recursión](03-flujo-de-control-y-continuaciones.md#recursión) | Flujo de control y continuaciones | `find-gnu`, `find-posix`, `m4`, `tcl-weird` |
| [Reescritura de términos y de cadenas de texto](05-lenguajes-formales-como-sustratos-de-computacion.md#reescritura-de-términos-y-de-cadenas-de-texto) | Los lenguajes formales como sustratos de cómputo | `ed-weird`, `m4`, `regex-sed` |
| [Reflexión y metaprogramación](06-estado-mas-alla-de-las-variables.md#reflexión-y-metaprogramación) | Estado más allá de las variables | `apl-weird`, `ex-weird`, `forth-weird`, `lisp-weird`, `tcl`, `tcl-weird`, `xaml` |
| [Relojes lógicos y orden de los eventos](03-flujo-de-control-y-continuaciones.md#relojes-lógicos-y-orden-de-los-eventos) | Flujo de control y continuaciones | `make-gnu` (analogía), `tar-gnu-weird` |
| [Reproducibilidad y compilaciones deterministas](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#reproducibilidad-y-compilaciones-deterministas) | Fugas de abstracción y dependencia de la implementación | `javascript`, `javascript-events`, `javascript-weird`, `tar-gnu`, `tar-gnu-weird` |
| [Restricciones de integridad](07-efectos-errores-y-confirmacion.md#restricciones-de-integridad) | Efectos, errores y confirmación | `cobol`, `find-gnu`, `find-posix`, `javascript`, `javascript-events`, `regex-pcre2grep`, `tar-gnu`, `tar-gnu-weird` |
| [Retroceso](07-efectos-errores-y-confirmacion.md#retroceso) | Efectos, errores y confirmación | `regex-dotnet`, `regex-pcre2`, `regex-pcre2grep`, `regex-perl` |
| [Revisión de código](01-lectura-de-un-programa-adversarial.md#revisión-de-código) | Cómo leer un programa adversarial | todas las entradas |
| [Seguridad basada en teoría de lenguajes](05-lenguajes-formales-como-sustratos-de-computacion.md#seguridad-basada-en-teoría-de-lenguajes) | Los lenguajes formales como sustratos de cómputo | `tar-gnu`, `xaml` |
| [Seguridad entre hilos y afinidad de hilo](07-efectos-errores-y-confirmacion.md#seguridad-entre-hilos-y-afinidad-de-hilo) | Efectos, errores y confirmación | `GoChallenge1`, `JavaChallenge1`, `KotlinChallenge1`, `LinqChallenge1`, `LinqChallenge2`, `ModernChallenge1`, `PythonChallenge1`, `RustChallenge1` |
| [Semántica operacional](02-que-cuenta-como-maquina.md#semántica-operacional) | ¿Qué cuenta como máquina? | `ex-weird`, `javascript`, `tar-gnu-weird` |
| [Serialización, deserialización y pickling de objetos](06-estado-mas-alla-de-las-variables.md#serialización-deserialización-y-pickling-de-objetos) | Estado más allá de las variables | `apl-weird`, `m4` (analogía), `regex-sed` (analogía), `tar-gnu`, `tcl-weird`, `xaml` |
| [Sistemas de transición y máquinas de estados](02-que-cuenta-como-maquina.md#sistemas-de-transición-y-máquinas-de-estados) | ¿Qué cuenta como máquina? | `ed-weird`, `find-gnu`, `find-posix`, `javascript-events`, `tar-gnu`, `tar-gnu-weird` |
| [Teoría de categorías](05-lenguajes-formales-como-sustratos-de-computacion.md#teoría-de-categorías) | Los lenguajes formales como sustratos de cómputo | `haskell` (analogía), `javascript-weird` (analogía), `LinqChallenge1` (analogía) |
| [Transacciones](07-efectos-errores-y-confirmacion.md#transacciones) | Efectos, errores y confirmación | `forth`, `regex-perl`, `tcl` |
| [Transparencia referencial](04-evaluacion-y-demanda.md#transparencia-referencial) | Evaluación y demanda | `apl`, `haskell`, `haskell-weird`, `javascript-weird` |
| [Trojan Source: caracteres que no puedes ver](01-lectura-de-un-programa-adversarial.md#trojan-source-caracteres-que-no-puedes-ver) | Cómo leer un programa adversarial | un ejercicio |
| [Ámbito y enlace de nombres](06-estado-mas-alla-de-las-variables.md#ámbito-y-enlace-de-nombres) | Estado más allá de las variables | `apl-weird`, `javascript`, `javascript-weird`, `lisp-weird`, `m4`, `tcl`, `tcl-weird` |
