#!/usr/bin/env python3
"""Pass when a unittest run has no failure outside a recorded baseline and no fewer tests.

Run me when: a gate runs the tool test suite and the repository has known failures.
Usage: python3 -m unittest discover ... 2>&1 | python3 no_new_failures.py BASELINE
Exit 0: no new failure. 1: a new failure or fewer tests ran. 2: input or baseline unreadable.
"""
import re
import sys


def main(argv):
    if len(argv) != 1:
        print("usage: no_new_failures.py BASELINE", file=sys.stderr)
        return 2
    try:
        lines = open(argv[0], encoding="utf-8").read().splitlines()
    except OSError as exc:
        print(f"no_new_failures: cannot read baseline: {exc}", file=sys.stderr)
        return 2
    known, ran_min = set(), None
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith("ran: "):
            ran_min = int(line[5:])
        else:
            known.add(line.strip())
    out = sys.stdin.read()
    sys.stdout.write(out)
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if ran is None or ran_min is None:
        print("no_new_failures: no 'Ran N tests' line or no 'ran:' baseline: fail closed", file=sys.stderr)
        return 2
    now = {m.group(2).strip() for m in re.finditer(r"^(FAIL|ERROR): (.+)$", out, re.M)}
    new = sorted(now - known)
    fixed = sorted(known - now)
    rc = 0
    if new:
        print("no_new_failures: NEW failures:\n  " + "\n  ".join(new), file=sys.stderr)
        rc = 1
    if int(ran.group(1)) < ran_min:
        print(f"no_new_failures: only {ran.group(1)} tests ran, baseline {ran_min}", file=sys.stderr)
        rc = 1
    if fixed:
        print("no_new_failures: now passing (remove from the baseline):\n  " + "\n  ".join(fixed), file=sys.stderr)
    if rc == 0:
        print(f"no_new_failures: OK ({len(now)} known failures, {ran.group(1)} tests)", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
