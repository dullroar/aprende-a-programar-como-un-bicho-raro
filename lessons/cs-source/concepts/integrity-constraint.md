---
title: "Restricciones de integridad"
chapter: 7
order: 50
---
Una restricción de integridad es una regla que la propia base de datos hace cumplir: `NOT NULL`, `UNIQUE`, `FOREIGN KEY` y `CHECK`. Existe porque "validamos en la aplicación" solo funciona si todas las aplicaciones validan. Una restricción hace que los datos incorrectos sean *imposibles*, no solo improbables. En este repositorio, `CHECK(demo_only=1)` aparece en casi todas las entradas. En esa tabla no puede existir una fila ajena a la demostración y cada `check.sh` intenta infringir la regla. Aquí las restricciones sirven como regla de parada (una infracción termina la ejecución) y como garantía. Conserva el segundo uso en los programas reales.

- **Úsala cuando:** una regla deba cumplirse sin importar quién escriba los datos. Consulta también [[invariant]].
- **Evítala cuando:** los usuarios necesiten mensajes de validación que les indiquen qué hacer. Una restricción simple tampoco sirve bien para reglas complejas que requieren disparadores.

**Lee más:**

- [Restricción de integridad](https://en.wikipedia.org/wiki/Integrity_constraint) (Wikipedia)
- [Restricción de comprobación](https://en.wikipedia.org/wiki/Check_constraint) (Wikipedia)
