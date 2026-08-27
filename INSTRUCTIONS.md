# RH850 complete core-family instruction inventories

Status: source-backed architecture corpus, independent of the Idriç implementation subset.

`RH850` is not one frozen ISA. Renesas's current CC-RH toolchain exposes five distinct CPU-core profiles through `-Xcpu`:

- `g3m`
- `g3k`
- `g3mh`
- `g3kh`
- `g4mh`

Renesas's RH850 simulator likewise says it executes each of those core architectures separately. This branch therefore keeps **five complete inventories**, not one misleading union presented as if every RH850 device implemented it.

## Canonical software manuals

| Core | Canonical instruction source |
| --- | --- |
| G3M | **RH850G3M User's Manual: Software**, R01US0123EJ0140, Rev.1.40 |
| G3K | **RH850G3K User's Manual: Software**, Rev.1.20 |
| G3MH | **RH850G3MH User's Manual: Software**, R01US0143EJ0130, Rev.1.30, 2016-12-22 |
| G3KH | **RH850G3KH User's Manual: Software**, R01US0165EJ0120, Rev.1.20, 2016-12-22 |
| G4MH | **RH850G4MH User's Manual: Software**, R01US0209EJ0220, Rev.2.20, 2023-12-20 |

Use the corresponding Renesas product/software manual, not a generic V850 mnemonic page, as the encoding/semantics authority.

## What counts as the complete instruction set

The manuals split real instruction descriptions into separately numbered **Instruction Set** sections. For example:

- G3MH/G3KH: `7.2.2 Basic Instruction Set`, `7.3.2 Cache Instruction Set`, and `7.4.4 Floating-Point Instruction Set`;
- G4MH: `2.2.3 Basic Instruction Set`, `2.3.2 Cache Instruction Set`, and `2.4.4 Floating-Point Instruction Set`.

The G4MH Rev.2.20 table of contents, for example, enumerates 120 basic instruction descriptions before the cache and floating-point sets. G3MH and G3KH have their own separately numbered catalogs and differ in architecture behavior and available FP facilities. G3KH documents single-precision FP support; G3MH documents both single- and double-precision-capable configurations; G4MH adds newer instruction forms and must not be flattened back to G3M.

Each instruction-description page preserves:

- mnemonic and all assembler operand forms;
- operation/semantics;
- opcode and instruction format, including 16/32/48/64-bit forms where defined;
- affected flags;
- exceptions and privilege/operating restrictions;
- core-specific notes.

Cache, floating-point, privileged, context-management and other instructions stay in the architecture inventory even when the first Idriç backend never emits them.

## Reproducible completeness check

`tools/extract-rh850-manual.py MANUAL.pdf [output-dir]` does not hard-code a short mnemonic list. It uses the manual itself as the oracle:

1. run `pdftotext -layout`;
2. parse the table of contents for every section whose title ends in **Instruction Set**;
3. collect every immediate numbered child entry of every such section;
4. require a matching exact numbered instruction heading in the body for every TOC entry;
5. retain the full body text block for every instruction as JSONL;
6. emit a TSV index and manifest with the manual hash and per-instruction-set counts;
7. fail if any TOC instruction is absent from the body or if no instruction-set section is found.

This automatically handles the different section numbering used by G3 and G4 manuals and includes basic, cache, floating-point, and any additional future section explicitly named `... Instruction Set` by the pinned manual.

## Family corpus versus follower backend

The complete architecture corpus is now deliberately broader than the first executable follower. `TARGET.md` still requires selecting **one exact core profile** before generated Idriç code is called an RH850 backend. That later choice does not delete the other four complete architecture inventories.

For an actual device, apply its optional-coprocessor/cache/MPU availability after selecting the core manual. Do not infer that an optional FPU exists merely because its core architecture manual describes the instruction set.

## Idriç support

The Idriç support matrix is separate. A tiny first G3M/G3MH/etc. lowering surface must never be substituted for the complete core instruction catalog.
