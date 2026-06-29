# Product Requirements

## Product statement

Layer Surgeon is an open-source, auditable engine for determining whether a failed 3D print can be recovered and producing deterministic recovery G-code from an evidence-backed boundary.

## Problem

Long prints can fail near completion. Reprinting wastes time, material, and energy, while manually editing G-code is opaque and can cause collisions, thermal mistakes, or incorrect extrusion state.

## Goal

Given the original sliced job and a defensible recovery boundary, produce a recovery artifact that is deterministic, reviewable, and explicit about every unresolved risk.

## Users

- Printer operators recovering valuable failed prints.
- Advanced users validating a recovery before running it.
- Contributors adding recovery support for slicers and printers.

## Current product: layer recovery

Given an original G-code file and a target layer, Layer Surgeon must:

1. Locate the exact requested layer without modifying the input.
2. Preserve source G-code from that layer onward.
3. Add an explicit recovery preamble.
4. Produce new G-code, a unified diff, and a Markdown report.
5. Report detected temperatures, Z height, positioning assumptions, and risky operations.
6. Produce identical output for identical input and options.
7. Fail clearly when the requested layer does not exist.

## Safety requirements

- Homing is omitted by default because it can collide with the existing part.
- Requested homing is visibly marked as risky in output and report.
- Original files are immutable inputs.
- Unsupported or ambiguous syntax is surfaced rather than silently normalized.
- The tool reports evidence, assumptions, and risk; it does not claim physical safety.
- Operators are told to supervise initial moves and be ready to stop the printer.

## Current supported scope

- Plain G-code input.
- Sliced ZIP-based 3MF input with embedded G-code discovery.
- Explicit plate selection for multi-plate archives using `plate_<number>.gcode` member names.
- Recovery by layer number.
- Common Bambu/Orca/Prusa and Cura-style layer comments.
- Basic lexical extraction of nozzle temperature, bed temperature, and layer Z height.
- Optional, explicitly risky homing.

The profile option is currently a report label, not a printer-specific safety policy. Recovery by Z height, complete Bambu/Orca semantics, 3MF metadata interpretation, collision analysis, and state reconstruction remain roadmap work.

## Quality attributes

- **Transparent:** every changed line is diffable.
- **Deterministic:** output has no hidden state or network dependency.
- **Reproducible:** reports expose the decisions needed to repeat a recovery.
- **Tested:** parser dialects, transformations, refusals, and risks have regression coverage.
- **Extensible:** parsing, analysis, policy, and rendering remain separable.

## Non-goals for the current product

- Automatically controlling a printer.
- Monitoring printers or detecting failures.
- Managing print farms, queues, cameras, or fleets.
- Guaranteeing collision-free motion.
- Repairing physically displaced prints.
- Re-slicing models.
- General-purpose G-code optimization, visualization, or editing.
- Silently normalizing arbitrary G-code dialects.
