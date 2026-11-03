# Phase 3 recipe and meal interface

Run from the repository root in PowerShell. These examples use checksum-verified Phase1B-v1.3.2, Phase2-v0.3.1, and Phase4-v0.1.2 packages read-only.

```powershell
$env:PYTHONPATH = 'stageC/src'
```

## Recipe workflow

Create or validate a structured recipe JSON file, append another ingredient JSON object, then calculate and export results:

```powershell
python -m stage_c.cli recipe create stageC/examples/recipe_apples_epicatechin.json --output my_recipes/apple.json
python -m stage_c.cli recipe validate my_recipes/apple.json
python -m stage_c.cli recipe add-ingredient my_recipes/apple.json --ingredient my_recipes/second_ingredient.json
python -m stage_c.cli recipe calculate my_recipes/apple.json --output stageC/reports/phase3/calculations/apple.json
```

`create` and `add-ingredient` validate before saving. The second ingredient file must be a complete ingredient object with explicit food and compound IDs, quantity/unit, source provenance, and measured or `not_reported` mass-balance fields. `validate` reports structure separately from measured mass/volume accounting. `calculate` writes JSON with source IDs, pinned upstream hashes, ingredient estimates, cooked status, and raw-reference totals.

## Meal workflow

Place recipe JSON files in one directory (each filename may be arbitrary; each document must have a unique `recipe_id`). A meal may combine recipe components with direct-food components. Calculate with:

```powershell
python -m stage_c.cli meal create stageC/examples/meal_apple_and_cocoa.json --recipes-dir my_recipes --output my_recipes/meal.json
python -m stage_c.cli meal validate my_recipes/meal.json --recipes-dir my_recipes
python -m stage_c.cli meal calculate my_recipes/meal.json --recipes-dir my_recipes --output stageC/reports/phase3/calculations/meal.json
```

Repeated direct food/compound pairs, and a direct pair already represented inside a recipe, are rejected to prevent duplicate contributions. A recipe component records both `servings_consumed` and `consumed_fraction`. For leftovers, set `leftovers_servings_consumed` explicitly; when used, both measured `serving_mass` and `leftovers_mass`, or measured `serving_volume` and `leftovers_volume`, are required. Consumed leftover servings may not exceed the measured amount. Leftovers are not inferred from raw-to-cooked differences.

## Calculation behavior

- Raw-reference totals are reported separately from the exposure total and are labeled as non-cooked references. Partial consumption is reflected in `raw_reference_totals`; unconsumed recipe serving references remain identifiable at the ingredient level.
- Recipe/mass results compare only explicitly measured fields: declared raw mass vs measured ingredient raw masses; cooked mass vs batch yield; cooked mass vs edible plus discarded mass; and cooked mass vs serving mass × serving count + leftover mass. Beverage output volume has a separate volume check. A positive residual is reported as unaccounted measured output; a negative residual is inconsistent. Missing values are not changed or inferred.
- mg/kg requires explicit mass; mg/L requires explicit volume. Cross-dimensional conversion needs a verified density source.
- The Phase2-v0.3.1 adapter verifies the 49-file release manifest and reports zero eligible cooked-concentration estimates. Cooked calculations therefore remain incomplete unless a future pinned Phase 2 package contains an accepted estimate with strict identity, an explicit source reference, all four compatibility gates, and measured cooked mass/volume.
- Phase4-v0.1.2 has one full-text primary source and six pending records. Its selector returns zero records; numerical plasma PK data cannot be a food-dose multiplier and cannot alter Phase 3 calculations.
- The example quantities (150 g apple and 5 g cocoa) are illustrative input values only. They are not reported intake or recommendations. Their food-concentration values and exact mapping IDs come from Phase1B-v1.3.2.

## Schema validation

The recipe, meal, Stage A handoff, Phase 2, and Phase 4 schemas declare Draft 2020-12. Install the pinned development dependency and run the formal checks plus the focused workflows:

```powershell
python -m pip install -r stageC/requirements-dev.txt
$env:PYTHONPATH = 'stageC/src;stageC/tests'
python -m unittest test_recipe_schema test_cooking_integration test_recipe_engine test_recipe_cli test_recipe_release_integration -v
```

The recipe CLI supports loading and editing a saved recipe through `recipe add-ingredient`; validate and calculate commands write JSON results with input and release provenance. The Stage A handoff contract is documented in [the integration readiness report](../phase2/STAGE_A_INTEGRATION_READINESS.md). It consumes caller-supplied records only. The inspected Stage A package has no serialized model or deployed output contract, so all Stage A-derived estimates remain blocked and no inference is run.
