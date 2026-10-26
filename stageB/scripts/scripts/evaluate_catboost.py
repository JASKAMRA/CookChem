"""Stage B, step 5: categorical/missingness-aware CatBoost under molecular GroupKFold."""
from pathlib import Path
import sys
import math
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import PowerTransformer

ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parent
sys.path.insert(0,str(ROOT/"scripts")); from evaluate_missingness_features import augmented_features
sys.path.insert(0,str(REPO/"stageA"/"scripts")); import run_stage_a as stage_a

def score(y,p): return {"MAE":float(mean_absolute_error(y,p)),"RMSE":float(math.sqrt(mean_squared_error(y,p))),"R2":float(r2_score(y,p))}

def prepare(x):
    x=x.copy(); cats=[c for c in x.columns if c in stage_a.CATEGORICAL]
    for c in cats: x[c]=x[c].fillna("Missing").astype(str)
    return x,cats

def main():
    out=ROOT/"outputs"; out.mkdir(exist_ok=True)
    df=pd.read_csv(REPO/"stageA"/"input"/"cookchem_molecular_retention_preprocessed.csv")
    x,cats=prepare(augmented_features(df)); y=df.Retention_Final.to_numpy(float); groups=df.Canonical_Molecular_ID.astype(str).to_numpy()
    rows=[]; foldrows=[]; oofs=[]
    for transform in ["log1p","yeo_johnson"]:
        oof=np.full(len(df),np.nan)
        for fold,(tr,va) in enumerate(GroupKFold(n_splits=5).split(x,y,groups),1):
            if set(groups[tr]).intersection(groups[va]): raise RuntimeError("Molecular leakage")
            if transform=="log1p": train_y=np.log1p(y[tr]); inverse=lambda p:np.expm1(np.clip(p,-20,20))
            else:
                power=PowerTransformer(method="yeo-johnson",standardize=True); train_y=power.fit_transform(y[tr].reshape(-1,1)).ravel(); inverse=lambda p:power.inverse_transform(np.asarray(p).reshape(-1,1)).ravel()
            model=CatBoostRegressor(iterations=450,depth=5,learning_rate=.04,l2_leaf_reg=8,loss_function="RMSE",random_seed=42,thread_count=1,verbose=False,allow_writing_files=False)
            model.fit(x.iloc[tr],train_y,cat_features=cats); pred=np.maximum(inverse(model.predict(x.iloc[va])),0); oof[va]=pred
            foldrows.append({"Model":f"CatBoost_{transform}","Fold":fold,"n":len(va),**score(y[va],pred)})
        rows.append({"Model":f"CatBoost_{transform}",**score(y,oof)}); oofs.append(pd.DataFrame({"Model":f"CatBoost_{transform}","Record_ID":df.Record_ID,"Canonical_Molecular_ID":groups,"actual":y,"predicted":oof}))
    results=pd.DataFrame(rows); ref=pd.read_csv(out/"stageB_step3_tail_aware_results.csv").query("Model == 'ExtraTrees_YeoJohnson'").iloc[0]
    for m in ["MAE","RMSE","R2"]: results[f"Delta_{m}_vs_current_best"]=results[m]-ref[m]
    results.to_csv(out/"stageB_step5_catboost_results.csv",index=False); pd.DataFrame(foldrows).to_csv(out/"stageB_step5_catboost_fold_results.csv",index=False); pd.concat(oofs).to_csv(out/"stageB_step5_catboost_oof_predictions.csv",index=False)
    print(results.to_string(index=False))

if __name__=="__main__": main()
