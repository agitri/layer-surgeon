from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern

from .errors import LayerNotFoundError
from .models import GCodeAnalysis, GCodeDocument, LayerMarker


@dataclass(frozen=True)
class LayerSyntax:
    pattern: Pattern[str]
    includes_total: bool = False


class GCodeAnalyzer:
    _layer_syntaxes = (
        LayerSyntax(
            re.compile(r"^;\s*layer\s+num/total_layer_count:\s*(\d+)\s*/\s*(\d+)", re.I),
            includes_total=True,
        ),
        LayerSyntax(re.compile(r"^;\s*LAYER:\s*(\d+)", re.I)),
        LayerSyntax(re.compile(r"^;\s*layer\s+(\d+)", re.I)),
    )
    _z_move = re.compile(r"\bZ(-?\d+(?:\.\d+)?)\b", re.I)
    _bed_temp = re.compile(r"^M(?:140|190)\s+S(\d+(?:\.\d+)?)", re.I)
    _nozzle_temp = re.compile(r"^M(?:104|109)\s+S(\d+(?:\.\d+)?)", re.I)

    def analyze(self, document: GCodeDocument) -> GCodeAnalysis:
        markers: list[LayerMarker] = []
        first_z_by_layer: dict[int, float] = {}
        bed_temp: float | None = None
        nozzle_temp: float | None = None
        current_layer: int | None = None

        for line_index, line in enumerate(document.lines):
            detected_layer = self._detect_layer(line)
            if detected_layer is not None:
                current_layer, total = detected_layer
                markers.append(LayerMarker(current_layer, total, line_index, line.rstrip("\r\n")))

            bed_temp = self._first_value(bed_temp, self._bed_temp, line)
            nozzle_temp = self._first_value(nozzle_temp, self._nozzle_temp, line)
            self._record_first_z(first_z_by_layer, current_layer, line)

        enriched_markers = tuple(
            LayerMarker(
                layer=marker.layer,
                total=marker.total,
                line_index=marker.line_index,
                text=marker.text,
                z_height=first_z_by_layer.get(marker.layer),
            )
            for marker in markers
        )
        return GCodeAnalysis(enriched_markers, bed_temp, nozzle_temp)

    def find_layer(self, analysis: GCodeAnalysis, target_layer: int) -> LayerMarker:
        marker = next(
            (candidate for candidate in analysis.layers if candidate.layer == target_layer),
            None,
        )
        if marker is not None:
            return marker

        available = ", ".join(str(candidate.layer) for candidate in analysis.layers[:10])
        if len(analysis.layers) > 10:
            available += ", ..."
        raise LayerNotFoundError(
            f"Layer {target_layer} not found. Available layers start with: {available}"
        )

    def _detect_layer(self, line: str) -> tuple[int, int | None] | None:
        stripped = line.strip()
        for syntax in self._layer_syntaxes:
            match = syntax.pattern.search(stripped)
            if match is None:
                continue
            total = int(match.group(2)) if syntax.includes_total else None
            return int(match.group(1)), total
        return None

    @staticmethod
    def _first_value(
        current: float | None,
        pattern: Pattern[str],
        line: str,
    ) -> float | None:
        if current is not None:
            return current
        match = pattern.search(line)
        return float(match.group(1)) if match is not None else None

    def _record_first_z(
        self,
        first_z_by_layer: dict[int, float],
        current_layer: int | None,
        line: str,
    ) -> None:
        if current_layer is None or current_layer in first_z_by_layer:
            return
        match = self._z_move.search(line)
        if match is not None:
            first_z_by_layer[current_layer] = float(match.group(1))
