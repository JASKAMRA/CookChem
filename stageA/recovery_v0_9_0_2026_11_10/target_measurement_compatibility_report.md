# Target and measurement compatibility

- Target contract: **439/439** rows are labelled `apparent_concentration_ratio_percent = 100 × C_cooked / C_raw`.
- **439/439** have both tabulated concentrations.
- Measurement basis and unit combinations are enumerated in `measurement_unit_basis_matrix.csv`; they are retained as stated and never converted in this audit.
- **0** rows are documented as having sufficient established mass-retention status. Therefore this package makes **no true total-mass retention calculation**.

The values are comparable apparent ratios only within their verified raw/cooked measurement contract. Moisture loss and unreported yield can raise concentration without proving preservation of total compound mass.
