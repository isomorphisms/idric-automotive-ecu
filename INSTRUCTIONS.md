# S32K3 Cortex-M7 complete instruction inventory

Status: source-backed architecture inventory, independent of the Idriç implementation subset.

## Exact target profile

The S32K3 family uses Arm Cortex-M7 application cores. NXP's current S32K3 data sheet identifies the CPU instruction profile as Armv7 + Thumb-2 with the DSP extension and an integrated **single-precision floating-point unit**.

For architecture purposes, pin this branch to:

- **Armv7E-M / T32 (Thumb-2)** — Armv7-M plus the DSP extension;
- the Cortex-M7 system instruction model;
- the **single-precision** Armv7-M floating-point profile implemented by S32K3;
- no double-precision FP instructions unless a concrete S32K3 part is shown by its authoritative data sheet to implement them.

The architecture manual applicable to Cortex-M7 is **Armv7-M Architecture Reference Manual, ARM DDI 0403E.e, ID021621**.

## Completeness oracle

Arm DDI 0403E.e is organized so that completeness can be checked mechanically:

- Chapter **A7.7, Alphabetical list of Armv7-M Thumb instructions**, states that **every Armv7-M Thumb instruction is listed in that section**;
- each instruction is a numbered heading `A7.7.N` and contains every architectural encoding/form, with applicability such as Armv7-M, Armv7E-M, and floating-point extension requirements;
- Chapter **B5** supplies the complete system-level definitions for `CPS`, `MRS`, and `MSR` and the special-register operand encodings;
- Chapters A5 and A6 are the encoding oracles for T32 and floating-point instructions respectively.

`tools/extract-armv7m-instructions.py` accepts the official E.e PDF, runs `pdftotext -layout`, and extracts every numbered A7.7 instruction description in order. It retains the entire text block for each instruction so extension/version/encoding lines are not lost. It separately indexes the three B5 system instruction definitions and emits a profile report for Armv7E-M and floating-point annotations.

The raw extracted blocks are the architecture record. A later normalizer may split instruction headings into individual T1/T2/T3/etc. encoding rows, but it may not omit any encoding in the source block.

## S32K3 profile selection

The full Armv7-M manual includes optional architecture material. The S32K3 profile is selected as follows:

1. retain every base Armv7-M instruction/encoding applicable to Cortex-M7;
2. retain every encoding marked **Armv7E-M** / DSP extension;
3. retain floating-point encodings supported by the **single-precision** implementation;
4. reject double-precision-only FP encodings;
5. retain privileged/system instructions even when the first Idriç program never emits them;
6. preserve architectural aliases and pre-UAL synonyms as aliases rather than counting them as new encodings.

This separation matters: the complete Armv7-M manual is the architecture universe, while S32K3's DSP/SP-FPU feature mask determines which optional rows are available on the target.

## Independent machine-readable cross-check

For assembler/disassembler/code-generation cross-checking, pin LLVM's Arm target at:

- repository: `llvm/llvm-project`
- commit: `74253d0e4f01fca3c2cc526aee9d073af3fad919`
- root: `llvm/lib/Target/ARM/ARM.td` and recursively included TableGen files.

LLVM TableGen records preserve concrete Thumb/Thumb-2/DSP/FP instruction forms and feature predicates. They are a useful independent check against the official manual, but the Arm manual remains the normative completeness oracle.

## Idriç support

The Idriç follower backend can begin with a tiny scalar Thumb-2 subset. Its support table is separate; unsupported DSP, FP, barrier, exception, privileged, saturation or packed-SIMD instructions remain in this complete architecture inventory.
