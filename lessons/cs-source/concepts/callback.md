---
title: "Funciones de devolución de llamada"
chapter: 10
order: 20
---
Una **función de devolución de llamada** (*callback*) es código que entregas a otro componente para que lo llame después. Quien llama decide cuándo y tú decides qué hacer. Existe porque una biblioteca o un motor suele saber *cuándo* pasa algo (se escribió un registro, una coincidencia llegó a un punto o venció un temporizador). Ese componente no puede saber *qué* quieres hacer al respecto. Las funciones de devolución de llamada son la puerta que te abre la herramienta.

La función de devolución de llamada se puede invocar enseguida, antes de que retorne la función que la recibió (una llamada *síncrona*). También se puede invocar después, desde el bucle de eventos (una llamada *asíncrona*). La primera es una llamada indirecta y se ejecuta en la misma pila de llamadas. La segunda necesita una cola. [[entry:regex-pcre2]] usa el primer tipo: en cada callout, el motor de coincidencias llama a una función de C y espera su respuesta. Luego decide si continúa (`0`) o da por fallida esa rama (`1`). [[entry:tar-gnu-weird]] le da a tar un comando que debe ejecutar en cada punto de control. [[entry:tcl-weird]] registra un comando de Tcl como función SQL, así que un disparador de la base de datos puede llamar al intérprete. En [[entry:javascript]] y [[entry:javascript-weird]], el pulso es una función de devolución de llamada de un temporizador. En [[entry:javascript-events]], los escuchadores de eventos son funciones de devolución de llamada que se llaman entre sí a través de un emisor.

- **Úsala cuando:** una herramienta sepa cuándo actuar y tú sepas qué hacer.
- **Evítala cuando:** las funciones de devolución de llamada se aniden demasiado ("infierno de funciones de devolución de llamada") o los errores deban volver a quien hizo la llamada. Una excepción lanzada dentro de una función de devolución de llamada llega al código que *la llamó*. Puede que ese código no la esté esperando.

**Lee más:**

- [Función de devolución de llamada (programación)](https://en.wikipedia.org/wiki/Callback_(computer_programming)) (Wikipedia)
- [Eventos: EventEmitter](https://nodejs.org/api/events.html) (documentación de Node.js)
