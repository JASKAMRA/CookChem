# Stage A continuous recovery log

## Iteration 1 — primary-source coverage and recovery (2026-11-10)

- **Weakness addressed:** source-family and food-matrix coverage; prior v0.3 source-held-out validation was negative.
- **Investigated:** historical family `10.1155/2016/1398298` (Ombra et al., 2016) and new primary literature.
- **Excluded, not repaired:** the 26 historical Ombra ratios remain excluded. Table 4 gives raw/cooked compound values and a pressure-cooker protocol, but does not state an unambiguous common fresh- or dry-weight basis for the chromatographic table. Rehydration and cooking change mass, so the observations cannot be silently treated as compatible concentration ratios.
- **Admitted:** Hossain et al. (2023), DOI `10.1016/j.heliyon.2023.e21709`, Tables 1 and 3. Added 36 primary-table observations (six vegetables × beta-carotene/vitamin C × boiling/steaming/microwaving). All values are mg/100 g fresh weight; means are triplicate means; treatment time, water amount, and microwave power are carried from Table 1. Temperature was not reported and is left missing.
- **Dataset lineage:** v0.3 (338 rows, six DOI families) → v0.4 (374 rows, seven DOI families; SHA-256 `60bab0b12c3d8eb345450cf71f5951522730b7eafa65c5b181465594912fe8db`). Target remains `100 * C_cooked / C_raw`, explicitly an apparent concentration ratio, never total-mass retention.
- **Model comparison:** selected experimental Extra Trees: compound-grouped 5-fold R² 0.3317, MAE 44.0411, RMSE 151.3577; source LOSO R² -0.0420, MAE 57.9199, RMSE 188.9914. Versus v0.3 selected RF, compound-grouped MAE improved from 48.1166 to 44.0411, but source transfer is still negative.
- **Validation and integrity:** dataset contract, row/source count, model checksum, and smoke prediction pass in `recovery_v0_4_0_2026_11_10/validate_v04.py`. No Stage C integration was authorized or changed.
- **Decision:** retain v0.4 as `EXPERIMENTAL_NOT_DEPLOYABLE`. The additional family improves compound-held-out MAE but does not establish unseen-source generalisation.

## Iteration 2 — next literature batch started (2026-11-10)

- **New candidates identified:**
  - `10.1007/s10068-017-0281-1` / PMC6049644, *Effect of different cooking methods on the content of vitamins and true retention in selected vegetables*: primary Table 2 reports vitamin-C concentrations and true retention across cooking treatments. Primary full-text XML retrieval returned an upstream HTTP 500, so no values were extracted from a search summary.
  - `10.3390/foods10050960` / PMC8145054: already included in v0.3; do not duplicate.
  - `10.1007/s11130-020-00808-0` / PMC7266791: potato vitamin-C and processing table; assess protocol fields and overlap before admission.
  - `10.3389/fnut.2020.580550` / PMC7779405: investigate measurement basis and per-treatment conditions before any admission.
- **Next highest-priority task:** retrieve and inspect the candidate primary tables and methods, extract only entries with a stated compatible basis and enough process metadata, then rerun strict source-, food-, and method-held-out diagnostics. Treat temporary full-text service errors as access limitations, not evidence.

## Current status

**RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT.** The concentration-ratio target is auditable for v0.4 admissions, but no model demonstrates useful new-source generalisation. Stage C remains fail-closed.

## Iteration 2 — independent-source expansion and strict validation completed (2026-11-10)

- **Admitted:** Narwojsz et al. (2020), DOI `10.1007/s11130-020-00808-0`: five raw/cooked vitamin-C pairs, Table 2, mg/100 g dry weight, one potato cultivar across boiling, steaming, combi steaming, microwaving, and grilling. All protocols were independently confirmed in Methods.
- **Excluded:** Managa et al. (2020), DOI `10.3389/fnut.2020.580550`: detailed raw/cooked phenolic values and protocols, but the table states mg/kg without fresh/dry basis while the analytical material is freeze-dried.
- **Still pending:** Lee et al. (2018), DOI `10.1007/s10068-017-0281-1`; do not recover from publisher preview or search snippets.
- **Lineage:** v0.4 374 rows/7 DOI families → v0.5 379 rows/8 DOI families. v0.5 hash: `72b1f7d547b19b40a58eb43db773d64996dfb1e6c4d5cb44d38c7d3845bb9cc0`.
- **Diversity:** 46 compound groups, 15 food matrices, 15 cooking-method labels. The added source improves independent source coverage but remains a narrow five-observation potato/vitamin-C family.
- **Models:** Random Forest selected by compound-grouped MAE: R² 0.3847, MAE 41.3572, RMSE 144.2958. Source LOSO: R² -0.0628. Extra Trees source LOSO: R² -0.0393. XGBoost source LOSO: R² -0.0275. None validates transfer to a new research source.
- **Additional stress tests:** food-matrix grouped pooled R² -0.0464; cooking-method LOSO pooled R² -0.0098. Single-observation method folds have undefined R² and are not evidence of generalisation.
- **Feature diagnostic:** `c__cooking_medium_Microwave` has 0.6725 full-fit Random Forest importance. This confirms a dominant protocol/source proxy, not a causal microwave conclusion.
- **Decision:** Preserve v0.5 as an experimental recovery package. Continue literature acquisition focused on independently sourced studies with explicit fresh/dry basis and process protocols; do not deploy or alter Stage C.

## Iteration 3 — source confounding and overlap diagnosis (2026-11-10)

