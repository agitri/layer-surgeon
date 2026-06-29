from __future__ import annotations

from pathlib import Path

from ..domain.errors import ArtifactPathError, ArtifactWriteError
from ..domain.models import RecoveryArtifacts
from ..ports import ArtifactTargets


class FilesystemArtifactWriter:
    def validate(self, input_path: Path, targets: ArtifactTargets) -> None:
        resolved_input = input_path.resolve()
        resolved_outputs = tuple(
            path.resolve() for path in (targets.gcode, targets.unified_diff, targets.report)
        )

        if resolved_input in resolved_outputs:
            raise ArtifactPathError(
                "Input and output paths must be different; original files are immutable"
            )
        if len(set(resolved_outputs)) != len(resolved_outputs):
            raise ArtifactPathError("Recovery G-code, diff, and report paths must be different")

    def write(
        self,
        targets: ArtifactTargets,
        artifacts: RecoveryArtifacts,
    ) -> None:
        try:
            targets.gcode.write_text(artifacts.gcode, encoding="utf-8")
            targets.unified_diff.write_text(artifacts.unified_diff, encoding="utf-8")
            targets.report.write_text(artifacts.report, encoding="utf-8")
        except OSError as exc:
            raise ArtifactWriteError(f"Unable to write recovery artifacts: {exc}") from exc
