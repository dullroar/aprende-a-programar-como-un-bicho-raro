---
title: "Máquinas raras"
chapter: 5
order: 110
---
"Máquina rara" (*weird machine*) es un término de la investigación en seguridad. Un programa tiene la máquina que sus autores quisieron, y también tiene *otra* máquina, hecha con las mismas piezas, que un atacante puede manejar con una entrada de datos preparada. En la programación orientada al retorno, por ejemplo, un atacante encadena trozos pequeños de código existente para formar un programa nuevo. El término existe para explicar por qué "solo debía analizar un archivo" no es un argumento de seguridad. Cada entrada de este repositorio es una máquina rara hecha a propósito, en un lugar seguro: un motor de expresiones regulares que cuenta, un analizador sintáctico que hace bucles, una herramienta de compilación que se reinicia. Cada una plantea al revés la pregunta de la lección: *¿qué hará este programa según la entrada de datos que reciba?*

- **Úsalo cuando:** revises una superficie de ataque, y cuando quieras entender cómo calcula una función "inofensiva".
- **Evita construirlas en producción.** Si debes hacerlo, describe la máquina en el README, como hacen las entradas de aquí.

**Más información:**

- [Máquina rara](https://en.wikipedia.org/wiki/Weird_machine) (Wikipedia)
- [Programación orientada al retorno](https://en.wikipedia.org/wiki/Return-oriented_programming) (Wikipedia)
- [[langsec]]