- **Dataset:** held fixed at v0.5 (379 rows, 8 DOI families); no new observation was admitted because the available candidate evidence did not satisfy the shared-basis contract.
- **Confounding evidence:** normalized mutual information with DOI is 0.9256 for food matrix and 0.9236 for measurement basis; compound is 0.6954; cooking medium is 0.4804. Temperature missingness ranges from 0 to 100% by source and duration missingness ranges by 90.9 percentage points. This shows source family strongly determines experimental domain and missingness pattern.
- **Ablation outcome:** the fixed 50-tree diagnostic RF full model gives source-LOSO R² -0.0416, MAE 56.1391. The lowest source-LOSO MAE is molecular-plus-cooking (56.0980), but R² remains -0.0412. Removing all medium variables worsens source R² to -0.1842; masking microwave medium worsens it to -0.6461. No ablation produces positive source transfer.
- **Microwave conclusion:** its apparent importance is a source/protocol proxy in the current sparse-overlap data. Feature removal demonstrates dependence on the label, not causality.
- **Coverage decision:** most DOI families occupy distinct compound–food–method–basis regions. The next acquisition must prioritize independent replications of existing cells, especially vitamin C/carotenoids under boiling, steaming, and microwave methods with an explicit common FW or DW basis.
- **Primary-source scan:** PMC6049644 / DOI `10.1007/s10068-017-0281-1` remains a high-value overlap candidate; primary-table access must be acquired before any extraction. A further candidate, DOI `10.1155/2020/8856260`, reports raw/cooked bioactive compounds on FW basis and should be inspected through its primary full text before admission.
- **Decision:** v0.6 is a diagnostic package only. Stage A remains **RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT** and Stage C remains untouched.

## Iteration 4 — matched experimental evidence acquisition (2026-11-10)

- **Recovered primary source:** Lee et al. (2018), DOI `10.1007/s10068-017-0281-1`, was accessed through PMC primary full text. Table 1 supplies method-specific timings and Table 2 supplies HPLC vitamin-C concentrations in mg/kg fresh weight.
- **Admitted:** 28 apparent-concentration pairs: vitamin C in broccoli, chard, potato, sweet potato, carrot, spinach, and zucchini; each under boiling, blanching, steaming, and microwaving. Temperature was not reported as an exact value and remains missing. The paper's true-retention statistic is retained as context but never substituted for the apparent-ratio target.
- **Lineage:** v0.5/v0.6 379 rows, 8 DOI families → v0.7 407 rows, 9 DOI families. Dataset formula validation passes for all 28 additions.
- **Exact compatible overlap:** six compound × food × method × basis cells now have two DOI families: vitamin C in carrot and spinach under boiling, steaming, and microwave treatment, all on fresh-weight basis. This is the first direct independent replication evidence in the clean dataset.
- **Decision gate:** D — continued data acquisition. Six two-source cells are insufficient to fit or validate a matched-cell model, and no new general model was trained. Candidate `10.1155/2020/8856260` is a verified primary paper with compatible protocols but its individual phenolic-acid tables remain pending extraction.
- **Status:** **RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT**. Stage C remains unchanged.

## Iteration 5 — Candidate B extraction and targeted overlap review (2026-11-10)

- **Candidate B completed:** Musilova et al. (2020), DOI `10.1155/2020/8856260`, Table 6: HPLC-DAD phenolic acids in mg/kg fresh weight across four sweet-potato cultivar-origin strata and boiling, steaming, microwave, and baking treatments.
- **Admitted:** 32 apparent-ratio pairs for chlorogenic acid and trans-ferulic acid. The source reports raw/cooked values on the same FW basis and explicit protocols. Neochlorogenic acid was documented but excluded from the model-ready data because the established descriptor schema has no verified canonical record; no descriptor was invented.
- **Lineage:** v0.7 407 rows/9 DOI families → v0.8 439 rows/10 DOI families. Formula and provenance validation pass.
- **Replication result:** Candidate B diversifies compounds and cooking conditions but does not create a third independent DOI for the six exact Vitamin C carrot/spinach FW cells. It does not resolve the source-overlap limitation.
- **Decision:** C — continue targeted matched-evidence acquisition; no model retraining is justified. Stage A remains **RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT**.

## Iteration 6 — full dataset intelligence and modelling-readiness audit (2026-11-10)

- **Dataset held fixed:** v0.9 is a reproducible audit of the v0.8 parent (439 observations, 10 DOI families); it adds, removes, converts, and re-estimates no observations. The parent SHA-256 is `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a`.
- **Strict overlap correction:** the six Vitamin-C carrot/spinach × boiling/steaming/microwave cases are cross-source matches only at compound × food × method × stated-basis level. Their duration and/or medium/protocol reporting differs, so they are six **categorical protocol near-matches**, not protocol-identical independent replications. Strict cross-source replications: zero.
- **Coverage:** Vitamin C has the strongest broad cross-source representation (51 observations, 3 DOI families, 12 foods); chlorogenic and ferulic acid have 37 each across 2 DOI families and 5 matrices. Large source-specific clusters remain: potato (84 rows from a 2-source total), pumpkin leaves (84 from one source), red cabbage (50 from one), broccoli (59 from two), and turmeric (33 from one).
- **Descriptor and target audit:** all 439 included observations have finite values for all recorded RDKit fields. The target remains the verified apparent concentration ratio `100 × C_cooked / C_raw`; the audit makes no total-mass-retention calculation because established matched mass/yield evidence is unavailable.
- **Readiness:** Domain A (Vitamin C carrot/spinach) contains 12 FW observations from two families but only protocol near-matches. Domain B (sweet-potato chlorogenic/ferulic acid) contains 32 FW observations from one family; cultivar-origin strata are not independent studies. Both are **C — more matched evidence required**. No model was trained.
- **Next decision:** seek a third independent, protocol-aligned FW Vitamin-C study first, then an independent raw/cooked FW HPLC study for sweet-potato chlorogenic/ferulic acid. Do not collect unrelated one-paper clusters. Stage A remains **RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT**; Stage C remains untouched.

