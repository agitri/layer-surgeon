from ...domain.models import RecoveryPlan


class MarkdownRecoveryReportRenderer:
    def render(self, plan: RecoveryPlan) -> str:
        input_details = self._input_details(plan)
        risk = self._risk_description(plan)
        return f"""# Layer Surgeon recovery report

## Input

{input_details}
- Target layer: {plan.settings.target_layer}
- Printer profile: {plan.settings.printer_profile}
- Original lines removed before recovery: {plan.start_line}
- Original total lines: {plan.original_line_count}
- Recovery total lines: {plan.output_line_count}

## Recovery settings

- Z height detected: {self._display(plan.z_height)}
- Bed temperature: {self._display(plan.bed_temp)}
- Nozzle temperature: {self._display(plan.nozzle_temp)}
- Risky homing: {risk}

## Warnings

- Keep one hand near the power switch.
- Stop immediately if the nozzle or bed approaches the existing part incorrectly.
- This file is intended for recovery only and should not replace the original sliced output.
"""

    @staticmethod
    def _input_details(plan: RecoveryPlan) -> str:
        provenance = plan.source.provenance
        details = [f"- Source file: {provenance.container_name}"]
        if provenance.member_path is not None:
            plate = provenance.plate if provenance.plate is not None else "unknown"
            details.extend(
                [
                    f"- 3MF G-code member: {provenance.member_path}",
                    f"- 3MF plate: {plate}",
                ]
            )
        return "\n".join(details)

    @staticmethod
    def _risk_description(plan: RecoveryPlan) -> str:
        if plan.settings.risk_allow_homing:
            return "YES - G28 homing is included"
        return "NO - homing omitted"

    @staticmethod
    def _display(value: float | None) -> str:
        return str(value) if value is not None else "unknown"
