# Project Status

Last updated: 2026-06-29.

Layer Surgeon is paused with a deliberately narrow scope: recover a failed print from a defensible boundary, produce deterministic recovery G-code, and explain every change.

## Current status

The project is useful as an experimental, expert-supervised recovery tool. It is not yet a trustworthy real-world recovery engine.

Approximate progress:

- Written roadmap: 28%.
- Technical MVP for layer-based recovery: about 70%.
- Useful for expert-supervised experiments: about 45%.
- Trustworthy real-world recovery: about 25-30%.
- Production 1.0: about 15-20%.

## What works

- Plain G-code input.
- Sliced 3MF or `.gcode.3mf` input when embedded G-code is present.
- Explicit plate selection for multi-plate 3MF archives.
- Recovery from an exact slicer layer marker.
- Generated recovery G-code, unified diff, and Markdown report.
- Basic detection of first bed temperature, first nozzle temperature, and target layer Z height.
- Explicit opt-in for risky homing.
- Path-collision protection for generated artifacts.

## Known hard limit

The recovery preamble is not yet state-aware. It currently makes assumptions about positioning and extrusion state, including resetting extrusion with `G92 E0`.

That is not good enough for reliable recovery, especially for files using absolute extrusion or non-trivial modal state changes.

## Next implementation step

Build state reconstruction as a small deterministic G-code interpreter.

Minimum first milestone:

1. Add a lossless parsed-command model that preserves raw lines, comments, and source line numbers.
2. Add an explicit `MachineState` model with unknown values where evidence is missing.
3. Replay G-code up to the recovery boundary.
4. Track at least units, coordinate mode, extrusion mode, XYZ/E position, feed rate, active tool, bed/nozzle targets, and fan state.
5. Refuse recovery when coordinate, extrusion, tool, or position evidence is required but unknown.
6. Replace the hardcoded recovery preamble with a state-aware preamble.
7. Include reconstructed state evidence and refusals in the report and golden tests.

Critical rule: for absolute extrusion, the recovery preamble must restore absolute extrusion semantics and the reconstructed E value. It must not blindly reset extrusion to zero.

## Intentionally out of scope

- Printer monitoring.
- Print-farm management.
- Camera or AI failure detection.
- Hardware devices.
- Automatically restarting printers.
- General-purpose G-code optimization, visualization, or editing.
- Re-slicing model files.

These ideas may be revisited later, but they are not part of the current recovery-engine goal.
