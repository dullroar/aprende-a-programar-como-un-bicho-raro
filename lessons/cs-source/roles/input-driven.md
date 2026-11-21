---
title: "La entrada de datos es el bucle"
order: 80
---
La entrada de datos es el bucle. AWK lee un registro a la vez y ejecuta cada regla de patrón y acción sobre él, así que el programa no contiene ningún bucle. [[entry:awk]] usa el bucle de la forma habitual. [[entry:awk-weird]] fija una expresión regular como separador de registros, así que un flujo de bytes aleatorios se convierte en dados, y un solo patrón (`t > 40 { exit }`) es la regla de parada.
