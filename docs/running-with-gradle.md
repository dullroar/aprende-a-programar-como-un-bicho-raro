# Ejecuta entradas con Gradle

El [`build.gradle`](../build.gradle) raíz tiene una tarea para cada entrada, además de tareas para el [entorno aislado (*sandbox*) de Docker](../sandbox/README.md):

```powershell
.\gradlew.bat runForth            # Windows
./gradlew runForth                # Linux, macOS
```

En IntelliJ IDEA, abre el repositorio, confía en él y recarga Gradle. Las tareas aparecen en la ventana de herramientas **Gradle**, en **learn-programming-the-weird-way → Tasks**, dentro de los grupos siguientes.

Una tarea solo inicia una entrada de su propia carpeta. Aun así, necesitas tener instalado el lenguaje de esa entrada.

## application: Java, Kotlin, Python, Go

`runJava` y `runKotlin` necesitan JDK 25. `runPython` necesita Python 3 para Windows (el lanzador `py`). `runGo` necesita el conjunto de herramientas de Go.

## aplicación (.NET)

`runLinq1`, `runLinq2`, `runModern`, `runXamlStrict`, `runXamlSqlite`, `runXamlEfcore`, `runRegexDotnet`

Necesitan el SDK de .NET 10. Todos salvo `runRegexDotnet` son WPF, así que solo funcionan en Windows.

## aplicación (WSL) / aplicación (Linux)

`runRust`, `runApl`, `runAplWeird`, `runForth`, `runForthWeird`, `runHaskell`, `runHaskellWeird`, `runCmake`, `runMakeGnu`, `runRegexPcre2`, `runRegexPcre2grep`, `runRegexPerl`, `runRegexSed`, `runCobol`, `runCobolWeird`, `runLisp`, `runLispWeird`, `runM4`, `runTcl`, `runTclWeird`, `runAwk`, `runAwkWeird`

En Windows se ejecutan dentro de WSL 2 (distribución `Ubuntu` o `-PwslDistro=Name`). En otros sistemas se ejecutan en `bash`. Cada uno comprueba primero si existe su herramienta y, si falta, la nombra y termina con el código de salida 127.

En Ubuntu 24.04, esto instala casi todo:

```bash
sudo apt install build-essential pkg-config sqlite3 perl make cmake gforth ghc gnucobol \
    libpcre2-dev cargo rustc libgtk-4-dev libsqlite3-dev \
    sbcl m4 tcl tk libsqlite3-tcl gawk
```

La última línea es para las entradas de Lisp, m4, Tcl y AWK. `runTclWeird` y `runTcl` necesitan el paquete `sqlite3` de Tcl (`libsqlite3-tcl`). Las tareas se ejecutan solo en modo texto: la ventana opcional de Tk (`tk`) es para cuando ejecutas `tclsh timecards.tcl --gui` por tu cuenta. `runAwkWeird` necesita gawk (usa `RT`). La verificación de herramientas nombra `gawk`, así que mawk, el predeterminado de Ubuntu, no es suficiente para esa entrada.

Las dos excepciones se compilan desde el código fuente:

- **GNU APL** (`runApl`, `runAplWeird`): consulta [`src/apl/README.md`](../src/apl/README.md).
- **`pcre2grep` con scripts de callout** (`runRegexPcre2grep`): la versión de Ubuntu no los incluye. Consulta [`src/regex-pcre2grep/README.md`](../src/regex-pcre2grep/README.md). La tarea busca en `~/.local/bin` o donde apunte `PCRE2GREP`.

`runRust` abre una ventana GTK, que necesita una pantalla (WSLg en Windows), y se mantiene abierta hasta que la cierras. Compila en `~/.cache/code-challenge/RustChallenge1-target` en el lado de Linux, porque las compilaciones en una unidad de Windows montada en WSL empezarían desde cero cada vez.

