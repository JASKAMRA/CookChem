# CookRisk Stage B V7 - clean restart

{
  "version": "v7",
  "anchors": 60,
  "records": 189,
  "drugs": 87,
  "publications": 121,
  "unique_nonempty_doi": 116,
  "numerical_records": 97,
  "classes": {
    "Human pharmacokinetic": 69,
    "In vitro": 66,
    "Animal": 50,
    "Controlled clinical": 4
  },
  "verification": {
    "abstract": 112,
    "metadata_only_recent_audit": 58,
    "full_text_selected": 19
  },
  "new_anchors": 16,
  "new_records": 42,
  "new_publications": 20,
  "new_verification": {
    "abstract": 36,
    "full_text_selected": 6
  },
  "inherited_review_upgrades": 6,
  "target": 60,
  "target_gap": 0,
  "warning_entries": 20,
  "distinct_warning_codes": 19,
  "issue_status_counts": {
    "Unresolved": 17,
    "Resolved with supporting source": 1,
    "Partially resolved": 3,
    "Not applicable after inspection": 2
  },
  "discovery_occurrences": 4805,
  "new_classes": {
    "In vitro": 22,
    "Animal": 13,
    "Human pharmacokinetic": 5,
    "Controlled clinical": 2
  }
}

## Added anchors

- Diosmetin: Citrus flavone; diclofenac and midazolam metabolism assays (20877134, 18191104).
- Rutin: Distinct citrus-peel rutinoside; florfenicol bacterial and tilapia experiments (31252064).
- Pterostilbene: Berry stilbene; drug/probe metabolism and positive/null mouse anticonvulsant findings (30976185, 30877660).
- Ursolic acid: Apple-peel ursane triterpene; doxorubicin and oxaliplatin experimental combinations (30572191, 27472952).
- Oleanolic acid: Distinct apple-peel oleanane triterpene; aminoglycoside synergy and antibiotic nulls (26360766).
- Sesamin: Sesame lignan; current S-warfarin CYP2C9 inhibition experiment (32601017).
- Nobiletin: Citrus flavonoid; 5-fluorouracil cell combination (23441616).
- Tangeretin: Distinct citrus flavonoid; ABCB1 drug response and contrasting midazolam metabolism (27058921, 18191104).
- Ascorbic acid: Defined L-ascorbic acid/vitamin C; human indinavir PK study (15767232). Mixed master vitamin-C analytes not linked.
- Folic acid: Fortified-food/supplement monoglutamate, distinct from total folate; human phenytoin PK and two clinical trials (688723, 21482950, 1828561).
- Phylloquinone: Dietary vitamin K1 reference; PK/PD study in warfarin-treated patients (4091996). IV study is not a food intervention.
- Vanillin: Dietary flavouring; separate tumor-cell, mouse antitumor and rat nephrotoxicity contexts (27493101).
- Oleuropein: Olive constituent; breast-tumor xenograft combination with doxorubicin (28646810). Unequal comparator doses flagged.
- Allyl isothiocyanate: Mustard/horseradish food additive; cisplatin cell and animal combination experiments (26396928).
- Zeaxanthin: Food xanthophyll; bounded null UGT1A9/propofol result (27529203).
- Lutein: Distinct food xanthophyll; trifluoperazine assay and non-SNEDDS warfarin null (27529203, 24009877).

## Validation

42/42 new V7 checks and 10/10 mutation tests passed. Status: PASS_WITH_WARNINGS. V6 suite before/after results and historical-result distinction are in the PDF and README.

V6 and the interrupted attempt are preserved. See the audit and provenance ledgers for unresolved issues.