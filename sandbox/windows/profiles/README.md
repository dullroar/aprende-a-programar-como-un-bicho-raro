# Perfiles de lenguaje de Windows Sandbox

Cada archivo de esta carpeta enseña a `run.ps1` y a `inside.ps1` cómo compilar e iniciar un tipo de entrada. Como todo lo que hay en `sandbox/`, son propiedad de los mantenedores: una entrada nunca incluye uno, solo incluye su código, un README y, si quiere, un `check.ps1`.

Un perfil define estas funciones (las dos primeras se ejecutan en el anfitrión y las demás dentro del entorno aislado (*sandbox*)):

| Función | Qué hace |
| --- | --- |
| `Test-Entry $dir` | Anfitrión. ¿Esta carpeta es una entrada de este tipo? Sirve para elegir el perfil cuando no se indica `-Profile`. |
| `Get-HostMaps` | Anfitrión. Las carpetas de la cadena de herramientas del anfitrión que se asignan en modo de **solo lectura**, como `@{ Host; Sandbox }`. Lanza un error, que remite a `SANDBOX-SETUP.md`, si la cadena de herramientas no está instalada. |
| `Initialize-Toolchain $work $home2 $onRunner` | Dentro. Pone la cadena de herramientas asignada en PATH, apunta las cachés a carpetas de trabajo con permiso de escritura y fuerza el funcionamiento sin conexión. |
| `Build-Entry $entry` | Dentro. Compila la entrada. Devuelve `$true` si lo logra. |
| `Start-Entry $entry $runArgs $out` | Dentro. Inicia la entrada y devuelve su proceso. |
| `Show-Outcome $entry $out` | Dentro, opcional. Después de mostrar y cerrar la ventana: imprime o guarda lo que produjo la entrada (filas de la base de datos, la página servida). |

| Perfil | Elige entradas con | Asigna en solo lectura |
| --- | --- | --- |
| `dotnet` | un `*.csproj` | el SDK de .NET y la caché de NuGet del anfitrión |
| `python` | un `*.py` (Tk) | la instalación de Python del anfitrión |
| `go` | un `go.mod` | la cadena de herramientas de Go y la caché de módulos del anfitrión |
| `gradle` | un `build.gradle` (Java, Kotlin) | el JDK y el directorio de Gradle del anfitrión |

Para añadir un lenguaje, añade un archivo aquí y nada más. El anfitrión necesita tener instalada la cadena de herramientas correspondiente; consulta [`SANDBOX-SETUP.md`](../../../SANDBOX-SETUP.md).
