const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const criteriaFields = [
  ["compound_identity", "Compound identity"], ["exposure_route", "Exposure route"],
  ["dose_units_and_basis", "Dose units and basis"], ["time_window", "Time window"],
  ["population_or_model", "Population or model"], ["preparation_or_matrix", "Preparation or matrix"],
];
let catalog = {foods: [], compounds: []};
let lastExport = null;
let selectedEvidence = null;
let catalogFilter = "";
let evidenceDetails = new Map();
let queueRows = [];
let queueTotal = 0;
let queueOffset = 0;
let queueLimit = 40;
let selectedReviewId = "";
let actionSubmitting = false;

function searchTerms(value = catalogFilter) {
  return value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
}

function foodMappedCompounds(row) {
  const ids = new Set(row.compound_ids || []);
  return catalog.compounds.filter(item => ids.has(item.compound_id));
}

function rowSearchText(row) {
  const compounds = foodMappedCompounds(row).map(item => `${item.name} ${item.compound_id}`).join(" ");
  return [row.food_record_id, row.food_name, row.raw_or_processed_state, row.source_title, compounds]
    .map(value => String(value || "")).join(" ").toLocaleLowerCase();
}

function matchingFoods() {
  const terms = searchTerms();
  if (!terms.length) return catalog.foods;
  return catalog.foods.filter(row => terms.every(term => rowSearchText(row).includes(term)));
}

function matchingCompoundsForFood(row) {
  const eligible = foodMappedCompounds(row);
  const terms = searchTerms();
  if (!terms.length) return eligible;
  const foodText = [row.food_record_id, row.food_name, row.raw_or_processed_state, row.source_title]
    .map(value => String(value || "")).join(" ").toLocaleLowerCase();
  const compoundTerms = terms.filter(term => !foodText.includes(term));
  if (!compoundTerms.length) return eligible;
  const matches = eligible.filter(item => compoundTerms.every(term =>
    `${item.name} ${item.compound_id}`.toLocaleLowerCase().includes(term)));
  return matches.length ? matches : eligible;
}

function populateFoodOptions(select) {
  const prior = select.value;
  const rows = matchingFoods();
  const selectedRow = catalog.foods.find(row => row.food_record_id === prior);
  const keepCurrent = selectedRow && !rows.some(row => row.food_record_id === prior);
  const visibleRows = keepCurrent ? [selectedRow, ...rows] : rows;
  select.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = rows.length ? `Select food record (${rows.length} matches)` : "No food records match this search";
  select.append(placeholder);
  visibleRows.forEach(row => {
    const option = document.createElement("option");
    option.value = row.food_record_id;
    const outsideSearch = keepCurrent && row.food_record_id === prior ? "Current selection · " : "";
    option.textContent = outsideSearch + row.food_name + " · " + row.food_record_id + " · " + display(row.normalized_concentration) + " " + row.normalized_unit;
    select.append(option);
  });
  select.value = prior;
}

function applyCatalogFilter() {
  catalogFilter = $("#catalog-filter").value;
  const rows = matchingFoods();
  const compoundMatches = catalog.compounds.filter(item => searchTerms().every(term =>
    `${item.name} ${item.compound_id}`.toLocaleLowerCase().includes(term)));
  $("#catalog-filter-status").textContent = catalogFilter.trim()
    ? `${rows.length} food records match across food names, mapped compound names/IDs, and source titles. ${compoundMatches.length} compound names/IDs match directly.`
    : `${rows.length} food records available. Compound options are always limited to the selected food's verified mappings.`;
  $$(".ingredient-card", $("#ingredient-list")).forEach(card => {
    populateFoodOptions($(".food-select", card));
    updateFoodDetails(card);
  });
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[ch]));
}
function display(value, fallback = "Not reported") {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}
function showError(container, message) {
  container.innerHTML = `<div class="result-banner pending">${escapeHtml(message)}</div>`;
}
function setStatus(container, message, tone = "") {
  container.className = `inline-status${tone ? ` ${tone}` : ""}`;
  container.textContent = message;
}
async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const type = response.headers.get("content-type") || "";
  if (!type.includes("application/json")) throw new Error(`Unexpected response (${response.status})`);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

function addIngredient() {
  const fragment = $("#ingredient-template").content.cloneNode(true);
  const card = $(".ingredient-card", fragment);
  const food = $(".food-select", card);
  const compound = $(".compound-select", card);
  food.addEventListener("change", () => updateFoodDetails(card, {resetState: true}));
  compound.addEventListener("change", () => updateIdentityNote(card));
  $(".food-state", card).addEventListener("change", () => updateStateNote(card));
  $(".remove-ingredient", card).addEventListener("click", () => {
    if ($$(".ingredient-card", $("#ingredient-list")).length > 1) card.remove();
    renumberIngredients();
  });
  $("#ingredient-list").append(fragment);
  populateFoodOptions(food);
  updateFoodDetails(card);
  renumberIngredients();
}

function unitDimension(row) {
  const unit = String(row?.normalized_unit || "").replace(/\s/g, "").toLocaleLowerCase();
  return unit.startsWith("mg/l") ? "volume" : "mass";
}

function catalogState(row) {
  const value = String(row?.raw_or_processed_state || "").toLocaleLowerCase();
  if (value.includes("ferment")) return "fermented";
  if (value.includes("dried") || value.includes("dry")) return "dried";
  if (value.includes("frozen") || value.includes("freeze")) return "frozen";
  if (value.includes("cook") || value.includes("boil") || value.includes("roast")) return "cooked";
  if (value.includes("process") || value.includes("extract") || value.includes("powder")) return "processed";
  if (value.includes("raw")) return "raw";
  return "other";
}

