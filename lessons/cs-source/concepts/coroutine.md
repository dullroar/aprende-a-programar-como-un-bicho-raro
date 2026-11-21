---
title: "Corrutinas"
chapter: 3
order: 60
---
Una corrutina es una función que puede pausarse a mitad de su ejecución y reanudarse después con sus variables locales intactas. Las funciones comunes se ejecutan de principio a fin. Una corrutina puede entregar un valor a quien la llamó, esperar y seguir cuando se lo pidan. Sirve para productores y consumidores, para generadores y para la multitarea cooperativa (`async`/`await` se basa en esta idea). Varias entradas son corrutinas disfrazadas. Un iterador de Rust hecho con `successors`, un `generateSequence` de Kotlin y el `iter(step, False)` de Python producen el siguiente valor solo cuando el bucle lo pide.

```mermaid
sequenceDiagram
    accTitle: Las corrutinas se suspenden y se reanudan de forma cooperativa. Conservan su estado local entre cesiones de control
    accDescr: Un diagrama de secuencia con un llamador y dos corrutinas, A y B. El llamador inicia A. A se ejecuta y cede el control a B. B se ejecuta y devuelve el control a A. A se reanuda justo después de ceder, con sus variables locales intactas. Sigue ejecutándose y vuelve a ceder el control a B. B se reanuda justo después de su propia cesión. B devuelve el control a A. A termina y retorna al llamador. Solo se ejecuta una rutina a la vez y el control cambia solo cuando una rutina lo cede.
    participant C as Llamador
    participant A as Corrutina A
    participant B as Corrutina B
    C->>A: inicia
    Note over A: se ejecuta hasta que cede el control
    A->>B: cede el control a B
    Note over B: inicia y se ejecuta hasta que cede
    B->>A: devuelve el control a A
    Note over A: se reanuda tras ceder, con sus variables intactas
    A->>B: vuelve a ceder el control a B
    Note over B: se reanuda tras ceder, sin volver al inicio
    B->>A: devuelve el control a A
    A->>C: termina y retorna al llamador
    Note over A,B: solo se ejecuta una a la vez: nada la interrumpe
```

El control cambia solo cuando una corrutina lo cede, así que solo se ejecuta una rutina a la vez. Esa es la diferencia con los hilos. Nada interrumpe a una corrutina para quitarle el control y nada se ejecuta en paralelo. Una corrutina que se reanuda sigue después de su último `yield`, con sus variables locales tal como las dejó. Una llamada común volvería a empezar desde el principio.

- **Úsala cuando:** proceses un flujo o quieras que dos partes del código se turnen sin hilos.
- **Evítala cuando:** necesites paralelismo real o los muchos puntos de pausa dificulten seguir el programa.

**Lee más:**

- [Corrutina](https://en.wikipedia.org/wiki/Coroutine) (Wikipedia)
- [[generators]] en "Evaluación y demanda"
