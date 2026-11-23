# Edition facts

Read this before the packets. These are the fixed facts of the Spanish edition; judge the text by them.

- **Edition:** v4-es.0-rc1
- **Title:** ¡Aprende a programar como un bicho raro!
- **Language tag:** es-419; register: tú with imperatives
- **Acronym:** BICHO = Bicho raro, Interpreta, Camino indirecto, Hallazgos y Octetos
- **Sentence limit N:** 29 words for descriptive sentences

## The five phases (original order and roles; only letters and names changed)

| Phase | Letter | Name | Weeks |
|---|---|---|---|
| 1 | B | Bicho raro | 1 a 2 |
| 2 | I | Interpreta | 3 a 6 |
| 3 | C | Camino indirecto | 7 a 10 |
| 4 | H | Hallazgos | 11 a 13 |
| 5 | O | Octetos | 14 a 15 |

## The timecard rule (frozen wording)

Las categorías se repiten en ciclo: `Meetings`, `Coding`, `Debugging`, `Learning`. Cada tarjeta tiene de 10 a 19 horas enteras. Agrega tarjetas y detente cuando el total pasa de 40. Un total de exactamente 40 continúa. Conserva la primera tarjeta con la que el total pasa de 40. Las ejecuciones conformes tienen de 3 a 5 tarjetas y un total de 41 a 59.

A total of **exactly 40 continues**; only a total **strictly greater than 40** stops. Wordings that stop at 40 are critical defects. Banned as a stop condition:

- hasta 40
- a partir de 40
- 40 o más
- al menos 40
- alcanza 40
- llega a 40
- llegue a 40
- llegar a 40
- alcance 40
- alcanzar 40
- menor que 40

## Assurance labels (three different guarantees; never interchangeable)

- *garantizado* = guaranteed
- *permitido por la implementación* = implementation-permitted
- *aprovechado por accidente* = accidentally exploited

## Left in English on purpose (not defects)

- All code, terminal output, SQL, identifiers, paths, URLs, `#Lnn` anchors, YAML keys and enum values.
- The four card categories, always as code, in one form per file: the English words `Meetings`, `Coding`, `Debugging`, `Learning` where the code still prints them, or the glossary words `Reuniones`, `Programación`, `Depuración`, `Aprendizaje` where the code was localized (decision 11). A mix or any other spelling is a defect.
- Mermaid syntax and node IDs; only the labels and `accTitle` / `accDescr` are Spanish.
- The English MIT `LICENSE`.
