---
title: "Una secuencia perezosa que alguien sigue pidiendo"
order: 20
---
No hay bucle. Hay una secuencia que alguien sigue pidiendo, y el programa se detiene cuando se deja de pedir. [[entry:haskell]] describe las tarjetas como una lista perezosa infinita y toma un prefijo con `span`. [[entry:haskell-weird]] pone los efectos dentro de la lista, así que leerla hace el trabajo. LINQ construye una canalización diferida que un operador final voraz fuerza. `generateSequence` de Kotlin, `successors` de Rust y `iter(step, False)` de Python dan una forma parecida en otros lenguajes. La diferencia entre las entradas es *quién fuerza la secuencia* y *cuándo*. [[entry:javascript-weird]] no tiene sentencia de bucle: tres clausuras (*closures*) fabrican tarjetas, y una canalización de iteradores demanda una tarjeta a la vez hasta que la máquina dice que terminó.
