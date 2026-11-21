---
title: "Búsqueda con regex, efectos secundarios y fallo deliberado"
order: 60
---
[[entry:regex-perl]], [[entry:regex-pcre2]] y [[entry:regex-pcre2grep]] usan una sola coincidencia para activar funciones de devolución de llamada (*callbacks*) o código incrustado. Las acciones construyen el resultado fuera del motor de coincidencias. Cada patrón acaba forzando que la coincidencia falle, y las escrituras ya hechas pueden sobrevivir a ese fallo. Las variables locales de Perl se deshacen con el retroceso, mientras que los callouts de PCRE2 guardan su estado en el anfitrión de C o en ayudantes externos.
