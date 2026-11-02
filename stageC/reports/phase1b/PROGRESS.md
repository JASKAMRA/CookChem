# Stage C Phase 1B Progress

- Historical release `Phase1-v1.2.0` remains preserved; no new release was created. The official USDA SR Legacy April 2018 CSV archive was downloaded and caffeine FDC 171890 / NDB 14209 was verified against the component tables; API provenance remains separately identified.
- Batches 010–015 each screened 25 distinct Stage B targets against primary-source panels (150 batch-specific outcomes total). Batches 010–015 contributed 85 quantitative food records. Batch 015 added eight raw common-bean records spanning eight analytes and newly covered one Stage B compound.
- Active dataset before current acquisition batches: 99 accepted food-composition records and 99 mappings, covering 39/119 compounds; 80 have no accepted quantitative measurement. Validation reports 19 identity-review entries.
- Batches 019–021 prepared 14 primary-study candidate rows for oleuropein (7 freeze-dried Kolovi olive samples), thymoquinone (6 commercial black seed oils), and cinnamaldehyde (one Korintje cinnamon sample with an isomer-review flag). Batch 023 adds two official USDA SR28 candidates: phylloquinone in raw spinach (exact analyte name) and total ascorbic acid (held for target-scope review). Batch 024 adds 50 primary-study candidates: 25 dried citrus-peel samples each for nobiletin and tangeretin, quantified separately by HPLC against named standards. Batch 025 adds two raw-spinach candidates with separate lutein and zeaxanthin values (n=7) from a controlled feeding study. Batch 026 adds two separate beta-cryptoxanthin database candidates (raw orange and papaya). Batch 027 adds 10 sample-level curcumin candidates from commercial turmeric powders measured by validated HPLC. Batch 028 screens barberry berberine fruit sources; only aggregate ranges are accessible and mass basis is unresolved, so no point rows were invented. Batch 029 adds two sulforaphane broccoli candidates from a primary study, explicitly held for analytical-hydrolysis exposure-basis review. Batch 030 adds four apple-peel candidates for ursolic and oleanolic acids at documented rootstock-specific extrema, retaining lyophilizate basis. These candidates have not changed accepted coverage; the tally stays at 39/119 until the release gate permits ingestion.
- Search log at the latest checkpoint: 391 source/compound events, spanning all 119 Stage B IDs. Candidate/source-screen batch CSVs contain 618 records across 52 files through Batch 077; 33 records from earlier source batches have now been promoted. These candidate-only totals are kept separate from accepted measurements. Candidate records remain subject to source/mapping review and gated ingestion. This establishes logged screening coverage, not exhaustive literature absence.
- Food evidence covers berries, citrus, fresh fruit/vegetables/spices, culinary and native herbs, native Australian fruits/spices, and Portuguese common beans. Semi-quantitative panels and dry/fresh bases remain explicitly flagged.
- Exact stereochemistry, positional isomers, glycosides/aglycones, free/bound fractions, and units/bases were not conflated. Batch 014 heatmap-only findings and Batch 015 generic stereoisomer values were not ingested. Paired cooked-bean values are held out of Phase 1B.
- No new exposure estimates were calculated; study-specific dried ingredients/raw-seed dry-weight measurements lack compatible individual as-consumed serving inputs.
- Pre-promotion validation PASS for 99 records is historical; current validation is recorded in `stageC/reports/validation/phase1_validation.json`. Details in `CLEAN_COPY_VALIDATION.json`.
- Historical integrity reports are point-in-time only. StageB_Final was reconciled on 2026-11-02; see `STAGEB_RELEASE_RECONCILIATION_2026-11-02.md`.

- Current ingestion gate: the connector fails on eight allowlisted Stage B files; an independent read-only comparison found 661/708 manifest paths mismatched and zero missing. Candidate ingestion and mapping rebuild are paused pending release-owner reconciliation. No Stage B files or manifests were edited and no gate was bypassed. See `STAGEB_CHECKSUM_GATE_STATUS_2026-11-02.md`.
- Candidate details: `batches/batch_019_oleuropein_kolovi_olives/`, `batches/batch_020_thymoquinone_black_seed_oils/`, `batches/batch_021_cinnamaldehyde_korintje_cinnamon/`, `batches/batch_022_eugenol_clove_buds/` (range-only and bibliographic discrepancy), `batches/batch_023_usda_sr28_spinach_vitamins/`, `batches/batch_024_citrus_peel_nobiletin_tangeretin/`, `batches/batch_025_spinach_lutein_zeaxanthin/`, `batches/batch_026_beta_cryptoxanthin_usda_ncc/`, `batches/batch_027_curcumin_commercial_turmeric_powders/`, `batches/batch_028_berberine_barberry_fruit_range/`, `batches/batch_029_sulforaphane_broccoli_hydrolysis_basis/`, `batches/batch_030_apple_peel_ursolic_oleanolic_acids/`, `batches/batch_031_usda_edamame_isoflavones/`, and `batches/batch_032_chrysin_greek_honey_matrices/`, `batches/batch_033_greek_honey_flavonoid_medians/`, `batches/batch_034_clementine_juice_naringin_neohesperidin/`, `batches/batch_035_danish_licorice_glycyrrhizin_foods/`, and `batches/batch_036_pterostilbene_vaccinium_range_only/`, and `batches/batch_037_phytosterols_oils_nuts/`, and `batches/batch_038_germinated_soy_isoflavones/`, and `batches/batch_039_salmon_astaxanthin_canthaxanthin/`; outcomes are logged in `SEARCH_LOG.csv` and `coverage_gap_register.csv`.


