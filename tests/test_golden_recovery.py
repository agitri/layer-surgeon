from layer_surgeon.adapters.renderers import (
    DifflibUnifiedDiffRenderer,
    MarkdownRecoveryReportRenderer,
    RecoveryGCodeRenderer,
)
from layer_surgeon.domain.analysis import GCodeAnalyzer
from layer_surgeon.domain.models import GCodeDocument, RecoverySettings, SourceProvenance
from layer_surgeon.domain.recovery import RecoveryPlanner

SOURCE_LINES = (
    "M140 S60\n",
    "M104 S220\n",
    "; layer num/total_layer_count: 111/120\n",
    "G1 Z22.200 F600\n",
    "G1 X1 Y1 E0.1\n",
    "; layer num/total_layer_count: 112/120\n",
    "G1 Z22.400 F600\n",
    "G1 X5 Y5 E0.1\n",
)

EXPECTED_GCODE = """; ------------------------------
; Layer Surgeon recovery file
; Start layer: 112
; Profile: bambu-h2s
; WARNING: Recovery print can collide with the existing part. Watch first moves.
; ------------------------------
M140 S60 ; set bed temperature
M104 S220 ; set nozzle temperature
; G28 intentionally omitted: position must already be valid
M190 S60 ; wait for bed temperature
M109 S220 ; wait for nozzle temperature
G90 ; absolute positioning
M83 ; relative extrusion
G92 E0 ; reset extruder
G1 Z23.400 F600 ; move just above recovery layer
G1 Z22.400 F300 ; move to recovery Z
; ---- original G-code resumes below ----
; layer num/total_layer_count: 112/120
G1 Z22.400 F600
G1 X5 Y5 E0.1
"""

EXPECTED_DIFF = """--- original.gcode
+++ recovery_layer_112.gcode
@@ -1,8 +1,20 @@
-M140 S60
-M104 S220
-; layer num/total_layer_count: 111/120
-G1 Z22.200 F600
-G1 X1 Y1 E0.1
+; ------------------------------
+; Layer Surgeon recovery file
+; Start layer: 112
+; Profile: bambu-h2s
+; WARNING: Recovery print can collide with the existing part. Watch first moves.
+; ------------------------------
+M140 S60 ; set bed temperature
+M104 S220 ; set nozzle temperature
+; G28 intentionally omitted: position must already be valid
+M190 S60 ; wait for bed temperature
+M109 S220 ; wait for nozzle temperature
+G90 ; absolute positioning
+M83 ; relative extrusion
+G92 E0 ; reset extruder
+G1 Z23.400 F600 ; move just above recovery layer
+G1 Z22.400 F300 ; move to recovery Z
+; ---- original G-code resumes below ----
 ; layer num/total_layer_count: 112/120
 G1 Z22.400 F600
 G1 X5 Y5 E0.1
"""

EXPECTED_REPORT = """# Layer Surgeon recovery report

## Input

- Source file: original.gcode
- Target layer: 112
- Printer profile: bambu-h2s
- Original lines removed before recovery: 5
- Original total lines: 8
- Recovery total lines: 20

## Recovery settings

- Z height detected: 22.4
- Bed temperature: 60.0
- Nozzle temperature: 220.0
- Risky homing: NO - homing omitted

## Warnings

- Keep one hand near the power switch.
- Stop immediately if the nozzle or bed approaches the existing part incorrectly.
- This file is intended for recovery only and should not replace the original sliced output.
"""


def test_recovery_artifacts_match_golden_output():
    source = GCodeDocument(SOURCE_LINES, SourceProvenance("original.gcode"))
    plan = RecoveryPlanner(GCodeAnalyzer()).create_plan(
        source,
        RecoverySettings(target_layer=112, printer_profile="bambu-h2s"),
    )

    assert RecoveryGCodeRenderer().render(plan) == EXPECTED_GCODE
    assert DifflibUnifiedDiffRenderer().render(plan) == EXPECTED_DIFF
    assert MarkdownRecoveryReportRenderer().render(plan) == EXPECTED_REPORT