function populateQuantityUnits(card, row) {
  const select = $(".unit", card);
  const previous = select.value;
  const units = unitDimension(row) === "volume" ? ["mL", "L"] : ["g", "kg", "mg", "ug"];
  select.replaceChildren(...units.map(unit => {
    const option = document.createElement("option");
    option.value = unit;
    option.textContent = unit;
    return option;
  }));
  select.value = units.includes(previous) ? previous : units[0];
}

function updateIdentityNote(card) {
  const row = catalog.foods.find(item => item.food_record_id === $(".food-select", card).value);
  const compoundId = $(".compound-select", card).value;
  const compound = catalog.compounds.find(item => item.compound_id === compoundId);
  if (!row) {
    $(".identity-note", card).textContent = "Choose a food record to see its mapped compounds.";
    return;
  }
  const mapped = new Set(row.compound_ids || []);
  if (!compound || !mapped.has(compoundId)) {
    $(".identity-note", card).textContent = "Choose a compound mapped to this food record.";
    return;
  }
  $(".identity-note", card).textContent = `Mapped compound · ${display(compound.identity_status, "identity status not reported")}. Mapping records support this food/compound pair; review any pending identity note.`;
}

function updateStateNote(card) {
  const state = $(".food-state", card).value;
  const note = $(".state-note", card);
  if (state === "cooked") {
    const row = catalog.foods.find(item => item.food_record_id === $(".food-select", card).value);
    if (row && unitDimension(row) === "volume") {
      note.textContent = "Cooked liquid estimates need compatible Phase 2 evidence and measured cooked volume. This form does not collect cooked volume, so the cooked estimate will remain unavailable.";
    } else {
      note.textContent = "A cooked estimate requires compatible Phase 2 evidence and measured cooked mass. Otherwise only the raw reference is reported.";
    }
  } else if (state === "processed") {
    note.textContent = "The selected record's state must represent this processed food; no raw-to-processed conversion is inferred.";
  } else {
    note.textContent = "Raw reference only. A cooking description does not change the selected concentration.";
  }
}

function updateFoodDetails(card, {resetState = false} = {}) {
  const foodId = $(".food-select", card).value;
  const row = catalog.foods.find(item => item.food_record_id === foodId);
  const source = $(".food-source", card);
  if (!row) {
    source.textContent = "Choose a record to see its state, concentration basis, source, and mapped compounds.";
    populateQuantityUnits(card, null);
    $(".compound-select", card).innerHTML = `<option value="">Select food first</option>`;
    updateIdentityNote(card);
    updateStateNote(card);
    return;
  }
  source.textContent = `${display(row.raw_or_processed_state, "state not reported")} · ${display(row.normalized_concentration)} ${display(row.normalized_unit)} · ${display(row.source_verification_status, "source status not reported")} · ${display(row.source_title, "source title not reported")}`;
  populateQuantityUnits(card, row);
  if (resetState) $(".food-state", card).value = catalogState(row);
  const cookedField = $(".cooked-mass", card).closest("label");
  const cookedNote = $(".cooked-measurement-note", card);
  const isVolume = unitDimension(row) === "volume";
  cookedField.hidden = isVolume;
  cookedNote.hidden = !isVolume;
  if (isVolume) cookedNote.textContent = "Cooked volume is not collected by this prototype. Cooked exposure estimates for this concentration basis remain unavailable.";
  const compound = $(".compound-select", card);
  const prior = compound.value;
  const choices = matchingCompoundsForFood(row);
  const currentIsMapped = foodMappedCompounds(row).some(item => item.compound_id === prior);
  const keepPrior = currentIsMapped && !choices.some(item => item.compound_id === prior);
  const visible = keepPrior ? [catalog.compounds.find(item => item.compound_id === prior), ...choices] : choices;
  compound.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = visible.length ? "Select a mapped compound" : "No compounds are mapped to this food";
  compound.append(placeholder);
  visible.forEach(item => {
    if (!item) return;
    const option = document.createElement("option");
    option.value = item.compound_id;
    option.textContent = `${keepPrior && item.compound_id === prior ? "Current selection · " : ""}${item.name} · ${item.compound_id}`;
    compound.append(option);
  });
  compound.value = currentIsMapped ? prior : "";
  updateIdentityNote(card);
  updateStateNote(card);
}

function renumberIngredients() {
  $$(".ingredient-card", $("#ingredient-list")).forEach((card, index) => {
    $(".ingredient-number", card).textContent = `Ingredient ${index + 1}`;
  });
}

function collectRecipeRequest() {
  const ingredients = $$(".ingredient-card", $("#ingredient-list")).map(card => ({
    food_record_id: $(".food-select", card).value,
    compound_id: $(".compound-select", card).value,
    quantity: $(".quantity", card).value,
    unit: $(".unit", card).value,
    serving_fraction: $(".serving-fraction", card).value,
    consumed_fraction: $(".consumed-fraction", card).value,
    food_state: $(".food-state", card).value,
    cooked_mass: $(".cooked-mass", card).value,
    cooked_mass_unit: "g",
    preparation_description: $(".preparation-description", card).value,
  }));
  const form = new FormData($("#recipe-form"));
  return {
    name: form.get("name"), ingredients,
    cooking_method: form.get("cooking_method"), duration_min: form.get("duration_min"),
    temperature_c: form.get("temperature_c"), cooking_medium: form.get("cooking_medium"),
    servings_count: form.get("servings_count"), meal: {servings_consumed: form.get("meal_servings"), consumed_fraction: "1"},
  };
}

function totalText(total) {
  if (!total) return "Not available";
  if (total.consumed_amount_low_mg === "" || total.consumed_amount_high_mg === "") return "Amount unavailable";
  if (total.consumed_amount_low_mg === total.consumed_amount_high_mg) return `${total.consumed_amount_low_mg} mg`;
  return `${total.consumed_amount_low_mg}–${total.consumed_amount_high_mg} mg`;
}

