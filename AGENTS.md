# Layer Surgeon Agent Instructions

## Mission

Build the most trusted transparent G-code recovery engine, then grow it into a compiler and debugger for G-code.

## Required context

Before changing code, read:

1. `PRD.md` for current product requirements.
2. `ARCHITECTURE.md` for existing and target boundaries.
3. `ROADMAP.md` for implementation status and priorities.
4. The relevant domain document linked from `docs/README.md`.

## Rules

1. Never silently modify G-code.
2. Every recovery produces a new G-code file, a unified diff, and a human-readable report.
3. Preserve original files and reject input/output path collisions.
4. Classify behavior as safe, risky, or experimental; never imply physical safety without evidence.
5. Prefer deterministic algorithms and explicit refusals over heuristics.
6. Add tests for every feature and defect, including failure and risk paths.
7. Keep parsing, analysis, recovery policy, rendering, and CLI concerns separate.
8. Preserve unknown commands and comments unless an explicit transformation changes them.
9. Isolate slicer and printer behavior behind adapters as those abstractions are introduced.
10. Keep documentation and `CHANGELOG.md` synchronized with user-visible behavior.

## Workflow

- Propose the design before a major refactor.
- Keep changes small and reviewable.
- Do not describe roadmap features as implemented.
- Verify behavior with tests and inspect generated G-code, diff, and report artifacts.

## Definition of done

A feature is complete only when it is deterministic, tested, documented, reviewable, and produces explainable output.
