import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { homedir, userInfo } from 'node:os';
import { join } from 'node:path';
import { cards, hoursFrom, machine } from './core.mjs';

// Los efectos de las hojas. Cada uno es una clausura que hace una cosa en el mundo exterior, y nada más es impuro.
const seed = Number(process.env.SEED) || crypto.getRandomValues(new Uint32Array(1))[0] % 2147483646 + 1;
const now = process.env.NOW ? new Date(`${process.env.NOW}T12:00:00Z`) : new Date();
const isoWeek = d => ((t, y) => [y = (t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7)), t.getUTCFullYear()),
                                 Math.ceil(((t - Date.UTC(y, 0, 1)) / 864e5 + 1) / 7)])(new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())));
const db = (dir => (mkdirSync(dir, { recursive: true }), new DatabaseSync(join(dir, 'demo-timecards.db'))))(
  join(process.env.XDG_DATA_HOME ?? join(homedir(), '.local', 'share'), 'JavaScriptWeird'));
db.exec(`
  CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, seed INTEGER NOT NULL, demo_only INTEGER NOT NULL DEFAULT 1 CHECK (demo_only = 1));
  CREATE TABLE IF NOT EXISTS demo_timecards(run_id INTEGER NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Meetings','Coding','Debugging','Learning')),
    hours INTEGER NOT NULL CHECK (hours BETWEEN 10 AND 19), running_total INTEGER NOT NULL,
    user_id TEXT NOT NULL, year INTEGER NOT NULL, week INTEGER NOT NULL,
    demo_only INTEGER NOT NULL DEFAULT 1 CHECK (demo_only = 1));`);
const run = Number(db.prepare('INSERT INTO runs(seed) VALUES (?)').run(seed).lastInsertRowid);
// save: una clausura sobre la sentencia preparada y la ejecución. Guarda un registro y lo devuelve, así cabe en una tubería.
const save = (insert => r => (insert.run(run, r.category, r.hours, r.total, r.user, r.year, r.week), r))(
  db.prepare('INSERT INTO demo_timecards(run_id, category, hours, running_total, user_id, year, week) VALUES (?, ?, ?, ?, ?, ?, ?)'));
// stamp: una clausura sobre el usuario y la fecha. Convierte una tarjeta en un registro.
const stamp = (user, [year, week]) => card => ({ ...card, user, year, week });

// EL PROGRAMA. No se saca nada hasta que `toArray` lo pide. Cada petición pasa una tarjeta por la máquina, la sella y la guarda,
// y la propia máquina dice cuándo no hay más (la tarjeta que llevó el total por encima de 40 fue la última).
const records = Iterator.from(cards(machine(hoursFrom(seed)))).map(stamp(userInfo().username, isoWeek(now))).map(save).toArray();

// Un pliegue sobre la lista terminada. reduce no puede parar antes, y aquí no lo necesita: la lista ya está completa.
const total = records.reduce((sum, r) => sum + r.hours, 0);
console.log(`# DEMO ONLY run ${run}\n${records.map(r => `${r.category}\t${r.hours}\t${r.total}\t${r.year}-W${String(r.week).padStart(2, '0')}\tDEMO ONLY`).join('\n')}\n`
  + `# committed total=${total} entries=${records.length} DEMO ONLY\n\nTotal simulated hours: ${total.toFixed(1)}\nSaved locally for the modernization exercise.`);

// El pulso es un efecto aparte, después de guardarlo todo. Sus dos variables quedan capturadas por la función del temporizador.
process.stdout.isTTY && process.env.TERM !== 'dumb' && ((plain, cycles) => {
  let frame = 0;
  const id = setInterval(() => {
    process.stdout.write(`\r\x1b[2K${plain ? (frame % 2 ? ' ' : '*') : frame % 2 ? '\x1b[2m' : '\x1b[1m'}DEMO ONLY - no real time system is involved${plain ? '' : '\x1b[0m'}`);
    frame++ >= 2 * cycles && (clearInterval(id), console.log());
  }, 600);
})('NO_COLOR' in process.env, Number(process.env.PULSE_CYCLES) || 3);
