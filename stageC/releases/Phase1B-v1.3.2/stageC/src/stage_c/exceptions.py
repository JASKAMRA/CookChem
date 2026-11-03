class StageCError(Exception):
    """Base error for Stage C operations."""


class ValidationError(StageCError):
    """Raised when input data violate a documented schema or invariant."""


class UnitConversionError(ValidationError):
    """Raised when units are unknown or dimensionally incompatible."""


class SourceIntegrityError(StageCError):
    """Raised when a source manifest or immutable snapshot does not match."""
