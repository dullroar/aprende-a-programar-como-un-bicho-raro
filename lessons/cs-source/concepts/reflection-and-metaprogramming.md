---
title: "Reflexión y metaprogramación"
chapter: 6
order: 60
---
La *reflexión* permite que un programa examine o cambie su propia estructura mientras se ejecuta. Puede buscar un tipo por su nombre, listar métodos y llamar a uno. La *metaprogramación* permite que un programa escriba o transforme programas. Existen porque los marcos de trabajo las necesitan. Los serializadores, los ejecutores de pruebas, la inyección de dependencias y los sistemas de complementos encuentran código que nunca han visto. XAML funciona por reflexión: un nombre de tipo en el marcado se convierte en un objeto. El protocolo de metaobjetos de Common Lisp permite que [[entry:lisp-weird]] consulte qué métodos se aplican a una llamada. El costo es que las herramientas y los optimizadores no pueden ver qué ocurre por dentro. Un nombre que proviene de los datos puede dar pie a un ataque.

- **Úsalas cuando:** debas buscar código por nombre en los límites de un marco de trabajo.
- **Evítalas en la lógica de negocio.** Si los nombres vienen de fuera, acepta solo los de una lista explícita.

**Lee más:**

- [Programación reflexiva](https://en.wikipedia.org/wiki/Reflective_programming) (Wikipedia)
- [Metaprogramación](https://en.wikipedia.org/wiki/Metaprogramming) (Wikipedia)
- [Metaobjeto](https://en.wikipedia.org/wiki/Metaobject) (Wikipedia)