## Iteration 7 — targeted independent-source acquisition (2026-11-10)

- **Dataset held fixed:** v1.0.0 is a bounded candidate-acquisition package over the v0.9 parent (439 observations, 10 admitted DOI families; parent SHA-256 `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a`). No new observation or source family was admitted.
- **Vitamin C evidence:** Oliveira et al. (2013), DOI `10.1108/NFS-12-2012-0126`, is an independent HPLC carrot study with raw/cooked numeric values and cooking details. It is a categorical match only, not a strict match: its table reports wet basis rather than explicit FW and uses 25-minute boiling/steaming or 10-minute microwave treatments. Zeng (2013), DOI `10.1108/NFS-11-2012-0123`, has the spinach/method scope but lacks an accessible auditable raw/cooked numeric table and basis verification. A further carrot paper has no DOI and is not admissible.
- **Sweet-potato evidence:** Kido et al. (2024), DOI `10.3390/foods13071101`, is independent HPLC CQA research but differs in analyte scope, methods and verified basis. Frankova et al. (2022), DOI `10.3390/molecules27061884`, is DW-based and shares Candidate-B author/protocol context; it is not independent matched evidence. Ryu et al. (2020), DOI `10.3746/jkfn.2020.49.8.836`, verifies FW LC-MS/MS scope but lacks an accessible individual raw/cooked numeric table.
- **Decision:** **C — both domains still require additional independent matched evidence.** Vitamin C remains the closer acquisition target, but neither domain supports model fitting or honest held-out-source validation. Strict protocol matches obtained: zero. Stage A remains **RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT**; Stage C remains untouched.

## Final implementation sprint — reproducible prototype evaluation (2026-11-10)

- **Frozen input:** v1.0 authoritative dataset, 439 observations and 10 DOI families, SHA-256 `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a`. The final package copied the input and changed no historical record.
- **Target and features:** all 439 verified apparent concentration ratios were eligible after formula validation allowing only documented two-decimal target rounding (maximum observed discrepancy below 0.01 percentage points). Molecular weight, LogP, TPSA, H-bond donor/acceptor counts, rotatable bonds, aromatic rings and hydroxyl groups were used as actual features together with raw concentration, temperature, time, class, food, method, medium and stated measurement basis. Canonical SMILES are not present in the authoritative data and were not invented.
- **Validation:** fold-safe preprocessing and bounded, documented configurations evaluated dummy, Ridge, Random Forest, Extra Trees and XGBoost under random, compound-grouped, food-matrix-grouped and leave-one-source-family-out designs. Random Extra Trees was strongest descriptively (R² 0.4340, MAE 32.92), but food-matrix and source-held-out performance stayed negative. The least-poor source-held-out candidate was Random Forest (R² -0.0264, MAE 50.58, RMSE 173.61).
- **Ablation:** descriptors alone failed (source-held-out R² -0.1157); molecular-plus-cooking achieved source-held-out R² -0.0249 but did not supply stable improvement and worsened compound-grouped performance relative to cooking/experimental features. Molecular descriptors therefore do not establish generalisable benefit in this dataset.
- **Final scope:** **C — no defensible general predictive model.** No serialized model was released; `prediction_interface.py` is fail-closed. Within-source random interpolation diagnostics are retained only as restricted descriptive evidence. Stage C remains blocked and untouched.

## Dataset expansion sprint — controlled batch 001 (2026-11-10)

- **Admission:** Zhao et al. (2024), DOI `10.1007/s10068-024-01623-y`, Table 2 and Methods: 12 red-bell-pepper Vitamin-C apparent-ratio condition means (oven cooking, air frying, infrared grilling × 170/180/190/200 °C; 15 min), measured by HPLC-PDA and stated as mg/g dry weight. Raw and cooked mean ± SD values are retained; triplicate technical measurements were not expanded into artificial rows.
- **Lineage:** v1 parent 439 rows/10 DOI families (SHA-256 `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a`) → controlled expansion master 451 rows/11 DOI families. Parent rows and historical packages remain unchanged.
- **Rejected backlog:** existing red-cabbage and potato DOI families were duplicate candidates; total-isothiocyanate yield was excluded as an aggregate assay outcome without one canonical molecular identity; wet-basis carrot data remain unadmitted rather than relabelled FW.
- **Decision:** 1,000 observations was not reached in this controlled batch. The additions create zero strict cross-source protocol-identical replications and do not authorize model retraining or Stage C integration. Continue only with primary-table batches meeting the same traceability contract.

## Dataset expansion sprint — controlled batch 002 (2026-11-10)

- **Admission:** Li et al. (2024), DOI `10.3390/foods13020230`, Table 1 and Methods §§2.2, 2.4–2.7: 20 triticale phenolic-acid apparent-ratio condition means in μg/g dry sample, measured by HPLC-DAD with authentic standards and reported as mean ± SD across three repetitions. The values cover atmospheric-pressure porridge boiling (90 min) and high-pressure boiling (60 min, 60 kPa).
- **Analytical-fraction safeguard:** the source makes separate free and bound extractions. Batch 002 preserves `analytical_definition` and only forms raw/cooked ratios within the same fraction. The 20 admitted values cover protocatechuic (4), syringic (4), caffeic (1), p-coumaric (3), ferulic (4), and sinapic acid (4). Four additional Table-1 analytes are excluded because exact verified descriptor identities are not present in the existing schema; no identity or descriptor was inferred.
- **Lineage:** Batch 001 451 rows/11 DOI families (SHA-256 `7c0e415ddd08363b509fb69e1ad934809fd4df31d6d75a94c2a4bc1adbbb3ab8`) → Batch 002 471 rows/12 DOI families. The batch validator proves byte-for-value preservation of the 451 parent rows on the original parent schema, formula correctness, source count, fraction labels, and non-null canonical molecular IDs for every addition.
- **Decision:** 1,000 observations is still not reached. The new cereal/HPLC source diversifies the evidence but creates zero strict protocol-identical cross-source replications. No model was retrained, Stage C remains untouched, and the research prototype remains not deployable.