## 2026-11-02 continuation — batch 031

Prepared two USDA database candidates for daidzein and genistein in raw green soybeans (NDB 11450). Values are Release 2.0 database means (20.34 and 22.57 mg/100 g edible portion; n=35), converted to mg/kg in candidate rows. Release 2.0 is superseded by R2.1, so candidates are held for version reconciliation and Stage B ID mapping. They do not increase accepted coverage.


## 2026-11-02 continuation — batch 032

Prepared five targeted chrysin candidate summaries across Greek blossom, fir, oak, pine and thyme honeys. The source provides group medians and sample counts, not per-honey observations; candidate rows preserve that distinction. These remain pending Stage B structure review and checksum gate and do not change accepted coverage.


## 2026-11-02 continuation — batch 033

Added 13 targeted honey-matrix median candidates for genistein, galangin and pinocembrin from the primary Greek honey LC-HRMS study. Below-LOD cells were omitted; group summaries were not expanded into fictitious sample rows. Candidates await mapping review and checksum-gated ingestion.


## 2026-11-02 continuation — batch 034

Prepared six exact-analyte clementine-juice candidates for naringin and neohesperidin, quantified against selected standards by HPLC-DAD in three Calabria juice samples. Retained the source mg/100 mL basis and n=3 analytical-replicate caveat; did not convert to food mass basis. Candidates await mapping review and the Stage B gate.


## 2026-11-02 continuation — batch 035

Prepared four category-level glycyrrhizinic-acid summary candidates for Danish licorice confectionery, ice cream and brewed tea. Kept food mass and beverage volume units distinct; records are pending the Stage B glycyrrhizin/acid-form identity review and checksum gate.


## 2026-11-02 continuation — batch 036

Screened two primary Vaccinium pterostilbene studies. Both confirm berry occurrence but accessible records provide only distinct study-level ranges; no individual measurements were inferred. Added a range-only note and follow-up to retrieve cultivar-level tables.


## 2026-11-02 continuation — batch 037

Prepared 35 phytosterol candidates across edible oils and nuts/seeds: β-sitosterol in 14 oils and seven nut/seed samples, plus stigmasterol in 14 oils. Exact-analyte LC-MS-MS and HPLC-DAD data were transcribed; co-eluting stigmasterol+campesterol values in the nut study were excluded from stigmasterol. Product-level and technical replicate limits remain explicit.


## 2026-11-02 continuation — batch 038

Prepared 90 exact-analyte soybean candidates from 18 germination conditions for daidzin, genistin, glycitein, daidzein and genistein. Table 4 mean ± SD values were converted from nmol/g to mg/kg using each target molecular weight; dried-sample basis and yield-correction denominator are flagged for review. Candidates are pending mapping and checksum-gated ingestion.


## 2026-11-02 continuation — batch 039

Prepared two provisional salmon-muscle candidate rows from the primary 1998 farmed Atlantic salmon cohort: astaxanthin 5.5 ± 1.1 mg/kg and canthaxanthin 0.200 ± 0.047 mg/kg, n=145. Accessible publisher abstract only; analytical method, edible-state/moisture basis, feed context and carotenoid isomer resolution require full-text review. Both remain pending and do not change accepted coverage. Search log now has 326 events across all 119 targets; candidate CSVs total 278 rows in 23 batches.


## 2026-11-02 continuation — batch 040

Prepared 14 exact-analyte coumestrol candidates from Ohta et al. (2021): six supermarket vegetables (Fig. 3) plus four commercial soybean-sprout products under uncultivated and 24°C/one-day controlled cultivation (Table 3). Means ± SD, n=3; original µg/g dry-material values are recorded as equivalent mg/kg dry material without moisture conversion. HPLC/standard identity and method validation are reported in the paper. These remain pending Stage B identity review and dry-basis admissibility; no ingestion or coverage increase. Candidate data now total 270 rows in 21 batches, with 327 search events across all 119 target IDs.


## 2026-11-02 continuation — batch 041

Prepared three exact-standard hesperidin candidates from Table 6 of the clementine juice HPLC-DAD study also screened in batch 034. Values are 81.08 ± 4.94, 40.06 ± 3.04 and 65.30 ± 3.54 mg/100 mL for three Calabria juice samples (n=3 analytical replicates). The reported mg/100 mL basis is retained; normalized values are mg/L (×10), with no density assumption. These remain pending exact Stage B mapping and checksum-gated ingestion. Current screening tally: 273 candidate records in 22 candidate batch CSVs, and 328 search events covering all 119 target IDs.


