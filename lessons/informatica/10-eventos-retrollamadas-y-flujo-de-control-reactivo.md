<!-- GENERADO por lessons/book/build.py a partir de lessons/cs-source/ y del frontmatter de las entradas. No lo edites; edita las fuentes y ejecuta build.py. -->

# Eventos, funciones de devolución de llamada y flujo de control reactivo

Para una ruta de lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre eventos, funciones de devolución de llamada y control reactivo](../guias-de-estudio/conceptos/eventos-retrollamadas-y-control-reactivo.md). Una función de devolución de llamada (*callback*) es una función que se entrega para que otro código la llame.

Cada entrada de este libro responde una pregunta: **¿quién decide qué se ejecuta después?** En un bucle `for`, el bucle decide. En una canalización con evaluación perezosa, decide quien pide el siguiente valor. En este capítulo decide otra cosa: un *evento*, un aviso de que ocurrió algo. Un programa registra funciones pequeñas y otra parte del sistema las llama cuando ocurre algo. El programa no dice cuándo.

Eso suena a una ventana con botones, pero es una forma general de organizar el flujo de control. Este libro la muestra con ejemplos pequeños y sin trucos ocultos. [`javascript-events`](../../src/javascript-events/README.md) usa solo diez escuchadores de eventos en un emisor. Un escuchador es una función que se registra para un evento y el emisor anuncia el evento. No hay ninguna sentencia de bucle. Los demás capítulos muestran cómo un contador, una demanda o una reescritura decide qué código se ejecuta. Este muestra qué cambia cuando la que decide es una *notificación*.

## ¿Quién decide qué se ejecuta después?

Las entradas dan tres respuestas para la misma tarea (dejar de sacar tarjetas cuando el total pasa de 40):

- **El programa decide** (un bucle). `while (total <= 40) { ... }`. El programa se hace la pregunta antes de cada tarjeta. [`javascript`](../../src/javascript/README.md) y [`cobol`](../../src/cobol/README.md) funcionan así.
- **El consumidor decide** (por demanda). No ocurre nada hasta que alguien pide el siguiente valor. [`javascript-weird`](../../src/javascript-weird/README.md) y [`haskell`](../../src/haskell/README.md) funcionan así. Pedir una y otra vez es el bucle.
- **El productor decide** (por envío). Algo anuncia "esto ocurrió" y se ejecutan todas las funciones que se registraron para ese aviso. [`javascript-events`](../../src/javascript-events/README.md) funciona así. También [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md): tar anuncia "se escribió un registro más" y una máquina de estados avanza un paso.

Hay dos formas de saber que algo ocurrió: **sondeo** y **notificación**. El sondeo es un bucle que pregunta "¿ya está?" una y otra vez. La notificación requiere registrarse: "llámame cuando esté". En el sondeo, el costo es el tiempo que pasa sin que ocurra nada. En la notificación, el costo es de *estructura*: el orden del programa queda repartido entre los lugares donde se registran y se anuncian los avisos.

## Tres formas de ejecutar el mismo proceso con las tarjetas

| | Un bucle | Un emisor síncrono | Eventos programados |
|---|---|---|---|
| Ejemplo | [`javascript`](../../src/javascript/README.md) | Los mismos escuchadores de eventos, con `emit('generate')` en lugar de `later('generate')` | [`javascript-events`](../../src/javascript-events/README.md) |
| Quién inicia la siguiente tarjeta | La sentencia `for` | El último escuchador de eventos, que llama a `emit` | El último escuchador de eventos, que se lo pide al bucle de eventos |
| La pila de llamadas (que guarda las llamadas activas) entre dos tarjetas | Vacía | **Crece** unos cuantos marcos por cada tarjeta | Vacía |
| Una ejecución de un millón de tarjetas | Sin problemas | `RangeError: Maximum call stack size exceeded` | Sin problemas |
| Un escuchador de eventos que lanza una excepción | No aplica | La excepción sube a quien llamó a `emit` y pasa por todas las tarjetas anteriores | La excepción llega a la función de devolución de llamada programada, así que cada escuchador captura la suya |
| Qué más se puede ejecutar entre dos tarjetas | Nada | Nada | Cualquier tarea del bucle de eventos: temporizadores, entrada y salida (I/O) u otros escuchadores de eventos |

La columna del medio tiene trampa. *Parece* un caso de eventos, pero se comporta como una recursión. En Node, `EventEmitter.emit()` llama a todos los escuchadores del evento en el orden en que se registraron **antes de retornar**. Si un escuchador de eventos vuelve a emitir, la pila crece. El bucle de eventos no interviene en absoluto. Solo una llamada a algo como `setImmediate()` le deja el siguiente paso al bucle de eventos. Primero se vacía la pila.