## Dataset expansion sprint — controlled batch 003 (2026-11-10)

- **Admission:** two independent primary DOI families, 17 additions. Najman et al. (2023), DOI `10.3390/molecules28073066`, Tables 3–4, supplies 14 quince pairs for lutein, beta-carotene, quercetin, chlorogenic, caffeic, p-coumaric, and ferulic acid under water cooking (100 °C, 40 min) and no-fat pan frying (40 min). Chang et al. (2024), DOI `10.3390/antiox13070755`, Table 5, supplies three detected free-caffeic-acid ProSoy pairs at 100 °C for 20 min across distinct grinding conditions.
- **Basis and identity safeguards:** quince `mg/100 g product` remains exactly that, never relabelled FW or DW. Soymilk values are explicitly dry basis. Nondetect pairs, aggregate endpoints, and analytes without an existing exact verified descriptor identity remain excluded.
- **Lineage:** Batch 002 471 rows/12 DOI families (SHA-256 `86d8ed4a7748fad15cb84a0aac783ce0c1f8ef85897055d4397cc0ad72800ee5`) → Batch 003 488 rows/14 DOI families. The validator confirms full parent preservation, calculated target values, DOI count, exact basis labels, and no Stage-C authorization.

## Dataset expansion sprint — controlled batch 004 (2026-11-10)

- **Admission:** Mustafa et al. (2021), DOI `10.3390/plants10102192`, Table 2 and Methods §§3.2–3.4: 36 individual HPLC-MS/MS raw/cooked concentration pairs from edible sweet-chestnut seed. The additions cover chlorogenic, caffeic, syringic, p-coumaric, and ferulic acid plus rutin, isoquercitrin, quercetin, and kaempferol under boiling, microwave roasting, oven roasting, and pan frying. The stated basis is dry weight; raw/cooked means ± SD arise from duplicate HPLC analyses.
- **Scope safeguards:** all chestnut shell values are excluded as non-edible matrix evidence; aggregate totals and nondetects are excluded; (+)-catechin is excluded rather than mapped to generic parent `Catechin`, because the source establishes a stereochemical form; no new identity or descriptor was inferred.
- **Lineage:** Batch 003 488 rows/14 DOI families (SHA-256 `0a051b09f3db43dc936bdc0cf3a2e064a78bb417f8142cf727e973a8f3a7d4a8`) → Batch 004 524 rows/15 DOI families. The validator confirms full parent preservation, analytic target equality, individual source basis, and the fail-closed Stage-C gate.
- **Decision:** the dataset is now materially larger and more compound-diverse but the 1,000-observation target remains unreached; the growing source clusters still do not establish source-held-out generalisation. Continue evidence-gated acquisition; do not retrain or deploy.

## Dataset expansion sprint — controlled batch 005 (2026-11-10)

- **Admission:** two independent primary DOI families add 15 pairs. Kongphapa et al. (2022), DOI `10.14456/apst.2022.5`, Table 4 and Methods §§2.1, 2.7, supplies nine individual HPLC-DAD raw-versus-boiled Chaya-leaf pairs (100 °C, 15 min, then dried; mg/100 g dry weight; triplicate mean ± SD). Kayahan and Saloglu (2021), DOI `10.3389/fsufs.2021.761145`, Table 4, supplies six individual HPLC-DAD chlorogenic-acid pairs in receptacles of Sakiz and Bayrampasa artichoke after boiling, microwave cooking, and baking.
- **Basis safeguard:** the artichoke Table 4 unit is mg/kg but does not label a fresh- or dry-weight basis. Those six values are retained exactly as `as reported (basis unspecified)` and are not converted, relabelled, or pooled with a fresh- or dry-weight subset.
- **Exclusions:** Chaya Table-4 compounds without exact existing descriptor identities are not inferred. Artichoke analytes without exact existing descriptor identities and limit-of-detection values are excluded. The red/purple-potato chlorogenic-acid-and-isomers endpoint is excluded as an aggregate; `10.3390/molecules31162740` is excluded as already present in the parent data; a Lima-bean source is held out because no article DOI was verified.
- **Lineage:** Batch 004 524 rows/15 DOI families (SHA-256 `87e88a8c51054f144a45f5baa9ba71566e1227eb73f02c8603af959f84c9d5bb`) → Batch 005 539 rows/17 DOI families. `validate_batch_005.py` proves parent preservation, new-ID uniqueness, formula equality, source count, exact reported bases, and the fail-closed Stage-C gate.
- **Decision:** 461 verified observations are still required. No model was retrained; no Stage B/C/D or Git state changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 006 (2026-11-10)

