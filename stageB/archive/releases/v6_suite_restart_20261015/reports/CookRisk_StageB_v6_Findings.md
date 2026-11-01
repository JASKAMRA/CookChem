# CookRisk Stage B v6 - release findings

Status: PASS_WITH_WARNINGS. Final: 44 anchors, 147 records, 71 drugs/probes, 101 primary PMIDs. Target gap: 6.

## Verified V5 baseline

{
  "anchors": 26,
  "records": 118,
  "drugs": 58,
  "publications": 80,
  "numerical_records": 73,
  "classes": {
    "Animal": 27,
    "Controlled clinical": 2,
    "Human pharmacokinetic": 61,
    "In vitro": 28
  },
  "inherited_v4": 73,
  "added_v5": 45
}

## Additions

- (+)-Catechin: Food flavanol; paclitaxel microsome null retained (12920504).
- (-)-Epicatechin: Distinct food flavanol stereoisomer; same study null (12920504).
- Morin: Mulberry flavonol; species-dependent paclitaxel assay plus rat/mouse PK (12920504, 16002304, 15885265).
- Hesperetin: Citrus-related aglycone; diclofenac CYP2C9 inhibition (20877134); study stereochemistry unspecified.
- 6-Gingerol: Ginger constituent; separate aconitine pretreatment arm (28051355).
- Thymoquinone: Black-seed constituent; model-specific null and positive doxorubicin findings (33149871, 20582416, 10755708).
- Eugenol: Clove constituent; fluconazole and azithromycin biofilm combinations (33074419).
- Cinnamaldehyde: Cinnamon constituent; metronidazole and colorectal drug combinations (38958374, 24276478).
- Carvacrol: Thyme constituent; metronidazole checkerboard synergy (38958374).
- Thymol: Distinct thyme isomer; partial metronidazole synergy (38958374).
- Glycyrrhizin: Licorice food ingredient; reverse rifampin-to-glycyrrhizin rat interaction (29908072).
- Diallyl sulfide: Garlic sulfide; rat phenacetin exposure (12136947).
- Diallyl disulfide: Distinct garlic disulfide; melphalan combination in myeloma cells (38148345).
- Diallyl trisulfide: Distinct garlic trisulfide; opposite oral PK directions across dipyridamole/nifedipine (22139695, 21535728).
- Allicin: Fresh-crushed-garlic thiosulfinate; doxorubicin-resistant cell co-treatment (38411783).
- Bergapten: Grapefruit furanocoumarin distinct from bergamottin; macitentan PK and microsomes (37492094).
- Diosmin: Citrus glycoside; three human drug PK studies (27690733, 17708066, 12698306).
- Hesperidin: Distinct citrus glycoside; rat verapamil exposure (18449511).

## Deferred candidates

- Baicalein: Qualifying rat doxorubicin report located (19827298), but common dietary-ingredient scope not resolved; medicinal plant use alone does not certify food relevance.
- Rutin: Historical apigenin/rutin paclitaxel attribution remains ambiguous (24871039); no independently curated qualifying isolated-rutin arm admitted in this release.
- Pterostilbene: Recent formulation and sensitization candidates retrieved; exact preparation, qualifying combination and food-source attribution not fully curated.
- Ursolic acid: Retrieved formulation, derivative and combination studies require separation of parent acid, modified carriers and actual drug co-treatment.
- Oleanolic acid: Retrieved azole and formulation candidates require drug-specific arm extraction and food-matrix verification.
- Glycyrrhetinic acid: Drug-probe microsome report located (22943175); metabolite-versus-dietary-parent scope and exact epimer not resolved. Not counted merely as a glycyrrhizin metabolite.

## Validation and access

90/90 checks and 20/20 mutation tests passed. 17 open warning entries / 16 codes. All 29 new interaction records are abstract-verified. V5 rows and files preserved.

See PDF report and machine-readable audits for full limitations and source-specific findings.