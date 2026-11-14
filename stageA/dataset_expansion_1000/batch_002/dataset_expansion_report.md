# Scientific dataset expansion — controlled batch 002

    ## Result

    The 1,000-observation target is **not reached**. The controlled master is
    **471 observations** from **12 DOI families**:
    20 additions from one independent primary paper. Its 451-row Batch-001
    parent is preserved exactly when projected to the parent schema.

    ## Admission

    Li et al. (2024), DOI `10.3390/foods13020230`, Table 1 and Methods, reports
    individual phenolic acids in raw and cooked triticale as mean ± SD across
    three repetitions. Values are HPLC-DAD measurements in μg/g dry sample.
    Atmospheric-pressure porridge boiling is 90 minutes; high-pressure boiling
    is 60 minutes at 60 kPa. The source explicitly uses separate free and bound
    extraction procedures; that fraction is preserved in `analytical_definition`
    and comparisons are only made within the same fraction.

    Six compounds with pre-existing verified descriptor identities contribute 20
    direct raw/cooked pairs: protocatechuic (4), syringic (4), caffeic (1),
    p-coumaric (3), ferulic (4), and sinapic acid (4). Four other Table-1
    analytes are deliberately excluded because no exact verified descriptor
    identity is available in the parent schema. No descriptor was generated or
    inferred.

    ## Boundary

    These are apparent concentration ratios only, not total-mass retention.
    They diversify source, cereal matrix, method, and analytical fraction, but
    do not create a strict protocol-identical cross-source replication. No model
    is retrained and Stage C is not authorized.
