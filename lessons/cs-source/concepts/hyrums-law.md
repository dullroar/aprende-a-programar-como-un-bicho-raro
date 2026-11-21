---
title: "Ley de Hyrum"
chapter: 8
order: 50
---
La ley de Hyrum dice que, si una interfaz tiene suficientes usuarios, alguien dependerá de *cada* comportamiento observable, sin importar lo que prometa la documentación. Hyrum Wright, ingeniero de software en Google, formuló esta observación. La ley explica la tercera etiqueta del libro, **aprovechado por accidente**. GNU Make documenta que se reinicia después de rehacer un makefile incluido. Nunca prometió que pudieras usar ese comportamiento como bucle. Cuando no hay coincidencia, `MATCHES` de CMake borra todas las variables `CMAKE_MATCH`. Es un comportamiento observado, sin garantía. Las entradas se apoyan en ambos comportamientos. Los mantenedores también conocen la ley. Go, por ejemplo, cambia al azar el orden de iteración de los mapas para que nadie dependa de él.

- **Úsala cuando:** cambies una biblioteca (alguien depende del comportamiento anterior) o decidas si puedes depender de un comportamiento sin documentar (anótalo y agrega una prueba).
- **Evítala cuando:** el código del que otros dependen necesite un comportamiento que nadie prometió.

**Lee más:**

- [Ley de Hyrum](https://en.wikipedia.org/wiki/Hyrum%27s_law) (Wikipedia)
- [Compatibilidad con versiones anteriores](https://en.wikipedia.org/wiki/Backward_compatibility) (Wikipedia)
