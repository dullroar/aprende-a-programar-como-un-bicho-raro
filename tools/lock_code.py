#!/usr/bin/env python3
"""tools/lock_code.py: protect the frozen files of the Spanish edition.

The frozen set is every file of the pinned English tree that tools/inventory.py classifies
as `frozen` (non-Markdown code, data, fixtures, scripts, solutions, the English LICENSE).
The manifest `translation/locked-code.sha256` lists `<sha256>  <path>` for each of them,
computed from the English clone at the pinned commit (never from this working tree, so a
damaged import cannot be locked in by mistake).

Usage:
  python3 tools/lock_code.py --write           (re)write the manifest from the English clone
  python3 tools/lock_code.py --verify          working tree vs manifest, and manifest vs the
                                               English clone (when reachable); exit 1 on drift
  python3 tools/lock_code.py --check-staged    pre-commit check: reject staged changes that
                                               alter, delete or rename a frozen file
  python3 tools/lock_code.py --install-hook    install .git/hooks/pre-commit that runs
                                               --check-staged (refuses to overwrite a foreign hook)

Exit codes: 0 ok, 1 drift or violation, 2 usage or environment error.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventory as inv  # noqa: E402

MANIFEST = "translation/locked-code.sha256"
HOOK_MARKER = "# managed-by: tools/lock_code.py"
HOOK_BODY = f"""#!/bin/sh
{HOOK_MARKER}
# Rejects commits that change frozen files (translation/locked-code.sha256). Do not bypass.
root="$(git rev-parse --show-toplevel)" || exit 1
exec python3 "$root/tools/lock_code.py" --check-staged
"""


class LockError(Exception):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_frozen(path: str) -> bool:
    return inv.classify(path) == ["frozen"]


# ---------------------------------------------------------------- manifest I/O

def format_manifest(entries: dict[str, str]) -> str:
    return "".join(f"{h}  {p}\n" for p, h in sorted(entries.items()))


def parse_manifest(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        h, sep, p = line.partition("  ")
        if not sep or len(h) != 64 or any(c not in "0123456789abcdef" for c in h) or not p:
            raise LockError(f"manifest line {n} is malformed: {line!r}")
        if p in entries:
            raise LockError(f"manifest line {n} repeats {p}")
        entries[p] = h
    return entries


def load_manifest(root: str) -> dict[str, str]:
    path = os.path.join(root, MANIFEST)
    if not os.path.exists(path):
        raise LockError(f"{MANIFEST} is missing; run --write")
    with open(path, encoding="utf-8") as fh:
        entries = parse_manifest(fh.read())
    if not entries:
        raise LockError(f"{MANIFEST} is empty")
    return entries


# ---------------------------------------------------------------- English clone

def english_hashes(cfg: dict) -> dict[str, str]:
    """sha256 of every frozen file at the pinned commit, read through git objects."""
    clone, sha = cfg.get("english_clone_path"), cfg.get("english_commit")
    if not clone or not sha:
        raise LockError("CONFIG.yaml lacks english_clone_path or english_commit")
    if not os.path.isdir(clone):
        raise LockError(f"English clone not found at {clone}")
    r = subprocess.run(["git", "-C", clone, "ls-tree", "-r", "-z", sha], capture_output=True)
    if r.returncode != 0:
        raise LockError(f"git ls-tree failed for {sha}: {r.stderr.decode(errors='replace')}")
    wanted: list[tuple[str, str]] = []
    for rec in r.stdout.decode("utf-8").split("\0"):
        if not rec:
            continue
        meta, _, path = rec.partition("\t")
        mode, otype, oid = meta.split()
        if otype != "blob":
            continue
        if mode == "120000":
            raise LockError(f"symlink in English tree: {path}; not supported by the lock")
        if is_frozen(path):
            wanted.append((path, oid))
    out: dict[str, str] = {}
    if not wanted:
        return out
    proc = subprocess.run(["git", "-C", clone, "cat-file", "--batch"],
                          input="".join(f"{oid}\n" for _, oid in wanted).encode(),
                          capture_output=True)
    if proc.returncode != 0:
        raise LockError(f"git cat-file failed: {proc.stderr.decode(errors='replace')}")
    buf, pos = proc.stdout, 0
    for path, oid in wanted:
        nl = buf.index(b"\n", pos)
        head = buf[pos:nl].split()
        if len(head) != 3 or head[0].decode() != oid or head[1] != b"blob":
            raise LockError(f"unexpected cat-file header for {path}: {buf[pos:nl]!r}")
        size = int(head[2])
        data = buf[nl + 1:nl + 1 + size]
        out[path] = sha256_bytes(data)
        pos = nl + 1 + size + 1
    return out


# ---------------------------------------------------------------- commands

def cmd_write(root: str) -> int:
    entries = english_hashes(inv.read_config(root))
    if not entries:
        raise LockError("no frozen files found in the English tree")
    with open(os.path.join(root, MANIFEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(format_manifest(entries))
    print(f"wrote {MANIFEST}: {len(entries)} frozen files")
    return 0


def crlf_checkout_paths(root: str, paths: list[str]) -> set[str]:
    """Paths git checks out as CRLF by attribute (`text eol=crlf`) while the index holds LF.

    For these the working-tree bytes differ from the committed blob only by the checkout
    conversion; git itself treats them as unchanged, so the lock compares them after
    CRLF -> LF. Any other difference still fails.
    """
    if not paths or not os.path.isdir(os.path.join(root, ".git")):
        return set()
    raw = git_bytes(root, "ls-files", "--eol", "-z", "--", *paths).decode("utf-8", "replace")
    out = set()
    for rec in raw.split("\0"):
        info, _, path = rec.partition("\t")
        if info.startswith("i/lf") and "w/crlf" in info and "eol=crlf" in info:
            out.add(path)
    return out


def tree_problems(root: str, entries: dict[str, str]) -> list[str]:
    problems, suspects = [], {}
    for path, want in sorted(entries.items()):
        full = os.path.join(root, path)
        if not os.path.isfile(full):
            problems.append(f"MISSING  {path}")
            continue
        with open(full, "rb") as fh:
            data = fh.read()
        if sha256_bytes(data) != want:
            suspects[path] = data
    crlf = crlf_checkout_paths(root, sorted(suspects))
    for path, data in sorted(suspects.items()):
        if path in crlf and sha256_bytes(data.replace(b"\r\n", b"\n")) == entries[path]:
            continue
        problems.append(f"CHANGED  {path}")
    return sorted(problems, key=lambda x: x.split("  ", 1)[1])


def clone_problems(cfg: dict, entries: dict[str, str]) -> list[str]:
    english = english_hashes(cfg)
    problems = []
    for path in sorted(set(english) | set(entries)):
        if path not in entries:
            problems.append(f"NOT-LOCKED  {path} (frozen in English, absent from manifest)")
        elif path not in english:
            problems.append(f"NOT-IN-ENGLISH  {path} (in manifest, not frozen at pinned SHA)")
        elif english[path] != entries[path]:
            problems.append(f"MANIFEST-DIFFERS  {path} (manifest hash is not the English hash)")
    return problems


def cmd_verify(root: str) -> int:
    cfg = inv.read_config(root)
    entries = load_manifest(root)
    problems = tree_problems(root, entries)
    try:
        problems += clone_problems(cfg, entries)
        clone_note = "and English clone agree"
    except LockError as e:
        problems.append(f"CLONE-UNREACHABLE  {e}")
        clone_note = ""
    for p in problems:
        print(p)
    if problems:
        print(f"lock_code --verify: FAIL ({len(problems)} problems)")
        return 1
    print(f"lock_code --verify: ok, {len(entries)} frozen files match the manifest {clone_note}")
    return 0


def git_bytes(root: str, *args: str) -> bytes:
    r = subprocess.run(["git", "-C", root, *args], capture_output=True)
    if r.returncode != 0:
        raise LockError(f"git {' '.join(args)} failed: {r.stderr.decode(errors='replace')}")
    return r.stdout


def staged_violations(root: str, entries: dict[str, str]) -> list[str]:
    """Frozen paths that the index would commit in a changed or deleted state."""
    raw = git_bytes(root, "diff", "--cached", "--name-status", "-z", "--no-renames")
    parts = [p for p in raw.decode("utf-8").split("\0") if p]
    bad = []
    for status, path in zip(parts[0::2], parts[1::2]):
        if path not in entries:
            continue
        if status.startswith("D"):
            bad.append(f"DELETED  {path}")
            continue
        got = sha256_bytes(git_bytes(root, "show", f":{path}"))
        if got != entries[path]:
            bad.append(f"CHANGED  {path}")
    return bad


def cmd_check_staged(root: str) -> int:
    entries = load_manifest(root)
    bad = staged_violations(root, entries)
    for b in bad:
        print(b, file=sys.stderr)
    if bad:
        print("lock_code: commit rejected, frozen files must stay byte-identical to the English "
              "source (hard rule 1). Mark the task blocked instead.", file=sys.stderr)
        return 1
    return 0


def cmd_install_hook(root: str) -> int:
    hooks = git_bytes(root, "rev-parse", "--git-path", "hooks").decode().strip()
    hooks = hooks if os.path.isabs(hooks) else os.path.join(root, hooks)
    os.makedirs(hooks, exist_ok=True)
    path = os.path.join(hooks, "pre-commit")
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as fh:
            if HOOK_MARKER not in fh.read():
                raise LockError(f"{path} exists and is not managed by lock_code.py; not overwritten")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HOOK_BODY)
    os.chmod(path, 0o755)
    print(f"installed {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--verify", action="store_true")
    g.add_argument("--check-staged", action="store_true")
    g.add_argument("--install-hook", action="store_true")
    ap.add_argument("--root", default=None, help="repo root (default: parent of tools/)")
    a = ap.parse_args(argv)
    root = a.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        if a.write:
            return cmd_write(root)
        if a.verify:
            return cmd_verify(root)
        if a.check_staged:
            return cmd_check_staged(root)
        return cmd_install_hook(root)
    except LockError as e:
        print(f"lock_code: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