- **Admission:** Ahmed and Ali (2013), DOI `10.1155/2013/367819`, Table 3 and Methods §§2.1–2.3.7, supplies 34 individual HPLC raw/cooked phenolic pairs in edible white-cauliflower florets, stated as mg/100 g dry weight. Conditions span steam/water blanching, steam/water boiling, microwave cooking, and stir-frying; methods document portions, media, temperature/power and durations. Every HPLC sample was analysed in triplicate, but Table 3 does not report per-analyte SD, so no SD is invented.
- **Scope safeguards:** only positive, individually identified table entries with an exact established descriptor identity are admitted. ND entries, molecules with no existing exact identity, and generic `Coumaric acid` (which cannot be silently assigned to `p-Coumaric acid`) remain excluded. A prospective broccoli table was rejected because DOI `10.3390/plants13101283` is already represented in the parent dataset.
- **Lineage:** Batch 005 539 rows/17 DOI families (SHA-256 `2199766393168dc7f6561f5f30751f7ba89877c8e2631287dffedb49021e5aee`) → Batch 006 573 rows/18 DOI families. `validate_batch_006.py` proves full parent preservation, unique IDs, direct target calculation, source count, stated DW basis, and fail-closed Stage-C status.
- **Decision:** 427 verified observations remain. This new source improves food and method coverage but creates no strict cross-source protocol-identical replication. No model was retrained; continue evidence-gated independent-source acquisition.

## Dataset expansion sprint — controlled batch 007 (2026-11-10)

- **Admission:** Chen et al. (2017), DOI `10.3136/fstr.23.193`, Table 4, supplies 12 individual HPLC dry-weight phenolic-acid pairs in purple sweet potato across steaming, microwave-then-steam, steam-then-microwave, and microwaving. Demirel Ozbek et al. (2024), DOI `10.1371/journal.pone.0299037`, Table 2, supplies 15 individual HPLC-UV dry-weight caffeic-acid pairs in the edible leaves and stems of *Trachystemon orientalis* across boiling, steaming, stir-frying, microwaving, and sous vide, each at three durations.
- **Scope safeguards:** Chen's values are treatment means from triplicate cooking procedures but Table 4 gives no SD, so none is invented. The Trachystemon table's raw-protocatechuic and raw-p-coumaric cells are non-detect; these are excluded rather than converted to zero or used to calculate ratios. Molecules without an exact established descriptor identity remain excluded.
- **Lineage:** Batch 006 573 rows/18 DOI families (SHA-256 `b825394f8bef74365b2e2e45691ec045b616db716033f5bf433ec8fa727efdf3`) → Batch 007 600 rows/20 DOI families. `validate_batch_007.py` verifies total count, full parent preservation, unique IDs, formula equality, stated DW basis, and fail-closed Stage-C status.
- **Decision:** 400 verified observations remain. No model was retrained and no Stage B/C/D, Git, commit, or remote state was changed. Continue with new independent sources rather than treating this checkpoint as completion.

## Dataset expansion sprint — controlled batch 008 (2026-11-10)

- **Admission:** Acito et al. (2024), DOI `10.1016/j.jff.2024.106380`, Table 1 and Methods §§2.2–2.3, supplies 35 individual HPLC-ESI-MS/MS raw/cooked pairs in mg/kg fresh matter. The raw, 40-minute boiled, and 20-minute pressure-cooked values cover catechin; chlorogenic, caffeic, p-coumaric and ferulic acids; rutin; and isoquercitrin across T0 local red-skinned potato, T1 one-month-stored local potato, and commercial red-skinned potato strata.
- **Scope safeguards:** each cultivar/storage/commercial stratum is preserved as a distinct food-matrix label; technical measurement repetitions are not expanded. All non-detects and analytes without an exact established descriptor identity remain excluded. The table reports an RSD range rather than per-cell SD; no individual SD is invented.
- **Lineage:** Batch 007 600 rows/20 DOI families (SHA-256 `827a9ac83a57cc523ed230512461f5a76e7ff4f46f35118eee6852a37a009176`) → Batch 008 635 rows/21 DOI families. The Batch-008 validator confirms full parent preservation, unique IDs, target equality, direct FM basis, DOI count, and fail-closed Stage-C status.
- **Decision:** 365 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 009 (2026-11-10)

- **Admission:** Pedišić et al. (2018), DOI `10.17113/ftb.56.04.18.5709`, Table 1 and the processing/HPLC methods, supplies 32 individual HPLC-UV/Vis-PDA raw/cooked phenolic-acid pairs in Croatian domestic garlic, explicitly stated as mg/100 g fresh mass. The evidence covers protocatechuic, caffeic, p-coumaric and ferulic acids under water blanching at 100 °C and dry frying at 120 °C, each for 2, 5, 8 and 10 minutes.
- **Scope safeguards:** the raw fresh control and each cooked condition mean become one row; reported technical measurement replication is never expanded. Crushed-at-room-temperature samples are not cooking treatments and are excluded. Gallic and p-hydroxybenzoic acid table values lack exact established descriptor identities in the current master and are not inferred. Total phenolics, trace-only quercetin, organosulfur compounds and aggregate endpoints are excluded.
- **Lineage:** Batch 008 635 rows/21 DOI families (SHA-256 `951a1ce20a60245c19aff1908ec806a9f75b27219b8a321d20662f290d5c6f79`) → Batch 009 667 rows/22 DOI families. `validate_batch_009.py` confirms full parent preservation, unique IDs, target equality, stated fresh-mass basis, source count, and the fail-closed Stage-C status.
- **Decision:** 333 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 010 (2026-11-10)

