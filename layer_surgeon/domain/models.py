from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceProvenance:
    container_name: str
    member_path: str | None = None
    plate: int | None = None

    @property
    def display_name(self) -> str:
        if self.member_path is None:
            return self.container_name
        return f"{self.container_name}:{self.member_path}"


@dataclass(frozen=True)
class GCodeDocument:
    lines: tuple[str, ...]
    provenance: SourceProvenance

    @classmethod
    def from_text(cls, text: str, provenance: SourceProvenance) -> GCodeDocument:
        return cls(tuple(text.splitlines(keepends=True)), provenance)


@dataclass(frozen=True)
class LayerMarker:
    layer: int
    total: int | None
    line_index: int
    text: str
    z_height: float | None = None


@dataclass(frozen=True)
class GCodeAnalysis:
    layers: tuple[LayerMarker, ...]
    bed_temp: float | None
    nozzle_temp: float | None


@dataclass(frozen=True)
class RecoverySettings:
    target_layer: int
    printer_profile: str = "generic"
    risk_allow_homing: bool = False
    bed_temp: float | None = None
    nozzle_temp: float | None = None
    add_comment_banner: bool = True


@dataclass(frozen=True)
class RecoveryPlan:
    source: GCodeDocument
    settings: RecoverySettings
    start_line: int
    z_height: float | None
    bed_temp: float | None
    nozzle_temp: float | None
    preamble: tuple[str, ...]

    @property
    def retained_lines(self) -> tuple[str, ...]:
        return self.source.lines[self.start_line :]

    @property
    def output_lines(self) -> tuple[str, ...]:
        return self.preamble + self.retained_lines

    @property
    def original_line_count(self) -> int:
        return len(self.source.lines)

    @property
    def output_line_count(self) -> int:
        return len(self.output_lines)


@dataclass(frozen=True)
class RecoveryArtifacts:
    gcode: str
    unified_diff: str
    report: str
