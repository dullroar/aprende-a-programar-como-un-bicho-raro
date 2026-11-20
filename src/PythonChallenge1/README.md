---
name: "Python"
teaches: "que Python puede controlar un programa completo con `iter(step, False)`, que llama a `step` hasta que devuelve `False`."
kind: port
languages: [python]
lesson: "languages/csharp-linq-xaml.md#the-one-statement-ports-same-trick-different-machinery"
loop-by: lazy-demand
evaluation: lazy
assurance: guaranteed
pairs-with: JavaChallenge1
machine: "Una función que `iter` llama hasta que devuelve el centinela `False`"
state: "Atributos de un objeto de estado que se pasa a la lambda"
tags: [evaluation-strategy, event-loop, generators, side-effect, thread-safety]
analogies: [coroutine]
counterexamples: [event-driven-programming]
---
# Una instrucción, edición Python

Es el port a Python que hizo Ken del reto en C# de Jim Lehmer. Es uno de cuatro ports hermanos, junto con [Java](../JavaChallenge1/README.md), [Kotlin](../KotlinChallenge1/README.md) y [Go](../GoChallenge1/README.md). El README de Java tiene [lo que hace cada versión](../JavaChallenge1/README.md#what-every-version-does) y la [comparación lado a lado](../JavaChallenge1/README.md#side-by-side) de las cuatro.

La restricción: `main` contiene exactamente una instrucción, un bucle `for` con el cuerpo vacío. Es una acrobacia con la mecánica de las expresiones, no un buen código de producción. Nada de esto se conecta con un sistema real de registro de horas: las tarjetas están marcadas con `is_demo`.

## Ejecútalo

Solo necesitas Python 3: `tkinter` y `sqlite3` vienen incluidos.

```powershell
py src\PythonChallenge1\program.py
```

O, desde la raíz del repositorio, con Gradle: `.\gradlew.bat runPython`.

La ventana es una ventana de Tk. Los registros se guardan en `src/PythonChallenge1/data/demo-timecards.db`, junto a `program.py`, sin importar el directorio de trabajo. Borra `data` para empezar de nuevo.

## Ejecútalo en un contenedor

