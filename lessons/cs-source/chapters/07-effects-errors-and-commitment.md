---
title: "Efectos, errores y confirmación"
---
Para una lectura avanzada con trazas y experimentos, consulta la [guía de estudio sobre efectos, errores y confirmación](../guias-de-estudio/conceptos/efectos-errores-y-confirmacion.md).

Un programa que no hace nada fuera de sí mismo es un calefactor carísimo. Los programas útiles cambian el mundo: escriben archivos, imprimen e insertan filas. Este capítulo trata las tres preguntas que se desprenden de ello. ¿Cuándo se produce un efecto (**efectos secundarios**)? ¿Qué pasa cuando algo sale mal (**errores**)? ¿En qué momento se vuelve definitivo un cambio (**confirmación**)?

Las entradas de este capítulo juegan con los tres conceptos. Un motor de expresiones regulares ejecuta toda la demostración y luego *provoca un fallo a propósito*. La lección está en lo que sobrevive al fallo. Una infracción de una restricción, un desbordamiento aritmético o el estado de salida de un programa *es* la regla de parada. La confirmación de una transacción de base de datos solo ocurre cuando el trabajo termina. Los conceptos que siguen dan un nombre y una razón a cada caso: efectos secundarios, sistemas de efectos, excepciones, estado de salida, restricciones, retroceso, corte, transacciones, idempotencia y seguridad entre hilos.
