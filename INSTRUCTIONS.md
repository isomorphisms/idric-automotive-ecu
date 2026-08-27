# e200z7 complete instruction inventory

Status: source-backed architecture inventory, independent of the Idriç implementation subset.

The e200z7 is not accurately described by one flat generic Power mnemonic list. This branch preserves four separately sourced instruction surfaces:

1. the e200z7 implemented base/embedded Power Architecture core instructions;
2. Variable-Length Encoding (VLE);
3. Signal Processing Engine (SPE);
4. the e200z7 Embedded Floating-Point Unit version 2 (EFPU v2).

## 1. e200z7 core instruction set

Canonical implementation source: **e200z7 Power Architecture Core Reference Manual, Rev. 2** (`e200z760RM`).

The manual's **Table 4-4, Instruction Timing by Mnemonic**, explicitly states that it gives detailed timing for **each instruction mnemonic** implemented by the core. That table is therefore the target-specific completeness oracle for the ordinary/core Power instructions, rather than importing the much larger contemporary server POWER ISA.

The inventory retains all of Table 4-4, including privileged/system, cache/TLB, reservation, exception-return and other operations that an initial Idriç compiler will not emit.

## 2. Variable-Length Encoding (VLE)

Canonical architecture source: **Variable-Length Encoding (VLE) Programming Environments Manual**, `VLEPEM`, Rev. 0, 07/2007.

The manual describes VLE as an extension to the base and embedded categories of the Power ISA. Its Appendix B explicitly **lists all instructions available in VLE mode**, first grouped by mnemonic and then by opcode. The complete VLE inventory is therefore the entire Appendix-B instruction table, preserving:

- every 16-bit `se_*` encoding;
- every 32-bit `e_*` encoding;
- supported non-VLE Power instructions listed by the manual for VLE mode;
- instruction format, opcode, privilege/mode and alias/simplified-mnemonic information.

Do not flatten a VLE spelling into a normal 32-bit Power instruction merely because the operation is semantically similar.

## 3. Signal Processing Engine (SPE)

Canonical architecture source: **Signal Processing Engine (SPE) Programming Environments Manual**, `SPEPEM`, Rev. 0.

Appendix B explicitly lists **all SPE and embedded-floating-point instructions**, grouped by mnemonic and opcode. The branch retains the complete Appendix-B table, including real encodings and simplified mnemonics/aliases. SPE contains the `ev*` vector/integer/DSP families plus operations such as `brinc`; aliases remain distinguishable from encoded instructions.

The e200z7 core reference manual's Chapter 6 is an implementation-specific cross-check for which SPE facilities and timings the core implements.

## 4. e200z7 EFPU version 2

The e200z7 core manual's Chapter 5 is the target-specific authority. It describes **Embedded Floating-Point Unit version 2** and gives the actual e200z7 instruction descriptions and opcode tables.

Important implementation boundary:

- scalar operations are single precision (`efs*`);
- vector operations are pairs of single-precision elements (`evfs*`);
- the ordinary Power ISA floating-point instructions are **not implemented** by e200z7;
- the target implements EFPU mode 0, not the optional mode 1;
- the manual warns that the architectural EFPU opcode space contains instructions not implemented by every CPU version, so the e200z7 chapter—not a generic EIS list—is the availability oracle.

The target-specific inventory is every `efs*` and `evfs*` instruction description present in Chapter 5 plus its Table 5-15/5-16/5-17 opcode data.

## Reproducible extraction

`tools/extract-e200z7-instructions.py CORE.pdf VLEPEM.pdf SPEPEM.pdf [output-dir]` runs `pdftotext -layout` and preserves these four **complete canonical sections**:

- `core-table-4-4.txt`;
- `efpu-chapter-5.txt`;
- `vle-appendix-b.txt`;
- `spe-appendix-b.txt`.

It also emits navigation indexes:

- `core-mnemonic-index.txt`;
- `efpu-mnemonic-index.txt`;
- `vle-prefixed-mnemonic-index.txt` — only the `e_` / `se_` subset of the complete VLE appendix;
- `spe-prefixed-mnemonic-index.txt` — a quick `ev*` / `ef*` / `brinc` lookup view, not a replacement for the complete SPE appendix.

Generation fails if the required manual sections are missing or a navigation extraction is empty. The preserved canonical manual sections—not the filtered indexes—are the completeness oracle.

## Idriç support

Follower-backend support is a separate matrix. Idriç can begin with a tiny scalar VLE or ordinary Power subset without deleting SPE, EFPU, privileged, cache/TLB, exception or other unsupported instructions from the architecture record.