function renderExposure(data) {
  const root = $("#result-content");
  const state = $("#calculation-state");
  state.hidden = true;
  root.hidden = false;
  const output = data.recipe_result;
  const meal = data.meal_result;
  const recipeTotal = (output.compound_totals || [])[0];
  const mealTotal = (meal.compound_totals || [])[0];
  const incomplete = String(output.calculation_status || "").toUpperCase() !== "COMPLETE" || String(meal.calculation_status || "").toUpperCase() !== "COMPLETE";
  const rows = output.ingredient_results || [];
  root.innerHTML = `
    <div class="result-banner ${incomplete ? "pending" : "ok"}">${incomplete ? "Some values are unavailable. Raw reference amounts remain separate from cooked estimates." : "All selected ingredient calculations are complete under the available evidence."}</div>
    <div class="summary-grid">
      <div class="summary-tile"><small>Recipe total · ${escapeHtml(display(recipeTotal?.compound_id))}</small><strong>${escapeHtml(totalText(recipeTotal))}</strong></div>
      <div class="summary-tile"><small>Meal total · ${escapeHtml(display(mealTotal?.compound_id))}</small><strong>${escapeHtml(totalText(mealTotal))}</strong></div>
    </div>
    <div class="result-table-wrap"><table class="result-table"><thead><tr><th>Food / compound</th><th>State</th><th>Raw reference</th><th>Consumed estimate</th><th>Status</th></tr></thead><tbody>
      ${rows.map(row => `<tr><td><strong>${escapeHtml(display(row.food_record_id))}</strong><br>${escapeHtml(display(row.compound_id))}</td><td>${escapeHtml(display(row.food_state))}</td><td>${escapeHtml(row.raw_reference_amount_mg === "" ? "Not available" : `${row.raw_reference_amount_mg} mg`)}</td><td>${escapeHtml(row.consumed_amount_low_mg === "" || row.consumed_amount_high_mg === "" ? "Not available" : `${row.consumed_amount_low_mg}–${row.consumed_amount_high_mg} mg`)}</td><td><span class="status-pill ${String(row.calculation_status || "").toUpperCase() === "COMPLETE" ? "complete" : "blocked"}">${escapeHtml(row.calculation_status)}</span><br><small>${escapeHtml(display(row.cooked_exposure_status, "Raw reference"))}</small></td></tr>`).join("")}
    </tbody></table></div>
    <div class="result-banner pending">Cooking evidence accepted: ${escapeHtml(String(data.release_context.phase2.accepted_cooking_evidence ?? "not reported"))}. A cooked estimate is withheld when the source, matrix, condition, or mass gates are not met.</div>
    ${renderCoverage(output.uncertainty_coverage)}
    ${renderCoverage(meal.uncertainty_coverage)}
    <details class="disclosure"><summary>Food sources, mappings and calculation provenance</summary><pre>${escapeHtml(JSON.stringify({ingredients: rows.map(row => ({estimate_id: row.estimate_id, food_record_id: row.food_record_id, compound_id: row.compound_id, mapping_id: row.mapping_id, input_source_ids: row.input_source_ids, provenance: row.provenance, warnings: row.warnings, missing_inputs: row.missing_inputs})), releases: data.release_context}, null, 2))}</pre></details>
    <details class="disclosure"><summary>Uncertainty and sensitivity details</summary><pre>${escapeHtml(JSON.stringify({recipe: output.ingredient_uncertainty, recipe_gap_registry: output.uncertainty_gap_registry, recipe_input_bounds: output.structured_input_uncertainty, recipe_multi_compound_sensitivity: output.multi_compound_interval_sensitivity, recipe_input_sensitivity_by_compound: output.structured_input_sensitivity_by_compound, meal: meal.ingredient_uncertainty, meal_gap_registry: meal.uncertainty_gap_registry, meal_input_bounds: meal.structured_input_uncertainty, meal_multi_compound_sensitivity: meal.multi_compound_interval_sensitivity, meal_input_sensitivity_by_compound: meal.structured_input_sensitivity_by_compound}, null, 2))}</pre></details>
    <p class="hint">Intervals are source-supported bounds or scenarios, not probability intervals. Point inputs without supported uncertainty are not treated as exact.</p>`;
  $("#export-actions").hidden = false;
  lastExport = {recipe: data.recipe, recipe_result: data.recipe_result, meal: data.meal, meal_result: data.meal_result, release_context: data.release_context, clinical_interpretation: "not_performed"};
}

function renderCoverage(coverage) {
  if (!coverage) return "";
  const missing = (coverage.dimensions || []).filter(row => row.coverage_status !== "AVAILABLE");
  return `<details class="disclosure"><summary>${escapeHtml(coverage.record_type)} uncertainty coverage · ${escapeHtml(coverage.aggregate_coverage?.status || "not assessed")}</summary><div class="result-table-wrap"><table class="result-table"><thead><tr><th>Input</th><th>Coverage</th><th>Supported</th><th>Missing</th><th>Not applicable</th></tr></thead><tbody>${(coverage.dimensions || []).map(row => `<tr><td>${escapeHtml(row.dimension)}</td><td>${escapeHtml(row.coverage_status)}</td><td>${escapeHtml(row.supported_count)}</td><td>${escapeHtml(row.missing_count)}</td><td>${escapeHtml(row.not_applicable_count)}</td></tr>`).join("")}</tbody></table></div>${missing.length ? `<p class="hint">Missing intervals are listed per ingredient in the uncertainty details. No zero-width bounds were substituted.</p>` : ""}</details>`;
}

