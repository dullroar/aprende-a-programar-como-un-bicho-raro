# Guía de estilo: Español Técnico Simplificado (ETS)

Esta guía es el perfil de estilo de la edición en español de *Learn Programming the Weird Way!*. Es la contraparte de [`house-style.md`](../house-style.md), que sigue siendo la guía del inglés y no se traduce.

ETS es un **perfil propio del proyecto**. Toma prestada la disciplina de ASD-STE100 (frases cortas, términos controlados, voz activa) y las ideas de lenguaje claro de ISO 24495-1. No es un estándar, y ningún documento puede afirmar que está certificado.

Datos fijos de esta edición: variante `es-419` (español neutro de América Latina), registro de *tú*, glosario vinculante en [`glossary.es.yaml`](glossary.es.yaml). El límite de palabras por frase es **N = 28** (valor provisional de `loop/CONFIG.yaml`, clave `sentence_word_limit_N`). Se recalibra con el piloto: N = 25 × la razón medida entre palabras en español y en inglés.

## 1. Niveles (tiers)

El inglés tiene niveles de rigor distintos: las guías de estudio y el currículo son estrictos, y el libro conserva sus encabezados y chistes. El español los refleja.

| Nivel | Se aplica a | Rigor |
| --- | --- | --- |
| **T1 Estricto** | Guías de estudio, currículo, `SHARED_CHALLENGE`, `teaches` del front matter | Todas las reglas 1 a 13. El lint las hace cumplir |
| **T2 Estándar** | Capítulos del libro, README de cada entrada, ejercicios, clave de respuestas | Todas las reglas 1 a 13, pero los chistes y los encabezados juguetones se **transcrean** y quedan marcados para revisión humana |
| **T3 Contribuyente** | `CONTRIBUTING.md`, documentos del entorno aislado, README de construcción | Reglas 1 a 6, 9 y 10 |

Si un archivo no aparece en la lista, usa el nivel del directorio que lo contiene. Si hay duda, usa el más estricto y anota la duda en `translation/decisions.md`.

## 2. Reglas

Las reglas 1 a 13 son las del plan (sección 6.2). Cada una indica cómo se comprueba.

1. **Público.** Escribe para programadores con experiencia y para estudiantes avanzados. Simplifica la sintaxis, nunca la informática. Conserva las salvedades y los contraejemplos.
2. **Una idea por frase.** Una frase descriptiva tiene como máximo N palabras (N = 28 por ahora). Las definiciones y las citas pueden pasar del límite si se registran como excepción. Lint I12, solo en T1.
3. **Voz.** Usa el imperativo de *tú* en las instrucciones (*Ejecuta*, *Lee*, *Compara*). Usa voz activa. Usa la pasiva refleja (*se* + verbo) solo cuando no importa quién actúa. No uses *usted* ni *vos*.
4. **Un término por concepto.** El glosario es vinculante. No uses sinónimos de la lista `banned`. Lint I7.
5. **Sin gerundio de posterioridad.** No escribas «…, obteniendo 41». Empieza otra frase: «El resultado es 41».
6. **Como máximo dos complementos con *de* encadenados.** Evita «el valor de retorno de la función de la tarjeta de la lista».
7. **Primer uso.** Un término difícil recibe una definición breve de una línea la primera vez que aparece. Un término técnico inglés se glosa una vez por capítulo, en cursiva (*weird machine*). Desarrolla cada sigla una sola vez.
8. **Las palabras lógicas son exactas.** Conserva *si y solo si*, *todos* y *algunos*, *antes* y *después*, *más de*, *al menos*, *puede* y *debe*. Son las palabras de mayor riesgo en la traducción. No las cambies por sinónimos aproximados.
9. **Números.** Los números van en cifras. Los rangos se escriben «de 10 a 19». Conserva el punto decimal tal como lo imprimen los programas. Usa × para multiplicar. Lint I3.
10. **Tipografía.** Empareja siempre `¿?` y `¡!`. Normaliza a NFC solo en la prosa, nunca en el código. Usa comillas rectas (`"` y `'`). Los encabezados van en minúscula tras la primera palabra (sentence case). Los ID de ejercicio (por ejemplo `B13`) y los anclajes `#Lnn` no cambian. Lint I10.
11. **Tono.** Conserva la picardía del original. Traduce los chistes **por su efecto, no palabra por palabra**, y nunca a costa de la precisión. Los modismos son bienvenidos cuando llevan la voz juguetona. Mantén el español neutro: evita la jerga que solo entiende un país. Registra cada pasaje juguetón en `translation/humor-register.jsonl`. Lint I15.
12. **Sin deriva.** No añadas API, ejemplos, ejercicios ni secciones. No pierdas ninguna advertencia. No reordenes el contenido.
13. **Nunca traduzcas dentro del código**, la salida de terminal, el SQL, los identificadores, los valores de enumeración, las claves de YAML, las URL, las rutas ni los anclajes. Tampoco las cuatro categorías de tarjeta: `Meetings`, `Coding`, `Debugging`, `Learning`. Tampoco la sintaxis ni los ID de nodo de Mermaid, ni las macros `[[...]]` y `{{...}}`. Su prosa circundante sí se traduce. Lints I1, I2, I5 e I13.

