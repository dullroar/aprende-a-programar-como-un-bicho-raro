# find

Entradas: [`src/find-posix`](../../src/find-posix/README.md) (portable) y [`src/find-gnu`](../../src/find-gnu/README.md) (todas las extensiones de GNU). `find` es una herramienta de búsqueda de archivos. Aquí se le pide que ejecute un programa y solo se le permite ser una herramienta de búsqueda de archivos: un comando, cuatro primarios, ninguna variable.

## Qué hace especial a find

Un comando `find` es una **expresión**. Se evalúa una vez por cada archivo de un árbol, de izquierda a derecha. Se detiene antes de terminar, como `&&` y `||`. Las pruebas (`-name`, `-path`) devuelven verdadero o falso. Las acciones (`-exec`, `-print`) hacen algo y también devuelven verdadero o falso. Eso es todo lo que tiene find: valores booleanos, patrones, efectos secundarios y un recorrido.

| Característica | Qué enseña |
| --- | --- |
| `-a` (y) está implícito y tiene mayor precedencia que `-o` (o) | `A -a B -o C -a D` significa "si A y B, de lo contrario si C y D". Una cadena de ramas `-o` es una sentencia `case`, con evaluación de cortocircuito gratis. |
| `-exec` devuelve el estado de salida del programa | Un comando también es una prueba. Un `mkdir` que falla hace falso el resto de la cadena `-a`. Flujo de control mediante código de error. |
| Los patrones `-path` son patrones glob donde `*` cruza `/` | `-path '*/0/*/0/*'` significa "la ruta tiene al menos dos directorios llamados `0`". La ruta es una cadena de texto y un glob es una forma de contar en ella. |
| El recorrido visita un directorio antes de leer sus entradas | Si `-exec` crea un directorio dentro del que se visita, el recorrido entra en él a continuación. Este es el bucle. POSIX no lo promete. |

## Un recorrido de árbol que cava su propio árbol

### Contempla la monstruosidad

```bash
sandbox/container/run-image.sh src/find-posix
```

Un `find` de unos 5.7 KB, sin `-delete`, sin `-printf`, sin `-regex` ni intérprete de comandos (*shell*), `awk` o `expr` en ninguna parte. El programa sortea horas, las suma, decide cuándo detenerse e imprime SQL.

### ¿Cómo demonios funciona eso?

- **El bucle es el recorrido.** Cada directorio que visita el recorrido crea el siguiente con `-exec mkdir {}/...` y el recorrido lo visita después. Para detenerse, la expresión simplemente deja de crear directorios.
- **La ruta es la pila de llamadas y los nombres son los registros.** Un nombre de un carácter es una hora. Cuenta de 1 a 9 y vuelve a 0, así que es el último dígito del total acumulado. Un nombre como `b07` es una cuenta regresiva. Un nombre de seis caracteres de `mktemp` es el dado. No se suma ni se resta nada. El *siguiente* nombre se escribe en la expresión como un literal, con una rama por valor.
- **El dígito de las decenas es un patrón glob.** Los dígitos se repiten en ciclo. Por eso, el número de directorios llamados exactamente `0` en la ruta es el dígito de las decenas del total. `-path '*/0/*/0/*'` lo lee.
- **El azar es un nombre.** `mktemp -d` crea un directorio con un nombre aleatorio. Un patrón `-name` o `-path` lee su último carácter. mktemp tiene 62 caracteres. De ellos, 60 forman diez grupos de seis, y `Y` y `Z` se vuelven a tirar.
- **La salida es texto SQL.** find imprime una sentencia `INSERT` pieza por pieza. mktemp también imprime la ruta que creó. La línea la convierte en un comentario SQL al imprimir ` -- ` primero.

