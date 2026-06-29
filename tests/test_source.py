from pathlib import Path
from zipfile import ZIP_BZIP2, ZIP_DEFLATED, ZipFile

import pytest

from layer_surgeon.cli import main
from layer_surgeon.recover import RecoveryOptions, recover_file
from layer_surgeon.source import discover_3mf_gcode, read_gcode_source


GCODE_TEMPLATE = """M140 S60
M104 S220
; layer num/total_layer_count: {layer}/120
G1 Z{z_height:.3f} F600
G1 X5 Y5 E0.1
"""


def write_3mf(path: Path, members: dict[str, str]) -> None:
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("3D/3dmodel.model", "<model />")
        for member_path, content in members.items():
            archive.writestr(member_path, content)


def test_discovers_bambu_plate_gcode(tmp_path: Path):
    archive_path = tmp_path / "print.gcode.3mf"
    write_3mf(
        archive_path,
        {"Metadata/plate_1.gcode": GCODE_TEMPLATE.format(layer=112, z_height=22.4)},
    )

    candidates = discover_3mf_gcode(archive_path)

    assert len(candidates) == 1
    assert candidates[0].member_path == "Metadata/plate_1.gcode"
    assert candidates[0].plate == 1


def test_reads_single_embedded_gcode(tmp_path: Path):
    archive_path = tmp_path / "print.3mf"
    write_3mf(
        archive_path,
        {"Metadata/plate_1.gcode": GCODE_TEMPLATE.format(layer=112, z_height=22.4)},
    )

    source = read_gcode_source(archive_path)

    assert source.archive_member == "Metadata/plate_1.gcode"
    assert source.plate == 1
    assert "; layer num/total_layer_count: 112/120\n" in source.lines


def test_requires_plate_for_multiple_gcode_members(tmp_path: Path):
    archive_path = tmp_path / "multi.3mf"
    write_3mf(
        archive_path,
        {
            "Metadata/plate_1.gcode": GCODE_TEMPLATE.format(layer=10, z_height=2.0),
            "Metadata/plate_2.gcode": GCODE_TEMPLATE.format(layer=20, z_height=4.0),
        },
    )

    with pytest.raises(ValueError, match="Multiple embedded G-code files"):
        read_gcode_source(archive_path)

    source = read_gcode_source(archive_path, plate=2)
    assert source.plate == 2
    assert "; layer num/total_layer_count: 20/120\n" in source.lines


def test_rejects_unsliced_3mf_without_gcode(tmp_path: Path):
    archive_path = tmp_path / "project.3mf"
    write_3mf(archive_path, {"Metadata/project_settings.config": "settings"})

    with pytest.raises(ValueError, match="No embedded .gcode"):
        read_gcode_source(archive_path)


def test_rejects_invalid_3mf_archive(tmp_path: Path):
    archive_path = tmp_path / "broken.3mf"
    archive_path.write_text("not a zip archive")

    with pytest.raises(ValueError, match="not a valid ZIP-based 3MF package"):
        read_gcode_source(archive_path)


def test_rejects_zip_without_3mf_package_structure(tmp_path: Path):
    archive_path = tmp_path / "renamed-zip.3mf"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "Metadata/plate_1.gcode",
            GCODE_TEMPLATE.format(layer=112, z_height=22.4),
        )

    with pytest.raises(ValueError, match=r"\[Content_Types\]\.xml is missing"):
        read_gcode_source(archive_path)


def test_rejects_unsafe_archive_member_path(tmp_path: Path):
    archive_path = tmp_path / "unsafe.3mf"
    write_3mf(
        archive_path,
        {"../plate_1.gcode": GCODE_TEMPLATE.format(layer=112, z_height=22.4)},
    )

    with pytest.raises(ValueError, match="unsafe member path"):
        read_gcode_source(archive_path)


def test_rejects_nonstandard_3mf_compression(tmp_path: Path):
    archive_path = tmp_path / "bzip2.3mf"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("3D/3dmodel.model", "<model />")
        archive.writestr(
            "Metadata/plate_1.gcode",
            GCODE_TEMPLATE.format(layer=112, z_height=22.4),
            compress_type=ZIP_BZIP2,
        )

    with pytest.raises(ValueError, match="Unsupported 3MF compression"):
        read_gcode_source(archive_path)


