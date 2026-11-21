---
title: "Teoría de categorías"
chapter: 5
order: 120
---
La teoría de categorías estudia la matemática de las **cosas y las flechas entre ellas** y cómo se componen esas flechas. Una **categoría** tiene *objetos* y *morfismos* (flechas). Cada morfismo va de un objeto a otro. Se cumplen dos reglas:

1. **Identidad.** Cada objeto tiene una flecha hacia sí mismo que no cambia nada: `id`.
2. **Composición.** Si `f : A → B` y `g : B → C`, entonces existe `g ∘ f : A → C`. La composición es asociativa: `h ∘ (g ∘ f) = (h ∘ g) ∘ f`. Y `f ∘ id = f = id ∘ f`.

En programación, la categoría habitual tiene *tipos* como objetos y *funciones* como flechas. Las reglas dicen algo que ya usas. Puedes encadenar funciones y agrupar la cadena con paréntesis donde quieras. Una función que devuelve su entrada de datos no cambia nada.

```haskell
-- Haskell: composition is a function, and the laws are things you can test.
(show . (+ 1)) 41          -- "42"
(id . show) 42 == show 42   -- True: identity
```

```python
# Python: the same idea. compose(g, f)(x) is g(f(x)).
compose = lambda g, f: lambda x: g(f(x))
assert compose(str, lambda n: n + 1)(41) == "42"
```

El vocabulario viene con tres advertencias sinceras:

- **Sirve para mirar, no para etiquetar.** Puedes *describir* muchas canalizaciones como flechas entre tipos. Eso no convierte a cada operador de LINQ, cada `map` o cada `INSERT ... SELECT` en parte formal de una categoría. Una afirmación como "esto es un funtor" trae consigo leyes que se deben cumplir.
- **La sintaxis no es la estructura.** Dos operaciones llamadas `map` pueden diferir en el grado de evaluación perezosa, en el orden de sus efectos y en lo que hacen con una entrada de datos vacía. Mismo nombre, misma forma, distinto comportamiento. Las leyes deciden y los nombres no.
- **Un viaje de ida y vuelta no implica un isomorfismo.** Un *isomorfismo* es un par de flechas `f` y `g` con `g ∘ f = id` y `f ∘ g = id`. Un codificador y un decodificador (consulta [[serialization-deserialization-pickling]]) forman uno solo si se cumplen ambas leyes. Muchos códecs solo cumplen la segunda ley para algunos valores.

Este libro usa las ideas donde una entrada les da algo concreto a lo que aferrarse. [[entry:haskell]] compone funciones puras pequeñas. [[entry:LinqChallenge1]] encadena operadores de consulta. Las páginas siguientes, [[functor]] y [[monoid-and-fold]], nombran dos leyes que permiten reorganizar esas cadenas con seguridad.

- **Úsala cuando:** quieras decir con precisión qué conserva una canalización. También cuando dos diseños se parezcan y necesites saber si se comportan igual.
- **Evítala cuando:** el vocabulario sustituya a la explicación. Si una frase sencilla dice lo mismo, escribe esa frase.

**Lee más:**

- [Teoría de categorías](https://en.wikipedia.org/wiki/Category_theory) (Wikipedia)
- [Categoría (matemáticas)](https://en.wikipedia.org/wiki/Category_(mathematics)) (Wikipedia)
- [Composición de funciones](https://en.wikipedia.org/wiki/Function_composition) (Wikipedia)
- [Isomorfismo](https://en.wikipedia.org/wiki/Isomorphism) (Wikipedia)
