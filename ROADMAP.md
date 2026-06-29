# Roadmap

Roadmap items describe intent, not a compatibility promise. Correctness and evidence gate each phase.

## 0.1 — Foundation

- [x] Recover from an exact layer marker in plain G-code.
- [x] Generate recovery G-code, unified diff, and Markdown report.
- [x] Recognize basic Bambu/Orca/Prusa and Cura layer comments.
- [x] Require explicit opt-in for risky homing.
- [x] Reject input/output path collisions.
- [x] Add golden artifact and failure-path tests.
- [ ] Define a stable diagnostic and risk taxonomy.

## 0.2 — Reliable recovery

- [ ] Recover by Z height.
- [x] Discover and read embedded plate G-code from sliced 3MF files.
- [ ] Interpret slicer-specific 3MF relationships and plate metadata beyond filename conventions.
- [ ] Add explicit Bambu, Orca, Prusa, and Cura dialect adapters.
- [ ] Reconstruct coordinate, extrusion, fan, temperature, offset, and tool state.
- [ ] Generate a recovery manifest with input digest and tool version.
- [ ] Build a fixture corpus from documented slicer versions.
- [ ] Add collision and clearance risk reporting.

## 0.3 — Recovery eligibility

- [ ] Define deterministic recoverable, risky, and refused outcomes.
- [ ] Refuse recovery when required coordinate, extrusion, tool, or position evidence is missing.
- [ ] Accept an explicit observed failure boundary without embedding printer monitoring.
- [ ] Validate approach motion against known printer geometry and retained toolpaths.
- [ ] Produce machine-readable diagnostics alongside the human report.

## 1.0 — Stable recovery engine

- [ ] Stable library and command-line APIs.
- [ ] Lossless intermediate representation with source maps.
- [ ] Verified recovery transformations.
- [ ] Versioned slicer dialect and printer recovery policies.
- [ ] Compatibility fixtures for supported slicer, firmware, and printer combinations.
- [ ] Five documented, supervised real-print recoveries with no unsafe motion.

## Release gate

A feature leaves experimental status only when its syntax is documented, representative fixtures exist, repeated execution is deterministic, and unresolved safety assumptions are explicit.