Cada entrada escribe sus registros en `~/.local/share/<Name>/` (o en `$XDG_DATA_HOME`). En Windows, eso queda dentro de WSL, en `\\wsl$\Ubuntu\home\<you>\.local\share\`.

## sandbox, sandbox (check), sandbox (show)

Estos ejecutan los scripts del entorno aislado del repositorio. Necesitan Docker, configurado como se explica en [`SANDBOX-SETUP.md`](../SANDBOX-SETUP.md#docker). En Windows también necesitan Git Bash, que viene con Git for Windows (o `-PgitBash=path`).

| Tarea | Qué hace |
| --- | --- |
| `sandboxBuildBases` | Construye las imágenes de confianza. Ejecútala una vez al principio (necesita red, unos 2,5 GB) y de nuevo con `-Pforce` después de traer cambios en `sandbox/`. |
| `sandboxSelftest` | Comprueba que el bloqueo funciona en tu máquina. |
| `sandboxCheck<Entry>` | Ejecuta el `check.sh` de la entrada exactamente igual que lo hace la [puerta](../sandbox/README.md). Hay uno por cada entrada con un `check.sh`. |
| `sandboxCheckAll` | Todo lo anterior. Cada entrada imprime `PASS` o `FAIL`. |
| `sandboxShow<Entry>` | Construye la imagen de contenedor de la entrada, la ejecuta bloqueada y muestra lo que escribió. Hay una por cada entrada con `Dockerfile`. Una copia va a `build/sandbox-out/<entry>/`, incluido `screenshot.png` para las entradas con interfaz gráfica. |

Los nombres de las tareas salen de los nombres de las carpetas (`src/apl-weird` da `sandboxCheckAplWeird`), así que las entradas nuevas obtienen tareas automáticamente. Una entrada nueva cuyo Dockerfile descarga archivos durante la compilación debe añadirse a la lista `onlineBuild` en `build.gradle`.

**Las entradas de WPF** (`LinqChallenge1`, `LinqChallenge2`, `ModernChallenge1`, `xaml`) no tienen tareas `sandbox…`, porque WPF no puede ejecutarse en los contenedores Linux de Docker. Para ejecutarlas de forma aislada, usa Windows Sandbox (`sandbox\windows\run.ps1 src\<entry>`, consulta [`SANDBOX-SETUP.md`](../SANDBOX-SETUP.md#windows-sandbox)), que requiere Windows 11 Pro, Enterprise o Education. El `check.ps1` de las entradas de Linq se ejecuta allí y en el trabajo de Windows del *gate*.

## Opciones

| Opción | Valor predeterminado | Para qué sirve |
| --- | --- | --- |
| `-PwslDistro=Name` | `Ubuntu` | La distribución de WSL para las tareas de Linux |
| `-PgitBash=path` | `C:/Program Files/Git/bin/bash.exe` | Git Bash para las tareas del entorno aislado |
| `-Pforce` | off | `sandboxBuildBases`: reconstruye todas las imágenes |

Agrégalas después del nombre de la tarea (`.\gradlew.bat runForth -PwslDistro=Ubuntu-24.04`), en el campo **Run** de una configuración de ejecución de IntelliJ o de forma permanente en `~/.gradle/gradle.properties` (`wslDistro=Ubuntu-24.04`).

## Cuando algo sale mal

| Síntoma | Solución |
| --- | --- |
| `<tool> is not installed in WSL` | Instálalo en WSL (consulta la sección anterior). |
| `/usr/bin/env: 'bash\r'` | El repositorio clonado tiene saltos de línea de Windows. [`.gitattributes`](../.gitattributes) evita esto en clones nuevos. En un clon más antiguo, ejecuta esto una sola vez con el árbol de trabajo limpio: `git rm -r --cached -q src && git reset -q --hard` |
| `failed to connect to the docker API` | Inicia Docker Desktop. |
| `missing cc-rt-…:local` o `command not found` en una comprobación del entorno aislado | Ejecuta `sandboxBuildBases` (con `-Pforce` si `sandbox/` cambió). |
| Sin animación de color en `runCmake`, `runMakeGnu` o las entradas de regex | La salida de Gradle no es una terminal, así que lo desactivan. En su lugar, ejecuta la entrada en una terminal (consulta su README). |
