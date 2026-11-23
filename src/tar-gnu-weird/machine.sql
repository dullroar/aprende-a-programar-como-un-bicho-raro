-- La memoria de la máquina, creada una vez por base de datos. .parameter @seed y @week los fija run-clock.sh.
-- fsm es todo el estado de una ejecución: una fila. Solo un tick la cambia (ver tick.sql).
CREATE TABLE IF NOT EXISTS fsm(
    run_id  INTEGER PRIMARY KEY,
    seed    INTEGER NOT NULL,                    -- estado del generador Park-Miller
    card    INTEGER NOT NULL DEFAULT 0,          -- tarjetas cerradas hasta ahora; elige la categoría
    worked  INTEGER NOT NULL DEFAULT 0,          -- horas trabajadas en la tarjeta abierta
    target  INTEGER NOT NULL CHECK (target BETWEEN 10 AND 19),  -- horas que tardará esta tarjeta
    total   INTEGER NOT NULL DEFAULT 0,          -- total acumulado, en horas
    done    INTEGER NOT NULL DEFAULT 0,          -- 1 una vez que una tarjeta ha hecho pasar el total de 40
    tick    INTEGER NOT NULL DEFAULT 0,          -- el último TAR_CHECKPOINT visto
    idle    INTEGER NOT NULL DEFAULT 0,          -- ticks que llegaron después de done y no cambiaron nada
    week    TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS demo_timecards(
    run_id INTEGER NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Meetings','Coding','Debugging','Learning')),
    hours INTEGER NOT NULL CHECK (hours BETWEEN 10 AND 19),
    running_total INTEGER NOT NULL,
    week TEXT NOT NULL,
    at_tick INTEGER NOT NULL,                    -- el punto de control en el que cerró esta tarjeta
    demo_only INTEGER NOT NULL CHECK (demo_only = 1));
-- La duración de la primera tarjeta se sortea aquí, con la misma fórmula que usa tick.sql para cada tarjeta posterior.
INSERT INTO fsm(seed, target, week)
    SELECT s, 10 + s % 10, @week FROM (SELECT @seed * 48271 % 2147483647 AS s);
SELECT last_insert_rowid();
