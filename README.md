# Idriç automotive ECU

Follower compiler backends and automotive integration notes for Idriç.

The primary implementation remains [`idric-arm-thumb`](https://github.com/isomorphisms/idric-arm-thumb), developed against the real Arm/Thumb device in hand. Automotive targets follow that work rather than competing with it.

## Target policy

1. **Arm Cortex-M7 / NXP S32K3** — automotive follower using the existing Thumb-2 work wherever the architecture and ABI permit. Treat startup, vector tables, linker layout, memory map, FPU/DSP, and peripherals as automotive integration work rather than a new ISA design.
2. **Renesas RH850** — first distinct non-Arm automotive ISA follower. Public ISA/ABI material and GCC/binutils support make a reproducible tiny executable backend plausible.
3. **NXP Power e200z7** — later distinct follower. Keep the Power/VLE/SPE architecture work separate from modern 64-bit POWER server work.
4. **Infineon TriCore TC1.8** — reference-only for now. The architecture is worth documenting, but implementation waits for a reproducible way to execute compiler-generated TC1.8 code without proprietary production infrastructure.

Automotive RISC-V should follow the general RISC-V backend rather than fork into a separate ISA backend prematurely.

## Backend rule

For every follower, distinguish complete architecture knowledge from the deliberately tiny executable emission surface. Grow only from exact executable oracles: constants, loads/stores, integer arithmetic/logic, compare/branch, direct call/return, stack/ABI operations, and one observable output boundary.

AUTOSAR integration, ISO 26262 qualification, production safety certification, and vendor-specific peripheral breadth are outside the first compiler milestone.
