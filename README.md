# Layer Surgeon

Layer Surgeon is an open-source, auditable recovery engine for failed 3D prints.

It takes plain G-code or G-code discovered inside a sliced 3MF package, starts from a chosen layer, adds an explicit recovery preamble, and produces:

- `recovery.gcode`
- `recovery.diff` — Git-style unified diff of every change
- `recovery_report.md` — readable summary

## What works today

- Plain G-code input.
- Automatic G-code discovery in sliced `.3mf` and `.gcode.3mf` archives.
- Explicit plate selection for multi-plate 3MF archives.
- Recovery by an exact slicer layer number.
- Bambu/Orca/Prusa-style markers such as `; layer num/total_layer_count: 112/120`.
- Cura-style markers such as `;LAYER:112`.
- Preservation of the original G-code from the selected layer onward.
- Basic detection of bed temperature, nozzle temperature, and layer Z height.
- Optional, explicitly risky homing.
- Unified diff and recovery report generation.

Printer profiles are currently labels included in the generated report. They do not yet change recovery behavior or provide printer-specific safety validation.

## Supported input

| Input | Current status |
| --- | --- |
| Plain `.gcode` | Supported |
| Sliced Bambu/Orca `.gcode.3mf` containing plate G-code | Supported |
| `.3mf` containing exactly one embedded `.gcode` | Supported |
| Multi-plate `.3mf` containing `plate_<number>.gcode` members | Supported with `--plate` |
| Unsliced project `.3mf` containing no G-code | Not supported |
| STL, STEP, OBJ | Not supported; Layer Surgeon is not a slicer |

3MF is a container format and does not guarantee that sliced G-code is present. Layer Surgeon reads embedded `.gcode` members directly from the archive without extracting files to disk. If no G-code exists, it refuses the input and asks for a sliced 3MF or plain G-code file.

## Install for local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Confirm that the CLI is available:

```bash
layer-surgeon --help
layer-surgeon recover --help
```

## Recover a print from a layer

Assume the print failed during layer 111 and layer 112 is the first layer that should be printed again.

Run:

```bash
layer-surgeon recover \
  --input original.gcode \
  --layer 112 \
  --output recovery.gcode \
  --diff recovery.diff \
  --report recovery_report.md \
  --profile bambu-h2s
```

Layer Surgeon will:

1. Find the exact layer 112 marker in `original.gcode`.
2. Detect its first associated Z height and the first configured temperatures in the file.
3. Generate a recovery preamble.
4. Append the unchanged source G-code from layer 112 onward.
5. Write the recovery file, unified diff, and report.

The original file is immutable input. Layer Surgeon rejects paths that would overwrite it and requires three distinct output paths.

### Recover from a sliced 3MF

If the 3MF contains exactly one embedded G-code file, discovery is automatic:

```bash
layer-surgeon recover \
  --input print.gcode.3mf \
  --layer 112 \
  --output recovery.gcode \
  --diff recovery.diff \
  --report recovery_report.md
```

If multiple plate G-code files exist, Layer Surgeon refuses to guess. Select the intended plate explicitly:

```bash
layer-surgeon recover \
  --input multi-plate.gcode.3mf \
  --plate 2 \
  --layer 112 \
  --output recovery.gcode \
  --diff recovery.diff \
  --report recovery_report.md
```

Plate discovery currently recognizes embedded names ending in `plate_<number>.gcode`, including the Bambu/Orca convention `Metadata/plate_2.gcode`. Generic embedded `.gcode` members are accepted when there is only one candidate.

### Choosing the layer

Layer numbers come from slicer comments inside the G-code. Numbering conventions can differ between slicers, so inspect the source before choosing a recovery layer:

```gcode
; layer num/total_layer_count: 112/120
G1 Z22.400 F600
```

The command requires an exact recognized marker. It fails if the requested layer is absent. Recovery by Z height is not implemented yet.

### Options

| Option | Meaning |
| --- | --- |
| `--input` | Original plain `.gcode` or sliced `.3mf`/`.gcode.3mf` file. |
| `--plate` | Plate number when a 3MF contains multiple `plate_<number>.gcode` members. |
| `--layer` | Exact layer number at which retained source G-code begins. |
| `--output` | New recovery G-code path. |
| `--diff` | Unified diff output path. |
| `--report` | Markdown recovery report path. |
| `--profile` | Informational printer-profile label; default: `generic`. |
| `--bed-temp` | Override the detected bed temperature. |
| `--nozzle-temp` | Override the detected nozzle temperature. |
| `--risk-allow-homing` | Insert `G28`; this is collision-prone and omitted by default. |

Example with explicit temperature overrides:

```bash
layer-surgeon recover \
  --input original.gcode \
  --layer 112 \
  --output recovery.gcode \
  --diff recovery.diff \
  --report recovery_report.md \
  --bed-temp 60 \
  --nozzle-temp 220
```

## Review the generated artifacts

Do not send `recovery.gcode` directly to a printer without inspection.

1. Read `recovery_report.md` for detected state, assumptions, and warnings.
2. Review `recovery.diff` to see every removed and inserted line.
3. Inspect the recovery preamble and the first retained layer in `recovery.gcode`.
4. Confirm physical alignment, clearance, coordinate state, extrusion state, and temperatures on the actual printer.

## Safety warning

Recovery G-code can crash into an existing part if the printer has lost position, the bed or part moved, or homing intersects the print. Omitting homing does not prove that the printer still has valid coordinates. Always supervise the first moves and be ready to stop the machine.

## Project direction

The goal is narrow: determine whether a failed print is recoverable, reconstruct the required machine state, and produce deterministic recovery G-code with a complete diff and risk report. Monitoring, farm management, printer control, visualization, optimization, and general-purpose G-code editing are out of scope.

- [Product requirements](PRD.md)
- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Documentation index](docs/README.md)

## License

MIT. See [LICENSE](LICENSE).
