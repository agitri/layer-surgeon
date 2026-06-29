# Changelog

All notable project changes are documented here. The project follows the structure of Keep a Changelog; versioning policy will be finalized before the first stable release.

## Unreleased

### Added

- Project charter, product requirements, architecture, roadmap, contribution guide, and domain documentation.
- Historical record of the original product vision.
- Planned printer flight recorder, telemetry adapters, source correlation, and incident reporting feature.
- Safe embedded G-code discovery for sliced 3MF archives, including explicit multi-plate selection.
- Archive provenance in recovery diffs, reports, and CLI output.
- Long-term print-farm monitoring and policy-gated automatic recovery requirements.

### Changed

- Expanded README usage documentation with supported input formats, complete recovery workflow, option reference, artifact review steps, and explicit 3MF limitations.
- Enforced immutable input and distinct recovery artifact paths.
- Refactored the MVP into a pragmatic hexagonal architecture with immutable domain models, typed errors, protocol-based ports, focused adapters, a `RecoverPrint` use case, and an explicit composition root.
- Added Ruff and strict mypy as required development checks.

## 0.1.0

### Added

- Recovery from an exact layer marker in plain G-code.
- Common Bambu/Orca/Prusa and Cura layer comment recognition.
- Generated recovery G-code, unified diff, and Markdown report.
- Explicit opt-in for risky `G28` homing.
