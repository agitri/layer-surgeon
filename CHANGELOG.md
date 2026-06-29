# Changelog

All notable project changes are documented here. The project follows the structure of Keep a Changelog; versioning policy will be finalized before the first stable release.

## Unreleased

### Added

- Project charter, product requirements, architecture, roadmap, contribution guide, and domain documentation.
- Historical record of the original product vision.
- Planned printer flight recorder, telemetry adapters, source correlation, and incident reporting feature.

### Changed

- Expanded README usage documentation with supported input formats, complete recovery workflow, option reference, artifact review steps, and explicit 3MF limitations.

## 0.1.0

### Added

- Recovery from an exact layer marker in plain G-code.
- Common Bambu/Orca/Prusa and Cura layer comment recognition.
- Generated recovery G-code, unified diff, and Markdown report.
- Explicit opt-in for risky `G28` homing.
