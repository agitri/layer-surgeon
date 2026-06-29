from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .domain.models import (
    GCodeDocument,
    RecoveryArtifacts,
    RecoveryPlan,
    RecoverySettings,
)


@dataclass(frozen=True)
class ArtifactTargets:
    gcode: Path
    unified_diff: Path
    report: Path


class SourceReader(Protocol):
    def supports(self, path: Path) -> bool: ...

    def read(self, path: Path, plate: int | None = None) -> GCodeDocument: ...


class RecoveryPlanBuilder(Protocol):
    def create_plan(
        self,
        source: GCodeDocument,
        settings: RecoverySettings,
    ) -> RecoveryPlan: ...


class GCodeRenderer(Protocol):
    def render(self, plan: RecoveryPlan) -> str: ...


class UnifiedDiffRenderer(Protocol):
    def render(self, plan: RecoveryPlan) -> str: ...


class RecoveryReportRenderer(Protocol):
    def render(self, plan: RecoveryPlan) -> str: ...


class ArtifactWriter(Protocol):
    def validate(self, input_path: Path, targets: ArtifactTargets) -> None: ...

    def write(
        self,
        targets: ArtifactTargets,
        artifacts: RecoveryArtifacts,
    ) -> None: ...
