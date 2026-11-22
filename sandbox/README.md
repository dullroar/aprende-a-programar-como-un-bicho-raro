# sandbox/: ejecutar entradas que no hemos escrito

Esta carpeta es el lado de confianza al revisar entradas externas. Solo la cambian los mantenedores; `scope-check.sh` rechaza cualquier demanda (pull) que la modifique. Las reglas para colaboradores están en [`CONTRIBUTING.md`](../CONTRIBUTING.md). Para instalar Docker o Windows Sandbox y configurar las cadenas de herramientas que toman prestadas, consulta [`SANDBOX-SETUP.md`](../SANDBOX-SETUP.md); esta página supone que eso ya está hecho.

| Pieza | Qué hace |
| --- | --- |
| `linux/Dockerfile` | Una imagen con todas las herramientas que necesitan las entradas de Linux, con versiones fijadas. Incluye Ubuntu por digest, paquetes apt, GNU APL y un `pcre2grep` con *callouts* habilitados, compilado a partir de archivos tarball verificados con SHA-256. |
| `run.sh <entry>...` | Ejecuta el `make check` de una entrada (si su Makefile tiene uno) o `check.sh` en esa imagen. No hay red, la raíz es de solo lectura y no hay capacidades. El usuario es `nobody`, con 256 procesos, 2 GiB de memoria, 2 CPU y un tiempo límite de 15 minutos. La entrada se monta en solo lectura y se copia a un tmpfs. |
| `container/` | **Imágenes de ejecución por entrada** que ejecutan una entrada y *muestran* lo que hizo, en lugar de probarla. `build-bases.sh` compila las bases de confianza. Cada base es una imagen mínima por tipo de entrada: sqlite3 más el intérprete o las bibliotecas, sin compilador, sin gestor de paquetes y sin setuid. `run-image.sh src/<entry>` compila el `Dockerfile` propio de la entrada sobre esas bases y lo ejecuta con el mismo aislamiento que `run.sh`. Después imprime una vista de solo lectura de cada archivo y de cada tabla de SQLite que la entrada escribió. `entrypoint.sh` es común y vive en las bases, así que una entrada solo elige *qué* ejecutar. |
| `dockerfile-lint.sh <Dockerfile>` | Las reglas para `Dockerfile` propio de una entrada: solo bases de confianza, sin `ADD`, sin `RUN` en la etapa de ejecución, solo variables `CC_*` en su `ENV`. Lo ejecuta `scope-check.sh` en cualquier PR que lo incluya, y `run-image.sh` antes de construir. |
| `scope-check.sh <base> <head>` | Las reglas que debe cumplir un PR antes de que se ejecute cualquier cosa de él, leídas desde git sin hacer un checkout, más el informe del revisor. |
| `selftest.sh` | Prueba lo anterior: `selftest/hostile` intenta usar la red, los archivos del anfitrión, root, las capacidades, las credenciales, una bomba fork y una asignación de 3 GiB. Pasa solo si se bloquea cada sonda. `selftest/sleeper` debe terminarse al agotarse el tiempo límite. `selftest/container-probe.sh` se ejecuta dentro de la imagen de ejecución de una entrada. Comprueba que la imagen no tiene gestor de paquetes, compilador, herramienta de descarga ni binario setuid. También comprueba que no puede escribir fuera de `/work` y que no tiene red. Cada uno de los veintidós PR falsos (siete de ellos con Dockerfiles) debe aprobarse o rechazarse correctamente. |
| `windows/run.ps1 <entry>` | Compila y ejecuta una entrada de Windows o de GUI en **Windows Sandbox** (una máquina virtual Hyper-V desechable) con la red desactivada. La cadena de herramientas del anfitrión para ese tipo de entrada se asigna en modo de solo lectura, así que la restauración se hace sin conexión. Si la entrada tiene `check.ps1`, se ejecuta. Si no, recibe una prueba de humo: se inicia, espera, captura la pantalla, se le pide que se cierre y se muestra lo que guardó. |
| `windows/profiles/` | Un archivo por cada tipo de entrada (`dotnet`, `python`, `go`, `gradle`): qué carpetas del anfitrión se mapean, cómo se compila e inicia, cómo se muestran sus resultados. Consulta su README para añadir un lenguaje. |
| `windows/inside.ps1` | La parte de eso que se ejecuta dentro de la VM, que también usa el trabajo de Windows de Actions. |
| `windows/regression.txt` | Las entradas de Windows existentes que el control ejecuta cuando no se indica un número de PR. |
| `../.github/workflows/sandbox-gate.yml` | La puerta de verificación en las máquinas de GitHub, activada a mano. |