## 2026-11-02 continuation — batch 042

Prepared five vanillin candidates from Table 1 of Neves et al. (2026) for Ugandan vanilla pod batches 10, 14, 15, 23 and 26. Actual HPLC reference means were 11.44, 6.90, 35.73, 5.56 and 12.65 mg/g original sample, respectively; values were converted to mg/kg original sample without moisture correction. Each reference is a three-pod composite with triplicate injections. The paper's summary ranges conflict, so only explicitly tabulated values were prepared. Candidates remain pending source/state and mapping review plus the Stage B checksum gate. Screening tally: 278 candidate records in 23 CSV batches and 329 search events across all 119 target IDs.


## 2026-11-02 continuation — batch 043

Prepared 13 candidate fisetin records for Canadian prairie small fruits from Kodikara et al. (2025), Tables 2a/2b: exact analyte row, mean ± SD, mg/kg dry weight, n=3 reported. Fourteenth tested matrix (chokeberry) was <LOD and was not converted to zero. Methods describe one composite sample per fruit species; replicate independence and fisetin-specific standard/calibration details remain flagged for review. Candidates await exact mapping/method review and checksum-gated ingestion; accepted coverage remains 39/119. Current tally: 291 candidate rows in 24 batch CSVs and 330 search events across all 119 target IDs.


## 2026-11-02 continuation — batch 044

Prepared 40 exact-analyte candidate measurements from Kodikara et al. (2025), Tables 2a/2b: Ellagic acid (4), Daidzein (3), Daidzin (14), Genistein (5), Glycitein (14). Exact-stage names and mg/kg dry-weight values are retained; NF, <LOQ and <LOD were omitted. One fruit composite per species and the table's n=3 replicate meaning, analyte-specific standards, and dry-basis eligibility need review. All records remain candidates; accepted coverage remains 39/119 behind the Stage B checksum gate. Current tally: 331 candidate rows across 25 candidate CSV batches and 335 search events across all 119 target IDs.


## 2026-11-02 continuation — batch 045

Prepared 21 Herbacetin and Isoquercetin candidate measurements from Kodikara et al. (2025), Tables 2a/2b. Exact-name numeric entries are preserved in mg/kg dry weight; NF/<LOQ values omitted. Isoquercetin remains distinct from quercetin-3-galactoside, with isomer-specific standard review flagged. Standard identity, n=3 independence and dry-basis eligibility need review. Candidates do not change accepted coverage (39/119) pending the Stage B checksum gate. Current tally: 352 candidate records across 26 candidate CSVs and 337 search events across all 119 target IDs.


## 2026-11-02 continuation — batch 046

Prepared 27 exact stereospecific candidate measurements from Kodikara et al. (2025): (−)-Epicatechin gallate (14) and (−)-Epigallocatechin (13) across Canadian small-fruit matrices, mg/kg dry weight. One NF entry was omitted. Standard identity, stereospecific calibration, n=3 replicate independence and dry-basis eligibility need review. Accepted coverage remains 39/119 pending review and the Stage B checksum gate. Current tally: 379 candidate records across 27 candidate CSVs and 339 search events across all 119 target IDs.


## 2026-11-02 continuation — batch 047

Prepared three USDA Flavonoid Database Release 3.3 candidates in raw strawberries (NDB 09316): (+)-Gallocatechin, (−)-Epigallocatechin and (−)-Epicatechin 3-gallate; USDA means, SEs, ranges and N values retained and converted from mg/100 g to mg/kg. These are aggregate values pending exact mapping and checksum-gated ingestion. Accepted coverage remains 39/119. Current tally: 382 candidate records across 28 candidate CSVs and 342 search events across all 119 target IDs.


## 2026-11-02 continuation — batch 048

Prepared five grapefruit furanocoumarin candidates: epoxybergamottin and bergamottin in peeled grapefruit flesh and commercial grapefruit juice from Melough et al. (2017), Table 4 (n=3 per food), plus Paradisin C in 12 grapefruit juice preparations from Hanley et al. (2013), Table 3. The Melough mass-based ng/g values are normalized to mg/kg; the Hanley µg/mL basis is retained as mg/L without density conversion. Paradisin C method and sample provenance remain flagged. Candidates do not change accepted coverage; checksum gate remains active. Current tally: 387 candidate rows across 29 candidate CSVs and 345 search events across all 119 targets.


## 2026-11-02 continuation — batch 049

Prepared one exact Paradisin A candidate for freshly prepared Ray Red grapefruit juice from Girennavar et al. (2008): 0.059 ± 0.001 µg/mL (0.059 mg/L), with Figure 4 identifying mean ± SD over 15 samples. Full-text HPLC-PDA method, standard-spiking identity confirmation, calibration and sample preparation were reviewed. This cultivar/site/harvest-specific volume-basis candidate does not change accepted coverage; source and exact dimer mapping remain pending the Stage B checksum gate.