- **Admission:** AlJuhaimi et al. (2024), DOI `10.3390/pr12102114`, Table 2 and Methods §§2.1–2.2.8, supplies 40 individual HPLC-PDA raw/cooked phenolic pairs in edible cauliflower florets, explicitly reported as mg/100 g dry weight. The additions cover catechin; caffeic, syringic, p-coumaric, ferulic and cinnamic acids; rutin; resveratrol; quercetin; and kaempferol under pressure cooking, conventional boiling, oven heating and microwave heating.
- **Scope safeguards:** each of the source's three independent experiment means stays a single condition row; analytical triplicates are never expanded. Gallic acid and 3,4-dihydroxybenzoic acid are excluded because neither has an exact established descriptor identity in the current master. Total phenolic/flavonoid, antioxidant and mineral outputs are aggregate or non-target endpoints and are excluded.
- **Lineage:** Batch 009 667 rows/22 DOI families (SHA-256 `e9de878deb24f88d6e25a3f52af389d155dc27227729efdd8c1b65a36806998c`) → Batch 010 707 rows/23 DOI families. `validate_batch_010.py` confirms full parent preservation, unique IDs, target equality, stated dry-weight basis, source count, and fail-closed Stage-C status.
- **Decision:** 293 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 011 (2026-11-10)

- **Admission:** Kaplan and Fıratlıgil (2024), DOI `10.3390/foods13213459`, Tables 6–7 and Methods §§2.3–2.5, supplies 12 raw/cooked pairs reported in mg/100 g dry basis. The additions are individual HPLC-PAD Vitamin-C data for broccoli, red pepper and carrot plus directly quantified beta-carotene for carrot under conventional oven cooking, 2450-MHz microwave cooking and 910-MHz solid-state microwave cooking.
- **Scope safeguards:** Table 1 reports the common 75 °C internal target and Table 2 gives cooking-time ranges. The time field is therefore left missing rather than assigned an invented midpoint. Each table mean is one record. Total phenolic content and chlorophyll are aggregate assays; lycopene is outside the current exact descriptor schema; all are excluded.
- **Lineage:** Batch 010 707 rows/23 DOI families (SHA-256 `911d49c39fb851bb05b59bdb7177f1d779acab0a3d19ef9306d066d2f9f57918`) → Batch 011 719 rows/24 DOI families. `validate_batch_011.py` confirms full parent preservation, unique IDs, target equality, reported dry basis, source count, and fail-closed Stage-C status.
- **Decision:** 281 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 012 (2026-11-10)

- **Admission:** Narwojsz et al. (2025), DOI `10.3390/app15010254`, Tables 3–4 and Methods §§2.2–2.5.2, supplies 30 individual raw/cooked pairs in whole unpeeled carrot roots, stated as µg/g dry weight. The source covers caffeic, chlorogenic, ferulic and p-coumaric acids plus lutein and beta-carotene under boiling, two separately documented steaming protocols, baking and sous-vide.
- **Scope safeguards:** the five source protocols remain distinguishable in the raw identifiers and the source method field, even though the two steaming treatments share a normalized class. Raw-absent quercetin entities and zero-cooked rutin values do not produce ratios. m-Coumaric and vanillic acids lack exact established descriptor identities in this master, so they are not inferred. Each of the three independent process means stays one row.
- **Lineage:** Batch 011 719 rows/24 DOI families (SHA-256 `4fd3ac9096e7dee2281dab8863d947a502e30db8fc6e371728f7b5f71154ab0f`) → Batch 012 749 rows/25 DOI families. `validate_batch_012.py` confirms full parent preservation, unique IDs, target equality, dry-weight labelling, source count, and fail-closed Stage-C status.
- **Decision:** 251 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 013 (2026-11-10)

- **Admission:** Jimenez-Aspee et al. (2026), DOI `10.1007/s11130-026-01551-8`, Table 1 and open publisher Supplementary Materials (Plant material), supplies eight individual raw/boiled Loche-squash-pulp pairs. Table results are reported in mg/100 g dry weight; the supplement verifies water at 1:5 w/v and a 20-minute boil before freeze-drying. The retained identities are beta-carotene, lutein, alpha- and gamma-tocopherol, and protocatechuic, caffeic, p-coumaric and ferulic acids.
- **Scope safeguards:** each published mean is one condition record. The paper calls the three separately prepared composite-pulp portions technical replicates, and they are never expanded into three observations. The table's digested-matrix results do not meet the raw/cooked target; nondetects, aggregates and identities lacking an exact existing descriptor remain excluded.
- **Lineage:** Batch 012 749 rows/25 DOI families (SHA-256 `eb12ba936cd1b834208603abf0ed108dcc31a63ce27163c047d65e1dd9808f9b`) → Batch 013 757 rows/26 DOI families. `validate_batch_013.py` confirms full parent preservation, unique IDs, target equality, dry-weight labelling, source count, 20-minute condition traceability, and fail-closed Stage-C status.
- **Decision:** 243 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 015 (2026-11-10)

- **Admission:** Prasanthi et al. (2017), DOI `10.1007/s13197-017-2547-2`, Tables 1, 4 and 5, adds 39 raw/cooked pairs from eight distinct corn matrices: baby, sweet and dent corn; popcorn with and without oil; corn grits; corn flour; and corn flakes. Table 1 documents steaming (8–10 min), boiling (3–8 min), pressure-cooker popping (6 min) and frying; Tables 4–5 explicitly report individual HPLC/RPHPLC results on a fresh-weight basis.
- **Scope safeguards:** only direct individual values for exact established identities—lutein plus caffeic, syringic, p-coumaric and ferulic acids—are retained. Each mean ± SD from three composite food samples remains one condition row. Aggregate endpoints, non-detects, and molecules without a verified exact descriptor identity are excluded. The unrelated sweet-potato candidate DOI `10.3390/horticulturae10010018` is explicitly logged inaccessible because the publisher’s full table is blocked; no search-preview value was used.
- **Lineage:** Batch 013 757 rows/26 DOI families (SHA-256 `3203ac3eb0ac24cf7a74c52f20dfddc70a1fc70523cdb2a1b799f4ce32caac8f`) → Batch 015 796 rows/27 DOI families. `validate_batch_015.py` proves full parent preservation, unique IDs, target equality, stated fresh-weight basis, DOI count and fail-closed Stage-C status.
- **Decision:** 204 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 016 (2026-11-10)

