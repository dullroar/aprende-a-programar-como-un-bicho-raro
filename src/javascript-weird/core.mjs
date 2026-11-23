// Todo el algoritmo, como tres clausuras. Sin E/S, sin instrucciones de bucle, sin `this`.
// Una clausura es una función junto con las variables entre las que nació. Aquí esas variables son el estado del programa,
// y la única forma de llegar a ellas es llamar a la función.

export const CATEGORIES = ['Reuniones', 'Programación', 'Depuración', 'Aprendizaje'];

// 1. Una fuente de horas: una clausura sobre un número (Park-Miller). Cada llamada mueve `state` y responde de 10 a 19.
export const hoursFrom = seed => (state => () => 10 + (state = state * 48271 % 2147483647) % 10)(seed);

// 2. La máquina de tarjetas: una clausura sobre tres variables. Cada llamada crea la siguiente tarjeta y las mueve. Después de la tarjeta
//    que lleva el total por encima del límite responde undefined, para siempre. LA REGLA DE PARADA ES la asignación a `over`.
export const machine = nextHours => {
  let n = 0, total = 0, over = false;                    // the captured environment: nothing else can see these
  return () => over ? undefined : (hours => (total += hours, over = total > 40, { category: CATEGORIES[n++ % 4], hours, total }))(nextHours());
};

// 3. El protocolo de iteración, a mano: un iterable es un objeto cuyo [Symbol.iterator]() responde con un objeto que tiene next().
//    next() pide una tarjeta a la máquina, y dice `done` cuando ya no hay. Una tarjeta se crea solo cuando alguien la pide.
export const cards = next => ({
  [Symbol.iterator]: () => ({ next: () => (card => card ? { value: card, done: false } : { value: undefined, done: true })(next()) }),
});
