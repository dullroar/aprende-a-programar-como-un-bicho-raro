---
name: "Go"
teaches: "un solo `for` de tres partes con un cuerpo vacío puede ejecutar todo el programa en Go."
kind: port
languages: [go]
lesson: "languages/csharp-linq-xaml.md#the-one-statement-ports-same-trick-different-machinery"
loop-by: loop-statement
evaluation: eager
assurance: guaranteed
pairs-with: JavaChallenge1
machine: "Tres espacios de expresión, con funciones auxiliares en los espacios"
state: "Campos de una struct anónima"
tags: [control-flow, side-effect, thread-safety]
---
# Una instrucción, edición Go

Port de Ken en Go del reto en C# de Jim Lehmer. Es uno de cuatro ports hermanos, junto con [Java](../JavaChallenge1/README.md), [Kotlin](../KotlinChallenge1/README.md) y [Python](../PythonChallenge1/README.md). El README de Java explica [qué hace cada versión](../JavaChallenge1/README.md#what-every-version-does) y tiene la [comparación lado a lado](../JavaChallenge1/README.md#side-by-side) de las cuatro.

La restricción: `main` contiene exactamente una instrucción, un bucle `for` con el cuerpo vacío. Esto es una acrobacia sobre la mecánica de las expresiones, no un buen código de producción. Nada de aquí se conecta con un sistema real de registro de horas: las tarjetas están marcadas con `is_demo`.

## Ejecútalo

Necesitas la cadena de herramientas de Go (`winget install GoLang.Go`). La primera ejecución descarga un módulo.

```powershell
cd src\GoChallenge1
go run .
```

O, desde la raíz del repositorio, con Gradle: `.\gradlew.bat runGo`.

La ventana es una página en tu navegador predeterminado. Pulsa Close en la página, o cierra la pestaña, para terminar. Los registros se guardan en `src/GoChallenge1/data/demo-timecards.db`; la ruta es relativa al directorio de trabajo, así que ejecuta el programa desde este directorio. Elimina `data` para empezar de nuevo.

Si un IDE en ejecución no detecta `go` después de instalarlo, reinicia el IDE para que tome el nuevo PATH.

## Ejecútalo en un contenedor

