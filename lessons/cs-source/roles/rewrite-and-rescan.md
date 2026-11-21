---
title: "Texto que se reescribe y se vuelve a leer"
order: 40
---
El programa es texto y repetir es reescribirlo. [[entry:regex-sed]] conserva una línea de texto y aplica sustituciones hasta que ninguna coincide. [[entry:m4]] define una macro cuyo texto de reemplazo contiene la propia macro, así que la salida se escanea otra vez, y otra. [[entry:make-gnu]] rehace un makefile que incluye, y luego *empieza de nuevo* con el nuevo. En los tres, lo que se repite es la lectura de una entrada reescrita, y el estado es lo que diga ahora el texto (o el conjunto de archivos). [[entry:ed-weird]] reescribe líneas con sustituciones protegidas, y une líneas para que las marcas se añadan una junto a otra. No tiene una rama al estilo de `sed`: su única repetición es un comando global.
