#!/usr/bin/env python3
"""Extract every instruction description from an RH850 core software manual.

The manual's table of contents is the completeness oracle.  Every section named
"... Instruction Set" contributes all of its immediate numbered children; each
child must have a matching numbered heading in the body.

Usage:
    extract-rh850-manual.py RH850_CORE_SOFTWARE_MANUAL.pdf [output-dir]
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

TOC = re.compile(r"^\s*(\d+(?:\.\d+)+)\s+(.+?)\s+\.{2,}\s*\d+\s*$")
BODY = re.compile(r"^\s*(\d+(?:\.\d+)+)\s+(.+?)\s*$")


def parts(section: str) -> tuple[int, ...]:
    return tuple(int(x) for x in section.split('.'))


def norm_title(title: str) -> str:
    return " ".join(title.strip().split())


def main() -> int:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: extract-rh850-manual.py MANUAL.pdf [output-dir]")

    pdf = Path(sys.argv[1])
    out = Path(sys.argv[2] if len(sys.argv) == 3 else "instructions")
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        txt = Path(td) / "manual.txt"
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True)
        lines = txt.read_text(encoding="utf-8", errors="replace").splitlines()

    toc_entries: list[tuple[str, str]] = []
    for line in lines:
        m = TOC.match(line)
        if m:
            toc_entries.append((m.group(1), norm_title(m.group(2))))

    set_roots = [
        (section, title)
        for section, title in toc_entries
        if title.lower().endswith("instruction set")
    ]
    if not set_roots:
        raise SystemExit("no '* Instruction Set' sections found in RH850 manual TOC")

    wanted: list[dict[str, str]] = []
    seen_sections: set[str] = set()
    for root, set_title in set_roots:
        root_parts = parts(root)
        for section, title in toc_entries:
            p = parts(section)
            if len(p) != len(root_parts) + 1 or p[:-1] != root_parts:
                continue
            if section in seen_sections:
                raise SystemExit(f"duplicate instruction section in TOC: {section}")
            seen_sections.add(section)
            wanted.append({
                "set_section": root,
                "set_title": set_title,
                "section": section,
                "mnemonic": title,
            })

    if not wanted:
        raise SystemExit("instruction-set sections exist but contain no numbered instruction children")
    wanted.sort(key=lambda r: parts(r["section"]))

    # Locate exact body headings. TOC lines contain dot leaders/page numbers and
    # therefore do not match this exact heading shape.
    body_positions: dict[str, tuple[int, str]] = {}
    wanted_by_section = {r["section"]: r for r in wanted}
    for i, line in enumerate(lines):
        m = BODY.match(line)
        if not m:
            continue
        section, title = m.group(1), norm_title(m.group(2))
        rec = wanted_by_section.get(section)
        if rec is None or title != rec["mnemonic"]:
            continue
        if section in body_positions:
            # Headers can be repeated by PDF layout only if they are truly exact;
            # require one unambiguous instruction-description start.
            raise SystemExit(f"duplicate exact body heading for instruction {section} {title}")
        body_positions[section] = (i, title)

    missing = [r for r in wanted if r["section"] not in body_positions]
    if missing:
        for r in missing:
            print(f"missing body heading: {r['section']} {r['mnemonic']}", file=sys.stderr)
        raise SystemExit(f"{len(missing)} TOC instructions missing from body")

    # Preserve every full instruction block. End a block at the next wanted
    # instruction heading in physical document order, or at the next same/higher
    # level section heading if no later instruction exists.
    ordered = sorted(
        ((body_positions[r["section"]][0], r) for r in wanted),
        key=lambda x: x[0],
    )
    jsonl = out / "instructions.jsonl"
    with jsonl.open("w", encoding="utf-8") as f:
        for n, (start, rec) in enumerate(ordered):
            end = ordered[n + 1][0] if n + 1 < len(ordered) else len(lines)
            # Bound the last instruction if a later numbered section begins.
            if n + 1 == len(ordered):
                level = len(parts(rec["section"]))
                for j in range(start + 1, end):
                    m = BODY.match(lines[j])
                    if not m:
                        continue
                    p = parts(m.group(1))
                    if len(p) <= level and parts(m.group(1)) > parts(rec["section"]):
                        end = j
                        break
            block = "\n".join(lines[start:end]).rstrip() + "\n"
            out_rec = dict(rec)
            out_rec["text"] = block
            f.write(json.dumps(out_rec, ensure_ascii=False, sort_keys=True) + "\n")

    with (out / "instructions.tsv").open("w", encoding="utf-8") as f:
        f.write("set_section\tset_title\tsection\tmnemonic\n")
        for rec in wanted:
            f.write(
                f"{rec['set_section']}\t{rec['set_title']}\t{rec['section']}\t{rec['mnemonic']}\n"
            )

    counts: dict[str, int] = {}
    for rec in wanted:
        key = f"{rec['set_section']} {rec['set_title']}"
        counts[key] = counts.get(key, 0) + 1

    raw = pdf.read_bytes()
    manifest = {
        "pdf": pdf.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "instruction_sets": counts,
        "instruction_descriptions": len(wanted),
        "completeness_check": "every immediate TOC child of every '* Instruction Set' section has an exact body heading",
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"{len(wanted)} instruction descriptions -> {out}", file=sys.stderr)
    for name, count in counts.items():
        print(f"  {name}: {count}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
