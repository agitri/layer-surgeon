# Layer Surgeon

Layer Surgeon is an auditable recovery tool for failed 3D prints.

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
pip install -e .
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

## Roadmap

- 3MF extraction and plate G-code discovery
- Visual layer diff
- Z-height based recovery
- Printer-specific adapters
- Collision risk report
- Half-layer recovery
- Web UI
