# Ejercicios

Paso 5 de cada lección: *ahora rómpelo tú*. Cada ejercicio tiene un objetivo, una forma segura de ejecutarlo, **criterios de aceptación** que un estudiante (o su agente de programación) puede comprobar y, cuando es práctico, un comando que los comprueba. Las soluciones desarrolladas están en el [solucionario](respuestas.md). **Todo ejercicio marcado como "verificado" se ha ejecutado de principio a fin con las entradas reales**, en Docker o en un entorno aislado (*sandbox*) de Windows (Windows Sandbox), con [`verify-exercises.sh`](tools/verify-exercises.sh) y [`verify-windows.ps1`](tools/verify-windows.ps1); los que no se han ejecutado así llevan la etiqueta **reto abierto**.

El ritmo de cada ejercicio es **predecir, ejecutar, comparar**. Escribe tu predicción *antes* de ejecutar nada. La comprobación solo te dice si obtuviste un resultado; la predicción te dice si entendiste.

## Ejecutar con seguridad

Estos programas escriben archivos e inician procesos. No ejecutes en tu propia máquina entradas que no hayas leído. Usa el modo restringido del propio repositorio; la configuración única está en [`SANDBOX-SETUP.md`](../SANDBOX-SETUP.md) (incluye `sandbox/container/build-bases.sh`, que debes ejecutar una vez, y de nuevo con `--force` si una ejecución dice `cobc: not found` o algo similar: una imagen antigua de la cadena de herramientas es anterior a algunas entradas).

| Quieres... | Comando (desde la raíz del repositorio) | Dónde se ejecuta |
| --- | --- | --- |
| **Mira** cómo se ejecuta una entrada de Linux | `sandbox/container/run-image.sh <folder>` | Docker: sin red, raíz de solo lectura, usuario `nobody`, límites, tiempo de espera |
| Ejecuta la **propia verificación** de una entrada | `sandbox/run.sh <folder>` | Imagen Docker con las herramientas, carpeta copiada en un tmpfs |
| Ejecuta **cualquier comando** en ese modo restringido, con las variables de entorno | `lessons/tools/run-in-sandbox.sh [-e NAME=VALUE] <folder> <command...>` | el mismo modo restringido, sobre una copia privada de la carpeta |
| Ejecuta una entrada **Windows/WPF** | `sandbox\windows\run.ps1 <folder>` | Windows Sandbox: una máquina virtual desechable con la red desactivada |

`<folder>` puede ser cualquier carpeta, no solo una dentro de `src/`. **Trabaja sobre una copia** para que tu copia de trabajo se mantenga limpia:

```bash
WORK=$(mktemp -d)                  # a scratch folder
cp -r src/cobol-weird "$WORK/"     # then edit $WORK/cobol-weird/... and run the commands on that folder
```

(`run-image.sh` da a su imagen de Docker el nombre de la carpeta, así que conserva el nombre de la carpeta.)

Reglas básicas:

1. **Datos DEMO ONLY.** Nada se conecta a un sistema real de control horario, y tu ejercicio tampoco debe hacerlo.
2. **Se espera que los ejercicios de ruptura fallen en el propio `check.sh` de una entrada.** Ese es el objetivo: la comprobación demostró que la restricción era real.
3. **Los tiempos de espera agotados son resultados.** Algunas rupturas se ejecutan para siempre. Define `SANDBOX_TIMEOUT=30`; la ejecución imprime entonces `TIMEOUT after 30s` y termina con `124`.
4. **La salida es aleatoria.** El número de filas y los totales cambian en cada ejecución. Los criterios siguientes están escritos para cumplirse en *todas* las ejecuciones, así que no compares tus números con la clave de respuestas; compara las propiedades.

### El verificador compartido

