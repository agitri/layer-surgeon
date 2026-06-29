# Contributing

Layer Surgeon treats G-code transformations as safety-sensitive changes. Contributions are welcome, but convenience is not a substitute for evidence.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Before changing code

Read `AGENTS.md`, `PRD.md`, `ARCHITECTURE.md`, and `ROADMAP.md`. For domain behavior, also read the relevant document under `docs/`.

## Change requirements

- Add focused tests for new behavior and fixed defects.
- Include failure and risk paths, not only successful output.
- Preserve unknown G-code unless the change is an explicit transformation.
- Keep behavior deterministic.
- Update user-facing documentation and `CHANGELOG.md` for visible changes.
- Explain any printer- or slicer-specific assumption in code and documentation.

Do not commit proprietary or personally identifying G-code fixtures. Minimize fixtures while preserving the syntax needed for the test, and record the slicer and version when known.

## Pull requests

Describe the observed problem, the evidence behind the solution, generated artifact changes, and safety implications. A parser change should include representative input. A transformation change should show its G-code and unified-diff output.

## Reporting safety defects

Clearly label issues that could cause collisions, unintended heating, extrusion errors, or unsafe motion. Include the command, relevant input excerpt, actual output, expected refusal or warning, printer/slicer context, and Layer Surgeon version. Do not send generated recovery G-code to a printer merely to confirm a suspected defect.
