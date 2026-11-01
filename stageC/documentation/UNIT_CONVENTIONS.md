# Unit conventions

The canonical food concentration is `mg/kg`; amount output is `mg`. Mass units g, mg, µg, ng, and kg are supported. Concentration units include mg/kg, µg/kg, mg/g, µg/g, mg/100 g, µg/100 g, and ng/g. Conversion uses exact decimal factors and preserves source value/unit in the record and provenance.

Volume units are rejected because density and matrix-specific support are absent. Molar conversion is available only with verified identity and molecular weight. Wet- and dry-weight records are never interconverted; concentration and ingredient mass must have a compatible explicitly recorded food basis. Negative and non-finite values are rejected. Unit conversion factors and implementation are in `src/stage_c/unit_conversion.py`.
