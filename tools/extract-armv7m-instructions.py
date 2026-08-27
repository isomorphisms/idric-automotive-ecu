#!/usr/bin/env python3
"""Extract every Armv7-M instruction description from ARM DDI 0403E.e.

Usage:
    ./tools/extract-armv7m-instructions.py DDI0403E_e.pdf [output-dir]

The official manual is the completeness oracle.  A7.7 explicitly says every
Armv7-M Thumb instruction is listed there, and each entry is numbered.  We keep
the complete text block for each entry rather than guessing extension support
from the mnemonic alone.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

A7 = re.compile(r"^\s*A7\.7\.(\d+)\s+(.+?)\s*$")
B5 = re.compile(r"^\s*B5\.2\.(\d+)\s+([A-Z][A-Z0-9.]*)\s*$")
EXPECTED_B5 = {"1": "CPS", "2": "MRS", "3": "MSR"}
ANNOTATIONS = (
    "Armv6-M",
    "Armv7-M",
    "Armv7E-M",
    "Floating-point",
    "FPv4-SP",
    "FPv4-D16",
    "FPv5",
    "single-precision",
    "double-precision",
)


def sections(lines: list[str], rx: re.Pattern[str]):
    starts: list[tuple[int, str, str]] = []
    seen: dict[str, str] = {}
    for i, line in enumerate(lines):
        m = rx.match(line)
        if not m:
            continue
        number, title = m.groups()
        title = " ".join(title.split())
        old = seen.get(number)
        if old is not None:
            if old != title:
                raise SystemExit(
                    f"conflicting titles for section {number}: {old!r} / {title!r}"
                )
            continue
        seen[number] = title
        starts.append((i, number, title))
    return starts


def main() -> int:
    if len(sys.argv) not in (2, 3):
        raise SystemExit(
            "usage: extract-armv7m-instructions.py DDI0403E_e.pdf [output-dir]"
        )
    pdf = Path(sys.argv[1])
    out = Path(sys.argv[2] if len(sys.argv) == 3 else "instructions")
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        text_path = Path(td) / "manual.txt"
        subprocess.run(
            ["pdftotext", "-layout", str(pdf), str(text_path)], check=True
        )
        lines = text_path.read_text(encoding="utf-8", errors="replace").splitlines()

    a7 = sections(lines, A7)
    if not a7:
        raise SystemExit("no A7.7.N instruction descriptions found")

    numbers = [int(number) for _, number, _ in a7]
    expected = list(range(1, max(numbers) + 1))
    if numbers != expected:
        missing = sorted(set(expected) - set(numbers))
        raise SystemExit(f"A7.7 instruction numbering is not contiguous; missing {missing}")

    records = []
    for n, (start, number, title) in enumerate(a7):
        end = a7[n + 1][0] if n + 1 < len(a7) else len(lines)
        # Do not let the last A7 entry swallow Part B.  The first B5 chapter marker
        # is a safe upper bound if present.
        if n + 1 == len(a7):
            for j in range(start + 1, end):
                if lines[j].strip() == "Chapter B5":
                    end = j
                    break
        block = "\n".join(lines[start:end]).rstrip() + "\n"
        found = [tag for tag in ANNOTATIONS if tag.lower() in block.lower()]
        records.append(
            {
                "section": f"A7.7.{number}",
                "title": title,
                "annotations_found": found,
                "text": block,
            }
        )

    with (out / "armv7m-instructions.jsonl").open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    with (out / "armv7m-instructions.tsv").open("w", encoding="utf-8") as f:
        f.write("section\ttitle\tannotations_found\n")
        for rec in records:
            annotations = ",".join(rec["annotations_found"])
            f.write(f"{rec['section']}\t{rec['title']}\t{annotations}\n")

    b5 = sections(lines, B5)
    got_b5 = {number: title for _, number, title in b5}
    if got_b5 != EXPECTED_B5:
        raise SystemExit(
            f"B5 system instruction set changed/unexpected: {got_b5!r}; "
            f"expected {EXPECTED_B5!r}"
        )
    (out / "system-instructions.tsv").write_text(
        "section\tmnemonic\n"
        + "".join(
            f"B5.2.{n}\t{EXPECTED_B5[n]}\n"
            for n in sorted(EXPECTED_B5, key=int)
        ),
        encoding="utf-8",
    )

    manifest = {
        "manual": "ARM DDI 0403E.e ID021621",
        "a7_instruction_descriptions": len(records),
        "first": records[0]["title"],
        "last": records[-1]["title"],
        "system_instructions": list(EXPECTED_B5.values()),
        "profile_note": (
            "S32K3: Armv7E-M/DSP plus the device's single-precision floating-point "
            "implementation; use per-encoding applicability text retained in JSONL."
        ),
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"{len(records)} A7 instruction descriptions + 3 B5 system definitions -> {out}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
