# Roadmap

Roadmap items describe intent, not a compatibility promise. Correctness and evidence gate each phase.

## 0.1 — Foundation

- [x] Recover from an exact layer marker in plain G-code.
- [x] Generate recovery G-code, unified diff, and Markdown report.
- [x] Recognize basic Bambu/Orca/Prusa and Cura layer comments.
- [x] Require explicit opt-in for risky homing.
- [x] Reject input/output path collisions.
- [ ] Add golden artifact and failure-path tests.
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

## 0.3 — Monitoring and incident reconstruction

- [ ] Add a vendor-neutral telemetry event model and append-only flight-recorder format.
- [ ] Add read-only adapters for Bambu MQTT and PrusaLink.
- [ ] Add OctoPrint and Moonraker adapters with source-position correlation where available.
- [ ] Associate monitored jobs with source-file digests and printer identities.
- [ ] Record job state, progress, layer/Z position, temperatures, fans, speed, tool state, and reported errors.
- [ ] Support timestamped camera snapshots without making computer vision a recovery prerequisite.
- [ ] Correlate telemetry with likely G-code layers and source ranges, including an explicit confidence level.
- [ ] Generate an incident report with the last healthy state, first abnormal state, and recommended recovery boundary.
- [ ] Keep monitoring read-only by default; printer control requires a separate explicit capability and safety policy.

## 0.4 — Inspection and patching

- [ ] `diff` command.
- [ ] `doctor` and `validate` commands.
- [ ] `explain` command.
- [ ] Visual layer and toolpath comparison.
- [ ] Machine-readable patch format and `patch` command.

## 1.0 — Stable toolchain

- [ ] Stable library and command-line APIs.
- [ ] Lossless intermediate representation with source maps.
- [ ] Verified transformation passes.
- [ ] Plugin SDK for dialects, analyzers, printer profiles, and transformations.
- [ ] GUI and editor integrations backed by the same core engine.

## Post-1.0 — Fleet recovery automation

- [ ] Monitor hundreds of printers through horizontally scalable adapter workers.
- [ ] Persist append-only job and incident timelines with source and artifact digests.
- [ ] Add fleet health, incident, approval, and recovery dashboards.
- [ ] Add a policy engine for per-printer and per-farm autonomy levels.
- [ ] Validate physical and machine state before generating or dispatching recovery jobs.
- [ ] Add idempotent job dispatch, bounded retries, lockout after repeated failure, and an operator kill switch.
- [ ] Support automatic recovery generation and restart only for policy-approved, high-confidence incidents.
- [ ] Preserve every decision, generated artifact, command, and outcome in an audit trail.

## Later exploration

- AI-assisted failure classification and recovery recommendations. Deterministic code remains responsible for all G-code transformations.
- Hosted collaboration services.
- Slicer and printer-management integrations beyond the monitoring adapters.

## Release gate

A feature leaves experimental status only when its syntax is documented, representative fixtures exist, repeated execution is deterministic, and unresolved safety assumptions are explicit.
