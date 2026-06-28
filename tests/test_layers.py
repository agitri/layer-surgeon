from layer_surgeon.gcode import analyze, find_layer_start
from layer_surgeon.recover import RecoveryOptions, recover_lines


def test_detects_bambu_layer_marker():
    lines = [
        "M104 S220\n",
        "; layer num/total_layer_count: 111/120\n",
        "G1 Z22.200 F600\n",
        "G1 X1 Y1 E0.1\n",
    ]
    analysis = analyze(lines)
    assert analysis.layers[0].layer == 111
    assert analysis.layers[0].total == 120
    assert analysis.layers[0].z_height == 22.2


def test_recover_starts_at_layer():
    lines = [
        "M104 S220\n",
        "; layer num/total_layer_count: 111/120\n",
        "G1 Z22.200 F600\n",
        "; layer num/total_layer_count: 112/120\n",
        "G1 Z22.400 F600\n",
        "G1 X5 Y5 E0.1\n",
    ]
    result = recover_lines(lines, RecoveryOptions(target_layer=112, risk_allow_homing=True))
    joined = "".join(result.output_lines)
    assert "; layer num/total_layer_count: 112/120" in joined
    assert "; layer num/total_layer_count: 111/120" not in joined
    assert "G28 ; RISKY" in joined
    assert result.z_height == 22.4
