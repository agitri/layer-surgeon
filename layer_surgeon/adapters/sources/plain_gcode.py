from __future__ import annotations

from pathlib import Path

from ...domain.errors import SourceError, SourceSelectionError
from ...domain.models import GCodeDocument, SourceProvenance


class PlainGCodeReader:
    def supports(self, path: Path) -> bool:
        return path.suffix.casefold() in {".gcode", ".gco"}

    def read(self, path: Path, plate: int | None = None) -> GCodeDocument:
        if plate is not None:
            raise SourceSelectionError("--plate can only be used with a .3mf input")

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise SourceError(f"Unable to read G-code input {path}: {exc}") from exc

        return GCodeDocument.from_text(text, SourceProvenance(path.name))
