---
title: "Publicación y suscripción"
chapter: 10
order: 30
---
En el modelo de **publicación y suscripción**, un *productor* anuncia que ocurrió algo. El mecanismo llama a cualquier cantidad de *consumidores* que hayan registrado su interés. El productor no sabe quiénes son y los consumidores no saben quién produjo el evento. De eso se trata: cada parte puede cambiar por su cuenta. Las colas de mensajes, los eventos del navegador y `EventEmitter` de Node siguen este modelo.

La idea tiene dos partes fáciles de confundir. El registro (la tabla de escuchadores de eventos) decide *a quién se llama*. El mecanismo decide *cuándo se les llama*: un `EventEmitter` los llama de inmediato y en orden, mientras que un intermediario de mensajes puede entregarles los mensajes más tarde y en otro lugar. [[entry:javascript-events]] usa un emisor de la forma más sencilla, con un escuchador de eventos por evento. Su README admite que con exactamente un escuchador de eventos la indirección no aporta nada. Un disparador de SQLite en [[entry:tcl-weird]] es una suscripción a "se insertó una fila". La acción del punto de control en [[entry:tar-gnu-weird]] es una suscripción con un solo suscriptor.

- **Úsalo cuando:** pueda interesarle a más de una parte o el remitente no deba saber a quién le interesa.
- **Evítalo cuando:** haya un solo receptor. Una llamada a una función es más corta y un depurador puede recorrerla paso a paso.

**Lee más:**

- [Patrón de publicación y suscripción](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) (Wikipedia)
- [Eventos: EventEmitter](https://nodejs.org/api/events.html) (documentación de Node.js)