- **Admission:** Pellegrini et al. (2010), DOI `10.1021/jf904306r`, Tables 2, 3, 5 and 6 plus Cooking Treatments, supplies 32 direct individual HPLC-DAD pairs for lutein and beta-carotene in fresh and frozen broccoli and Brussels sprouts. The source records boiling, 300-W no-water microwave, basket steaming and 100 °C oven steaming, with food-specific treatment durations.
- **Scope safeguards:** table footnotes explicitly state dry-weight means ± SD (`n=3`) and pure-standard identity. Each condition mean remains one row. Only exact pre-existing individual carotenoid identities are admitted; other endpoints, aggregates and unreviewed identities are excluded.
- **Lineage:** Batch 015 796 rows/27 DOI families (SHA-256 `29c39f9700c3dd72c95f414137ef07634eb9d122a042bb8170bdf009ac86756a`) → Batch 016 828 rows/28 DOI families. `validate_batch_016.py` confirms full parent preservation, unique IDs, target equality, stated dry-weight basis, source count, and the fail-closed Stage-C status.
- **Decision:** 172 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Candidate adjudication — pumpkin carotenoid study (2026-11-10)

- **Source reviewed and excluded:** Bergantin et al. (2018), DOI `10.3390/molecules23112791`, has a directly accessible primary PDF, traceable HPLC-UV/Vis-APCI-MS/MS methods, explicit 20-minute oven (200 °C) and steam (100 °C) protocols, and raw/cooked lutein and beta-carotene values. It is not admitted because Table 2 labels the raw concentrations as μg/g fresh matter, while Table 3 supplies the cooked concentrations on dry-matter basis. The paper does not report a numeric conversion adequate to put the paired observations on a common basis.
- **Decision:** Candidate and exclusion ledgers now record the basis mismatch. No observations, model outputs, Stage B/C/D files, Git, commit, push, or remote state were changed by this adjudication.

## Dataset expansion sprint — controlled batch 018 (2026-11-10)

- **Admission:** Fratianni et al. (2024), DOI `10.3390/foods13030472`, Tables 2–3 and Methods §2.2, supplies 30 raw/cooked individual pairs in five leafy matrices: *Sonchus oleraceus*, *S. asper*, spinach, chicory and chard. Results are directly reported as mg/100 g fresh weight. The retained identities are lutein, beta-carotene and gamma-tocopherol under boiling and steaming.
- **Scope safeguards:** Methods specify 100 g leaf portions, 10-minute boiling in 1 L water (1:10) or 10-minute rack steaming over boiling water. Each of the source's three treatment repetitions is represented by one reported mean with SD, never expanded. Isomers, molecules without exact established identities, minerals and aggregate endpoints are excluded.
- **Lineage:** Batch 016 828 rows/28 DOI families (SHA-256 `b7f4be81111a423df0c09bba46bce15eeda302c84f57ab784ffafbc15c311a2a`) → Batch 018 858 rows/29 DOI families. `validate_batch_018.py` proves parent preservation, unique IDs, target equality, stated fresh-weight basis, DOI count and fail-closed Stage-C status.
- **Decision:** 142 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Candidate adjudication — shiitake vitamin study (2026-11-10)

- **Source reviewed and excluded:** Lee et al. (2019), DOI `10.3136/fstr.25.115`, is a fully accessible primary study with documented five-method cooking conditions and numerical vitamin tables. Its Table 3 reports concentration as CW (cooked weight), including its raw/cooked comparison framework, rather than a stated common basis suitable for the current apparent-concentration target. The true-retention outputs do not substitute for paired compatible concentrations.
- **Decision:** Candidate and exclusion ledgers record the basis mismatch. No observations, model outputs, Stage B/C/D files, Git, commit, push, or remote state changed.

## Dataset expansion sprint — controlled batch 019 (2026-11-10)

- **Admission:** Miglio et al. (2008), DOI `10.1021/jf072304b`, Tables 2, 4 and 5 plus Cooking Treatments, supplies 56 individual raw/cooked pairs across carrot, courgette and broccoli. All retained values are explicitly mg/100 g dry weight. The retained identities are lutein, beta-carotene, chlorogenic/caffeic/p-coumaric/sinapic/ferulic acids, quercetin, kaempferol and Vitamin C.
- **Scope safeguards:** The source documents 1:5 boiling-water, atmospheric oven-steaming, and 170 °C peanut-oil frying treatments. It reports optimized vegetable-specific minimum durations without values; no duration was invented. Each published mean ± SD (`n=3`) stays one row. Unregistered or aggregate identities and nondetect cells are excluded.
- **Lineage:** Batch 018 858 rows/29 DOI families (SHA-256 `7676a64b043791c13419faa6690e0e27acb177678836a3d32984441ea0834f74`) → Batch 019 914 rows/30 DOI families. `validate_batch_019.py` confirms full parent preservation, unique IDs, target equality, stated dry-weight basis, DOI count, and the fail-closed Stage-C status.
- **Decision:** 86 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Candidate adjudication — carrot nutrient study (2026-11-10)

- **Source reviewed and excluded:** Lee and Chung (2020), DOI `10.11002/kjfp.2020.27.3.311`, provides a direct primary numerical carrot vitamin table and documented cooking categories, but labels its concentrations merely as mg/100 g without specifying fresh or dry basis. No basis was inferred.
- **Decision:** Candidate and exclusion ledgers record the basis omission. No observations, model outputs, Stage B/C/D files, Git, commit, push, or remote state changed.

