---
title: "El bucle de eventos y la planificación de turnos"
chapter: 10
order: 40
---
Un **bucle de eventos** espera a que suceda algo y ejecuta el código registrado para ese evento, una parte a la vez. Así un hilo puede hacer muchas cosas sin bloquearse: mientras una parte espera un archivo o un temporizador, otra puede ejecutarse. En cada vuelta del bucle, una función de devolución de llamada (*callback*) se ejecuta hasta el final. Eso es un **turno**. El turno siguiente solo empieza cuando la pila de llamadas está vacía.

Por eso `setImmediate()` es útil en [[entry:javascript-events]]. No llama a la función. La pone en la cola del bucle y Node la ejecuta en un turno posterior, después de que se ha desenrollado la pila y de que se ha ejecutado todo lo demás que estaba en espera. Compara con `emit()`, que hace una llamada en la pila *actual*. Esa diferencia evita que un millón de tarjetas se conviertan en un millón de llamadas anidadas. En [[entry:javascript]] y [[entry:javascript-weird]], el bucle hace que un temporizador de pulsos se ejecute *después* del trabajo síncrono. También explica por qué una ejecución con salida redirigida sale de inmediato: sin un temporizador registrado, el bucle no tiene nada que esperar.

Las bibliotecas de interfaz de usuario ejecutan el mismo tipo de bucle. Lo hacen el despachador de WPF (`Application.Run` en [[entry:ModernChallenge1]] y [[entry:LinqChallenge1]]), `mainloop` de Tk en [[entry:PythonChallenge1]] y `MainLoop` de GLib en [[entry:RustChallenge1]]. Cada uno espera eventos y llama a sus manejadores. En esas entradas el bucle solo muestra la ventana. Las tarjetas ya se habían creado cuando empezó.

- **Úsalo cuando:** muchas tareas lentas e independientes deban compartir un hilo.
- **Evítalo cuando:** una función de devolución de llamada tarde mucho en ejecutarse. En ese lapso no se ejecuta nada más en el hilo. Un turno lento retrasa a todos los demás.

**Lee más:**

- [Bucle de eventos](https://en.wikipedia.org/wiki/Event_loop) (Wikipedia)
- [El bucle de eventos](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop) (MDN)
- [El bucle de eventos de Node.js, los temporizadores y process.nextTick()](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick) (documentación de Node.js)