function validateRecipeForm() {
  const issues = [];
  const ingredients = $$(".ingredient-card", $("#ingredient-list"));
  if (!ingredients.length) issues.push("Add at least one ingredient.");
  ingredients.forEach((card, index) => {
    const number = index + 1;
    const row = catalog.foods.find(item => item.food_record_id === $(".food-select", card).value);
    const compoundId = $(".compound-select", card).value;
    const mapped = row && (row.compound_ids || []).includes(compoundId);
    const quantity = Number($(".quantity", card).value);
    const serving = Number($(".serving-fraction", card).value);
    const consumed = Number($(".consumed-fraction", card).value);
    const state = $(".food-state", card).value;
    if (!row) issues.push(`Ingredient ${number}: choose a catalog food record.`);
    if (!mapped) issues.push(`Ingredient ${number}: choose a compound mapped to the selected food.`);
    if (!Number.isFinite(quantity) || quantity <= 0) issues.push(`Ingredient ${number}: quantity must be greater than zero.`);
    if (!Number.isFinite(serving) || serving < 0 || serving > 1) issues.push(`Ingredient ${number}: serving fraction must be between 0 and 1.`);
    if (!Number.isFinite(consumed) || consumed < 0 || consumed > 1) issues.push(`Ingredient ${number}: consumed fraction must be between 0 and 1.`);
    if (!state) issues.push(`Ingredient ${number}: choose the state represented by the amount you entered.`);
    if (state === "cooked") {
      if (!$("[name='cooking_method']").value) issues.push(`Ingredient ${number}: select a cooking method for a cooked state.`);
      if (row && unitDimension(row) === "volume") issues.push(`Ingredient ${number}: cooked estimates for liquid concentrations cannot be calculated because cooked volume is not collected. Select the raw or processed reference state to use the reference concentration.`);
      const cookedMass = $(".cooked-mass", card).value;
      if (cookedMass && (!Number.isFinite(Number(cookedMass)) || Number(cookedMass) <= 0)) issues.push(`Ingredient ${number}: measured cooked mass must be greater than zero.`);
    }
  });
  const servings = Number($("[name='servings_count']").value);
  const mealServings = Number($("[name='meal_servings']").value);
  if (!Number.isFinite(servings) || servings <= 0) issues.push("Recipe servings must be greater than zero.");
  if (!Number.isFinite(mealServings) || mealServings < 0) issues.push("Meal servings consumed must be zero or greater.");
  return issues;
}

async function runCalculation(event) {
  event.preventDefault();
  const status = $("#calculation-state");
  const content = $("#result-content");
  status.hidden = false;
  content.hidden = true;
  $("#export-actions").hidden = true;
  const issues = validateRecipeForm();
  if (issues.length) {
    status.innerHTML = `<strong>Check the recipe inputs</strong><ul>${issues.map(issue => `<li>${escapeHtml(issue)}</li>`).join("")}</ul>`;
    return;
  }
  status.innerHTML = `<strong>Calculating from pinned data…</strong><span>Please wait.</span>`;
  try {
    const data = await requestJson("/api/recipe/calculate", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(collectRecipeRequest())});
    renderExposure(data);
  } catch (error) {
    showError(status, error.message);
  }
}

function evidenceIdOf(row) {
  return row?.source_reference?.evidence_id || row?.source_record?.Evidence_ID || "";
}

function sourceOf(row) { return row?.source_record || {}; }
function machineOf(row) { return row?.machine_assessment || {}; }
function reviewStateOf(row) { return row?.current_review_state || {}; }

function evidenceButton(row, index) {
  const source = sourceOf(row);
  const machine = machineOf(row);
  const review = reviewStateOf(row);
  const polarity = machine.finding_polarity || "unclear";
  const hasConflict = Boolean(source.Conflict_Group) || machine.triage_state === "CONFLICT_REVIEW";
  const humanStatus = review.human_review_status || "Not returned";
  return `<button class="evidence-result" data-queue-index="${index}" aria-pressed="false">
    <strong>${escapeHtml(display(source.Compound))} · ${escapeHtml(display(source.Drug))}</strong>
    <small>${escapeHtml(evidenceIdOf(row))} · ${escapeHtml(display(row.review_id))} · ${escapeHtml(display(source.Source_Title))}</small>
    <span class="polarity ${escapeHtml(polarity)}">Machine · ${escapeHtml(polarity)}</span>
    <span class="polarity triage">${escapeHtml(display(machine.triage_state, "triage not reported"))}</span>
    ${hasConflict ? `<span class="polarity conflicting">Conflict marked</span>` : ""}
    <small>Human review · ${escapeHtml(humanStatus)} · actions ${escapeHtml(display(review.action_count, "not reported"))}</small>
  </button>`;
}

function collectQueueFilters() {
  return {
    compound: $("#filter-compound").value.trim(),
    drug: $("#filter-drug").value.trim(),
    study: $("#filter-study").value.trim(),
    evidence_category: $("#evidence-category").value,
    outcome_polarity: $("#filter-polarity").value,
    conflict_status: $("#filter-conflict").value,
    identity_status: $("#filter-identity").value.trim(),
    source_verification_status: $("#filter-source-verification").value,
    human_review_status: $("#filter-human-status").value,
  };
}

function queueQuery(offset = 0, limit = queueLimit) {
  const params = new URLSearchParams({limit: String(limit), offset: String(offset)});
  Object.entries(collectQueueFilters()).forEach(([key, value]) => { if (value) params.set(key, value); });
  return params;
}

