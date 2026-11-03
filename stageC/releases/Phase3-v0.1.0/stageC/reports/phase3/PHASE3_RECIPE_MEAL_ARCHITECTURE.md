# Stage C Phase 3 — recipe and meal exposure foundation

## Scope

`stage_c.recipe_engine` builds source-traceable ingredient, recipe, and meal exposure outputs on the Phase 1 food-composition records and mapping rules. It does not implement clinical-risk interpretation. Stage B is read-only. Stage A retention modeling is never called.

## Data objects

- A recipe has a stable ID, name, source/provenance, ingredients, cooking operations, serving count, and an explicit recipe mass-balance record.
- Each ingredient names its food record and compound IDs, its mass or volume quantity, food state, serving allocation fraction, consumed fraction, preparation, source provenance, operations, and explicit measured/not-reported mass fields. A measured mass or volume requires a unit and measurement source reference.
- Mass tracking keeps raw, prepared, cooked, edible, discarded, retained/discarded cooking liquid, and retained/discarded oil distinct. Recipe totals separately track batch yield, serving mass/count, and leftovers. Recipes can also record cooked, serving, and leftover volume for beverages without converting volume to mass.
- A meal consists of uniquely identified recipe or direct-food components. Recipe ingredients are expanded once. A repeated food/compound pair as both a recipe ingredient and a direct meal item is rejected as potential double counting.

## Calculation rules

For an unheated ingredient, exposure uses the Phase 1 verified-food and mapping gates: normalized food concentration × explicit mass or volume × explicit serving allocation × consumed fraction. Mass concentrations use mass; volume concentrations use volume. Crossing between mass and volume requires a source-verified density. No tablespoon, cup, or household-unit conversion is assumed.

For a cooked ingredient, a raw-reference amount may be shown for provenance, but the eaten cooked amount remains unavailable unless a Phase 2 retention interval has a source ID/reference, all four compatibility gates are explicitly true, and cooked mass (for mg/kg) or cooked volume (for mg/L) is measured. The retained interval is applied through the existing Phase 2 guarded arithmetic helper. Missing evidence, compatibility, or cooked yield leaves the cooked result incomplete. No Phase 2 numeric output is presently available, so ordinary cooked recipes correctly remain unresolved.

Only explicit user/source fractions are used. `serving_fraction` allocates a batch ingredient to a serving; ingredient `consumed_fraction` represents the portion of that allocation eaten; and a meal recipe component separately records servings consumed and the fraction eaten. `leftovers_servings_consumed` records portions explicitly eaten from leftovers. Measured serving and leftover mass (or volume) bound that amount. These quantities are multiplied without inferring missing values. Cooking liquid or oil measurements do not imply compound transfer or retention.

The mass-accounting report compares measured recipe raw mass with measured ingredient raw masses; cooked mass with batch yield; cooked mass with edible plus discarded mass; and cooked mass with serving mass × servings count + leftover mass. A positive residual is explicitly unaccounted mass and a negative residual is inconsistent. Beverage volume has a separate volume equation and is never folded into mass balance without density.

## Outputs and uncertainty

Ingredient outputs preserve raw reference concentration/amount, cooked status, source food and mapping, Stage B release hash, Phase 2 evidence ID, compatibility gates, operations, and serving/consumption fractions. Recipe and meal totals sum compatible mg contributions only when every contributing item is complete; an unresolved component blocks the total while remaining visible. Valid Phase 2 bounds are summed as interval endpoints, not as probability distributions. Missing source uncertainty is explicitly retained.

## Interface and storage

The `cookrisk-stagec recipe` and `meal` CLI commands create, update, validate, calculate, and export JSON documents. The CLI verifies the pinned Phase1B-v1.3.1, Phase2-v0.3.0, and Phase4-v0.1.2 manifests before use. Phase 4 is surfaced through an approved-context-only adapter; numerical PK evidence is not exposed to calculations.

Recipes and meals are portable JSON documents validated before save and after load. Draft 2020-12 JSON Schemas are in `stageC/schemas/recipe.schema.json` and `meal.schema.json`; application validators add supported-unit, cross-record, mass-accounting, interval, and double-count checks. Install `stageC/requirements-dev.txt` for formal schema validation.

## Current limitations

The engine supports kg/g/mg/µg/ng and L/mL, plus explicit kg/L density. It does not infer density or household measures. It expects food/compound IDs to be supplied; it does not guess chemical mappings. The pinned Phase2 package has zero quantitative cooked outputs, so the guarded cooked path has no approved live estimate. The engine aggregates food-compound exposure only and assigns no clinical meaning or safety threshold.
