from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path
from typing import cast

from .application import RecoverPrint, RecoverPrintCommand, RecoveryExecution
from .composition import create_recover_print
from .domain.errors import LayerSurgeonError
from .domain.models import RecoverySettings
from .ports import ArtifactTargets


class LayerSurgeonCLI:
    def __init__(self, recover_print: RecoverPrint) -> None:
        self._recover_print = recover_print
        self._parser = argparse.ArgumentParser(prog="layer-surgeon")
        self._configure_commands()

    def run(self, argv: list[str] | None = None) -> int:
        arguments = self._parser.parse_args(argv)
        handler = cast(Callable[[argparse.Namespace], int], arguments.command_handler)
        return handler(arguments)

    def _configure_commands(self) -> None:
        commands = self._parser.add_subparsers(dest="command", required=True)
        recover = commands.add_parser(
            "recover",
            help="Create auditable recovery G-code from a chosen layer",
        )
        recover.add_argument(
            "--input",
            required=True,
            type=Path,
            help="Original .gcode or sliced .3mf file",
        )
        recover.add_argument(
            "--plate",
            type=int,
            default=None,
            help="Plate number when a 3MF contains multiple G-code files",
        )
        recover.add_argument("--layer", required=True, type=int, help="Layer to start from")
        recover.add_argument("--output", required=True, type=Path, help="Recovery G-code output")
        recover.add_argument("--diff", required=True, type=Path, help="Unified diff output")
        recover.add_argument("--report", required=True, type=Path, help="Markdown report output")
        recover.add_argument("--profile", default="generic", help="Printer profile label")
        recover.add_argument(
            "--risk-allow-homing",
            action="store_true",
            help="Include G28 homing even though it can collide",
        )
        recover.add_argument(
            "--bed-temp",
            type=float,
            default=None,
            help="Override bed temperature",
        )
        recover.add_argument(
            "--nozzle-temp",
            type=float,
            default=None,
            help="Override nozzle temperature",
        )
        recover.set_defaults(command_handler=self._recover, command_parser=recover)

    def _recover(self, arguments: argparse.Namespace) -> int:
        command = RecoverPrintCommand(
            input_path=arguments.input,
            plate=arguments.plate,
            targets=ArtifactTargets(arguments.output, arguments.diff, arguments.report),
            settings=RecoverySettings(
                target_layer=arguments.layer,
                printer_profile=arguments.profile,
                risk_allow_homing=arguments.risk_allow_homing,
                bed_temp=arguments.bed_temp,
                nozzle_temp=arguments.nozzle_temp,
            ),
        )
        try:
            execution = self._recover_print.execute(command)
        except LayerSurgeonError as exc:
            arguments.command_parser.error(str(exc))

        self._print_summary(execution)
        return 0

    @staticmethod
    def _print_summary(execution: RecoveryExecution) -> None:
        plan = execution.plan
        provenance = plan.source.provenance
        print(f"Recovery created: {execution.targets.gcode}")
        print(f"Diff created:     {execution.targets.unified_diff}")
        print(f"Report created:   {execution.targets.report}")
        print(f"Started at source line: {plan.start_line}")
        if provenance.member_path is not None:
            print(f"3MF G-code member: {provenance.member_path}")
        if provenance.plate is not None:
            print(f"3MF plate:        {provenance.plate}")
        if plan.z_height is not None:
            print(f"Detected Z height: {plan.z_height}")


def main(argv: list[str] | None = None) -> int:
    return LayerSurgeonCLI(create_recover_print()).run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
