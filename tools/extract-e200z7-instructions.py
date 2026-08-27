#!/usr/bin/env python3
"""Extract the complete e200z7 core/VLE/SPE/EFPU instruction surfaces.

Usage:
  extract-e200z7-instructions.py CORE.pdf VLEPEM.pdf SPEPEM.pdf [output-dir]

Canonical pdftotext section snapshots are retained.  Normalized mnemonic lists
are navigation aids only; they never replace the source sections.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def pdf_text(pdf: Path) -> str:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "manual.txt"
        subprocess.run(["pdftotext", "-layout", str(pdf), str(out)], check=True)
        return out.read_text(encoding="utf-8", errors="replace")


def between(text: str, start: str, end: str, label: str) -> str:
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"{label}: missing start marker {start!r}")
    b = text.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f"{label}: missing end marker {end!r}")
    return text[a:b]


def first_tokens(block: str, allowed: re.Pattern[str]) -> list[str]:
    names = set()
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        token = line.split()[0].rstrip(',')
        # Expand comma-separated table cells when pdftotext keeps them together.
        for part in token.split(','):
            part = part.strip().rstrip(',')
            if allowed.fullmatch(part):
                names.add(part)
    return sorted(names)


def repeated_headings(block: str, allowed: re.Pattern[str]) -> list[str]:
    names = set()
    for raw in block.splitlines():
        words = raw.strip().split()
        if len(words) >= 2 and words[0] == words[1] and allowed.fullmatch(words[0]):
            names.add(words[0])
    return sorted(names)


def write_list(path: Path, names: list[str]) -> None:
    if not names:
        raise SystemExit(f"empty normalized instruction list for {path.name}")
    path.write_text("\n".join(names) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) not in (4, 5):
        raise SystemExit(
            "usage: extract-e200z7-instructions.py CORE.pdf VLEPEM.pdf SPEPEM.pdf [output-dir]"
        )

    core_pdf, vle_pdf, spe_pdf = map(Path, sys.argv[1:4])
    out = Path(sys.argv[4] if len(sys.argv) == 5 else "instructions")
    out.mkdir(parents=True, exist_ok=True)

    core = pdf_text(core_pdf)
    vle = pdf_text(vle_pdf)
    spe = pdf_text(spe_pdf)

    # e200z7 core manual explicitly says Table 4-4 gives detailed timing for
    # each instruction mnemonic.  Stop at 4.8 so later prose cannot pollute it.
    core_44 = between(
        core,
        "Table 4-4. Instruction Timing by Mnemonic",
        "4.8 Operand Placement on Performance",
        "e200z7 core Table 4-4",
    )
    (out / "core-table-4-4.txt").write_text(core_44, encoding="utf-8")
    base_rx = re.compile(r"[a-z][a-z0-9_.]*(?:\[[a-z.]+\])*")
    core_names = first_tokens(core_44, base_rx)
    # Filter obvious table/prose tokens that survive first-column extraction.
    reject = {
        "mnemonic", "latency", "serialization", "table", "continued",
        "freescale", "instruction", "e200z7",
    }
    core_names = [x for x in core_names if x not in reject]
    write_list(out / "core-mnemonics.txt", core_names)

    # Chapter 5 contains target-specific EFPU v2 instruction description pages.
    # Repeated heading form "efsabs efsabs" / "evfsabs evfsabs" is stable and
    # avoids counting mere prose references.
    efpu = between(core, "Chapter 5\nEmbedded Floating-Point Unit", "Chapter 6\nSignal Processing Extension", "e200z7 EFPU chapter")
    (out / "efpu-chapter-5.txt").write_text(efpu, encoding="utf-8")
    efpu_rx = re.compile(r"(?:efs|evfs)[a-z0-9_.]+")
    efpu_names = repeated_headings(efpu, efpu_rx)
    # Also retain opcode/timing-table-only names in case a form lacks a repeated
    # description heading in a future PDF layout.
    efpu_names = sorted(set(efpu_names) | set(first_tokens(efpu, efpu_rx)))
    write_list(out / "efpu-mnemonics.txt", efpu_names)

    # VLEPEM Appendix B says it lists all VLE instructions by mnemonic/opcode.
    vle_b = between(
        vle,
        "Appendix B\nVLE Instruction Set Tables",
        "Index",
        "VLE Appendix B",
    )
    (out / "vle-appendix-b.txt").write_text(vle_b, encoding="utf-8")
    vle_rx = re.compile(r"(?:se|e)_[a-z0-9_.]+")
    vle_names = sorted(set(vle_rx.findall(vle_b)))
    write_list(out / "vle-mnemonics.txt", vle_names)

    # SPEPEM Appendix B says it lists all SPE and embedded-FP instructions.
    spe_b = between(
        spe,
        "Appendix B\nSPE and Embedded Floating-Point Opcode Listings",
        "Index",
        "SPE Appendix B",
    )
    (out / "spe-appendix-b.txt").write_text(spe_b, encoding="utf-8")
    # Most real/simplified SPE/EFPU names are ev*/ef*, with brinc the notable
    # non-ev operation called out by the manual.  Keep both real and simplified
    # spellings; the raw appendix preserves encoding/alias identity.
    spe_rx = re.compile(r"(?:ev|ef)[a-z0-9_.]+|brinc")
    spe_names = sorted(set(spe_rx.findall(spe_b)))
    write_list(out / "spe-mnemonics.txt", spe_names)

    manifest = {
        "manuals": {
            "core": {"title": "e200z7 Power Architecture Core Reference Manual, Rev. 2", "sha256": hashlib.sha256(core_pdf.read_bytes()).hexdigest()},
            "vle": {"title": "VLE Programming Environments Manual, Rev. 0", "sha256": hashlib.sha256(vle_pdf.read_bytes()).hexdigest()},
            "spe": {"title": "SPE Programming Environments Manual, Rev. 0", "sha256": hashlib.sha256(spe_pdf.read_bytes()).hexdigest()},
        },
        "counts": {
            "core_mnemonic_rows": len(core_names),
            "efpu_mnemonics": len(efpu_names),
            "vle_mnemonics": len(vle_names),
            "spe_and_embedded_fp_names": len(spe_names),
        },
        "note": "canonical extracted text blocks are the completeness oracle; normalized lists are convenience indexes",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