## 2026-11-02 continuation — batch 050

Prepared one exact hesperetin-aglycone candidate for not-from-concentrate orange juice: 7 ± 0.7 mg/kg, reported separately from hesperidin at 315 ± 25.3 mg/kg. The primary study says less than 3% of flavanones occurred as aglycones. HPLC/LC-PDA/ESI-MS instrumentation and purchased analyte standards are reported, but exact juice quantification workflow and batch/sample semantics need review. Candidate does not change accepted coverage and remains behind the Stage B checksum gate.


## 2026-11-02 continuation — batch 051

Prepared five exact-standard Hyperoside values for anonymized 100% apple juice products PAJ1–PAJ5 (0.012–0.1399 mg/L). PAJ6 and PAJ7 were reported as ND and remain nonnumeric; no zeros were imputed. The primary UPLC-MS/MS study's exact standard, method, Table 3, juice-volume units and retail sampling notes were checked. Product replicate dispersion remains unclear, and the candidates do not change accepted coverage pending review and the Stage B checksum gate.


## 2026-11-02 continuation — batch 052

Screened phloretin in a primary four-cultivar apple-tree study. The paper reports aglycone phloretin in dried leaves (maximum 2.8 ± 1.4 mg/g DW), but not in whole fruit, bark or twigs. Leaf material is not established as ordinary food in this source, so no candidate record was added. The screening note records the matrix/basis reason and preserves the apple-fruit ND as distinct from zero.


## 2026-11-02 continuation — batch 053

Screened baicalin, baicalein and wogonin in four commercial *Scutellaria baicalensis* root tinctures from a validated primary HPLC-UV study. Individual product values and triplicate statistics were transcribed to the screening note, but these are medicinal botanical tinctures; Phase 1B screening rule 6 excludes them from verified food mappings. No candidate food records were added.

## 2026-11-02 continuation — batch 054

Prepared two Puerarin candidates from a primary food-company supplied *Pueraria lobata* root study: 72.07 g/kg dry weight at 1-year growth and 20.90 g/kg at 5 years. Only the textual endpoints were extracted; intermediate figure values were not estimated. Candidate remains pending food-ingredient scope and replicate review, plus the checksum gate.


## 2026-11-02 continuation — batch 055

Prepared 18 separate thyme-spice candidates for carvacrol and thymol from nine commercial *Thymus vulgaris* lots measured by sample-specific MHS-SPME-GC-MS with authentic standards (Sgorbini et al., 2015). Table 2 reports concentrations in mg/g on the solid herb matrix. Values were normalized arithmetically to mg/kg without conflating the two positional isomers. The source does not explicitly state moisture/drying basis, so candidates remain held and do not change accepted coverage.


## 2026-11-02 continuation — batch 056

Prepared ten eugenol candidates from separative MHS-SPME-GC-MS measurements of ten commercial clove lots in the same primary study used for Batch 055. This provides sample-level values beyond Batch 022’s separate range-only source. Values remain held because the commercial lots’ drying/moisture basis is unspecified; accepted coverage remains 39/119.


## 2026-11-02 continuation — batch 057

Located and prepared 22 exact phloretin aglycone candidates from 11 apple cultivars, with peel and flesh stored separately. Unlike the earlier limited apple study that found phloretin ND in whole apples, this primary HPLC-DAD-MS/MS study reports cultivar-specific means±SD in µg/g fresh weight, uses an authentic phloretin standard and distinguishes phloridzin. Fresh-weight values are explicit; n=4 biological-versus-technical replication remains for review. Accepted coverage remains 39/119 pending review and the Stage B checksum gate.


## 2026-11-02 continuation — batch 058

Screened a primary bilberry pterostilbene paper reporting six sample-level values, but its 1.274–2.162 mg/g dry-weight scale conflicts by roughly three orders of magnitude with other primary Vaccinium reports, and the accessible method lacks pterostilbene-specific standard/calibration detail. No candidates were prepared; the unresolved unit/identity discrepancy is logged for source clarification.


## 2026-11-02 continuation — batch 060

Prepared 16 purple-garlic sample-level candidates for diallyl sulfide (8 positive Table 2 cells), diallyl disulfide (6), and diallyl trisulfide (2). Values are means ± SD from triplicate biological garlic samples, reported in µg/g and normalized to mg/kg fresh garlic. The source uses a 2-octanol internal-standard area/mass ratio and NIST 14 library identity matches >60%, without compound-specific authentic standards or response calibration; candidates are held for analytical review and the Stage B checksum gate. ND cells were omitted. Accepted coverage remains 39/119; search log now has 364 events across all 119 targets, with 462 candidate rows in 37 CSVs.


## 2026-11-02 continuation — batch 061

