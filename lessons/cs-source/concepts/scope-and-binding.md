---
title: "Ámbito y enlace de nombres"
chapter: 6
order: 40
---
El *ámbito* es la parte de un programa donde un nombre es visible. El *enlace* es la asociación entre un nombre y un valor. La mayoría de los lenguajes usa el ámbito *léxico*: el significado de un nombre depende de dónde está escrito. Algunos usan el ámbito *dinámico*: el nombre significa lo que le asignó el invocador más reciente. El ámbito dinámico puede ser útil y también peligroso. En [[entry:apl-weird]] permitiría que una función reescrita sobrescribiera las variables de su función padre. Por eso cada encabezado generado vuelve a declarar sus variables locales. En Tcl, `uplevel` ejecuta código en el ámbito de otro marco de pila. [[entry:tcl-weird]] usa `uplevel #0`, que indica el ámbito global. En m4 y Make todos los nombres son globales.

```mermaid
flowchart TB
    accTitle: El ámbito fija dónde se busca un nombre. El enlace es el valor al que remite el nombre
    accDescr: Dos recuadros anidados. El ámbito exterior enlaza x con 10 e y con 20. El ámbito interior, dibujado dentro del exterior, enlaza x con 99. La expresión x más y se evalúa en el ámbito interior. La búsqueda de x encuentra primero x igual a 99 en el ámbito interior. Esa x oculta la del ámbito exterior. La búsqueda de y no encuentra nada en el ámbito interior, así que sigue hacia afuera y encuentra y igual a 20. El resultado es 99 más 20, que da 119.
    subgraph OUT["Ámbito exterior"]
        direction TB
        ox["x = 10 (oculta)"] ~~~ oy["y = 20"]
        subgraph INN["Ámbito interior"]
            direction TB
            ix["x = 99"] ~~~ use["x + y = 99 + 20 = 119"]
        end
    end
    use -->|"x: aparece primero aquí"| ix
    use -->|"y: busca afuera"| oy
```

La búsqueda de un nombre empieza en el ámbito más interno y sigue hacia afuera. Aquí la búsqueda encuentra `x` de inmediato en el ámbito interior. Ese enlace *oculta* el `x = 10` exterior. El nombre `y` no tiene enlace en el ámbito interior, así que la búsqueda sigue hacia afuera. El ámbito decide dónde buscar y el enlace es lo que la búsqueda encuentra. El dibujo muestra el ámbito léxico: los recuadros representan cómo se anida el texto fuente.

- **Usa el ámbito léxico** casi siempre. Te permite leer una función sin saber quién la llama.
- **Evítalo cuando:** un nombre necesite un ámbito dinámico o global sin un motivo deliberado y documentado.

**Lee más:**

- [Ámbito (programación informática)](https://en.wikipedia.org/wiki/Scope_(computer_programming)) (Wikipedia)
- [Enlace de nombres](https://en.wikipedia.org/wiki/Name_binding) (Wikipedia)
- [Clausura (programación informática)](https://en.wikipedia.org/wiki/Closure_(computer_programming)) (Wikipedia)
- [Ámbito](https://developer.mozilla.org/en-US/docs/Glossary/Scope) (glosario de MDN)
