from ...domain.models import RecoveryPlan


class RecoveryGCodeRenderer:
    def render(self, plan: RecoveryPlan) -> str:
        return "".join(plan.output_lines)
