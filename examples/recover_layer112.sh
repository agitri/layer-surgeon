#!/usr/bin/env bash
set -euo pipefail
layer-surgeon recover \
  --input original_plate_1.gcode \
  --layer 112 \
  --output recovery_layer112.gcode \
  --diff recovery_layer112.diff \
  --report recovery_layer112_report.md \
  --profile bambu-h2s \
  --risk-allow-homing