## Lee una traza

Una ejecución de [`javascript-events`](../../src/javascript-events/README.md) con tres tarjetas de 19 horas. `>name` marca el inicio de un `emit` y `<name` marca su retorno:

```text
>start <start                              <- turn 1: asks for the first card, returns
>generate >card-created >card-saved >total-updated
<total-updated <card-saved <card-created <generate     <- turn 2: card 1, then the stack is empty
>generate >card-created >card-saved >total-updated
<total-updated <card-saved <card-created <generate     <- turn 3: card 2
>generate >card-created >card-saved >total-updated >finished >done
<done <finished <total-updated <card-saved <card-created <generate   <- turn 4: card 3 (57 hours)
```

El anidamiento muestra la pila de llamadas. Dentro de un turno, los eventos son *llamadas*: `card-created` se ejecuta dentro de `generate` y `generate` no puede retornar hasta que termine esa llamada. Entre turnos, la pila queda vacía y el bucle de eventos retoma el control. El diagrama:

```mermaid
sequenceDiagram
    accTitle: Un turno de eventos programados. emit anida llamadas y el bucle de eventos separa los turnos
    accDescr: Diagrama de secuencia. El bucle de eventos inicia un turno al llamar al escuchador de eventos de generate. Ese escuchador emite card-created, así que el emisor llama al escuchador de card-created dentro de la llamada en curso. Ese escuchador emite card-saved y el emisor llama al escuchador de card-saved dentro de esa llamada. Los escuchadores retornan en orden inverso y así se vacía la pila. El último escuchador le pidió al bucle de eventos el siguiente turno con setImmediate. El bucle de eventos solo inicia ese turno cuando la pila está vacía.
    participant L as Bucle de eventos
    participant G as Escuchador de eventos de generate
    participant C as Escuchador de eventos de card-created
    participant S as Escuchador de eventos de card-saved
    L->>G: Empieza un turno
    G->>C: emit card-created: llamada anidada
    C->>S: emit card-saved: otra llamada anidada
    S-->>L: setImmediate pide el siguiente turno
    S-->>C: Retorna
    C-->>G: Retorna
    G-->>L: Retorna: pila vacía
    Note over L: Solo ahora empieza el siguiente turno
```

## Qué reglas de Node importan aquí