Prepared three raw-garlic paste candidates for allicin, diallyl disulfide and diallyl trisulfide from a primary HPLC study with compound reference standards, reporting 5.59 ± 0.26, 0.14 ± 0.01 and 0.22 ± 0.02 mg/g dry weight. Converted to mg/kg DW. The source paste included added water (100 g cloves + 50 mL water); dry-weight denominator linkage and triplicate biological independence need review. No accepted coverage increase; total candidate rows 465 in 38 CSVs, and search log 367 events over all 119 targets.


## 2026-11-02 continuation — batch 062

Recorded one NIST-certified curcumin candidate for ground turmeric SRM 3299: 12.17 ± 0.56 mg/g dry mass (12,170 mg/kg). NIST specifies a 95% expanded uncertainty and describes LC-absorbance plus collaborating-laboratory LC methods. The SRM is explicitly for research use and not human consumption, and it is irradiated; therefore the candidate is held and excluded from edible exposure mappings. Accepted coverage remains 39/119.


## 2026-11-02 continuation — batch 063

Prepared two sample-specific berberine candidates from a primary *Berberis vulgaris* fruit HPTLC study: wild-collected freeze-dried fruit, 5.46 mg/100 g, and online-purchased dried fruit, 1 mg/100 g. Converted to 54.6 and 10 mg/kg on the same dried-fruit basis; no fresh-weight conversion or unreported SD was inferred. HPTLC identity relies on Rf matching to berberine sulfate, so cation-versus-sulfate mass expression and food provenance remain review flags. A separate 2018 edible-berry study reports concentration in an ethanolic extract and was not treated as fruit composition. No accepted coverage change; Stage B checksum gate persists.


## 2026-11-02 continuation — batch 064

Prepared four exact-standard naringin candidates from a validated UPLC-PDA grapefruit-juice study: Juice A (412 ± 15 µmol/L), concentrate C (1182 ± 16), Florida’s Natural Ruby Red D (371 ± 15), and Simply Grapefruit E (381 ± 15). Converted to 239.178, 686.186, 215.377 and 221.182 mg/L original juice using MW 580.53 g/mol. Juice B, a solvent/resin-treated furanocoumarin-free derivative, was excluded. Although standard identity, original-juice basis and method validation are explicit, the authors note UPLC flavonoid values were approximately twice prior HPLC values and leave the difference unexplained; candidates remain held for method-comparability review. No accepted coverage increase; checksum gate persists.


## 2026-11-02 continuation — Batch 065

Prepared 48 strawberry free-ellagic-acid candidates from Atkinson et al. (2006), Tables 1–2 (33 cultivar values in year 1; 15 in year 2). Exact free EA was measured without acid hydrolysis and quantified against ellagic acid dehydrate. Kept the source’s µg/g frozen-weight basis (same numerical value in mg/kg frozen weight); omitted ND (not determined). Cultivar samples pooled fruit collected across six plants, but tables provide no SD or assay replicate count. The records are held for statistical representation and basis review; no accepted coverage increase. At this checkpoint: 520 candidate rows in 42 CSVs and 371 search events across all 119 targets; accepted coverage remains 99 records mapping to 39/119 compounds.


## 2026-11-02 continuation — Batch 066

Screened Mesimeri et al. (2024) for phenethyl isothiocyanate. Table 1 reports PEITC in broccoli florets (infected and noninfected) at 5.3 ± 0.06 and 5.6 ± 0.14 µg/g DW, respectively. I did not prepare candidate rows because Stage B marks this target identity as source-transcribed pending independent parser/adjudication, and rule 6 excludes identity-pending compounds. Sample replication and native-versus-handling-generated ITC interpretation also need review. This is a source lead only; accepted coverage remains 99 records mapping to 39/119 compounds. Search log then contained 372 events across all 119 targets.


## 2026-11-02 continuation — USDA spinach vitamin C method adjudication

Followed the held USDA SR28 spinach Vitamin C candidate into USDA SR documentation and method references. Nutrient 401 is total ascorbic acid; the documented AOAC 967.22 microfluorometric method quantifies total vitamin-C-active forms after oxidation, including dehydroascorbic acid. The individual SR28 entry has no linked source method, so applicability is indirect; retain 28.1 mg/100 g as an unmapped candidate and do not treat it as exact reduced ascorbic acid. No candidate-row or accepted-coverage count increase. Search log now contains 373 events across all 119 targets.


## 2026-11-02 continuation — Batch 067

Verified the full text and Table 5 of Sabbioni et al. (2006), a validated HPLC study of 18β-glycyrrhetic acid in commercial licorice confectionery and roots. Positive confectionery results are 0.13%, 0.04%, and 0.03% w/w; one root sample is 0.25% w/w. Tabulated n.d. results are left nonnumeric. Although a suitable food source and exact reported analyte are now verified, Stage B identity remains parser/adjudication pending, so no candidate rows were allowed under Phase 1B rule 6. The exact values are documented in the source-screening note; accepted coverage does not change. Search log now has 374 events across all 119 targets.


