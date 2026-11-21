---
title: "Disparadores de base de datos"
chapter: 6
order: 80
---
Un disparador es código que la base de datos ejecuta por sí sola al insertar, actualizar o borrar una fila. Sirve para mantener las reglas cerca de los datos: registros de auditoría, columnas derivadas y comprobaciones que una restricción `CHECK` no puede expresar. En [[entry:tcl-weird]] un disparador hace de bucle. Cada inserción activa el disparador, que inserta la siguiente fila hasta que una cláusula `WHERE` no encuentra nada que insertar. El costo es un flujo de control invisible. Nada en el código de la aplicación dice "esto también ocurre". El orden y la profundidad de los disparadores pueden sorprenderte.

```mermaid
flowchart TB
    accTitle: Un disparador es código que la base de datos ejecuta en respuesta a un evento de tabla. Los datos que cambian dan lugar al siguiente paso
    accDescr: Diagrama de flujo de un disparador recursivo. El código anfitrión ejecuta un solo INSERT y no contiene ningún bucle. La inserción es un evento de tabla que activa el disparador. El disparador comprueba su condición. Si la condición selecciona una fila, el disparador inserta la siguiente fila. Ese nuevo evento de tabla vuelve a activar el disparador. Si la condición no selecciona nada, la cadena termina.
    H["Código anfitrión: un INSERT, sin bucle"] --> E["Evento de tabla: se inserta una fila"]
    E --> T{{"Disparador: ¿la condición selecciona una fila?"}}
    T -->|"sí: el disparador inserta la siguiente fila"| E
    T -->|"no: nada que insertar"| X(["Fin de la cadena"])
```

El código anfitrión ejecuta un solo `INSERT` y no tiene bucle. El disparador pertenece a la tabla, así que cada inserción es un evento que lo activa. El `INSERT` del disparador también es un evento. Así un cambio causa el siguiente. Una cadena así solo termina porque al final la condición no selecciona ninguna fila. Las bases de datos toman precauciones. SQLite solo permite que un disparador se active a sí mismo si `PRAGMA recursive_triggers` está habilitado. [[entry:tcl-weird]] lo habilita a propósito.

- **Úsalo cuando:** necesites registros de auditoría o reglas que deban cumplirse sin importar quién escriba los datos.
- **Evítalo cuando:** quieras meter procesos de negocio en disparadores o usarlos como bucle del programa (como hace esta entrada a propósito).

**Lee más:**

- [Disparador de base de datos](https://en.wikipedia.org/wiki/Database_trigger) (Wikipedia)
- [SQLite](https://en.wikipedia.org/wiki/SQLite) (Wikipedia)
