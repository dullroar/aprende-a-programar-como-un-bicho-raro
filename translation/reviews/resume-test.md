# Resume test (P3-009)

Scratch repo `translation/work/resume-test/main`, real `loop/ralph.sh`, `tools/next_task.py`, `tools/seedtask.py`.
Two driver runs with two different `AGENT_CMD` invocations; STOP between them.

## Driver output

Run 1 (agent A, `--mode partial-stop`):

```
ralph: start at iteration 1; max_iter=10 max_usd=100 timeout=1m
ralph: iteration 1 progressed (rc=0, 0s, spent $0.0000).
ralph: STOP sentinel found.
ralph: finished. Iterations: 1. Spent: $0.0000. See <scratch>/loop/HANDOFF.md and <scratch>/loop/STATE.md.
```

Run 2 (agent B, `--mode resume`):

```
ralph: start at iteration 2; max_iter=10 max_usd=100 timeout=1m
ralph: iteration 2 progressed (rc=0, 0s, spent $0.0000).
ralph: iteration 3 progressed (rc=0, 0s, spent $0.0000).
ralph: iteration 4 progressed (rc=0, 0s, spent $0.0000).
ralph: DONE sentinel found: DONE
ralph: finished. Iterations: 4. Spent: $0.0000. See <scratch>/loop/HANDOFF.md and <scratch>/loop/STATE.md.
```

## Agent calls (iteration, name, mode)

```
1 A partial-stop
2 B resume
3 B resume
4 B resume
```

## loop/log.md in the scratch repo

```
1 T-1 partial segments 1 to 2 done; stopped by STOP
2 T-1 done resumed from HANDOFF.md and the queue at segment 3
3 T-2 done all segments
```

## Part file work/T-1.part

```
T-1 segment 1
T-1 segment 2
T-1 segment 3
T-1 segment 4
```

## Verdict

PASS

Negative cases (all must be caught): restart instead of resume, STOP at the start, stalled agent, held lock.