## 2026-11-02 continuation — Batch 068

Prepared two exact-standard rutin candidates from a primary HPLC-DAD caper study: raw capers 175.9 ± 3.9 mg/100 g sample and pickled capers 117.5 ± 15.1 mg/100 g sample, both before in vitro digestion. Converted units to 1,759 ± 39 and 1,175 ± 151 mg/kg as-analyzed sample without inferring dry/fresh basis. The paper reports analyte-specific rutin standard/calibration and caper moisture, but Table 3 does not state n/replicate unit or explicitly label the concentration denominator fresh/dry. Hold both candidates for these reviews and the Stage B checksum gate; accepted coverage remains 99 records/39 compounds. Current tally: 522 candidate rows in 43 files; 377 search events.


## 2026-11-02 continuation — Batch 018 sesame-seed mapping review

Reconciled the existing Kim et al. sesame-seed aggregate candidate to exact Stage B sesamin ID `CHEM-PUBCHEM-72307` (complete identity audit) and populated its PubChem CID/InChIKey. Confirmed authentic sesamin standard, HPLC-DAD, mean 3816.7 ± 1414.2 mg/kg, range 1568.4–7746.8, n=21 across eight countries. Kept the candidate held because roast/processing state and moisture basis are not specified. No candidate row count or accepted coverage increase. Search log now has 376 events across all 119 targets.


## 2026-11-02 continuation — Batch 017 folic-acid exact mapping

Mapped the 12 existing Phillips et al. ready-to-eat cereal folic-acid candidates to the complete exact Stage B identity. The paper separately measured folic acid by validated LC-MS with a 13C-folic acid internal standard; each product has four regional composites, each pooling three locations. Values are as-sold µg/100 g and preserve mean, SE, RSD and range. Product labels remain anonymized A–L and the study sampled in 2006. Exact mapping is ready; ingestion remains gated by the Stage B checksum failure. Candidate row count is unchanged; no accepted coverage increase. Search log now contains 377 events across all 119 targets.


- Mapping reconciliation: seven Batch 019 oleuropein rows, six Batch 020 thymoquinone rows, and the exact phylloquinone row in Batch 023 now carry Stage B compound IDs, PubChem CIDs, InChIKeys, and explicit exact-mapping review metadata. Batch 023 total ascorbic acid remains intentionally unmapped pending target-scope resolution. These are candidate-only metadata updates: accepted coverage remains 99 records / 39 compounds because the Stage B checksum gate is still unresolved. Thymoquinone oil sample 6 is flagged for additive/food-eligibility review.


- Batch 069 prepared 44 exact-standard isorhamnetin food/season candidates from Cao et al. 2010 Table 2 (Harbin retail food composites; mg/kg FW, mean ± SD, n=3 as reported). Acid hydrolysis converts glycosides to aglycones, so candidates are explicitly held from native free-isorhamnetin coverage. Accepted coverage remains 99 records / 39 compounds; no Stage B or accepted dataset edits were made.


- Batch 070 prepared 10 exact-standard gentisic-acid candidates from Di Stefano et al. 2017 Table 2: green/ripe avocado pulp, 0.24–4.24 mg/kg fresh sample. Direct methanolic extraction, with no hydrolysis reported. Candidates remain held because Table 2 does not report SD or clarify biological versus independent-extract replicate allocation. Accepted coverage remains 99 records / 39 compounds.


- Batch 071 recovered three exact cultivar-level pterostilbene values from the table in an edible-berries review, which cites Rimando and Cody (2005): Tifblue 0.151, Climax 0.099, and deerberry selection SHF3A-2-108 0.520 µg/g DW. Values remain held because primary table, n and calibration are not directly confirmed; no fresh-weight conversion or accepted coverage change.


- Batch 071 source audit: accessed the authors’ LCGC article and verified sample species, whole/lyophilized berry preparation, GC–MS/SIM, synthetic pterostilbene external standard, LOD 18 ng/g and LOQ 61 ng/g DW, and the 99–520 ng/g species-level range. Corrected a DOI error: jf040095e is not the 2005 LCGC article. Exact cultivar values still come from the review table because original Table III numeric cells were not directly readable; rows remain held.


- Batch 072 prepared six source-verified syringic-acid conjugated/bound fraction candidates in green soy bean. Rows retain fresh-weight basis, regional sampling and biological n=3; kept held because values are hydrolysis-released fractions.


- Batch 073 prepared eight HPLC AITC measurements from commercial mustard, preserving as-sold fresh-weight basis and the analytical-replicate limitation.


- Batch 074 prepared three semi-quantified tectochrysin honey candidates for blossom, oak and pine categories; chrysin calibration surrogate is explicit and all rows remain held.


## 2026-11-02 continuation — Batch 075

