$ErrorActionPreference = "Stop"
$stage = Split-Path -Parent $PSScriptRoot
$schemaRoot = Join-Path $stage "schemas"

function Assert-ValidSchemaInstance {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][object]$Value
    )
    $schemaPath = Join-Path $schemaRoot $Name
    $json = ConvertTo-Json -InputObject $Value -Depth 100 -Compress
    if (-not (Test-Json -Json $json -SchemaFile $schemaPath)) {
        throw "JSON Schema validation failed for $Name"
    }
    [pscustomobject]@{ schema = $Name; result = "PASS" }
}

$snapshot = Join-Path $stage "data\stage_b_snapshot_20261103"
$compound = Import-Csv -LiteralPath (Join-Path $snapshot "compound_registry.csv") | Select-Object -First 1
$food = Import-Csv -LiteralPath (Join-Path $stage "data\food_composition\food_composition.csv") | Select-Object -First 1
$mapping = Import-Csv -LiteralPath (Join-Path $stage "data\compound_food_mapping\compound_food_mapping.csv") | Select-Object -First 1
$importManifest = Get-Content -Raw -LiteralPath (Join-Path $snapshot "import_manifest.json") | ConvertFrom-Json

$results = @()
$results += Assert-ValidSchemaInstance "stage_b_import_manifest_schema.json" $importManifest
$results += Assert-ValidSchemaInstance "compound_schema.json" $compound
$results += Assert-ValidSchemaInstance "food_composition_schema.json" $food
$results += Assert-ValidSchemaInstance "compound_food_mapping_schema.json" $mapping
$results += Assert-ValidSchemaInstance "food_schema.json" ([pscustomobject]@{
    food_name = "Synthetic schema fixture"
    raw_or_processed_state = "raw"
    food_part = "fruit"
    moisture_basis = "wet weight"
})
$results += Assert-ValidSchemaInstance "exposure_input_schema.json" ([pscustomobject]@{
    compound_id = "SYN-C-1"
    food_record_id = "SYN-F-1"
    ingredient_quantity = "100"
    ingredient_unit = "g"
    consumed_fraction = "1"
})
$results += Assert-ValidSchemaInstance "exposure_output_schema.json" ([pscustomobject]@{
    estimate_id = "SYN-E-1"
    compound_id = "SYN-C-1"
    food_record_id = "SYN-F-1"
    calculation_status = "Incomplete: missing concentration"
    calculation_method = "synthetic schema fixture"
    input_source_ids = @()
    stage_b_release_reference = "StageB_FINALIZED"
    warnings = @()
    missing_inputs = @("reported_concentration")
    calculation_timestamp = "2026-11-03T00:00:00Z"
    software_version = "1.3.0"
})
$results += Assert-ValidSchemaInstance "provenance_schema.json" ([pscustomobject]@{
    estimate_id = "SYN-E-1"
    stage_b_release = "StageB_FINALIZED"
    stage_b_manifest_sha256 = ("a" * 64)
    compound_id = "SYN-C-1"
    food_record_id = "SYN-F-1"
    formula = "synthetic fixture"
    software_version = "1.3.0"
})

$invalidManifest = $importManifest | ConvertTo-Json -Depth 100 | ConvertFrom-Json
$invalidManifest.compound_count = 119
$invalidJson = ConvertTo-Json -InputObject $invalidManifest -Depth 100 -Compress
$mutationRejected = $false
try {
    $mutationRejected = -not (Test-Json -Json $invalidJson -SchemaFile (Join-Path $schemaRoot "stage_b_import_manifest_schema.json"))
} catch {
    $mutationRejected = $true
}
if (-not $mutationRejected) {
    throw "Mutation check failed: the import schema accepted an obsolete 119-compound manifest"
}

$results | ConvertTo-Json -Depth 4
Write-Output "JSON Schema fixtures: $($results.Count)/$($results.Count) PASS; invalid-manifest mutation rejected"
