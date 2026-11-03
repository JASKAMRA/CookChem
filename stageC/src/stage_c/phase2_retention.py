"""Phase 2 helpers for source-bounded cooking-retention intervals.

These helpers do not identify compounds or decide whether two food records are
scientifically compatible. Callers must establish those conditions explicitly.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class Phase2CompatibilityError(ValueError):
    """Raised when retention cannot be applied to the supplied food record."""


def _decimal(value: Decimal | str | int | float, label: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise Phase2CompatibilityError(f"{label} must be a finite decimal") from None
    if not result.is_finite():
        raise Phase2CompatibilityError(f"{label} must be a finite decimal")
    return result


@dataclass(frozen=True)
class PercentInterval:
    low: Decimal
    high: Decimal

    def __post_init__(self) -> None:
        low = _decimal(self.low, "interval low")
        high = _decimal(self.high, "interval high")
        object.__setattr__(self, "low", low)
        object.__setattr__(self, "high", high)
        if low < 0 or high > 100 or low > high:
            raise Phase2CompatibilityError("percentage interval must satisfy 0 <= low <= high <= 100")


@dataclass(frozen=True)
class ConcentrationInterval:
    low: Decimal
    high: Decimal


def retention_from_loss(loss_low_percent: Decimal | str | int | float,
                        loss_high_percent: Decimal | str | int | float) -> PercentInterval:
    """Convert a reported loss interval to its mathematically complementary retention interval.

    This preserves bounds only. It does not imply a probability distribution,
    confidence interval, or universal cooking coefficient.
    """
    loss_low = _decimal(loss_low_percent, "loss_low_percent")
    loss_high = _decimal(loss_high_percent, "loss_high_percent")
    if loss_low < 0 or loss_high > 100 or loss_low > loss_high:
        raise Phase2CompatibilityError("loss interval must satisfy 0 <= low <= high <= 100")
    return PercentInterval(Decimal("100") - loss_high, Decimal("100") - loss_low)


def adjust_concentration_interval(
    concentration: Decimal | str | int | float,
    retention: PercentInterval,
    *,
    exact_compound_match: bool,
    food_matrix_match: bool,
    cooking_condition_match: bool,
    measurement_basis_compatible: bool,
) -> ConcentrationInterval:
    """Apply a verified retention interval to concentration, with compatibility gates."""
    gates = {
        "exact compound identity": exact_compound_match,
        "food matrix": food_matrix_match,
        "cooking conditions": cooking_condition_match,
        "measurement basis": measurement_basis_compatible,
    }
    missing = [name for name, ok in gates.items() if not ok]
    if missing:
        raise Phase2CompatibilityError("retention application blocked: verify " + ", ".join(missing))
    value = _decimal(concentration, "concentration")
    if value < 0:
        raise Phase2CompatibilityError("concentration must be nonnegative")
    scale = Decimal("100")
    return ConcentrationInterval(value * retention.low / scale, value * retention.high / scale)
