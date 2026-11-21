---
title: "Principio de mínimo privilegio"
chapter: 1
order: 40
---
El principio de mínimo privilegio dice que cada parte de un sistema debe recibir solo los permisos que necesita. Existe porque todo programa tiene bichos. Si alguien aprovecha un bicho, el daño se limita a lo que esa parte tenía permiso de hacer. En este repositorio, los contenedores de ejecución funcionan con el usuario sin privilegios `nobody`, sin red y con un sistema de archivos de solo lectura. Si una entrada se porta mal, casi no tiene *con qué* hacerlo.

- **Úsalo cuando:** siempre. Es la regla predeterminada para cuentas, servicios, contenedores, tokens de API y permisos de archivo.
- **Evita su modo de fallo:** si una tarea sufre un fallo por falta de un permiso, concede justo ese permiso. No lo "arregles" ejecutándola como root.

**Lee más:**

- [Principio de mínimo privilegio](https://en.wikipedia.org/wiki/Principle_of_least_privilege) (Wikipedia)
- [RFC 4949: glosario de seguridad en Internet](https://www.rfc-editor.org/rfc/rfc4949), que define el término (busca "least privilege" en la página)
