---
name: Fixture lesson on state machines
teaches: A machine is state plus a rule for the next state.
machine: a stack of integers and an ADD instruction
state: the stack contents before and after each step
assurance: guaranteed
kind: concept
---

# Timecards and the stop rule

<!-- fixture: this comment must survive byte for byte -->

The total must be **strictly greater than 40** to stop; exactly 40 continues. See [the Forth solution](../../lessons/solutions/forth/timecards.fs) and <https://example.com/a?b=1&c=2> for the details.

Run `python3 timecards.py --week 12` and then read `running_total` in the output. The call `sum(3)` returns `6`, and [[entry:m4]] points at the matching entry in [[call-stack]].

Phase {{phase.1.letter}} is called {{phase.1.name}}. The four card categories are Meetings, Coding, Debugging and Learning.

## Output you must never translate

```text
Hello, world!
entries=3 committed total=41.5
DEMO ONLY run
```

```python
def total(hours):
    # Add up the hours, then compare with 40
    return sum(hours)
```

## A table with escaped pipes

| Operator | Meaning | Example |
|----------|---------|---------|
| `a \| b` | bitwise or | `1 \| 2` gives 3 |
| `>=` | at least | exactly 40 continues |
| `&&` | both are true | `x > 0 && y > 0` |

## Raw HTML and entities

<details>
<summary>Click for the answer</summary>

The answer is **42**.

</details>

<p align="center"><img src="images/figure-1.png" alt="Figure one"></p>

## Unicode that must round trip

- Spanish: ¿Qué hora es? ¡Eso es todo! Señor Muñoz come piñas en Málaga.
- Combining mark: the word "año" is spelled with n and U+0303, and "año" is precomposed.
- APL: ⍳10 ⌽⍴ ⍋⍒ +/⍳5
- Symbols: s′ ≤ s″, 40 ≥ 40, → ← ↔ ✓
- Emoji and wide: 🐛 🪲 漢字
- Non-breaking space between 40 and hours: 40 hours; a tab:	end.

1. Ordered item one.
2. Ordered item two with `code` inside.
   - Nested bullet with a [link](https://example.com/x#y).

> A block quote with a warning: never run this as root.

Final line without a trailing blank line.
