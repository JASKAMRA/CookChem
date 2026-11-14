# 989 arithmetic-matching recovery audit

Of 989 arithmetic-matching records, 338 are `arithmetic_and_source_verified` from preserved Batch021 primary-source mappings. This recovered 221 beyond the prior 117 locally verified records; it does not infer evidence from arithmetic alone.

The 651 not retained earlier divide into: 610 metadata-missing/no contradiction, 0 measurement-basis-unverified, 23 pairing-ambiguous, and 18 DOI/source-conflict. Missing documentation is not proof of a wrong value.

The 81 discrepant and 54 non-comparable records remain separate; no corrections were proposed without direct evidence.

The recovered subset has 338 observations, 45 molecular identities, and 6 DOI families. Fixed historical XGBoost molecular-CV mean fold R² is -2.462845 (SD 6.775628); mean MAE 46.671816; mean RMSE 147.158865. This is not directly comparable to 0.4004 because the dataset target/data provenance are now explicitly constrained, even though the historical feature schema and fixed parameters were used. DOI overlap occurs in every molecular fold; see the source-overlap audit.