Screened nootkatone in grapefruit/pomelo peel using the 2019 citrus extraction review and its cited Ortuño et al. (1995) primary study. The review reproduces immature-fruit sesquiterpene values of 5 ± 0.5 and 0.9 ± 0.4 mg/100 g fresh peel for grapefruit and pomelo. Two candidate rows are held because the review's result cells say “sesquiterpene” and the original Table 2 was not independently inspected to verify the exact analyte/value linkage. Mature-fruit ND was not encoded as zero. Current candidate ledger: 598 rows in 50 CSVs; 389 search events across all 119 IDs. Accepted coverage remains 99 records / 39 compounds.


## 2026-11-02 continuation — Batch 076

Prepared 18 artichoke-head candidate records (nine per target) for 1,3- and 1,5-dicaffeoylquinic acid from Tarantino et al. (2020), Table 3. The exact positional standards are stated; the source reports treatment marginal means ± SE on a dry-matter basis. Amounts use 5-caffeoylquinic acid as the quantitation reference, so the rows remain held for surrogate-calibration review. Experimental wastewater irrigation and marginal-mean groupings are preserved. Current candidate ledger: 618 rows across 51 batch CSVs; 391 search events cover all 119 targets. Accepted coverage remains 99 records / 39 compounds.


## 2026-11-02 — Batch 077 promotion and active validation

After StageB_Final passed 16/16 portable release checks and its manifest was reconciled, Stage C imported a new versioned snapshot. Promoted 33 source-verified food records from existing batches: 12 folic acid, 8 allyl isothiocyanate, 7 oleuropein, 5 thymoquinone and 1 phylloquinone. Excluded thymoquinone oil sample 6 because of added rosemary extract/tocopherols; retained total Vitamin C as held due analyte-scope ambiguity. Active composition is 132 records, mappings 132, and verified coverage 44/119 compounds (36.97%); 75 targets remain uncovered. Stage C validation PASS with zero food, mapping, orphan-ID, or scientific-integrity findings. No exposure estimates were created.


## 2026-11-02 — Batch 078 promotion and active validation

Promoted 10 Curcumin I commercial turmeric-powder records and two USDA/NCC beta-cryptoxanthin aggregate records (orange and papaya). Active food composition now contains 144 records and 144 mappings covering 46/119 compounds (38.66%); 73 targets remain uncovered. Phase 1 validation PASS with zero food, mapping, exposure, orphan-ID, or scientific-integrity findings. Turmeric technical-replicate and as-sold powder limitations, and carotenoid database source-count/confidence limits, remain explicit. No exposure estimates were created.


## 2026-11-02 — Batch 078–079 promotions and active validation

Added 12 records from curcumin and beta-cryptoxanthin screening plus 50 citrus-peel nobiletin/tangeretin values. Active food composition now contains 194 records and mappings covering 48/119 compounds (40.34%); 71 targets remain uncovered. Phase 1 validation PASS with zero food, mapping, orphan-ID, or scientific-integrity findings. Source basis, confidence, and technical-replicate limits remain explicit. No exposure estimates were created.


## 2026-11-02 — Batch 080 promotion and active validation

Promoted 93 source-verified records from existing screened batches; 14 previously uncovered compounds gained accepted quantitative food mappings. Active composition now contains 287 records and mappings covering 62/119 compounds (52.10%); 57 remain uncovered. Phase 1 validation PASS with zero food, mapping, exposure, orphan-ID, or scientific-integrity findings. The Danish licorice tea result reported only per liter remains held because no density-based conversion was made. No exposure estimates were created.


## 2026-11-02 — Batch 081 promotion and active validation

Promoted 124 verified source measurements across 16 newly covered compounds. Active dataset now contains 411 food records and mappings covering 78/119 compounds (65.55%); 41 remain uncovered. Phase 1 validation PASS with zero food, mapping, exposure, orphan-ID, or scientific-integrity findings. Source-specific bases and summary/replicate caveats are retained. Volume-based Paradisin C remains held.


## 2026-11-02 coverage refresh

Rebuilt exact mappings from the active dataset and reran Phase 1 validation: **453 records, 453 mappings, 92/119 compounds covered, 27 uncovered; validation PASS.** Refreshed the coverage gap register and quantitative-record counts in the compound priority register.


## 2026-11-02 coverage refresh

Rebuilt exact mappings from the active dataset and reran Phase 1 validation: **464 records, 464 mappings, 97/119 compounds covered, 22 uncovered; validation PASS.** Refreshed the coverage gap register and quantitative-record counts in the compound priority register.


## 2026-11-02 coverage refresh

Rebuilt exact mappings from the active dataset and reran Phase 1 validation: **464 records, 464 mappings, 97/119 compounds covered, 22 uncovered; validation PASS.** Refreshed the coverage gap register and quantitative-record counts in the compound priority register.


## 2026-11-02 coverage refresh

Rebuilt exact mappings from the active dataset and reran Phase 1 validation: **504 records, 504 mappings, 107/119 compounds covered, 12 uncovered; validation PASS.** Refreshed the coverage gap register and quantitative-record counts in the compound priority register.


## 2026-11-02 coverage refresh

