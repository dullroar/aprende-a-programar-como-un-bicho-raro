---
title: "Programación dirigida por eventos"
chapter: 10
order: 10
---
En la **programación dirigida por eventos**, el programa no decide cuándo se ejecuta su código. Otro componente produce *eventos* y el programa registra *funciones de devolución de llamada* (*callbacks*), funciones que se ejecutan cuando llega un evento. El flujo de control se invierte: tú no llamas al marco de trabajo. Él te llama a ti. Así funcionan las interfaces gráficas, los servidores y los temporizadores.

[[entry:javascript-events]] es el caso más claro del repositorio: sus diez escuchadores de eventos forman todo el programa. Cada uno emite el evento que espera el siguiente. [[entry:tar-gnu-weird]] es el otro caso claro. tar escribe un archivo y llama a un comando cada 512 bytes. El comando no tiene bucle ni sabe cuántas veces lo llamarán. Avanza un paso en una máquina de estados. Cambia la disposición del archivo y el mismo programa recibe una cantidad distinta de eventos. [[entry:javascript]] y [[entry:javascript-weird]] muestran un caso real pequeño. Después de guardar todas las tarjetas, un temporizador `setInterval` llama a una función cada 600 milisegundos para actualizar la línea DEMO ONLY con cada pulso. Las llamadas solo ocurren después de que termina el código síncrono. JavaScript se ejecuta en un solo hilo y su **bucle de eventos** ejecuta una función de devolución de llamada solo cuando no hay nada más en ejecución. Una ejecución con salida redirigida no inicia ningún temporizador. Así Node no tiene ningún evento que esperar y sale de inmediato.

Una ventana no basta para que un programa se guíe por eventos. Las entradas de WPF, Tk, GLib y Swing inician un bucle de interfaz. Pero sus tarjetas provienen de una sentencia `for`, una canalización o un analizador sintáctico, así que son contraejemplos.

- **Úsala cuando:** el trabajo consista en reaccionar a lo que llega: clics, solicitudes, pulsos o archivos.
- **Evítala cuando:** el orden importe y las funciones de devolución de llamada lo oculten. Una cadena de funciones de devolución de llamada es difícil de leer y aún más difícil de probar.

**Lee más:**

- [Programación dirigida por eventos](https://en.wikipedia.org/wiki/Event-driven_programming) (Wikipedia)
- [El bucle de eventos](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop) (MDN)
- [Eventos: EventEmitter](https://nodejs.org/api/events.html) (documentación de Node.js)
