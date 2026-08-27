# Cortex-M7 / S32K3 follower

This branch follows `isomorphisms/idric-arm-thumb`; it does not define an independent Arm compiler.

## Reuse first

Keep existing Thumb-2 lowering, integer operations, loads/stores, branches, calls, stack handling, and object emission wherever the pinned Cortex-M7 ABI and execution profile allow them unchanged.

## Automotive delta

Research and implement only the differences needed to execute on an S32K3-class Cortex-M7 target:

- M-profile execution/startup
- reset entry and vector table
- linker script and memory map
- exception/interrupt boundary
- applicable floating-point/DSP options
- eventual peripheral access

## First oracle

A minimal bare-metal program must start from reset, establish the stack, call a function, perform integer arithmetic and a conditional branch, write/read RAM, and expose one deterministic result. The generated Idriç path should reuse the upstream Arm implementation wherever possible.

Tracked by issue #2.
