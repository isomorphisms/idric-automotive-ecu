# RH850 follower

RH850 is the first distinct non-Arm automotive follower backend.

## Gate

Do not broaden implementation until a clean, reproducible assemble/link/execute loop exists using publicly obtainable documentation and tooling.

Pin the exact architecture level, ABI, register roles, stack/call convention, endianness, object format, relocations, and executable environment before emitting Idriç code.

## First emission surface

- integer constants and moves
- only the byte/halfword/word loads and stores needed by the first programs
- add/subtract and minimal logic
- compare/test and branches
- direct call and return
- required stack-frame operations
- one deterministic observable result

Keep the complete ISA inventory separate from this supported subset. Every generated case should have an independent executable oracle.

Tracked by issue #3.