El [README](../../src/find-posix/README.md#cómo-funciona-el-truco) tiene la tabla completa de tareas y [`build-line.py`](../../src/find-posix/build-line.py) muestra las tablas en forma legible.

**La versión GNU deja que find haga la aritmética.** [`find-gnu`](../../src/find-gnu/README.md) usa el mismo recorrido, pero GNU find puede medir cosas por ti. `%d` imprime la profundidad de un directorio. Un directorio es una hora, así que la profundidad *es* el total acumulado. `%TG-W%TV` imprime la semana ISO de la fecha de modificación del directorio nuevo. `-regex` sustituye las tablas de patrones glob por `([^/]*/){41}.*` ("al menos 41 barras", la regla de parada). `-fprintf /dev/fd/3` envía el SQL a su propio descriptor de archivo. La línea ocupa unos 3 KB en lugar de 5.7 KB.

**El optimizador no tiene nada que mover.** `-O3` reordena las pruebas, pero nunca a través de un efecto secundario. En este programa cada rama es una prueba seguida de un efecto. Por eso, el árbol de expresiones es idéntico en `-O0` y en `-O3`. Además, `-D rates` (el perfil del propio find) muestra por qué las estimaciones uniformes del 80 % del optimizador son incorrectas aquí.

### ¿Qué acabamos de aprender?

- **Un orden de recorrido es un contrato o es una costumbre.** Aquí es una costumbre. Funciona en GNU find, bfs y busybox, pero POSIX no dice que deba hacerlo.
- **Un patrón de ruta es un analizador sintáctico diminuto.** Con un comodín que cruza `/`, puedes contar, buscar y comprobar el último segmento.
- **Haz que los nombres lleven el estado.** En un lenguaje sin variables, el sistema de archivos es la memoria.
- **La evaluación de cortocircuito es un contador de programa.** La prueba que falló determina qué rama se ejecuta después.
- **Las propias mediciones de una herramienta pueden ser tus valores.** La profundidad y la fecha del archivo hicieron, con una directiva cada una, lo que hicieron tablas de diez filas en la versión portable.
- **La promesa de un optimizador es barata de probar.** Ejecuta en cada nivel y compara. Aquí la promesa se cumplió y nada se movió.

Etiquetas: `-fprintf`, `%d`, `%T`, `-regex` y `-D` son extensiones de GNU (**permitido por la implementación**). POSIX garantiza la precedencia de `-a`/`-o`, `-name`, `-path` y `-exec` (**garantizado**). Entrar en un directorio que `-exec` acaba de crear es **aprovechado por accidente**. `{}` dentro de un argumento más largo es **permitido por la implementación**: POSIX lo deja sin especificar y GNU find, bfs y busybox lo reemplazan. `mktemp` está fuera de POSIX, pero está en todos los sistemas BSD y Linux.

### Haz esto en producción y estás despedido

- **Una ejecución terminada deja una ruta con más de cien nombres de profundidad.** La entrada la crea en una carpeta temporal y elimina la carpeta al salir, incluso con Ctrl-C.
- **Que `*` cruce `/` es una trampa.** La primera versión hizo coincidir `*/1/b*` con un `1/b...` anterior en la misma ruta y el dígito quedó fijado. Los patrones deben terminar en un nombre de ancho fijo.
- **Es difícil razonar sobre un recorrido que cambia lo que recorre.** El resultado depende de qué entradas del directorio se leen antes y después de cada visita.
- **La línea tiene 5.7 KB.** Nadie puede revisarla a simple vista. Por eso existe [`build-line.py`](../../src/find-posix/build-line.py) y por eso `check.sh` comprueba que ambos coincidan.

Usos legítimos: `find ... -exec ... {} +` y `-prune` son herramientas de uso diario. Los manuales advierten sobre modificar el árbol mientras find lo recorre.

### Ahora rómpelo tú

Mira los [ejercicios](../exercises.md#b14-find-manipula-los-dados-verificado) y [B15](../exercises.md#b15-gnu-find-mueve-la-regla-de-parada-lee-el-perfil-verificado).

<!-- BEGIN GENERATED program-flow:languages/find.md -->
## Cómo corre cada programa

Cada imagen de abajo es la sección `## Flujo del programa` del README de una entrada, copiada aquí por la compilación. Muestra cómo ese programa hace el trabajo: lo que el lenguaje, el entorno de ejecución o la herramienta hacen en realidad. [La introducción](../introduccion.md#qué-hace-el-reto) muestra qué pide el reto y en qué se distinguen las entradas.

### Flujo del programa de `find-gnu`

Desde [`find-gnu`](../../src/find-gnu/README.md) ([sección original](../../src/find-gnu/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: find-gnu: la profundidad de un directorio es el total acumulado
    accDescr: Un diagrama de flujo. find visita un directorio. Se elige una cadena de ramas -o por nombre y por expresión regular sobre la ruta. La mayoría de las ramas cavan el siguiente directorio con mkdir o mktemp. La primera hora de una tarjeta es el propio directorio dice, y las demás horas son directorios llamados de b17 a b00 en orden descendente, así que la profundidad del directorio es el total acumulado. Al final de una tarjeta, fprintf escribe SQL en el descriptor de archivo 3, con la profundidad como total y la fecha de modificación del directorio como semana ISO. Si la ruta tiene al menos 41 barras, el total pasa de 40 y no se cava nada. Después de visitar, find lee las entradas del directorio y visita el nuevo directorio. El recorrido termina cuando no se cava nada nuevo, y sqlite3 lee el descriptor de archivo 3.
    A["find visita un directorio: las pruebas -name, -path y -regex eligen una rama"] --> B{{"¿La rama cava un directorio nuevo?"}}
    B -->|"sí: de b17 a b01, o tras una tarjeta de 40 barras o menos, el siguiente dado"| C["-exec lo cava; en b00, -fprintf escribe SQL en fd 3: depth es el total y mtime la semana"]
    C --> D["find lee las entradas de este directorio después de visitarlo y encuentra la nueva"]
    D --> A
    B -->|"no: b00 con 41 o más barras diagonales en la ruta"| E["Se escribe la última fila, no se excava nada y el recorrido termina; sqlite3 lee fd 3"]
```

**Qué muestra:** el mismo truco que [`find-posix`](../../src/find-posix/README.md), con extras de GNU que eliminan el trabajo de contabilidad. `-fprintf` puede escribir en su propio descriptor de archivo, `%d` es la profundidad del directorio y `%TG-W%TV` da formato a la hora de modificación como semana ISO. Así, la profundidad *es* el total y no hace falta aritmética dígito por dígito.

**Por qué importa este mecanismo:** la regla de parada es una expresión regular sobre la ruta: "al menos 41 barras". GNU find también tiene un optimizador que puede reordenar las pruebas. Un efecto fija el orden, así que el programa da la misma respuesta en cada nivel de optimización. Eso se comprueba con pruebas; no es una promesa.

### Flujo del programa de `find-posix`

Desde [`find-posix`](../../src/find-posix/README.md) ([sección original](../../src/find-posix/README.md#flujo-del-programa)).

```mermaid
flowchart TD
    accTitle: find-posix: `find` recorre los directorios que su propio `-exec` acaba de crear
    accDescr: Un diagrama de flujo. find visita un directorio. Una cadena de ramas -o ejecuta exactamente una rama, elegida según el nombre y la ruta del directorio. La mayoría de las ramas ejecutan un exec que crea un directorio nuevo un nivel por debajo del actual e imprimen parte de una sentencia SQL. Después de visitar un directorio, find lee sus entradas; así encuentra el directorio nuevo y lo visita a continuación. Al final de una tarjeta cuyo total no pasa de 40, la rama crea el directorio de dados de la tarjeta siguiente. Al final de una tarjeta cuyo total pasa de 40, la rama no crea ningún directorio. Entonces el recorrido termina y sqlite3 lee el texto SQL que find imprimió.
    A["find visita un directorio: su nombre y su ruta eligen una rama -o"] --> B{{"¿La rama cava un directorio nuevo?"}}
    B -->|"sí: hora, cuenta regresiva o los dados de la siguiente tarjeta"| C["-exec mkdir o mktemp -d lo crea; printf y date añaden texto SQL"]
    C --> D["find lee las entradas de este directorio después de visitarlo y encuentra la nueva"]
    D --> A
    B -->|"no: el final de una tarjeta con un total que pasa de 40"| E["El recorrido termina; sqlite3 lee el texto SQL desde la tubería"]
```

**Qué muestra:** el bucle es un recorrido de árbol que sigue creciendo. find lee las entradas de un directorio *después* de visitarlo, así que un directorio que `-exec` crea dentro del actual se recorre a continuación. La ruta desde el inicio es el historial, y el nombre del directorio es el estado. Es la pila de llamadas de una recursión, dibujada en el sistema de archivos.

**Por qué importa este mecanismo:** la regla de parada es la ausencia de un hijo nuevo: al final de una tarjeta, cinco dígitos de hora `0` en la ruta (o cuatro y un último dígito distinto de cero) significan que el total pasa de 40, y ninguna rama cava. El total acumulado es el número de directorios de hora en la ruta, y no hay aritmética en ninguna parte. Esto depende del orden en que find lee y visita, que es accidental en find y no una promesa de POSIX.
<!-- END GENERATED program-flow:languages/find.md -->

## La informática detrás de esta página

<!-- BEGIN GENERATED concepts:languages/find.md -->
Las ideas de ciencias de la computación detrás de esta página: [Sistemas de transición y máquinas de estados](../informatica/02-que-cuenta-como-maquina.md#sistemas-de-transición-y-máquinas-de-estados), [Cómo representar el estado](../informatica/02-que-cuenta-como-maquina.md#cómo-representar-el-estado), [Observabilidad](../informatica/02-que-cuenta-como-maquina.md#observabilidad), [Flujo de control](../informatica/03-flujo-de-control-y-continuaciones.md#flujo-de-control), [Recursión](../informatica/03-flujo-de-control-y-continuaciones.md#recursión), [Evaluación de cortocircuito](../informatica/04-evaluacion-y-demanda.md#evaluación-de-cortocircuito), [Expresiones regulares](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#expresiones-regulares), [Lenguajes específicos de dominio](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#lenguajes-específicos-de-dominio), [Máquinas raras](../informatica/05-lenguajes-formales-como-sustratos-de-computacion.md#máquinas-raras), [La pila de llamadas](../informatica/06-estado-mas-alla-de-las-variables.md#la-pila-de-llamadas), [Efectos secundarios](../informatica/07-efectos-errores-y-confirmacion.md#efectos-secundarios), [Restricciones de integridad](../informatica/07-efectos-errores-y-confirmacion.md#restricciones-de-integridad), [Comportamiento indefinido, no especificado y definido por la implementación](../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#comportamiento-indefinido-no-especificado-y-definido-por-la-implementación), [Portabilidad](../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#portabilidad), [Optimizadores](../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#optimizadores), [Ley de Hyrum](../informatica/08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#ley-de-hyrum).
<!-- END GENERATED concepts:languages/find.md -->
