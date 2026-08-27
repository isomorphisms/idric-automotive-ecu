#!/usr/bin/env python3
"""Extract all numbered TriCore instruction headings and verify TOC == body."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile

TOC = re.compile(r"^\s*(3\.[1-9]\.[0-9]+)\s+([A-Z][A-Z0-9.]*)\s+\.{2,}\s*[0-9]+\s*$")
BODY = re.compile(r"^\s*(3\.[1-9]\.[0-9]+)\s+([A-Z][A-Z0-9.]*)\s*$")

def skey(section):
    return tuple(map(int, section.split('.')))

def collect(lines, rx):
    out = {}
    for line in lines:
        m = rx.match(line)
        if m:
            section, mnemonic = m.groups()
            if section in out and out[section] != mnemonic:
                raise SystemExit(f"conflicting mnemonic for {section}")
            out[section] = mnemonic
    return out

def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: extract-manual-instructions.py TC18-VOL2.pdf [instructions.tsv]")
    pdf = Path(sys.argv[1])
    out = Path(sys.argv[2] if len(sys.argv) == 3 else "instructions.tsv")
    with tempfile.TemporaryDirectory() as td:
        text = Path(td) / "manual.txt"
        subprocess.run(["pdftotext", "-layout", str(pdf), str(text)], check=True)
        lines = text.read_text(encoding="utf-8", errors="replace").splitlines()
    toc, body = collect(lines, TOC), collect(lines, BODY)
    if not toc or not body:
        raise SystemExit("failed to find instruction headings")
    if set(toc.items()) != set(body.items()):
        raise SystemExit("manual completeness failure: TOC instruction set != body instruction set")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write("section\tmnemonic\n")
        for section, mnemonic in sorted(body.items(), key=lambda x: skey(x[0])):
            f.write(f"{section}\t{mnemonic}\n")
    print(f"{len(body)} instruction headings -> {out}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
