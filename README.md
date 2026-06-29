# Layer Surgeon

Layer Surgeon is an open-source, auditable recovery tool for failed 3D prints—and the foundation of a compiler and debugger for G-code.

It takes an original G-code file, starts from a chosen layer, adds a small safety/recovery preamble, and produces:

- `recovery.gcode`
- `recovery.diff` — Git-style unified diff of every change
- `recovery_report.md` — readable summary

## Current MVP

- Generic G-code input
- Layer recovery by layer number
- Detects Bambu/Orca/Prusa-style layer comments such as `; layer num/total_layer_count: 112/120`
- Preserves all G-code from the chosen layer onward
- Optional risky homing mode
- Full unified diff output

## Install for local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
layer-surgeon recover \
  --input original.gcode \
  --layer 112 \
  --output recovery.gcode \
  --diff recovery.diff \
  --report recovery_report.md \
  --profile bambu-h2s \
  --risk-allow-homing
```

## Safety warning

Recovery G-code can crash into an existing part if the printer has lost position, the bed moved, or homing hits the print. Always watch the first moves with one hand near the power switch.

## Project direction

The long-term goal is the Git of G-code: deterministic tools to monitor, recover, diff, diagnose, explain, visualize, patch, and eventually optimize printer instruction streams.

- [Product requirements](PRD.md)
- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Documentation index](docs/README.md)
- [Long-term master plan](docs/masterplan.md)

Roadmap commands are not implemented until identified as complete in `ROADMAP.md` and documented here.

## License

MIT. See [LICENSE](LICENSE).
