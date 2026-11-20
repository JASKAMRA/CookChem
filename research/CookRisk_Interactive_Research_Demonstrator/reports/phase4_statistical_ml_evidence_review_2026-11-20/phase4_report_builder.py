"""Build read-only Phase 4 reports from explicitly approved Stage A evidence."""
import csv, hashlib, json, math, statistics
from collections import Counter
from pathlib import Path

RECON = Path("stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv")
BATCH = Path("stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv")
BATCH_DIR = BATCH.parent
AUDIT = Path("stageA/molecular_vs_source_validation_audit")
OUT = Path("research/CookRisk_Interactive_Research_Demonstrator/reports/phase4_statistical_ml_evidence_review_2026-11-20")
RECON_PIN = "f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0"
BATCH_PIN = "111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8"
MODELS = ["dummy_median", "extra_trees", "gradient_boosting", "random_forest", "ridge", "svr_rbf", "xgboost"]
METRICS = ["r2", "mae", "rmse"]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def sidecar(d):
    out = {}
    for line in (d / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        x = line.split(None, 1)
        if len(x) == 2:
            out[x[1].strip()] = x[0].strip().lower()
    return out

def check(d, sums, name):
    actual = digest(d / name)
    expected = sums.get(name, "")
    return {"actual": actual, "expected": expected, "match": bool(expected and actual == expected)}

def write_csv(name, fields, rows):
    with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def quantile(v, p):
    s = sorted(v); pos = (len(s)-1)*p; lo = math.floor(pos); hi = math.ceil(pos)
    return s[lo] + (s[hi]-s[lo])*(pos-lo)

def summarize(v):
    n = len(v); mean = statistics.mean(v) if n else None; med = statistics.median(v) if n else None
    sd = statistics.stdev(v) if n > 1 else None
    m2 = sum((x-mean)**2 for x in v)/n if n else 0
    m3 = sum((x-mean)**3 for x in v)/n if n else 0
    return {"n_valid":n,"mean":mean,"median":med,"sd_sample":sd,
            "q1_linear":quantile(v,.25) if n else None,"q3_linear":quantile(v,.75) if n else None,
            "minimum":min(v) if n else None,"maximum":max(v) if n else None,
            "skewness_moment":m3/(m2**1.5) if m2 else 0.0,
            "mad_unscaled":statistics.median([abs(x-med) for x in v]) if n else None}

def table(headers, rows):
    lines=["| "+" | ".join(headers)+" |","| "+" | ".join(["---"]*len(headers))+" |"]
    lines += ["| "+" | ".join(str(x).replace("|","/") for x in r)+" |" for r in rows]
    return "\n".join(lines)

def fmt(x):
    return "NA" if x is None else f"{x:.3f}"

def main():
    # Hash gates precede parsing of either approved dataset.
    rh, bh = digest(RECON), digest(BATCH)
    if rh != RECON_PIN: raise SystemExit(f"Reconstruction hash mismatch: {rh}; expected {RECON_PIN}")
    if bh != BATCH_PIN: raise SystemExit(f"Batch021 hash mismatch: {bh}; expected {BATCH_PIN}")
    allowed_outputs = {
        "phase4_report_builder.py", "PHASE4_STATISTICAL_AND_ML_REVIEW.md", "STATISTICAL_REVIEW_TABLE.csv",
        "HISTORICAL_ML_EVIDENCE_REGISTER.csv", "ML_PROVENANCE_GAP_REGISTER.csv",
        "VALIDATION_DESIGN_REVIEW.csv", "METRIC_INTERPRETATION_REGISTER.csv", "PHASE4_EXECUTION_LOG.md",
    }
    unexpected = [p.name for p in OUT.iterdir()] if OUT.exists() else []
    unexpected = [name for name in unexpected if name not in allowed_outputs]
    if unexpected:
        raise SystemExit(f"Unexpected pre-existing items in output folder: {unexpected}")
    recon = read_csv(RECON)
    with BATCH.open(encoding="utf-8-sig", newline="") as f:
        rd=csv.DictReader(f); bcols=rd.fieldnames; bn=sum(1 for _ in rd)
    if (len(recon),len(recon[0])) != (1016,43) or (bn,len(bcols)) != (1016,38):
        raise SystemExit("Approved input dimensions differ from expected dimensions")

    bs, aus = sidecar(BATCH_DIR), sidecar(AUDIT)
    post = json.loads((BATCH_DIR/"post1000_validation_summary.json").read_text(encoding="utf-8"))
    pjson={f"{r['model']}|{r['validation']}":r for r in post["models"]}
    pagg={f"{r['model']}|{r['validation']}":r for r in read_csv(BATCH_DIR/"post1000_model_comparison.csv")}
    pcomp={}
    for model in MODELS:
        for r in read_csv(BATCH_DIR/f"post1000_model_comparison_{model}.csv"):
            pcomp[f"{r['model']}|{r['validation']}"]=r
    keys=sorted(pjson)
    if len(keys)!=21 or set(keys)!=set(pagg) or set(keys)!=set(pcomp): raise SystemExit("Post1000 coverage mismatch")
    conflicts=[]
    for key in keys:
        for m in METRICS:
            if abs(float(pjson[key][m])-float(pcomp[key][m]))>1e-12: raise SystemExit(f"Component/JSON conflict at {key} {m}")
        if any(abs(float(pcomp[key][m])-float(pagg[key][m]))>1e-12 for m in METRICS): conflicts.append(key)
    post_names=["post1000_model_comparison.csv","post1000_fold_metrics.csv","post1000_oof_predictions.csv",
                "post1000_validation_summary.json","post1000_validation_and_evaluation.md"]
    post_integrity={n:check(BATCH_DIR,bs,n) for n in post_names}
    component_integrity={}
    for model in MODELS:
        for stem in ["model_comparison","fold_metrics","oof_predictions"]:
            n=f"post1000_{stem}_{model}.csv"; component_integrity[n]=check(BATCH_DIR,bs,n)
    if not all(x["match"] for x in component_integrity.values()):
        raise SystemExit("A model-specific component checksum differs; stop and inspect")

    mol=json.loads((AUDIT/"validation_summary.json").read_text(encoding="utf-8"))
    if mol.get("input_sha256")!=BATCH_PIN: raise SystemExit("Molecular/source input digest mismatch")
    audit_names=["validation_summary.json","validation_summary_rows.csv","fold_metrics.csv","oof_predictions.csv",
                 "split_audit.csv","validation_comparison_report.md"]
    audit_integrity={n:check(AUDIT,aus,n) for n in audit_names}
    if not all(x["match"] for x in audit_integrity.values()): raise SystemExit("Molecular/source sidecar mismatch")
    split=read_csv(AUDIT/"split_audit.csv")

    def numeric(col):
        vals=[]
        for r in recon:
            try:
                x=float(r[col])
                if math.isfinite(x): vals.append(x)
            except (ValueError,TypeError): pass
        return vals
    fields=["target_value_percent","raw_concentration","cooked_concentration","Temperature_C",
            "Cooking_Time_min","raw_sd","cooked_sd","RDKit_Molecular_Weight","RDKit_LogP","RDKit_TPSA",
            "RDKit_HBond_Donors","RDKit_HBond_Acceptors","RDKit_Rotatable_Bonds",
            "RDKit_Aromatic_Rings","RDKit_Hydroxyl_Groups"]
    stats={n:summarize(numeric(n)) for n in fields}
    missing={n:len(recon)-stats[n]["n_valid"] for n in fields}
    acr=numeric("target_value_percent"); q1,q3=quantile(acr,.25),quantile(acr,.75)
    lo,hi=q1-1.5*(q3-q1),q3+1.5*(q3-q1)
    high_flags=sum(x>hi for x in acr); sensitivity=summarize([x for x in acr if lo<=x<=hi])
    gt100=sum(x>100 for x in acr); gt1000=sum(x>1000 for x in acr)
    zero=sum(float(r["cooked_concentration"])==0 for r in recon)
    units=len({r["concentration_unit"].strip() for r in recon if r["concentration_unit"].strip()})
    bases={r["measurement_basis"].strip() for r in recon if r["measurement_basis"].strip()}
    # Preserve Phase 3's documented semantic classification (6 labels); a
    # literal substring count would miss labels adjudicated as unspecified.
    unspecified=6
    miss={n:sum(not r[n].strip() for r in recon) for n in
          ["food_matrix","compound","compound_class","cooking_method_normalized","doi",
           "analytical_definition","reported_replicate_design","raw_sd","cooked_sd","Temperature_C","Cooking_Time_min"]}
    groups={}
    for name in ["food_matrix","compound","compound_class","cooking_method_normalized"]:
        counts=Counter(r[name].strip() or "[MISSING]" for r in recon); sizes=list(counts.values())
        groups[name]={"categories":len(counts),"missing":counts.get("[MISSING]",0),
                      "lt5":sum(n<5 for n in sizes),"5to9":sum(5<=n<=9 for n in sizes),
                      "ge10":sum(n>=10 for n in sizes),"singletons":sum(n==1 for n in sizes)}
    dois=Counter(r["doi"].strip() or "[MISSING]" for r in recon)
    doi={"families":len(dois),"missing":dois.get("[MISSING]",0),
         "repeated":sum(n>1 for n in dois.values()),"largest":max(dois.values()),
         "top3_share":sum(n for _,n in dois.most_common(3))/len(recon)}
    source_overlap=[int(r["source_group_overlap_count"]) for r in split if r["validation_strategy"]=="molecular_grouped"]
    mol_overlap=[int(r["molecular_group_overlap_count"]) for r in split if r["validation_strategy"]=="source_held_out"]
    OUT.mkdir(parents=True, exist_ok=True)

    # Statistical evidence table.
    sf=["review_id","domain","check","dataset_or_evidence","status","value_or_finding","interpretation_and_limit","evidence_reference"]
    sr=[]
    def addstat(i,d,c,ds,s,v,l,e):
        sr.append(dict(review_id=i,domain=d,check=c,dataset_or_evidence=ds,status=s,
                       value_or_finding=v,interpretation_and_limit=l,evidence_reference=e))
    addstat("S01","Integrity","Reconstruction hash/shape","Reconstruction","VERIFIED",f"{rh}; 1,016 x 43",
            "Approved demonstrator descriptive role only; not canonical or independently validated.","Phase 2/3; current hash gate")
    for i,n in enumerate(fields,2):
        unit=("ACR percentage points" if n=="target_value_percent" else
              "heterogeneous concentration units/bases; pooled physical interpretation invalid" if n in
              ["raw_concentration","cooked_concentration","raw_sd","cooked_sd"] else
              "compound-level calculated descriptor repeated across observations" if n.startswith("RDKit_") else
              "reported temperature/time; source definitions not re-adjudicated")
        addstat(f"S{i:02d}","Description",n+" distribution","Reconstruction","VERIFIED",
                json.dumps({**stats[n],"missing":missing[n]},separators=(",",":")),
                unit+"; descriptive only, no inferential claim.","Phase 4 standard-library summary")
    for i,n in enumerate(["food_matrix","compound","compound_class","cooking_method_normalized"],2+len(fields)):
        addstat(f"S{i:02d}","Group support",n,"Reconstruction","VERIFIED",json.dumps(groups[n],separators=(",",":")),
                "Counts are rows, not independent studies; sparse groups/label variants limit inference.","Phase 4 counts")
    next_stat=2+len(fields)+4
    addstat(f"S{next_stat:02d}","Clustering","DOI/study clustering","Reconstruction","VERIFIED",json.dumps(doi,separators=(",",":")),
            "Rows in DOI families cannot be assumed independent.","Phase 4 DOI counts; Phase 3 report")
    next_stat+=1
    addstat(f"S{next_stat:02d}","Missingness","Definitions/replicate metadata","Reconstruction","VERIFIED",json.dumps(miss,separators=(",",":")),
            "Missing replicate design/SD limits uncertainty and pseudoreplication assessment.","Phase 4 missingness")
    next_stat+=1
    addstat(f"S{next_stat:02d}","Sensitivity","Tukey high-value descriptive sensitivity","Reconstruction ACR","VERIFIED",
            json.dumps({"lower_fence":lo,"upper_fence":hi,"high_flags":high_flags,"all_rows":stats["target_value_percent"],
                        "excluding_high_flags_sensitivity_only":sensitivity},separators=(",",":")),
            "97 high flags excluded from a summary only; no row removed/corrected; flags are not error determinations.","Phase 3 outlier CSV; Phase 4")
    next_stat+=1
    addstat(f"S{next_stat:02d}","Anomalies","ACR thresholds/cooked-zero","Reconstruction ACR","VERIFIED",
            json.dumps({"acr_gt_100":gt100,"acr_gt_1000":gt1000,"cooked_zero":zero}),
            "Review flags, not errors; ACR is not mass retention.","Phase 3 report; Phase 4 counts")
    next_stat+=1
    addstat(f"S{next_stat:02d}","Compatibility","Units and measurement bases","Reconstruction","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED",
            json.dumps({"unit_labels":units,"basis_labels":len(bases),"basis_labels_classified_unspecified_in_phase3":unspecified,
                        "analytical_definition_missing":miss["analytical_definition"]}),
            "Heterogeneous/unspecified bases block harmonized inference.","Phase 3 report; Phase 4 counts")
    next_stat+=1
    addstat(f"S{next_stat:02d}","Target","Stored-target precision comparison","Reconstruction/Batch021","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED",
            "Phase 3 found 118 strict stored-target versus recalculated-ACR differences; all match displayed precision. Separately, Reconstruction versus Batch021 has 15 serialized target-cell differences, maximum numeric delta 2.842170943040401e-14 pp.",
            "Source rounding and unrounded values remain unverified; the two comparisons are distinct.","Phase 3 report/comparison")
    next_stat+=1
    addstat(f"S{next_stat:02d}","Inference","Cooking/group hypothesis tests","Reconstruction","BLOCKED","No inferential tests run.",
            "Independence, sample unit, compatible measurements, pairing, replicate uncertainty and multiplicity plan are not established.",
            "Phase 3 gaps; Phase 4 design")
    next_stat+=1
    addstat(f"S{next_stat:02d}","Scientific meaning","ACR versus total-mass retention","Reconstruction","BLOCKED",
            "No paired masses or validated yield; Phase 3 says NOT_ESTABLISHED for all 1,016 rows.",
            "ACR=100 x C_cooked/C_raw; it does not establish total-mass retention. Retention_Final source not accessed.",
            "Phase 3 report; scope boundary")
    write_csv("STATISTICAL_REVIEW_TABLE.csv",sf,sr)

    # Evidence register: paired values make unresolved historical versions explicit.
    rf=["evidence_id","artifact_path","artifact_type","model","dataset_family_and_role","target_definition",
        "evaluation_type","component_summary_metrics","current_combined_csv_metrics","available_input_hash",
        "code_configuration_provenance","fold_or_population_information","integrity_and_interpretability"]
    rr=[]
    cfg={"dummy_median":"DummyRegressor median","ridge":"Ridge alpha=10",
         "random_forest":"RandomForest 10 trees, leaf=2, seed=42","extra_trees":"ExtraTrees 10 trees, leaf=2, seed=42",
         "gradient_boosting":"GradientBoosting 25 estimators, leaf=3, learning_rate=0.03, seed=42",
         "svr_rbf":"SVR RBF C=10, epsilon=0.1",
         "xgboost":"XGBoost 10 estimators, depth=4, learning_rate=0.03, subsample/colsample=0.8, seed=42"}
    prot={"compound_grouped_5fold":"GroupKFold(5), canonical_molecular_id",
          "food_matrix_grouped_5fold":"GroupKFold(5), food_matrix",
          "leave_one_source_out":"LeaveOneGroupOut, DOI; 32 source folds"}
    for key in keys:
        c,j,a=pcomp[key],pjson[key],pagg[key]; model,val=key.split("|")
        saved={m:c[m] for m in METRICS}; current={m:a[m] for m in METRICS}
        mismatch=any(abs(float(saved[m])-float(current[m]))>1e-12 for m in METRICS)
        rr.append(dict(evidence_id="P21-"+model+"-"+val,
            artifact_path=f"stageA/dataset_expansion_1000/batch_021/post1000_model_comparison_{model}.csv; post1000_validation_summary.json; post1000_validation_and_evaluation.md; post1000_model_comparison.csv",
            artifact_type="Saved pooled OOF metrics; fold/OOF artifacts listed in package",
            model=model,dataset_family_and_role="Batch021 historical ML family; Reconstruction not substituted",
            target_definition="target_value_percent = 100*cooked_concentration/raw_concentration; apparent ratio percent",
            evaluation_type=val,component_summary_metrics=json.dumps(saved,separators=(",",":")),
            current_combined_csv_metrics=json.dumps(current,separators=(",",":")),
            available_input_hash="Not embedded in post1000 JSON; package path/sidecar and code link adjacent CSV, not per-run digest",
            code_configuration_provenance=cfg[model]+"; run_one_post1000_model.py; no tuning trace found",
            fold_or_population_information=prot[val]+"; component OOF has 1,016 distinct IDs/model/protocol",
            integrity_and_interpretability=("Component/summary values agree and match sidecar; combined row conflicts." if mismatch
                else "Component/summary values agree and match sidecar; combined row agrees numerically but file hash fails. No rerun.")))
    for r in mol["results"]:
        rr.append(dict(evidence_id="MVS-"+r["validation_strategy"],
            artifact_path="stageA/molecular_vs_source_validation_audit/validation_summary.json; fold_metrics.csv; split_audit.csv; oof_predictions.csv; validation_comparison_report.md",
            artifact_type="Saved single-model grouped-validation and split evidence",model="ExtraTreesRegressor",
            dataset_family_and_role="Batch021 historical; embedded input_sha256 matches approved Batch021",
            target_definition="target_value_percent = 100*cooked_concentration/raw_concentration",
            evaluation_type=r["validation_strategy"],
            component_summary_metrics=json.dumps({m:r[m] for m in ["r2","mae","rmse","mean_fold_r2","std_fold_r2"]},separators=(",",":")),
            current_combined_csv_metrics="",available_input_hash=mol["input_sha256"],
            code_configuration_provenance="25 trees; min_samples_leaf=2; max_features=0.8; seed=42; fold-local preprocessing; no tuning documented",
            fold_or_population_information=f"GroupKFold(5); n={r['n_observations']}; {r['n_molecular_groups']} molecular/{r['n_source_groups']} DOI groups",
            integrity_and_interpretability="Named summary/fold/split/OOF/report digests match sidecar; no rerun."))
    imp=check(BATCH_DIR,bs,"extra_trees_feature_importance.csv")
    rr.append(dict(evidence_id="P21-ET-FEATURE-IMPORTANCE",
        artifact_path="stageA/dataset_expansion_1000/batch_021/extra_trees_feature_importance.csv; run_one_post1000_model.py",
        artifact_type="Full-data transformed feature importance; not a validation metric",model="ExtraTreesRegressor",
        dataset_family_and_role="Batch021 historical",target_definition="target_value_percent; apparent ratio percent",
        evaluation_type="Full-data fit, not holdout",component_summary_metrics="",current_combined_csv_metrics="",
        available_input_hash="Not embedded; code reads adjacent Batch021 master",
        code_configuration_provenance="Full pipeline fit; importance descriptive only",
        fold_or_population_information="Full dataset, not unbiased holdout",
        integrity_and_interpretability=f"Sidecar match={imp['match']}; not causal or external-validity evidence."))
    write_csv("HISTORICAL_ML_EVIDENCE_REGISTER.csv",rf,rr)

    # Provenance gaps.
    gf=["gap_id","priority","area","finding","status","evidence","impact","safe_next_step"]
    grows=[
      ["G01","HIGH","Integrity","Combined post1000 comparison/fold/OOF CSVs fail recorded digests.","VERIFIED","Actual and sidecar hashes in report; component triplets and JSON/Markdown match.","Combined outputs not checksum-pinned.","Preserve; owner identifies intended version."],
      ["G02","HIGH","Metric consistency",f"{len(conflicts)}/21 combined model/protocol rows conflict with component and JSON/Markdown.","VERIFIED","All 21 components agree with summary; aggregate differs in listed rows.","Model rankings and exact values ambiguous.","Do not choose or recalculate; request provenance."],
      ["G03","HIGH","Divergence cause","Reason for combined artifact divergence not established.","MISSING","Static scripts reveal plausible alternate writer/specification, no execution record proves cause.","Cannot identify intended result version.","Review contemporaneous logs/backups with owner."],
      ["G04","MEDIUM","Input linkage","Post1000 JSON lacks a run-specific input_sha256.","VERIFIED","Code/path/sidecar link adjacent Batch021 file; digest absent from summary.","No explicit per-run input binding.","Preserve gap; no retroactive edit."],
      ["G05","MEDIUM","Split linkage","No full observation-level train/test membership file; combined OOF lacks fold ID and fails hash.","BLOCKED","Fold rows contain group names/counts, not full train/test record IDs.","Exact record-level leakage cannot be independently audited.","Future authorized package should preserve immutable fold assignments."],
      ["G06","MEDIUM","Model selection","No tuning or test reuse log found.","MISSING","Fixed final settings in code; no selection trace in reviewed evidence.","Selection bias cannot be excluded.","Request contemporaneous records; do not infer no tuning."],
      ["G07","HIGH","External validity","No external lab, temporal, prospective or deployment validation documented.","MISSING","Only named internal Stage A packages reviewed.","No cross-lab/deployment claim.","Any future validation separately authorized."],
      ["G08","HIGH","Scientific endpoint","ACR compatibility and mass retention unresolved.","BLOCKED","Phase 3 documents heterogeneity, missing definitions, no paired masses and NOT_ESTABLISHED mass retention.","No total-mass or harmonized endpoint inference.","Primary-source adjudication and compatible paired mass/yield needed."],
      ["G09","HIGH","Statistical inference","Inferential comparisons unsupported by independence/pairing/replicate/multiplicity evidence.","BLOCKED","Sparse groups, DOI clustering, missing replicate metadata/SD and mixed bases.","No significance or causal claims.","Specify sample unit, design and multiplicity before testing."],
      ["G10","MEDIUM","Fitted model artifact","No estimator file among inspected Batch021 .pkl/.joblib/.model/.ubj files.","MISSING","Targeted non-recursive extension check in Batch021 only.","No serialized fitted model to verify.","Future reproduction requires pinned environment and authorization."],
    ]
    write_csv("ML_PROVENANCE_GAP_REGISTER.csv",gf,[dict(zip(gf,r)) for r in grows])

    # Required ML design statuses.
    vf=["check_id","review_area","item","status","evidence_reviewed","assessment","remaining_gap_or_consequence"]
    vr=[
      ["V01","Input","Batch021 pin/shape","VERIFIED",f"{bh}; 1,016 x 38; package sidecar matches.","Historical family identified.","Does not reproduce metrics."],
      ["V02","Input","Reconstruction pin/shape","VERIFIED",f"{rh}; 1,016 x 43.","Descriptive role only.","Not used as ML replacement."],
      ["V03","Target","Historical target","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","Saved code/summary: 100*cooked/raw; Phase 2/3 formula evidence.","Apparent concentration-ratio percent.","Source precision/mass semantics limited."],
      ["V04","Split","Compound grouping","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","GroupKFold(5) by canonical molecular ID.","Molecular holdout, DOI may remain.","Not unseen source."],
      ["V05","Split","Food-matrix grouping","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","GroupKFold(5) by food_matrix.","Matrix holdout within dataset.","DOI overlap not saved for this split."],
      ["V06","Split","Post1000 DOI grouping","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","LeaveOneGroupOut DOI; 32 folds; saved component OOF 1,016 unique IDs/model/protocol.","Paper-family holdout; all saved source R2 values negative.","Combined files fail hash; DOI not lab identity."],
      ["V07","Split","Molecular-audit molecular strategy","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED",f"Zero molecular overlap; {min(source_overlap)}-{max(source_overlap)} DOI overlaps in saved folds.","Unseen molecular ID stress test, not source.","One fixed model."],
      ["V08","Split","Molecular-audit DOI strategy","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED",f"Zero DOI overlap; {min(mol_overlap)}-{max(mol_overlap)} molecular overlaps.","DOI holdout, not unseen compounds/labs.","Overlap not independently recreated."],
      ["V09","Preprocessing","Fold-local transformations","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","Pipelines fit imputation/scaling/encoding on training folds per code and split audit.","Fold-aware as documented.","No rerun."],
      ["V10","Features","Direct target as predictor","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","Feature lists omit target and cooked concentration; one audit uses raw_concentration, target denominator.","No direct target column found.","Use-time availability unspecified."],
      ["V11","Features","Feature selection","NOT_APPLICABLE","Reviewed fixed columns; no selection step in pipelines.","No feature selection to inspect.","Selection of model/hyperparameters remains unknown."],
      ["V12","Randomness","Seed/split randomness","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","Seed 42 for configured stochastic estimators; GroupKFold/LOGO has no shuffle/random state.","Split seed not configured.","Software versions absent from summary."],
      ["V13","Selection","Tuning history","MISSING","No selection log; only fixed final settings.","Cannot exclude test-informed model selection.","No pass claim."],
      ["V14","Leakage","Group overlap","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","Molecular folds: 17-20 DOI overlap; DOI folds: zero DOI overlap and 6-18 molecular overlap.","Protocols answer different transfer questions.","Saved overlap not recomputed."],
      ["V15","Leakage","Exact row-level split/duplicate linkage","BLOCKED","No full row-level split membership; combined OOF lacks fold ID and fails digest.","Cannot inspect every related record across train/test.","Needs immutable assignment evidence."],
      ["V16","Leakage","Target leakage","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","Target omitted; raw_concentration appears in separate audit and is denominator.","No direct target column leakage found.","Prediction context not specified."],
      ["V17","Leakage","Preprocessing leakage","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","Training-only preprocessing documented in script/split audit.","No such leak is documented.","Not independently rerun."],
      ["V18","Leakage","Test-set reuse","MISSING","No experiment history.","Cannot determine reuse.","No pass claim."],
      ["V19","Validation","External validation","MISSING","No external test source/lab.","Internal grouped outputs only.","No external claim."],
      ["V20","Validation","Temporal validation","MISSING","No time-ordered holdout.","Drift not evaluated.","No temporal claim."],
      ["V21","Validation","Lab/site validation","MISSING","DOI available; lab/site IDs absent.","DOI is not lab identity.","No cross-lab claim."],
      ["V22","Generalization","Unseen compounds","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","Saved molecular grouped pooled and mean-fold R2 negative.","No positive transfer demonstrated for fixed model.","Historical only."],
      ["V23","Generalization","Unseen food","BLOCKED","Food-matrix metrics exist but combined digest fails; no source overlap audit.","Exact performance not adjudicated.","Do not claim unseen-food performance."],
      ["V24","Generalization","Cross-study","DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED","DOI holdout exists; all saved source R2 values negative in both views.","No positive source-heldout result evidenced.","Metric conflict/lab gap remain."],
      ["V25","Generalization","Deployment","MISSING","No prospective/deployment test; report says no model selected.","Deployment unsupported.","Historical research only."],
      ["V26","Statistical","Inferential/causal comparisons","BLOCKED","No independent sampling frame, compatible paired data, replicate uncertainty or multiplicity plan.","Descriptive groups are noncausal.","No significance testing."],
      ["V27","Metrics","Pooled vs mean-fold R2","VERIFIED","Molecular/source summary stores different r2 and mean_fold_r2 fields.","Must remain distinct.","No post1000 fold means derived."],
      ["V28","Integrity","Combined post1000 outputs","VERIFIED","Combined comparison/fold/OOF fail sidecar; components and JSON/Markdown match.","Integrity discrepancy confirmed.","Cause/version unresolved."],
    ]
    write_csv("VALIDATION_DESIGN_REVIEW.csv",vf,[dict(zip(vf,r)) for r in vr])

    # Metric register keeps original metric names and all saved numerical views.
    mf=["metric_record_id","source_artifact","model","evaluation_protocol","saved_metric_names_and_values",
        "definitions_and_units","evaluation_population","interpretation_and_limit","status","reconciliation"]
    mr=[]
    defs={"r2":"R-squared; unitless; pooled OOF goodness of fit.",
          "mae":"Mean absolute error; target percentage points.",
          "rmse":"Root mean squared error; target percentage points; more sensitive to large errors."}
    for key in keys:
        c,a=pcomp[key],pagg[key]; model,protocol=key.split("|")
        values={"component_and_summary":{m:c[m] for m in METRICS},"current_combined_csv":{m:a[m] for m in METRICS}}
        bad=any(abs(float(c[m])-float(a[m]))>1e-12 for m in METRICS)
        mr.append(dict(metric_record_id="P21-"+model+"-"+protocol,
            source_artifact=f"post1000_model_comparison_{model}.csv; post1000_validation_summary.json; combined comparison CSV",
            model=model,evaluation_protocol=protocol,saved_metric_names_and_values=json.dumps(values,separators=(",",":")),
            definitions_and_units=json.dumps(defs,separators=(",",":")),
            evaluation_population=prot[protocol]+"; pooled 1,016 OOF predictions",
            interpretation_and_limit="R2 is not accuracy; errors do not establish causal/cross-study comparability or total-mass meaning.",
            status="BLOCKED" if bad else "DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED",
            reconciliation="Conflicting values; no view selected." if bad else "Values agree but combined digest fails; no rerun."))
    for result in mol["results"]:
        names=["r2","mae","rmse","mean_fold_r2","std_fold_r2","mean_fold_mae","std_fold_mae","mean_fold_rmse","std_fold_rmse"]
        units_map={m:("unitless" if "r2" in m else "target percentage points") for m in names}
        pop={m:("pooled 1,016 OOF predictions" if not m.startswith(("mean_fold","std_fold")) else
                "arithmetic mean/sample SD across five folds") for m in names}
        mr.append(dict(metric_record_id="MVS-"+result["validation_strategy"],
            source_artifact="molecular_vs_source_validation_audit/validation_summary.json and sidecar-matched split/fold/OOF",
            model="ExtraTreesRegressor",evaluation_protocol=result["validation_strategy"],
            saved_metric_names_and_values=json.dumps({m:result[m] for m in names},separators=(",",":")),
            definitions_and_units=json.dumps(units_map,separators=(",",":")),
            evaluation_population=json.dumps(pop,separators=(",",":"))+"; GroupKFold(5)",
            interpretation_and_limit="Pooled and fold-mean R2 are distinct; saved history, not fresh reproduction.",
            status="DOCUMENTED_BUT_NOT_INDEPENDENTLY_VERIFIED",reconciliation="Copied without recomputing or replacing values."))
    write_csv("METRIC_INTERPRETATION_REGISTER.csv",mf,mr)

    # Main narrative.
    labels={"target_value_percent":"ACR target (% points)","raw_concentration":"Raw concentration (mixed units)",
            "cooked_concentration":"Cooked concentration (mixed units)","Temperature_C":"Temperature_C",
            "Cooking_Time_min":"Cooking_Time_min","raw_sd":"raw_sd (mixed units)","cooked_sd":"cooked_sd (mixed units)",
            "RDKit_Molecular_Weight":"RDKit_Molecular_Weight","RDKit_LogP":"RDKit_LogP","RDKit_TPSA":"RDKit_TPSA",
            "RDKit_HBond_Donors":"RDKit_HBond_Donors","RDKit_HBond_Acceptors":"RDKit_HBond_Acceptors",
            "RDKit_Rotatable_Bonds":"RDKit_Rotatable_Bonds","RDKit_Aromatic_Rings":"RDKit_Aromatic_Rings",
            "RDKit_Hydroxyl_Groups":"RDKit_Hydroxyl_Groups"}
    nrows=[[labels[n],stats[n]["n_valid"],missing[n],fmt(stats[n]["mean"]),fmt(stats[n]["median"]),
            fmt(stats[n]["sd_sample"]),fmt(stats[n]["q1_linear"]),fmt(stats[n]["q3_linear"]),
            fmt(stats[n]["minimum"]),fmt(stats[n]["maximum"]),fmt(stats[n]["skewness_moment"])] for n in fields]
    grows2=[[n,groups[n]["categories"],groups[n]["missing"],groups[n]["lt5"],groups[n]["5to9"],
             groups[n]["ge10"],groups[n]["singletons"]] for n in ["food_matrix","compound","compound_class","cooking_method_normalized"]]
    molr, srcr=mol["results"]
    jr=[float(pjson[f"{m}|leave_one_source_out"]["r2"]) for m in MODELS]
    ar=[float(pagg[f"{m}|leave_one_source_out"]["r2"]) for m in MODELS]
    pi=post_integrity
    report=f"""# COOKRISK Phase 4 — Statistical and Historical ML Evidence Review

**Overall status: PARTIALLY COMPLETE**  
**Review date:** 2026-11-20  
**Phase 5/6:** Not started.

## Executive summary

The approved Reconstruction descriptive review and read-only review of named Batch021 historical ML evidence were completed as far as available records allow. Both approved dataset hashes and dimensions match. No model training, prediction generation, validation rerun, source-data edit, or historical artifact repair occurred.

Reconstruction contains 1,016 stored apparent concentration ratios (ACR). Mean={fmt(stats['target_value_percent']['mean'])}%, median={fmt(stats['target_value_percent']['median'])}%, moment skewness={fmt(stats['target_value_percent']['skewness_moment'])}; there are {high_flags} upper Tukey flags. Excluding those flags from a sensitivity summary only gives mean={fmt(sensitivity['mean'])}% and median={fmt(sensitivity['median'])}% over {sensitivity['n_valid']} rows. No data were changed or removed. Heterogeneous bases, DOI clustering, missing replicate metadata and incomplete analytical definitions preclude pooled inference or causal claims. ACR is not total-mass retention.

The Batch021 package has seven saved model families across compound-, food-matrix- and DOI-grouped evaluations. Three combined post1000 CSV files fail recorded SHA256SUMS checks. The current combined model comparison conflicts with checksum-matched per-model files and JSON/Markdown in {len(conflicts)}/21 model/protocol rows. Both views show negative DOI-held-out R2 for every model, but values and ranking differ; no view was selected. A separate molecular/source ExtraTrees audit has a hash-matched Batch021 input and matching saved summary/fold/split/OOF checksums; pooled R2 is negative under both group strategies. Evidence does not support deployment, external-lab, temporal or real-world predictive claims.

## Scope and safety

Reviewed the required Phase 2 provenance and Phase 3 ACR reports/registers, approved Reconstruction and Batch021 identities, and named Stage A validation packages only. The restricted metrics catalog, Stage B, restricted Stage C/D materials, and Retention_Final source CSV were not accessed. Reconstruction was used only for descriptive statistics; Batch021 remained the historical ML evidence family. No existing source, dataset, registry, model, prediction, metric, validation output, dependency or lockfile was modified. No Git write operation occurred.

## Input identities

| Dataset | Approved role | Expected SHA-256 | Fresh SHA-256 | Shape | Result |
|---|---|---|---|---|---|
| {BATCH.as_posix()} | Historical ML evidence | {BATCH_PIN} | {bh} | {bn} x {len(bcols)} | VERIFIED |
| {RECON.as_posix()} | Descriptive exploration only | {RECON_PIN} | {rh} | {len(recon)} x {len(recon[0])} | VERIFIED |

Molecular/source summary embeds the exact Batch021 input digest. Post1000 JSON lacks input_sha256; code/path and package sidecar link the adjacent Batch021 file, not a per-run digest.

| Combined Batch021 artifact | Actual SHA-256 | Sidecar SHA-256 | Result |
|---|---|---|---|
| post1000_model_comparison.csv | {pi['post1000_model_comparison.csv']['actual']} | {pi['post1000_model_comparison.csv']['expected']} | MISMATCH |
| post1000_fold_metrics.csv | {pi['post1000_fold_metrics.csv']['actual']} | {pi['post1000_fold_metrics.csv']['expected']} | MISMATCH |
| post1000_oof_predictions.csv | {pi['post1000_oof_predictions.csv']['actual']} | {pi['post1000_oof_predictions.csv']['expected']} | MISMATCH |

The JSON summary, Markdown report and all 21 per-model comparison/fold/OOF component files match their sidecars. Component and JSON metrics agree for all 21 rows; current combined comparison differs for {len(conflicts)}. The sidecar is a local checksum list, not a digital signature. The cause and intended output version are unestablished.

## Statistical methods and findings

After the Reconstruction hash gate, Python standard-library CSV parsing and arithmetic were used. Quartiles use linear interpolation; SD is sample SD; skewness is the unadjusted standardized third central moment; MAD is unscaled. These are descriptive statistics, not uncertainty intervals or inference.

### Descriptive distributions

{table(["Field","Valid n","Missing","Mean","Median","Sample SD","Q1","Q3","Min","Max","Skew"],nrows)}

ACR is stored target_value_percent using the documented 100 x C_cooked/C_raw equation. Raw and cooked concentration summaries pool mixed units/bases and have no common physical interpretation. Temperature_C has 438 nonblank values (578 missing); Cooking_Time_min has 810 (206 missing). RDKit descriptors are compound-level calculated fields repeated across observations, not independent measurements. Source-specific definitions were not re-adjudicated.

### Group support and clustering

{table(["Grouping field","Labels","Missing rows","Groups n<5","Groups n=5-9","Groups n>=10","Singleton groups"],grows2)}

The data have {doi['families']} DOI families, no blank DOI, and all families contain repeated rows. The largest family has {doi['largest']} rows; top three contribute {doi['top3_share']*100:.2f}%. Phase 3 documented 232 extra repeated DOI/compound/matrix/method contexts across 82 contexts. These are related rows, not established independent replicates. Compound/class labels include wording variants; no harmonization occurred.

### Missingness and outlier sensitivity

Blank counts: analytical_definition={miss['analytical_definition']}, reported_replicate_design={miss['reported_replicate_design']}, raw_sd={miss['raw_sd']}, cooked_sd={miss['cooked_sd']}, Temperature_C={miss['Temperature_C']}, Cooking_Time_min={miss['Cooking_Time_min']}. Phase 3 documented {units} concentration-unit labels and {len(bases)} basis labels, with {unspecified} basis labels classified as unspecified. Raw/cooked compatibility remains unestablished; no paired food masses or validated yield establish total-mass retention.

The Tukey upper fence is {hi:.6f}%; {high_flags} values exceed it. ACR is >100% in {gt100} rows and >1,000% in {gt1000}; cooked concentration is zero in {zero}. Flags are review prompts, not errors. The sensitivity excludes high flags from a summary only; it is not a corrected dataset. Phase 3's 118 strict target differences remain unresolved at source precision; all matched displayed precision, but source rounding was not verified.

### Inferential analysis and limitations

No significance tests were run. Independence, a valid sampling unit, source-level measurement compatibility, pairing, replicate uncertainty and multiplicity plan are not established. Uneven groups, source clustering, heterogeneous units/bases, missing definitions/replicate design/SD, possible pseudoreplication and unverified source precision block inference and causal claims. Descriptive differences are noncausal; no p-values were generated.

## Historical ML evidence reviewed

Reviewed saved Batch021 post1000 outputs and the molecular/source validation audit. The former includes Dummy median, Ridge, Random Forest, Extra Trees, Gradient Boosting, SVR-RBF and XGBoost comparison metrics, folds, OOF outputs, summary, report, code and full-data Extra-Trees feature importance. A targeted package-level check found no serialized .pkl/.joblib/.model/.ubj estimator. No model or validation script was executed.

The model-specific runner uses GroupKFold(5) by canonical_molecular_id, GroupKFold(5) by food_matrix, and LeaveOneGroupOut by DOI (32 source folds). Fixed settings are in the code: RF/ET 10 trees; GB 25; XGBoost 10; Ridge alpha 10; SVR C=10/epsilon=0.1; seed 42 where configured. No tuning trace was located. A second static run_post1000_evaluation.py contains different 75-estimator tree settings and writes the same combined file names. This is a plausible alternate writer path, not proven cause.

Checksum-matched per-model/summary source-held-out R2 values are all negative (range {min(jr):.6f} to {max(jr):.6f}); current combined values are also negative (range {min(ar):.6f} to {max(ar):.6f}). The component/summary view has highest R2 for XGBoost ({float(pjson['xgboost|leave_one_source_out']['r2']):.6f}); current combined CSV has highest R2 for Dummy median ({float(pagg['dummy_median|leave_one_source_out']['r2']):.6f}). The rankings differ. Do not compare/select across views. Post1000 values are pooled OOF metrics; mean-fold metrics were not derived.

The separate audit uses one ExtraTreesRegressor (25 trees, leaf=2, max_features=0.8, seed 42), five-fold GroupKFold and fold-local preprocessing. It distinguishes pooled R2 and mean-fold R2:

{table(["Strategy","Pooled OOF R2","Mean-fold R2 +/- SD","Pooled MAE","Pooled RMSE","Groups"],[
[molr["validation_strategy"],f"{molr['r2']:.6f}",f"{molr['mean_fold_r2']:.6f} +/- {molr['std_fold_r2']:.6f}",f"{molr['mae']:.6f}",f"{molr['rmse']:.6f}",f"{molr['n_molecular_groups']} molecular / {molr['n_source_groups']} DOI"],
[srcr["validation_strategy"],f"{srcr['r2']:.6f}",f"{srcr['mean_fold_r2']:.6f} +/- {srcr['std_fold_r2']:.6f}",f"{srcr['mae']:.6f}",f"{srcr['rmse']:.6f}",f"{srcr['n_molecular_groups']} molecular / {srcr['n_source_groups']} DOI"]])}

Molecular-grouped folds have zero molecular overlap but {min(source_overlap)}-{max(source_overlap)} DOI-family overlap. DOI-grouped folds have zero DOI overlap but {min(mol_overlap)}-{max(mol_overlap)} molecular-group overlap. They test different transfer questions. DOI holdout is not independent-laboratory holdout. Full-data feature importance is descriptive, not causal.

## Metric interpretation and leakage review

R2 is unitless; MAE/RMSE are target percentage points. Negative pooled OOF R2 describes residual variation relative to variation around the pooled target mean; it is not negative accuracy. Mean-fold R2 is distinct. Post1000 exact model values remain blocked by file-integrity/cross-file conflicts.

Reviewed feature lists exclude target_value_percent and cooked_concentration, so direct target-column leakage was not found in static code. The molecular/source audit includes raw_concentration, the target denominator; prediction-time availability is unspecified. Fold-local preprocessing is documented in code and saved audit. Tuning history, test reuse, exact complete row-level fold memberships, external source, temporal holdout, lab/site holdout and prospective deployment evidence are missing. Combined OOF lacks fold ID and fails its digest, so exact record-level leakage checks are blocked. No leakage PASS is claimed.

## What is supported

- **Historical evidence:** saved grouped Batch021 evaluations exist; the separate molecular/source audit embeds the exact Batch021 input hash; pooled and mean-fold metrics are separate.
- **Not independently reproduced:** model fits, predictions and metrics. No evaluation code was rerun.
- **Not supported:** positive unseen-source performance, external-lab transfer, temporal generalization, deployment, causal cooking effects, or total-mass retention from ACR.
- **Unresolved:** combined post1000 outputs fail their recorded digests and {len(conflicts)}/21 metric rows conflict; intended version and cause are unknown.

## Errors and corrections

- The initial package probe under Python 3.14 raised `ModuleNotFoundError: No module named 'pandas'`. This was an environment limitation. No dependency was installed; standard-library CSV, JSON, hashing and arithmetic were sufficient.
- A long inline command was rejected by the execution launcher with: `MXC launcher: The target executable 'C:\\Program Files\\WindowsApps\\OpenAI.CodexPrimaryRuntime.v26-1116-1220-0_26.1116.1220.0_x64__3k8sg7r9htsxt\\dependencies\\native\\powershell\\pwsh.exe' appears to be a packaged (MSIX) app. Packaged apps cannot be launched inside a sandboxed container. Uninstall the packaged version and install an unpackaged build.` No audit code ran from that command. It was replaced with a saved, scoped report helper and a short invocation; no software was installed or changed.
- The first helper run reported `FileExistsError: [WinError 183] Cannot create a file when that file already exists` for the new Phase 4 output directory. The helper file had already created its parent directory. The helper was corrected to accept its own directory and create it idempotently.
- The next helper run reported `NameError: name 'protocols' is not defined. Did you mean: 'protocol'?` in a new report-generation variable reference. The typo was corrected to the already-defined protocol map and the helper was rerun.
- A subsequent guard stopped with `Output reports already exist; refusing overwrite` after the previous run had written four partial Phase 4 CSVs. The directory was inspected; it contained only the new helper and those partial Phase 4 outputs. The guard was narrowed to allow only the helper and the seven explicitly named Phase 4 outputs; the incomplete report outputs were regenerated from the approved inputs. No pre-existing project evidence was touched.
- A later helper compile failed with SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2170-2171: truncated \\UXXXXXXXX escape. Cause: a Windows path in a normal triple-quoted log string was parsed as an escape. Correction: make the generated log a raw f-string and rerun.
- The next compile attempt reported SyntaxError: unterminated string literal (detected at line 527). Cause: captured traceback text contained a triple-quote delimiter that closed the generated log literal. Correction: replace the delimiter/caret excerpt with plain explanatory text.
- The following compile attempt reported IndentationError: unexpected indent at line 526. Cause: the caret line remained after replacing the embedded delimiter. Correction: replace the caret excerpt with plain text.
- Review of the first generated report found that a literal substring check counted one basis label containing the exact word “unspecified”, while Phase 3's broader documented classification is six labels. Cause: lexical counting did not reproduce Phase 3's semantic category. Correction: use and label the Phase 3 documented six-label classification; source data remain unchanged.
- Review also caught a draft statistical-table sentence that combined two different target comparisons. The first concerned 118 stored-target versus recalculated-ACR strict differences; the second concerned 15 Reconstruction/Batch021 serialized cells. The table text was separated and corrected; no input or historical output changed.
- The final helper execution completed. No further errors occurred.

## Unresolved gaps and safe next action

See ML_PROVENANCE_GAP_REGISTER.csv and VALIDATION_DESIGN_REVIEW.csv. The evidence owner must identify the intended combined-output version and explain the hash/metric divergence before exact comparative claims are used. Do not regenerate or replace historical outputs under this task. Scientific inference requires compatible source-level measurements, replicate uncertainty and an identified independent sampling unit.

## Conclusion

Phase 4 is **PARTIALLY COMPLETE**. Safe descriptive and named historical-evidence checks are completed, but inferential analysis is scientifically blocked and consolidated post1000 metrics are inconsistent with checksum-matched component evidence. Do not close this as a validated-performance review until artifact provenance and scientific gaps are addressed. This does not imply a metric is false; its intended version and interpretation are not established. No Phase 5 work started.
"""
    (OUT/"PHASE4_STATISTICAL_AND_ML_REVIEW.md").write_text(report,encoding="utf-8")

    final_r,final_b=digest(RECON),digest(BATCH)
    if final_r!=RECON_PIN or final_b!=BATCH_PIN: raise SystemExit("Dataset hash changed during report generation")
    log=fr"""# Phase 4 Execution Log

**Status:** PARTIALLY COMPLETE  
**Date:** 2026-11-20

## Work completed

- Read the required Phase 2 provenance report and Phase 3 ACR report, gap register, execution log and comparison outputs.
- Verified dataset pins before parsing: Batch021 {bh} (1,016 x 38); Reconstruction {rh} (1,016 x 43). Rechecked after generation: {final_b}; {final_r}; both still match.
- Computed Reconstruction descriptive statistics for ACR, concentration/process/replicate fields and RDKit numeric predictors, plus category support, missingness, DOI clustering and summary-only Tukey sensitivity using Python standard library.
- Reviewed only named Batch021 and molecular/source saved evidence; checked sidecars, embedded input linkage, fold/OOF schemas/counts, and static model/split/preprocessing code.
- Wrote seven required reports/registers and one supporting builder helper in the new Phase 4 folder. Existing project files were not changed.

## Historical integrity

- Batch021 input, post1000 JSON/Markdown, all 21 per-model comparison/fold/OOF components, and named molecular/source summary/fold/split/OOF/report match their sidecars where checked.
- Combined post1000 comparison/fold/OOF fail their recorded hashes. The combined metric comparison conflicts in {len(conflicts)}/21 rows. Cause is unknown.
- No historical artifact was edited, regenerated, retrained or replaced.

## Errors, root causes and corrections

1. Package probe traceback: `Traceback (most recent call last): File "<string>", line 1, in <module>; ModuleNotFoundError: No module named 'pandas'`. Cause: pandas is unavailable in the existing Python 3.14 interpreter. Classification: environment limitation. Correction: no installation; use Python standard-library parsing and arithmetic.
2. Long inline command error: `MXC launcher: target PowerShell executable was a packaged MSIX app and could not be launched inside the sandboxed container.` No audit code ran from that command. Classification: execution-launcher limitation. Correction: save the scoped report builder and invoke it with a short command; no software was installed or changed.
3. Initial helper traceback ended with `FileExistsError: [WinError 183] Cannot create a file when that file already exists`. Cause: the patch had already created the helper's parent directory. Classification: report-helper issue. Correction: make directory creation idempotent after verifying the directory contents.
4. Helper traceback ended with `NameError: name 'protocols' is not defined. Did you mean: 'protocol'?`. Cause: new helper variable-name typo. Classification: report-helper issue. Correction: reference the existing `prot` mapping and rerun.
5. Safety guard output: `Output reports already exist; refusing overwrite`. Cause: the previous failed run had created four partial Phase 4 CSVs. Classification: intentional overwrite guard, not a data error. Correction: inspect the folder, confirm it contained only this new helper and its partial outputs, then allow only the explicitly named Phase 4 outputs to be regenerated. The guard prevented writes during that attempt.
6. Helper compilation failed with SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2170-2171: truncated \UXXXXXXXX escape. Cause: a Windows path in a normal triple-quoted generated-log string. Classification: report-helper issue. Correction: use a raw f-string and rerun.
7. The next compile attempt ended with SyntaxError: unterminated string literal (detected at line 527). Cause: embedded triple-quote text closed the helper log literal. Correction: describe the source line without inserting a quote delimiter.
8. The following compile attempt ended with IndentationError: unexpected indent at line 526. Cause: a caret excerpt remained after replacing the quote delimiter. Correction: replace the caret excerpt with plain text.
9. Post-generation review found a basis-label classification discrepancy: the literal text count was 1 while Phase 3 documented 6 unspecified-basis labels. Cause: the lexical check did not match the documented semantic classification. Correction: preserve the Phase 3 value of 6 and label it as inherited documentation; no source data changed.
10. Post-generation review caught a draft sentence conflating the 118 stored-target/recalculated-ACR differences with the separate 15 Reconstruction/Batch021 target cells. Correction: describe the two comparisons separately; no scientific input changed.
11. Final helper run and CSV parsing completed successfully; no further errors occurred.

### Captured exception tracebacks

Pandas probe:

    Traceback (most recent call last):
      File "<string>", line 1, in <module>
    ModuleNotFoundError: No module named 'pandas'

First helper run:

    Traceback (most recent call last):
      File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 508, in <module>
        main()
      File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 146, in main
        OUT.mkdir(parents=True)
      File "C:\Python314\Lib\pathlib\__init__.py", line 1011, in mkdir
        os.mkdir(self, mode)
    FileExistsError: [WinError 183] Cannot create a file when that file already exists: 'research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20'

Second helper run:

    Traceback (most recent call last):
      File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 508, in <module>
        main()
      File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 312, in main
        evaluation_population=protocols[protocol]+"; pooled 1,016 OOF predictions",
    NameError: name 'protocols' is not defined. Did you mean: 'protocol'?

The launcher rejection had no Python traceback. The later output-directory guard was an intentional stop and printed its exact refusal message; it did not modify files during that attempt.

Compile-time error on the next attempt:

    File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 527
        SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2170-2171: truncated \UXXXXXXXX escape
                                                              ^
    SyntaxError: unterminated string literal (detected at line 527)

Compile-time error on the following attempt:

    File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 526
        ^^^
    IndentationError: unexpected indent

Compile-time error:

    File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 536
        [closing triple-quote delimiter; compiler caret was displayed here]
    SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2170-2171: truncated \UXXXXXXXX escape

## Verification

- Hash gates before and after: PASS.
- Expected shapes: PASS (Batch021 1,016 x 38; Reconstruction 1,016 x 43).
- Component/summary consistency: PASS, 21/21.
- Combined comparison consistency: FAIL, {len(conflicts)}/21 conflicting rows; preserved, not repaired.
- Combined comparison/fold/OOF sidecars: FAIL; component files and JSON/Markdown: PASS.
- Molecular/source input hash and named audit sidecars: PASS.
- Report CSV parsing: PASS; counts below.
- Training, predictions, metric recalculation, model build, validation rerun and dependency install: NOT PERFORMED.

## Boundaries

No Git writes; no Stage B/C/D access; no restricted catalog or Retention_Final source access; no application, dataset, registry, model, metric, dependency or lockfile edits. Writes are confined to this new Phase 4 report package.

## Required CSV parse counts
"""
    csv_names=["STATISTICAL_REVIEW_TABLE.csv","HISTORICAL_ML_EVIDENCE_REGISTER.csv","ML_PROVENANCE_GAP_REGISTER.csv",
               "VALIDATION_DESIGN_REVIEW.csv","METRIC_INTERPRETATION_REGISTER.csv"]
    counts={}
    for name in csv_names:
        with (OUT/name).open(encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f); rows=list(reader)
            if not reader.fieldnames or any(not h for h in reader.fieldnames) or any(None in r for r in rows):
                raise SystemExit(f"Invalid generated CSV: {name}")
            counts[name]=len(rows); log+=f"\n- {name}: PASS; {len(rows)} data rows."
    (OUT/"PHASE4_EXECUTION_LOG.md").write_text(log+"\n",encoding="utf-8")
    required=["PHASE4_STATISTICAL_AND_ML_REVIEW.md",*csv_names,"PHASE4_EXECUTION_LOG.md","phase4_report_builder.py"]
    for name in required:
        p=OUT/name
        if not p.is_file() or p.stat().st_size==0: raise SystemExit(f"Missing/empty file: {name}")
    print(json.dumps({"output_dir":str(OUT),"files":required,"csv_rows":counts,"metric_conflict_rows":len(conflicts),
                      "final_batch_hash":final_b,"final_reconstruction_hash":final_r,"status":"PARTIALLY COMPLETE"},indent=2))

if __name__=="__main__":
    main()
