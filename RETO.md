# Ven a crear algo bellamente erróneo

**Una sentencia, dos puntos y coma** es un reto de algoritmos ofuscados: toma un programa pequeño y corriente, impón una regla sintáctica absurda y haz que funcione de todos modos. No basta con que compile. Tiene que funcionar.

Lo que empezó en C# se ha escapado a Rust, XAML en tiempo de ejecución, Java, Kotlin, Python y Go. Hay cuatro variedades de regex ejecutable: regex de código en línea de Perl, regex con callouts de PCRE2, callouts estándar de `pcre2grep` y grupos de equilibrio de .NET. Trae un lenguaje, una restricción o una característica que se use para algo que su diseñador desaconsejaría con cortesía.

## El reto compartido

Con el sabor particular de mal juicio de tu lenguaje:

- genera tarjetas de horas ficticias, de 10 a 19 horas cada una, para Meetings, Coding, Debugging o Learning;
- sigue añadiéndolas hasta que el total acumulado pase de 40;
- mantén toda la salida en local, claramente marcada como **DEMO ONLY**, y completamente separada del reporte real de horas; y
- muestra el resultado en una ventana, un navegador, una terminal o lo que tenga más sentido.

El mecanismo es tuyo. La familia `for` usa un bucle sin cuerpo. Rust retuerce iteradores y clausuras (*closures*: funciones que recuerdan las variables de donde se crearon) hasta darles forma. XAML convierte el análisis sintáctico en ejecución. Las entradas de regex hacen que la coincidencia, el retroceso, los callouts o las pilas de captura hagan el trabajo pesado. Conserva el comportamiento y luego busca la manera más gloriosamente inapropiada que tu lenguaje te permita para expresarlo.

## Qué hacer y qué no

**Haz** que los efectos secundarios carguen con peso real cuando el lenguaje lo permita. Apóyate en la reflexión, la interpretación, la metaprogramación, el análisis sintáctico, la maquinaria de ejecución u otra rareza nativa, en lugar de la mera sintaxis. Un anfitrión diminuto que siembra datos, lanza una operación o informa un resultado es válido. El trabajo interesante debe pertenecer visiblemente a la acrobacia.

**No** escondas una solución normal detrás de una expresión ingeniosa que llame a `RunEverything()` (o a su equivalente local). Mover los bucles, los condicionales y la orquestación a otro método, script o archivo no es una adaptación: es un cambio de disfraz. Y esto no es un patrón de producción: nada de datos reales, nada de sistemas en red y nada de fingir que lo ilegible es una virtud fuera del juego.

## Puntos extra

- Deja `main` casi vacío, o conviértelo en el lanzador de una idea todavía peor.
- Pon el flujo de control donde no corresponde: un analizador sintáctico, un iterador, un motor de regex, un documento de marcado, un sistema de tipos o una herramienta de compilación.
- Haz que el retroceso haga todo el trabajo y luego devuelve a propósito "sin coincidencia".
- Construye o anima una interfaz de usuario en tiempo de ejecución sin el cableado convencional de manejadores de eventos.
- Añade una prueba que demuestre que la restricción ridícula es real de verdad.
- Si el lenguaje choca con un muro genuino, documéntalo con precisión. Una limitación bien demostrada es más interesante que hacer trampa para esquivarla.

Haz que funcione. Haz que sea raro.

Y pase lo que pase, no se lo cuentes al jefe.
