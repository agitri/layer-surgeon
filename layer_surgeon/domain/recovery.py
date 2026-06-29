from __future__ import annotations

from .analysis import GCodeAnalyzer
from .models import GCodeDocument, RecoveryPlan, RecoverySettings


class RecoveryPlanner:
    def __init__(self, analyzer: GCodeAnalyzer) -> None:
        self._analyzer = analyzer

    def create_plan(
        self,
        source: GCodeDocument,
        settings: RecoverySettings,
    ) -> RecoveryPlan:
        analysis = self._analyzer.analyze(source)
        marker = self._analyzer.find_layer(analysis, settings.target_layer)
        bed_temp = self._prefer_override(settings.bed_temp, analysis.bed_temp)
        nozzle_temp = self._prefer_override(settings.nozzle_temp, analysis.nozzle_temp)
        preamble = self._build_preamble(settings, marker.z_height, bed_temp, nozzle_temp)

        return RecoveryPlan(
            source=source,
            settings=settings,
            start_line=marker.line_index,
            z_height=marker.z_height,
            bed_temp=bed_temp,
            nozzle_temp=nozzle_temp,
            preamble=preamble,
        )

    @staticmethod
    def _prefer_override(override: float | None, detected: float | None) -> float | None:
        return detected if override is None else override

    def _build_preamble(
        self,
        settings: RecoverySettings,
        z_height: float | None,
        bed_temp: float | None,
        nozzle_temp: float | None,
    ) -> tuple[str, ...]:
        return (
            *self._banner(settings),
            *self._temperature_command("M140", bed_temp, "set bed temperature"),
            *self._temperature_command("M104", nozzle_temp, "set nozzle temperature"),
            self._homing_command(settings),
            *self._temperature_command("M190", bed_temp, "wait for bed temperature"),
            *self._temperature_command("M109", nozzle_temp, "wait for nozzle temperature"),
            "G90 ; absolute positioning\n",
            "M83 ; relative extrusion\n",
            "G92 E0 ; reset extruder\n",
            *self._z_commands(z_height),
            "; ---- original G-code resumes below ----\n",
        )

    @staticmethod
    def _banner(settings: RecoverySettings) -> tuple[str, ...]:
        if not settings.add_comment_banner:
            return ()
        return (
            "; ------------------------------\n",
            "; Layer Surgeon recovery file\n",
            f"; Start layer: {settings.target_layer}\n",
            f"; Profile: {settings.printer_profile}\n",
            "; WARNING: Recovery print can collide with the existing part. Watch first moves.\n",
            "; ------------------------------\n",
        )

    @staticmethod
    def _temperature_command(
        command: str,
        temperature: float | None,
        comment: str,
    ) -> tuple[str, ...]:
        if temperature is None:
            return ()
        return (f"{command} S{temperature:g} ; {comment}\n",)

    @staticmethod
    def _homing_command(settings: RecoverySettings) -> str:
        if settings.risk_allow_homing:
            return "G28 ; RISKY: home all axes before recovery\n"
        return "; G28 intentionally omitted: position must already be valid\n"

    @staticmethod
    def _z_commands(z_height: float | None) -> tuple[str, ...]:
        if z_height is None:
            return ()
        return (
            f"G1 Z{z_height + 1.0:.3f} F600 ; move just above recovery layer\n",
            f"G1 Z{z_height:.3f} F300 ; move to recovery Z\n",
        )
