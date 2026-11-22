# Cómo preparar todo para ejecutar las entradas de forma segura

Cada entrada de aquí es código que hace cosas raras a propósito, así que no necesitas ejecutar nada en tu máquina real para disfrutarla o revisarla. Hay dos lugares desechables donde ejecutar una entrada, y esta página es el único sitio que explica cómo dejar listo cada uno. Los README de cada entrada solo dicen lo que es propio de esa entrada y enlazan de vuelta aquí.

| Quieres ejecutar... | Usa | Necesita |
| --- | --- | --- |
| Una entrada de Linux (APL, Forth, Haskell, regex, Make, CMake, Go, Rust/GTK, Python/Tk, Java/Kotlin Swing, regex de .NET...) | **Docker**: `sandbox/container/run-image.sh src/<entry>` | [Docker](#docker) |
| Una entrada de Windows o de GUI (WPF, XAML, LINQ, Python/Tk, Java/Kotlin Swing, Go en un navegador) | **Windows Sandbox**: `sandbox\windows\run.ps1 src\<entry>` | [Windows Sandbox](#windows-sandbox), más la [cadena de herramientas](#toolchains-de-windows) de la entrada |
| Para juzgar una demanda (pull) de alguien que no conoces | Los mismos dos, ejecutados por la [puerta de verificación](sandbox/README.md#cómo-revisar-una-demanda-pull-de-alguien-a-quien-no-conocemos) | Ambos, o solo GitHub Actions |

Ninguno sustituye leer el código. Consulta [qué demuestra y qué no demuestra esto](sandbox/README.md#qué-prueba-y-qué-no-prueba-esto).

## Docker

Se usa para las entradas de Linux. Cada una se ejecuta desde su propia imagen pequeña con **sin red, un sistema de archivos de solo lectura, sin capacidades, usuario `nobody`, límites de recursos y un tiempo límite**, y te muestra lo que produjo.

### Instala

- **Windows 11:** instala [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) con el backend **WSL 2** (el predeterminado). Inícialo y espera a que el ícono de la ballena indique que está en ejecución. Los scripts se ejecutan en **Git Bash** (viene con [Git for Windows](https://git-scm.com/download/win)) o en un intérprete de comandos (*shell*) de WSL, el programa donde escribes comandos.
- **macOS:** Docker Desktop para Mac.
- **Linux:** Docker Engine de tu distribución o del repositorio de Docker. Los scripts deben poder ejecutar `docker` sin `sudo` (agrégate al grupo `docker`).

### Comprueba que funciona

```bash
docker run --rm hello-world
```

### Una sola vez: compila las imágenes base de confianza

La primera ejecución necesita internet una sola vez, para descargar Ubuntu y sus paquetes. Después, las entradas se ejecutan sin conexión.

```bash
sandbox/container/build-bases.sh
```

Este paso crea la cadena de herramientas de compilación (es lento la primera vez: incluye GHC, .NET y GNU APL, unos 2.5 GB) y las imágenes de ejecución pequeñas sobre las que se construyen las entradas (de 120 a 770 MB cada una). Ejecútalo de nuevo con `--force` después de traer cambios a `sandbox/`.

### Ejecuta una entrada

```bash
sandbox/container/run-image.sh src/forth                    # build the entry's image, run it, show the rows
sandbox/container/run-image.sh --out ./results src/haskell  # also copy what it wrote to ./results
sandbox/container/run-image.sh --tty src/regex-sed           # give it a terminal (for the animations)
sandbox/container/run-image.sh --online-build --out ./results src/RustChallenge1   # a GUI entry (Rust, Python, Java, Kotlin): screenshot.png lands in ./results
```

Las entradas que deben descargar dependencias durante la compilación (la entrada de Go, que obtiene su módulo de SQLite; la entrada de Rust, que obtiene sus *crates* bloqueados; y las entradas de Java y Kotlin, que obtienen Gradle y sus dependencias de Maven) necesitan `--online-build`. Usa eso solo en entradas que ya están integradas en `master`: entonces la compilación tiene red, pero la ejecución nunca la tiene.

### Si algo sale mal

| Síntoma | Solución |
| --- | --- |
| `failed to connect to the docker API` | Docker Desktop no se está ejecutando. Inícialo y vuelve a intentarlo. |
| `missing cc-rt-...:local: run build-bases.sh first` | Ejecuta `sandbox/container/build-bases.sh`. |
| `$'\r': command not found` o `invalid option name` desde un script del intérprete de comandos | Una copia de trabajo de Windows con finales de línea CRLF. `run-image.sh` y `run.sh` los convierten en una copia privada; si ejecutas un script a mano, no los convierten. |
| La compilación es muy lenta o se queda sin disco | La imagen de disco de Docker Desktop está llena: `docker system prune`, o aumenta el límite en la configuración de Docker Desktop. |

## Windows Sandbox

Se usa para las entradas de Windows y de interfaz gráfica. Es una máquina virtual de Hyper-V desechable con **la red desactivada, sin portapapeles, impresora, audio ni cámara, y con una sola carpeta de salida donde se puede escribir**. Empieza limpia cada vez y se borra al cerrarla.

### Instala

Necesitas **Windows 11 Pro, Enterprise o Education** (no Home), con la virtualización activada en la BIOS/UEFI. En un PowerShell de **administrador**:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM -All
```

Luego reinicia. Windows 11 24H2 y versiones posteriores también incluyen el comando `wsb`, que los scripts prefieren porque puede detener la máquina virtual por ti; compruébalo con `wsb --help`.

### Reglas básicas

- **Solo puede ejecutarse un entorno aislado (*sandbox*) a la vez.** Cierra primero cualquier ventana abierta de Windows Sandbox.
- Tu propio entorno aislado no estorba: el script usa su propia configuración y no toca la predeterminada.
- Windows Sandbox en Windows ARM64 necesita versiones ARM64 de las herramientas que aparecen abajo, porque se asignan desde tu máquina.

### Ejecuta una entrada

```powershell
sandbox\windows\run.ps1 src\PythonChallenge1     # builds/starts it, screenshots it, closes it, prints what it saved
sandbox\windows\run.ps1 src\xaml -RunArgs strict.xaml
sandbox\windows\run.ps1 src\ModernChallenge1 -Seconds 30 -Keep    # -Keep leaves the log and screenshot in a scratch folder
```

El perfil (el tipo de entrada) se elige a partir de los archivos de la carpeta de la entrada. El resultado es un registro de ejecución, una captura de pantalla (`screenshot.png`) y lo que haya guardado la entrada (su base de datos, la página que sirvió una entrada de Go) en la carpeta temporal, que se borra si la ejecución termina bien, salvo que pases `-Keep`.

### Toolchains de Windows

El entorno aislado no tiene internet. Por eso toma prestada la cadena de herramientas de tu máquina (montada en **solo lectura**) y restaura paquetes solo desde tus cachés. Instala lo que necesita la entrada y ejecuta la entrada una vez con normalidad para que se llenen las cachés.

| Tipo de entrada | Lo que necesitas en el anfitrión | Notas |
| --- | --- | --- |
| .NET (C#, XAML, LINQ) | El SDK de .NET 10 (`winget install Microsoft.DotNet.SDK.10`) | Los paquetes NuGet vienen de `%USERPROFILE%\.nuget\packages`; compila la entrada una vez en el anfitrión antes de usarla. |
| Python (Tk) | Python 3 para Windows con **tcl/tk e IDLE** (`winget install Python.Python.3.14`) | No uses el stub de Microsoft Store. No necesita nada más. |
| Go | Go (`winget install GoLang.Go`) | Ejecuta `go mod download` una vez en la carpeta de la entrada para que la caché de módulos quede llena. **Aún no se ha probado en hardware real.** |
| Java, Kotlin | Un JDK que corresponda a la entrada (Java 25) y un `%USERPROFILE%\.gradle` con las dependencias ya descargadas | Ejecuta `.\gradlew.bat runJava` (o `runKotlin`) una vez en el anfitrión. **Aún no se ha probado en hardware real.** |

Si falta una cadena de herramientas, `run.ps1` se detiene antes de iniciar nada e indica cuál falta.

### Si algo sale mal

| Síntoma | Solución |
| --- | --- |
| `Windows Sandbox is not enabled` | Haz el [paso de instalación](#instala-1) y reinicia. |
| `A Windows Sandbox is already running` | Cierra su ventana, o ejecuta `wsb list` y luego `wsb stop --id <id>`. |
| `network was reachable; refusing to run` | El entorno aislado se inició con la red activada. No la anules; revisa tu configuración de Sandbox y tu versión de Windows. |
| Se agotó el tiempo; se conservó la carpeta temporal | Abre `inside.log` en la carpeta temporal conservada que indica. |
