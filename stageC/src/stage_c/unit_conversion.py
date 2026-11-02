"""Explicit mass and mass-concentration conversions using Decimal arithmetic."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from .exceptions import UnitConversionError

MASS_TO_MG = {
    "kg": Decimal("1000000"), "g": Decimal("1000"), "mg": Decimal("1"),
    "ug": Decimal("0.001"), "µg": Decimal("0.001"), "μg": Decimal("0.001"),
    "ng": Decimal("0.000001"),
}
CONCENTRATION_TO_MG_PER_KG = {
    "mg/kg": Decimal("1"), "ug/kg": Decimal("0.001"), "µg/kg": Decimal("0.001"), "μg/kg": Decimal("0.001"),
    "mg/g": Decimal("1000"), "ug/g": Decimal("1"), "µg/g": Decimal("1"), "μg/g": Decimal("1"),
    "mg/100 g": Decimal("10"), "mg/100g": Decimal("10"),
    "ug/100 g": Decimal("0.01"), "µg/100 g": Decimal("0.01"), "μg/100 g": Decimal("0.01"),
    "ug/100g": Decimal("0.01"), "µg/100g": Decimal("0.01"), "μg/100g": Decimal("0.01"),
    "ng/g": Decimal("0.001"),
}
MOLE_TO_MOL = {"mol": Decimal("1"), "mmol": Decimal("0.001"), "umol": Decimal("0.000001"), "µmol": Decimal("0.000001"), "μmol": Decimal("0.000001"), "nmol": Decimal("0.000000001")}


def _decimal(value: object) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise UnitConversionError(f"Invalid numeric value: {value!r}") from None
    if not number.is_finite() or number < 0:
        raise UnitConversionError("Mass and concentration values must be finite and nonnegative")
    return number


def normalize_unit(unit: str) -> str:
    return " ".join(unit.strip().lower().replace(" per ", "/").split())


def mass_to_mg(value: object, unit: str) -> Decimal:
    key = normalize_unit(unit).replace("μg", "ug").replace("µg", "ug")
    if key not in MASS_TO_MG:
        raise UnitConversionError(f"Unsupported mass unit: {unit!r}")
    return _decimal(value) * MASS_TO_MG[key]


def mass_to_kg(value: object, unit: str) -> Decimal:
    return mass_to_mg(value, unit) / Decimal("1000000")


def concentration_to_mg_per_kg(value: object, unit: str) -> Decimal:
    key = normalize_unit(unit).replace("μg", "ug").replace("µg", "ug")
    key = key.replace("100g", "100 g")
    if key not in CONCENTRATION_TO_MG_PER_KG:
        raise UnitConversionError(f"Unsupported mass concentration unit: {unit!r}")
    return _decimal(value) * CONCENTRATION_TO_MG_PER_KG[key]


def concentration_factor_to_mg_per_kg(unit: str) -> Decimal:
    """Return the exact multiplicative factor for a source unit."""
    key = normalize_unit(unit).replace("μg", "ug").replace("µg", "ug").replace("100g", "100 g")
    if key not in CONCENTRATION_TO_MG_PER_KG:
        raise UnitConversionError(f"Unsupported mass concentration unit: {unit!r}")
    return CONCENTRATION_TO_MG_PER_KG[key]


def amount_moles_to_mg(value: object, unit: str, molecular_weight_g_mol: object,
                       identity_confirmed: bool, molecular_weight_verified: bool) -> Decimal:
    if not identity_confirmed or not molecular_weight_verified:
        raise UnitConversionError("Molar conversion requires confirmed identity and verified molecular weight")
    key = normalize_unit(unit).replace("μ", "µ")
    if key not in MOLE_TO_MOL:
        raise UnitConversionError(f"Unsupported amount-of-substance unit: {unit!r}")
    mw = _decimal(molecular_weight_g_mol)
    if mw == 0:
        raise UnitConversionError("Molecular weight must be greater than zero")
    # mol × g/mol × 1000 mg/g = mg
    return _decimal(value) * MOLE_TO_MOL[key] * mw * Decimal("1000")
