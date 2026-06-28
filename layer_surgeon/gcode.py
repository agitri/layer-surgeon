from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

LAYER_PATTERNS = [
    re.compile(r"^;\s*layer\s+num/total_layer_count:\s*(\d+)\s*/\s*(\d+)", re.I),
    re.compile(r"^;\s*LAYER:\s*(\d+)", re.I),
    re.compile(r"^;\s*layer\s+(\d+)", re.I),
]
Z_MOVE_RE = re.compile(r"\bZ(-?\d+(?:\.\d+)?)\b", re.I)
BED_TEMP_RE = re.compile(r"^M(?:140|190)\s+S(\d+(?:\.\d+)?)", re.I)
NOZZLE_TEMP_RE = re.compile(r"^M(?:104|109)\s+S(\d+(?:\.\d+)?)", re.I)

@dataclass(frozen=True)
class LayerMarker:
    layer: int
    total: int | None
    line_index: int
    text: str
    z_height: float | None = None

@dataclass(frozen=True)
class GCodeAnalysis:
    layers: list[LayerMarker]
    bed_temp: float | None
    nozzle_temp: float | None
    first_z_by_layer: dict[int, float]


def read_lines(path: str | Path) -> list[str]:
    return Path(path).read_text(errors="replace").splitlines(keepends=True)


def write_lines(path: str | Path, lines: list[str]) -> None:
    Path(path).write_text("".join(lines))


def detect_layer(line: str) -> tuple[int, int | None] | None:
    stripped = line.strip()
    for i, pattern in enumerate(LAYER_PATTERNS):
        match = pattern.search(stripped)
        if not match:
            continue
        layer = int(match.group(1))
        total = int(match.group(2)) if i == 0 and len(match.groups()) >= 2 else None
        return layer, total
    return None


def analyze(lines: list[str]) -> GCodeAnalysis:
    layers: list[LayerMarker] = []
    bed_temp: float | None = None
    nozzle_temp: float | None = None
    first_z_by_layer: dict[int, float] = {}
    current_layer: int | None = None

    for idx, line in enumerate(lines):
        found = detect_layer(line)
        if found:
            current_layer, total = found
            layers.append(LayerMarker(current_layer, total, idx, line.rstrip("\n")))

        if bed_temp is None:
            m = BED_TEMP_RE.search(line)
            if m:
                bed_temp = float(m.group(1))
        if nozzle_temp is None:
            m = NOZZLE_TEMP_RE.search(line)
            if m:
                nozzle_temp = float(m.group(1))

        if current_layer is not None and current_layer not in first_z_by_layer:
            mz = Z_MOVE_RE.search(line)
            if mz:
                first_z_by_layer[current_layer] = float(mz.group(1))

    enriched = []
    for marker in layers:
        enriched.append(LayerMarker(
            layer=marker.layer,
            total=marker.total,
            line_index=marker.line_index,
            text=marker.text,
            z_height=first_z_by_layer.get(marker.layer),
        ))
    return GCodeAnalysis(enriched, bed_temp, nozzle_temp, first_z_by_layer)


def find_layer_start(lines: list[str], target_layer: int) -> LayerMarker:
    analysis = analyze(lines)
    for marker in analysis.layers:
        if marker.layer == target_layer:
            return marker
    available = ", ".join(str(m.layer) for m in analysis.layers[:10])
    if len(analysis.layers) > 10:
        available += ", ..."
    raise ValueError(f"Layer {target_layer} not found. Available layers start with: {available}")
