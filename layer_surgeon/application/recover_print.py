from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..domain.errors import SourceError
from ..domain.models import RecoveryArtifacts, RecoveryPlan, RecoverySettings
from ..ports import (
    ArtifactTargets,
    ArtifactWriter,
    GCodeRenderer,
    RecoveryPlanBuilder,
    RecoveryReportRenderer,
    SourceReader,
    UnifiedDiffRenderer,
)


@dataclass(frozen=True)
class RecoverPrintCommand:
    input_path: Path
    targets: ArtifactTargets
    settings: RecoverySettings
    plate: int | None = None


@dataclass(frozen=True)
class RecoveryExecution:
    plan: RecoveryPlan
    artifacts: RecoveryArtifacts
    targets: ArtifactTargets


class RecoverPrint:
    def __init__(
        self,
        source_readers: tuple[SourceReader, ...],
        planner: RecoveryPlanBuilder,
        gcode_renderer: GCodeRenderer,
        diff_renderer: UnifiedDiffRenderer,
        report_renderer: RecoveryReportRenderer,
        artifact_writer: ArtifactWriter,
    ) -> None:
        self._source_readers = source_readers
        self._planner = planner
        self._gcode_renderer = gcode_renderer
        self._diff_renderer = diff_renderer
        self._report_renderer = report_renderer
        self._artifact_writer = artifact_writer

    def execute(self, command: RecoverPrintCommand) -> RecoveryExecution:
        self._artifact_writer.validate(command.input_path, command.targets)
        reader = self._select_reader(command.input_path)
        source = reader.read(command.input_path, command.plate)
        plan = self._planner.create_plan(source, command.settings)
        artifacts = RecoveryArtifacts(
            gcode=self._gcode_renderer.render(plan),
            unified_diff=self._diff_renderer.render(plan),
            report=self._report_renderer.render(plan),
        )
        self._artifact_writer.write(command.targets, artifacts)
        return RecoveryExecution(plan, artifacts, command.targets)

    def _select_reader(self, path: Path) -> SourceReader:
        reader = next(
            (candidate for candidate in self._source_readers if candidate.supports(path)),
            None,
        )
        if reader is None:
            raise SourceError(f"No source reader supports {path}")
        return reader
