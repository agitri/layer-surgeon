import difflib

from ...domain.models import RecoveryPlan


class DifflibUnifiedDiffRenderer:
    def render(self, plan: RecoveryPlan) -> str:
        lines = difflib.unified_diff(
            plan.source.lines,
            plan.output_lines,
            fromfile=plan.source.provenance.display_name,
            tofile=f"recovery_layer_{plan.settings.target_layer}.gcode",
            lineterm="",
        )
        return "".join(line if line.endswith("\n") else line + "\n" for line in lines)
