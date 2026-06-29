# Master Plan

## Direction

Layer Surgeon aims to become the Git of G-code: an open-source platform for monitoring, inspecting, recovering, comparing, patching, validating, and understanding 3D-printer jobs.

The mission is to build the most trusted recovery engine in the 3D-printing ecosystem through transparency, determinism, and rigorous engineering.

## Principles

1. Never silently modify G-code.
2. Make every modification reviewable.
3. Treat original files as immutable.
4. Produce deterministic output.
5. Put safety before convenience.
6. Remain vendor-neutral where practical.
7. Use AI as an advisor, never as an opaque transformation engine.

## Product pillars

- **Monitor:** record printer telemetry and reconstruct incidents as an auditable timeline.
- **Recover:** resume failed jobs from evidence-backed boundaries.
- **Diff:** compare instruction streams at text, command, layer, and path levels.
- **Explain:** translate machine instructions and diagnostics into understandable reasoning.
- **Patch:** apply reviewable, reproducible transformations.
- **Visualize:** inspect layers, paths, extrusion, and state transitions.
- **Validate:** find malformed syntax, unsafe assumptions, and inconsistent state.

## Target users

- Makers recovering individual prints.
- Print farms standardizing recovery and validation.
- Engineers debugging slicer and firmware behavior.
- Repair technicians diagnosing failed jobs.
- Open-source contributors extending dialect and printer support.

## Platform model

Every interface—CLI, GUI, editor integration, or hosted service—consumes the same UI-independent engine. The engine evolves toward lossless parsing, a provenance-preserving intermediate representation, state analysis, deterministic planning, printer policy, and multiple auditable renderers.

Printer profiles describe homing, startup, shutdown, geometry, tool configuration, and firmware quirks independently from slicer dialects.

Monitoring adapters remain separate from printer profiles. An adapter describes how telemetry is acquired; a profile describes how printer behavior should be interpreted.

## Recovery modes

- **Safe:** makes no unsupported position assumptions and never removes a required safety command.
- **Risky:** requires explicit acceptance for operations such as unsafe homing or recovery with unresolved state.
- **Experimental:** exposes research behavior with no stability promise.

These labels require a formal policy before they become public compatibility guarantees.

## Diff and artifact model

Every transformation should eventually emit:

- transformed G-code;
- a unified text diff;
- a machine-readable patch or manifest;
- a human-readable report.

Later comparison layers include visual layer diffs, path diffs, extrusion diffs, and machine-state diffs.

## AI boundary

AI may estimate a failure layer, classify a failure, explain diagnostics, or recommend a recovery strategy. AI does not directly edit G-code. A deterministic engine validates and performs every transformation.

## Ecosystem

The core remains permissively licensed and open-source. Extension points should support printer profiles, dialect adapters, analyzers, and transformation plugins. Hosted AI or collaboration services may be commercial without reducing the capability or auditability of the local core.

## Long-term outcome

When a print fails, the default community response should be: "Run Layer Surgeon."
