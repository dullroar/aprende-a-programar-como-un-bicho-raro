---
title: "Trojan Source: caracteres que no puedes ver"
chapter: 1
order: 60
exercise: "exercises.md#f2-trojan-source-hide-a-character-then-find-it-verified"
---
Trojan Source es un ataque contra la persona que revisa. Unicode incluye caracteres que no puedes ver: espacios de ancho cero y controles "bidireccionales" que cambian el orden visual del texto. Un código puede *parecer* inofensivo para una persona y *significar* otra cosa para el compilador. Investigadores de Cambridge describieron el ataque en 2021 (CVE-2021-42574). Este repositorio se defiende de forma sencilla: `sandbox/scope-check.sh` rechaza los caracteres ocultos y los que cambian la dirección en una solicitud de cambios. El Unicode visible no da problemas. APL necesita `⍴` y `⍳`.

- **Usa la defensa cuando:** aceptes código de otras personas. Busca caracteres invisibles de forma automática.
- **Evita corregir de más:** no prohíbas todo el texto que no sea ASCII. Prohíbe los caracteres que no tienen forma visible.

**Más información:**

- [Trojan Source](https://en.wikipedia.org/wiki/Trojan_Source) (Wikipedia)
- [Texto bidireccional](https://en.wikipedia.org/wiki/Bidirectional_text) (Wikipedia)
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629), la codificación que transporta todo este texto
