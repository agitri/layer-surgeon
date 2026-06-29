from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZIP_STORED, BadZipFile, ZipFile, ZipInfo

from ...domain.errors import SourceError, SourceSelectionError, UnsafeArchiveError
from ...domain.models import GCodeDocument, SourceProvenance


@dataclass(frozen=True)
class GCodeCandidate:
    member_path: str
    plate: int | None
    uncompressed_size: int


class ThreeMFArchiveValidator:
    def validate(self, infos: tuple[ZipInfo, ...]) -> None:
        seen: set[str] = set()
        file_names: set[str] = set()

        for info in infos:
            self._validate_member_path(info.filename, seen)
            seen.add(info.filename)
            if not info.is_dir():
                file_names.add(info.filename.casefold())

        if "[content_types].xml" not in file_names:
            raise UnsafeArchiveError(
                "Input is a ZIP archive but not a valid 3MF package: [Content_Types].xml is missing"
            )
        if not any(name.endswith(".model") for name in file_names):
            raise UnsafeArchiveError(
                "Input is a ZIP archive but not a valid 3MF package: no 3D model part was found"
            )

    @staticmethod
    def _validate_member_path(name: str, seen: set[str]) -> None:
        if name in seen:
            raise UnsafeArchiveError(f"3MF package contains a duplicate member: {name}")
        if "\\" in name:
            raise UnsafeArchiveError(f"3MF package contains an invalid member path: {name}")

        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise UnsafeArchiveError(f"3MF package contains an unsafe member path: {name}")


class GCodeMemberSelector:
    _plate_name = re.compile(r"(?:^|/)plate_(\d+)\.gcode$", re.IGNORECASE)

    def candidates(self, infos: tuple[ZipInfo, ...]) -> tuple[GCodeCandidate, ...]:
        candidates = (
            self._candidate(info)
            for info in infos
            if not info.is_dir() and info.filename.casefold().endswith(".gcode")
        )
        return tuple(sorted(candidates, key=lambda item: item.member_path.casefold()))

    def select(
        self,
        candidates: tuple[GCodeCandidate, ...],
        plate: int | None,
        container_name: str,
    ) -> GCodeCandidate:
        if not candidates:
            raise SourceSelectionError(
                f"No embedded .gcode was found in {container_name}. "
                "The file may be an unsliced 3MF project; export a sliced "
                ".gcode.3mf or plain .gcode file."
            )
        if plate is not None:
            return self._select_plate(candidates, plate, container_name)
        if len(candidates) == 1:
            return candidates[0]
        raise SourceSelectionError(
            f"Multiple embedded G-code files were found in {container_name}: "
            f"{self._describe(candidates)}. Select one with --plate."
        )

    def _select_plate(
        self,
        candidates: tuple[GCodeCandidate, ...],
        plate: int,
        container_name: str,
    ) -> GCodeCandidate:
        if plate < 1:
            raise SourceSelectionError("Plate number must be greater than zero")

        matches = tuple(candidate for candidate in candidates if candidate.plate == plate)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            paths = ", ".join(candidate.member_path for candidate in matches)
            raise SourceSelectionError(f"Plate {plate} is ambiguous in {container_name}: {paths}")

        available = ", ".join(
            str(candidate.plate) for candidate in candidates if candidate.plate is not None
        )
        suffix = f" Available plates: {available}." if available else ""
        raise SourceSelectionError(f"Plate {plate} was not found in {container_name}.{suffix}")

    def _candidate(self, info: ZipInfo) -> GCodeCandidate:
        match = self._plate_name.search(info.filename)
        plate = int(match.group(1)) if match is not None else None
        return GCodeCandidate(info.filename, plate, info.file_size)

    @staticmethod
    def _describe(candidates: tuple[GCodeCandidate, ...]) -> str:
        return ", ".join(
            f"plate {candidate.plate}: {candidate.member_path}"
            if candidate.plate is not None
            else candidate.member_path
            for candidate in candidates
        )


class GCodeMemberReader:
    def __init__(
        self,
        max_uncompressed_bytes: int = 512 * 1024 * 1024,
        max_compression_ratio: int = 200,
    ) -> None:
        self._max_uncompressed_bytes = max_uncompressed_bytes
        self._max_compression_ratio = max_compression_ratio

    def read(self, archive: ZipFile, info: ZipInfo) -> str:
        self._validate(info)
        with archive.open(info) as member:
            content = member.read(self._max_uncompressed_bytes + 1)

        if len(content) > self._max_uncompressed_bytes:
            raise UnsafeArchiveError(
                f"Embedded G-code exceeds the {self._max_uncompressed_bytes}-byte "
                f"safety limit: {info.filename}"
            )
        return content.decode("utf-8", errors="replace")

    def _validate(self, info: ZipInfo) -> None:
        if info.flag_bits & 0x1:
            raise UnsafeArchiveError(f"Encrypted G-code members are not supported: {info.filename}")
        if info.compress_type not in {ZIP_STORED, ZIP_DEFLATED}:
            raise UnsafeArchiveError(f"Unsupported 3MF compression method for {info.filename}")
        if info.file_size > self._max_uncompressed_bytes:
            raise UnsafeArchiveError(
                f"Embedded G-code exceeds the {self._max_uncompressed_bytes}-byte "
                f"safety limit: {info.filename}"
            )
        if self._compression_ratio(info) > self._max_compression_ratio:
            raise UnsafeArchiveError(
                f"Embedded G-code compression ratio exceeds the safety limit: {info.filename}"
            )

    @staticmethod
    def _compression_ratio(info: ZipInfo) -> float:
        if info.compress_size > 0:
            return info.file_size / info.compress_size
        return 0 if info.file_size == 0 else float("inf")


class ThreeMFReader:
    def __init__(
        self,
        validator: ThreeMFArchiveValidator | None = None,
        selector: GCodeMemberSelector | None = None,
        member_reader: GCodeMemberReader | None = None,
    ) -> None:
        self._validator = validator or ThreeMFArchiveValidator()
        self._selector = selector or GCodeMemberSelector()
        self._member_reader = member_reader or GCodeMemberReader()

    def supports(self, path: Path) -> bool:
        return path.name.casefold().endswith(".3mf")

    def discover(self, path: Path) -> tuple[GCodeCandidate, ...]:
        try:
            with ZipFile(path) as archive:
                infos = tuple(archive.infolist())
                self._validator.validate(infos)
                return self._selector.candidates(infos)
        except BadZipFile as exc:
            raise SourceError(f"{path} is not a valid ZIP-based 3MF package") from exc
        except OSError as exc:
            raise SourceError(f"Unable to read 3MF input {path}: {exc}") from exc

    def read(self, path: Path, plate: int | None = None) -> GCodeDocument:
        try:
            with ZipFile(path) as archive:
                infos = tuple(archive.infolist())
                self._validator.validate(infos)
                candidate = self._selector.select(
                    self._selector.candidates(infos),
                    plate,
                    path.name,
                )
                info = next(item for item in infos if item.filename == candidate.member_path)
                text = self._member_reader.read(archive, info)
        except BadZipFile as exc:
            raise SourceError(f"{path} is not a valid ZIP-based 3MF package") from exc
        except OSError as exc:
            raise SourceError(f"Unable to read 3MF input {path}: {exc}") from exc

        provenance = SourceProvenance(path.name, candidate.member_path, candidate.plate)
        return GCodeDocument.from_text(text, provenance)
