# Guía de estilo

Usa esta guía para los README de las entradas, *¡Aprende a programar como un bicho raro!* y sus guías de estudio.

## Voz

- Dirígete al lector de tú. Usa "nosotros" para los mantenedores cuando importe quién hizo el trabajo.
- Prefiere verbos activos, oraciones directas y ejemplos concretos. Define los términos y los acrónimos la primera vez que los uses. Usa un solo término para cada concepto.
- Conserva los títulos juguetones de las lecciones del libro y sus bromas ocasionales. Usa formas completas como "cannot" en la prosa del cuerpo. Los títulos de humor fijos y las citas textuales pueden conservar sus contracciones.
- Usa "repo" o "repositorio" en el libro. Usa "repositorio" en las guías de estudio.

## Ortografía y puntuación

- Usa ortografía estadounidense. Escribe "forever", "rerun", "reread", "reentrancy" y "redeclare".
- Escribe "built-in" y "read-only" como adjetivos. Usa "side effect" como sustantivo y "side-effecting" como adjetivo. Usa "non-zero", "callback", "backtracking" y el sustantivo "lookup".
- Usa mayúscula solo al inicio en los encabezados. "Program Flow" es el nombre fijo de la sección de la entrada del README. No pongas numeración manual en los encabezados de lecciones y objetivos. Los ID de ejercicio, como B13, se mantienen porque los lectores y la clave de respuestas los usan.
- Omite la coma en serie en una lista simple. Úsala cuando aclare la agrupación. Usa viñetas o una tabla cuando los elementos sean largos.
- Pon un punto o una coma fuera de un fragmento citado, salvo que el signo pertenezca a la cita. Una oración completa entre comillas lleva su propio signo de puntuación.
- Escribe comillas y apóstrofos rectos en Markdown. Usa una oración nueva para dividir la prosa donde iría una raya. Conserva la puntuación en los nombres propios y en los ejemplos literales.
- Escribe los rangos en prosa con "de … a …", como en "de 10 a 19". Escribe las unidades en prosa con todas sus letras, como en "40 horas" y "jornada de 8 horas". Da formato de código a la notación literal y a la salida. En la prosa aritmética usa × para la multiplicación.
- Usa comillas invertidas para los identificadores literales y los ID de entrada. En la lista de entradas con que abre un capítulo usa rutas del repositorio como `src/forth`. Usa AWK, Make y Ex para los lenguajes y nombres de ejecutables en minúsculas como `awk`, `gawk`, `find`, `tar`, `ed`, `sed` y `busybox`.

## Redacción y evidencia de los retos

- Conserva la primera tarjeta que lleva el total a más de 40. El bucle se detiene cuando el total pasa de 40. Un total de exactamente 40 continúa. Indica cuándo una entrada concreta difiere de esa regla.
- Usa tres etiquetas en negrita en la prosa. **garantizado** se refiere a una especificación con nombre o a una API documentada. **permitido por la implementación** depende de una implementación, una plataforma o una versión concretas. **aprovechado por accidente** se apoya en un comportamiento que nadie promete. Da la evidencia y su ámbito en texto sencillo. Usa `accidentally-exploited` como valor del frontmatter.
- Empieza el texto de la entrada `teaches:` con una cláusula en minúsculas que comience con "that". Si el README tiene una línea **Teaches you:**, haz que coincida exactamente con el frontmatter.
- En una fuente de concepto, empieza la guía práctica con **Úsalo cuando:** y **Evítalo cuando:**. Usa una etiqueta más específica si aporta información.

## Guías de estudio

- Usa Inglés Técnico Simplificado para lectores avanzados. Prefiere verbos literales, una idea por oración y un máximo de 25 palabras en una oración descriptiva. Usa una lista o una tabla para una serie larga.
- Sigue la [plantilla de la guía](lessons/guias-de-estudio/README.md#cómo-funciona-cada-guía). Empieza "El reto compartido" con el párrafo estándar de especificación. Pon los detalles propios de la entrada y las excepciones en el párrafo siguiente.
- Empieza una pregunta de Evidencia con un hablante con nombre y una afirmación concreta. Usa este patrón: Un revisor dice: "El total se queda en 40". Diseña una prueba que pueda fallar.
- Guarda los comandos de compilación y las notas para colaboradores en [la guía de compilación](lessons/book/README.md#compilación-de-las-guías-de-estudio).

## Fuente y publicación

Edita prosa y metadatos del README de cada entrada en `src/`, las fuentes de conceptos en `lessons/cs-source/` y el Markdown de lecciones o guías escrito a mano. Regenera `lessons/informatica/` y los bloques generados marcados. La [guía de compilación](lessons/book/README.md) tiene los comandos para comprobar y recompilar ambos volúmenes a partir de esas fuentes.
