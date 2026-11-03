# Phase 5 Synthetic Arithmetic Benchmark Protocol

## Status and scope

**SYNTHETIC — TEST FIXTURE ONLY.** The fixture at `tests/fixtures/synthetic_validation_benchmark.json` and its schema are designed to check arithmetic plumbing. Every value is invented. It is not published evidence, a real-world benchmark, a food-safety validation set, or an external-validation dataset.

## Protocol

1. Load the JSON fixture and validate its structure against `schemas/synthetic_validation_benchmark.schema.json` using a Draft 2020-12 JSON Schema validator.
2. Compute the two point examples with the independent reference arithmetic function. Keep mass and volume dimensions separate; do not use density.
3. For the retention example, multiply the invented raw concentration by each retention endpoint, then by the cooked portion quantity and consumed fraction. Compare exact Decimal outputs with the recorded expectations.
4. Run mutation cases that alter one expected or calculated amount and confirm the corresponding arithmetic check fails. Keep boundary cases such as zero quantity, zero fraction, coincident interval endpoints, and an endpoint equal to the point value explicit.
5. Record only software/arithmetic test status. Never pass these fixture rows to `compare_to_reference(layer="published_data_comparison")`, published-data error metrics, or an external validation claim.

## Expected calculations

- Mass: `5 mg/kg × 0.200 kg × 0.5 = 0.5 mg`.
- Volume: `10 mg/L × 0.250 L × 0.4 = 1.0 mg`.
- Retention bounds: `5 mg/kg × [0.40, 0.60] × 0.100 kg × 0.5 = [0.10, 0.15] mg`.

The retention interval is a deterministic endpoint propagation for an invented example. It is not a probability interval. A matching fixture result verifies the implementation against arithmetic expectations only; it does not verify any scientific input or model applicability.
