import { EventEmitter } from 'node:events';
import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { homedir, userInfo } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// El mismo reto que ../javascript y ../javascript-weird, sin ninguna sentencia de bucle y sin cadena de clausuras.
// El programa es el conjunto de ESCUCHADORES registrados en un solo EventEmitter. Cada escuchador hace una cosa pequeña y luego
// emite el evento que espera el siguiente escuchador. El arranque visible es una sola línea, al final del archivo:
//
//     program(realWorld()).emit('start');
//
// DEMO ONLY: tarjetas de horas ficticias, guardadas en un archivo SQLite desechable. Nada de aquí toca el registro de horas real.
//
//   start --(setImmediate)--> generate --> card-created --> card-saved --> total-updated --+--> finished
//                                 ^                                                        |
//                                 +-------------------(setImmediate)----------------------+
//   Any listener that throws --> failed
//
// Dos clases de flechas. Las flechas normales son emit(): Node llama a todos los escuchadores de ese evento, en el orden en que se
// registraron, ANTES de que emit() devuelva el control. La pila de llamadas crece unos cuantos marcos y vuelve a deshacerse. Las flechas de setImmediate
// son distintas: el paso siguiente se pone en la cola del bucle de eventos y se ejecuta solo después de que la pila se haya deshecho. Sin
// ese límite, la cadena de emits sería una recursión con un nivel más por cada tarjeta.

const LIMIT = 40;
export const CATEGORIES = ['Reuniones', 'Programación', 'Depuración', 'Aprendizaje'];

const SCHEMA = `
  CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, seed INTEGER NOT NULL, demo_only INTEGER NOT NULL DEFAULT 1 CHECK (demo_only = 1));
  CREATE TABLE IF NOT EXISTS demo_timecards(run_id INTEGER NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Reuniones','Programación','Depuración','Aprendizaje')),
    hours INTEGER NOT NULL CHECK (hours BETWEEN 10 AND 19), running_total INTEGER NOT NULL,
    user_id TEXT NOT NULL, year INTEGER NOT NULL, week INTEGER NOT NULL,
    demo_only INTEGER NOT NULL DEFAULT 1 CHECK (demo_only = 1));`;

// El año y la semana ISO de una fecha: el jueves de esa misma semana decide el año.
export const isoWeek = d => {
  const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));
  const year = t.getUTCFullYear();
  return [year, Math.ceil(((t - Date.UTC(year, 0, 1)) / 864e5 + 1) / 7)];
};

// Todo lo que el programa necesita del mundo exterior es un solo objeto, así una prueba puede pasar el suyo. `rng` responde
// un número y las horas son 10 + (ese número % 10); `schedule` ejecuta una función en un turno POSTERIOR del bucle de eventos;
// `open` crea la base de datos; `every` inicia un temporizador repetitivo y responde con la función que lo detiene.
export const realWorld = () => {
  const seed = Number(process.env.SEED) || crypto.getRandomValues(new Uint32Array(1))[0] % 2147483646 + 1;
  const now = process.env.NOW ? new Date(`${process.env.NOW}T12:00:00Z`) : new Date();
  return {
    seed, limit: LIMIT, user: userInfo().username, week: isoWeek(now),
    rng: (r => () => (r = r * 48271 % 2147483647))(seed),           // Park-Miller: SEED=42 replays a run
    schedule: setImmediate,
    open: () => {
      const dir = join(process.env.XDG_DATA_HOME ?? join(homedir(), '.local', 'share'), 'JavaScriptEvents');
      mkdirSync(dir, { recursive: true });
      return new DatabaseSync(join(dir, 'demo-timecards.db'));
    },
    out: line => console.log(line), raw: text => process.stdout.write(text), err: line => console.error(line),
    tty: Boolean(process.stdout.isTTY) && process.env.TERM !== 'dumb', plain: 'NO_COLOR' in process.env,
    cycles: Number(process.env.PULSE_CYCLES) || 3,
    every: (fn, ms) => { const id = setInterval(fn, ms); return () => clearInterval(id); },
    exit: code => { process.exitCode = code; },
  };
};

