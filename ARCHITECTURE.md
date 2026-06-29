# Architecture

## Current system

Layer Surgeon is a Python 3.10+ command-line application with no runtime dependencies.

```text
CLI arguments
    |
    v
G-code parsing and analysis
    |
    v
Recovery policy and preamble generation
    |
    +--> recovery G-code
    +--> unified diff
    +--> Markdown report
```

## Current modules

- `layer_surgeon/cli.py`: command-line parsing and completion output.
- `layer_surgeon/gcode.py`: text I/O, layer recognition, and basic state extraction.
- `layer_surgeon/recover.py`: recovery options, preamble generation, source preservation, diff generation, and reporting.
- `tests/`: behavioral and parser tests.
- `examples/`: executable usage examples.

The package is intentionally small. Splitting it into directories before responsibilities require independent implementations would add structure without isolation.

## Recovery data flow

1. Read input text while preserving line endings.
2. Analyze layer markers, temperatures, and per-layer Z heights.
3. Find the exact requested layer or fail.
4. Resolve explicit temperature options before detected values.
5. Build an annotated recovery preamble.
6. Append the untouched source suffix beginning at the layer marker.
7. Render recovery G-code, unified diff, and report.

## Target boundaries

As support grows, introduce boundaries in this order:

- **Reader:** decoding, line identity, archive and 3MF extraction.
- **Dialect adapter:** slicer and firmware syntax recognition.
- **Intermediate representation:** commands, comments, layers, machine state, and source provenance.
- **Analyzer:** state reconstruction, hazards, invariants, and diagnostics.
- **Planner:** deterministic recovery plans and future transformation passes.
- **Policy:** printer-profile constraints and risk classification.
- **Renderer:** G-code, patches, reports, and visualization data.

Every intermediate node should retain source provenance so transformed lines and diagnostics can be traced to input.

## Design constraints

- Parsing preserves unknown commands and comments.
- Analysis does not mutate parsed input.
- Transformations are deterministic and independently testable.
- Printer-specific behavior does not leak into generic parsing.
- Generated and preserved content remain distinguishable.
- Refusals and warnings are stable, tested product behavior.
- The core library remains independent of any future GUI or hosted service.

## Testing strategy

- Unit tests for marker and machine-state parsing.
- Golden tests for complete G-code, diff, and report artifacts.
- Fixtures produced by documented slicer versions.
- Property tests for preservation and determinism once an intermediate representation exists.
- Safety regressions for homing, coordinate mode, extrusion mode, temperatures, offsets, and missing state.

## Safety boundary

G-code controls physical machinery. Treat input as untrusted text and generated files as safety-sensitive artifacts. Layer Surgeon provides analysis and transformation, not a guarantee that a print is physically recoverable.
