---
title: "Casos de estudio comparativos"
---
Para una lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre diseño comparativo de máquinas](../guias-de-estudio/conceptos/diseno-comparativo-de-maquinas.md).

El [reto compartido](../introduccion.md#what-the-challenge-does) pide tarjetas ficticias hasta incluir la primera tarjeta con la que el total pasa de 40. También pide un registro local de esas tarjetas y un resultado que el lector pueda ver. Algunas entradas imprimen en una terminal. Otras abren una ventana. Consulta [en qué se distinguen las entradas](../introduccion.md#where-entries-differ) para ver los datos fijos de LINQ, el techo de cuatro pasadas de XAML y las variantes de persistencia. Cada sección pregunta qué cumple un **papel** en particular, desde lo que se repite.

Las tablas se generan a partir de los metadatos al inicio del README de cada entrada. Puedes comprobar la clasificación en el README y en el código fuente ejecutable. La evaluación describe qué impulsa el cómputo principal. Por ejemplo, en el `for` de C#, `Sum()` consume de inmediato una proyección diferida de LINQ incluida en el bucle cada vez que se comprueba la condición. La tabla final presenta una lista de todas las entradas con su tipo, su estrategia de evaluación y el grado de garantía más débil que requieren.

{{table:roles}}

## ¿Dónde vive el programa y qué hace que se ejecute el siguiente paso?

Haz estas dos preguntas sobre cualquier entrada y las raras dejarán de parecer iguales. La primera indica dónde se guardan el programa y su estado. La segunda indica qué hace que se ejecute el siguiente paso.

| Entrada | Dónde viven el programa y su estado | Qué lo hace avanzar |
| --- | --- | --- |
| [[entry:xaml]] | Un documento declarativo que se convierte en objetos | El analizador sintáctico: crea los objetos en el orden del documento |
| [[entry:tar-gnu]] | Miembros serializados del archivo y un contrato (`tarprog/1`) que tar desconoce | El recorrido de tar por los miembros y la opción `--to-command` del operador |
| [[entry:tar-gnu-weird]] | La estructura del archivo y una fila de registros en SQLite | Los eventos de punto de control de GNU tar: un pulso por cada registro escrito |
| [[entry:ed-weird]] | El búfer del editor: líneas y filas de marcas | La edición por direcciones: un comando global y sustituciones que solo se aplican cuando hay coincidencia |
| [[entry:ex-weird]] | El búfer, las marcas y los registros del editor y una cinta de líneas numeradas | Ex mismo: un registro que se ejecuta a sí mismo, guiado por una línea de datos |
| [[entry:make-gnu]] | Los objetivos, las dependencias y el estado del reinicio | La resolución del grafo de compilación y el reinicio |
| [[entry:find-posix]] y [[entry:find-gnu]] | El árbol de directorios, su profundidad y los nombres | El recorrido del árbol |
| [[entry:haskell-weird]] | Valores perezosos que contienen efectos | La demanda: lo que se fuerza se ejecuta |
| [[entry:tcl-weird]] | Filas de SQL que contienen el código fuente almacenado | La búsqueda de un comando desconocido por parte del intérprete y los disparadores |
| [[entry:javascript]] | Propiedades de un objeto literal en un `for` sin cuerpo | La sentencia `for`: inicializador, condición e iterador |
| [[entry:javascript-weird]] | Variables capturadas por clausuras (*closure*, funciones junto con su entorno léxico) | La demanda del consumidor sobre un iterador: cada `next()` ejecuta un paso |
| [[entry:javascript-events]] | Un objeto al que solo acceden los escuchadores de eventos de un `EventEmitter` | Un evento y luego el planificador: cada escuchador de eventos emite el siguiente evento y `setImmediate` da un turno al bucle de eventos entre tarjetas |

## Cómo se escribe un programa, se vuelve a leer y se ejecuta

Cuatro acciones distintas se esconden tras las palabras "el programa es datos". La **serialización** escribe algo como bytes. La **deserialización** vuelve a leer los bytes y recupera las piezas. La **interpretación** les da un significado. La **ejecución** le da un efecto a ese significado. Un formato puede detenerse tras cualquiera de esas acciones. Un consumidor puede combinarlas. Para la seguridad importa *qué autoridad le diste a cada consumidor*. Consulta [[serialization-deserialization-pickling]].

| Entrada | Serialización | Deserialización | Interpretación y ejecución | Qué promete al escribir y volver a leer |
| --- | --- | --- | --- | --- |
| [[entry:tar-gnu]] | Un generador escribe los miembros de un archivo en un orden fijo a partir de una semilla | Tar analiza la sintaxis de los miembros. Un inspector pasivo hace lo mismo sin ejecutar nada | Un despachador da significado a cuatro tipos de registros y solo los ejecuta si el operador pasa `--to-command` | La misma semilla da los mismos bytes (comprobado con `cmp`). El inspector y la base de datos coinciden en cada tarjeta. Un archivo en dos bases de datos nuevas da las mismas tarjetas. **No** promete reanudar una ejecución detenida |
| [[entry:xaml]] | Un archivo `.xaml` es un grafo de objetos escrito como marcado | `XamlReader.Load` hace el análisis sintáctico | La misma llamada lo ejecuta: se invocan métodos a medida que se crean los objetos | Ninguna. El análisis sintáctico *es* la ejecución y la entrada nunca vuelve a escribir el documento |
| [[entry:tcl-weird]] | El código fuente Tcl se guarda en filas de SQLite | Un comando `unknown` redefinido recupera una fila | El texto recuperado se define y se evalúa como Tcl | El código fuente vuelve como el texto que se guardó. No conserva la identidad de ningún objeto |
| [[entry:apl-weird]] | `⎕CR` escribe una función como matriz de caracteres | `⎕FX` define una función a partir de dicha matriz | Cada función reescribe su código fuente, define la copia y la invoca | `⎕FX` acepta de vuelta la matriz: una propiedad de GNU APL que aprovecha la entrada |
| [[entry:regex-sed]] y [[entry:m4]] | Ninguna fuera del texto mismo: el estado *es* texto | Ninguna: no hay nada que volver a leer | Las reglas reescriben el texto hasta que ninguna se aplica | El texto es su propia representación. Escribirlo y volverlo a leer lo deja idéntico. Es una analogía y no una serialización en el sentido de los grafos de objetos |

Lee la última columna de arriba abajo. Solo una de las cinco filas promete algo sobre el *comportamiento* tras escribir y volver a leer. Además, dice qué no promete. Así quedan claros los límites: "puedo escribirlo y volver a leerlo" es una afirmación más débil que "hará lo mismo". Ambas son más débiles que "puedo pausarlo y continuar".


## Todas las entradas de un vistazo

{{table:glance}}
