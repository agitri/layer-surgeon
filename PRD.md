# Product Requirements

## Product statement

Layer Surgeon is an open-source, auditable toolchain for inspecting and transforming G-code. Its first product is deterministic recovery of failed 3D prints from a selected layer.

## Problem

Long prints can fail near completion. Reprinting wastes time, material, and energy, while manually editing G-code is opaque and can cause collisions, thermal mistakes, or incorrect extrusion state.

## Vision

Become the Git of G-code: a transparent, reproducible foundation for monitoring, recovery, diagnosis, comparison, patching, explanation, visualization, and optimization.

## Users

- Printer operators recovering valuable failed prints.
- Advanced users investigating slicer output or printer behavior.
- Tool authors building G-code analysis and transformation workflows.
- Contributors adding slicer and printer support.

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

## Planned monitoring and incident reconstruction

Layer Surgeon should provide an opt-in printer flight recorder that:

- collects timestamped job, progress, layer, Z-height, temperature, fan, speed, tool, printer-state, and error telemetry when exposed by the printer;
- supports vendor-neutral adapters, initially targeting Bambu MQTT, PrusaLink, OctoPrint, and Moonraker;
- associates each monitoring session with a source-file digest and printer identity;
- correlates telemetry with source G-code layers and line ranges;
- records state transitions and optional camera snapshots;
- produces an incident report containing the last healthy state, first abnormal state, reported error, likely failure layer or line range, and confidence level;
- recommends a recovery boundary without automatically controlling the printer.

The system must distinguish reported facts from inferred locations. Printer telemetry often cannot identify the exact command being physically executed, and mechanical failures may not produce firmware errors. Command-level claims require stronger evidence, such as a host-reported file position or an instrumented G-code stream.

## Long-term fleet recovery

Layer Surgeon should scale from one printer to print-farm operation with hundreds of concurrent machines. A fleet service should:

- maintain independent, reconnectable monitoring sessions per printer;
- retain an append-only incident history linked to printer, job, source digest, and generated artifacts;
- identify a failed job and reconstruct the best-supported recovery boundary;
- generate and validate recovery G-code deterministically;
- apply printer-specific policy before any automated action;
- queue a recovery job only when evidence and configured confidence thresholds allow it;
- prevent duplicate commands and repeated recovery loops through idempotency keys and attempt limits;
- expose fleet-wide health, incidents, pending approvals, and recovery outcomes;
- retain an operator kill switch and complete audit trail.

Fully automatic restart is a controlled execution mode, not the default. It requires reliable printer control adapters, physical-state evidence, collision and state validation, explicit operator policy, and bounded retry behavior. AI may classify an incident or recommend a boundary, but deterministic code must generate and validate the recovery artifact.

## Quality attributes

- **Transparent:** every changed line is diffable.
- **Deterministic:** output has no hidden state or network dependency.
- **Reproducible:** reports expose the decisions needed to repeat a recovery.
- **Tested:** parser dialects, transformations, refusals, and risks have regression coverage.
- **Extensible:** parsing, analysis, policy, and rendering remain separable.

## Non-goals for the current product

- Automatically controlling a printer.
- Guaranteeing collision-free motion.
- Repairing physically displaced prints.
- Re-slicing models.
- Silently normalizing arbitrary G-code dialects.
