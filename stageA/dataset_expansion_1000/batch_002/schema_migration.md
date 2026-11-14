# Schema migration

    Batch 002 preserves every Batch-001 field and adds `analytical_definition`.
    Parent and Batch-001 rows are null for that field because an individual
    free/bound extraction category was not captured in their source contracts.
    The 20 Li rows set it to either `free phenolic-acid extract` or `bound
    phenolic-acid extract`. These are distinct analytical quantities; no row is
    a total-phenolic or total-mass-retention result.