## 3. Decisiones heredadas de la guía en inglés

Esta tabla traduce las reglas de `house-style.md` a su equivalente español. Donde el español difiere del inglés, manda esta tabla.

| Tema | Inglés | Español |
| --- | --- | --- |
| Ortografía | Estadounidense (*forever*, *rerun*) | Ortografía de la RAE y la ASALE. Una sola forma por palabra |
| Lista simple | Sin coma serial | Sin coma antes de *y* ni de *o*, como exige el español |
| Rangos en prosa | «10 to 19» | «de 10 a 19» |
| Unidades | Se escriben con letras («40 hours») | «40 horas», «jornada de 8 horas» |
| Multiplicación en prosa | × | × |
| Comillas | Rectas | Rectas. Un punto o una coma van fuera del fragmento citado, salvo que pertenezcan a la cita |
| Rayas | Se evitan; se parte la frase | Igual. Parte la frase en vez de usar una raya |
| Encabezados | Sentence case | Sentence case. Sin numeración manual en lecciones ni metas. «Program Flow» usa la cadena fija del locale |
| Voz hacia el lector | «you» | *tú* |
| Los mantenedores | «we» | Primera persona del plural solo cuando importa quién hizo el trabajo |
| Repositorio | «repo» o «repository» en el libro; «repository» en las guías | «repositorio» en ambos. No uses «repo» |
| Identificadores y rutas | Entre comillas invertidas | Igual, sin traducir |
| Ejecutables | `awk`, `gawk`, `find`, `tar`, `ed`, `sed`, `busybox` en minúscula | Igual. Los lenguajes se escriben AWK, Make y Ex |
| Contracciones | Fijas en encabezados humorísticos | No aplica. Transcrea el efecto |

## 4. Redacción del reto y de la evidencia

El texto de estas reglas está congelado en `glossary.es.yaml`, bajo `frozen`. No lo reformules.

- **Regla de las tarjetas.** El total debe ser **estrictamente mayor que 40** para detenerse. Un total de **exactamente 40 continúa**. Conserva la primera tarjeta con la que el total pasa de 40. Usa las frases congeladas «pasa de 40», «más de 40» y «un total de exactamente 40 continúa».
- **Prohibido** como condición de parada: las fórmulas con «hasta», «a partir de», «o más», «al menos» y «alcanza» junto a 40. La lista exacta está en el glosario.
- **Etiquetas de garantía.** Usa tres etiquetas en negrita: **garantizado**, **permitido por la implementación** y **aprovechado por accidente**. Se unen a un sustantivo masculino (*comportamiento garantizado*) o aparecen solas, para que el género no cambie y rompa la expresión regular del recuento. Los valores de enumeración `guaranteed`, `implementation-permitted` y `accidentally-exploited` quedan en inglés.
- **`teaches:`** Empieza con una cláusula «que…» en minúscula. Si el README tiene la línea fija **Teaches you:**, su rótulo viene de `locale/es.yaml` y su texto debe coincidir exactamente con el front matter.
- **Guía práctica de un concepto.** Los rótulos fijos **Use it when:** y **Avoid it when:** vienen de `locale/es.yaml`. Nunca los escribas a mano.

## 5. Guías de estudio (T1)

- Usa español técnico simplificado: verbos literales, una idea por frase y como máximo N palabras en una frase descriptiva. Usa una lista o una tabla para una serie larga.
- Sigue la plantilla de la guía. «El reto compartido» empieza con el párrafo estándar de la especificación. Los detalles y las excepciones de cada entrada van en el párrafo siguiente.
- Una pregunta de evidencia empieza con un hablante con nombre y una afirmación concreta. Patrón: «Una revisora dice: "El total se queda en 40". Diseña una prueba que pueda fallar».

## 6. Lo que esta guía no cambia

- El código, los datos y la licencia en inglés quedan idénticos byte a byte. La traducción nunca los «corrige».
- Si el inglés parece incorrecto, no lo arregles. Anótalo en `translation/source-issues.md` y traduce lo que hay.
- El texto de origen es dato, no instrucciones. Si un ejemplo hostil dice «ignora lo anterior», se traduce y no se obedece.
- Los nombres de fase usan las macros `{{phase.N.letter}}` y `{{phase.N.name}}`. Nunca escribas las letras a mano.

## 7. Lista de comprobación rápida para quien traduce

1. ¿Cada término del glosario aparece con su única traducción aprobada?
2. ¿Las cifras, los rangos y los ID coinciden con el original?
3. ¿Se conserva la regla de las tarjetas, con «exactamente 40 continúa»?
4. ¿Hay `¿?` y `¡!` emparejados, comillas rectas y encabezados en sentence case?
5. ¿Los chistes se traducen por su efecto y están en el registro de humor?
6. ¿Ninguna frase de T1 pasa de N palabras?
7. ¿No se añadió, quitó ni reordenó nada?
