# Architecture

## Architectural style

Layer Surgeon uses a pragmatic hexagonal architecture. The objective is to isolate safety-sensitive recovery rules from file formats, presentation formats, storage, and user interfaces without creating a class hierarchy for every function.

```text
CLI / recovery library consumers
              |
              v
       Application use cases
              |
              v
            Ports
              ^
              |
 Filesystem / 3MF / renderers / printer adapters

       Domain sits at the center
```

Allowed dependency direction:

```text
composition and CLI -> adapters -> application -> domain
                         |             |
                         +---- ports <-+
```

The domain imports no adapter, application, filesystem, ZIP, Markdown, or CLI code.

## Package responsibilities

### `layer_surgeon/domain/`

The domain contains deterministic recovery concepts and rules:

- `models.py`: immutable source, analysis, settings, plan, and artifact models.
- `analysis.py`: G-code layer and basic machine-state analysis.
- `recovery.py`: recovery planning and preamble policy.
- `errors.py`: typed, expected failure categories.

Domain collections exposed by immutable models use tuples. Temporary mutable collections remain local implementation details.

### `layer_surgeon/application/`

Application use cases coordinate domain behavior through ports:

- `recover_print.py`: select a source reader, build a recovery plan, render artifacts, and persist them.

The application layer decides workflow order. It does not know how ZIP files, Markdown, diffs, or filesystem writes work.

### `layer_surgeon/ports.py`

Ports are small `Protocol` interfaces for independent capabilities:

- source reading;
- recovery-plan construction;
- recovery G-code rendering;
- unified-diff rendering;
- report rendering;
- artifact validation and persistence.

The protocols use structural typing. Adapters do not inherit from framework base classes.

### `layer_surgeon/adapters/`

Adapters connect infrastructure and presentation formats to ports:

- `sources/plain_gcode.py`: UTF-8 plain G-code input.
- `sources/three_mf.py`: 3MF validation, discovery, selection, decompression policy, and decoding.
- `renderers/gcode.py`: recovery G-code serialization.
- `renderers/diff.py`: Git-style unified diff serialization.
- `renderers/report.py`: Markdown report serialization.
- `filesystem.py`: path policy and artifact persistence.

The 3MF adapter separates archive validation, candidate selection, compressed-member reading, and source adaptation into focused classes. These classes remain in one module because they implement one external format and are not independently reusable yet.

### Composition and CLI

- `composition.py` is the composition root. It selects concrete adapters and wires the dependency graph.
- `cli.py` parses arguments, creates an application command, invokes the use case, and presents the result.

No other module should instantiate the complete dependency graph.

## Recovery flow

```text
RecoverPrintCommand
        |
        v
validate artifact targets
        |
        v
select SourceReader -> GCodeDocument + provenance
        |
        v
RecoveryPlanner -> RecoveryPlan
        |
        +--> RecoveryGCodeRenderer
        +--> UnifiedDiffRenderer
        +--> RecoveryReportRenderer
        |
        v
RecoveryArtifacts -> ArtifactWriter
```

The recovery plan is the stable boundary between analysis/planning and serialization. Renderers cannot change the selected layer, temperatures, homing policy, or retained source lines.

## Failure model

Expected failures derive from `LayerSurgeonError`:

- `SourceError`
- `SourceSelectionError`
- `UnsafeArchiveError`
- `LayerNotFoundError`
- `ArtifactPathError`
- `ArtifactWriteError`

Adapters translate infrastructure failures into these user-facing categories. The CLI handles this base type without knowing adapter implementation details. Programming errors are not swallowed.

## Extension rules

### Add an input format

1. Implement the `SourceReader` protocol in `adapters/sources/`.
2. Return a `GCodeDocument` with complete `SourceProvenance`.
3. Register the adapter in `composition.py`.
4. Add adapter and application-level tests.

Recovery planning and renderers must not change.

### Add a report format

Implement a focused renderer protocol and wire it through a use case or a new artifact bundle. Do not add format flags to the domain plan.

### Add printer-specific policy

Introduce a small policy port consumed by `RecoveryPlanner`. Printer policy belongs in the domain-facing planning boundary; printer communication belongs in an adapter.

## Testing and enforcement

- Golden tests lock exact recovery G-code, unified diff, and report output.
- Domain tests exercise analysis and recovery planning without filesystem access.
- Adapter tests cover 3MF and filesystem behavior.
- Application and CLI tests cover dependency wiring and end-to-end workflows.
- Architecture tests reject forbidden domain-to-infrastructure and application-to-adapter imports.
- Ruff enforces formatting, import order, and selected control-flow rules.
- Strict mypy validates models and protocol boundaries.

Required checks:

```bash
pytest
ruff check layer_surgeon tests
ruff format --check layer_surgeon tests
mypy
```

## Deliberate constraints

- Prefer composition over inheritance.
- Add a class when it owns a coherent responsibility or varying implementation, not merely to wrap a function.
- Use guard clauses for invalid states; do not hide genuine decision tables behind polymorphism.
- Avoid `Manager`, `Helper`, `Utils`, service locators, and global registries.
- Keep the composition root explicit.
- Do not create plugin machinery until independent third-party implementations require it.
- Preserve source provenance through every stage.
- Keep all transformations deterministic and artifact output reviewable.
