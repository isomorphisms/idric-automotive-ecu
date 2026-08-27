#!/usr/bin/env python3
"""Extract the complete e200z7 core/VLE/SPE/EFPU instruction surfaces.

Usage:
  extract-e200z7-instructions.py CORE.pdf VLEPEM.pdf SPEPEM.pdf [output-dir]

The canonical extracted manual sections are the completeness oracle.  Any
normalized name list is only a navigation view and is labelled accordingly.
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


def between_re(
    text: str,
    start_pattern: str,
    end_pattern: str,
    label: str,
    *,
    last_start: bool = False,
) -> str:
    starts = list(re.finditer(start_pattern, text, re.MULTILINE | re.DOTALL))
    if not starts:
        raise SystemExit(f"{label}: missing start pattern {start_pattern!r}")
    start = starts[-1] if last_start else starts[0]
    end = re.search(end_pattern, text[start.end():], re.MULTILINE | re.DOTALL)
    if end is None:
        raise SystemExit(f"{label}: missing end pattern {end_pattern!r}")
    return text[start.start(): start.end() + end.start()]


def first_tokens(block: str, allowed: re.Pattern[str]) -> list[str]:
    names = set()
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        token = line.split()[0].rstrip(',')
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
        raise SystemExit(f"empty navigation index for {path.name}")
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

    # The core manual says Table 4-4 gives detailed timing for each instruction
    # mnemonic.  Preserve the full table, not just tokens extracted from it.
    core_44 = between_re(
        core,
        r"Table 4-4\.\s+Instruction Timing by Mnemonic",
        r"4\.8\s+Operand Placement on Performance",
        "e200z7 core Table 4-4",
    )
    (out / "core-table-4-4.txt").write_text(core_44, encoding="utf-8")
    base_rx = re.compile(r"[a-z][a-z0-9_.]*(?:\[[a-z.]+\])*")
    core_names = first_tokens(core_44, base_rx)
    reject = {
        "mnemonic", "latency", "serialization", "table", "continued",
        "freescale", "instruction", "e200z7",
    }
    core_names = [x for x in core_names if x not in reject]
    write_list(out / "core-mnemonic-index.txt", core_names)

    # Chapter 5 is the target-specific EFPU-v2 authority.  Preserve it whole;
    # the efs*/evfs* index is only a fast lookup view.
    efpu = between_re(
        core,
        r"Chapter 5\s+Embedded Floating-Point Unit",
        r"Chapter 6\s+Signal Processing Extension",
        "e200z7 EFPU chapter",
    )
    (out / "efpu-chapter-5.txt").write_text(efpu, encoding="utf-8")
    efpu_rx = re.compile(r"(?:efs|evfs)[a-z0-9_.]+")
    efpu_names = sorted(
        set(repeated_headings(efpu, efpu_rx)) | set(first_tokens(efpu, efpu_rx))
    )
    write_list(out / "efpu-mnemonic-index.txt", efpu_names)

    # VLEPEM Appendix B says it lists all instructions available in VLE mode.
    # Use the actual B.1 occurrence, not the TOC mention, and preserve B.1+B.2
    # through the real Index heading.  The e_/se_ view is intentionally partial.
    vle_b = between_re(
        vle,
        r"^\s*B\.1\s+VLE Instruction Set Sorted by Mnemonic\s*$",
        r"^\s*Index\s*$",
        "VLE Appendix B",
        last_start=True,
    )
    (out / "vle-appendix-b.txt").write_text(vle_b, encoding="utf-8")
    vle_rx = re.compile(r"(?:se|e)_[a-z0-9_.]+")
    vle_prefixed = sorted(set(vle_rx.findall(vle_b)))
    write_list(out / "vle-prefixed-mnemonic-index.txt", vle_prefixed)

    # SPEPEM Appendix B says it lists all SPE and embedded-FP instructions.
    # Preserve the complete appendix; the prefix view below is not advertised as
    # exhaustive because Appendix B also contains simplified/alias spellings.
    spe_b = between_re(
        spe,
        r"^\s*B\.1\s+Instructions \(Binary\) by Mnemonic\s*$",
        r"^\s*Index\s*$",
        "SPE Appendix B",
        last_start=True,
    )
    (out / "spe-appendix-b.txt").write_text(spe_b, encoding="utf-8")
    spe_rx = re.compile(r"(?:ev|ef)[a-z0-9_.]+|brinc")
    spe_prefixed = sorted(set(spe_rx.findall(spe_b)))
    write_list(out / "spe-prefixed-mnemonic-index.txt", spe_prefixed)

    manifest = {
        "manuals": {
            "core": {
                "title": "e200z7 Power Architecture Core Reference Manual, Rev. 2",
                "sha256": hashlib.sha256(core_pdf.read_bytes()).hexdigest(),
            },
            "vle": {
                "title": "VLE Programming Environments Manual, Rev. 0",
                "sha256": hashlib.sha256(vle_pdf.read_bytes()).hexdigest(),
            },
            "spe": {
                "title": "SPE Programming Environments Manual, Rev. 0",
                "sha256": hashlib.sha256(spe_pdf.read_bytes()).hexdigest(),
            },
        },
        "canonical_complete_sections": [
            "core-table-4-4.txt",
            "efpu-chapter-5.txt",
            "vle-appendix-b.txt",
            "spe-appendix-b.txt",
        ],
        "navigation_index_counts": {
            "core_mnemonic_index": len(core_names),
            "efpu_mnemonic_index": len(efpu_names),
            "vle_e_se_prefixed_index": len(vle_prefixed),
            "spe_ev_ef_prefixed_index": len(spe_prefixed),
        },
        "note": (
            "canonical extracted text blocks are the completeness oracle; "
            "normalized/prefix lists are convenience indexes only"
        ),
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
