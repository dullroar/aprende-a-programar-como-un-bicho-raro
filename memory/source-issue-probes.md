---
gist: "Read me when: you suspect a defect in the English book (Node ordering, PCRE2 JIT callouts, setImmediate) and must prove it before you log it."
---

# Probes before you log an English source issue

Log a proven defect in `translation/source-issues.md`. Do not open an upstream issue. Do not patch the English.

- **Node ordering.** Probe top-level `process.nextTick` and promise ordering separately in CommonJS and in ES modules. Do this before you record a Node ordering claim.
- **PCRE2 JIT.** Distinguish support for callouts from support for `callout_flags`. Check the installed `pcre2callout(3)` and `pcre2jit(3)` manuals.
- **setImmediate.** Check the order of `setImmediate()` from inside an I/O callback before you treat earlier queued timers as ahead of it.
- Run unusual example programs only in the sandbox container, never on the host.
