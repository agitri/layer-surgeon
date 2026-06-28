from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import difflib

from .gcode import analyze, find_layer_start, read_lines, write_lines

@dataclass(frozen=True)
class RecoveryOptions:
    target_layer: int
    printer_profile: str = "generic"
    risk_allow_homing: bool = False
    bed_temp: float | None = None
    nozzle_temp: float | None = None
    add_comment_banner: bool = True

@dataclass(frozen=True)
class RecoveryResult:
    output_lines: list[str]
    diff_lines: list[str]
    report: str
    start_line: int
    z_height: float | None


def build_preamble(options: RecoveryOptions, z_height: float | None, bed_temp: float | None, nozzle_temp: float | None) -> list[str]:
    lines = []
    if options.add_comment_banner:
        lines.extend([
            "; ------------------------------\n",
            "; Layer Surgeon recovery file\n",
            f"; Start layer: {options.target_layer}\n",
            f"; Profile: {options.printer_profile}\n",
            "; WARNING: Recovery print can collide with the existing part. Watch first moves.\n",
            "; ------------------------------\n",
        ])

    if bed_temp is not None:
        lines.append(f"M140 S{bed_temp:g} ; set bed temperature\n")
    if nozzle_temp is not None:
        lines.append(f"M104 S{nozzle_temp:g} ; set nozzle temperature\n")

    if options.risk_allow_homing:
        lines.append("G28 ; RISKY: home all axes before recovery\n")
    else:
        lines.append("; G28 intentionally omitted: position must already be valid\n")

    if bed_temp is not None:
        lines.append(f"M190 S{bed_temp:g} ; wait for bed temperature\n")
    if nozzle_temp is not None:
        lines.append(f"M109 S{nozzle_temp:g} ; wait for nozzle temperature\n")

    lines.extend([
        "G90 ; absolute positioning\n",
        "M83 ; relative extrusion\n",
        "G92 E0 ; reset extruder\n",
    ])
    if z_height is not None:
        safe_z = z_height + 1.0
        lines.append(f"G1 Z{safe_z:.3f} F600 ; move just above recovery layer\n")
        lines.append(f"G1 Z{z_height:.3f} F300 ; move to recovery Z\n")
    lines.append("; ---- original G-code resumes below ----\n")
    return lines


def recover_lines(original_lines: list[str], options: RecoveryOptions) -> RecoveryResult:
    marker = find_layer_start(original_lines, options.target_layer)
    analysis = analyze(original_lines)
    bed_temp = options.bed_temp if options.bed_temp is not None else analysis.bed_temp
    nozzle_temp = options.nozzle_temp if options.nozzle_temp is not None else analysis.nozzle_temp
    z_height = marker.z_height

    preamble = build_preamble(options, z_height, bed_temp, nozzle_temp)
    output_lines = preamble + original_lines[marker.line_index:]

    diff_lines = list(difflib.unified_diff(
        original_lines,
        output_lines,
        fromfile="original.gcode",
        tofile=f"recovery_layer_{options.target_layer}.gcode",
        lineterm="",
    ))
    diff_lines = [line if line.endswith("\n") else line + "\n" for line in diff_lines]

    report = build_report(options, marker.line_index, len(original_lines), len(output_lines), z_height, bed_temp, nozzle_temp)
    return RecoveryResult(output_lines, diff_lines, report, marker.line_index, z_height)


def build_report(options: RecoveryOptions, start_line: int, original_count: int, output_count: int, z_height: float | None, bed_temp: float | None, nozzle_temp: float | None) -> str:
    risk = "YES - G28 homing is included" if options.risk_allow_homing else "NO - homing omitted"
    return f"""# Layer Surgeon recovery report

## Input

- Target layer: {options.target_layer}
- Printer profile: {options.printer_profile}
- Original lines removed before recovery: {start_line}
- Original total lines: {original_count}
- Recovery total lines: {output_count}

## Recovery settings

- Z height detected: {z_height if z_height is not None else 'unknown'}
- Bed temperature: {bed_temp if bed_temp is not None else 'unknown'}
- Nozzle temperature: {nozzle_temp if nozzle_temp is not None else 'unknown'}
- Risky homing: {risk}

## Warnings

- Keep one hand near the power switch.
- Stop immediately if the nozzle or bed approaches the existing part incorrectly.
- This file is intended for recovery only and should not replace the original sliced output.
"""


def recover_file(input_path: Path, output_path: Path, diff_path: Path, report_path: Path, options: RecoveryOptions) -> RecoveryResult:
    original = read_lines(input_path)
    result = recover_lines(original, options)
    write_lines(output_path, result.output_lines)
    write_lines(diff_path, result.diff_lines)
    report_path.write_text(result.report)
    return result