Requisito previo: Docker, configurado una sola vez como se describe en [`SANDBOX-SETUP.md`](../../SANDBOX-SETUP.md#docker).

```bash
sandbox/container/run-image.sh --out ./results src/PythonChallenge1
```

Construye el [`Dockerfile`](Dockerfile) de esta carpeta y ejecuta el resultado sin red, con un sistema de archivos de solo lectura y con el usuario `nobody`. La imagen contiene Python 3 con Tk, Xvfb y una herramienta de capturas de pantalla. No tiene pip ni compilador (unos 340 MB). La ventana se abre en una pantalla virtual (Xvfb) *dentro* del contenedor, así que no se dibuja nada en tu escritorio: la ejecución toma una captura de la ventana, la cierra e imprime las filas que escribió. Con `--out`, `results/screenshot.png` es la ventana.

## Ejecútalo en Windows Sandbox

Requisitos previos: Windows Sandbox y la cadena de herramientas de esta entrada en tu máquina, configuradas una sola vez como se describe en [`SANDBOX-SETUP.md`](../../SANDBOX-SETUP.md#windows-sandbox).

```powershell
sandbox\windows\run.ps1 src\PythonChallenge1
```

Ejecuta la entrada en una VM desechable con la red desactivada, captura la ventana, le pide que se cierre e imprime lo que guardó. Este ya se probó.

## Estructura

[program.py](program.py) es todo el port. Las clases de entidad y de repositorio están en el mismo archivo, encima de `main`.

## Flujo del programa

```mermaid
flowchart TD
    accTitle: PythonChallenge1: iter con un centinela llama a una función hasta que devuelve False
    accDescr: Un diagrama de flujo. Una lambda construye la función step a partir del objeto de estado. La instrucción for itera iter(step, False), así que llama a step una y otra vez. Cada llamada comprueba si el total no pasa de 40 y si queda una categoría. Si es así, se ejecuta una tupla de llamadas de izquierda a derecha: bloquear, sumar horas, preparar una tarjeta, desbloquear, iniciar un hilo que guarda. El último elemento de la tupla es True, que no es el centinela, así que se ejecuta el cuerpo vacío y el bucle llama a step otra vez. Si no, la rama else construye una ventana de Tk a partir de una cadena de texto XML y llama a mainloop, que bloquea hasta que se cierra la ventana, y step devuelve False. Eso es igual al centinela, así que iter se detiene y el for termina.
    A["Inicializador: una lambda recibe el estado y devuelve paso"] --> B["for _ in iter(step, False) llama a step()"]
    B --> C{{"step: total <= 40 y ¿quedan categorías?"}}
    C -->|sí| D["Tupla, de izquierda a derecha: lock, horas, tarjeta, unlock, hilo; valor True"]
    D -->|"True: el cuerpo es ..., llama a paso otra vez"| B
    D -.-> T["Hilo: save_all"]
    C -->|no| F["Si no: construye una ventana Tk a partir de XML, mainloop bloquea"]
    F --> G["paso devuelve False, el centinela: iter se detiene"]
```

**Qué muestra:** Python no tiene un `for` de tres cláusulas, así que el bucle es `iter(step, False)`: llama a `step` hasta que devuelva el centinela. Una expresión condicional es la prueba, y una tupla ocupa el lugar de la lista separada por comas. Python evalúa los elementos de la tupla en orden, y el último elemento (`True`) es el valor de la actualización.

**Por qué importa este mecanismo:** la parada es un valor de retorno que `iter` compara con el centinela, no una condición que `for` comprueba por su cuenta. La ventana muestra la misma idea que las otras versiones: la rama final hace el último trabajo y después devuelve el valor que termina el bucle.

## Cómo funciona el truco

El trabajo se divide en tres partes: un **inicializador** que construye el estado del bucle, una **condición** que decide si el bucle continúa (y, en la última comprobación, muestra la ventana) y una **actualización** que hace una pasada de trabajo. Los rótulos en comentarios del código fuente marcan los límites.

Python no tiene un `for` de tres partes, ni expresiones con coma, ni sentencias dentro de expresiones, así que el bucle es `for _ in iter(step, False): ...`. Llamar a `step` una y otra vez es el bucle. Se detiene cuando `step` devuelve el valor centinela `False`.

- **Inicializador.** `SimpleNamespace` guarda el estado. Se pasa a una lambda que construye `step`.
- **Condición.** Una expresión condicional: `(update ...) if total <= 40 and categories else (show the window ...)`.
- **Actualización.** Una tupla de llamadas cuyo último elemento es `True`; `[-1]` lo elige. Las tuplas se evalúan de izquierda a derecha, y eso reemplaza la lista con comas. Bloquea, suma horas, prepara una tarjeta, desbloquea e inicia un `threading.Thread`.
- **Cuerpo vacío.** El cuerpo es `...`, una expresión constante sin más. Un `pass` sería una segunda instrucción.
- **Ventana.** La ventana es una ventana de Tk, descrita por una cadena de texto XML que `xml.etree.ElementTree` analiza en tiempo de ejecución, con un widget por elemento mediante `getattr(tkinter, tag)`. `after()` repite un temporizador que mezcla el color de cada etiqueta hacia el color del fondo (las etiquetas de Tk no tienen alfa). `mainloop()` bloquea la ejecución hasta que se cierra la ventana.
- **Guardado.** El programa usa `sqlite3` de la biblioteca estándar. `getattr(repo, "save_all")` hace el papel de la reflexión.
- **Advertencia.** `main` es exactamente una sentencia `for`, pero las lambdas y las comprensiones que contiene son solo expresiones. Las importaciones, la entidad y el repositorio quedan fuera de `main`.

## Trampas que conviene conocer

- **`main` es una sola sentencia `for`, pero no todo lo es.** Las lambdas y las comprensiones que contiene son solo expresiones. Las importaciones, la entidad y el repositorio quedan fuera de `main`.
- **El cuerpo vacío es `...`.** Un `pass` sería una segunda sentencia.
- **Los datos viven junto al programa.** Los registros se guardan en `data/`, junto a `program.py`, sin importar el directorio de trabajo.
- **Las etiquetas de Tk no tienen alfa.** Por eso el pulso mezcla el color de cada etiqueta hacia el color del fondo, en lugar de desvanecerla.
- **Este port no tiene script de verificación,** así que el control del entorno aislado (*sandbox*) todavía no lo cubre. Un entorno aislado es un espacio separado donde el código se ejecuta sin afectar tu equipo. Ya se probó su perfil de Windows Sandbox.
