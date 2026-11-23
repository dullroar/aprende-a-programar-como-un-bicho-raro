import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { homedir, userInfo } from 'node:os';
import { join } from 'node:path';

// Una versión para Node.js del reto de C# de 2008 de Jim Lehmer: una sola sentencia `for` cuyo cuerpo está vacío.
// Todo lo que hace el programa ocurre en las tres cláusulas entre los paréntesis: el inicializador construye el estado,
// la condición decide si se continúa (y, cuando debe parar, muestra el resultado) y el iterador añade una tarjeta.
// Las tarjetas son DEMO ONLY: ficticias, locales y nunca se envían a ninguna parte.
for // Still the only statement.
(
  // El literal de objeto sigue siendo el contenedor del estado del iterador. Un inicializador de `for` admite una declaración, y esta es
  // la única declaración que puede guardar una docena de clases de estado. Hace el papel del objeto anónimo de C#.
  // C# también permite que el inicializador sea una lista de expresiones. JavaScript no mezcla las dos cosas: después de `let i = ...` una
  // coma empieza el siguiente *declarador*, no es el operador coma. Por eso el literal pasa por una flecha que
  // lo completa, y el cuerpo de la flecha sí puede usar el operador coma.
  let i = (s => (
    // Una clausura sobre la semilla: Park-Miller. SEED=42 reproduce una ejecución (Math.random no admite semilla).
    s.rnd = (r => () => (r = r * 48271 % 2147483647))(s.seed),
    // Archivo SQLite local, como en el original (allí: EF Core bajo LocalApplicationData). node:sqlite viene incluido.
    s.db.exec(`
      CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, seed INTEGER NOT NULL, demo_only INTEGER NOT NULL DEFAULT 1 CHECK (demo_only = 1));
      CREATE TABLE IF NOT EXISTS demo_timecards(run_id INTEGER NOT NULL,
        category TEXT NOT NULL CHECK (category IN ('Reuniones','Programación','Depuración','Aprendizaje')),
        hours INTEGER NOT NULL CHECK (hours BETWEEN 10 AND 19), running_total INTEGER NOT NULL,
        user_id TEXT NOT NULL, year INTEGER NOT NULL, week INTEGER NOT NULL,
        demo_only INTEGER NOT NULL DEFAULT 1 CHECK (demo_only = 1));`),
    s.run = Number(s.db.prepare('INSERT INTO runs(seed) VALUES (?)').run(s.seed).lastInsertRowid),
    s.insert = s.db.prepare('INSERT INTO demo_timecards(run_id, category, hours, running_total, user_id, year, week) VALUES (?, ?, ?, ?, ?, ?, ?)'),
    s))({
      hours: [],
      user: userInfo().username,
      categories: ['Reuniones', 'Programación', 'Depuración', 'Aprendizaje'],
      seed: Number(process.env.SEED) || crypto.getRandomValues(new Uint32Array(1))[0] % 2147483646 + 1,
      now: process.env.NOW ? new Date(`${process.env.NOW}T12:00:00Z`) : new Date(),
      // La semana ISO de una fecha, como [año ISO, semana]: el jueves de la misma semana decide el año.
      iso: d => ((t, y) => [y = (t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7)), t.getUTCFullYear()),
                           Math.ceil(((t - Date.UTC(y, 0, 1)) / 864e5 + 1) / 7)])(new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))),
      db: (dir => (mkdirSync(dir, { recursive: true }), new DatabaseSync(join(dir, 'demo-timecards.db'))))(
        join(process.env.XDG_DATA_HOME ?? join(homedir(), '.local', 'share'), 'JavaScript')),
      tty: process.stdout.isTTY && process.env.TERM !== 'dumb',
      plain: 'NO_COLOR' in process.env,
      frames: 0,
    })
  //   *
  //  *
  ;   // **************** FIRST SEMICOLON ****************
  //  *
  //   *
  // El original suma las horas con el Sum() de LINQ; aquí su pariente más cercano es un pliegue. Mientras el total sea 40 o
  // menos, la respuesta es `true` y el bucle da otra vuelta. En caso contrario la condición muestra el resultado, en línea,
  // y su valor es `false`: el bucle termina. Donde C# abría una ventana WPF, esto imprime y, en una terminal, hace pulsar
  // la línea DEMO ONLY con un temporizador, como el guion gráfico del original hacía aparecer y desvanecerse su ventana.
  i.hours.reduce((sum, h) => sum + h, 0) <= 40
    ? true
    : (console.log(`# DEMO ONLY run ${i.run}\n${i.db.prepare('SELECT category, hours, running_total, year, week FROM demo_timecards WHERE run_id = ? ORDER BY rowid').all(i.run)
        .map(r => `${r.category}\t${r.hours}\t${r.running_total}\t${r.year}-W${String(r.week).padStart(2, '0')}\tDEMO ONLY`).join('\n')}\n`
        + `# committed total=${i.hours.reduce((sum, h) => sum + h, 0)} entries=${i.hours.length} DEMO ONLY\n`
        + `\nTotal simulated hours: ${i.hours.reduce((sum, h) => sum + h, 0).toFixed(1)}\nSaved locally for the modernization exercise.`),
       i.tty && setInterval(function () {
         process.stdout.write(`\r\x1b[2K${i.plain ? (i.frames % 2 ? ' ' : '*') : i.frames % 2 ? '\x1b[2m' : '\x1b[1m'}DEMO ONLY - no real time system is involved${i.plain ? '' : '\x1b[0m'}`);
         i.frames++ >= 2 * (Number(process.env.PULSE_CYCLES) || 3) && (clearInterval(this), console.log());
       }, 600),
       false)
  //   *
  //  *
  ;  // **************** LAST SEMICOLON ****************
  //  *
  //   *
  // El iterador saca una cantidad de horas al azar y guarda una tarjeta, como hacía el original. Allí, un hilo en segundo plano
  // y la reflexión guardaban a través de un Mutex; aquí node:sqlite guarda de forma síncrona, así que nada de eso hace falta.
  i.hours.push(10 + i.rnd() % 10),
  i.insert.run(i.run, i.categories[(i.hours.length - 1) % 4], i.hours.at(-1), i.hours.reduce((sum, h) => sum + h, 0),
               i.user, ...i.iso(i.now))
)
{ /* Intentionally empty. */ }
