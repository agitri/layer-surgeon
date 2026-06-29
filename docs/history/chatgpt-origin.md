# Origin of Layer Surgeon

This document preserves the original product direction that motivated the repository. It is a historical record, not a claim that every command described here is implemented.

## Problem

Prints can fail at 95%, after most of their time and material have already been spent. Manual G-code recovery is opaque and risky.

## Initial vision

Layer Surgeon should become the Git of G-code: a serious open-source tool whose transformations are transparent, deterministic, reproducible, and diffable.

The first concrete product is failed-print recovery. Each recovery preserves its source, produces a new G-code file, shows every change as a unified diff, and explains its decisions in a report.

## Founding principles

- Never silently modify G-code.
- Preserve original files.
- Explain every recovery.
- Make identical inputs produce identical outputs.
- Surface safety assumptions and risk.
- Support the major slicer ecosystems: Bambu, Orca, Prusa, and Cura.
- Do not trade correctness for convenience.

## Larger direction

Recovery is version one. The larger opportunity is a compiler and debugger for G-code, with a tool vocabulary such as:

```bash
layer-surgeon recover model.3mf --layer 112
layer-surgeon diff old.gcode new.gcode
layer-surgeon doctor print.gcode
layer-surgeon optimize print.gcode
layer-surgeon visualize print.gcode
layer-surgeon explain print.gcode
layer-surgeon patch print.gcode patch.diff
```

The conceptual combination is Git-style provenance and diffs, compiler-style parsing and transformations, and debugger-style inspection and explanation for physical machine instructions.

## Why preserve this

Implementation details will change. This record exists so later architectural decisions can still be evaluated against the original problem: making G-code recovery and transformation understandable enough to trust.
