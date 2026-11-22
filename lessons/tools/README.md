# Herramientas

| Script | Qué hace |
| --- | --- |
| [`check-demo.sh`](check-demo.sh) | Comprueba la *forma* de la salida de cualquier entrada: la marca `DEMO ONLY`, las horas 10-19, los totales acumulados, la parada en la tarjeta correcta y la coincidencia de la línea de resumen. Es la prueba de aceptación que usan casi todos los [ejercicios](../exercises.md). |
| [`run-in-sandbox.sh`](run-in-sandbox.sh) | Ejecuta cualquier comando en el contenedor de herramientas bloqueado del repositorio, sobre una copia privada de una carpeta, con `-e NAME=VALUE` opcional. |
| [`verify-exercises.sh`](verify-exercises.sh) | Ejecuta la solución de referencia de cada ejercicio de Docker e imprime PASS o FAIL para cada uno. Así se comprobó la [clave de respuestas](../respuestas.md). |
| [`verify-windows.ps1`](verify-windows.ps1) | Lo mismo para los ejercicios del entorno aislado (*sandbox*) de Windows (E1, E2). |

Las respuestas de referencia que son programas reales están en [`../solutions/`](../solutions).