[`lessons/tools/check-demo.sh`](tools/check-demo.sh) comprueba un informe que cumple la [regla numérica compartida](introduccion.md#what-the-challenge-does): un marcador `DEMO ONLY`, las horas de cada fila de 10 a 19, cada total acumulado igual al total anterior más las horas, la ejecución detenida en la primera tarjeta cuyo total pasa de 40 (el límite por defecto) y la línea `# committed` (o `# captured`) coincide con las filas. El código de salida 0 significa PASS.

```bash
sandbox/container/run-image.sh src/cobol-weird > out.txt 2>&1
bash lessons/tools/check-demo.sh out.txt          # PASS: 3 rows, total 46 (limit 40)
bash lessons/tools/check-demo.sh out.txt 50       # the same check against a limit of 50
```

## A. Calentamiento: predice y luego ejecuta

### A1. Lee las filas (verificado)

**Objetivo:** determina, solo a partir de la salida, qué tarjeta detuvo la ejecución y por qué eso no es un error por uno.

1. Elige tres entradas de [lenguajes](lenguajes/README.md) distintos que implementen la regla de la tarjeta que cruza el tope. Consulta las [diferencias entre entradas](introduccion.md#where-entries-differ) antes de elegir. Ejecútalas y guarda cada salida.
2. Para cada una, anota cuántas tarjetas había, qué tarjeta pasó de 40 y qué total llevaba la tarjeta *anterior*.
3. Ejecuta una cuarta (prueba `src/regex-dotnet`, cuyas filas no tienen columna de total acumulado) y predice su número de tarjetas antes de mirar.

Criterios de aceptación:

- `check-demo.sh` pasa en cada ejecución.
- En cada ejecución, el total antes de la última tarjeta es **de 40 como máximo**, y el total final **pasa de 40**.
- En una oración: ¿por qué un total de *exactamente* 40 no detiene la ejecución? (Pista: observa el `<= 40` en las reglas de parada.)

## B. Por lenguaje

### B1. COBOL: predice y luego rompe `ALTER` (verificado)

**Lección:** [COBOL / ALTER](lenguajes/cobol.md#alter). **Entrada:** una copia de `src/cobol-weird`.

1. **Predice:** el margen empieza en 59 ([`timecards.cob` L44](../src/cobol-weird/timecards.cob#L44)). Si empieza en 49, ¿por encima de qué total se detiene la ejecución?
2. Cambia `59` a `49`. Ejecútalo con `run-image.sh` y luego ejecuta la verificación propia de la entrada con `sandbox/run.sh`.
3. **Predice:** ¿qué ocurre si agregas `DISPLAY "x"` como primera línea dentro de `NEXT-CARD`?
4. Pruébalo en una copia nueva.

Criterios de aceptación:

- Paso 2: `check-demo.sh out.txt 50` pasa (la nueva regla es "el total pasa de 50") y `sandbox/run.sh` **falla** (la comprobación propia de la entrada exige 40).
- Paso 4: la compilación falla. El mensaje del compilador nombra el problema; anótalo. Tu respuesta explica por qué `ALTER` necesita un párrafo que sea *solo* un `GO TO`.

### B2. Haskell: rompe la pereza (verificado)

**Lección:** [Haskell](lenguajes/haskell.md#la-es-perezosa-como-flujo-de-control). **Entrada:** una copia de `src/haskell-weird`.

1. **Predice:** reemplaza `entries <- evaluate (length cards)` ([L144](../src/haskell-weird/timecards.hs#L144)) por `let entries = length cards`. ¿Qué pasa?
2. **Predice:** en una copia nueva, quita `unsafeInterleaveIO` de `lazily` y reemplaza `unsafeInterleaveIO $ case actions of` ([L64](../src/haskell-weird/timecards.hs#L64)) por `id $ case actions of`. ¿Qué pasa y se cuelga?
3. Ejecuta cada una.

Criterios de aceptación:

- Cambio 1: la salida contiene `handle is closed` y `check-demo.sh` falla. Explica qué se exigió *después* de que se cerró la tubería.
- Cambio 2: el programa se detiene con `cyclic evaluation in fixIO` en lugar de quedarse colgado. Explica qué valor necesita a cuál: la lista de acciones se fuerza ahora antes de que exista la lista de tarjetas.

### B3. Forth: mueve el ancla (verificado)

**Lección:** [Forth](lenguajes/forth.md). **Entrada:** una copia de `src/forth-weird`.

1. **Predice** y luego prueba cada cambio en una copia nueva:
   - (a) Pon `0 0` en su propia línea antes de `>in @ step rewind?` ([L101](../src/forth-weird/timecards.fs#L101)).
   - (b) Escribe la línea como `>in @ 0 0 step rewind?` (estado *después* del ancla).
   - (c) En `rewind?` ([L92-94](../src/forth-weird/timecards.fs#L92-L94)) cambia `41 <` por `51 <`.

Criterios de aceptación:

- (a) es inofensivo: `check-demo.sh` pasa. Explica por qué (el ancla sigue estando *después* de `0 0`).
- (b) se descontrola: usa `SANDBOX_TIMEOUT=30`. No hay ninguna línea `# committed`, aparecen muchas filas (cientos) y el total acumulado de cada fila es igual a sus propias horas (el estado se reinicia en cada pasada).
- (c) `check-demo.sh out.txt 50` pasa.
- En una oración: ¿por qué solo (b) rompe el bucle?

### B4. Make: quita la operación sin efecto y sobrescribe el reloj (verificado)

**Lección:** [GNU Make](lenguajes/make-cmake.md#gnu-make). **Entrada:** una copia de `src/make-gnu`.

1. **Predice:** elimina el `@:` final de la línea de la receta ([`Makefile` L111](../src/make-gnu/Makefile#L111)): cambia `...,0))@:)` por `...,0)))`. ¿Qué pasa?
2. En la entrada *sin modificar*, el Makefile ya tiene una sobrescritura de `NOW=<epoch>`. Ejecuta `lessons/tools/run-in-sandbox.sh src/make-gnu make NOW=1700000000`.

Criterios de aceptación:

- Paso 1: la salida termina en `# committed total=0 entries=0` y `make re-executed itself 0 times`: nunca se escribió una tarjeta que hubiera que rehacer, así que Make nunca se reinició. Tu explicación usa las palabras "la receta se expande a nada" y "rehacer".
- Paso 2: las filas muestran la semana ISO `2023-W46`, que coincide con `date -u -d @1700000000 +%G-W%V`.

### B5. CMake: muta el literal (verificado)

**Lección:** [CMake](lenguajes/make-cmake.md#cmake). **Entrada:** una copia de `src/cmake`.

1. **Predice:** la prueba de parada es un literal de regex de 41 `x` ([`timecards.cmake` L41](../src/cmake/timecards.cmake#L41)). Acórtalo a 31. ¿Cuál es la nueva regla de parada?
2. Ejecútalo y luego ejecuta la propia comprobación de la entrada.

Criterios de aceptación:

- `check-demo.sh out.txt 30` pasa.
- `sandbox/run.sh` en tu copia **falla**. (El propio `check.sh` del repositorio realiza esta misma mutación para demostrar que el literal controla el bucle.)
- Explica por qué la prueba de parada debe ir *primero* en la condición `while()`.

### B6. APL: la reescritura del error por uno (verificada)

**Lección:** [APL, funciones que se modifican a sí mismas](lenguajes/apl.md#funciones-que-se-modifican-a-sí-mismas-apl-weird). **Entrada:** una copia de `src/apl-weird`.

1. **Predice:** cambia `,5↓⊂[1]` por `,4↓⊂[1]` en [L53](../src/apl-weird/timecards.apl#L53). ¿Qué conserva cada hija de su madre?
2. Ejecútalo con `SANDBOX_TIMEOUT=40`.
3. En una copia nueva, cambia `⎕IO←0` ([L17](../src/apl-weird/timecards.apl#L17)) por `⎕IO←1` y ejecútalo.

Criterios de aceptación:

- Paso 2: la ejecución nunca termina por sí sola: obtienes `TIMEOUT after 40s` (salida `124`) o, en una máquina donde la recursión consume memoria más rápido que eso, se termina el contenedor por superar su límite de memoria (`Killed`, salida `137`). En ningún caso aparece una línea `# committed`. Aparecen filas cuyo total acumulado es igual a sus propias horas: cada hijo conserva la línea `T←H` de su padre y reinicia el total, así que la regla de parada nunca se activa. Explica por qué el `check.sh` de la entrada se ejecuta bajo `timeout`.
- Paso 3: se imprime un `INDEX ERROR` y no aparece ninguna fila. Explica qué indexación del programa supone origen 0.

### B7. LINQ: enumera dos veces (verificado)

**Lección:** [C# y LINQ](lenguajes/csharp-linq-xaml.md#la-ejecución-diferida-y-el-truco-de-convertir-void-en-valor).

1. En una carpeta nueva y vacía, crea un proyecto de consola (`dotnet new console`, destino `net10.0`) cuyo `Program.cs` construye
   `var q = Enumerable.Range(1, 3).Select(i => { Console.WriteLine($"effect {i}"); return i; });`
2. **Predice** cuántas líneas `effect` se imprimen después de: (a) declarar `q`; (b) un `q.Sum()`; (c) `q.Sum()` *y* `q.ToList()`; (d) `q.ToList()` una vez y luego `.Sum()` sobre la *lista*.
3. Ejecútalo (Docker: `lessons/tools/run-in-sandbox.sh -e DOTNET_NOLOGO=1 <folder> dotnet run`; o `dotnet run` en una máquina Windows). Imprime una línea marcadora entre los pasos para poder contar.
4. Agrega `var r = new Random(42);` e imprime `r.Next(10, 20)` cinco veces. La entrada XAML inicializa exactamente este generador ([`strict.xaml` L13](../src/xaml/strict.xaml#L13)).

Criterios de aceptación:

- (a) 0, (b) 3, (c) 6, (d) 3 líneas `effect`. Nombra la propiedad de `Select` que hace que (a) sea cero y (c) sea seis.
- Las cinco horas para la semilla 42 son `16 11 11 15 11`. Explica por qué un programa XAML con semilla 42 produce las mismas tarjetas en cada ejecución.
- Nombra el único operador de [`LinqChallenge1/Program.cs`](../src/LinqChallenge1/Program.cs#L45) que es *ansioso* (*eager*) y fuerza las etapas perezosas. En [`ModernChallenge1`](../src/ModernChallenge1/Program.cs#L64-L68), ¿cuándo produce la consulta la suma que controla el bucle?

### B8. Regex: qué sobrevive a una coincidencia fallida (verificado)

**Lecciones:** [Regex](lenguajes/regex.md). **Entradas:** copias de `src/regex-dotnet` y `src/regex-pcre2grep`.

1. **.NET:** para una entrada de prueba fija, reemplaza `Random.Shared.Next(10, 20)` en `Draw()` por `10`. Ejecuta una vez en un directorio de datos temporal nuevo. Después cambia el final del patrón en [L13](../src/regex-dotnet/Program.cs#L13) de `)*");` a `)*(?!)");` y ejecuta en otro directorio nuevo. Predice qué puede seguir leyendo el anfitrión. Compara stdout, el estado de salida del proceso y el TSV guardado.
2. **pcre2grep:** en `timecards.sh`, cambia el primer `(?C{/usr/bin/sqlite3` por `(?C{sqlite3`. Predice qué ocurre.

Criterios de aceptación:

- .NET: el patrón sin mutar devuelve true, con cinco filas, un total de 50 y salida 0. El fallo forzado devuelve false, con cero filas, un total de cero y salida 1. El anfitrión sigue añadiendo el encabezado y el resumen a su TSV.
- pcre2grep: **ninguna salida**, código de salida 0, ninguna fila; `check-demo.sh` falla. Un callout que no puede iniciarse es indistinguible de una rama vetada.
- Escribe tres oraciones que contrasten qué sobrevive a una coincidencia fallida en Perl (`local` se deshace, los efectos secundarios permanecen), PCRE2 (la estructura de C persiste) y .NET (se devuelven cero capturas, y el anfitrión aun así imprime y escribe su informe vacío).

### B9. sed: observa un cálculo (verificado)

**Lección:** [GNU sed](lenguajes/regex.md#gnu-sed). **Entrada:** `src/regex-sed`.

1. Ejecuta `lessons/tools/run-in-sandbox.sh -e TRACE=1 src/regex-sed ./timecards.sh 2> trace.txt`.
2. **Predice** cuántas líneas de estado escribe el programa por tarjeta, aproximadamente.

Criterios de aceptación:

- `trace.txt` tiene muchas líneas que contienen `tot:`; la última tiene un campo `tot:` de **41 o más** caracteres `#`.
- Encuentra, en [`timecards.sed`](../src/regex-sed/timecards.sed), la regla que rechaza un sorteo de 10 a 15 para el valor de 4 bits ([L29](../src/regex-sed/timecards.sed#L29)) y di qué coincide con el patrón `1(01|1)`.
- El número de líneas de estado por tarjeta *no* es constante: explica por qué (los sorteos rechazados repiten un paso).

### B10. Lisp: cambia la combinación de métodos (verificado)

**Lección:** [Common Lisp](lenguajes/lisp.md#combinación-de-métodos-como-flujo-de-control). **Entrada:** copias de `src/lisp-weird`.

1. **Predice:** en una copia, reemplaza `or` por `progn` en ambos lugares: `(:method-combination or)` ([L61](../src/lisp-weird/timecards.lisp#L61)) y `(defmethod punch or ...)` dentro de `defcard` ([L39](../src/lisp-weird/timecards.lisp#L39)). `progn` ejecuta *todos* los métodos. ¿Cuántas tarjetas imprimirá cada ejecución?
2. **Predice**, en una copia nueva: cambia *solo* `(:method-combination or)` de la función genérica a `progn` y deja intactos los calificadores `or`.
3. **Predice**, en una copia nueva: cambia la prueba de parada `(> (total ledger) 40)` ([L84](../src/lisp-weird/timecards.lisp#L84)) por `(> (total ledger) 100)`.
4. Ejecuta cada una con `run-image.sh` (o `lessons/tools/run-in-sandbox.sh <copy> sbcl --script timecards.lisp`).

Criterios de aceptación:

- Paso 1: **exactamente cinco filas de tarjeta en cada ejecución** (ejecútalo cinco veces) y la nota final dice `PUNCH had 0 OR methods and 5 ran`. El `check.sh` propio de la entrada **falla** en tu copia.
- Paso 2: SBCL muestra advertencias que contienen `Invalid qualifiers for PROGN method combination`. Explica cuál es la regla: los calificadores de un método deben pertenecer a la combinación de su función genérica.
- Paso 3: **exactamente cinco filas en cada ejecución**, un total final de 95 como máximo y `check-demo.sh out.txt 100` falla con "does not pass 100". Explica por qué cinco es el máximo que este programa puede repartir y qué tendrías que cambiar para admitir un límite de 100.
- En una oración: ¿qué única palabra es la regla de parada y por qué quitarla no hace que el programa falle con un error?

### B11. m4: cita la recursión (verificado)

**Lección:** [m4](lenguajes/m4.md#un-bucle-hecho-de-reescaneo). **Entrada:** copias de `src/m4`.

1. **Predice:** ejecuta `lessons/tools/run-in-sandbox.sh src/m4 m4 -Dtc_seed=12345 timecards.m4` dos veces. ¿Qué cambia entre las ejecuciones y qué no?
2. **Predice:** en una copia, quita los corchetes alrededor de la llamada recursiva: cambia `[tc_card()]` al final de `tc_card` ([L82](../src/m4/timecards.m4#L82)) por `tc_card()`. Ejecútalo con `SANDBOX_TIMEOUT=20` y luego otra vez como `m4 -L 50 -Dtc_seed=7 timecards.m4`. (`-L` limita el anidamiento.)
3. En una copia nueva, cambia `eval(tc_total > 40)` por `eval(tc_total > 60)`.

Criterios de aceptación:

- Paso 1: las filas de tarjetas son idénticas en ambas ejecuciones (`Meetings 19`, `Coding 13`, `Debugging 16`, con totales 19, 32 y 48); solo el id de ejecución (contiene el reloj) puede diferir. Explica por qué una semilla fija produce las mismas tarjetas: el generador es una fórmula y el programa no tiene ninguna otra fuente de aleatoriedad.
- Paso 2: sin `-L` la ejecución termina en `TIMEOUT after 20s` (exit 124) y no imprime nada; con `-L 50` m4 se detiene con `recursion limit of 50 exceeded`, termina con un código distinto de cero y no hay ninguna línea `# committed`. Explica, en términos de *cuándo expande m4 los argumentos*, por qué los corchetes son la regla de parada.
- Paso 3: `check-demo.sh out.txt 60` pasa.

### B12. Tcl: edita el programa en la base de datos (verificado)

**Lección:** [Tcl](lenguajes/tcl.md#sqlite-como-programa). **Entrada:** copias de `src/tcl-weird`.

1. **Predice:** en una copia, cambia `PRAGMA recursive_triggers = ON;` ([L55](../src/tcl-weird/timecards.tcl#L55)) por `OFF`. ¿Cuántas filas de tarjetas se imprimirán? ¿Cuántas contará el resumen?
2. **Predice:** en una copia nueva, cambia el cuerpo de la fila `hours` ([L73](../src/tcl-weird/timecards.tcl#L73)) de `expr {10 + int(rand() * 10)}` a `expr {10}`. Estás editando *texto dentro de una cadena de texto SQL*, no un procedimiento (*proc*) de Tcl.
3. Ejecuta cada una: `sandbox/container/run-image.sh <copy>`.

Criterios de aceptación:

- Paso 1: se imprime **exactamente una fila de tarjeta** y el resumen dice `entries=2`: el disparador se ejecutó una vez (por eso la tarjeta 2 se insertó y se contó), pero una inserción hecha por un disparador no vuelve a activar el disparador a menos que la recursión esté habilitada, así que la tarjeta 2 nunca se imprimió. `check-demo.sh` falla.
- Paso 2: cada ejecución imprime **exactamente cinco filas**, con horas todas iguales a 10 y totales de 10, 20, 30, 40 y 50. `check-demo.sh` **pasa**. Explica por qué la ejecución no se detiene en 40 (compara con la última pregunta de [A1](#a1-lee-las-filas-verificado)).
- Nombra los tres puntos de enganche (una función SQL que llama a Tcl, `unknown`, un disparador) e indica cuál cambiaste en el paso 2.

### B13. AWK: el `RT` que falta (verificado)

**Lección:** [AWK](lenguajes/awk.md#registros-a-partir-de-un-flujo-de-bytes-aleatorios-awk-weird). **Entrada:** copias de `src/awk-weird`.

1. **Predice:** en una copia, crea un archivo de dígitos `printf '1 2\n' > d.txt` en la carpeta de la copia y ejecuta `lessons/tools/run-in-sandbox.sh <copy> gawk -f timecards.awk d.txt`. ¿Cuáles son las tarjetas? (Dados: `10 + RT`.)
2. **Predice:** en una copia nueva, ejecuta el mismo comando después de borrar la regla 1, la línea `RT == "" { next }` ([L52](../src/awk-weird/timecards.awk#L52)).
3. Ejecuta el programa *sin modificar* con mawk **solo con el archivo finito**: `lessons/tools/run-in-sandbox.sh <copy> mawk -f timecards.awk d.txt`. **No** lo ejecutes con mawk sobre `/dev/urandom`: nunca se detiene y consume memoria hasta que muere.
4. En una copia nueva cambia la regla de parada `t > 40 { exit }` ([L69](../src/awk-weird/timecards.awk#L69)) por `t > 80 { exit }` y ejecútalo sobre `/dev/urandom` (`run-image.sh`).

Criterios de aceptación:

- Paso 1: dos tarjetas, `Meetings 11 11`, `Coding 12 23` y `# committed total=23 entries=2`. El salto de línea final del archivo deja un último registro vacío que la regla 1 omite.
- Paso 2: **tres** tarjetas; la tercera es `Debugging 10 33` y el resumen dice `entries=3`. Explica por qué un `RT` vacío contó como una tarjeta de 10 horas (`10 + ""`).
- Paso 3: aparecen el encabezado y `# committed total=0 entries=0`, sin error, con código de salida 0. Explica por qué: mawk no tiene `RT`, así que `RT == ""` es verdadero para todos los registros y la regla 1 los omite todos. Di qué enseña esto sobre el código que "parece portable" y de qué [nivel de conocimiento](introduccion.md#three-kinds-of-knowledge) es `RT`.
- Paso 4: `check-demo.sh out.txt 80` pasa.

### B14. find: manipula los dados (verificado)

**Lección:** [find](lenguajes/find.md). **Entrada:** una copia de `src/find-posix`.

1. En la copia, crea un directorio `bin` con un script ejecutable `bin/mktemp` que siempre nombre el nuevo directorio `xxxxxS`:

   ```sh
   #!/bin/sh
   if [ "$#" -eq 2 ] && [ "$1" = -d ]; then d=${2%XXXXXX}xxxxxS; mkdir "$d" && printf '%s\n' "$d"; else exec /usr/bin/mktemp "$@"; fi
   ```

   Ejecuta `lessons/tools/run-in-sandbox.sh <copy> sh -c 'PATH=$PWD/bin:$PATH sh ./timecards.sh'`. **Predice** primero las filas. (Los dados usan el *último* carácter; `S` está en el grupo `STUVWX`, que es el décimo grupo.)
2. Cambia el nombre en el script a `xxxxxY` y ejecútalo de nuevo. **Predice:** se descarta `Y`.
3. Cambia el nombre a `xxxxYZ` y ejecútalo de nuevo. **Predice:** se descartan los dos últimos caracteres.

Criterios de aceptación:

- Paso 1: tres tarjetas, `Meetings 19 19`, `Coding 19 38`, `Debugging 19 57` y `# committed total=57 entries=3`. Cada dado muestra el mismo grupo, así que cada tarjeta tiene 19 horas.
- Paso 2: el recorrido lee el carácter anterior a `Y`. Ese carácter es `x`, del grupo `stuvwx`, el cuarto grupo, así que cada tarjeta tiene 13 horas: `13 13`, `26`, `39`, `52`. Son cuatro tarjetas, y el 39 *continúa*, porque 39 no pasa de 40. Explica por qué la regla de parada necesita aquí una cuarta tarjeta.
- Paso 3: se descartan los dos caracteres, así que las horas son 10. Cinco tarjetas: totales de 10, 20, 30, 40 y 50. El 40 continúa (un total de exactamente 40 no pasa de 40), y la quinta tarjeta vuelve a ser `Meetings`, porque solo hay cuatro categorías.

### B15. GNU find: mueve la regla de parada, lee el perfil (verificado)

**Lección:** [find](lenguajes/find.md). **Entrada:** copias de `src/find-gnu`.

1. **Predice:** en una copia, cambia la prueba de parada en `timecards.sh`, `-regex '([^/]*/){41}.*'`, a `{31}`. ¿Cuál es la nueva regla de parada? Ejecútala con `sandbox/container/run-image.sh` y luego ejecuta el `check.sh` de la propia entrada (`sandbox/run.sh <copy>`).
2. En una copia *nueva*, ejecuta `lessons/tools/run-in-sandbox.sh -e FIND_D=rates <copy> sh ./timecards.sh`. Mira el error estándar.

Criterios de aceptación:

- Paso 1: la nueva regla es "parar cuando la ruta tenga 31 barras o más", que equivale a "el total pasa de 30". `check-demo.sh out.txt 30` pasa. El `check.sh` propio de la entrada **falla**: sus escenarios de dados forzados esperan tarjetas que ya no se crean. Explica por qué basta con cambiar un número en una expresión regular para cambiar la regla de parada.
- Paso 2: find imprime, para cada prueba del programa, una línea como `[real success rate 1/94=0.01064]`. Podrás decir cuántas veces tuvo éxito la prueba `-name b00` (una vez por tarjeta) y por qué la estimación propia de find (`est success rate`) para las pruebas `-regex` queda tan lejos de la realidad.

### B16. tar: lee el programa y luego ejecútalo (verificado)

**Lección:** [tar](lenguajes/tar.md). **Entrada:** una copia de `src/tar-gnu`.

1. En la copia, escribe un archivo con horas fijas y léelo sin ejecutarlo: `sh build-archive.sh --seed 1 --hours "12 12 12 12 12" a.tar`, luego `sh inspect.sh a.tar`. **Predice** cuántas tarjetas se ejecutarán y cuáles de las cinco ranuras de tarjeta se leerán y se ignorarán. Después ejecútalo: `sh interpret.sh --execute a.tar`.
2. Desarma el programa con tar simple: `mkdir x && tar -C x -xf a.tar`. Abre `x/021.stop-over` y cambia `limit=40` por `limit=20`. Empaquétalo de nuevo **en el mismo orden**: `tar --format=ustar -cf b.tar -C x 000.begin 010.card 011.stop-over 020.card 021.stop-over 030.card 031.stop-over 040.card 041.stop-over 050.card 051.stop-over 990.show`. **Predice** las filas y ejecuta `b.tar`. Borra primero la base de datos anterior (`rm "$XDG_DATA_HOME/TarGnu/demo-timecards.db"`), para que solo esté esta ejecución. Ejecútalo con la tabla `trace` a la vista: `sqlite3 "$XDG_DATA_HOME/TarGnu/demo-timecards.db" 'select * from trace'`.
3. Añade un miembro que no está en el conjunto de instrucciones: `printf 'touch pwned\n' > x/025.exec`, empaqueta `x` de nuevo con `025.exec` después de `021.stop-over` y ejecuta `sh inspect.sh c.tar; echo $?`, luego `sh interpret.sh --execute c.tar; echo $?`. **Predice** ambos estados de salida y si aparece un archivo llamado `pwned`.

Criterios de aceptación:

- Paso 1: cuatro tarjetas (`Meetings 12 12`, `Coding 12 24`, `Debugging 12 36`, `Learning 12 48`); el programa lee la quinta posición y la ignora. `check-demo.sh` pasa.
- Paso 2: dos tarjetas (`Meetings 12 12`, `Coding 12 24`). El límite está en el archivo, así que cambiar un miembro cambió la regla de parada, y `dispatch.sh` no cambió. La traza muestra `ok` para las dos primeras tarjetas y `ignored: halted` para el resto. `check-demo.sh out.txt 20` pasa.
- Paso 3: el inspector imprime la línea `REFUSE (unknown record type)` y termina con código 4. `interpret.sh` termina con código 4 y dice que no se ejecutó nada. No existe ningún archivo `pwned`. Explica por qué `tar -xf` simple del mismo archivo comprimido tampoco lo crearía.
- En una frase para cada uno: ¿qué paso *analizó* el programa, qué paso lo *ejecutó* y dónde estaba la frontera de confianza?

### B17. tar, más raro: predice el reloj (verificado)

**Lección:** [tar](lenguajes/tar.md#el-archivo-es-el-reloj). **Entrada:** una copia de `src/tar-gnu-weird`.

Con la semilla 42 las tarjetas son `Meetings 12`, `Coding 17` y `Debugging 17`, así que el total sube a 12, 29 y 46 horas. La ejecución necesita 46 ticks.

1. **Predice** y luego ejecuta: `sh run-clock.sh --seed 42 --ticks 45` y después `--ticks 46`. Mira el estado de salida de cada una (`echo $?`).
2. **Predice** cuántos *ticks* obtienes con `sh run-clock.sh --seed 42 --ticks 92 --interval 2` y con `--ticks 91 --interval 2`. Luego ejecuta ambos.
3. **Predice** la salida de `sh run-clock.sh --seed 42 --ticks 260 --blocking 4`. ¿Cuántos registros escribe tar?
4. Abre la cinta de la última ejecución (`tr -d '\000' < tape.tar | wc -c` cuenta los bytes que no son cero). ¿Qué hay en ella y importa el contenido?

Criterios de aceptación:

- Paso 1: con 45 ticks la tercera tarjeta no termina, así que ves dos tarjetas, el mensaje `the clock ran out` y el estado de salida 3. Con 46 ticks la ejecución termina con tres tarjetas y estado de salida 0.
- Paso 2: con `--interval 2` la función de devolución de llamada (*callback*) se ejecuta una vez por cada dos registros. Una función de devolución de llamada es una función que el código llama cuando le toca. 92 registros dan 46 ticks, así que la ejecución termina. 91 registros dan 45 ticks, así que se atasca. El último `TAR_CHECKPOINT` en la ejecución terminada es 92, que es el número de registros; la máquina contó 46 llamadas.
- Paso 3: `-b 4` hace que un registro ocupe cuatro bloques. 260 bloques forman 65 registros y 65 ticks. La ejecución termina con las mismas tres tarjetas y hay 19 ticks inactivos.
- Paso 4: Casi todo `tape.tar` son ceros. Los únicos otros bytes son el encabezado de 512 bytes del miembro (su nombre, su modo y demás), menos de 100 de ellos. La carga útil no importa. Su *tamaño* es el reloj.

### B18. ed: mueve la regla de parada y rompe la limpieza (verificado)

**Lección:** [ed and Ex](lenguajes/editores.md#el-búfer-es-la-máquina). **Entrada:** una copia de `src/ed-weird`.

El lanzador recibe `DICE="a b c d e"`: cinco dígitos. Cada tarjeta tiene 10 horas más el valor de su dígito.

1. **Predice** y luego ejecuta: `DICE="0 0 0 0 0" sh timecards.sh` y `DICE="9 9 9 9 9" sh timecards.sh`. ¿Cuántas tarjetas imprimirá cada uno y por qué la quinta tarjeta del primero vuelve a ser `Meetings`?
2. En la copia, cambia `x\{41,\}` en `timecards.ed` por `x\{31,\}`. **Predice** las filas de `DICE="3 3 3 3 3"` antes y después del cambio. Luego ejecuta ambos.
3. Borra la línea `g/^Dead /d` de `timecards.ed`. Ejecuta el programa de ed por separado: `printf '3\n3\n3\n3\n3\n' > d.txt; ed -s d.txt < timecards.ed`. **Predice** la línea extra.

Criterios de aceptación:

- Paso 1: todas las tarjetas de diez horas dan cinco tarjetas con totales de 10, 20, 30, 40 y 50 (un total de exactamente 40 no detiene la ejecución, y solo hay cuatro categorías, así que la quinta es `Meetings` otra vez). Todas las tarjetas de 19 horas dan tres tarjetas: 19, 38 y 57.
- Paso 2: antes del cambio, `13 13 13 13 13` dan cuatro tarjetas (13, 26, 39, 52). Después, tres tarjetas (13, 26, 39): la ejecución ahora se detiene después del primer total que pasa de 30. `check-demo.sh out.txt 30` pasa. Un número en una expresión regular movió la regla de parada.
- Paso 3: la salida termina con una línea extra `Dead 0 52`. Es la quinta tarjeta, que se convirtió en una tarjeta muerta porque el total pasó de 40 en la tarjeta 4. La regla `Dead` es la que impide que las tarjetas cuenten; la limpieza solo las oculta.
- En una frase: ¿qué función de ed hizo posible cada uno de los tres cambios?

### B19. Ex: mueve el límite en la cinta y corta el bucle (verificado)

**Lección:** [ed and Ex](lenguajes/editores.md#un-programa-que-puedes-editar). **Entrada:** una copia de `src/ex-weird`.

El lanzador recibe `DICE="a b c d e"`: cinco dígitos. Cada tarjeta dura 10 horas más las horas de su dígito.

1. **Predice** y luego ejecuta: `DICE="1 1 1 1 1" sh timecards.sh`. ¿Cuántas tarjetas hay y cuáles son los totales?
2. En la copia, haz que la cinta diga "go on" hasta 45 en lugar de 40: `sed -i 's/^\(4[1-5]\) "$/\1 @a/' timecards.ex`. **Predice** las filas para los mismos dados y luego ejecútalas.
3. Quita el bucle: `sed -i 's/|@n$//' timecards.ex`. **Predice** cuántas tarjetas se ejecutan y luego ejecútalo con `DICE="5 5 5 5 5"`.
4. Mira el final de la línea del programa en `timecards.ex`. ¿Qué comando es el bucle y qué línea de la cinta lo detiene?

Criterios de aceptación:

- Paso 1: cuatro tarjetas, 11, 22, 33 y 44. El total pasa de 40 en la cuarta tarjeta, así que la fila de la cinta `44` es la primera instrucción "stop" que lee el programa, y la ejecución termina ahí. `check-demo.sh` pasa.
- Paso 2: cinco tarjetas, 11, 22, 33, 44 y 55. La fila 44 ahora dice `@a`, así que la ejecución continúa; la fila 55 sigue diciendo `"`. `check-demo.sh out.txt 45` pasa. El programa no cambió: solo cambió una línea de datos.
- Paso 3: una tarjeta. El programa se ejecuta una vez y no vuelve a iniciarse solo, porque ya nada ejecuta el registro `n`. Con `DICE="5 5 5 5 5"` la fila es `Meetings 15 15`.
- Paso 4: `@n` es el bucle, y el registro `n` guarda la instrucción de la línea de la cinta. La línea que lo detiene es la primera cuya instrucción es `"`, que es la del total de 41.

### B20. JavaScript: lee las cláusulas, mueve el límite y haz fallar la comprobación de estructura (verificado)

**Lección:** [JavaScript](lenguajes/javascript.md#el-for-sin-cuerpo-en-node). **Entrada:** una copia de `src/javascript`.

1. **Predice** y luego ejecuta: `SEED=42 node timecards.mjs`. ¿Qué tarjeta pasa de 40? (El generador es Park-Miller y las horas de las tres primeras tarjetas para esta semilla son 12, 17 y 17.)
2. En la copia, cambia `<= 40` en la condición por `<= 20`. **Predice** las filas de `SEED=42` y luego ejecútalas.
3. Pon una sentencia en el cuerpo del bucle: reemplaza `{ /* Intentionally empty. */ }` por `{ i.frames++; }`. Ejecuta `node timecards.mjs` y luego `node check-structure.mjs timecards.mjs`.
4. Ejecuta `NOW=2026-12-31 SEED=42 node timecards.mjs` y `NOW=2024-12-30 SEED=42 node timecards.mjs`. **Predice** la columna de la semana.

Criterios de aceptación:

- Paso 1: tres tarjetas, `Meetings 12 12`, `Coding 17 29`, `Debugging 17 46`, y la tercera tarjeta hace que el total pase de 40. `check-demo.sh` pasa.
- Paso 2: dos tarjetas, 12 y 29. La condición se evalúa después de que el iterador añade una tarjeta, así que se guarda la tarjeta que lleva el total de 12 a 29 y luego la prueba (29 es más de 20) termina el bucle. `check-demo.sh out.txt 20` pasa.
- Paso 3: el programa sigue ejecutándose e imprime las mismas tarjetas (la sentencia adicional cambia un contador que nadie lee), y la comprobación de estructura **falla** con un mensaje sobre el cuerpo. La restricción era una regla que rompiste, y la comprobación es la prueba de que era real.
- Paso 4: `2026-W53` y `2025-W01`. La semana es la semana ISO, y el año impreso es el año ISO, que puede diferir del año calendario en Año Nuevo.

### B21. JavaScript, más raro: mueve la regla de parada a una clausura (*closure*) y observa la demanda (verificado)

**Lección:** [JavaScript](lenguajes/javascript.md#clausuras-hasta-el-fondo). **Entrada:** una copia de `src/javascript-weird`.

1. Ejecuta el laboratorio de clausuras (*closure*: una función que conserva las variables del lugar donde se creó) en la copia sin modificar: `node --expose-gc --test check.mjs`. ¿Cuántas pruebas pasan?
2. En `core.mjs`, cambia la regla de parada `over = total > 40` por `over = total > 20`. **Predice** las filas de `SEED=42 node timecards.mjs` (las horas de las primeras tarjetas son 12, 17 y 17). Luego ejecuta el laboratorio otra vez. **Predice** si pasa.
3. Ejecuta esto, **predice** qué imprime y en qué orden:

   ```bash
   node --input-type=module -e "
   import { cards, machine } from './core.mjs';
   const m = machine(() => (console.log('drawn'), 15));
   const p = Iterator.from(cards(m)).map(c => c.total);
   console.log('built');
   console.log(p.take(1).toArray());"
   ```
4. En el mismo comando, cambia `take(1)` por `take(2)`. ¿Cuántas líneas `drawn` obtienes?

Criterios de aceptación:

- Paso 1: pasan las 12 pruebas.
- Paso 2: dos tarjetas (`Meetings 12 12`, `Coding 17 29`): la máquina dice `over` en cuanto el total pasa de 20. El laboratorio **no** pasa: fallan 7 de las 12 pruebas, y son las que fijan la regla de parada (la tarjeta que cruza el límite, exactamente 40, el número de sorteos, la repetición de la semilla 42). Las 5 que pasan tratan de las clausuras (*closure*: una función que recuerda las variables del lugar donde se creó) y no dependen del límite. En una frase: ¿por qué las pruebas de clausuras no dependen del límite?
- Paso 3: `built`, luego `drawn` y luego `[ 15 ]`. Construir la canalización no sortea nada. `take(1)` pide una tarjeta, así que se sortea un valor de horas.
- Paso 4: dos líneas `drawn` (y `[ 15, 30 ]`). El consumidor decide cuántas tarjetas existen.

### B22. JavaScript, dirigido por eventos: predice la traza y luego elimina el límite (verificado)

**Lección:** [JavaScript](lenguajes/javascript.md#escuchadores-de-eventos-hasta-el-fondo). **Capítulo:** [Eventos, funciones de devolución de llamada y flujo de control reactivo](informatica/10-eventos-retrollamadas-y-flujo-de-control-reactivo.md). **Entrada:** una copia de `src/javascript-events`.

1. Ejecuta el laboratorio de eventos en la copia sin modificar: `node --test check.mjs`. ¿Cuántas pruebas pasan?
2. **Predice** el orden de las tres líneas que imprime esto y luego ejecútalo:

   ```bash
   node --input-type=module -e "
   import { EventEmitter } from 'node:events';
   const e = new EventEmitter();
   e.on('x', () => console.log('listener'));
   setImmediate(() => console.log('immediate'));
   e.emit('x');
   console.log('after emit');"
   ```
3. **Predice** la traza de una ejecución en la que las tres tarjetas tienen 19 horas cada una. Escribe las líneas en orden, con `>name` donde empieza un `emit` y `<name` donde regresa. Luego ejecuta esto y compara. ¿Qué línea muestra que `emit('start')` regresó antes de que se creara la primera tarjeta?

   ```bash
   XDG_DATA_HOME=$(mktemp -d) node --input-type=module -e "
   import { program, realWorld } from './timecards.mjs';
   let hours = [19, 19, 19];
   const w = { ...realWorld(), rng: () => hours.shift() - 10, out: () => {} };
   const e = program(w); const raw = e.emit.bind(e);
   e.emit = (name, ...a) => { console.log('>' + name); try { return raw(name, ...a); } finally { console.log('<' + name); } };
   e.emit('start');
   console.log('main is done');"
   ```
4. En la copia, quita el límite de planificación: en el escuchador de eventos `total-updated`, reemplaza `later('generate')` por `events.emit('generate')`. Ejecuta el laboratorio de nuevo y `node check-static.mjs timecards.mjs`. Luego haz una ejecución muy larga:

   ```bash
   XDG_DATA_HOME=$(mktemp -d) node --input-type=module -e "
   import { program, realWorld } from './timecards.mjs';
   program({ ...realWorld(), limit: 10_000_000, out: () => {} }).emit('start');"
   ```

   **Predice** qué imprime y cuál es el estado de salida. Luego vuelve a poner `later('generate')` y ejecuta el mismo comando con `limit: 30_000`.

Criterios de aceptación:

- Paso 1: pasan las 14 pruebas.
- Paso 2: `listener`, `after emit`, `immediate`. `emit()` llama al escuchador de eventos antes de devolver el control. `setImmediate()` solo pregunta, y la función se ejecuta después de que termine el código actual.
- Paso 3: `>start <start main is done`, luego tres turnos. Cada uno de los dos primeros es `>generate >card-created >card-saved >total-updated <total-updated <card-saved <card-created <generate`. El tercero tiene `>finished >done <done <finished` dentro del `total-updated` más interno, porque 57 horas pasa de 40. `<start` y `main is done` vienen antes del primer `>generate`: `emit('start')` retornó antes de que existiera cualquier tarjeta.
- Paso 4: con el límite eliminado, una ejecución normal sigue funcionando (las tarjetas son las mismas), porque 40 horas solo llegan a unas pocas tarjetas de profundidad. El laboratorio **no** pasa: 12 pruebas pasan y 2 fallan, la de los eventos que se anidan dentro de un turno y la de una pila plana de más de 2000 tarjetas. `check-static.mjs` falla con un mensaje sobre `generate`. La ejecución muy larga imprime `timecards: Maximum call stack size exceeded` una vez y el estado de salida es 1: cada tarjeta añadió unos cuantos niveles a la pila. Con el límite restablecido y `limit: 30_000` se ejecuta con unas 2000 tarjetas y no imprime nada, con estado 0.

## C. Por patrón de solución

### C1. Lo raro junto a lo aburrido (verificado)

**Lección:** [Lo raro junto a lo aburrido](introduccion.md#weird-next-to-boring). El repositorio tiene muchos pares ya preparados, entre ellos `cobol`/`cobol-weird`, `haskell`/`haskell-weird`, `forth`/`forth-weird`, `apl`/`apl-weird`, `lisp`/`lisp-weird`, `tcl`/`tcl-weird`, `awk`/`awk-weird`, `tar-gnu`/`tar-gnu-weird`, `ed-weird`/`ex-weird` y `javascript`/`javascript-weird`.

Compara un par. Ejecuta ambos y cuenta las líneas de código (no los comentarios) de cada programa.

Criterios de aceptación:

- Ambas salidas pasan `check-demo.sh`.
- Una tabla pequeña compara el número de líneas, lo que podrías probar con pruebas unitarias, lo que mostraría un depurador y una cosa que solo la versión rara puede hacer.
- Respondes a la pregunta recurrente: *¿en qué circunstancias sería la versión rara la mejor opción?*

### C2. Haz real la restricción (verificada)

**Lección:** [patrones](patrones.md). Cada entrada incluye un `check.sh` que prueba su regla (por ejemplo, [`cobol-weird/check.sh`](../src/cobol-weird/check.sh) busca con grep las palabras prohibidas y cuenta los `ALTER`).

Escribe una comprobación para la regla de `src/forth-weird`: *sin palabras de bucle ni de rama, sin variables y `>in @` se lee al menos dos veces.*

Criterios de aceptación:

- Tu verificación pasa con el `timecards.fs` sin modificar.
- Falla con cada una de tres mutaciones (agrega un `begin`; agrega un `variable`; elimina los `>in @`). Muestra los tres comandos.
- Una palabra prohibida dentro de un comentario de `\` o de una `." string"` **no** lo activa (por eso debes quitar primero los comentarios y las cadenas de texto).

### C3. Un bucle cuyo estado no es una variable (verificado)

**Lección:** [Controla el estado fuera de las variables](patrones.md#control-state-outside-variables).

En awk, **sin** `for`, `while`, `do`, `function`, recursión ni `goto`, imprime los números de 1 a N, con N elegido por el *llamador*. (¿Dónde puede vivir el estado del bucle si no está en tu código?)

Criterios de aceptación:

- La salida es de `1` a `N` para N en 1, 3 y 10, ejecutada dentro del entorno aislado: `seq N | lessons/tools/run-in-sandbox.sh <folder> bash -c "awk '...'"`.
- Un `grep -Ew 'for|while|do|function|goto'` del código fuente de tu awk no encuentra nada.
- Indica en qué [nivel de conocimiento](introduccion.md#three-kinds-of-knowledge) se apoya tu truco.

## D. Adapta el reto (verificado: respuesta de referencia en awk)

**Objetivo:** implementa la demostración compartida en un lenguaje que todavía no esté en el repositorio (Lua, Ruby, Prolog, una CTE recursiva de SQL, PowerShell, Scheme, Perl...). Desde entonces el repositorio incorporó entradas de Common Lisp, m4, Tcl y awk, así que esos ya no están disponibles según las reglas de [`RETO.md`](../RETO.md); ejecútala solo en el entorno aislado.

Criterios de aceptación:

1. `check-demo.sh` pasa en **25 ejecuciones consecutivas**. En esas ejecuciones aparecen al menos cinco valores de hora distintos.
2. La salida tiene un marcador `DEMO ONLY` y una línea `# committed total=N entries=M` que coincide con las filas.
3. La regla de parada es una propiedad de tu truco, no un auxiliar llamado `RunEverything()`.
4. Los datos viven en un archivo SQLite local cuyo esquema rechaza una fila que no es de demostración (`CHECK(demo_only = 1)`), y tu verificación lo demuestra al intentar insertar una.
5. Un `Dockerfile` que pasa [`sandbox/dockerfile-lint.sh`](../sandbox/dockerfile-lint.sh) y se ejecuta con `run-image.sh`.
6. Un `check.sh` que impone tu restricción (consulta C2), un README con **Cómo funciona el truco** y **límites** honestos.

```bash
for i in $(seq 25); do
  sandbox/container/run-image.sh <your-folder> > out.txt 2>&1 || { echo "run $i failed"; break; }
  bash lessons/tools/check-demo.sh out.txt || { echo "run $i bad"; break; }
done
```

Consulta [`CONTRIBUTING.md`](../CONTRIBUTING.md) si quieres enviarlo. Una respuesta de referencia está en [`lessons/solutions/awk-port`](solutions/awk-port) (consulta la [clave de respuestas](respuestas.md#d-adaptación-del-reto)); intenta primero la tuya. Se escribió antes de que awk estuviera en el repositorio y es un tercer diseño breve (quien llama pasa por la tubería cinco registros y un patrón es la regla de parada), distinto de [`src/awk`](../src/awk/README.md) (un bucle `BEGIN`) y de [`src/awk-weird`](../src/awk-weird/README.md) (gawk y `RS`/`RT`): compara los tres.

## E. Pista de Windows Sandbox (verificada en Windows 11 Pro)

Para las entradas de WPF. Necesitas Windows Sandbox y un SDK de .NET 10 local ([configuración](../SANDBOX-SETUP.md#windows-sandbox)). Haz una compilación de cada entrada en el anfitrión antes, para que sus paquetes de NuGet queden en caché. Solo puede ejecutarse un entorno aislado a la vez.

### E1. Ejecuta y lee la evidencia

```powershell
sandbox\windows\run.ps1 src\LinqChallenge1
sandbox\windows\run.ps1 src\xaml -RunArgs strict.xaml
```

Criterios de aceptación:

- Cada ejecución termina con una línea `PASS ...`. El registro muestra `network: blocked`, así que la VM realmente no tenía red.
- `LinqChallenge1` informa `exactly 40.0h across 5 fixed rows` (su `check.ps1` espera esto) y se escribe un `screenshot.png`.
- `xaml` informa que escribió `xaml-demo-timecards.xml` y que el arnés cerró la ventana.
- Nombra una entrada cuyas filas dan un total de exactamente 40 porque los datos son fijos, y otra cuyas filas son aleatorias.

### E2. Cambia la semilla del intérprete XAML

Trabaja sobre una copia de `src\xaml`. En `strict.xaml`, la variable es el `Random` creado en [L13](../src/xaml/strict.xaml#L13): `<x:Arguments><sys:Int32>42</sys:Int32></x:Arguments>`.

1. Cambia `42` por `7` y ejecuta `sandbox\windows\run.ps1 <your copy> -RunArgs strict.xaml`.
2. **Predice:** ¿cambian las horas? Con el proyecto de consola de B7, calcula las primeras cinco horas para las semillas 42 y 7.

Criterios de aceptación:

- La ejecución en el entorno aislado sigue pasando con la nueva semilla.
- Tu programa de B7 imprime secuencias de horas distintas para 42 y 7, y la *misma* secuencia en cada ejecución con la misma semilla.
- Explica por qué el bucle de estos archivos `.xaml` tuvo que desenrollarse cuatro veces y qué elementos hacen el papel de "la variable".

## F. Demuestra una afirmación del README (verificada)

### F1. Prueba una afirmación de tu elección

Cada README tiene una sección "Gotchas" o "Walls". Elige **una afirmación** y escribe una prueba que fallaría si fuera falsa. Encuentras un ejemplo resuelto en la [clave de respuestas](respuestas.md#f-demuestra-una-afirmación-del-readme): "`takeWhile` no basta" ([`src/haskell/README.md`](../src/haskell/README.md#trampas-que-conviene-conocer)).

Otras afirmaciones válidas: "`SYSTEM` devuelve el estado de espera sin procesar (el código de salida 3 vuelve como 768)", "GnuCOBOL emite cinco advertencias sobre `ALTER`", "pcre2grep no busca en `PATH`".

Criterios de aceptación:

- La prueba se ejecuta en el entorno aislado y **pasa** con el comportamiento actual.
- También demuestras que **falla** ante un cambio deliberado (un control negativo).
- Indica si la afirmación es **garantizado**, **permitido por la implementación** o **aprovechado por accidente**, y cita la evidencia.

### F2. Trojan Source: oculta un carácter y luego encuéntralo (verificado)

**Lección:** [Trojan Source](informatica/01-lectura-de-un-programa-adversarial.md#trojan-source-characters-you-cannot-see). **Entrada:** ninguna. Ninguna entrada de este repositorio puede contener un carácter invisible, así que creas el archivo tú mismo en una carpeta temporal y nunca lo subes con *commit*. La afirmación que debes probar es la de [`CONTRIBUTING.md`](../CONTRIBUTING.md): "no invisible or direction-changing Unicode characters. APL glyphs and other visible Unicode are fine."

1. En una carpeta temporal, crea un programa con un espacio de ancho cero (U+200B) después de `admin` en la primera línea:

   ```bash
   printf 'const user = "admin\xe2\x80\x8b";\nconsole.log(user === "admin");\n' > greet.js
   ```

   Obsérvalo con `cat greet.js`. **Predice** qué imprime `node greet.js` y luego ejecútalo (por ejemplo con `lessons/tools/run-in-sandbox.sh <folder> node greet.js`).
2. Encuentra el carácter como lo hace la compuerta: `LC_ALL=C.UTF-8 grep -nP '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2060}-\x{2064}\x{2066}-\x{2069}\x{FEFF}\x{00AD}\x{2028}\x{2029}]' greet.js`. Después mira los bytes: `od -c greet.js | head`.
3. **Control negativo.** Crea el mismo archivo sin el carácter (`printf 'const user = "admin";\nconsole.log(user === "admin");\n' > clean.js`). Ejecuta el escaneo sobre él y ejecútalo también con `node`.
4. **La otra mitad de la afirmación.** Ejecuta el mismo escaneo sobre `src/apl-weird` (su código fuente está lleno de glifos APL visibles): `LC_ALL=C.UTF-8 grep -rlP '<the class above>' src/apl-weird`. **Predice** qué encuentra.

Criterios de aceptación:

- Paso 1: el archivo parece un programa que imprime `true`, y el programa imprime `false`. La cadena de texto tiene cinco caracteres que puedes ver (`a d m i n`) y uno que no puedes ver, así que no es igual a `admin`.
- Paso 2: el escaneo imprime la línea 1 de `greet.js` y `od` muestra los tres bytes `342 200 213` después de `admin`.
- Paso 3: el escaneo no encuentra nada en `clean.js` y el programa imprime `true`. Este es el control negativo: el escaneo se activa con el carácter oculto y con nada más.
- Paso 4: el escaneo no encuentra **ningún archivo** en `src/apl-weird`. El Unicode visible (`⍴`, `⍳`, `⎕`) no está en la clase, así que un revisor puede leerlo y la compuerta lo deja pasar. Explica en una oración por qué prohibir todo el texto que no sea ASCII sería la defensa equivocada.
- Indica si la afirmación es **garantizado**, **permitido por la implementación** o **aprovechado por accidente**, y cita la evidencia. (Pista: la regla de la puerta está escrita en `sandbox/scope-check.sh`, y `grep -P` con una clase de caracteres es su mecanismo. La clase solo tiene en su lista los caracteres que conocemos.)

## G. Retos abiertos (sin verificar; pueden ser imposibles)

Estos son los huecos de [problemas bloqueantes](problemas-bloqueantes.md). **Nadie ha demostrado que se puedan cerrar**, y no hay clave de respuestas. Ese es el objetivo: un muro bien documentado es un buen resultado ([`RETO.md`](../RETO.md)). Si resuelves uno, envíalo; si no puedes, documenta exactamente dónde falla.

| Bloqueo | Tarea | Cómo se ve el éxito |
| --- | --- | --- |
| LINQ no sortea horas aleatorias | Reemplaza la semana laboral fija por sorteos aleatorios de 10 a 19 horas, siempre en **una sentencia** | `check.ps1` sigue cumpliendo sus reglas de una sentencia; las horas varían entre ejecuciones |
| `regex-dotnet` no puede fallar a propósito | Haz que la coincidencia falle mientras el anfitrión sigue obteniendo las filas | Las mismas filas que la versión sin modificar; explicas cómo sobrevivieron las capturas |
| `regex-dotnet` no tiene efectos secundarios | Produce un pulso o una escritura durante la coincidencia sin `Replace`, `Matches`, `NextMatch` ni un bucle del anfitrión | Pulso visible; la lista de API prohibidas de `check.sh` de la entrada sigue pasando |
| `cmake` produce salida solo después del bucle | Imprime una fila desde *dentro* de la condición `while()` | Una fila por pasada antes de que termine el bucle, y la regla de sin cuerpo sigue cumpliéndose |
| Make necesita un intérprete de comandos (*shell*), el programa que ejecuta comandos de texto | Reemplaza `mkdir -p`, `sqlite3` o `rm` por algo nativo de Make en **uno** de ellos | La salida no cambia; la lista de programas del intérprete de comandos en `check.sh` se reduce en uno |
| Solo algunas entradas usan hilos | Agrega un hilo de trabajo a una entrada de script | Las filas se escriben desde el hilo y el hilo principal solo espera; `check-demo.sh` pasa |
| El RNG de `sed` es un juguete | Reemplaza el LFSR de 16 bits por uno de 32 bits | En 25 ejecuciones aparecen más de 16 primeros sorteos distintos; `check.sh` pasa |
| `awk-weird` necesita gawk | Obtén una tirada de dado sin `RT` para que también se ejecute en mawk | La misma forma de salida en gawk **y** mawk; sin `rand`, `srand`, bucle ni `if`; `check.sh` pasa en ambos |
| `m4` necesita un intérprete de comandos (*shell*, el programa que ejecuta los comandos que escribes) para su semilla y su semana | Genera la semilla y la semana ISO sin `esyscmd` | La semilla cambia de una ejecución a otra y la semana es correcta, con solo las funciones integradas de m4; si no puedes, anota exactamente a qué no puede acceder m4 |
| `lisp-weird` solo funciona en SBCL | Ejecútalo en una segunda implementación de Common Lisp (ECL o CCL) y cambia solo las llamadas específicas de cada implementación | Obtén la misma salida y la misma prueba de `or`/`progn` en ambas; da la lista de las líneas que cambiaste |
| `find-posix` nunca se ejecutó en BSD | Ejecuta `src/find-posix/check.sh` en un `find` BSD o macOS | O bien `check.sh` pasa, o das la lista exacta de qué primario, qué uso de `{}` o qué utilidad falló y qué hace cada BSD en su lugar |
