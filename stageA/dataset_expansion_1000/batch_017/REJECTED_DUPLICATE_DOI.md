# Batch 017 source check — no dataset change

Kongphapa et al. (2022), DOI `10.14456/apst.2022.5`, was retrieved as a direct primary PDF and screened for its Table 4 raw/cooked individual HPLC values. Before any output data were written, the duplicate-family guard found that all nine eligible Chaya pairs were already present in the Batch 016 parent master under this exact DOI.

No master dataset, ledger, state, model, or historical package was changed for this duplicate source. The generated build script intentionally fails before writing if reused; it is retained as an audit trail of the rejected duplicate check, not as a validated batch.