Las fuentes son la [documentación de `events`](https://nodejs.org/api/events.html) de Node.js y su guía sobre el [bucle de eventos, los temporizadores y `process.nextTick()`](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick).

- **`emit()` es síncrono.** Los escuchadores de eventos se ejecutan en el orden en que se registraron, antes de que `emit` retorne. La documentación lo promete. No ocurre por accidente.
- **El nombre `error` es especial.** Si no hay un escuchador de eventos, `emit('error', e)` *lanza* `e`. Si no hay un escuchador para cualquier otro nombre, no pasa nada.
- **Cada `emit` usa una copia de la lista de escuchadores de eventos.** Si un escuchador quita o agrega escuchadores, cambia lo que hará el *siguiente* emit. La emisión en curso no cambia.
- **Los temporizadores, los trabajos inmediatos y las microtareas tienen un orden** que quizá no esperas. Cuando termina el código actual, Node ejecuta las funciones de devolución de llamada de `process.nextTick` y luego las de las promesas (microtareas). Después recorre el bucle de eventos: primero los temporizadores vencidos, luego las funciones de devolución de llamada de entrada y salida, después las de `setImmediate` y así sucesivamente. Si el módulo principal llama a `setTimeout(fn, 0)` y `setImmediate(fn)`, *no hay garantía* de cuál se ejecuta primero: depende de cuánto tardó en arrancar el proceso. Dentro de una función de devolución de llamada de entrada y salida, `setImmediate` siempre se ejecuta primero. Este comportamiento depende de la implementación. Es del tipo que describe [Ley de Hyrum](08-fugas-de-abstraccion-y-dependencia-de-la-implementacion.md#ley-de-hyrum). Por eso [`javascript-events`](../../src/javascript-events/README.md) usa solo `setImmediate` y nunca depende del orden entre los dos.
- **Un `try` alrededor de `emit` no captura el fallo de un escuchador de eventos `async`.** El escuchador devuelve una promesa y `emit` ya retornó. La opción `captureRejections` convierte ese rechazo en un evento `error`.
- **Alguien debe hacerse cargo de los escuchadores de eventos.** Un escuchador que nadie retira puede mantener vivo un objeto entero. Node avisa cuando un evento tiene más de diez escuchadores, porque eso suele indicar una fuga. Un temporizador o un trabajo inmediato pendiente puede impedir que el proceso termine. Al terminar, [`javascript-events`](../../src/javascript-events/README.md) retira todos los escuchadores. Su laboratorio comprueba que no quede ningún temporizador ni trabajo inmediato.

## Máquinas de estados, reentrada y finalización

Un programa de escuchadores de eventos es un [Sistemas de transición y máquinas de estados](02-que-cuenta-como-maquina.md#sistemas-de-transición-y-máquinas-de-estados): tiene un estado y los eventos provocan transiciones. [`javascript-events`](../../src/javascript-events/README.md) guarda su estado en un solo objeto al que solo acceden los escuchadores. Cada escuchador es una transición. Dos preguntas permiten saber si un programa así está bien construido.

**¿Se puede volver a llamar a un escuchador de eventos mientras aún se ejecuta?** Eso es la *reentrada*. Un `emit` síncrono lo permite: un escuchador emite un evento y el escuchador de ese evento vuelve a emitir el primero. Eso es justo lo que ocurre en la columna síncrona de arriba. La pila paga el precio. La versión programada no admite esa reentrada porque la siguiente tarjeta se procesa en otro turno.

**¿Termina?** Una cadena de eventos que nunca se detiene es un bucle que nadie ve. El programa debe tener un escuchador de eventos que *no* anuncie el siguiente paso. También debe revertir lo que no se confirmó, cerrar la base de datos, retirar los escuchadores y detener los temporizadores. En [`javascript-events`](../../src/javascript-events/README.md) esa función corresponde a `finished` (o a `failed`). Luego `done` retira todo.

Un escuchador de eventos no puede pausarse a mitad de camino y reanudarse después. Por eso una cadena de escuchadores no es una [Corrutinas](03-flujo-de-control-y-continuaciones.md#corrutinas). Cada escuchador se ejecuta hasta el final y retorna. El siguiente empieza de cero. El estado debe quedar fuera de los escuchadores. Lo mismo ocurre con un [Clausuras y entornos léxicos](06-estado-mas-alla-de-las-variables.md#clausuras-y-entornos-léxicos) que se usa como función de devolución de llamada: conserva variables, pero no conserva un *punto* para reanudar la ejecución.

## Contrapresión y cuándo conviene evitar los eventos

Una fuente de eventos anuncia lo que ocurre a su propio ritmo. Los eventos no tienen cómo decir "más despacio". Si el productor va más rápido que el consumidor, la cola crece sin límite o se pierden eventos. La **contrapresión** permite que el consumidor frene al productor. La demanda es la forma más simple: el consumidor pide un valor cuando está listo. [`javascript-weird`](../../src/javascript-weird/README.md) no se puede saturar, porque no extrae nada hasta que alguien llama a `next()`. [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) muestra lo contrario. tar sigue escribiendo registros y llamando al reloj después de que la máquina termina. Esos tics solo cuentan como inactividad.

```mermaid
flowchart TB
    accTitle: Avisar no regula el flujo. La contrapresión se diseña
    accDescr: Dos paneles. En el envío sin regulación, un productor rápido manda eventos a una cola con 1, 2, 3, 4 y así sucesivamente. La cola sigue creciendo mientras un consumidor lento lee de ella. Por eso la cola crece o se pierden eventos. En el flujo por demanda, el consumidor pide un elemento cuando está listo. El productor emite uno. El consumidor lo procesa y pide el siguiente, así que marca el ritmo.
    subgraph PULL["Demanda del consumidor"]
        RDY["Consumidor: ¿listo?"] --> REQ["Pide un elemento"] --> EMIT["El productor emite uno"] --> PROC["El consumidor lo procesa"] --> NXT["Pide el siguiente"]
    end
    subgraph PUSH["Envío sin regulación"]
        FP["Productor rápido"] -->|"eventos"| Q["Cola: 1, 2, 3, 4, ... Crece o pierde eventos"] --> SC["Consumidor lento"]
    end
```

Decirle al consumidor "ocurrió algo" no le dice al productor que baje el ritmo. A la izquierda, nada limita el ritmo. A la derecha, lo limita la solicitud del consumidor. Una cola acotada o un flujo que se pueda pausar y reanudar también pueden ejercer contrapresión. El `EventEmitter` básico de Node carece de contrapresión. Un `emit()` síncrono es una llamada, no una cola. La traza de arriba muestra el orden de las llamadas. Este diagrama muestra sus *ritmos*.

[`javascript-events`](../../src/javascript-events/README.md) evita la avalancha por una razón sencilla: cada tarjeta espera a la anterior, así que el productor y el consumidor son el mismo programa. Una fuente real de eventos, como un socket de red, necesita una cola acotada o un flujo.

Los eventos tampoco convienen cuando:

- hay exactamente un escuchador de eventos y siempre es el mismo. Una llamada a una función dice lo mismo y es más corta. Un depurador permite recorrerla paso a paso;
- el orden debe ser evidente. Con eventos, el orden está en los nombres y en la secuencia de registro;
- necesitas que te devuelvan un resultado. Un evento anuncia algo y no responde.

## Eventos en este repositorio y casos que solo se les parecen

No toda función de devolución de llamada es un evento ni toda ventana se rige por eventos. La tabla muestra qué tiene realmente cada entrada.

| Entrada | Qué tiene | ¿El programa se rige por eventos? |
|---|---|---|
| [`javascript-events`](../../src/javascript-events/README.md) | Diez escuchadores de eventos en un emisor, `setImmediate` entre tarjetas y un temporizador para el pulso | **Sí.** Los escuchadores de eventos son el programa |
| [`javascript`](../../src/javascript/README.md) | Una sentencia `for` y luego una función de devolución de llamada de `setInterval` para el pulso | Solo el pulso. Un bucle procesa las tarjetas |
| [`javascript-weird`](../../src/javascript-weird/README.md) | Una canalización por demanda y luego el mismo temporizador | Solo el pulso. Las tarjetas se obtienen bajo demanda |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | tar ejecuta un comando en cada punto de control | **Sí.** Una función de devolución de llamada externa hace que una máquina de estados avance un paso. No hay bucle en el programa |
| [`regex-pcre2`](../../src/regex-pcre2/README.md) | El motor llama a una función en cada callout | Una **función de devolución de llamada** síncrona. El motor la llama directamente, sin poner un evento en una cola |
| [`tcl-weird`](../../src/tcl-weird/README.md) | Un disparador llama a una función de SQL que a su vez llama a Tcl | Una **cadena de funciones de devolución de llamada** en una sola pila de llamadas. La base de datos despacha las llamadas y nada espera en una cola |
| [`ModernChallenge1`](../../src/ModernChallenge1/README.md), [`LinqChallenge1`](../../src/LinqChallenge1/README.md), [`xaml`](../../src/xaml/README.md) | Una ventana de WPF con su bucle de mensajes (`Application.Run`) y una animación iniciada por un disparador `Loaded` | **No.** La infraestructura de la interfaz de usuario tiene un bucle de eventos. El programa declara una animación, sin suscribirse a ella. Las tarjetas salen de una sentencia `for`, una canalización de LINQ y un analizador sintáctico |
| [`PythonChallenge1`](../../src/PythonChallenge1/README.md), [`RustChallenge1`](../../src/RustChallenge1/README.md) | Un `mainloop` de Tk y un `MainLoop` de GLib, con un temporizador que cambia un color | **No.** Igual que antes: la ventana ejecuta su propio bucle y las tarjetas se crean antes de abrirla |
| [`JavaChallenge1`](../../src/JavaChallenge1/README.md), [`KotlinChallenge1`](../../src/KotlinChallenge1/README.md), [`GoChallenge1`](../../src/GoChallenge1/README.md) | Un cuadro de diálogo modal de Swing con un temporizador que atenúa los colores (Java, Kotlin) y una página que se sirve al navegador (Go) | **No.** La ventana se abre al final y las tarjetas salen de una sentencia `for` o de una secuencia |

Una infraestructura de animación, el enlace de datos y el propio bucle de una ventana son *mecanismos* que usan eventos. Eso no hace que el programa que los inicia se rija por eventos. La prueba es sencilla: **¿la lógica de las tarjetas se ejecuta porque llegó un evento?** Si la respuesta es "no, la ejecuta un bucle o una canalización y luego se abre una ventana", la entrada es un bucle con ventana.

## Predice y luego ejecuta

El [ejercicio B22](../exercises.md#b22-javascript-dirigido-por-eventos-predice-la-traza-y-luego-elimina-el-límite-verificado) te pide que escribas la traza de una ejecución *antes* de verla y que predigas qué imprimen `emit` y `setImmediate`. También te pide que quites la separación entre turnos y veas cómo un millón de tarjetas agotan la pila. Haz primero la predicción en papel. La gracia está en la sorpresa.

## Programación dirigida por eventos

En la **programación dirigida por eventos**, el programa no decide cuándo se ejecuta su código. Otro componente produce *eventos* y el programa registra *funciones de devolución de llamada* (*callbacks*), funciones que se ejecutan cuando llega un evento. El flujo de control se invierte: tú no llamas al marco de trabajo. Él te llama a ti. Así funcionan las interfaces gráficas, los servidores y los temporizadores.

[`javascript-events`](../../src/javascript-events/README.md) es el caso más claro del repositorio: sus diez escuchadores de eventos forman todo el programa. Cada uno emite el evento que espera el siguiente. [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) es el otro caso claro. tar escribe un archivo y llama a un comando cada 512 bytes. El comando no tiene bucle ni sabe cuántas veces lo llamarán. Avanza un paso en una máquina de estados. Cambia la disposición del archivo y el mismo programa recibe una cantidad distinta de eventos. [`javascript`](../../src/javascript/README.md) y [`javascript-weird`](../../src/javascript-weird/README.md) muestran un caso real pequeño. Después de guardar todas las tarjetas, un temporizador `setInterval` llama a una función cada 600 milisegundos para actualizar la línea DEMO ONLY con cada pulso. Las llamadas solo ocurren después de que termina el código síncrono. JavaScript se ejecuta en un solo hilo y su **bucle de eventos** ejecuta una función de devolución de llamada solo cuando no hay nada más en ejecución. Una ejecución con salida redirigida no inicia ningún temporizador. Así Node no tiene ningún evento que esperar y sale de inmediato.

Una ventana no basta para que un programa se guíe por eventos. Las entradas de WPF, Tk, GLib y Swing inician un bucle de interfaz. Pero sus tarjetas provienen de una sentencia `for`, una canalización o un analizador sintáctico, así que son contraejemplos.

- **Úsala cuando:** el trabajo consista en reaccionar a lo que llega: clics, solicitudes, pulsos o archivos.
- **Evítala cuando:** el orden importe y las funciones de devolución de llamada lo oculten. Una cadena de funciones de devolución de llamada es difícil de leer y aún más difícil de probar.

**Lee más:**

- [Programación dirigida por eventos](https://en.wikipedia.org/wiki/Event-driven_programming) (Wikipedia)
- [El bucle de eventos](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop) (MDN)
- [Eventos: EventEmitter](https://nodejs.org/api/events.html) (documentación de Node.js)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`javascript`](../../src/javascript/README.md) | JavaScript, SQLite | demuestra | Que una sentencia for consta de tres expresiones y un cuerpo vacío, y que el orden de evaluación propio de JavaScript, la veracidad de los valores y el operador coma bastan para ejecutar un programa completo a partir de las tres cláusulas. |
| [`javascript-events`](../../src/javascript-events/README.md) | JavaScript, SQLite | demuestra | Que un programa puede ser un conjunto de escuchadores de eventos, cada uno con una sola tarea pequeña que termina emitiendo el evento que espera el siguiente; y que emit() llama a sus escuchadores de inmediato, así que solo un límite de planificación explícito da un turno al bucle de eventos. |
| [`javascript-weird`](../../src/javascript-weird/README.md) | JavaScript, SQLite | demuestra | Que una clausura es una máquina de estados: una función más las variables junto a las que se creó, que un iterador hace avanzar un paso a la vez, con reduce como el único pliegue que no puede detenerse. |
| [`LinqChallenge1`](../../src/LinqChallenge1/README.md) | C#, LINQ | contraejemplo | Que una cadena de métodos de LINQ puede expresar el programa completo. |
| [`ModernChallenge1`](../../src/ModernChallenge1/README.md) | C# | contraejemplo | Que una sentencia `for` con el cuerpo vacío puede controlar XAML en tiempo de ejecución, LINQ to Objects, EF Core y la animación de WPF. |
| [`PythonChallenge1`](../../src/PythonChallenge1/README.md) | Python | contraejemplo | Que Python puede controlar un programa completo con `iter(step, False)`, que llama a `step` hasta que devuelve `False`. |
| [`RustChallenge1`](../../src/RustChallenge1/README.md) | Rust | contraejemplo | Que los iteradores y las clausuras (*closures*, funciones que capturan variables de su entorno) pueden expresar el flujo de control de un programa completo en Rust. |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | demuestra | Que la disposición física de un archivo puede marcar el ritmo de un programa: los puntos de control de tar son un reloj y cada pulso hace avanzar un paso a una máquina de estados. |
| [`xaml`](../../src/xaml/README.md) | XAML, C# | contraejemplo | Que un analizador sintáctico de marcado puede ejecutar un programa mientras describe una interfaz de usuario. |

## Funciones de devolución de llamada

Una **función de devolución de llamada** (*callback*) es código que entregas a otro componente para que lo llame después. Quien llama decide cuándo y tú decides qué hacer. Existe porque una biblioteca o un motor suele saber *cuándo* pasa algo (se escribió un registro, una coincidencia llegó a un punto o venció un temporizador). Ese componente no puede saber *qué* quieres hacer al respecto. Las funciones de devolución de llamada son la puerta que te abre la herramienta.

La función de devolución de llamada se puede invocar enseguida, antes de que retorne la función que la recibió (una llamada *síncrona*). También se puede invocar después, desde el bucle de eventos (una llamada *asíncrona*). La primera es una llamada indirecta y se ejecuta en la misma pila de llamadas. La segunda necesita una cola. [`regex-pcre2`](../../src/regex-pcre2/README.md) usa el primer tipo: en cada callout, el motor de coincidencias llama a una función de C y espera su respuesta. Luego decide si continúa (`0`) o da por fallida esa rama (`1`). [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) le da a tar un comando que debe ejecutar en cada punto de control. [`tcl-weird`](../../src/tcl-weird/README.md) registra un comando de Tcl como función SQL, así que un disparador de la base de datos puede llamar al intérprete. En [`javascript`](../../src/javascript/README.md) y [`javascript-weird`](../../src/javascript-weird/README.md), el pulso es una función de devolución de llamada de un temporizador. En [`javascript-events`](../../src/javascript-events/README.md), los escuchadores de eventos son funciones de devolución de llamada que se llaman entre sí a través de un emisor.

- **Úsala cuando:** una herramienta sepa cuándo actuar y tú sepas qué hacer.
- **Evítala cuando:** las funciones de devolución de llamada se aniden demasiado ("infierno de funciones de devolución de llamada") o los errores deban volver a quien hizo la llamada. Una excepción lanzada dentro de una función de devolución de llamada llega al código que *la llamó*. Puede que ese código no la esté esperando.

**Lee más:**

- [Función de devolución de llamada (programación)](https://en.wikipedia.org/wiki/Callback_(computer_programming)) (Wikipedia)
- [Eventos: EventEmitter](https://nodejs.org/api/events.html) (documentación de Node.js)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`javascript`](../../src/javascript/README.md) | JavaScript, SQLite | demuestra | Que una sentencia for consta de tres expresiones y un cuerpo vacío, y que el orden de evaluación propio de JavaScript, la veracidad de los valores y el operador coma bastan para ejecutar un programa completo a partir de las tres cláusulas. |
| [`javascript-events`](../../src/javascript-events/README.md) | JavaScript, SQLite | demuestra | Que un programa puede ser un conjunto de escuchadores de eventos, cada uno con una sola tarea pequeña que termina emitiendo el evento que espera el siguiente; y que emit() llama a sus escuchadores de inmediato, así que solo un límite de planificación explícito da un turno al bucle de eventos. |
| [`javascript-weird`](../../src/javascript-weird/README.md) | JavaScript, SQLite | demuestra | Que una clausura es una máquina de estados: una función más las variables junto a las que se creó, que un iterador hace avanzar un paso a la vez, con reduce como el único pliegue que no puede detenerse. |
| [`regex-pcre2`](../../src/regex-pcre2/README.md) | C, PCRE2, Regular expressions | demuestra | Que los callouts de regex pueden servir como un conjunto diminuto de instrucciones. |
| [`regex-pcre2grep`](../../src/regex-pcre2grep/README.md) | PCRE2, Regular expressions | analogía | Que los códigos de salida de un programa pueden dirigir el flujo de control. |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | demuestra | Que la disposición física de un archivo puede marcar el ritmo de un programa: los puntos de control de tar son un reloj y cada pulso hace avanzar un paso a una máquina de estados. |
| [`tcl-weird`](../../src/tcl-weird/README.md) | Tcl, SQLite | demuestra | Que el código Tcl se compone solo de cadenas de texto. Por eso puede residir en una base de datos, recuperarse, definirse y ejecutarse bajo demanda. Los disparadores de SQLite determinan el flujo de control. |

## Publicación y suscripción

En el modelo de **publicación y suscripción**, un *productor* anuncia que ocurrió algo. El mecanismo llama a cualquier cantidad de *consumidores* que hayan registrado su interés. El productor no sabe quiénes son y los consumidores no saben quién produjo el evento. De eso se trata: cada parte puede cambiar por su cuenta. Las colas de mensajes, los eventos del navegador y `EventEmitter` de Node siguen este modelo.

La idea tiene dos partes fáciles de confundir. El registro (la tabla de escuchadores de eventos) decide *a quién se llama*. El mecanismo decide *cuándo se les llama*: un `EventEmitter` los llama de inmediato y en orden, mientras que un intermediario de mensajes puede entregarles los mensajes más tarde y en otro lugar. [`javascript-events`](../../src/javascript-events/README.md) usa un emisor de la forma más sencilla, con un escuchador de eventos por evento. Su README admite que con exactamente un escuchador de eventos la indirección no aporta nada. Un disparador de SQLite en [`tcl-weird`](../../src/tcl-weird/README.md) es una suscripción a "se insertó una fila". La acción del punto de control en [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) es una suscripción con un solo suscriptor.

- **Úsalo cuando:** pueda interesarle a más de una parte o el remitente no deba saber a quién le interesa.
- **Evítalo cuando:** haya un solo receptor. Una llamada a una función es más corta y un depurador puede recorrerla paso a paso.

**Lee más:**

- [Patrón de publicación y suscripción](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) (Wikipedia)
- [Eventos: EventEmitter](https://nodejs.org/api/events.html) (documentación de Node.js)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`javascript-events`](../../src/javascript-events/README.md) | JavaScript, SQLite | demuestra | Que un programa puede ser un conjunto de escuchadores de eventos, cada uno con una sola tarea pequeña que termina emitiendo el evento que espera el siguiente; y que emit() llama a sus escuchadores de inmediato, así que solo un límite de planificación explícito da un turno al bucle de eventos. |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | analogía | Que la disposición física de un archivo puede marcar el ritmo de un programa: los puntos de control de tar son un reloj y cada pulso hace avanzar un paso a una máquina de estados. |
| [`tcl-weird`](../../src/tcl-weird/README.md) | Tcl, SQLite | analogía | Que el código Tcl se compone solo de cadenas de texto. Por eso puede residir en una base de datos, recuperarse, definirse y ejecutarse bajo demanda. Los disparadores de SQLite determinan el flujo de control. |

## El bucle de eventos y la planificación de turnos

Un **bucle de eventos** espera a que suceda algo y ejecuta el código registrado para ese evento, una parte a la vez. Así un hilo puede hacer muchas cosas sin bloquearse: mientras una parte espera un archivo o un temporizador, otra puede ejecutarse. En cada vuelta del bucle, una función de devolución de llamada (*callback*) se ejecuta hasta el final. Eso es un **turno**. El turno siguiente solo empieza cuando la pila de llamadas está vacía.

Por eso `setImmediate()` es útil en [`javascript-events`](../../src/javascript-events/README.md). No llama a la función. La pone en la cola del bucle y Node la ejecuta en un turno posterior, después de que se ha desenrollado la pila y de que se ha ejecutado todo lo demás que estaba en espera. Compara con `emit()`, que hace una llamada en la pila *actual*. Esa diferencia evita que un millón de tarjetas se conviertan en un millón de llamadas anidadas. En [`javascript`](../../src/javascript/README.md) y [`javascript-weird`](../../src/javascript-weird/README.md), el bucle hace que un temporizador de pulsos se ejecute *después* del trabajo síncrono. También explica por qué una ejecución con salida redirigida sale de inmediato: sin un temporizador registrado, el bucle no tiene nada que esperar.

Las bibliotecas de interfaz de usuario ejecutan el mismo tipo de bucle. Lo hacen el despachador de WPF (`Application.Run` en [`ModernChallenge1`](../../src/ModernChallenge1/README.md) y [`LinqChallenge1`](../../src/LinqChallenge1/README.md)), `mainloop` de Tk en [`PythonChallenge1`](../../src/PythonChallenge1/README.md) y `MainLoop` de GLib en [`RustChallenge1`](../../src/RustChallenge1/README.md). Cada uno espera eventos y llama a sus manejadores. En esas entradas el bucle solo muestra la ventana. Las tarjetas ya se habían creado cuando empezó.

- **Úsalo cuando:** muchas tareas lentas e independientes deban compartir un hilo.
- **Evítalo cuando:** una función de devolución de llamada tarde mucho en ejecutarse. En ese lapso no se ejecuta nada más en el hilo. Un turno lento retrasa a todos los demás.

**Lee más:**

- [Bucle de eventos](https://en.wikipedia.org/wiki/Event_loop) (Wikipedia)
- [El bucle de eventos](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop) (MDN)
- [El bucle de eventos de Node.js, los temporizadores y process.nextTick()](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick) (documentación de Node.js)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`javascript`](../../src/javascript/README.md) | JavaScript, SQLite | demuestra | Que una sentencia for consta de tres expresiones y un cuerpo vacío, y que el orden de evaluación propio de JavaScript, la veracidad de los valores y el operador coma bastan para ejecutar un programa completo a partir de las tres cláusulas. |
| [`javascript-events`](../../src/javascript-events/README.md) | JavaScript, SQLite | demuestra | Que un programa puede ser un conjunto de escuchadores de eventos, cada uno con una sola tarea pequeña que termina emitiendo el evento que espera el siguiente; y que emit() llama a sus escuchadores de inmediato, así que solo un límite de planificación explícito da un turno al bucle de eventos. |
| [`javascript-weird`](../../src/javascript-weird/README.md) | JavaScript, SQLite | demuestra | Que una clausura es una máquina de estados: una función más las variables junto a las que se creó, que un iterador hace avanzar un paso a la vez, con reduce como el único pliegue que no puede detenerse. |
| [`LinqChallenge1`](../../src/LinqChallenge1/README.md) | C#, LINQ | demuestra | Que una cadena de métodos de LINQ puede expresar el programa completo. |
| [`ModernChallenge1`](../../src/ModernChallenge1/README.md) | C# | demuestra | Que una sentencia `for` con el cuerpo vacío puede controlar XAML en tiempo de ejecución, LINQ to Objects, EF Core y la animación de WPF. |
| [`PythonChallenge1`](../../src/PythonChallenge1/README.md) | Python | demuestra | Que Python puede controlar un programa completo con `iter(step, False)`, que llama a `step` hasta que devuelve `False`. |
| [`RustChallenge1`](../../src/RustChallenge1/README.md) | Rust | demuestra | Que los iteradores y las clausuras (*closures*, funciones que capturan variables de su entorno) pueden expresar el flujo de control de un programa completo en Rust. |

## Contrapresión

La **contrapresión** es la forma en que un consumidor lento le pide a un productor rápido que espere. Una fuente de eventos emite avisos a su propio ritmo. Si el consumidor no puede seguirle el ritmo, la cola crece sin límite hasta agotar la memoria o se descartan eventos. La contrapresión convierte eso en una conversación. Puede usar un búfer acotado, un flujo que pausa su fuente o un mecanismo de *demanda* (*pull*), en el que el consumidor pide un valor cuando está listo.

La demanda es la forma más sencilla de contrapresión y [`javascript-weird`](../../src/javascript-weird/README.md) la usa. No se puede saturar porque no extrae nada hasta que alguien lo pide. [`javascript-events`](../../src/javascript-events/README.md) no tiene contrapresión ni la necesita. Cada tarjeta espera a la anterior, así que el productor y el consumidor son un solo programa. [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) muestra qué pasa sin esa señal. tar sigue escribiendo registros y, por tanto, sigue consultando el reloj después de que la máquina termina. Esos pulsos solo cuentan como inactividad, porque no hay forma de pedirle a tar que se detenga.

- **Úsala cuando:** no controles la velocidad del productor.
- **Evítala cuando:** el productor y el consumidor sean un solo programa secuencial. Basta un bucle sencillo.

**Lee más:**

- [Contrapresión](https://en.wikipedia.org/wiki/Back_pressure) (Wikipedia)

**En este repositorio:**

| Entrada | Lenguaje | Cómo se relaciona | Qué enseña |
| --- | --- | --- | --- |
| [`javascript-events`](../../src/javascript-events/README.md) | JavaScript, SQLite | contraejemplo | Que un programa puede ser un conjunto de escuchadores de eventos, cada uno con una sola tarea pequeña que termina emitiendo el evento que espera el siguiente; y que emit() llama a sus escuchadores de inmediato, así que solo un límite de planificación explícito da un turno al bucle de eventos. |
| [`javascript-weird`](../../src/javascript-weird/README.md) | JavaScript, SQLite | analogía | Que una clausura es una máquina de estados: una función más las variables junto a las que se creó, que un iterador hace avanzar un paso a la vez, con reduce como el único pliegue que no puede detenerse. |
| [`tar-gnu-weird`](../../src/tar-gnu-weird/README.md) | GNU tar, SQLite | analogía | Que la disposición física de un archivo puede marcar el ritmo de un programa: los puntos de control de tar son un reloj y cada pulso hace avanzar un paso a una máquina de estados. |
