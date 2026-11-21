---
title: "Búsqueda con regex que devuelve capturas"
order: 61
---
[[entry:regex-dotnet]] gasta fichas de una pila de capturas mientras reconoce horas en unario. Un presupuesto vacío impide empezar otra tarjeta, así que la coincidencia puede tener éxito con el prefijo que incluye la tarjeta que cruza el límite. El anfitrión lee las capturas de esa coincidencia para construir un informe TSV. Una coincidencia fallida no expone capturas, así que la misma cinta con una aserción de fallo al final produce cero tarjetas.