function renderQueueRows() {
  const resultBox = $("#evidence-results");
  if (!queueRows.length) {
    resultBox.innerHTML = `<div class="empty-state compact"><strong>No matching review records</strong><span>Change one or more filters and apply them again.</span></div>`;
    $("#load-more-records").hidden = true;
    return;
  }
  resultBox.innerHTML = queueRows.map(evidenceButton).join("");
  $$(".evidence-result", resultBox).forEach(button => button.addEventListener("click", () => {
    const row = queueRows[Number(button.dataset.queueIndex)];
    $$(".evidence-result", resultBox).forEach(el => {
      el.classList.toggle("selected", el === button);
      el.setAttribute("aria-pressed", el === button ? "true" : "false");
    });
    selectEvidence(row);
  }));
  $$(".evidence-result", resultBox).forEach(button => {
    const selected = queueRows[Number(button.dataset.queueIndex)]?.review_id === selectedReviewId;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", selected ? "true" : "false");
  });
  const nextOffset = queueRows.length;
  $("#load-more-records").hidden = nextOffset >= queueTotal;
}

async function searchEvidence({append = false, keepSelected = false} = {}) {
  const status = $("#queue-result-status");
  const resultBox = $("#evidence-results");
  const offset = append ? queueRows.length : 0;
  setStatus(status, append ? "Loading the next page…" : "Applying server-side queue filters…");
  if (!append) resultBox.innerHTML = `<p class="hint">Loading review records from the pinned queue…</p>`;
  try {
    const data = await requestJson(`/api/review-queue?${queueQuery(offset)}`);
    if (!append) queueRows = [];
    queueRows = queueRows.concat(data.records || []);
    queueTotal = Number(data.total_count ?? data.source?.record_count ?? queueRows.length);
    queueOffset = offset + (data.records || []).length;
    const selectedIndex = queueRows.findIndex(row => row.review_id === selectedReviewId);
    setStatus(status, `${queueRows.length} of ${queueTotal} matching records shown · source ${display(data.source?.release_id)} · machine triage remains separate from human review.`);
    renderQueueRows();
    if (!append && selectedIndex < 0) {
      selectedEvidence = null;
      selectedReviewId = "";
      $("#selected-evidence").className = "empty-state compact";
      $("#selected-evidence").textContent = "Select a source record to inspect its finding, machine triage, mechanism candidate, and human review trace.";
      $("#gate-panel").hidden = true;
      $("#review-action-panel").hidden = true;
    } else if (selectedIndex >= 0) {
      selectEvidence(queueRows[selectedIndex]);
    }
  } catch (error) {
    setStatus(status, `Review queue unavailable: ${error.message}`, "error-text");
    if (!append) showError(resultBox, "The Stage D review queue could not be loaded. Check the loopback API and pinned queue integrity.");
    $("#load-more-records").hidden = true;
  }
}

function countText(counts = {}) {
  const pairs = Object.entries(counts).filter(([, count]) => Number(count) > 0);
  return pairs.length ? pairs.map(([name, count]) => `${name.replaceAll("_", " ")} ${count}`).join(" · ") : "None recorded";
}

async function refreshReviewCoverage() {
  try {
    const data = await requestJson("/api/review-coverage");
    const machineCounts = data.machine_triage_counts || {};
    const humanCounts = data.human_review_status_counts || {};
    const coverage = Number(data.review_coverage_fraction || 0) * 100;
    $("#review-coverage").innerHTML = `
      <div class="coverage-tile"><small>Immutable source queue</small><strong>${escapeHtml(data.record_count)} records</strong><span>${escapeHtml(display(data.source_release_id))}</span></div>
      <div class="coverage-tile machine-tile"><small>Machine triage · not decisions</small><strong>${escapeHtml(countText(machineCounts))}</strong><span>Automatic approvals ${escapeHtml(data.automatic_approval_count ?? 0)} · negative inference ${escapeHtml(data.automatic_negative_inference_count ?? 0)}</span></div>
      <div class="coverage-tile human-tile"><small>Human review status</small><strong>${escapeHtml(countText(humanCounts))}</strong><span>${escapeHtml(data.audit_action_count ?? 0)} append-only actions · accepted ${escapeHtml(data.expert_accepted_count ?? 0)} · rejected ${escapeHtml(data.expert_rejected_count ?? 0)}</span></div>
      <div class="coverage-tile"><small>Review coverage</small><strong>${coverage.toFixed(1)}%</strong><span>${escapeHtml(data.reviewed_record_count ?? 0)} reviewed · ${escapeHtml(data.not_reviewed_record_count ?? 0)} not reviewed</span></div>`;
  } catch (error) {
    $("#review-coverage").innerHTML = `<div class="result-banner pending">Review coverage unavailable: ${escapeHtml(error.message)}</div>`;
  }
}

function populateEvidenceCategories(records) {
  const select = $("#evidence-category");
  const previous = select.value;
  const categories = new Set();
  for (const row of records) {
    const source = row.source_record || row;
    const machine = row.machine_assessment || {};
    if (source.Evidence_Type || row.evidence_type) categories.add(String(source.Evidence_Type || row.evidence_type));
    if (machine.normalized_study_category || row.study_category) categories.add(String(machine.normalized_study_category || row.study_category));
  }
  select.replaceChildren(new Option("All categories", ""));
  [...categories].sort((a, b) => a.localeCompare(b)).forEach(value => select.append(new Option(value, value)));
  if (categories.has(previous)) select.value = previous;
}

async function loadEvidenceCategories() {
  try {
    const data = await requestJson("/api/evidence?limit=100");
    populateEvidenceCategories(data.results || []);
  } catch (error) {
    setStatus($("#queue-result-status"), `Evidence category choices unavailable: ${error.message}`, "error-text");
  }
}

function safeExternalLink(value) {
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) ? url.href : "";
  } catch { return ""; }
}

