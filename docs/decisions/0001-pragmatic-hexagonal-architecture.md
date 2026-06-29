# ADR 0001: Pragmatic Hexagonal Architecture

- Status: Accepted
- Date: 2026-06-29

## Context

The initial MVP correctly demonstrated recovery behavior but concentrated source detection, 3MF processing, G-code analysis, planning, rendering, and filesystem writes in a few procedural modules. Adding printer adapters, monitoring, or fleet automation to that structure would increase branching and couple physical-machine policy to infrastructure details.

The project needs SOLID boundaries, but a deeply layered framework or class-per-function design would add ceremony without improving correctness.

## Decision

Adopt a pragmatic hexagonal architecture with:

- an infrastructure-independent domain;
- application use cases that coordinate work;
- small structural-typing ports;
- concrete source, renderer, persistence, and future printer adapters;
- one explicit composition root;
- typed expected failures;
- immutable domain models;
- golden artifact tests plus automated formatting and strict type checking.

Classes represent cohesive responsibilities or replaceable behavior. Pure calculations may remain functions or methods where no independent abstraction is required.

## Consequences

Positive:

- New source and printer integrations do not change recovery rules.
- Recovery rules can be tested without ZIP files, a filesystem, or printers.
- CLI, future web, and fleet workers can share application use cases.
- Artifact formats remain independently replaceable and reviewable.
- Dependency direction is visible in the package tree.

Costs:

- More modules and constructor wiring than the MVP.
- Ports and composition require disciplined naming.
- Cross-cutting changes may touch a command, use case, model, and adapter deliberately rather than one large module.

## Rejected alternatives

- **Keep the procedural MVP:** simple now, but source formats and fleet features would compound branching and coupling.
- **Full enterprise Clean Architecture:** too much indirection for the current project size.
- **Inheritance-heavy service hierarchy:** nominal base classes provide less flexibility than Python protocols and composition.
- **Plugin framework immediately:** premature until independent external integrations exist.
