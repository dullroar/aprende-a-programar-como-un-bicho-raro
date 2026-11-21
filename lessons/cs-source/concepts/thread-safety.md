---
title: "Seguridad entre hilos y afinidad de hilo"
chapter: 7
order: 100
---
Un código es seguro entre hilos (*thread-safe*) si se comporta bien cuando varios hilos lo usan al mismo tiempo. Es un problema porque datos compartidos y modificables más hilos en paralelo producen una carrera: el resultado depende de quién llega primero. Las entradas de .NET y de sus adaptaciones tocan dos versiones del problema. En las entradas de C#, un `DbContext` de EF Core no es seguro entre hilos. En las adaptaciones de una sola sentencia, el código usa un bloqueo alrededor de las tarjetas preparadas mientras un hilo en segundo plano las guarda. Y WPF tiene *afinidad de hilo*: una ventana solo la puede tocar el hilo que la creó. Que un código funcione una vez no prueba que sea seguro.

- **Úsalo cuando:** compartas datos entre hilos: usa bloqueos, datos inmutables o un contexto por hilo.
- **Evítalo cuando:** los hilos compartirían un objeto modificable sin sincronización. Una prueba que pasa no basta para demostrar la seguridad.

**Más información:**

- [Seguridad entre hilos](https://en.wikipedia.org/wiki/Thread_safety) (Wikipedia)
- [Condición de carrera](https://en.wikipedia.org/wiki/Race_condition) (Wikipedia)
