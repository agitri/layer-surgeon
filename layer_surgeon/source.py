from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo


MAX_EMBEDDED_GCODE_BYTES = 512 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200
PLATE_GCODE_RE = re.compile(r"(?:^|/)plate_(\d+)\.gcode$", re.IGNORECASE)


@dataclass(frozen=True)
class GCodeCandidate:
    member_path: str
    plate: int | None
    uncompressed_size: int


@dataclass(frozen=True)
class GCodeSource:
    input_path: Path
    lines: list[str]
    archive_member: str | None = None
    plate: int | None = None

    @property
    def display_name(self) -> str:
        if self.archive_member is None:
            return self.input_path.name
        return f"{self.input_path.name}:{self.archive_member}"


def is_3mf_path(path: str | Path) -> bool:
    return Path(path).name.lower().endswith(".3mf")


def read_gcode_source(path: str | Path, plate: int | None = None) -> GCodeSource:
    input_path = Path(path)
    if not is_3mf_path(input_path):
        if plate is not None:
            raise ValueError("--plate can only be used with a .3mf input")
        lines = input_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        return GCodeSource(input_path=input_path, lines=lines)

    return read_3mf_gcode(input_path, plate)


def discover_3mf_gcode(path: str | Path) -> list[GCodeCandidate]:
    input_path = Path(path)
    try:
        with ZipFile(input_path) as archive:
            infos = archive.infolist()
            _validate_3mf_package(infos)
            candidates = [_candidate_from_info(info) for info in infos if _is_gcode_member(info)]
    except BadZipFile as exc:
        raise ValueError(f"{input_path} is not a valid ZIP-based 3MF package") from exc

    return sorted(candidates, key=lambda candidate: candidate.member_path.casefold())


def read_3mf_gcode(path: str | Path, plate: int | None = None) -> GCodeSource:
    input_path = Path(path)
    try:
        with ZipFile(input_path) as archive:
            infos = archive.infolist()
            _validate_3mf_package(infos)
            matching_infos = [info for info in infos if _is_gcode_member(info)]
            candidates = [_candidate_from_info(info) for info in matching_infos]
            selected = _select_candidate(candidates, plate, input_path)
            info = next(info for info in matching_infos if info.filename == selected.member_path)
            _validate_gcode_member(info)
            with archive.open(info) as member:
                content = member.read(MAX_EMBEDDED_GCODE_BYTES + 1)
    except BadZipFile as exc:
        raise ValueError(f"{input_path} is not a valid ZIP-based 3MF package") from exc

    if len(content) > MAX_EMBEDDED_GCODE_BYTES:
        raise ValueError(
            f"Embedded G-code exceeds the {MAX_EMBEDDED_GCODE_BYTES}-byte safety limit: "
            f"{selected.member_path}"
        )

    lines = content.decode("utf-8", errors="replace").splitlines(keepends=True)
    return GCodeSource(
        input_path=input_path,
        lines=lines,
        archive_member=selected.member_path,
        plate=selected.plate,
    )


def _validate_3mf_package(infos: list[ZipInfo]) -> None:
    seen: set[str] = set()
    names: set[str] = set()

    for info in infos:
        name = info.filename
        if name in seen:
            raise ValueError(f"3MF package contains a duplicate member: {name}")
        seen.add(name)

        if "\\" in name:
            raise ValueError(f"3MF package contains an invalid member path: {name}")
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"3MF package contains an unsafe member path: {name}")
        if not info.is_dir():
            names.add(name.casefold())

    if "[content_types].xml" not in names:
        raise ValueError("Input is a ZIP archive but not a valid 3MF package: [Content_Types].xml is missing")
    if not any(name.endswith(".model") for name in names):
        raise ValueError("Input is a ZIP archive but not a valid 3MF package: no 3D model part was found")


def _is_gcode_member(info: ZipInfo) -> bool:
    return not info.is_dir() and info.filename.casefold().endswith(".gcode")


def _candidate_from_info(info: ZipInfo) -> GCodeCandidate:
    match = PLATE_GCODE_RE.search(info.filename)
    plate = int(match.group(1)) if match else None
    return GCodeCandidate(info.filename, plate, info.file_size)


def _select_candidate(
    candidates: list[GCodeCandidate],
    plate: int | None,
    input_path: Path,
) -> GCodeCandidate:
    if not candidates:
        raise ValueError(
            f"No embedded .gcode was found in {input_path.name}. "
            "The file may be an unsliced 3MF project; export a sliced .gcode.3mf or plain .gcode file."
        )

    if plate is not None:
        if plate < 1:
            raise ValueError("Plate number must be greater than zero")
        matches = [candidate for candidate in candidates if candidate.plate == plate]
        if not matches:
            available = ", ".join(
                str(candidate.plate) for candidate in candidates if candidate.plate is not None
            )
            suffix = f" Available plates: {available}." if available else ""
            raise ValueError(f"Plate {plate} was not found in {input_path.name}.{suffix}")
        if len(matches) > 1:
            paths = ", ".join(candidate.member_path for candidate in matches)
            raise ValueError(f"Plate {plate} is ambiguous in {input_path.name}: {paths}")
        return matches[0]

    if len(candidates) > 1:
        choices = ", ".join(
            f"plate {candidate.plate}: {candidate.member_path}"
            if candidate.plate is not None
            else candidate.member_path
            for candidate in candidates
        )
        raise ValueError(
            f"Multiple embedded G-code files were found in {input_path.name}: {choices}. "
            "Select one with --plate."
        )

    return candidates[0]


def _validate_gcode_member(info: ZipInfo) -> None:
    if info.flag_bits & 0x1:
        raise ValueError(f"Encrypted G-code members are not supported: {info.filename}")
    if info.compress_type not in {ZIP_STORED, ZIP_DEFLATED}:
        raise ValueError(f"Unsupported 3MF compression method for {info.filename}")
    if info.file_size > MAX_EMBEDDED_GCODE_BYTES:
        raise ValueError(
            f"Embedded G-code exceeds the {MAX_EMBEDDED_GCODE_BYTES}-byte safety limit: {info.filename}"
        )
    if info.compress_size == 0:
        ratio = 0 if info.file_size == 0 else float("inf")
    else:
        ratio = info.file_size / info.compress_size
    if ratio > MAX_COMPRESSION_RATIO:
        raise ValueError(
            f"Embedded G-code compression ratio exceeds the safety limit: {info.filename}"
        )
