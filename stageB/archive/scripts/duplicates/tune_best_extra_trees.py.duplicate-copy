"""Stage B, step 6: nested grouped tuning of the current best Extra Trees recipe."""
from pathlib import Path
import sys, json, math
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, ParameterGrid
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer
from sklearn.compose import TransformedTargetRegressor

ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parent
sys.path.insert(0,str(ROOT/"scripts")); from evaluate_missingness_features import augmented_features
sys.path.insert(0,str(REPO/"stageA"/"scripts")); import run_stage_a as stage_a

def score(y,p): return {"MAE":float(mean_absolute_error(y,p)),"RMSE":float(math.sqrt(mean_squared_error(y,p))),"R2":float(r2_score(y,p))}
def pipe(columns, params):
    model=ExtraTreesRegressor(random_state=42,n_jobs=1,n_estimators=300,**params)
    return Pipeline([("preprocess",stage_a.preprocessor(columns)),("model",TransformedTargetRegressor(regressor=model,transformer=PowerTransformer(method="yeo-johnson",standardize=True)))])
def main():
    out=ROOT/"outputs"; out.mkdir(exist_ok=True); df=pd.read_csv(REPO/"stageA"/"input"/"cookchem_molecular_retention_preprocessed.csv")
    x=augmented_features(df); y=df.Retention_Final.to_numpy(float); g=df.Canonical_Molecular_ID.astype(str).to_numpy(); outer=GroupKFold(n_splits=5)
    grid=list(ParameterGrid({"min_samples_leaf":[1,2,4],"max_features":[1.0,0.7],"max_depth":[None]})); oof=np.full(len(df),np.nan); tuning=[]; folds=[]
    for fold,(tr,va) in enumerate(outer.split(x,y,g),1):
        candidates=[]; inner=GroupKFold(n_splits=3)
        for params in grid:
            scores=[]
            for it,iv in inner.split(x.iloc[tr],y[tr],g[tr]):
                train=tr[it]; valid=tr[iv]; m=pipe(x.columns.tolist(),params); m.fit(x.iloc[train],y[train]); scores.append(score(y[valid],np.maximum(m.predict(x.iloc[valid]),0)))
            row={"outer_fold":fold,"params":json.dumps(params,sort_keys=True),"inner_MAE":float(np.mean([s['MAE'] for s in scores])),"inner_RMSE":float(np.mean([s['RMSE'] for s in scores])),"inner_R2":float(np.mean([s['R2'] for s in scores]))}; candidates.append(row); tuning.append(row)
        chosen=sorted(candidates,key=lambda r:(r['inner_RMSE'],r['inner_MAE'],-r['inner_R2']))[0]; params=json.loads(chosen['params']); m=pipe(x.columns.tolist(),params); m.fit(x.iloc[tr],y[tr]); pred=np.maximum(m.predict(x.iloc[va]),0); oof[va]=pred; folds.append({"Fold":fold,"n":len(va),"params":chosen['params'],**score(y[va],pred)})
    total=score(y,oof); baseline=pd.read_csv(out/"stageB_step3_tail_aware_results.csv").query("Model=='ExtraTrees_YeoJohnson'").iloc[0]; result={"Model":"ExtraTrees_YeoJohnson_nested_tuned",**total,**{f"Delta_{m}":total[m]-baseline[m] for m in ['MAE','RMSE','R2']}}
    pd.DataFrame([result]).to_csv(out/"stageB_step6_tuned_results.csv",index=False); pd.DataFrame(folds).to_csv(out/"stageB_step6_fold_results.csv",index=False); pd.DataFrame(tuning).to_csv(out/"stageB_step6_tuning_log.csv",index=False); pd.DataFrame({"Record_ID":df.Record_ID,"Canonical_Molecular_ID":g,"actual":y,"predicted":oof}).to_csv(out/"stageB_step6_oof_predictions.csv",index=False); print(pd.DataFrame([result]).to_string(index=False))
if __name__=='__main__': main()
