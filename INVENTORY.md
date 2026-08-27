# Architecture inventory invariant

Every architecture branch in this repository must preserve **complete architecture knowledge separately from the Idriç subset that happens to be implemented**.

A branch is not considered inventoried merely because it links a manual or names instruction families.

## Required artifacts

Each architecture branch must carry an exhaustive, reproducible inventory containing at least:

- the exact core/ISA revision and silicon/profile assumptions;
- every architectural instruction mnemonic in that pinned scope;
- distinct encodings/operand forms where they change semantics or availability;
- extension membership such as DSP, floating-point, VLE, SPE, virtualization or safety/system facilities;
- aliases/pseudoinstructions clearly separated from real encodings;
- privileged/system instructions retained in the architecture record even when the first Idriç backend is user/bare-metal scalar only;
- provenance for the primary specification or permissively licensed machine-readable instruction data;
- a separate table for the subset Idriç currently emits.

For large ISAs, use a pinned reproducible extractor rather than a hand-maintained list. If public material is insufficient to prove completeness, say so explicitly; do not silently call a partial public subset complete.

## Current branches

| Branch | Architecture boundary |
| --- | --- |
| `follower/arm-cortex-m7-s32k3` | S32K3-class Cortex-M7: Armv7E-M / Thumb-2 plus the exact implemented DSP/FPU profile |
| `follower/power-e200z7` | Power Architecture e200z7, including the core Power, VLE, SPE and target-specific EFPU-v2 surfaces |
| `follower/rh850` | Separate complete RH850 G3M, G3K, G3MH, G3KH and G4MH architecture inventories; an executable Idriç backend must still pin one exact core profile |
| `reference/tricore-tc18` | Infineon TriCore TC1.8 reference architecture |

Follower/reference status controls implementation priority only; it does not relax the architecture-inventory requirement.