export const program = world => {
  const { seed, limit, user, week, rng, schedule, open, out, raw, err, tty, plain, cycles, every, exit } = world;
  const events = new EventEmitter();
  const s = { db: null, insert: null, run: 0, n: 0, total: 0, frame: 0, stop: null };

  // Un throw dentro de un escuchador viaja HACIA ARRIBA por emit() hasta quien lo llamó. Aquí eso es una función programada
  // que nadie espera, así que el throw terminaría el proceso. Cada escuchador lo captura y lo informa como un evento.
  const on = (name, listener) => events.on(name, (...args) => {
    try { listener(...args); } catch (e) { events.emit('failed', e); }
  });
  const attempt = undo => { try { undo(); } catch { /* it is already broken: say nothing more */ } };
  const later = name => schedule(() => events.emit(name));       // the one place where a step waits for a new turn

  // 1. start: abre la base de datos y empieza la transacción, y luego pide la primera tarjeta EN UN TURNO POSTERIOR.
  on('start', () => {
    s.db = open();
    s.db.exec(SCHEMA);
    s.db.exec('BEGIN');
    s.run = Number(s.db.prepare('INSERT INTO runs(seed) VALUES (?)').run(seed).lastInsertRowid);
    s.insert = s.db.prepare('INSERT INTO demo_timecards(run_id, category, hours, running_total, user_id, year, week) VALUES (?, ?, ?, ?, ?, ?, ?)');
    out(`# DEMO ONLY run ${s.run}`);
    later('generate');
  });

  // 2. generate: crea una tarjeta. Emitir ejecuta los escuchadores de card-created AHORA MISMO, dentro de esta llamada.
  on('generate', () => {
    s.n += 1;
    events.emit('card-created', { category: CATEGORIES[(s.n - 1) % 4], hours: 10 + rng() % 10 });
  });

  // 3. card-created: la guarda. node:sqlite es síncrono, así que la fila queda escrita cuando run() devuelve el control, antes de la
  //    línea siguiente, y nada más adelante puede ver una tarjeta que no esté guardada.
  on('card-created', card => {
    const total = s.total + card.hours;
    s.insert.run(s.run, card.category, card.hours, total, user, ...week);
    events.emit('card-saved', { ...card, total });
  });

  // 4. card-saved: solo ahora cambia el total acumulado. Imprime la fila.
  on('card-saved', card => {
    s.total = card.total;
    out(`${card.category}\t${card.hours}\t${card.total}\t${week[0]}-W${String(week[1]).padStart(2, '0')}\tDEMO ONLY`);
    events.emit('total-updated', s.total);
  });

  // 5. total-updated: la regla de parada y la única bifurcación. Si pasa del límite: anuncia el final ahora. Si no: la tarjeta siguiente
  //    espera a un turno nuevo, de modo que la pila se deshace primero.
  on('total-updated', total => (total > limit ? events.emit('finished') : later('generate')));

  // 6. finished: confirma la transacción, informa, cierra, y o bien termina o bien pasa el control al temporizador del pulso.
  on('finished', () => {
    s.db.exec('COMMIT');
    out(`# committed total=${s.total} entries=${s.n} DEMO ONLY\n\nTotal simulated hours: ${s.total.toFixed(1)}\nSaved locally for the modernization exercise.`);
    s.db.close();
    s.db = null;
    if (!tty) return events.emit('done');
    s.stop = every(() => events.emit('frame'), 600);
  });

  // 7. frame: un latido del pulso, desde un temporizador. El temporizador es lo único que mantiene vivo el proceso después de la
  //    última tarjeta. Cada latido es un turno separado del bucle de eventos.
  on('frame', () => {
    raw(`\r\x1b[2K${plain ? (s.frame % 2 ? ' ' : '*') : s.frame % 2 ? '\x1b[2m' : '\x1b[1m'}DEMO ONLY - no real time system is involved${plain ? '' : '\x1b[0m'}`);
    if (s.frame++ >= 2 * cycles) { s.stop(); s.stop = null; raw('\n'); events.emit('done'); }
  });

  // 8. done: no queda ningún escuchador, así que nada puede mantener vivo el proceso y nada puede volver a llamarse.
  events.on('done', () => { events.removeAllListeners(); exit(0); });

  // 9. failed: se ejecuta una vez. Deshace lo que no se confirmó, libera todo y avisa al usuario. El último paso quita todos los
  //    escuchadores, este también, así que un segundo fallo no encuentra a nadie a quien avisar. Eso es lo que lo hace ocurrir exactamente una vez.
  events.on('failed', e => {
    attempt(() => s.db?.exec('ROLLBACK'));
    attempt(() => s.db?.close());
    attempt(() => s.stop?.());
    err(`timecards: ${e?.message ?? e}`);
    events.removeAllListeners();
    exit(1);
  });

  // El nombre 'error' es especial en Node: emit('error', e) SIN escuchador LANZA e. Este escuchador convierte un 'error' suelto
  // en nuestro propio 'failed', así que el programa tiene una sola manera de fallar.
  events.on('error', e => events.emit('failed', e));
  return events;
};

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) program(realWorld()).emit('start');
