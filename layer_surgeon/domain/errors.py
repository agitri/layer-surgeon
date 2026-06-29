class LayerSurgeonError(Exception):
    """Base class for expected, user-facing Layer Surgeon failures."""


class SourceError(LayerSurgeonError):
    """The requested input cannot be read as a supported G-code source."""


class SourceSelectionError(SourceError):
    """A source contains no unambiguous selectable G-code payload."""


class UnsafeArchiveError(SourceError):
    """An archive violates package or resource safety constraints."""


class LayerNotFoundError(LayerSurgeonError):
    """The requested recovery layer is absent from the source document."""


class ArtifactPathError(LayerSurgeonError):
    """Artifact targets would overwrite or alias another required path."""


class ArtifactWriteError(LayerSurgeonError):
    """Generated recovery artifacts could not be persisted."""