function selectEvidence(row) {
  selectedEvidence = row;
  selectedReviewId = row.review_id;
  const source = sourceOf(row);
  const machine = machineOf(row);
  const review = reviewStateOf(row);
  const evidenceId = evidenceIdOf(row);
  const detail = evidenceDetails.get(evidenceId) || {};
  const url = safeExternalLink(source.Source_URL || detail.source_url || "");
  const outcome = source.Outcome || source.Interaction_Effect || detail.raw_outcome;
  const selected = $("#selected-evidence");
  selected.className = "selected-source";
  selected.innerHTML = `
    <div class="state-separation"><span class="polarity ${escapeHtml(machine.finding_polarity || "unclear")}">Machine polarity · ${escapeHtml(display(machine.finding_polarity, "unclear"))}</span><span class="polarity triage">Machine triage · ${escapeHtml(display(machine.triage_state, "not reported"))}</span><span class="polarity human-state">Human status · ${escapeHtml(display(review.human_review_status, "not returned"))}</span></div>
    <h3>${escapeHtml(display(source.Compound))} · ${escapeHtml(display(source.Drug))}</h3>
    <p class="queue-id-line"><strong>Evidence_ID:</strong> ${escapeHtml(evidenceId)} · <strong>Review_ID:</strong> ${escapeHtml(display(row.review_id))}</p>
    <p><strong>Original outcome:</strong> ${escapeHtml(display(outcome))}<br><strong>Direction:</strong> ${escapeHtml(display(source.Direction || detail.direction))}<br><strong>Quantitative outcome:</strong> ${escapeHtml(display(source.Quantitative_Outcome || detail.quantitative_outcome))}</p>
    <dl class="source-meta">
      <dt>Machine triage</dt><dd>${escapeHtml(display(machine.triage_state))} · ${escapeHtml((machine.triage_reason_codes || []).join("; ") || "no reason codes reported")}<br>Source verification at triage: ${escapeHtml(display(machine.source_verification))}</dd>
      <dt>Evidence category</dt><dd>${escapeHtml(display(source.Evidence_Type))} · normalized ${escapeHtml(display(machine.normalized_study_category))}</dd>
      <dt>Study</dt><dd>${escapeHtml(display(source.Study_ID || detail.study_id))} · ${escapeHtml(display(source.Study_Design || detail.study_design))} · ${escapeHtml(display(source.Population || detail.population))}</dd>
      <dt>Dose text</dt><dd>${escapeHtml(display(source.Dose || detail.dose))}</dd>
      <dt>Source</dt><dd>${escapeHtml(display(source.Authors || detail.authors))} (${escapeHtml(display(source.Year || detail.year))}). ${escapeHtml(display(source.Source_Title || detail.source_title))}</dd>
      <dt>DOI / PMID</dt><dd>${escapeHtml(display(source.DOI || detail.doi))} / ${escapeHtml(display(source.PMID || detail.pmid))}</dd>
      <dt>Locator</dt><dd>${escapeHtml(display(source.Source_Locator || detail.source_locator))}${url ? ` · <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">Open source</a>` : ""}</dd>
      <dt>Identity</dt><dd>${escapeHtml(display(source.Identity_Status))} · Compound_ID ${escapeHtml(display(source.Compound_ID))}</dd>
      <dt>Conflict</dt><dd>${escapeHtml(display(source.Conflict_Group, "No source conflict group"))} · machine flag ${escapeHtml(display(machine.explicit_conflict_group, "none"))}</dd>
      <dt>Limitations</dt><dd>${escapeHtml(display(source.Limitations))}</dd>
    </dl>
    <details class="disclosure"><summary>Machine assessment and source record</summary><pre>${escapeHtml(JSON.stringify({machine_assessment: machine, source_record: source, source_reference: row.source_reference, groups: row.groups}, null, 2))}</pre></details>
    ${renderMechanism(detail.mechanism_candidate)}
    ${renderDecisionTrace(row)}
    <p class="hint">Source-reported outcome wording is retained. Machine polarity and conflict labels are separate from human review status.</p>`;
  const gate = $("#gate-panel");
  gate.hidden = false;
  $("#gate-grid").innerHTML = criteriaFields.map(([key, label]) => `<label class="field">${escapeHtml(label)}<select data-criterion="${key}"><option value="">Not assessed</option><option value="true">Yes · explicitly satisfied</option><option value="false">No · failed</option></select></label>`).join("");
  $("#gate-result").innerHTML = "";
  renderReviewActionForm(row);
  if (!detail.evidence_id && evidenceId) {
    requestJson(`/api/evidence?q=${encodeURIComponent(evidenceId)}&limit=100`).then(data => {
      const found = (data.results || []).find(item => item.evidence_id === evidenceId);
      if (!found) return;
      evidenceDetails.set(evidenceId, found);
      if (selectedReviewId === row.review_id) selectEvidence(row);
    }).catch(error => setStatus($("#queue-result-status"), `Source detail lookup unavailable: ${error.message}`, "error-text"));
  }
}

function renderMechanism(candidate) {
  if (!candidate || !candidate.mechanism_candidate) return `<div class="mechanism-box"><strong>Mechanism candidate:</strong> No registered source-linked mechanism candidate is returned for this Evidence_ID.</div>`;
  const item = candidate.mechanism_candidate;
  const mechanism = item.mechanism_candidate || {};
  return `<div class="mechanism-box"><strong>Mechanism candidate · ${escapeHtml(item.mechanism_record_id)}</strong>
    <p>${escapeHtml(display(mechanism.candidate_family))} · source reports ${escapeHtml(display(mechanism.source_reported_relation))}<br>Target: ${escapeHtml(display(mechanism.source_reported_target))}</p>
    <span class="polarity pending-review">${escapeHtml(display(mechanism.classification_status, "pending manual review"))}</span>
    <small>Source review: ${escapeHtml(display(item.source_verification?.review_status))} · identity: ${escapeHtml(display(item.review_state?.identity_adjudication, "not adjudicated"))}</small>
    <details class="disclosure"><summary>Mechanism provenance, criteria, and discrepancies</summary><pre>${escapeHtml(JSON.stringify(item, null, 2))}</pre></details>
    <em>Candidate only. It is not an approved mechanism or clinical interpretation.</em></div>`;
}

function renderDecisionTrace(row) {
  const state = reviewStateOf(row);
  const status = display(state.human_review_status, "No server-derived human status returned");
  const actions = Array.isArray(state.review_history) ? [...state.review_history] : [];
  if (!actions.length && state.latest_action) actions.push(state.latest_action);
  const actionCount = Number(state.action_count || 0);
  const header = `<div class="decision-trace"><h4>Human decision trace</h4><p>Current server-derived status: <strong>${escapeHtml(status)}</strong> · source verification: ${escapeHtml(display(state.source_verification_status, "not returned"))} · recorded actions: ${escapeHtml(actionCount)}</p>`;
  if (!actionCount) return `${header}<p class="trace-empty">No human actions are recorded for this queue item. Machine triage has not created a decision.</p></div>`;
  if (!actions.length) return `${header}<p class="trace-empty">The server reports prior action(s), but event detail is not included in this response. No details are reconstructed in the browser.</p></div>`;
  const partialNote = actions.length < actionCount ? `<p class="hint">Showing ${actions.length} returned event${actions.length === 1 ? "" : "s"} of ${actionCount}; earlier event details are not included in the queue response.</p>` : "";
  const timeline = actions.map((event, index) => `<article class="trace-event"><div class="trace-event-top"><strong>${escapeHtml(display(event.resulting_status))}</strong><span>${escapeHtml(display(event.review_date))} · ${escapeHtml(display(event.reviewer_name))} (${escapeHtml(display(event.reviewer_role))})</span></div><p>${escapeHtml(display(event.rationale))}</p><small>${escapeHtml(display(event.action_id))} · ${escapeHtml(display(event.source_locator))} · negative evidence ${escapeHtml(display(event.negative_evidence_assessment, "NOT_ASSESSED"))}</small>${event.event_sha256 ? `<small class="hash-line">Event hash · ${escapeHtml(event.event_sha256)}</small>` : ""}</article>`).join("");
  return `${header}${partialNote}<div class="trace-timeline">${timeline}</div></div>`;
}

function renderReviewActionForm(row) {
  const panel = $("#review-action-panel");
  panel.hidden = false;
  const review = reviewStateOf(row);
  const allowed = Array.isArray(review.allowed_next_statuses) ? review.allowed_next_statuses : [];
  const statusSelect = $("#action-status");
  const note = $("#allowed-actions-note");
  statusSelect.replaceChildren();
  if (!allowed.length) {
    statusSelect.append(new Option("No action currently allowed", ""));
    statusSelect.disabled = true;
    $("#submit-review-action").disabled = true;
    note.textContent = "The server returned no allowed next status for this review record. The UI does not infer or advance workflow state.";
    return;
  }
  statusSelect.disabled = false;
  statusSelect.append(new Option("Choose an action status", ""));
  allowed.forEach(status => statusSelect.append(new Option(status.replaceAll("_", " "), status)));
  const terminal = allowed.filter(status => ["EXPERT_ACCEPTED", "EXPERT_REJECTED"].includes(status));
  note.textContent = terminal.length
    ? `Allowed next status${allowed.length === 1 ? "" : "es"} returned by the server: ${allowed.join(", ")}. Expert acceptance or rejection is available only with the expert role.`
    : `Allowed next status${allowed.length === 1 ? "" : "es"} returned by the server: ${allowed.join(", ")}.`;
  updateActionSubmitState();
}

function updateActionSubmitState() {
  const review = reviewStateOf(selectedEvidence);
  const status = $("#action-status").value;
  const role = $("#action-reviewer-role").value;
  const allowed = Array.isArray(review.allowed_next_statuses) ? review.allowed_next_statuses : [];
  const expertOnly = ["EXPERT_ACCEPTED", "EXPERT_REJECTED"].includes(status);
  $("#submit-review-action").disabled = actionSubmitting || !status || !allowed.includes(status) || (expertOnly && role !== "expert");
}

async function submitReviewAction(event) {
  event.preventDefault();
  if (!selectedEvidence || actionSubmitting) return;
  const review = reviewStateOf(selectedEvidence);
  const action = {
    review_id: selectedEvidence.review_id,
    evidence_id: evidenceIdOf(selectedEvidence),
    resulting_status: $("#action-status").value,
    reviewer_name: $("#action-reviewer-name").value.trim(),
    reviewer_role: $("#action-reviewer-role").value,
    review_date: $("#action-review-date").value,
    source_locator: $("#action-source-locator").value.trim(),
    rationale: $("#action-rationale").value.trim(),
    negative_evidence_assessment: $("#action-negative-assessment").value,
  };
  if (!(review.allowed_next_statuses || []).includes(action.resulting_status)) {
    setStatus($("#review-action-result"), "The server has not returned this as an allowed next status. Refresh the queue before submitting.", "error-text");
    return;
  }
  if (["EXPERT_ACCEPTED", "EXPERT_REJECTED"].includes(action.resulting_status) && action.reviewer_role !== "expert") {
    setStatus($("#review-action-result"), "Expert acceptance or rejection requires the expert reviewer role.", "error-text");
    return;
  }
  if (!action.reviewer_name || !action.review_date || !action.source_locator || !action.rationale) {
    setStatus($("#review-action-result"), "Enter the reviewer, date, source locator, and rationale before submitting.", "error-text");
    return;
  }
  if (!window.confirm(`Append this human-entered action to the local Stage D audit log?\n\nEvidence_ID: ${action.evidence_id}\nReviewer: ${action.reviewer_name} (${action.reviewer_role})\nStatus: ${action.resulting_status}\n\nThis records your submitted review action; it does not alter source evidence.`)) return;
  actionSubmitting = true;
  updateActionSubmitState();
  setStatus($("#review-action-result"), "Submitting the explicitly entered action to the local audit log…");
  try {
    const data = await requestJson("/api/review-action", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(action)});
    const backup = data.backup || {};
    setStatus($("#review-action-result"), `Human-entered action recorded: ${display(data.event?.action_id)} · ${display(data.event?.resulting_status)} · backup ${display(backup.status, "not reported")}. Server-returned state: ${display(data.current_review_state?.human_review_status)}.`, backup.status === "FAILED" ? "error-text" : "success-text");
    await Promise.all([refreshReviewCoverage(), searchEvidence({keepSelected: true})]);
  } catch (error) {
    setStatus($("#review-action-result"), `Action was not confirmed by the server: ${error.message}`, "error-text");
  } finally {
    actionSubmitting = false;
    updateActionSubmitState();
  }
}

async function exportReviewAssignment() {
  const params = queueQuery(0, 100);
  params.set("format", "csv");
  const assignedTo = $("#assigned-to").value.trim();
  if (assignedTo) params.set("assigned_to", assignedTo);
  setStatus($("#queue-result-status"), "Preparing assignment CSV. Exporting records no review actions or decisions…");
  try {
    const response = await fetch(`/api/review-assignment?${params}`);
    if (!response.ok) {
      const payload = (response.headers.get("content-type") || "").includes("application/json") ? await response.json() : {};
      throw new Error(payload.error || `Export failed (${response.status})`);
    }
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = "cookrisk-review-assignment.csv";
    link.click();
    URL.revokeObjectURL(url);
    setStatus($("#queue-result-status"), "Assignment CSV downloaded. It contains no submitted reviewer decisions.");
  } catch (error) { setStatus($("#queue-result-status"), `Assignment export unavailable: ${error.message}`, "error-text"); }
}

function clearQueueFilters() {
  ["#filter-compound", "#filter-drug", "#filter-study", "#filter-identity"].forEach(selector => { $(selector).value = ""; });
  ["#evidence-category", "#filter-polarity", "#filter-conflict", "#filter-source-verification", "#filter-human-status"].forEach(selector => { $(selector).value = ""; });
  searchEvidence();
}

async function evaluateGates() {
  if (!selectedEvidence) return;
  const criteria = {};
  $$("[data-criterion]").forEach(select => {
    const value = select.value;
    criteria[select.dataset.criterion] = value === "" ? null : value === "true";
  });
  const box = $("#gate-result");
  box.innerHTML = `<p class="hint">Evaluating explicitly selected gates…</p>`;
  try {
    const data = await requestJson("/api/comparability", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({evidence_id: evidenceIdOf(selectedEvidence), criteria})});
    const gate = data.comparability;
    const tone = gate.decision === "READY_FOR_REVIEW" ? "ok" : "pending";
    box.innerHTML = `<div class="result-banner ${tone}"><strong>${escapeHtml(gate.decision)}</strong><br>${escapeHtml(gate.decision_reason)}<br><br>Cross-stage exposure linkage: ${escapeHtml(data.cross_stage_linkage)}. Clinical interpretation: not performed.</div><details class="disclosure"><summary>Gate details</summary><pre>${escapeHtml(JSON.stringify(gate.criteria, null, 2))}</pre></details>`;
  } catch (error) { showError(box, error.message); }
}

async function exportResult(format) {
  if (!lastExport) return;
  try {
    const response = await fetch("/api/export", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({format, filename: "cookrisk-recipe", result: lastExport})});
    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.error || `Export failed (${response.status})`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `cookrisk-recipe.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) { showError($("#result-content"), error.message); }
}

