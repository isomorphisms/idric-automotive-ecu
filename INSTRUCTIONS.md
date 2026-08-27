# TriCore TC1.8 complete instruction inventory

Status: reference architecture inventory. Reference-only implementation priority does not relax completeness.

## Normative source

Infineon **TriCore TC1.8 architecture manual volume 2 — Instruction Set**, V1.0.0, 2024-02-14.

The manual explicitly states that Volume 2 gives a **complete description of the TriCore instruction set**, including optional MMU and FPU extensions. Its instruction chapter says it contains descriptions of **all TriCore instructions**. The architecture includes the 16-bit and 32-bit core forms, DSP/packed operations, floating-point families, double-precision TC1.8 operations, privileged/system operations and virtualization instructions.

AURIX TC4xx product documentation identifies its main CPUs as TC1.8 implementations, notes virtualization and double-precision IEEE-754-2019 FP relative to TC1.6, and separately states that the optional MMU is not implemented in that product family. Architecture inventory and product availability are therefore different columns.

## Exhaustive extraction

Every documented instruction has a numbered Chapter-3 subsection, for example `3.1.1 ABS`; the table of contents repeats the same numbered instruction set. `tools/extract-manual-instructions.py` extracts both sets independently from the official PDF and **fails unless TOC and body match exactly**.

The resulting TSV is the complete mnemonic/section inventory. Individual instruction pages remain the authority for:

- 16-bit versus 32-bit syntax/forms;
- exact opcode fields;
- RTL semantics;
- status flags;
- execution-mode/privilege restrictions;
- examples and related instructions.

A later structured pass may normalize those fields but may not remove any heading from the completeness-checked list.

## Implementation status

This branch remains reference-only unless public tooling/execution becomes adequate for a reproducible compiler-generated fixture. That status has no bearing on whether the architecture catalog itself is complete.
