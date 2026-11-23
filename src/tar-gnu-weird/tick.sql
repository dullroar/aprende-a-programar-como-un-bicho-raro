-- Un punto de control = una hora = una transición acotada de la máquina. Lo ejecuta tick.sh, con @t = TAR_CHECKPOINT.
-- Aquí dentro nada hace bucle, y nada decide cuándo se detiene tar: tar no se detiene. Después de que la regla de parada
-- haya saltado (done = 1) un tick solo cambia el contador `idle`.
BEGIN;
UPDATE fsm SET idle = idle + 1, tick = @t
    WHERE run_id = (SELECT max(run_id) FROM fsm) AND done;
UPDATE fsm SET worked = worked + 1, total = total + 1, tick = @t
    WHERE run_id = (SELECT max(run_id) FROM fsm) AND NOT done;
INSERT INTO demo_timecards(run_id, category, hours, running_total, week, at_tick, demo_only)
    SELECT run_id,
           CASE card WHEN 0 THEN 'Reuniones' WHEN 1 THEN 'Programación' WHEN 2 THEN 'Depuración' WHEN 3 THEN 'Aprendizaje' ELSE 'Reuniones' END,
           worked, total, week, tick, 1
    FROM fsm WHERE run_id = (SELECT max(run_id) FROM fsm) AND NOT done AND worked = target;
UPDATE fsm SET card = card + 1, worked = 0, done = total > 40,
               seed = seed * 48271 % 2147483647, target = 10 + (seed * 48271 % 2147483647) % 10
    WHERE run_id = (SELECT max(run_id) FROM fsm) AND NOT done AND worked = target;
COMMIT;
