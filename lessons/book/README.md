# Compilación del libro

El libro completo, *¡Aprende a programar como un bicho raro!*, se compila en **un solo** documento con [pandoc](https://pandoc.org):

```bash
python lessons/book/build.py            # writes learn-programming-the-weird-way.pdf and .epub in the repo root, and lessons/book/out/weird-way.html
python lessons/book/build.py --check    # builds the HTML and verifies every internal link resolves
python lessons/book/build.py --check-diagrams   # the full render gate for the Program Flow diagrams (see Diagrams below)
```

- `chapters.txt` define el orden de lectura. Para añadir un capítulo, añade su ruta ahí.
- `metadata.yaml` contiene el título, el número de edición (`book-version`), el autor y la configuración de la tabla de contenido. El libro está numerado desde v3: sube `book-version`, el título y la portada de `front-matter.md`, y añade una sección a [`VERSIONS.md`](VERSIONS.md) (lo que añadió esa edición). `build.py` falla si no coinciden.
- `build.py` ensambla los capítulos y reescribe los enlaces después de que Pandoc analiza el Markdown. Los ejemplos de código se conservan literales. Un enlace a otro capítulo se convierte en un ancla dentro del libro. Un enlace al índice web se convierte en texto plano. Un enlace a cualquier otra cosa del repositorio (archivos fuente, `src/*/README.md`, `RETO.md`) se convierte en su URL de GitHub. Los capítulos en sí siguen siendo Markdown corriente, apto para GitHub.

- **Por qué las fuentes usan enlaces relativos y el PDF y el EPUB usan enlaces absolutos.** En GitHub y en un clon, un enlace relativo siempre funciona, y sigue funcionando si se renombra o se bifurca el repositorio. Un PDF o un EPUB no tiene ningún repositorio alrededor, así que sus enlaces a archivos fuente deben ser URL completas. [`repo_links.py`](repo_links.py) es el único lugar que conoce la dirección del repositorio: un valor canónico fijo por defecto (`https://github.com/dullroar/learn-programming-the-weird-way`, rama `master`), de modo que las mismas fuentes producen los mismos bytes en cualquier máquina. La compilación nunca lee `git remote`. Un *fork* puede definir `REPOSITORY_WEB_BASE` (y `REPOSITORY_BRANCH`) para publicar sus propios enlaces. Las páginas de título y de derechos de autor usan los marcadores `{{REPOSITORY_WEB_URL}}` y `{{REPOSITORY_WEB_LABEL}}`, que la compilación rellena. Si el repositorio vuelve a renombrarse, cambia `DEFAULT_WEB_BASE` ahí, recompila las publicaciones y haz *commit* de ellas. [`test_repo_links.py`](test_repo_links.py) prueba la correspondencia; [`test_repo_identity.py`](test_repo_identity.py) falla si el nombre antiguo del repositorio reaparece en cualquier sitio fuera de una lista corta y revisada (la etiqueta de la imagen interna del entorno aislado `code-challenge-sandbox:local` y un directorio de caché de compilación de Rust por usuario), incluso en los PDF y EPUB publicados.
- **El PDF** se escribe en la raíz del repositorio como `learn-programming-the-weird-way.pdf` y requiere [WeasyPrint](https://weasyprint.org) (`uv tool install weasyprint` o `pipx install weasyprint`; también requiere la biblioteca Pango, que la mayoría de los escritorios Linux y de las imágenes de WSL ya incluyen). Sin WeasyPrint, el script omite el PDF y deja una nota; el EPUB y el HTML quedan completos en ambos casos. El diseño de página es `book.css`; las fuentes son DejaVu, cuya cara monoespaciada tiene los glifos de APL (`⍴ ⍳ ⎕`; consulta [Cómo ver los glifos](../../src/apl/README.md#cómo-ver-los-glifos)).
- Las **páginas de título y de derechos de autor** están en [`front-matter.md`](../preliminares.md) (HTML plano, insertado antes de la tabla de contenido). El EPUB pone este material en su página de apertura. Edita los autores y la línea de derechos de autor en la fuente.
- Las **líneas de código largas** (expresiones regulares, XAML, CMake) se parten a la fuerza en el PDF mediante `wrap-code.lua`, para que nada se salga de la página. Una línea que continúa termina en `↩` y la siguiente empieza con `↪`. El Markdown fuente no se toca; el HTML y el EPUB reajustan el texto por su cuenta.
- El PDF y el EPUB de la raíz del repositorio se guardan con *commit*. El HTML y el Markdown ensamblado van a `lessons/book/out/`, que Git ignora.
- **Las guías de estudio son un conjunto de documentos aparte.** [`lessons/guias-de-estudio/`](../guias-de-estudio/README.md) contiene guías escritas a mano que se compilan con `python lessons/guias-de-estudio/build.py` en `learn-programming-the-weird-way-study-guides.pdf` y `.epub`, junto a los del libro. Ese script importa a este (`build_documents`), de modo que la reescritura de enlaces, el renderizado de diagramas, la llamada a Pandoc, la hoja de estilo y la regla de reproducibilidad se comparten y no se copian. Las guías no están en `chapters.txt`; el libro solo enlaza a ellas. [`study_guides.py`](study_guides.py) las comprueba y [`test_study_guides.py`](test_study_guides.py) prueba esas comprobaciones.

## Control de publicación del PDF

Cada compilación completa pasa por un lint el PDF que acaba de escribir. El libro y las guías de estudio usan el mismo gancho, incluso con `--artifacts-dir`. Ejecuta la compilación con `--release` para exigir WeasyPrint, un análisis de lint completo y cero errores. Sin `--release`, el lint posterior a la compilación informa de los diagnósticos y la compilación continúa. Las rutas `--check` que solo producen HTML no necesitan las dependencias del lint del PDF.

```bash
# From the repository root, in the Python environment used for the builds.
python -m pip install -r lessons/book/requirements-pdf-lint.txt

# Check finished PDFs without invoking Pandoc, Mermaid or WeasyPrint.
python lessons/book/lint_pdf.py --release \
  --json lessons/book/out/pdf-lint/both.json \
  --annotate-dir lessons/book/out/pdf-lint/pages \
  learn-programming-the-weird-way.pdf \
  learn-programming-the-weird-way-study-guides.pdf

# Run the same ordered gates as CI, with the build and diagram tools installed.
python lessons/book/build.py --check
python lessons/guias-de-estudio/build.py --check
python lessons/book/build.py --check-diagrams
python lessons/book/test_pdf_lint.py
python lessons/book/build.py --release
python lessons/guias-de-estudio/build.py --release
```

La CLI independiente usa los nombres de archivo de las publicaciones para elegir los centinelas del libro y de las guías de estudio. Usa `--profile book` o `--profile study-guides` para una copia renombrada, o `--profile letter` para la geometría de unos datos de prueba. Sus estados de salida son **0** para un análisis completo con cero errores, **1** para un análisis terminado con errores y **2** para un análisis incompleto o un fallo de invocación. Las advertencias son solo informativas en todos los modos. `--release` también rasteriza cada página a baja resolución y falla si el rasterizador lanza una excepción o si la imagen sale totalmente blanca pese a haber contenido sustancial detectado. El [flujo de trabajo de publicación del PDF](../../.github/workflows/pdf-release-gate.yml) compila ambos documentos desde la fuente y sube los diagnósticos del lint cuando se produce un fallo.

El linter deriva el tamaño Letter y su rectángulo de contenido de `book.css`. Comprueba MediaBox y CropBox con una tolerancia de 0.1 pt, el borde de la página con 1 pt y el margen del contenido con 1.5 pt. Las tolerancias de colocación admiten pequeñas variaciones en las métricas de los glifos. El análisis inicial también destapó una tabla y dos listados resaltados con intrusiones medibles muy por encima de esas tolerancias. El contenido del título, de los derechos de autor, de la tabla de contenido y del índice usa los márgenes regulares. La excepción del pie exige el número de página físico, la fuente y el tamaño esperados y una posición centrada en el pie.

| Reglas | Evidencia |
| --- | --- |
| PDF-001 a PDF-005 | Finalización del análisis, geometría de página y límites de colocación de glifos y de imágenes rasterizadas mostradas. |
| PDF-006 | Desbordamiento vectorial informativo, a partir de los límites de la ruta y de los límites del recorte que la contiene. |
| PDF-007 | Página de publicación vacía cuando no se detecta ningún objeto de cuerpo ni de dibujo. Los casos ambiguos y los datos de prueba genéricos de tamaño Letter son informativos. |
| PDF-008 y PDF-009 | Superposición informativa según el área relativa de los recuadros, una página casi vacía, un pie de figura sin evidencia de una figura cercana, o cuadrículas de tabla coincidentes con un borde abierto en un salto de página. |
| PDF-010 | Centinelas con nombre de texto seleccionable para las comparaciones de Mermaid y las etiquetas de Forth, los glifos de APL, los literales de expresiones regulares y de sed, y ciertos saltos de línea de Forth y de Make. Los datos de prueba renderizan comparaciones literales y el `#gt;` de Mermaid mediante la ruta SVG fijada. Su comparación de saltos de línea elimina solo las flechas emparejadas adyacentes de un corte deliberado en mitad de un token, donde no se perdió ningún espacio de la fuente. |
| PDF-011 | Fallos de rasterización de publicación y de la vista previa de diagnóstico. |

Los límites de ruta aproximan la tinta visible. Los recuadros de recorte aproximan el recorte, y el contenido descartado antes de serializar el PDF puede ser indetectable. Las mediciones de imágenes rasterizadas describen la colocación incluso cuando el enmascarado afecta a los píxeles visibles. Las comprobaciones de texto seleccionable cubren las cadenas de texto con nombre de [la lista de centinelas](pdf_sentinels.py). Los glifos convertidos en contornos y los límites semánticos de fila requieren inspección visual o evidencia de la fuente. La escala de las figuras sigue siendo responsabilidad de `--check-diagrams`. Una comprobación estructural aparte con `qpdf` es opcional y queda fuera de este control.

Guarda los diagnósticos en `lessons/book/out/`, que Git ignora. El gancho de compilación guarda un informe por documento en `out/pdf-lint/<stem>/report.json` y escribe las páginas afectadas en su subdirectorio `pages/`. Una vista previa muestra la región de contenido permitida en verde azulado, marca los recuadros medidos e indica la regla y el desplazamiento en una leyenda lateral. El límite por defecto es de 20 hallazgos en la consola y 12 páginas de vista previa por PDF, con hasta 12 elementos marcados por PNG. `--verbose` imprime todos los hallazgos y produce una vista previa de cada página afectada. El JSON siempre incluye todos los hallazgos.

La versión 1 del esquema JSON tiene los campos de nivel superior `documents`, `diagnostics`, `errors`, `warnings` y `exit_status`. Cada documento registra su nombre base, su perfil, `page_count`, `pages_scanned`, `complete`, `page_failures`, `content_checks` y `findings`. Cada hallazgo registra la regla, la gravedad, el mensaje, la página física con base uno (o null), un extracto, `box`, `allowed_box`, `overflow_pt` y un nombre de archivo de vista previa cuando existe. Los recuadros normalmente no están rotados y se expresan en puntos relativos al recorte, en el orden `[left, top, right, bottom]`. Los hallazgos de geometría de página muestran los recuadros de página medido y esperado. En una superposición, `allowed_box` es el recuadro medido del otro objeto. Una comprobación a nivel de documento puede tener geometría nula. Los documentos se ordenan por nombre base y los hallazgos por página, gravedad, regla y geometría. Los informes no contienen marcas de tiempo ni rutas de entrada absolutas.

Para una excepción intencionada, especifica el perfil, la regla y la firma del objeto observable, registra por qué se espera esa posición y prueba tanto esa excepción como un fallo genuino cercano. El archivo de dependencias de desarrollo fija PyMuPDF y Pillow. Este repositorio usa la distribución AGPL de PyMuPDF como herramienta local y de integración continua instalada, y distribuye las publicaciones de WeasyPrint y el código fuente del lint sin el paquete PyMuPDF. PyMuPDF sigue disponible bajo AGPL o bajo los términos comerciales de Artifex. [Licencias de PyMuPDF](https://pymupdf.io/licensing)

## Diagramas

El README de cada entrada tiene una sección `## Program Flow` con un diagrama de Mermaid (el contrato está en [`CONTRIBUTING.md`](../../CONTRIBUTING.md#program-flow-a-picture-of-the-machine)). El diagrama es texto en Git, y la compilación lo convierte en una figura. La imagen compartida de "qué hace el reto" es un bloque `mermaid` delimitado en [`intro.md`](../introduccion.md); el capítulo sobre eventos tiene otra. **Cualquier** bloque `mermaid` de un capítulo se renderiza.

**Cómo fluye.** `src/<entry>/README.md` (la fuente de verdad) la lee [`diagrams.py`](diagrams.py) con un escáner de Markdown que reconoce los bloques delimitados, no con una expresión regular. La sección `## Program Flow` la copia `build.py --generate` en el bloque generado `How each program runs` de la página de lección que nombra la clave `lesson:` de la entrada (la página conserva el bloque de Mermaid, así que GitHub también lo dibuja). Al compilar el libro, Mermaid CLI renderiza cada bloque `mermaid` una vez a SVG y otra a PNG, y lo sustituye por un `<figure>` HTML con pie de figura (`accTitle`) y texto alternativo (`accDescr`) antes de que se ejecute pandoc. El PDF y el HTML usan el SVG (vectorial, escalado para caber en una página); el EPUB usa el PNG (todos los lectores lo dibujan). Hay un solo renderizador y ningún segundo mecanismo.

**Preparación (una sola vez, sin necesidad de root).** Necesitas Node y un Chromium. Mermaid CLI está fijado en [`diagrams/package.json`](diagrams/package.json) y [`package-lock.json`](diagrams/package-lock.json) (`@mermaid-js/mermaid-cli` 12.2.0; probado con Node 24 y Chrome for Testing 147):

```bash
cd lessons/book/diagrams
PUPPETEER_SKIP_DOWNLOAD=1 npm ci          # installs Mermaid CLI into diagrams/node_modules (git-ignored)
# a Chromium: any of these is found automatically, or set MERMAID_CHROME=/path/to/chrome
npx playwright install chromium-headless-shell    # -> ~/.cache/ms-playwright   (or: apt install chromium)
```

Después de eso, la compilación funciona sin conexión. Si el entorno aislado de Chromium no funciona en tu contenedor, define `MERMAID_NO_SANDBOX=1`; los diagramas son texto de este repositorio, renderizado con el `securityLevel: strict` de Mermaid.

**Qué se comprueba y cuándo.**

| Comando | ¿Necesita el renderizador? | Qué comprueba |
| --- | --- | --- |
| `build.py --check` | No (lo avisa si falta) | Cada entrada tiene exactamente un encabezado `## Program Flow`, escrito exactamente así, con un bloque `mermaid`, `accTitle` y `accDescr`, sin etiquetas HTML, sin subencabezados y con las dos frases iniciales en negrita. Las páginas de lección generadas están al día. Si el renderizador está presente, también renderiza y comprueba cada diagrama. **Sin el renderizador, esto es solo una comprobación de sintaxis y estructura, y la compilación lo dice** |
| `build.py --check-diagrams` | Sí | **El control completo de renderizado.** Renderiza cada diagrama, imprime su familia, su tamaño natural, la escala que lo ajusta a una página Letter y el tamaño impreso de sus etiquetas. Falla si hay un error de renderizado (con la entrada, el encabezado y el mensaje de Mermaid), si un diagrama se imprimiría por debajo del 70 % de escala (etiquetas de menos de 8.4 pt), o si una segunda pasada no se sirve íntegramente desde la caché |
| `build.py` | Sí | Renderiza (o reutiliza) las figuras, borra los archivos en caché que ningún diagrama usa y compila el PDF, el EPUB y el HTML. Nunca escribe una figura en blanco ni un bloque de código sin renderizar: cualquier fallo lo detiene |

**Caché.** Las figuras viven en `lessons/book/out/diagrams/<key>.svg` y `.png` (Git ignora `out/`). La clave es un hash del texto del diagrama, la versión de Mermaid CLI, la versión de Chrome, la escala del PNG y [`diagrams/mermaid-config.json`](diagrams/mermaid-config.json). Si editas un diagrama, solo se vuelve a dibujar su figura. Si cambias el renderizador, el navegador o el estilo, se vuelven a dibujar todas. Una copia limpia renderiza todo una vez (unos 15 segundos). El PDF y el EPUB del repositorio contienen las figuras.

**Ajuste a la página.** `diagrams.py` calcula el tamaño impreso de cada figura (`FIT_W`, `FIT_H` en píxeles CSS, 1 px = 1/96 de pulgada) a partir de la geometría de página de `book.css`, de modo que una figura siempre cabe en una página con su encabezado y su pie, y nunca se parte. Si un diagrama es tan grande que escalarlo reduciría sus etiquetas por debajo del mínimo, la compilación falla y te dice qué README corregir. Las correcciones están en las reglas de contribución: menos nodos, etiquetas más cortas, hexágonos para las decisiones.

**Estilo.** [`diagrams/mermaid-config.json`](diagrams/mermaid-config.json): el tema `neutral`, DejaVu Sans (la fuente del libro), líneas oscuras sobre fondo blanco, etiquetas de texto SVG (`htmlLabels: false`, porque WeasyPrint no dibuja HTML dentro de un SVG) y ningún color que lleve significado.

**Un PDF ligero.** Dos cosas mantienen livianas las figuras para los visores de PDF, y un PDF temprano de v4 no tenía ninguna. El aspecto predeterminado `neo` de Mermaid da a cada nodo un borde con degradado y una sombra difuminada, así que la configuración dice `"look": "classic"` (plano y vectorial, pero nítido). Además, Mermaid centra cada etiqueta y dibuja los fondos de las etiquetas semitransparentes, y WeasyPrint escribe cada uno como un *grupo de transparencia* del PDF. Edge y Chrome (PDFium) dibujan cada grupo en un mapa de bits fuera de pantalla, y un libro con miles de ellos mostró páginas en blanco durante mucho tiempo, incluso en páginas sin figura, porque todas las páginas compartían una lista de recursos que nombraba todos los grupos. [`diagrams/flatten-text.mjs`](diagrams/flatten-text.mjs) se ejecuta sobre cada SVG después de Mermaid: el mismo Chrome mide cada etiqueta, el script la mueve a la posición equivalente anclada a la izquierda y convierte `opacity` de una sola forma en `fill-opacity`, y hace fallar la figura si alguna etiqueta se movió más de medio píxel. El PNG para el EPUB no se toca. El resultado: el PDF pasó de unos 7,500 objetos y 4.3 MB a unos 400 objetos y 2.1 MB, sin grupos de transparencia. `test_diagrams.py` comprueba que no quede texto centrado y (cuando WeasyPrint está instalado) que una figura se convierta en un PDF sin grupos. Si ves `a label moved by`, la figura usa una característica de texto que el script aún no maneja; el mensaje nombra el archivo.

**Modos de fallo.** `cannot render ... Mermaid CLI is not installed`: ejecuta la preparación de arriba. `no Chromium found`: define `MERMAID_CHROME`. Un error de análisis de Mermaid se imprime con la ruta del README y la línea de la que se queja Mermaid (una causa común es un `;` dentro de un mensaje de diagrama de secuencia). Los visores de PDF difieren: comprobamos el PDF con MuPDF; Ghostscript, con algunas resoluciones, omite partes de un SVG de WeasyPrint, y eso es un problema de Ghostscript.

**Pseudocódigo.** No hay una sección de pseudocódigo; es a propósito. Ningún estándar define uno que sirva para programas imperativos, de evaluación perezosa, de reescritura, automodificables y orientados a eventos sin borrar la diferencia entre ellos. El pseudocódigo puede aparecer en la prosa de una entrada cuando ayuda, etiquetado como tal; nunca sustituye al diagrama.

**Cómo añadir o cambiar un diagrama.** Edita la sección `## Program Flow` del README de la entrada, ejecuta `python lessons/book/build.py --generate` (actualiza la copia de la página de lección) y luego `--check-diagrams`. Mira la figura. No hay nada más que editar a mano. `python lessons/book/test_diagrams.py` prueba el extractor, las claves de la caché y el contrato.

## Capítulos dirigidos por metadatos

Una parte del libro se **genera** a partir de metadatos y de Markdown escrito por los autores. La comprobación de actualización verifica que el resultado coincida con esas entradas. Revisa las etiquetas contra la implementación y sus pruebas antes de cambiar los metadatos.

| Fuente (escrita a mano) | En qué se convierte |
| --- | --- |
| El front matter YAML al principio de cada `src/*/README.md` (consulta [`CONTRIBUTING.md`](../../CONTRIBUTING.md#how-your-entry-plugs-into-the-book)) | La tabla "En este repositorio" de cada concepto, el capítulo comparativo y las tablas entre los marcadores `<!-- BEGIN GENERATED ... -->` de `goals.md`, `patterns.md` y las páginas de lenguajes |
| [`cs-source/concepts/<id>.md`](../cs-source/concepts/): un archivo por concepto de ciencias de la computación (`title`, `chapter`, `order` y luego la prosa) | Una sección de un capítulo de `lessons/informatica/`. El nombre del archivo es la **etiqueta** que usan las entradas |
| [`cs-source/roles/<id>.md`](../cs-source/roles/): un archivo por cada papel de "lo que hace de bucle" | Una sección del capítulo comparativo (capítulo 9) |
| [`cs-source/chapters/NN-name.md`](../cs-source/chapters/) y [`cs-source/index.md`](../cs-source/index.md) | Las introducciones de los capítulos y la apertura de la parte "Por concepto de ciencias de la computación" |
| [`link-hosts.txt`](link-hosts.txt) | Los únicos sitios externos a los que puede enlazar la prosa |

**Cómo se fundamenta un concepto.** Cada página de concepto necesita algo real detrás, y la compilación falla si no lo tiene. Una entrada puede relacionarse con un concepto de tres maneras, indicadas en su front matter: `tags` (**demuestra** la idea), `analogies` (se parece a la idea) o `counterexamples` (muestra lo que la idea no es). La tabla "En este repositorio" del concepto tiene una columna que indica cuál. Algunos hechos son ciertos para *todas* las entradas, y un mantenedor los declara una sola vez en el front matter del propio concepto, en lugar de etiquetar cada entrada: `applies-to: all` (o `has:machine`, para las entradas que nombran su máquina) con una frase `applies-because:` obligatoria. Un concepto que ninguna entrada demuestra puede, en cambio, apuntar a un ejercicio específico con `exercise: exercises.md#anchor`. Se rechaza la frase de prosa "ninguna entrada usa esto todavía": ahora el generador dice qué hay detrás de cada concepto. `python lessons/book/build.py --orphans` imprime el fundamento de cada concepto y falla si alguno no tiene ninguno. `python lessons/book/test_cs.py` prueba las reglas.

Ejecuta `python lessons/book/build.py --generate` para actualizar el Markdown generado (los archivos de `lessons/informatica/` y los bloques marcados) sin ejecutar pandoc. Los archivos generados están **en el repositorio**, así que los lectores de GitHub ven los capítulos completos, y `--check` falla si están desactualizados o si algún metadato no es válido (una etiqueta desconocida, una clave ausente, un enlace a un sitio que no está en la lista).

En la prosa puedes escribir `[[concept-id]]` para enlazar a un concepto, `[[entry:folder-name]]` para enlazar a una entrada, y `{{table:glance}}`, `{{table:evaluation}}` o `{{table:roles}}` para una tabla generada. El cuerpo del archivo de un concepto debe contener: un párrafo (por qué existe y por qué se usa), una línea **Úsalo cuando**, una línea **Evítalo cuando** y una lista **Lee más**. El generador añade por sí mismo la tabla "En este repositorio".

### Enlaces

Los enlaces externos deben seguir la política de [`link-hosts.txt`](link-hosts.txt): primero Wikipedia, y después solo fuentes duraderas y con licencia abierta o de lectura libre (RFC del IETF, OWASP, MDN). `build.py --check` aplica la lista de sitios sin conexión. `build.py --check-links` consulta cada enlace externo de la prosa e informa de los que ya no cargan. Necesita red, así que deliberadamente **no** forma parte de `--check`; ejecútalo de vez en cuando y antes de una publicación.

### Compilaciones reproducibles

Las mismas fuentes dan los mismos bytes. Toda lista está ordenada, nada lee el reloj, y `SOURCE_DATE_EPOCH` se toma de la línea `date:` de [`metadata.yaml`](metadata.yaml), que también guarda un identificador EPUB fijo. Sube `date:` cuando publiques libros nuevos. La comprobación es simple: compila dos veces con `--artifacts-dir` apuntando a dos directorios vacíos y compara los archivos con `sha256sum`. Coinciden con las mismas versiones de pandoc y WeasyPrint (probado con pandoc 3.1.3 y WeasyPrint en Ubuntu 24.04). Eso incluye una compilación desde una caché de diagramas vacía (`lessons/book/out/diagrams/`): la caché solo ahorra tiempo, y el PDF y el EPUB del repositorio no dependen de ella.

Ese último punto requirió una corrección. Mermaid dibuja algunas formas de nodo, sobre todo el estadio `A(["..."])`, con rough.js, que agita cada contorno con números aleatorios. Sin semilla, cada dibujo nuevo de uno de esos diagramas difería del anterior. Muchas páginas de concepto usan estadios, así que una copia limpia recompilaba bytes distintos, y los archivos del repositorio solo podían reproducirse con la caché exacta que los había generado. [`diagrams/mermaid-config.json`](diagrams/mermaid-config.json) ahora define `handDrawnSeed`, que hace que la agitación sea la misma en cada dibujo. No lo quites. `test_diagrams.py` dibuja cada forma de nodo dos veces desde una caché vacía y falla si el SVG o el PNG cambian. Si cambias la semilla, la versión de Mermaid CLI o de Chrome, o la configuración, se vuelven a dibujar todos los diagramas y cambian el PDF y el EPUB: recompila los seis y haz *commit* de ellos juntos.

### Cuando se añade una entrada (para mantenedores)

Después de fusionar una entrada nueva: añade su fila a la tabla de `README.md` de la raíz, añade cualquier etiqueta, papel o lenguaje nuevo a `lessons/cs-source/`, ejecuta `python lessons/book/build.py` (regenera los capítulos, el índice, el PDF y el EPUB) y actualiza la línea en negrita **"N retos en M lenguajes"** al principio de `README.md` de la raíz. La compilación imprime los números correctos y avisa cuando esa línea está desactualizada. Es el único recuento que se mantiene a mano.

Para que el libro siga compilándose: da a cada capítulo exactamente un título `# `, enlaza entre capítulos con enlaces `.md` relativos y pon las respuestas de los ejercicios en [`answers-key.md`](../respuestas.md).

### Revisión del impacto en las guías

Compara una revisión propuesta con su base antes de compilar ambos volúmenes. El informe usa los ID de entradas y de conceptos, los enlaces a las fuentes y las dependencias indirectas de [`guide-dependencies.json`](guide-dependencies.json). Es una lista de lectura para quien revisa. Añade las dependencias que falten cuando una guía enseñe un mecanismo sin nombrar la fuente editada. Si un archivo modificado no afecta a ninguna guía, registra una lista vacía para esa ruta en el archivo de dependencias después de la revisión.

```bash
python lessons/book/guide_impact.py master                    # compare master with HEAD
python lessons/book/guide_impact.py master --worktree         # include uncommitted edits
python lessons/book/guide_impact.py master --check-review review.json
```

Cuando hayas comprobado las trazas, los ejercicios, los límites y las citas de fuentes de una guía, registra su token impreso en un objeto JSON con la ruta de la guía como clave, por ejemplo `languages/apl.md`. La comprobación rechaza los tokens ausentes y los que han quedado obsoletos por una edición de la guía o de las fuentes relevantes. Registra en la revisión la ejecución o la evidencia de fuente que lo respalda. Recompila juntos el libro y las guías de estudio por separado.

## Compilación de las guías de estudio

Las guías se compilan como su propio conjunto de HTML, PDF y EPUB, aparte del libro. El PDF y el EPUB del libro no las contienen.

```bash
python lessons/guias-de-estudio/build.py --check   # lint the guides, build the HTML, verify every internal link
python lessons/guias-de-estudio/build.py           # write the PDF and EPUB next to the book's, in the repository root
python lessons/book/test_study_guides.py       # the tests: template, diagrams, links, index
```

Las salidas son `learn-programming-the-weird-way-study-guides.pdf` y `.epub`. El orden de lectura está en [`chapters.txt`](../guias-de-estudio/chapters.txt). La compilación reutiliza la canalización del propio libro ([`lessons/book/build.py`](build.py)) para reescribir enlaces, renderizar diagramas, llamar a Pandoc y mantener la reproducibilidad. [`lessons/book/study_guides.py`](study_guides.py) comprueba en cada guía la plantilla, el texto de relleno, que los diagramas coincidan con su fuente y los enlaces.

El [control de publicación del PDF](README.md#control-de-publicación-del-pdf) comprueba el PDF de las guías después de cada compilación completa. Pasa `--release` para hacer obligatorios el PDF y su análisis de lint.

**Diagramas.** Un diagrama de "Flujo del programa" de una guía se copia literalmente de `src/<entry>/README.md` y se marca con `<!-- diagram-source: src/<entry>/README.md#program-flow -->`. La compilación falla si una copia se ha desviado. Solo se permite un diagrama nuevo cuando muestra una relación que ningún diagrama fuente muestra (ubicación del estado entre lenguajes, una traza de demanda perezosa, un límite de la transacción o un límite de autoridad). Se marca con `<!-- diagram-new: kind - why -->`.

**Enlaces externos.** Una guía solo puede enlazar a los sitios de [`lessons/book/link-hosts.txt`](link-hosts.txt). Wikipedia va primero. Los manuales del Proyecto GNU (`www.gnu.org/software/`) se añadieron para las guías, porque una afirmación sobre una implementación necesita su manual.

## Compilación del plan de estudios

El plan de estudios es un solo archivo escrito a mano, [`docs/plan-de-estudios.md`](../../docs/plan-de-estudios.md): un plan de curso de 16 semanas que apunta a los capítulos del libro, a las guías de estudio y a los ejercicios sin modificarlos. Se compila como su propio HTML, PDF y EPUB, aparte del libro y de las guías de estudio.

```bash
python lessons/plan-de-estudios/build.py --check   # lint the curriculum, build the HTML, verify every internal link
python lessons/plan-de-estudios/build.py           # write curriculum.pdf and curriculum.epub in the repository root
python lessons/book/test_curriculum.py       # the tests: plan, diagram, links, house style, page limit
```

[`lessons/plan-de-estudios/build.py`](../plan-de-estudios/build.py) importa el `build_documents` de esta compilación, igual que la compilación de las guías de estudio, de modo que se comparten la reescritura de enlaces, el renderizado de Mermaid, la llamada a Pandoc, la hoja de estilo, la regla de reproducibilidad y el lint del PDF. Sus propias comprobaciones cubren las semanas de 1 a 16 una sola vez cada una, el único diagrama con `accTitle` y `accDescr`, los enlaces y los sitios, el estilo de la casa (como máximo 25 palabras por frase de prosa, sin contracciones, sin rayas) y un límite de 12 páginas de PDF. La página de título y los metadatos están en [`lessons/plan-de-estudios/`](../plan-de-estudios/). Cuando cambia la edición del libro, también debe cambiar `companion-to` en `metadata.yaml`, después de que alguien revise el plan de estudios.
