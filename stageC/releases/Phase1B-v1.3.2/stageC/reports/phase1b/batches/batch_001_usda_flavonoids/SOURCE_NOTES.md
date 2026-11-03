# USDA Release 3.3 extraction notes — batch 001

Source inspected: USDA ARS, *Database for the Flavonoid Content of Selected Foods*, Release 3.3 (March 2018), official PDF. The summary tables report weighted mean, N, standard error, minimum, maximum, confidence code, and source reference IDs; concentration units are mg/100g edible portion. USDA documentation states the data came from studies using acceptable specific chromatographic/separation methods, and that database table values are weighted aggregates. The 2 selected apple analytes are catechin/epicatechin flavan-3-ols, for which the documentation says no glycoside-to-aglycone conversion is applied.

Accepted records (both raw apple, NDB 09003, printed p.22 / PDF p.24):

- (-)-Epicatechin: mean 7.53 mg/100g; N=150; SE=0.44; range 0.80–19.16; confidence B; source refs 11, 15, 58, 67, 110, 158, 269, 276, 279, 283.
- (+)-Catechin: mean 1.30 mg/100g; N=140; SE=0.07; range 0.00–5.10; confidence B; source refs 11, 15, 58, 67, 110, 269, 276, 283. USDA defines database zero as below detection; it is retained only as range metadata and is not converted to missing.

The underlying Access file that contains individual source observations was listed on the USDA page but was not accessed here. Thus the accepted records are explicitly database-derived aggregate values, not full-text-verified individual study values. No DOI/PMID has been attributed to the aggregated measurement.

Pending candidates are tracked separately in `../CANDIDATES.csv`: apple quercetin (possible glycoside-to-aglycone aggregation ambiguity) and standardized green tea EGCG infusion (basis/category review). Neither is in production data.
