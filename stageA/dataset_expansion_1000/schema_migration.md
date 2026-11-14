# Schema migration

`updated_master_dataset.csv` preserves every parent column and appends `raw_sd`, `cooked_sd`, and `reported_replicate_design`. Parent rows are null in these extensions because their original source tables did not uniformly provide a retained SD field. The 12 Zhao rows preserve reported condition-level SDs; they are not expanded into artificial replicates.