## Dataset expansion sprint — controlled batch 020 (2026-11-11)

- **Admission:** Murador, Mercadante and de Rosso (2016), DOI `10.1016/j.foodchem.2015.10.037`, author-deposited thesis Chapter 3, Tables 1 and 4, adds 24 primary raw/cooked pairs in kale and red cabbage. The retained individual analytes are all-trans lutein, all-trans beta-carotene, 9-cis-beta-carotene, and Vitamin C, under boiling, steaming and stir-frying. The source's methods specify 1:5 covered-pot boiling for 4 minutes, food-specific steaming (5 or 15 minutes), and 4-minute soybean-oil stir-frying, with endpoint temperatures.
- **Scope safeguards:** The authors explicitly calculate the tables relative to raw vegetable mass to eliminate moisture gain/loss confounding; this is retained as a common raw-sample reference basis, not relabelled as FW or DW. Each published triplicate mean ± SD remains one condition row. One-sample detections, non-detects, total carotenoids/anthocyanins/phenolics, antioxidant assays and ambiguous mixture/identity rows are excluded. The 9-cis beta-carotene identity remains separate from all-trans beta-carotene; it is not treated as an aggregate beta-carotene measurement.
- **Lineage:** Batch 019 914 rows/30 DOI families (SHA-256 `ba6b83225f02a2a6b6a790f736ce8e4102416a7492372a711103d5d18a43f390`) → Batch 020 938 rows/31 DOI families (SHA-256 `31c2059e3f90f8733461e7ba263856ee2b86a5da24537fdf035ee3648d95cb0d`). `validate_batch_020.py` proves full parent preservation, unique IDs, target equality, common-basis labelling, DOI count and fail-closed Stage-C status.
- **Decision:** 62 observations remain. No model was retrained and no Stage B/C/D, Git, commit, push, or remote state was changed. Continue independent primary-table acquisition.

## Dataset expansion sprint — controlled batch 021 (2026-11-11)

- **Admission:** Buratti et al. (2020), DOI `10.3390/foods9050607`, Methods §2.2 and Tables 2–3, adds 78 direct primary-table raw/cooked pairs. The retained individual HPLC analytes are beta-carotene in carrots and orange-fleshed sweet potatoes plus alpha-carotene in carrots, under boiling, electric steaming and 500-W microwave cooking. All values are explicitly stated as mg/100 g dry weight.
- **Scope safeguards:** The article states that its two cooking trials occurred on different days specifically to account for raw-material variation. Each trial is therefore retained as a distinct experimental lot; its within-sample triplicate HPLC assays remain one published mean and are never expanded. Values are paired only against their corresponding method/trial raw row. Aggregate total-phenolic and antioxidant assays, non-detects, and cauliflower ascorbate whose usable baseline is post-blanching are excluded.
- **Lineage:** Batch 020 938 rows/31 DOI families (SHA-256 `31c2059e3f90f8733461e7ba263856ee2b86a5da24537fdf035ee3648d95cb0d`) → Batch 021 1,016 rows/32 DOI families (SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`). `validate_batch_021.py` proves full parent preservation, unique IDs, stated dry-weight basis, target equality, individual-compound scope, source count and technical-replicate restraint.
- **Decision:** The 1,000-observation acquisition threshold is met. No scientific readiness conclusion follows from count alone: complete compatibility, diversity, source-dominance, duplicate-leakage and fold-safe evaluation are required next. No Stage B/C/D, Git, commit, push, or remote state was changed.

## Post-1,000 compatibility and model evaluation — Batch 021 (2026-11-11)

- **Validation:** The completed Batch-021 master has 1,016 rows, 32 DOI families, 51 compounds, 66 food matrices and 41 normalized cooking-method labels. All 78 newly admitted rows are unique, positive raw/cooked direct-table pairs and formula-exact. The full master has no exact duplicate experimental keys, no aggregate/assay compound rows, and no recomputation deviation above 0.01 percentage points. Two legacy Vitamin-C rows with cooked concentration zero are reported rather than altered; they predate Batch 021.
- **Coverage and replication:** The largest single DOI contributes 84 rows (8.27%); the three largest contribute 246 rows (24.21%). Strict cross-source replication—same analyte, matrix, normalized method, time and measurement basis—remains zero, so numerical expansion did not resolve source-transfer evidence gaps.
- **Fold-safe models:** The independent package contains 294 fold-metric rows and 21,336 OOF-prediction rows across dummy, ridge, Random Forest, Extra Trees, Gradient Boosting, RBF-SVR and XGBoost. Source-family LOSO remains negative for every model. XGBoost has the least-negative source R² (−0.0123; MAE 131.80); RBF-SVR has the lowest source-LOSO MAE (104.41; R² −0.0320). Neither supports unseen-source prediction. The resource-bounded configurations are explicitly documented and are not hyperparameter-tuned benchmarks.
- **Historical comparison limitation:** The frozen 439-row final-prototype audit also found no defensible source-general model (best source R² was ridge −0.0276; lowest source MAE was Random Forest 51.58). Batch 004 is the 524-row data checkpoint but has no historical model-evaluation artifact, so an exact model-performance comparison to 524 cannot be made without creating a new retrospective run; its preserved data-count/source-family comparison remains documented. The 1,016-row results are not directly numerically comparable to the 439 artifact because the dataset, outlier distribution and fixed resource-bound model settings differ.
- **Decision:** Stage A acquisition is complete, but the model remains experimental and non-deployable; Stage C stays fail-closed. No Stage B/C/D, Git, commit, push or remote state changed.
