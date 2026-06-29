from .adapters.filesystem import FilesystemArtifactWriter
from .adapters.renderers import (
    DifflibUnifiedDiffRenderer,
    MarkdownRecoveryReportRenderer,
    RecoveryGCodeRenderer,
)
from .adapters.sources import PlainGCodeReader, ThreeMFReader
from .application import RecoverPrint
from .domain.analysis import GCodeAnalyzer
from .domain.recovery import RecoveryPlanner


def create_recover_print() -> RecoverPrint:
    analyzer = GCodeAnalyzer()
    return RecoverPrint(
        source_readers=(ThreeMFReader(), PlainGCodeReader()),
        planner=RecoveryPlanner(analyzer),
        gcode_renderer=RecoveryGCodeRenderer(),
        diff_renderer=DifflibUnifiedDiffRenderer(),
        report_renderer=MarkdownRecoveryReportRenderer(),
        artifact_writer=FilesystemArtifactWriter(),
    )
