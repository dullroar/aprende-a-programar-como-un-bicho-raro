#!/usr/bin/env python3
"""Make a study guide's Mermaid copies carry the same Spanish as their canonical source (plan Appendix A step 4).

A guide diagram is preceded by `<!-- diagram-source: src/<entry>/README.md#program-flow -->` and must equal that README's
diagram exactly (lessons/book/study_guides.py). In English the copy is verbatim, so a guide label and the README label with the
same English text and the same role must get the same Spanish. Translating the guide and the README separately breaks that
(different wording in the same node), so this tool copies the README's PO translation into the guide's PO.

    python3 -I tools/sync_guide_diagrams.py GUIDE.md            # report only (exit 1 when anything would change)
    python3 -I tools/sync_guide_diagrams.py GUIDE.md --write    # update translation/po/GUIDE.md.po, then run apply.py GUIDE.md --write

Run it on the English file (restore it from the pinned English clone first: `git checkout` gives you the Spanish one) and
then apply the PO, as for any hand edit of a PO. A diagram whose source README has no translation yet is reported as pending and
left alone; run the tool again after that README is translated. A guide label with no counterpart in the source is a problem:
the diagram is not a verbatim copy, and the guide check will say so too.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import apply as ap          # noqa: E402
import segment              # noqa: E402

MARKER_RE = re.compile(r"^<!--\s*diagram-source:\s*(\S+?)\s*-->\s*$")


def slug(heading):
    h = re.sub(r"`", "", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", h).replace(" ", "-")


def diagrams_with_markers(seg):
    """[(source ref, mermaid block)] for every mermaid block that has a diagram-source line before it."""
    out = []
    lines = seg.original_lines()
    for b in seg.blocks:
        if b.kind != "mermaid":
            continue
        i = b.start - 1
        while i >= 0 and not lines[i].strip():
            i -= 1
        m = MARKER_RE.match(lines[i].strip()) if i >= 0 else None
        if m:
            out.append((m.group(1), b))
    return out


def section_diagram(seg, anchor):
    """The first mermaid block under the heading whose slug is `anchor`, or None."""
    current = None
    for b in seg.blocks:
        if b.kind == "heading":
            current = slug(re.sub(r"^#+\s*", "", b.text or ""))
        elif b.kind == "mermaid" and current == anchor:
            return b
    return None


def sync(guide_seg, guide_po, load_source):
    """Copy translations from source READMEs into `guide_po` (a polib.POFile) in place.

    `load_source(path)` returns (English text, polib.POFile or None) of a source file. Returns (changed, pending, problems):
    counts of copied labels, labels whose source has no translation yet, and messages about diagrams that are not copies."""
    entries = {e.msgctxt: e for e in guide_po}
    changed = pending = 0
    problems = []
    for ref, block in diagrams_with_markers(guide_seg):
        path, _, anchor = ref.partition("#")
        try:
            en_text, src_po = load_source(path)
        except FileNotFoundError:
            problems.append("%s: source file not found" % ref)
            continue
        src_seg = segment.Segmentation(en_text, path)
        src_block = section_diagram(src_seg, anchor)
        if src_block is None:
            problems.append("%s: no diagram under that heading" % ref)
            continue
        src_by_id = {e.msgctxt: e for e in src_po} if src_po is not None else {}
        src_labels = {}
        for lab in src_block.labels:
            if lab.translate:
                src_labels.setdefault((lab.info, lab.masked), lab)
        for lab in block.labels:
            if not lab.translate:
                continue
            twin = src_labels.get((lab.info, lab.masked))
            if twin is None:
                problems.append("%s: label %r (%s) has no counterpart in the source diagram" % (ref, lab.text[:40], lab.info))
                continue
            theirs = src_by_id.get(twin.id)
            mine = entries.get(lab.id)
            if theirs is None or not theirs.msgstr.strip() or "fuzzy" in theirs.flags:
                pending += 1
                continue
            if mine is None:
                problems.append("%s: guide PO has no entry for label %r" % (ref, lab.text[:40]))
                continue
            if mine.msgstr != theirs.msgstr:
                mine.msgstr = theirs.msgstr
                if "fuzzy" in mine.flags:
                    mine.flags.remove("fuzzy")
                changed += 1
    return changed, pending, problems


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.split("\n\n")[0])
        return 2
    rel = args[0]
    import inventory
    clone = inventory.read_config(ROOT)["english_clone_path"]

    def read_en(path):
        with open(os.path.join(clone, path), encoding="utf-8", newline="") as f:
            return f.read()

    def load_source(path):
        po_file = ap.po_path_for(path)
        return read_en(path), (ap.load_po(po_file) if os.path.isfile(po_file) else None)

    seg = segment.Segmentation(read_en(rel), rel)
    po_file = ap.po_path_for(rel)
    po = ap.load_po(po_file)
    changed, pending, problems = sync(seg, po, load_source)
    for p in problems:
        print("PROBLEM " + p)
    print("labels to change: %d, pending (source not translated): %d" % (changed, pending))
    if "--write" in argv and not problems:
        po.save(po_file)
        print("wrote " + po_file)
    return 1 if problems or (changed and "--write" not in argv) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
