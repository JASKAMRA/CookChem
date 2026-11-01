"""Stage B, step 4: test whether extreme retention is predictable from inputs alone."""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import average_precision_score, brier_score_loss, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_missingness_features import augmented_features
sys.path.insert(0, str(REPO / "stageA" / "scripts"))
import run_stage_a as stage_a


def main():
    out = ROOT / "outputs"; out.mkdir(exist_ok=True)
    df = pd.read_csv(REPO / "stageA" / "input" / "cookchem_molecular_retention_preprocessed.csv")
    threshold = float(df.Retention_Final.quantile(.99))
    y = (df.Retention_Final >= threshold).astype(int).to_numpy()
    groups = df[stage_a.GROUP].astype(str).to_numpy(); x = augmented_features(df)
    oof = np.zeros(len(df)); fold_rows=[]
    for fold, (tr, va) in enumerate(GroupKFold(n_splits=5).split(x, y, groups), 1):
        if set(groups[tr]).intersection(groups[va]): raise RuntimeError("Molecular leakage")
        model = Pipeline([("preprocess", stage_a.preprocessor(x.columns.tolist())), ("classifier", ExtraTreesClassifier(n_estimators=500, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=1))])
        model.fit(x.iloc[tr], y[tr]); prob=model.predict_proba(x.iloc[va])[:,1]; oof[va]=prob
        pred=(prob>=.5).astype(int); pr,rc,f1,_=precision_recall_fscore_support(y[va], pred, average="binary", zero_division=0)
        fold_rows.append({"Fold":fold,"n":len(va),"extreme_n":int(y[va].sum()),"PR_AUC":average_precision_score(y[va],prob),"ROC_AUC":roc_auc_score(y[va],prob),"precision_at_0.5":pr,"recall_at_0.5":rc,"f1_at_0.5":f1})
    pred=(oof>=.5).astype(int); pr,rc,f1,_=precision_recall_fscore_support(y,pred,average="binary",zero_division=0)
    summary={"threshold":threshold,"n":len(df),"extreme_n":int(y.sum()),"prevalence":float(y.mean()),"OOF_PR_AUC":float(average_precision_score(y,oof)),"OOF_ROC_AUC":float(roc_auc_score(y,oof)),"OOF_Brier":float(brier_score_loss(y,oof)),"precision_at_0.5":float(pr),"recall_at_0.5":float(rc),"f1_at_0.5":float(f1)}
    pd.DataFrame(fold_rows).to_csv(out / "stageB_step4_extreme_classifier_fold_results.csv",index=False)
    pd.DataFrame({"Record_ID":df.Record_ID,"Canonical_Molecular_ID":groups,"actual_extreme":y,"extreme_probability":oof,"prediction_at_0.5":pred}).to_csv(out / "stageB_step4_extreme_classifier_oof.csv",index=False)
    (out / "stageB_step4_extreme_detectability.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__": main()
