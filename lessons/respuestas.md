# Clave de respuestas

Soluciones desarrolladas para los [ejercicios](exercises.md). **Primero intenta el ejercicio**: escribe tu predicción, ejecútalo y solo entonces lee aquí.

Todas las soluciones siguientes se ejecutaron con las entradas reales:

- Ejercicios de Docker mediante [`tools/verify-exercises.sh`](tools/verify-exercises.sh) (cada modificación se hace en una *copia* de la entrada);
- Ejercicios de Windows Sandbox, un entorno aislado (*sandbox*) que limita el acceso al sistema anfitrión, mediante [`tools/verify-windows.ps1`](tools/verify-windows.ps1) en Windows 11 Pro.

La salida es aleatoria, así que los números aquí son *ejemplos*. Lo que está garantizado es la **propiedad** que cada ejercicio te pide observar. Variables de carpeta: `WORK=$(mktemp -d)` y `cp -r src/<entry> "$WORK/"` antes de editar.

## A1. Lee las filas

Ejemplo de salida de `src/cobol-weird`:

```text
Meetings   15   15
Coding     19   34
Debugging  12   46      <- crossing card: the total before it was 34, which is <= 40
# committed total=46 entries=3 DEMO ONLY
```

- La tarjeta que cruza el tope es la primera cuyo total acumulado es **más de 40**; el total anterior siempre es **como máximo 40** (de otro modo, la ejecución se habría detenido antes). Los totales pueden terminar entre 41 y 59.
- Un total de exactamente 40 continúa según la regla del reto. Cuatro tarjetas de 10 horas suman exactamente 40, así que una ejecución conforme conserva una quinta tarjeta. Se corrigió el antiguo techo de cuatro nombres en las entradas de regex y de encabezado `for`. Consulta la [introducción](introduccion.md#dónde-difieren-las-entradas) para el techo de cuatro pasadas de XAML y las demostraciones corregidas de LINQ. [`regex-dotnet`](../src/regex-dotnet/README.md) no imprime una columna de total acumulado, así que `check-demo.sh` suma las horas por sí mismo.

## B1. COBOL: predice y luego rompe `ALTER`

```bash
cp -r src/cobol-weird "$WORK/"                                   # run everything from the repo root
sed -i 's/PIC 99 VALUE 59\./PIC 99 VALUE 49./' "$WORK/cobol-weird/timecards.cob"
sandbox/container/run-image.sh "$WORK/cobol-weird" > out.txt 2>&1
bash lessons/tools/check-demo.sh out.txt 50                      # PASS: 4 rows, total 59 (limit 50)
sandbox/run.sh "$WORK/cobol-weird"                               # FAIL run N: kept going after the total passed 40
```

- **Predicción:** `WS-HEADROOM` es `PIC 99`. Se desborda cuando `headroom + total` llega a 100, es decir, cuando `total >= 100 - 49 = 51`. Así que la ejecución se detiene en la primera tarjeta que lleva el total **por encima de 50**. (Con el 59 original, es más de 40.)
- La ejecución termina con totales de 51 a 69; `check-demo.sh ... 50` pasa. El propio `check.sh` de la entrada falla porque contiene el valor 40 fijo en el código.
- **`DISPLAY "x"` dentro de `NEXT-CARD`:** la *compilación* falla porque `ALTER` solo puede reescribir un párrafo que sea exactamente un `GO TO`:

```text
timecards.cob:158: error: 'NEXT-CARD' is not an alterable paragraph
```

  (cinco de estos, uno por `ALTER`). El compilador debe saber que el único contenido del párrafo es un salto cuyo destino puede modificar.

## B2. Haskell: rompe la evaluación perezosa

1. `let entries = length cards` (un enlace perezoso) termina la ejecución con:

   ```text
   timecards: fd:5: hPutStr: illegal operation (handle is closed)
   ```

   Nada demanda las tarjetas hasta que se imprime la línea de resumen. Esto ocurre *después* de `COMMIT` y después de cerrar la tubería hacia `sqlite3`. Al forzar una celda se dispara su efecto sobre un manejador cerrado. `check-demo.sh` falla (una o dos filas, sin resumen).
2. Reemplazar `unsafeInterleaveIO $ case ...` por `id $ case ...` **no** se cuelga. Termina de inmediato con:

   ```text
   timecards: cyclic evaluation in fixIO
   ```

   Sin intercalar, construir la lista de acciones compara `before` con un patrón. Esto necesita `cards`, que `fixIO` aún no ha producido. (Solo se imprime la primera fila, `Meetings 10 10`, antes de detectar el bucle). `case` debe estar *dentro* de la acción diferida.

## B3. Forth: mueve el ancla

- **(a)** `0 0` en su propia línea, seguido de `>in @ step rewind?`: **funciona**. `>in @` captura la posición *después* de `@`. El retroceso salta a esa ancla, que está después de `0 0`. Por eso `0 0` nunca se vuelve a ejecutar. `check-demo.sh` pasa.
- **(b)** `>in @ 0 0 step rewind?`: el ancla está ahora *antes* de `0 0`. Cada retroceso vuelve a ejecutar `0 0` y apila un nuevo estado cero. El total vuelve a cero en cada pasada y la regla de parada nunca se activa. Con `SANDBOX_TIMEOUT=30` obtienes cientos de filas (678 en la ejecución de verificación). Cada fila tiene total = horas y no hay línea `# committed`.
- **(c)** `41 <` a `51 <`: `check-demo.sh out.txt 50` pasa (se detiene cuando el total llega a 51).
- **¿Por qué solo (b)?** La posición de análisis es un contador de programa: el punto al que vuelve determina qué tokens forman el cuerpo del bucle. El estado debe permanecer *fuera* del cuerpo (antes del ancla).

## B4. Make: elimina la operación nula y reemplaza el reloj

1. Sin `@:`, la receta `$(if ...,$(file >$@,...))` se expande a nada. Por eso Make no ejecuta ningún comando y **no considera reconstruido el makefile**. Nunca se reinicia, así que no se incluye ninguna tarjeta:

   ```text
   # committed total=0 entries=0 DEMO ONLY
   # make re-executed itself 0 times, once per card
   ```

   El archivo de tarjetas *sí* se escribió durante la expansión, pero Make solo detecta un makefile reconstruido cuando se ejecutó un comando. (`sandbox/run.sh` falla: "unexpected stderr".)
2. `lessons/tools/run-in-sandbox.sh src/make-gnu make NOW=1700000000` imprime filas etiquetadas `2023-W46`. `date -u -d @1700000000 +%G-W%V` imprime `2023-W46`.

## B5. CMake: modifica el literal

Con 31 `x` (`"^xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`), el bucle se detiene cuando el total llega a 31, es decir, **pasa de 30**. `check-demo.sh out.txt 30` pasa en cada ejecución. Con el límite predeterminado de 40 solo pasa cuando el total final resulta ser 41 o más, así que no dependas de eso. `sandbox/run.sh` falla porque la comprobación de la propia entrada espera 40.

La prueba de parada debe ir **primero** en la condición porque un `MATCHES` fallido borra todos los registros `CMAKE_MATCH_n` y uno exitoso los reescribe. La coincidencia *principal* debe ejecutarse al final para que sus capturas sobrevivan a la siguiente pasada.

## B6. APL: la reescritura con error de uno

1. `4↓` descarta solo el encabezado y *tres* líneas de genes. Por eso el cuerpo del hijo conserva el gen `T←H` del padre (el cuarto). Cada hijo reinicia su total acumulado con solo sus propias horas y `Alive←40≥T` siempre es 1. El programa recurre hasta agotar el tiempo:

   ```text
   Meetings    18    18    ...
   Coding    17    17    ...        <- total equals hours on every row
   ...
   TIMEOUT after 40s          (exit 124)
   ```

   En la computadora portátil usada para la nueva ejecución del 2026-11-16, la recursión llenó primero el límite de memoria de 2 GB del contenedor. Por eso la ejecución terminó con `Killed` (salida 137) tras unas 2,000 líneas, en vez de agotar el tiempo. En ambos casos nunca llega a `# committed`; cuál observas depende de la máquina.

   Por eso [`apl-weird/check.sh`](../src/apl-weird/check.sh) se ejecuta bajo `timeout`: este fallo es silencioso y estructural.
2. `⎕IO←1` produce un `INDEX ERROR` en `Card0[5]`, la línea `Show(⊃Categories[C])...`. `C` cuenta las categorías desde 0 (`C←0`, `4|C+1`), que es un índice válido solo con origen 0. No se imprime ninguna fila.

## B7. LINQ: enumera dos veces

El programa (también en [`solutions/b7-linq`](solutions/b7-linq)):

```csharp
var q = Enumerable.Range(1, 3).Select(i => { Console.WriteLine($"effect {i}"); return i; });
Console.WriteLine("-- (a) declared q");
Console.WriteLine("-- (b) q.Sum()");
_ = q.Sum();
Console.WriteLine("-- (c) q.Sum() and q.ToList()");
_ = q.Sum(); _ = q.ToList();
Console.WriteLine("-- (d) q.ToList() once, then sum the list");
var list = q.ToList(); _ = list.Sum();
var r = new Random(42);
Console.WriteLine(string.Join(" ", Enumerable.Range(0, 5).Select(_ => r.Next(10, 20))));
```

| Paso | Líneas de `effect` | Por qué |
| --- | --- | --- |
| (a) declarar | 0 | `Select` es **diferido**: construye una descripción, no un resultado. |
| (b) `Sum()` | 3 | La enumeración ejecuta la lambda una vez por elemento. |
| (c) `Sum()` y `ToList()` | 6 | Cada enumeración vuelve a ejecutar la canalización y cada efecto secundario que contiene. |
| (d) `ToList()` y luego sumar la lista | 3 | `ToList()` es inmediato y toma una instantánea de los valores; sumar una lista no vuelve a ejecutar nada. |

La semilla 42 da `16 11 11 15 11`. Un `System.Random` con una semilla fija es una secuencia determinista. El archivo `.xaml` crea `new Random(42)` sin otra entropía, así que cada ejecución produce las mismas tarjetas. El operador inmediato que fuerza la cola diferida en `LinqChallenge1` es el `.Aggregate(0, (count, _) => count + 1)` final. En `ModernChallenge1`, el `for` que lo contiene evalúa su condición en cada turno. `Sum()` consume la proyección diferida durante esa prueba de condición, antes de que la comparación pueda decidir si continúa.

## B8. Regex: qué sobrevive a una coincidencia fallida

- **.NET:** la cinta fija de solo 10 normalmente devuelve una coincidencia exitosa con cinco filas, total 50 y estado de salida 0. Al agregar `(?!)`, `Match.Success` es falso y la coincidencia fallida no expone capturas. El anfitrión sale con 1 después de imprimir y agregar un informe que contiene solo su encabezado y resumen.

  ```text
  match returned: false
  # captured total=0 entries=0 DEMO ONLY
  ```

  Por eso la entrada .NET debe *devolver true*, mientras que las entradas de Perl y PCRE2 pueden devolver false después de escribir todo. Su salida es un efecto secundario; la salida de `regex-dotnet` son las capturas.
- **pcre2grep:** `pcre2grep` inicia un programa de callout con `fork` y `execv`, que no busca en `PATH`. Un `sqlite3` sin más no logra iniciarse. El motor lo trata igual que un callout que devolvió un valor distinto de cero: una rama vetada. La ejecución no imprime **nada**, sale con 0 y no escribe filas.
- **Contraste (tres frases):** En Perl, las variables `local` se deshacen durante el retroceso, pero los `print` y `INSERT` ya ocurrieron, así que el trabajo sobrevive a una coincidencia fallida. En la entrada C de PCRE2, el estado vive en una estructura del anfitrión y el callout de finalización cierra el TSV antes del fallo deliberado. En la entrada .NET, el anfitrión no dispone de las capturas de una coincidencia fallida, así que su informe tiene cero filas de tarjetas.

## B9. sed: observa un cálculo

```bash
lessons/tools/run-in-sandbox.sh -e TRACE=1 src/regex-sed ./timecards.sh 2> trace.txt
grep -c 'tot:' trace.txt                  # e.g. 48 for a three-card run
grep -E 'tot:#{41}' trace.txt | tail -1   # the final state: 41+ tally marks
```

- El estado ocupa una línea, por ejemplo `run:... k:### rng:0110101000001111 cats:Coding,... tot: n: c:Meetings`; `tot:` crece con marcas de conteo (`#`). En la ejecución de verificación hay unas 16 líneas por tarjeta, pero **varía** debido al rechazo.
- [L29](../src/regex-sed/timecards.sed#L29), `/ rng:1(01|1)/b draw`, vuelve a sortear cuando el nibble de 4 bits es de 10 a 15. `1(01|1)` coincide con `101x` (10, 11) y `11xx` (12-15): son los valores que no puede usar un sorteo de 10 a 19 horas. Un sorteo rechazado repite los pasos del registro de desplazamiento. Por eso el número de líneas por tarjeta no es constante.

## B10. Lisp: cambia la combinación de métodos

1. Con `progn` en ambos lugares, cada ejecución reparte **las cinco tarjetas**, porque `progn` llama a todos los métodos aplicables e ignora sus valores de retorno:

   ```text
   Meetings	13	78	2026-W47	DEMO ONLY
   # committed total=78 entries=5 DEMO ONLY
   # PUNCH had 0 OR methods and 5 ran: the class precedence list is the loop, and OR is the stop rule
   ```

   Los totales terminan entre 50 y 95. El recuento de métodos dice `0 OR methods` porque la nota cuenta los métodos con el calificador `or` y ahora no hay ninguno. `check.sh` falla en tu copia porque exige `(:method-combination or)`. (La propia comprobación de la entrada sin modificar ejecuta esta misma mutación para demostrar que `or` es la regla de parada.)
2. Cambiar solo la función genérica deja cinco métodos con un calificador que `progn` no acepta. SBCL advierte:

   ```text
   WARNING:
      Invalid qualifiers for PROGN method combination in method
      #<STANDARD-METHOD TIMECARDS-WEIRD::PUNCH OR (CARD-5) ...>:
        (OR).
   ```

   Los calificadores de un método deben coincidir con la combinación de su función genérica: la función genérica elige la combinación, no el método.
3. Con `100` siempre hay cinco filas y un total de 95 como máximo. El programa se detiene porque **se queda sin clases**, no porque se cumplió la regla; `check-demo.sh out.txt 100` falla con `final total N does not pass 100`. Cinco es el máximo que puede repartir: las tarjetas son de al menos 10 horas, así que cuatro tarjetas suman como mínimo 40 y una quinta siempre pasa de 40. Un límite de 100 necesita once clases (diez tarjetas de 10 suman exactamente 100, así que una undécima debe superar ese total). Por eso agregarías formas `defcard` y volverías a numerar.
- **La regla de parada es `or`**, y el programa no falla sin ella porque `progn` es una combinación válida: el programa simplemente nunca se detiene antes. Un cambio silencioso de significado es todo el riesgo de la técnica.

## B11. m4: entrecomilla la recursión

1. Misma semilla, mismas tarjetas:

   ```text
   Meetings	19	19
   Coding	13	32
   Debugging	16	48
   ```

   Solo puede diferir el identificador de ejecución (`1794869456-12345`: el reloj y la semilla). El generador es la fórmula de Park-Miller y nada más aporta aleatoriedad. `ifdef([tc_seed], [], ...)` ([L34](../src/m4/timecards.m4#L34)) crea una semilla aleatoria solo si aún no has definido una.
2. Sin corchetes, `tc_card()` *se llama mientras se recopilan los argumentos de `ifelse`*, así que cada llamada hace otra antes de que `ifelse` pueda elegir algo. m4 expande los argumentos antes de ejecutar la macro. Con `SANDBOX_TIMEOUT=20` la ejecución termina por tiempo agotado (salida 124) y no imprime nada: m4 guarda su salida en un búfer y fue terminado antes de vaciarlo. Con `-L 50`:

   ```text
   m4:timecards.m4:87: recursion limit of 50 exceeded, use -L<N> to change it
   ```

   y estado de salida 1. Los corchetes convierten `tc_card()` en texto que solo se expande cuando `ifelse` lo devuelve, después de la prueba; esa es la única regla de parada del programa.
3. `eval(tc_total > 60)`: la ejecución se detiene en la primera tarjeta que hace que el total pase de 60. `check-demo.sh out.txt 60` pasa la comprobación.

## B12. Tcl: edita el programa en la base de datos

1. Con `recursive_triggers = OFF`, el primer `INSERT` activa el disparador una vez; el disparador inserta la tarjeta 2. **Esa** inserción no vuelve a activar el disparador, porque un disparador no se activa a sí mismo salvo que la recursión esté habilitada. Por eso se imprime la tarjeta 1 (mediante `tcl('born', ...)` en el disparador). La tarjeta 2 está en la base de datos, pero nunca se imprimió:

   ```text
   Meetings	17	17	2026-W47	DEMO ONLY
   # committed total=31 entries=2 DEMO ONLY
   ```

   `check-demo.sh` falla: "final total 17 does not pass 40", y la línea de resumen no coincide con la única fila.
2. El texto de la fila `hours` es el programa Tcl para los dados. Con `expr {10}` cada tarjeta tiene 10 horas:

   ```text
   Meetings	10	10
   Coding	10	20
   Debugging	10	30
   Learning	10	40
   Meetings	10	50
   # committed total=50 entries=5 DEMO ONLY
   ```

   La regla del disparador es `NEW.running_total <= 40`, así que un total de exactamente 40 continúa y se extrae otra tarjeta (por la misma razón que en A1). `check-demo.sh` pasa: cinco tarjetas de 10 horas son una ejecución válida.
- **Los tres ganchos:** `db function tcl call` (SQL llama a Tcl), la sustitución de `unknown` (la tabla es la biblioteca) y el disparador recursivo (el bucle). En el paso 2 cambiaste una fila que `unknown` recupera: el *programa* cambió sin editar una línea de Tcl.

## B13. AWK: el `RT` que falta

El archivo de dígitos es `1 2` seguido de un salto de línea. Con `RS="[0-9]"` los registros son: `""` termina en `1` (RT=1), `" "` termina en `2` (RT=2) y `"\n"` **no** tiene un dígito después (RT está vacío).

1. Los dados 1 y 2 dan 11 y 12 horas:

   ```text
   Meetings	11	11	2026-W47	DEMO ONLY
   Coding	12	23	2026-W47	DEMO ONLY
   # committed total=23 entries=2 DEMO ONLY
   ```

   La regla 1 omite el tercer registro: `RT == "" { next }`.
2. Sin la guarda, el tercer registro se reparte como los demás y `10 + RT` con un `RT` vacío es `10 + 0`: una tarjeta fantasma, `Debugging 10 33`, `entries=3`. También es un INSERT real.
3. mawk no tiene `RT`. La variable nunca recibe un valor, así que `RT == ""` es verdadero para **cada** registro. La regla 1 los omite todos, `t` nunca crece y `t > 40` nunca se activa:

   ```text
   # committed total=0 entries=0 DEMO ONLY
   ```

   Sin error, salida 0. En `/dev/urandom` el mismo programa nunca se detiene y mawk lee hasta quedarse sin memoria (verificado con un límite de 400 MB). Un programa que *parece* portable y no calcula nada sin avisar es peor que uno que falla. `RT` es una extensión de gawk (**permitido por la implementación**) fuera de POSIX.
4. `t > 80 { exit }`: la ejecución se detiene en la primera tarjeta que lleva el total a más de 80 y `check-demo.sh out.txt 80` pasa. El patrón *es* la regla de parada: `check.sh` hace el mismo cambio en un flujo de 5 para demostrarlo (tres tarjetas pasan a ser seis).

## B14. find: carga los dados

El `mktemp` falso produce los dados. El recorrido lee el último carácter de cada nombre de seis caracteres, con el patrón `-path '*/[!/][!/][!/][!/][!/][STUVWX]/?'`.

1. `xxxxxS` está en el grupo 9, así que cada tarjeta tiene 19 horas:

   ```text
   Meetings	19	19	2026-W47	DEMO ONLY
   Coding	19	38	2026-W47	DEMO ONLY
   Debugging	19	57	2026-W47	DEMO ONLY
   # committed total=57 entries=3 DEMO ONLY
   ```

   El primer total, 19, es la secuencia de dígitos 1 ... 9, 0 ... 9: la ruta tiene un directorio llamado `0` y el último dígito es 9. Después de la tercera tarjeta, la ruta tiene cinco de ellos. Por eso el dígito de las decenas es 5 y se activa la regla de parada.
2. `xxxxxY` termina en `Y`, que no es uno de los 60 caracteres válidos. Por eso el recorrido prueba el carácter anterior. Ese es `x`, en el grupo `stuvwx`: 13 horas. Los totales son 13, 26, 39 y 52. La regla de parada dice "más de 40" y 39 no cumple esa condición, así que se crea una cuarta tarjeta. Las categorías son `Meetings`, `Coding`, `Debugging`, `Learning`.
3. `xxxxYZ`: se descarta `Z` y también `Y`, que lo precede. La última rama de la tabla es la predeterminada: 10 horas. Los totales son 10, 20, 30, 40 y 50. La regla de parada es "cinco directorios llamados `0`, o cuatro de ellos y un último dígito distinto de `0`". Con 40, la ruta tiene cuatro de ellos y el último dígito es `0`, así que continúa. La quinta tarjeta es `Meetings` otra vez.

## B15. GNU find: mueve la regla de parada y lee el perfil

1. `([^/]*/){31}.*` coincide con una ruta con al menos 31 barras. El directorio inicial `t` está a profundidad 0 y el final de una tarjeta está a una profundidad igual al total acumulado. Por tanto, la prueba es verdadera exactamente cuando el total es 31 o más, es decir, "más de 30". `check-demo.sh out.txt 30` pasa. El propio `check.sh` de la entrada falla porque los siete escenarios con dados forzados (por ejemplo `10 10 10 10 10`, cinco tarjetas) ahora se detienen tras menos tarjetas. La regla de parada es ese número porque la profundidad es el total.
2. Con `FIND_D=rates`, find imprime su perfil en stderr después del recorrido. Cada prueba muestra `[est success rate 0.8]` (la estimación uniforme del optimizador) y `[real success rate a/b=...]`. La prueba `-name b00` tiene éxito una vez por tarjeta, así que `a` es igual al número de filas. La estimación es muy imprecisa porque el optimizador no sabe que la mayoría de los directorios se llaman `b..` y solo uno de cada 15 aproximadamente termina una tarjeta.

## B16. tar: lee el programa y luego ejecútalo

1. Se ejecutan cuatro tarjetas: 12, 24, 36 y 48. El total pasa de 40 en la cuarta tarjeta. Por eso, se leen e ignoran el quinto espacio (`050.card`) y los miembros `stop-over` posteriores a la parada. La tabla de traza muestra `ignored: halted` para ellos.
2. Cambiar `limit=40` por `limit=20` en `021.stop-over` hace que la parada ocurra después de la segunda tarjeta (24 es más de 20). Nada cambió en `dispatch.sh`: el límite es un dato en el archivo. `check-demo.sh out.txt 20` pasa la prueba. El orden importa: tar lee los miembros en el orden del archivo, así que volver a empaquetarlos en otro orden produce un programa distinto.
3. `inspect.sh` marca `025.exec` como `REFUSE (unknown record type)` y sale con 4. `interpret.sh --execute` consulta primero al inspector, así que sale con 4, imprime que no se ejecutó nada y no inicia tar. No aparece `pwned`. Un `tar -xf` sin más escribe `025.exec` como archivo inerte y no ejecuta nada, porque un archivo no puede registrar un hook para sí mismo. El **análisis sintáctico** lo realizaron `tar -t` y `tar -xO` dentro de `inspect.sh`, y tar otra vez dentro de `interpret.sh`. La **ejecución** ocurrió solo en `interpret.sh --execute`, en `tar --to-command`. La frontera de confianza es la línea de comandos que escribió el operador.

## B17. tar, más raro: predice el reloj

1. Con 45 tics la máquina alcanza 45 horas de trabajo, pero la tercera tarjeta necesita el tic 46. Imprime las dos tarjetas cerradas (`Meetings 12 12`, `Coding 17 29`), informa `the clock ran out` y sale con 3. Con 46 tics termina: tres tarjetas, total 46, salida 0.
2. `--ticks 92 --interval 2`: 92 registros, una función de devolución de llamada cada dos registros, así que hay 46 funciones de devolución de llamada y la ejecución termina. `--ticks 91`: 45 funciones de devolución de llamada y se atasca. `TAR_CHECKPOINT` es el número de registro, así que el último valor de la ejecución terminada es 92 y `fsm.tick` lo muestra. La máquina ha contado 46 horas. El script de comprobación lo expresa así: último `TAR_CHECKPOINT` = tics x K.
3. 260 bloques con `-b 4` son 65 registros, así que hay `floor(65 / 1) = 65` tics. Las mismas tres tarjetas, un total de 46 y 65 - 46 = 19 tics inactivos. La cinta tiene 65 × 2,048 = 133,120 bytes.
4. La carga útil son ceros y los únicos otros bytes son los de la cabecera del miembro (un nombre y algunos números; 74 bytes distintos de cero en la ejecución de prueba). Nada lee el contenido por su significado. Solo cuenta el tamaño, porque decide cuántos registros escribe tar.

## B18. ed: mueve la regla de parada y rompe la limpieza

1. `DICE="0 0 0 0 0"`: cinco tarjetas de 10 horas, totales 10, 20, 30, 40, 50. La ejecución continúa en 40, porque 40 no es más de 40. La quinta tarjeta recibe la categoría de la línea 5, `Meetings` (la lista de categorías es Meetings, Coding, Debugging, Learning, Meetings). `DICE="9 9 9 9 9"`: tres tarjetas de 19 horas, 19, 38, 57.
2. `DICE="3 3 3 3 3"` son 13 horas por tarjeta. Con `x\{41,\}`: 13, 26, 39, 52, cuatro tarjetas. Con `x\{31,\}`: 13, 26, 39, tres tarjetas, porque 39 es más de 30 y la barra se convierte en un signo de exclamación. `check-demo.sh out.txt 30` pasa la prueba. La regla de parada es la expresión regular sobre las marcas.
3. La salida tiene una quinta línea, `Dead 0 52`. En la tarjeta 4 el total es 52, así que la línea del libro de registro tiene un `!`. La tarjeta 5 se une a ella, la regla Dead reescribe la línea unida como `Dead 0!` más las marcas y las reglas decimales imprimen el total. Con la limpieza activa `g/^Dead /d` la elimina. **Características:** el paso 1 es la tabla de reescritura y el direccionamiento (una cantidad distinta de marcas); el paso 2 es un intervalo de expresión regular; el paso 3 es `g` con `d`.

## B19. Ex: mueve el límite en la cinta y corta el bucle

1. `DICE="1 1 1 1 1"` son once horas por tarjeta: totales 11, 22, 33, 44. Después de la tarjeta 4 la marca está en la fila 44 de la cinta, cuya instrucción es el comentario. Por eso termina la ejecución. Cuatro tarjetas.
2. Al cambiar las filas de 41 a 45 de `"` a `@a`, la fila 44 ahora continúa. La quinta tarjeta lleva el total a 55, que es la fila 55: sigue siendo un comentario. Cinco tarjetas: 11, 22, 33, 44, 55. `check-demo.sh out.txt 45` pasa la prueba. Una edición de datos movió la regla de parada.
3. Sin el `|@n` final el programa termina después de una tarjeta: `Meetings 15 15` para `DICE="5 5 5 5 5"`. Nada inicia el programa de nuevo.
4. El bucle es `@n`, el último comando de la línea del programa. El registro `n` contiene el texto de la línea de la cinta, menos el total. Se detiene en la primera fila cuyo texto es `"` (la fila correspondiente a 41). El límite de 40 no está en ninguna parte del programa: es la frontera en la cinta.

## B20. JavaScript: lee las cláusulas, mueve el límite y haz fallar la comprobación de estructura

1. `SEED=42` da las horas 12, 17 y 17: totales de 12, 29 y 46. La tercera tarjeta pasa de 40 y se conserva. La primera prueba ve 0, la segunda 12, la tercera 29 (todos 40 o menos) y la cuarta ve 46 y se detiene.
2. Con `<= 20`: la prueba ve 0 y 12 (continúa) y luego 29 (más de 20), así que son dos tarjetas: 12 y 29. La tarjeta que pasa el límite es la segunda.
3. La sentencia adicional es JavaScript válido y el programa se ejecuta. `check-structure.mjs` informa `FAIL: the body must be empty`. Esa es la prueba de que se comprueba la regla del truco y no solo se afirma.
4. 2026-12-31 es jueves y 2026 empieza en jueves, así que tiene 53 semanas: `2026-W53`. 2024-12-30 es lunes, en la semana cuyo jueves es 2025-01-02, así que es `2025-W01`.

## B21. JavaScript, más raro: mueve la regla de parada en una clausura y observa la demanda

1. Pasan 12 pruebas.
2. Con `over = total > 20` y `SEED=42` los totales son 12 y 29, así que la máquina termina después de la segunda tarjeta: dos tarjetas. El laboratorio muestra entonces 7 fallos y 5 pruebas que pasan. Los fallos son las pruebas que usan el número 40 o las tres tarjetas iniciales: la tarjeta que pasa el límite, exactamente 40, el recuento de extracciones, la repetición y otras similares. Las cinco pruebas que pasan (dos entornos, `map` diferido frente a inmediato, vida de la clausura, clausura frente a `this` y clausura frente a continuación) tratan de cómo se comportan las clausuras, no de cuándo se detiene esta máquina. Las reglas de una clausura no dependen de su propósito.
3. `built`, `drawn`, `[ 15 ]`. La canalización es solo una descripción hasta que `toArray()` pide un valor. `take(1)` se detiene después de un valor, así que se consulta la máquina una vez y se llama una vez a la fuente de horas.
4. `take(2)` imprime `drawn` dos veces y luego `[ 15, 30 ]`: el total de la máquina es 15 después de la primera tarjeta y 30 después de la segunda.

## B22. JavaScript, dirigido por eventos: predice la traza y luego quita el límite

1. Pasan 14 pruebas.
2. `listener`, `after emit`, `immediate`. `emit` es una llamada normal: ejecuta sus dos escuchadores de eventos en la pila de llamadas y luego regresa. `setImmediate` pone la función en la cola del bucle de eventos. Node la ejecuta después del código actual, aquí después del último `console.log`.
3. `>start`, `<start`, `main is done` y luego un turno por tarjeta. Un turno empieza con `>generate` y anida dentro `card-created`, `card-saved` y `total-updated`. Por eso, cada `>` se cierra con su `<` en orden inverso. En el tercer turno, `total-updated` encuentra que el total (57) pasa de 40 y emite `finished`, que emite `done`: `>finished >done <done <finished` queda dentro de `total-updated`. `<start` aparece antes del primer `>generate`: `start` pidió la primera tarjeta con `setImmediate`, así que la tarjeta se crea en un turno posterior.
4. Sin `later`, `total-updated` llama a `generate` dentro de sí mismo y la pila nunca se desenrolla entre tarjetas. 40 horas son tres o cuatro tarjetas, así que una ejecución normal funciona bien y las tarjetas son las mismas. El laboratorio muestra 12 pruebas aprobadas y 2 fallos. La prueba de la traza no pasa porque ahora cada `generate` queda dentro del `total-updated` anterior y no en su propio turno. Tampoco pasa la prueba de profundidad de la pila porque la pila es más profunda en cada tarjeta. El escaneo encuentra `emit('generate'` y no pasa. Con `limit: 10_000_000`, la pila se agota después de unos miles de tarjetas. Un `RangeError` va al escuchador de eventos `failed` y este imprime una línea, `timecards: Maximum call stack size exceeded`, con estado 1. Con el límite restablecido y `limit: 30_000`, la misma llamada es plana y termina con estado 0.

## C1. Lo raro junto a lo aburrido

Medido con el script de verificación (líneas que no son comentarios):

| Par | Idiomático | Raro |
| --- | --- | --- |
| COBOL | 156 | 170 |
| Haskell | 91 | 108 |
| Forth | 97 | 84 |
| APL | 41 | 47 |
| Lisp | 150 | 110 |
| Tcl | 138 | 118 |
| AWK | 85 | 41 |

Ejemplo de comparación para Haskell: `timecards` idiomático es una **función pura** (`span`). Por eso, una prueba unitaria no necesita una base de datos y un depurador muestra listas simples. La versión rara no se puede probar sin ejecutar sus efectos y el orden de los efectos depende del consumidor. Pero puede hacer algo que la idiomática no puede: *escribir cada fila justo cuando se solicita esa tarjeta por primera vez*, sin un bucle ni un acumulador en el programa. Es la elección adecuada para una biblioteca de flujo de datos con evaluación diferida o una demostración didáctica, no para código de aplicación.

Forth es la excepción instructiva: la versión rara es *más corta* porque elimina las `variable` y la palabra que las actualiza, a cambio de disciplina de pila.

Lisp, Tcl y AWK también resultan más cortos en la versión rara, pero sobre todo porque las versiones raras *hacen menos*, no porque la pirueta sea más compacta. `lisp` calcula la semana ISO por sí mismo (aritmética de calendario, más un argumento de fecha opcional y una estructura `card`), mientras `lisp-weird` solo consulta a `date`. `tcl` tiene un espacio de nombres con procedimientos separados para `draw`, `save`, `row` y ventanas, mientras `tcl-weird` tiene dos procedimientos y algo de SQL. `awk` tiene seis funciones auxiliares, mientras `awk-weird` no tiene ninguna. El recuento de líneas mide lo que lleva cada programa, no lo difícil que es entenderlo (las entradas raras ponen la dificultad en comentarios y README). Los recuentos incluyen líneas vacías y excluyen líneas que solo contienen comentarios.

## C2. Haz real la restricción

Una comprobación de referencia, [`solutions/c2-forth-rule-check.sh`](solutions/c2-forth-rule-check.sh):

```bash
code=$(tr -d '\r' < "$f" | sed -E -e 's/(^|[[:space:]])[\]([[:space:]].*)?$//' \
                                  -e 's/[(][^)]*[)]//g' -e 's/[.]"[^"]*"//g')   # strip \ comments, ( ) comments, ." strings
grep -Eiqw 'begin|until|while|repeat|again|if|then|else|do|loop|case|of|recurse|exit|leave' <<<"$code" && fail
grep -Eiqw 'variable|buffer:' <<<"$code" && fail
(( $(grep -o '>in @' <<<"$code" | wc -l) >= 2 )) || fail
```

Al ejecutarse con el archivo real imprime `OK: no control words, no variables, >in @ x3`. Las tres mutaciones (verificadas):

```bash
sed 's/^drop /begin drop /'              timecards.fs > m1.fs   # FAIL: banned control word: begin
sed 's/^utime drop/variable v utime drop/' timecards.fs > m2.fs # FAIL: a variable is declared
sed 's/>in @/0/g'                         timecards.fs > m3.fs  # FAIL: >in @ appears 0 time(s)
```

Un `begin if until` situado después de un `\` en una línea se elimina primero, así que no lo activa.

## C3. Un bucle cuyo estado no es una variable

```bash
seq 10 | awk '{ print ++c }'          # prints 1..10
```

El bucle es el **bucle principal implícito** de awk: ejecuta la regla una vez por cada registro de entrada de datos. El estado ("cuántas veces") vive en el *flujo de entrada de datos*, que controla quien llama (`seq N` proporciona N registros). `c` solo cuenta. No aparece `for`, `while`, `do`, `function` ni `goto`. Verificado para N = 1, 3, 10. Nivel de conocimiento: **garantizado**: POSIX define el modelo de procesamiento de registros.

## D. Adaptación del reto

Una respuesta de referencia completa en awk está en [`solutions/awk-port`](solutions/awk-port): `timecards.awk`, un `Dockerfile` y un `check.sh`. Ejecútala:

```bash
sandbox/container/run-image.sh lessons/solutions/awk-port   # build and run, shows the rows and the SQLite table
sandbox/run.sh lessons/solutions/awk-port                   # its own check: 25 runs
```

Cómo cumple los criterios:

| Criterio | Cómo |
| --- | --- |
| La regla de parada es el truco | `total <= 40 { ... }` es un *patrón*; los cinco registros vienen de `seq 5` y, cuando el total pasa de 40, ningún registro posterior coincide. Cinco registros siempre bastan (5 × 10 ≥ 50). |
| Se aplica DEMO ONLY | `CHECK(demo_only = 1)` en la tabla; `check.sh` intenta insertar `demo_only = 0` y falla si se acepta. |
| 25 ejecuciones, horas variadas | `check.sh` ejecuta un bucle 25 veces y compara las filas impresas con la línea `# committed` y el recuento de filas de SQLite. Exige al menos 5 valores distintos de horas. |
| La restricción es real | `check.sh` elimina comentarios y cadenas de texto y falla ante `for`, `while`, `do`, `function`, `func` o `goto`. |

Mutaciones verificadas: añadir un bucle `for` hace que falle la comprobación; hacer constantes las horas (`hours = 10`) hace que falle (menos de cinco valores distintos de horas).

## E1. Ejecuta y lee la evidencia (Windows Sandbox)

```powershell
sandbox\windows\run.ps1 src\LinqChallenge1
sandbox\windows\run.ps1 src\xaml -RunArgs strict.xaml
```

Aspectos destacados de la salida verificada:

```text
network: blocked
OK: no orchestration helper, build clean, one run persisted exactly 40.0h across 5 fixed rows, and the process exited on its own
PASS LinqChallenge1 (check.ps1 exited 0)
...
wrote: C:\work\xaml\data\xaml-demo-timecards.xml (607 bytes)
screenshot: ...\out\screenshot.png
PASS xaml (still running with a window after 20s; closed cleanly by the harness)
```

Entradas con datos fijos: las de LINQ siempre tienen un total de exactamente 40 horas (una semana laboral fija). Aleatorias: `ModernChallenge1` y todas las demás entradas; `xaml` usa aleatoriedad *con semilla* (`Random(42)`), así que es igual en cada ejecución. Necesita el SDK de .NET 10 en el anfitrión.

## E2. Cambia la semilla del intérprete de XAML

Al reemplazar `<sys:Int32>42</sys:Int32>` por `7` en `strict.xaml` y ejecutarlo en Windows Sandbox, la prueba aún pasa (el arnés muestra y cierra la ventana). El entorno aislado no imprime las horas, así que léelas con el programa B7: la semilla 42 da `16 11 11 15 11`; `new Random(7)` da una secuencia distinta. La misma semilla siempre da la misma secuencia porque `System.Random` es determinista para una semilla dada.

"La variable" es el recurso `<sys:Random x:Key="rnd">` más los **arreglos portadores**: cada llamada `ObjectDataProvider` llena un `char[]`/`byte[]` in situ y la siguiente lo lee. El bucle está desenrollado (cuatro pasadas copiadas, según el [README](../src/xaml/README.md)) porque XAML no tiene una construcción de bucle. El archivo necesita una copia de la secuencia de sorteo y almacenamiento por tarjeta.

## F. Demuestra una afirmación del README

Afirmación de [`src/haskell/README.md`](../src/haskell/README.md): "`takeWhile` no basta: `takeWhile (<= 40)` descarta la tarjeta que cruza el límite y el reto la necesita. `span` devuelve ambas mitades."

[`solutions/f-takewhile.hs`](solutions/f-takewhile.hs):

```haskell
main :: IO ()
main = do
  let totals = scanl1 (+) [15, 11, 12, 11] :: [Int]            -- 15, 26, 38, 49
  putStrLn ("takeWhile: " ++ show (takeWhile (<= 40) totals))
  let (under, over) = span (<= 40) totals
  putStrLn ("span: " ++ show (under ++ take 1 over))
```

```bash
lessons/tools/run-in-sandbox.sh lessons/solutions runghc f-takewhile.hs
# takeWhile: [15,26,38]          <- the crossing total, 49, is dropped
# span: [15,26,38,49]            <- kept
```

Control negativo: cambia el límite a `<= 50` y `takeWhile` devuelve los cuatro totales. **Etiqueta: garantizado**, porque ambas funciones están especificadas por el `Prelude` de Haskell y tu prueba no depende de la implementación.

## F2. Trojan Source: oculta un carácter y luego encuéntralo

1. `node greet.js` imprime `false`. La primera línea contiene `"admin"` seguido de U+200B, un carácter sin forma. Por eso la cadena de texto tiene cinco letras visibles (`a d m i n`) y un carácter invisible: no es igual a `"admin"`. La segunda línea la compara con la palabra simple. Un lector que ve `user === "admin"` espera `true`.
2. El escaneo imprime la línea 1, `1:const user = "admin";`. Hay otro carácter entre `n` y la comilla de cierre que tu terminal dibuja como si no hubiera nada (esa es la idea). `od -c` muestra `a d m i n 342 200 213 "`: UTF-8 para U+200B son los tres bytes E2 80 8B, que son `342 200 213` en octal.
3. `clean.js` no encuentra coincidencias e imprime `true`. El escaneo se activa con ese carácter y con nada más.
4. Ningún archivo en `src/apl-weird` tiene una coincidencia. Los glifos de APL son visibles, así que una persona revisora los ve. Prohibir todos los caracteres no ASCII también prohibiría APL y todos los nombres que no estén en inglés. Tampoco detendría a un atacante que use un carácter ASCII de aspecto similar. La defensa consiste en prohibir lo que no tiene forma visible. La etiqueta es **permitido por la implementación**: la regla está escrita (`sandbox/scope-check.sh`, la línea que establece `hidden=`). Su mecanismo es `grep -P` y sus tablas Unicode. La clase de caracteres enumera solo los caracteres que conocemos. Por eso, un nuevo carácter invisible en una versión futura de Unicode no se detectaría hasta actualizar la lista.

## G. Retos abiertos

No hay respuestas: estos retos no están resueltos. Si resuelves uno, envíalo.
