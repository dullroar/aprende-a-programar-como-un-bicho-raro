---
title: "Entorno aislado"
chapter: 1
order: 30
applies-to: all
applies-because: "Cada entrada documenta un comando para un contenedor de Linux o para Windows Sandbox. Si una entrada incluye un script de comprobación, consulta su README para saber cómo ejecutar las comprobaciones."
---
Un entorno aislado (*sandbox*) es un espacio que limita el acceso al sistema anfitrión. Allí puedes ejecutar código en el que no confías. El código recibe un espacio pequeño y cercado: poca memoria, sin red y sin acceso a tus archivos. Existe porque "lee primero cada línea" no funciona a gran escala y porque un programa astuto puede ocultar lo que hace. Aquí todas las entradas se ejecutan en uno. El entorno aislado de Linux no tiene red, usa un sistema de solo lectura y ejecuta el código con un usuario sin privilegios. Las entradas de Windows usan Windows Sandbox. Consulta [`SANDBOX-SETUP.md`](../../SANDBOX-SETUP.md).

- **Úsalo cuando:** ejecutes código que no escribiste o código que procese una entrada de datos que no escribiste.
- **Evita confiar a ciegas:** los entornos aislados tienen bichos que permiten escapar y no pueden proteger los datos que les das o que sacas de ellos. Usa el entorno como una capa entre varias (*defensa en profundidad*) y lee el código de todos modos.

**Lee más:**

- [Entorno aislado (seguridad informática)](https://en.wikipedia.org/wiki/Sandbox_(computer_security)) (Wikipedia)
- [Virtualización a nivel del sistema operativo](https://en.wikipedia.org/wiki/Operating-system-level_virtualization), la idea detrás de los contenedores (Wikipedia)