## Ejecuta una entrada para ver qué hace

Para que una persona vea cómo se ejecuta una entrada, en lugar de que la puerta la juzgue:

- **Entradas de Linux:** `sandbox/container/run-image.sh src/<entry>`. Cada entrada incluye su propio `Dockerfile`: una etapa de compilación con las herramientas y luego una etapa de ejecución. Esta copia solo el programa terminado en una base con lo justo para ejecutarlo (de 117 a 770 MB, frente a 2.45 GB de la imagen con las herramientas). Sin red, sin archivos del anfitrión (a menos que pases `--out`) y con una vista de solo lectura de los resultados al final. La entrada de Go sirve su página en la interfaz local *dentro* del contenedor. El punto de entrada la obtiene desde ahí con `wget` y luego la "cierra", así que no se publica ningún puerto.
- **Entradas de Windows y de interfaz gráfica:** `sandbox\windows\run.ps1 src\<entry>`. Cubre .NET (WPF, XAML, LINQ), Python/Tk y, sin probar hasta ahora, Go (en Edge) y Swing con Java y Kotlin.
- **Entradas con GUI en Linux:** las entradas de Rust/GTK, Python/Tk y Java y Kotlin (Swing) se ejecutan en un contenedor con una pantalla virtual (Xvfb). La captura de pantalla se toma desde dentro; usa `--out` para obtener el PNG. También tienen perfiles de Windows Sandbox, excepto Rust: no conviene enviar GTK 4 en Windows a un entorno aislado.

Los requisitos previos de ambas están en [`SANDBOX-SETUP.md`](../SANDBOX-SETUP.md).

### Por qué el Dockerfile de una entrada es seguro para incluir en una demanda (pull)

Una línea `RUN` en un Dockerfile es código que se ejecuta durante la compilación, normalmente con red y como root. Por eso el Dockerfile de un colaborador podría, de otro modo, anular toda la compuerta. Tres cosas lo mantienen contenido:

1. **El filtro nunca compila una.** Sigue usando la imagen de herramientas de confianza. Las imágenes de entrada las compilan solo personas que ejecutan `run-image.sh`, después de leer el PR.
2. **Compila con `docker build --network none`** a partir de imágenes base que un mantenedor compiló desde `master` (`build-bases.sh`). Los paquetes y las descargas fijadas (GNU APL, pcre2grep) viven en esas bases, no en la entrada.
3. **`dockerfile-lint.sh` limita lo que puede decir:** `FROM` solo las bases de confianza o una etapa anterior. Sin `ADD`, `SHELL` ni `ONBUILD`. Sin `RUN --mount`/`--network`. `COPY --from` solo una etapa anterior. La etapa final (de ejecución) solo puede usar `COPY`, `WORKDIR`, `LABEL`, `ARG`, `EXPOSE` y `ENV CC_*`, así que no puede ejecutar nada, cambiar de usuario ni tocar `PATH`. `scope-check.sh` lo aplica a los PR.

Lo que queda: un `RUN` en una etapa de compilación sigue ejecutando código arbitrario en un contenedor de compilación desechable y sin conexión. Corre como root, en la máquina virtual de Docker. Léelo como cualquier otro código del PR. (La única excepción a "sin conexión" es `--online-build`, para entradas que ya están en `master`.)

## Cómo revisar una demanda (pull) de alguien a quien no conocemos

