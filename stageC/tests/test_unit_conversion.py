import sys
import unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stage_c.exceptions import UnitConversionError
from stage_c.unit_conversion import amount_moles_to_mg, concentration_to_mg_per_kg, mass_to_kg, mass_to_mg

class UnitConversionTests(unittest.TestCase):
    def test_supported_mass_units(self):
        self.assertEqual(mass_to_mg("1", "g"), Decimal("1000"))
        self.assertEqual(mass_to_mg("1000", "ug"), Decimal("1.000"))
        self.assertEqual(mass_to_kg("200", "g"), Decimal("0.2"))

    def test_concentration_factors_independently(self):
        self.assertEqual(concentration_to_mg_per_kg("5", "mg/kg"), Decimal("5"))
        self.assertEqual(concentration_to_mg_per_kg("5", "mg/100 g"), Decimal("50"))
        self.assertEqual(concentration_to_mg_per_kg("5", "ug/g"), Decimal("5"))
        self.assertEqual(concentration_to_mg_per_kg("5", "ng/g"), Decimal("0.005"))

    def test_rejects_volume_and_unknown_units(self):
        for unit in ("mg/L", "mg/mL", "widgets"):
            with self.subTest(unit=unit), self.assertRaises(UnitConversionError): concentration_to_mg_per_kg(1, unit)

    def test_rejects_negative_and_nonfinite(self):
        for value in ("-1", "NaN", "Infinity"):
            with self.subTest(value=value), self.assertRaises(UnitConversionError): mass_to_mg(value, "mg")

    def test_molar_conversion_requires_verified_identity_and_weight(self):
        with self.assertRaises(UnitConversionError): amount_moles_to_mg(1, "mmol", 180, False, True)
        self.assertEqual(amount_moles_to_mg(1, "mmol", 180, True, True), Decimal("180.000000"))

if __name__ == "__main__": unittest.main()