Rebuilt exact mappings from the active dataset and reran Phase 1 validation: **505 records, 505 mappings, 108/119 compounds covered, 11 uncovered; validation PASS.** Refreshed the coverage gap register and quantitative-record counts in the compound priority register.


## 2026-11-02 — Batch 097: syringic acid in cornelian cherry

Added one fresh-weight food measurement from Ciurlă et al. (2025), Table 6: 51.7 ± 0.73 µg/g in mature Cornus mas fruit. The study used an individual authentic syringic-acid standard and compound-specific HPLC-DAD calibration (R²=0.9999). Biological sample count and the mean/SD replication basis are not reported; the extraction uses acidified solvent, so the value remains method-defined extractable content. Exact Stage B CID/InChIKey mapping was verified. Official mapping and Phase 1 validation PASS: 505 records, 505 mappings, 108/119 compounds covered, 11 uncovered; no exposure estimate added.


## 2026-11-02 coverage refresh

Rebuilt exact mappings from the active dataset and reran Phase 1 validation: **511 records, 511 mappings, 109/119 compounds covered, 10 uncovered; validation PASS.** Refreshed the coverage gap register and quantitative-record counts in the compound priority register.


## 2026-11-02 — Batch 098: astaxanthin and Phase 1B final screen

Promoted six HPLC-measured astaxanthin treatment means in Atlantic salmon muscle from Ytrestøyl et al. (2025), Table 4. The paper reports 12°C treatment means per tank ± SEM (N=3); six fish per tank were sampled. The crystalline all-E standard and tissue HPLC method are documented. The paper reports mg/kg muscle without a fresh/dry denominator, retained verbatim; these experimental feeding groups are not retail/population averages and were not used for exposure calculations.

Final targeted screening of all remaining gaps did not locate additional eligible quantitative food measurements. Scutellaria markers (baicalein, baicalin, scutellarein, wogonin, oroxylin A, 7-methoxyflavanone and wogonoside) are tied to medicinal roots/tinctures/herbal products; amentoflavone and irilone leads were supplement/medicinal botanical or clinical-extract measurements; the exact citrus polymethoxyflavone lacked an eligible quantified food result. Those records remain missing rather than inferred. Final active dataset: 511 records / 511 exact mappings; 109/119 targets covered; 10 remain uncovered. Phase 1 validation PASS with no mapping or scientific-integrity errors. Phase 1B screening is closed with documented gaps; see `PHASE1B_COMPLETION_REPORT.md`.


## Batch 099 — final re-review after user follow-up

Rechecked all 10 remaining targets against primary literature and source tables. No additional eligible, independently verifiable quantitative food values were promoted. One secondary monograph gives a red-clover leaf irilone value, but the numeric primary table and statistical meaning could not be independently checked; it remains held. Scutellaria results remain medicinal root/tincture/herbal-tea contexts; the exact citrus PMF still lacks a verified numeric food value. Gap register and search log now record this final review. Phase 1B remains closed with 10 explicit gaps; active data and validation are unchanged at 511 records, 109/119 covered, validation PASS.


## Batch 100 — contextual reconciliation after user follow-up

Completed an additional quantitative-context pass on the final ten. Captured six exact flavonoid values from medicinal *Scutellaria* root studies (including dry-matter HPLC values for baicalein, baicalin, scutellarein, wogonin, wogonoside, and oroxylin A), HPLC amentoflavone values from *Viburnum* leaves/branches, and a secondary red-clover irilone value held for primary-table verification. No exact numeric value was established for 7-methoxyflavanone or the exact pentamethoxyflavone. These are documented separately in `batches/batch_100_contextual_reconciliation/`; none meet ordinary-food inclusion, so official coverage remains 109/119 and Phase 1 validation remains PASS at 511 records/mappings. The final-target screening/reconciliation work is complete, with ten food-coverage gaps retained transparently.


## Phase 1B final audit and release — 2026-11-02

Audited all 100 batch directories, active accepted rows, central candidates, mapping rows, coverage outputs, and current Stage B snapshot. Regenerated mappings from the checksummed 119-target registry; the rebuilt 511-row mapping file matched byte-for-byte. The actual active dataset has 511 positive source-backed records, 511 mappings, zero duplicate IDs, 109/119 ordinary-food compounds, and validation PASS. Full Stage C tests passed 61/61; focused mapping/food/unit/exposure/integration/CLI tests passed 50/50. The clean-copy release suite also passed 61/61 and Phase 1 validation passed with 511 records/mappings. Versioned package: `stageC/releases/Phase1B-v1.0.0/`.

The current Stage A and Stage B archive trees match the Git HEAD; the Stage B connector verifies 710 current release-manifest entries. The old `BASELINE_CHECKSUMS.json` hash list is stale against the current repository and remains preserved as historical evidence. Exact mismatch counts and the current-tree audit are in `PROTECTED_TREE_AUDIT_2026-11-02.json`; no Stage B source/evidence table was edited in final packaging.