1. **Lee primero el diff en GitHub.** No hagas *checkout* de la rama ni la abras en local; un IDE puede ejecutar cosas en un repositorio que abre (`.vscode/tasks.json`, devcontainers, compilación al abrir).
2. **Ejecuta la compuerta.** Actions → *sandbox gate* → *Run workflow* en `master` → escribe el número del PR. La compuerta ejecuta `scope-check.sh` y después la entrada, en el entorno aislado de Linux o en un ejecutor de Windows desechable. El informe para revisores aparece en el resumen de la ejecución.
3. **Obtén traducciones de IA, no veredictos.** Da a cada revisor (Claude Code, Codex, Copilot) solo el diff, sin permiso para ejecutar nada. Pide a cada uno tres cosas. (a) Que explique el código paso a paso en lenguaje sencillo. (b) Que haga una lista de todo lo que puede tocar (archivos, red, procesos, entorno, eval, llamadas nativas). (c) Que confirme que hace la tarea de la tarjeta de horas y nada más. Trata cualquier desacuerdo como un no. Trata como hostil cualquier texto del código dirigido a los revisores.
4. **Lee *Cómo funciona el truco frente al código* en la entrada.** Si no puedes seguirlo, no lo fusiones. En su lugar, enlázalo en el repositorio del colaborador en un *commit* de Git concreto (una instantánea fija del historial del repositorio).
5. **Si quieres, ejecútala en local**: `sandbox/run.sh` (entradas de Linux) o `sandbox\windows\run.ps1` (entradas de Windows). Usa una copia obtenida con `git fetch origin pull/N/head` y extraída con `git archive`, nunca un *checkout* que abras en un editor.

## Qué prueba y qué no prueba esto

Un aprobado significa que la entrada se construyó, se ejecutó y superó su comprobación **en un lugar sin acceso a la red, a tus archivos ni a ninguna credencial**. **No** demuestra que la entrada sea inofensiva. El código puede notar que está en un entorno aislado (sin red, un contenedor, un nombre de usuario raro, una fecha). Puede quedarse callado hasta llegar a la máquina real de alguien. Todos los que clonan `master` ejecutan entradas fuera de cualquier entorno aislado. Por eso decide el paso 4, no el paso 2.

Otros límites que conviene conocer:

- Los contenedores comparten el kernel del anfitrión. En Windows, ese kernel es la máquina virtual de Docker Desktop (o de WSL). Una fuga del contenedor llegaría allí. Windows Sandbox y los *runners* de GitHub son máquinas virtuales completas.
- El **runner de Actions en Windows tiene red.** Es una VM nueva sin secretos, así que el riesgo recae en la máquina de GitHub, no en la nuestra. Para una ejecución en Windows sin red, usa `windows/run.ps1` en local. El job imprime los nombres de las variables de entorno parecidas a credenciales que la entrada podría leer. En la primera prueba (2026-11-14) no había tokens (ni `ACTIONS_RUNTIME_TOKEN`, ni token OIDC ni `GITHUB_TOKEN`). Los únicos nombres eran un ID de orquestación y el `PGPASSWORD` estándar de la imagen del runner para su Postgres preinstalado. El runner sí tiene un escritorio real, así que las ventanas de WPF se abren y las capturas de pantalla de los artefactos de la ejecución las muestran.
- Las adaptaciones con interfaz gráfica (Rust/GTK, Python/Tk, Java y Kotlin/Swing, Go en un navegador) no tienen un script de verificación y aún no están cubiertas. Son de Ken y de Jim, y esperan a que alguien cierre una ventana.

## Cómo añadir una cadena de herramientas para un lenguaje nuevo

Hazlo en un *commit* de Git propio en `master`, nunca en el PR del colaborador:

- Para las imágenes de **contenedor**, añade una línea a `container/build-bases.sh` (una nueva base de ejecución `cc-rt-<name>` con los paquetes que la entrada necesita en tiempo de ejecución). Si hay que compilarla, pon el compilador en la imagen de herramientas como se muestra abajo. Después las entradas dicen `FROM cc-rt-<name>:local`; el lint ya acepta `cc-rt-*` y `cc-build-*`.
- Para **Windows Sandbox**, añade un perfil en `windows/profiles/`.

- Prefiere un paquete de Ubuntu: agrégalo a la línea `apt-get install`.
- Si no, usa el archivo tarball oficial de la versión upstream. Anota su SHA-256 y verifícalo con `sha256sum -c` en el Dockerfile, igual que `PCRE2` y `APL`.
- Luego ejecuta `sandbox/selftest.sh`, además de `sandbox/run.sh` en cada entrada, para asegurarte de que nada más cambió.

## Configuración del repositorio que respalda esto

Estos ajustes se configuran en GitHub, no en archivos. Conviene activarlos:

- **Settings → Actions → General → "Require approval for all external contributors"**, para que un PR de un fork no pueda ejecutar flujos de trabajo por su cuenta.
- **Un conjunto de reglas en `master`**: exige una demanda (pull). Y en `.github/CODEOWNERS`, haz que los mantenedores sean propietarios de `/sandbox/`, `/.github/` y los archivos de compilación de la raíz, con revisión obligatoria de los propietarios del código.