Requisito previo: Docker, configurado una sola vez como se describe en [`SANDBOX-SETUP.md`](../../SANDBOX-SETUP.md#docker).

```bash
sandbox/container/run-image.sh src/GoChallenge1
```

Compila el [`Dockerfile`](Dockerfile) de esta carpeta y ejecuta el resultado sin red, con un sistema de archivos de solo lectura y con el usuario `nobody`. Después muestra la salida y una vista de solo lectura de las filas que escribió. La imagen contiene un binario estático de Go, sqlite3 (para el paso de inspección) y un `wget` diminuto. No tiene la cadena de herramientas de Go. Necesita `--online-build` (`sandbox/container/run-image.sh --online-build src/GoChallenge1`) porque la compilación descarga el módulo de SQLite. La ejecución en sí no tiene red. La página que el programa sirve en `127.0.0.1` se obtiene desde *dentro* del contenedor con `wget`, se guarda como `page.html` y luego se "cierra", así que nunca se publica nada en tu máquina.

## Ejecútalo en Windows Sandbox

Requisitos previos: Windows Sandbox y la cadena de herramientas de esta entrada, instalados en tu máquina y configurados una sola vez como se describe en [`SANDBOX-SETUP.md`](../../SANDBOX-SETUP.md#windows-sandbox).

```powershell
sandbox\windows\run.ps1 src\GoChallenge1
```

Ejecuta la entrada en una máquina virtual desechable con la red desactivada, captura la ventana, le pide que se cierre e imprime lo que guardó. La página se abre en Edge dentro de la máquina virtual, y el arnés también la obtiene por loopback y la guarda. **Aún no se ha probado en hardware real.**

## Estructura

| Archivo | Papel |
| --- | --- |
| [main.go](main.go) | `main` y su única instrucción |
| [helpers.go](helpers.go) | La entidad, el repositorio y los asistentes de expresiones |
| `go.mod`, `go.sum` | Definición del módulo |

Igual que en el original, la entidad y el tipo de acceso a datos quedan fuera de `main`. Go también necesita allí pequeñas funciones auxiliares (se explican más abajo).

## Flujo del programa

```mermaid
flowchart TD
    accTitle: GoChallenge1: una sola sentencia for, una goroutine y un diálogo servido por HTTP
    accDescr: Un diagrama de flujo. El inicializador crea una estructura de estado y abre el repositorio. La condición es verdadera mientras el total no pase de 40 y queden categorías. Entonces se ejecuta el cuerpo vacío, y la sentencia posterior ejecuta Seq, que bloquea, suma horas, prepara una tarjeta, desbloquea e inicia una goroutine que guarda las tarjetas preparadas. Cuando la condición es falsa, After ejecuta ShowDialog, que sirve una página y espera a que el navegador envíe por POST el aviso de que se cerró. Después WaitForSaves espera a las goroutines, y la condición devuelve falso para que el for termine.
    A["Inicializador: construye la estructura de estado y abre SQLite"] --> B{{"Condición: total <= 40 y ¿quedan categorías?"}}
    B -->|true| C["Cuerpo vacío"]
    C --> D["Sentencia posterior: Seq ejecuta sus argumentos en orden: lock, hours, card, unlock, spawn"]
    D --> B
    D -.->|go| G["Goroutine: bloquea, ejecuta SaveAll por reflexión, desbloquea"]
    B -->|false| E["Después: ShowDialog sirve una página en loopback y espera /closed"]
    E --> W["WaitForSaves espera a las goroutines"]
    G -.-> W
    W --> X["Después de que devuelve false: el for termina"]
```

**Qué muestra:** `for` en Go tiene las mismas tres cláusulas que el original en C#, pero Go solo permite instrucciones simples ahí. Por eso el trabajo pasa a funciones auxiliares, y `Seq(...)` ejecuta sus argumentos en orden, en lugar de usar la lista separada por comas. Las aristas punteadas son la parte concurrente: cada pasada inicia una goroutine, y el programa debe esperar a todas antes de terminar.

**Por qué importa este mecanismo:** el bucle termina por su condición, no por un `break`. Con `||`, la rama falsa hace el trabajo final (mostrar la página, esperar los guardados) y luego devuelve `false`. La ventana es una página del navegador, porque Go no tiene una biblioteca estándar para interfaces gráficas.

## Cómo funciona el truco

El trabajo se divide en tres partes: un **inicializador** que construye el estado del bucle, una **condición** que decide si se sigue adelante (y, en la última comprobación, muestra la ventana) y una **actualización** que hace una pasada de trabajo. Los banners de comentarios en el código fuente marcan los límites.

Go es el más estricto: una cláusula `for` permite solo sentencias simples, y Go no tiene operador ternario, ni expresión con coma, ni sentencias dentro de expresiones. El bucle sigue siendo un `for i := &struct{...}{...}; condition; post { }` real de tres partes, con los mismos dos puntos y coma que la versión en Java.

- **Inicializador.** `i := &struct{...}{...}`. Una estructura anónima guarda el estado: el fragmento de CSS, las horas, el usuario, el repositorio, las tarjetas preparadas, las categorías y un mutex.
- **Condición.** `total <= 40 && len(categories) > 0 || After(false, ShowDialog(...), WaitForSaves())`. El `||` cumple el papel del operador ternario: cuando el bucle debe terminar, se muestra la página, se esperan los guardados y el resultado es `false`.
- **Actualización.** Una sola llamada, `Seq(...)`, cuyos argumentos se evalúan de izquierda a derecha. Go evalúa en orden las llamadas a función de una lista de argumentos, así que `Seq` ocupa el lugar de la lista separada por comas: `Lock`, `Append` horas, `Append` una tarjeta, `Unlock`, `Spawn`.
- **El precio.** Todo lo que necesita una sentencia (`Lock`, `Append`, `Pop`, `Spawn`, `ShowDialog`) es una función pequeña que devuelve un valor en `helpers.go`. El cuerpo de la goroutine es una sola llamada a `Seq(...)`.
- **Ventana.** Go no tiene una GUI en su biblioteca estándar, así que `ShowDialog` sirve una página en un puerto de retorno local (*loopback*) y la abre en el navegador predeterminado. El pulso es un fragmento de animación CSS, igual que el original tenía un fragmento de animación. La página envía una petición POST a `/closed` cuando pulsas Close o la abandonas, y eso desbloquea el bucle.
- **Guardado.** El controlador es `modernc.org/sqlite`, un controlador escrito solo en Go que no necesita compilador de C. `MethodByName` de `reflect` llama a `SaveAll`. `WaitForSaves` evita que el proceso termine antes de que las goroutines acaben.

## Trampas que conviene conocer

- **Las funciones auxiliares son el precio.** Go no tiene expresiones-sentencia, así que cada operación que solo existe como sentencia (`Lock`, `Append`, `Pop`, `Spawn`, `ShowDialog`) vive en una pequeña función en `helpers.go`. Ese es el costo declarado de esta versión.
- **La ventana es una página web.** Go no tiene una interfaz gráfica (GUI) en su biblioteca estándar, así que el programa sirve una página en un puerto de loopback y abre tu navegador predeterminado. Presiona Close en la página, o cierra la pestaña, para terminar.
- **Ejecútalo desde este directorio.** La ruta de los datos es relativa al directorio de trabajo.
- **La compilación del contenedor necesita red.** Se necesita `--online-build` porque la compilación descarga el módulo de SQLite. La ejecución en sí no tiene red.
- **El perfil de Windows Sandbox aún no se ha probado en hardware real,** y esta versión portada no tiene script de comprobación, así que la verificación del entorno aislado (*sandbox*, un espacio separado del resto del sistema donde se ejecuta el programa) todavía no la cubre.
