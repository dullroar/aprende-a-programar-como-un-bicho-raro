---
title: "Flujo de control que se reescribe a sí mismo"
order: 50
---
El programa cambia adónde va a continuación. [[entry:cobol-weird]] usa `ALTER` para recablear un `GO TO`. [[entry:forth-weird]] mueve `>in`, la posición de análisis del intérprete de texto, hacia atrás para ejecutar de nuevo las mismas palabras. [[entry:apl-weird]] lee su propio código fuente con `⎕CR`, lo reescribe y define la función nueva con `⎕FX`: cada paso fabrica a su sucesor. Este es el papel más peligroso del libro. También es la imagen más clara de lo que de verdad es un contador de programa. [[entry:ex-weird]] copia una línea de datos de una cinta a un registro y la ejecuta. En la cinta, la instrucción es `@a` (ejecuta el programa otra vez) o un comentario (detente), así que el programa lee su siguiente paso en los datos.
