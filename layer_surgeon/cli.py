from __future__ import annotations

import argparse
from pathlib import Path

from .recover import RecoveryOptions, recover_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="layer-surgeon")
    sub = parser.add_subparsers(dest="command", required=True)

    recover = sub.add_parser("recover", help="Create auditable recovery G-code from a chosen layer")
    recover.add_argument("--input", required=True, type=Path, help="Original G-code file")
    recover.add_argument("--layer", required=True, type=int, help="Layer to start from")
    recover.add_argument("--output", required=True, type=Path, help="Recovery G-code output")
    recover.add_argument("--diff", required=True, type=Path, help="Unified diff output")
    recover.add_argument("--report", required=True, type=Path, help="Markdown report output")
    recover.add_argument("--profile", default="generic", help="Printer profile label")
    recover.add_argument("--risk-allow-homing", action="store_true", help="Include G28 homing even though it can collide")
    recover.add_argument("--bed-temp", type=float, default=None, help="Override bed temperature")
    recover.add_argument("--nozzle-temp", type=float, default=None, help="Override nozzle temperature")

    args = parser.parse_args(argv)

    if args.command == "recover":
        options = RecoveryOptions(
            target_layer=args.layer,
            printer_profile=args.profile,
            risk_allow_homing=args.risk_allow_homing,
            bed_temp=args.bed_temp,
            nozzle_temp=args.nozzle_temp,
        )
        result = recover_file(args.input, args.output, args.diff, args.report, options)
        print(f"Recovery created: {args.output}")
        print(f"Diff created:     {args.diff}")
        print(f"Report created:   {args.report}")
        print(f"Started at source line: {result.start_line}")
        if result.z_height is not None:
            print(f"Detected Z height: {result.z_height}")
        return 0

    return 1

if __name__ == "__main__":
    raise SystemExit(main())
