from layer_surgeon.domain.analysis import GCodeAnalyzer
from layer_surgeon.domain.models import GCodeDocument, RecoverySettings, SourceProvenance
from layer_surgeon.domain.recovery import RecoveryPlanner


def document(lines: tuple[str, ...]) -> GCodeDocument:
    return GCodeDocument(lines, SourceProvenance("original.gcode"))


def test_detects_bambu_layer_marker():
    source = document(
        (
            "M104 S220\n",
            "; layer num/total_layer_count: 111/120\n",
            "G1 Z22.200 F600\n",
            "G1 X1 Y1 E0.1\n",
        )
    )

    analysis = GCodeAnalyzer().analyze(source)

    assert analysis.layers[0].layer == 111
    assert analysis.layers[0].total == 120
    assert analysis.layers[0].z_height == 22.2


def test_recovery_plan_starts_at_selected_layer():
    source = document(
        (
            "M104 S220\n",
            "; layer num/total_layer_count: 111/120\n",
            "G1 Z22.200 F600\n",
            "; layer num/total_layer_count: 112/120\n",
            "G1 Z22.400 F600\n",
            "G1 X5 Y5 E0.1\n",
        )
    )
    planner = RecoveryPlanner(GCodeAnalyzer())

    plan = planner.create_plan(
        source,
        RecoverySettings(target_layer=112, risk_allow_homing=True),
    )
    output = "".join(plan.output_lines)

    assert "; layer num/total_layer_count: 112/120" in output
    assert "; layer num/total_layer_count: 111/120" not in output
    assert "G28 ; RISKY" in output
    assert plan.z_height == 22.4