def test_rejects_suspicious_gcode_compression_ratio(tmp_path: Path):
    archive_path = tmp_path / "compression-bomb.3mf"
    repetitive_gcode = "G1 X0 Y0 E0\n" * 100_000
    write_3mf(archive_path, {"Metadata/plate_1.gcode": repetitive_gcode})

    with pytest.raises(ValueError, match="compression ratio exceeds"):
        read_gcode_source(archive_path)


def test_recover_file_uses_selected_3mf_plate(tmp_path: Path):
    archive_path = tmp_path / "multi.3mf"
    output_path = tmp_path / "recovery.gcode"
    diff_path = tmp_path / "recovery.diff"
    report_path = tmp_path / "recovery_report.md"
    write_3mf(
        archive_path,
        {
            "Metadata/plate_1.gcode": GCODE_TEMPLATE.format(layer=111, z_height=22.2),
            "Metadata/plate_2.gcode": GCODE_TEMPLATE.format(layer=112, z_height=22.4),
        },
    )

    result = recover_file(
        archive_path,
        output_path,
        diff_path,
        report_path,
        RecoveryOptions(target_layer=112),
        plate=2,
    )

    assert result.source is not None
    assert result.source.archive_member == "Metadata/plate_2.gcode"
    assert result.source.plate == 2
    assert "G1 Z22.400 F300" in output_path.read_text()
    assert "--- multi.3mf:Metadata/plate_2.gcode" in diff_path.read_text()
    assert "- 3MF G-code member: Metadata/plate_2.gcode" in report_path.read_text()
    assert "- 3MF plate: 2" in report_path.read_text()


def test_rejects_input_output_path_collision(tmp_path: Path):
    input_path = tmp_path / "original.gcode"
    input_path.write_text(GCODE_TEMPLATE.format(layer=112, z_height=22.4))

    with pytest.raises(ValueError, match="original files are immutable"):
        recover_file(
            input_path,
            input_path,
            tmp_path / "recovery.diff",
            tmp_path / "recovery_report.md",
            RecoveryOptions(target_layer=112),
        )


def test_rejects_plate_for_plain_gcode(tmp_path: Path):
    input_path = tmp_path / "original.gcode"
    input_path.write_text(GCODE_TEMPLATE.format(layer=112, z_height=22.4))

    with pytest.raises(ValueError, match="--plate can only be used"):
        read_gcode_source(input_path, plate=1)


def test_rejects_non_positive_plate_number(tmp_path: Path):
    archive_path = tmp_path / "print.3mf"
    write_3mf(
        archive_path,
        {"Metadata/plate_1.gcode": GCODE_TEMPLATE.format(layer=112, z_height=22.4)},
    )

    with pytest.raises(ValueError, match="greater than zero"):
        read_gcode_source(archive_path, plate=0)


def test_rejects_duplicate_output_paths(tmp_path: Path):
    input_path = tmp_path / "original.gcode"
    shared_output_path = tmp_path / "recovery.out"
    input_path.write_text(GCODE_TEMPLATE.format(layer=112, z_height=22.4))

    with pytest.raises(ValueError, match="paths must be different"):
        recover_file(
            input_path,
            shared_output_path,
            shared_output_path,
            tmp_path / "recovery_report.md",
            RecoveryOptions(target_layer=112),
        )


def test_cli_recovers_selected_3mf_plate(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    archive_path = tmp_path / "multi.gcode.3mf"
    output_path = tmp_path / "recovery.gcode"
    diff_path = tmp_path / "recovery.diff"
    report_path = tmp_path / "recovery_report.md"
    write_3mf(
        archive_path,
        {
            "Metadata/plate_1.gcode": GCODE_TEMPLATE.format(layer=111, z_height=22.2),
            "Metadata/plate_2.gcode": GCODE_TEMPLATE.format(layer=112, z_height=22.4),
        },
    )

    exit_code = main(
        [
            "recover",
            "--input",
            str(archive_path),
            "--plate",
            "2",
            "--layer",
            "112",
            "--output",
            str(output_path),
            "--diff",
            str(diff_path),
            "--report",
            str(report_path),
        ]
    )

    assert exit_code == 0
    assert "3MF G-code member: Metadata/plate_2.gcode" in capsys.readouterr().out
    assert output_path.exists()