async function init() {
  $$(".tab").forEach(button => button.addEventListener("click", () => {
    $$(".tab").forEach(item => item.classList.toggle("active", item === button));
    $$(".view").forEach(view => view.classList.toggle("active", view.id === button.dataset.view));
  }));
  $("#recipe-form").addEventListener("submit", runCalculation);
  $("#add-ingredient").addEventListener("click", addIngredient);
  $("#catalog-filter").addEventListener("input", applyCatalogFilter);
  $("#search-evidence").addEventListener("click", searchEvidence);
  $("#clear-filters").addEventListener("click", clearQueueFilters);
  $("#load-more-records").addEventListener("click", () => searchEvidence({append: true}));
  $("#export-assignment").addEventListener("click", exportReviewAssignment);
  $("#review-action-form").addEventListener("submit", submitReviewAction);
  $("#action-status").addEventListener("change", updateActionSubmitState);
  $("#action-reviewer-role").addEventListener("change", updateActionSubmitState);
  ["#filter-compound", "#filter-drug", "#filter-study", "#filter-identity"].forEach(selector => {
    $(selector).addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); searchEvidence(); } });
  });
  $("#evaluate-gates").addEventListener("click", evaluateGates);
  $$("[data-export]").forEach(button => button.addEventListener("click", () => exportResult(button.dataset.export)));
  try {
    const [health, data] = await Promise.all([requestJson("/api/health"), requestJson("/api/catalog")]);
    catalog = data;
    $("#release-status").textContent = `Verified inputs · Phase 1B ${health.phase1b.release_id} (${health.phase1b.food_records} foods) · Phase 2 ${health.phase2.release_id} (${health.phase2.accepted_cooking_evidence} accepted cooking estimates) · Stage B source ${health.stage_b_source.rows} rows · Stage A inference not run.`;
    addIngredient();
    $("#action-review-date").value = new Date().toISOString().slice(0, 10);
    await Promise.all([searchEvidence(), refreshReviewCoverage(), loadEvidenceCategories()]);
  } catch (error) {
    $("#release-status").textContent = `Pinned data could not be loaded: ${error.message}. Check the local data package integrity before continuing.`;
    $("#release-status").classList.add("error-text");
  }
}

document.addEventListener("DOMContentLoaded", init);
