---
title: "Denegación de servicio mediante expresiones regulares"
chapter: 8
order: 70
---
ReDoS (denegación de servicio mediante expresiones regulares) es un ataque que envía una entrada de datos con la que un motor de expresiones regulares con retroceso tarda un tiempo exponencial o muy largo. Un patrón como `(a+)+$` funciona bien con la mayoría de las cadenas de texto y pésimo con una secuencia larga de caracteres `a` seguida de `!`. El ataque existe porque un motor de retroceso prueba todas las formas de hallar una coincidencia antes de rendirse. Esto ha causado interrupciones reales: una expresión regular en una regla de un cortafuegos web tumbó Cloudflare en 2019. Otra, que buscaba espacios en blanco, ralentizó Stack Overflow en 2016. Las medidas de mitigación son sencillas: usa un motor que halle coincidencias en tiempo lineal (RE2, `regex` de Rust o la opción `NonBacktracking` de .NET). Fija un tiempo máximo para hallar una coincidencia y limita la longitud de la entrada.

- **Aplica este conocimiento cuando:** cualquier expresión regular procese datos que tú no controlas.
- **Evítalo cuando:** un patrón con solapamientos tenga cuantificadores anidados o un usuario envíe un patrón sin revisar.

**Lee más:**

- [Denegación de servicio mediante una expresión regular](https://en.wikipedia.org/wiki/Regular_expression_denial_of_service) (Wikipedia)
- [Ataque de complejidad algorítmica](https://en.wikipedia.org/wiki/Algorithmic_complexity_attack) (Wikipedia)
- [Denegación de servicio mediante una expresión regular: ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) (OWASP)
