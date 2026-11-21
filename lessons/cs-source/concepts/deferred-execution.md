---
title: "Ejecución diferida"
chapter: 4
order: 50
---
Con la ejecución diferida describes ahora una consulta o una canalización. La consulta o la canalización se ejecuta más tarde, cuando alguien pide los resultados. En LINQ de C#, `Where` y `Select` no hacen ningún trabajo por sí solos. El trabajo ocurre cuando `foreach`, `ToList` o `Aggregate` lee la secuencia. Así puedes combinar canalizaciones con poco costo y un proveedor (como Entity Framework) puede traducir la consulta completa a SQL. Sí que hay sorpresas. La consulta se ejecuta *de nuevo* en cada lectura. Sus efectos ocurren tarde y para entonces una variable que captura puede haber cambiado. [[entry:LinqChallenge1]] y [[entry:LinqChallenge2]] ponen efectos dentro de la canalización a propósito. Un operador final de evaluación inmediata fuerza su ejecución.

- **Úsala cuando:** armes consultas y transformaciones sin efectos.
- **Evítala cuando:** una etapa tenga efectos secundarios. Decide quién fuerza la ejecución de la canalización y cuándo.

**Lee más:**

- [Consulta integrada en el lenguaje](https://en.wikipedia.org/wiki/Language_Integrated_Query) (Wikipedia)
- [Evaluación perezosa](https://en.wikipedia.org/wiki/Lazy_evaluation) (Wikipedia)
- [Iterador](https://en.wikipedia.org/wiki/Iterator) (Wikipedia)
