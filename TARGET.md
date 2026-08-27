# Power e200z7 follower

This is a later automotive follower and a deliberately separate 32-bit embedded Power target. Do not conflate it with modern 64-bit POWER server work.

## Gate

Pin the e200z7 architecture, VLE/SPE documentation, embedded Power ABI, object/relocation conventions, and a reproducible assemble/link/execute path before implementing compiler emission.

## First emission surface

Start only with what a tiny executable Idriç program needs: constants, loads/stores, integer arithmetic/logic, compare/branch, direct call/return, stack/ABI operations, and one observable result.

VLE mixed-width encoding and SPE facilities belong in the architecture inventory first. Emit them only when a concrete program requires them.

Priority remains behind the real Arm/Thumb line and the first RH850 executable slice.

Tracked by issue #4.
