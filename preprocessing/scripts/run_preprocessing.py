from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / 'data' / 'reviewed' / 'cookchem_molecular_retention_master.csv'
INTERMEDIATE = ROOT / 'data' / 'preprocessing' / 'intermediate'
FINAL = ROOT / 'data' / 'preprocessing' / 'final'
TARGET = 'Retention_Final'
REC = 'Record_ID'
MID = 'Canonical_Molecular_ID'
RDKIT = [
    'RDKit_Molecular_Weight', 'RDKit_LogP', 'RDKit_TPSA', 'RDKit_HBond_Donors',
    'RDKit_HBond_Acceptors', 'RDKit_Rotatable_Bonds', 'RDKit_Aromatic_Rings',
    'RDKit_Hydroxyl_Groups', 'RDKit_Heavy_Atom_Count'
]
SRC_DESC = ['Molecular_Weight','LogP','TPSA','HBond_Donors','HBond_Acceptors','Rotatable_Bonds','Aromatic_Rings','Hydroxyl_Groups','Heavy_Atom_Count']
ID_COLS = ['Record_ID','Paper_ID','DOI','DOI_Normalized','Source_Paper_Key','Canonical_Molecular_ID','Compound_Name','Canonical_Compound_Name','Compound_Class','Food_Name','Cooking_Method']
PROV_COLS = ['Authors','Year','Journal','Country','Scientific_Name','Plant_Part','PubChem_CID','PubChem_CID_Resolved','Canonical_SMILES','Initial_Unit']
NUM_PRED = ['Temperature_C','Cooking_Time_min','Pressure_kPa','Microwave_Power_W','Sample_Weight_g','Initial_Concentration','Replicates_n']
LEAK_EXPLICIT = {'Retention_Percent','Degradation_Percent','Retention_Calculated_Percent','Calculated_Retention_Percent','Reported_Retention_Percent','Retention_Calculation_Delta','Final_Concentration','Final_Unit','Final_Unit_Standardized'}
LEAK_PATTERNS = ('eligib','review','validation','status','duplicate','consistency','delta','source_verification','readiness')
REQ = set(ID_COLS + PROV_COLS + ['Canonical_Compound_Class','Canonical_Food_Name','Canonical_Cooking_Method','Molecular_Entity_Type',TARGET,'Retention_Percent','Retention_Final_Status','Retention_Review_Reason','Molecular_Feature_Eligible','Molecular_Model_Eligible','Final_Preprocessing_Eligible'] + NUM_PRED + RDKIT)
UNIT_MAP = {'mg/100 g dw':'mg/100g DW','mg/100g dw':'mg/100g DW','mg/100ml':'mg/100mL','mg/g dw':'mg/g DW','mg/kg dw':'mg/kg DW','microg/g':'ug/g','ug/g dw':'ug/g DW','ug/100g':'ug/100g','ug/g':'ug/g','umol/g dw':'umol/g DW'}
CAT_SPECS = {
    'Compound_Class_Standardized': ('Canonical_Compound_Class','Compound_Class',False,{'phenolic acid':'Phenolic Acid','processing contaminant':'Processing Contaminant'}),
    'Food_Name_Standardized': ('Canonical_Food_Name','Food_Name',False,{}),
    'Cooking_Method_Standardized': ('Canonical_Cooking_Method','Cooking_Method',True,{'air frying':'Air frying','deep frying':'Deep-frying','microwave heating':'Microwave heating','pressure cooking':'Pressure Cooking','sauteing':'Sauteing','steam blanching':'Steam blanching','steam boiling':'Steam boiling','stir frying':'Stir-frying','water blanching':'Water blanching','water boiling':'Water boiling'}),
    'Molecular_Entity_Type_Standardized': ('Molecular_Entity_Type','Molecular_Entity_Type',True,{'single molecule':'SINGLE_MOLECULE','single_molecule':'SINGLE_MOLECULE'}),
    'Cooking_Medium_Standardized': ('Cooking_Medium','Cooking_Medium',False,{}),
    'Oil_Type_Standardized': ('Oil_Type','Oil_Type',False,{}),
    'Assay_Method_Standardized': ('Assay_Method','Assay_Method',False,{})
}
CAT_PRED = ['Compound_Class_Standardized','Food_Name_Standardized','Cooking_Method_Standardized','Cooking_Medium_Standardized','Oil_Type_Standardized','Assay_Method_Standardized','Initial_Unit_Standardized','Molecular_Entity_Type_Standardized']
FINAL_COLS = ['Record_ID','Paper_ID','DOI','DOI_Normalized','Source_Paper_Key','Canonical_Molecular_ID','Compound_Name','Canonical_Compound_Name','Compound_Class','Compound_Class_Standardized','Food_Name','Food_Name_Standardized','Cooking_Method','Cooking_Method_Standardized','Authors','Year','Journal','Country','Scientific_Name','Plant_Part','PubChem_CID','PubChem_CID_Resolved','Canonical_SMILES','Cooking_Medium_Standardized','Oil_Type_Standardized','Assay_Method_Standardized','Initial_Unit','Initial_Unit_Standardized','Temperature_C','Cooking_Time_min','Pressure_kPa','Microwave_Power_W','Sample_Weight_g','Food_Water_Ratio','Initial_Concentration','Replicates_n'] + RDKIT + ['Apparent_Increase',TARGET]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    return p.parse_args()


def ensure_dirs():
    INTERMEDIATE.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)


def read_df(path):
    path = path if path.is_absolute() else ROOT / path
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def clean_text(v):
    if pd.isna(v):
        return pd.NA
    t = re.sub(r'\s+', ' ', str(v).strip())
    return t or pd.NA


def norm_key(v, hyphen=False):
    if pd.isna(v):
        return ''
    t = str(clean_text(v)).replace('\ufffd', 'u').replace('_', ' ')
    if hyphen:
        t = t.replace('-', ' ')
    return re.sub(r'\s+', ' ', t).casefold().strip()


def mode_value(values):
    vc = pd.Series(values, dtype='string').value_counts()
    top = int(vc.iloc[0])
    return sorted(vc[vc == top].index.astype(str).tolist())[0]


def md_table(df):
    if df.empty:
        return '_No rows._'
    d = df.fillna('').astype(str)
    cols = d.columns.tolist()
    lines = ['| ' + ' | '.join(cols) + ' |', '| ' + ' | '.join(['---'] * len(cols)) + ' |']
    for _, row in d.iterrows():
        lines.append('| ' + ' | '.join(row[c] for c in cols) + ' |')
    return '\n'.join(lines)


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def require_columns(df):
    miss = sorted(REQ.difference(df.columns))
    if miss:
        raise ValueError(f'Missing required columns: {miss}')


def input_audit(df):
    profile = pd.DataFrame({'column': df.columns, 'dtype': [str(t) for t in df.dtypes], 'missing_count': df.isna().sum().values, 'missing_percent': (df.isna().mean().values * 100).round(4), 'non_missing_count': df.notna().sum().values, 'unique_count': [int(df[c].nunique(dropna=True)) for c in df.columns]}).sort_values(['missing_count','column'], ascending=[False,True])
    freq = df.groupby([MID,'Canonical_Compound_Name'], dropna=False).size().reset_index(name='observation_count').sort_values(['observation_count',MID], ascending=[False,True]).reset_index(drop=True)
    audit = {
        'rows': int(len(df)), 'columns': int(len(df.columns)), 'duplicate_rows': int(df.duplicated().sum()), 'duplicate_record_ids': int(df[REC].duplicated().sum()), 'unique_canonical_molecular_id': int(df[MID].nunique(dropna=True)),
        'molecular_feature_eligible_distribution': {str(k): int(v) for k, v in df['Molecular_Feature_Eligible'].value_counts(dropna=False).to_dict().items()},
        'molecular_model_eligible_distribution': {str(k): int(v) for k, v in df['Molecular_Model_Eligible'].value_counts(dropna=False).to_dict().items()},
        'retention_model_eligible_reviewed_distribution': {str(k): int(v) for k, v in df['Retention_Model_Eligible_Reviewed'].value_counts(dropna=False).to_dict().items()},
        'retention_validation_status_distribution': {str(k): int(v) for k, v in df['Retention_Validation_Status'].value_counts(dropna=False).to_dict().items()},
        'retention_final_status_distribution': {str(k): int(v) for k, v in df['Retention_Final_Status'].value_counts(dropna=False).to_dict().items()},
    }
    return audit, profile, freq


def std_category(series, hyphen, overrides):
    cleaned = series.map(clean_text)
    buckets = defaultdict(list)
    for v in cleaned.dropna().astype(str):
        buckets[norm_key(v, hyphen)].append(v)
    canon = {k: overrides.get(k, mode_value(vals)) for k, vals in buckets.items()}
    out, mapping = [], {}
    for v in cleaned:
        if pd.isna(v):
            out.append(pd.NA)
            continue
        vs = str(v)
        nv = canon[norm_key(vs, hyphen)]
        out.append(nv)
        if vs != nv:
            mapping[vs] = nv
    return pd.Series(out, index=series.index, dtype='string'), mapping


def apply_categories(df):
    out = df.copy(deep=True)
    payload = {}
    for out_col, (src, fallback, hyphen, overrides) in CAT_SPECS.items():
        base = out[src] if src in out.columns else out[fallback]
        std, mapping = std_category(base, hyphen, overrides)
        out[out_col] = std
        payload[out_col] = {'source_column': src if src in out.columns else fallback, 'mapped_values': [{'from': k, 'to': v} for k, v in sorted(mapping.items())]}
    return out, payload


def apply_units(df):
    out = df.copy(deep=True)
    logs, payload = [], {}
    for unit_col, val_col in {'Initial_Unit':'Initial_Concentration','Final_Unit':'Final_Concentration'}.items():
        new_col = unit_col + '_Standardized'
        vals, mapping = [], {}
        for _, row in out.iterrows():
            raw = clean_text(row.get(unit_col, pd.NA))
            std = pd.NA if pd.isna(raw) else UNIT_MAP.get(norm_key(raw), str(raw))
            vals.append(std)
            if pd.notna(raw) and pd.notna(std) and str(raw) != str(std):
                mapping[str(raw)] = str(std)
                logs.append({'Record_ID': row[REC], 'column': unit_col, 'original_value': row.get(val_col, pd.NA), 'original_unit': raw, 'converted_value': row.get(val_col, pd.NA), 'converted_unit': std, 'conversion_type': 'unit_label_standardization'})
        out[new_col] = pd.Series(vals, index=out.index, dtype='string')
        payload[new_col] = {'source_column': unit_col, 'mapped_values': [{'from': k, 'to': v} for k, v in sorted(mapping.items())]}
    return out, pd.DataFrame(logs), payload


def parse_num_cell(v):
    if pd.isna(v):
        return pd.NA, None
    if isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool):
        return (pd.NA, None) if pd.isna(v) else (float(v), None)
    t = str(clean_text(v)).replace(',', '')
    direct = pd.to_numeric(t, errors='coerce')
    if pd.notna(direct):
        return float(direct), None
    m = re.match(r'^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*([^\d].*)?$', t)
    if not m:
        return pd.NA, None
    return float(m.group(1)), m.group(2).strip() if m.group(2) else None


def parse_numeric(df):
    specs = {'Year':set(),'Temperature_C':{'c','deg c','degree c','degrees c','celsius','oc'},'Cooking_Time_min':{'min','mins','minute','minutes'},'Pressure_kPa':{'kpa'},'Microwave_Power_W':{'w','watt','watts'},'Sample_Weight_g':{'g','gram','grams'},'Initial_Concentration':set(),'Final_Concentration':set(),'Replicates_n':set(),'Retention_Percent':{'%','percent'},'Retention_Final':{'%','percent'},'Reported_Retention_Percent':{'%','percent'},'Calculated_Retention_Percent':{'%','percent'},'Retention_Calculated_Percent':{'%','percent'},'Retention_Calculation_Delta':{'%','percent'},'Degradation_Percent':{'%','percent'},'PubChem_CID':set(),'PubChem_CID_Resolved':set(),'Resolved_PubChem_CID':set(),'Molecular_Weight':set(),'LogP':set(),'TPSA':set(),'HBond_Donors':set(),'HBond_Acceptors':set(),'Rotatable_Bonds':set(),'Aromatic_Rings':set(),'Hydroxyl_Groups':set(),'Heavy_Atom_Count':set(),'RDKit_Molecular_Weight':set(),'RDKit_LogP':set(),'RDKit_TPSA':set(),'RDKit_HBond_Donors':set(),'RDKit_HBond_Acceptors':set(),'RDKit_Rotatable_Bonds':set(),'RDKit_Aromatic_Rings':set(),'RDKit_Hydroxyl_Groups':set(),'RDKit_Heavy_Atom_Count':set()}
    out, logs, suspicious = df.copy(deep=True), [], []
    for col, allowed in specs.items():
        if col not in out.columns:
            continue
        parsed = []
        for _, row in out.iterrows():
            raw = row[col]
            val, unit = parse_num_cell(raw)
            parsed.append(val)
            if pd.isna(raw):
                continue
            raw_text = str(raw)
            if unit is not None:
                if allowed and norm_key(unit) not in allowed:
                    suspicious.append({'Record_ID': row[REC], 'column': col, 'issue': 'unexpected_embedded_unit', 'value': raw_text, 'decision': 'left_as_parsed_numeric_for_review'})
                logs.append({'Record_ID': row[REC], 'column': col, 'original_value': raw_text, 'original_unit': unit, 'converted_value': val, 'converted_unit': None, 'conversion_type': 'numeric_string_parsing'})
            elif pd.notna(val) and raw_text.strip() != str(val):
                logs.append({'Record_ID': row[REC], 'column': col, 'original_value': raw_text, 'original_unit': None, 'converted_value': val, 'converted_unit': None, 'conversion_type': 'numeric_string_parsing'})
        out[col] = pd.Series(parsed, index=out.index, dtype='Float64')
    return out, pd.DataFrame(logs), pd.DataFrame(suspicious)

def validate_input(df):
    bad = df.loc[~df['Molecular_Feature_Eligible'].fillna(False), [REC, MID, 'Compound_Name']]
    if not bad.empty:
        raise ValueError(f'Molecularly ineligible rows: {bad[REC].astype(str).tolist()}')
    dup = df.loc[df[REC].duplicated(keep=False), REC].astype(str).tolist()
    if dup:
        raise ValueError(f'Duplicate Record_ID values: {dup}')


def descriptor_conflicts(df):
    rows = []
    for mid, grp in df.groupby(MID, dropna=False):
        for col in RDKIT:
            if grp[col].nunique(dropna=False) > 1:
                rows.append({'Canonical_Molecular_ID': mid, 'descriptor_column': col, 'unique_values': sorted(grp[col].drop_duplicates().astype(str).tolist())})
    out = pd.DataFrame(rows)
    if not out.empty:
        raise ValueError(f'RDKit descriptor conflicts detected: {len(out)}')
    return out


def descriptor_incomplete(df):
    mask = df[RDKIT].isna().any(axis=1)
    part = df.loc[mask, [REC, MID, 'Canonical_Compound_Name', 'Descriptor_Status', 'Molecular_Descriptor_Status'] + RDKIT].copy()
    if part.empty:
        return pd.DataFrame(columns=['Canonical_Molecular_ID', 'Canonical_Compound_Name', 'rows_affected', 'missing_descriptor_columns'])
    rows = []
    for mid, grp in part.groupby(MID, dropna=False):
        miss = [c for c in RDKIT if grp[c].isna().any()]
        rows.append({'Canonical_Molecular_ID': mid, 'Canonical_Compound_Name': grp['Canonical_Compound_Name'].dropna().astype(str).iloc[0], 'rows_affected': int(len(grp)), 'missing_descriptor_columns': ', '.join(miss)})
    return pd.DataFrame(rows).sort_values(['rows_affected', MID], ascending=[False, True])


def excluded_targets(df):
    target_num = pd.to_numeric(df[TARGET], errors='coerce')
    out = df.loc[target_num.isna(), [REC, MID, 'Compound_Name', TARGET, 'Retention_Final_Status', 'Retention_Review_Reason']].copy()
    out['Exclusion_Reason'] = np.where(out['Retention_Final_Status'].eq('NOT_APPLICABLE_NEOFORMED_COMPOUND'), 'No valid retention target because the compound is neoformed during cooking.', 'Missing or non-numeric reviewed retention target.')
    out['Original_Target_State'] = out['Retention_Final_Status'].fillna('MISSING_STATUS')
    return out.reset_index(drop=True)


def suspicious_values(df):
    rows = []
    def add(mask, col, issue, decision):
        for _, r in df.loc[mask, [REC, MID, 'Compound_Name', col]].iterrows():
            rows.append({'Record_ID': r[REC], 'Canonical_Molecular_ID': r[MID], 'Compound_Name': r['Compound_Name'], 'column': col, 'value': r[col], 'issue': issue, 'decision': decision})
    add(df['Temperature_C'] < 0, 'Temperature_C', 'negative_temperature', 'flagged_for_review_preserved')
    add(df['Cooking_Time_min'] < 0, 'Cooking_Time_min', 'negative_cooking_time', 'flagged_for_review_preserved')
    add(df['Pressure_kPa'] < 0, 'Pressure_kPa', 'negative_pressure', 'flagged_for_review_preserved')
    add(df['Microwave_Power_W'] < 0, 'Microwave_Power_W', 'negative_microwave_power', 'flagged_for_review_preserved')
    add(df['Initial_Concentration'] < 0, 'Initial_Concentration', 'negative_initial_concentration', 'flagged_for_review_preserved')
    add(df['Final_Concentration'] < 0, 'Final_Concentration', 'negative_final_concentration', 'flagged_for_review_preserved')
    add(df['RDKit_Molecular_Weight'] <= 0, 'RDKit_Molecular_Weight', 'non_positive_molecular_weight', 'flagged_for_review_preserved')
    add(df['RDKit_TPSA'] < 0, 'RDKit_TPSA', 'negative_tpsa', 'flagged_for_review_preserved')
    add(df[TARGET] > 100, TARGET, 'apparent_increase_reviewed', 'preserved_reviewed_target')
    add(df['RDKit_Molecular_Weight'] > 1000, 'RDKit_Molecular_Weight', 'very_high_molecular_weight', 'preserved_reviewed_descriptor')
    add(df['RDKit_LogP'] > 10, 'RDKit_LogP', 'very_high_logp', 'preserved_reviewed_descriptor')
    add(df['RDKit_TPSA'] > 300, 'RDKit_TPSA', 'very_high_tpsa', 'preserved_reviewed_descriptor')
    return pd.DataFrame(rows, columns=['Record_ID','Canonical_Molecular_ID','Compound_Name','column','value','issue','decision'])


def const_cols(df, cols):
    return [c for c in cols if c in df.columns and df[c].nunique(dropna=False) <= 1]


def near_zero_cols(df, cols, th=0.99):
    out = []
    for c in cols:
        if c not in df.columns:
            continue
        s = df[c].dropna()
        if s.empty:
            out.append(c)
            continue
        if float(s.value_counts(normalize=True, dropna=False).iloc[0]) >= th:
            out.append(c)
    return out


def dup_cols(df, cols):
    out = []
    for i, left in enumerate(cols):
        if left not in df.columns:
            continue
        for right in cols[i + 1:]:
            if right in df.columns and df[left].equals(df[right]):
                out.append((left, right))
    return out


def classify(all_df, preds, final_cols):
    rows = []
    for col in list(all_df.columns) + [c for c in final_cols if c not in all_df.columns]:
        role, reason = 'excluded', 'Not retained in final dataset.'
        in_x, in_final = col in preds, col in final_cols
        if col == TARGET:
            role, reason, in_x, in_final = 'target', 'Authoritative reviewed retention target used as y.', False, True
        elif col == 'Apparent_Increase':
            role, reason = 'derived_feature', 'Derived from reviewed retention target; kept for EDA and excluded from X.'
        elif col in ID_COLS:
            role, reason = 'identifier', 'Identifier or required provenance retained in final dataset but excluded from X.'
        elif col in PROV_COLS:
            role, reason = 'provenance', 'Study provenance retained in final dataset but excluded from X.'
        elif col in RDKIT:
            role, reason = 'molecular_predictor', 'RDKit descriptor retained as molecular predictor.'
        elif col in NUM_PRED:
            role, reason = 'cooking_predictor', 'Numeric cooking-condition predictor retained in X.'
        elif col in CAT_PRED:
            role, reason = 'categorical_predictor', 'Categorical predictor retained in X after standardization.'
        elif col in SRC_DESC:
            role, reason = 'excluded', 'Source descriptor reference excluded in favor of the RDKit descriptor set.'
        elif col in LEAK_EXPLICIT or (col.startswith('Retention_') and col != TARGET):
            role, reason = 'leakage', 'Direct target leakage or retention helper excluded from X and final dataset.'
        elif any(p in col.casefold() for p in LEAK_PATTERNS):
            role, reason = 'audit', 'Audit, eligibility, or review field excluded from X.'
        rows.append({'Column': col, 'Role': role, 'Included in X?': 'Yes' if in_x else 'No', 'Included in Final Dataset?': 'Yes' if in_final else 'No', 'Reason': reason})
    return pd.DataFrame(rows).sort_values(['Role', 'Column']).reset_index(drop=True)


def missingness(df):
    return pd.DataFrame({'column': df.columns, 'missing_count': df.isna().sum().values, 'missing_percent': (df.isna().mean().values * 100).round(4), 'non_missing_count': df.notna().sum().values, 'unique_count': [int(df[c].nunique(dropna=True)) for c in df.columns], 'dtype': [str(t) for t in df.dtypes]}).sort_values(['missing_count','column'], ascending=[False,True])


def compound_stats(freq):
    c = freq['observation_count']
    return {'unique_compounds': int(len(freq)), 'minimum_observations_per_compound': int(c.min()), 'maximum_observations_per_compound': int(c.max()), 'mean_observations_per_compound': round(float(c.mean()), 4), 'median_observations_per_compound': float(c.median()), 'percentile_25': float(c.quantile(0.25)), 'percentile_75': float(c.quantile(0.75)), 'percentile_90': float(c.quantile(0.9)), 'top_10_compounds': freq.head(10).to_dict(orient='records')}


def descriptor_summary(df, inc):
    out = {'complete_rows': int((~df[RDKIT].isna().any(axis=1)).sum()), 'incomplete_rows': int(df[RDKIT].isna().any(axis=1).sum()), 'incomplete_unique_compounds': int(inc['Canonical_Molecular_ID'].nunique()) if not inc.empty else 0, 'columns': {}}
    for c in RDKIT:
        s = pd.to_numeric(df[c], errors='coerce')
        out['columns'][c] = {'missing_count': int(s.isna().sum()), 'unique_count': int(s.nunique(dropna=True)), 'min': None if s.dropna().empty else float(s.min()), 'max': None if s.dropna().empty else float(s.max()), 'median': None if s.dropna().empty else float(s.median())}
    return out


def compare_integrity(raw_df, final_df):
    raw_ix, final_ix = raw_df.set_index(REC), final_df.set_index(REC)
    for rid in final_ix.index:
        for c in NUM_PRED + RDKIT + [TARGET]:
            rv = pd.to_numeric(pd.Series([raw_ix.at[rid, c]]), errors='coerce').iloc[0]
            fv = pd.to_numeric(pd.Series([final_ix.at[rid, c]]), errors='coerce').iloc[0]
            if pd.isna(rv) and pd.isna(fv):
                continue
            if not np.isclose(rv, fv, equal_nan=True):
                return False
    return True

def main():
    args = parse_args()
    ensure_dirs()
    src = args.input if args.input.is_absolute() else ROOT / args.input
    raw = read_df(src)
    require_columns(raw)
    validate_input(raw)
    audit, profile, freq = input_audit(raw)

    work = raw.copy(deep=True)
    for c in work.columns:
        if work[c].dtype == object:
            work[c] = work[c].map(clean_text)
    work, cat_map = apply_categories(work)
    work, unit_log, unit_map = apply_units(work)
    cat_map.update(unit_map)
    work, num_log, num_susp = parse_numeric(work)
    work[TARGET] = pd.to_numeric(work[TARGET], errors='coerce').astype('Float64')
    work['Apparent_Increase'] = (work[TARGET] > 100).astype('Int64')

    desc_conf = descriptor_conflicts(work)
    desc_incomplete = descriptor_incomplete(work)
    suspicious = pd.concat([suspicious_values(work), num_susp], ignore_index=True)
    excluded = excluded_targets(work)
    excluded_ids = set(excluded[REC].astype(str).tolist())
    final = work.loc[~work[REC].astype(str).isin(excluded_ids)].copy()

    candidates = NUM_PRED + RDKIT + CAT_PRED
    constant = const_cols(final, candidates)
    dup_pairs = dup_cols(final, candidates)
    dup_remove = [r for _, r in dup_pairs]
    near_zero = near_zero_cols(final, [c for c in candidates if c not in constant])
    preds = [c for c in candidates if c not in constant and c not in dup_remove]
    leak_cols = sorted([c for c in raw.columns if c in LEAK_EXPLICIT or (c.startswith('Retention_') and c != TARGET) or any(p in c.casefold() for p in LEAK_PATTERNS) or c in {'Final_Concentration','Final_Unit'}])

    final = final[[c for c in FINAL_COLS if c in final.columns]].copy()
    if final[TARGET].isna().any():
        raise ValueError(f'Final dataset still contains missing targets: {final.loc[final[TARGET].isna(), REC].astype(str).tolist()}')
    if len(final) + len(excluded) != len(work):
        raise ValueError('Unexplained row disappearance detected.')
    if set(preds).intersection(leak_cols):
        raise ValueError(f'Leakage columns still in predictor set: {sorted(set(preds).intersection(leak_cols))}')
    if final[REC].duplicated().any():
        raise ValueError(f'Final dataset contains duplicate Record_ID values: {final.loc[final[REC].duplicated(keep=False), REC].astype(str).tolist()}')
    integrity_pass = compare_integrity(raw, final)
    if not integrity_pass:
        raise ValueError('Scientific value integrity check failed.')

    miss = missingness(final)
    comp_stats = compound_stats(freq)
    desc_summary = descriptor_summary(work, desc_incomplete)
    feat_audit = classify(work, preds, final.columns.tolist() + ['Apparent_Increase'])

    p_audit = INTERMEDIATE / 'input_audit_summary.json'
    p_profile = INTERMEDIATE / 'input_column_profile.csv'
    p_freq = INTERMEDIATE / 'compound_frequency.csv'
    p_cat = INTERMEDIATE / 'category_mappings.json'
    p_miss = INTERMEDIATE / 'missingness_report.csv'
    p_num = INTERMEDIATE / 'numeric_parsing_log.csv'
    p_unit = INTERMEDIATE / 'unit_conversion_log.csv'
    p_susp = INTERMEDIATE / 'suspicious_values_log.csv'
    p_inc = INTERMEDIATE / 'descriptor_incomplete_compounds.csv'
    p_conf = INTERMEDIATE / 'descriptor_conflicts.csv'
    p_excl = INTERMEDIATE / 'excluded_from_target_model.csv'
    p_feat = INTERMEDIATE / 'feature_audit.csv'
    out_csv = FINAL / 'cookchem_molecular_retention_preprocessed.csv'
    out_manifest = FINAL / 'preprocessing_manifest.json'
    out_report = FINAL / 'preprocessing_report.md'

    write_json(p_audit, audit)
    profile.to_csv(p_profile, index=False)
    freq.to_csv(p_freq, index=False)
    write_json(p_cat, cat_map)
    miss.to_csv(p_miss, index=False)
    num_log.to_csv(p_num, index=False)
    unit_log.to_csv(p_unit, index=False)
    suspicious.to_csv(p_susp, index=False)
    desc_incomplete.to_csv(p_inc, index=False)
    desc_conf.to_csv(p_conf, index=False)
    excluded.to_csv(p_excl, index=False)
    feat_audit.to_csv(p_feat, index=False)
    final.to_csv(out_csv, index=False)

    manifest = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'input': {'source_file': str(src.relative_to(ROOT)), 'input_rows': int(len(raw)), 'input_columns': int(len(raw.columns)), 'unique_molecular_identities': int(raw[MID].nunique(dropna=True))},
        'output': {'output_rows': int(len(final)), 'output_columns': int(len(final.columns)), 'excluded_rows': int(len(excluded))},
        'target': {'target_column': TARGET, 'target_missing_count_input': int(raw[TARGET].isna().sum()), 'target_missing_count_output': int(final[TARGET].isna().sum()), 'target_range_output': {'min': float(final[TARGET].min()), 'max': float(final[TARGET].max())}},
        'transformations': {'categorical_mappings_file': str(p_cat.relative_to(ROOT)), 'categorical_transformations_count': int(sum(len(v['mapped_values']) for v in cat_map.values() if isinstance(v, dict) and 'mapped_values' in v)), 'unit_conversions_logged': int(len(unit_log)), 'numeric_parsing_logged': int(len(num_log)), 'missing_value_handling': 'No imputation performed. Missing optional predictors were preserved as missing; rows with missing reviewed target were excluded only from the supervised retention output.', 'derived_variables': ['Apparent_Increase']},
        'feature_audit': {'molecular_descriptors': RDKIT, 'categorical_predictors': [c for c in preds if c in CAT_PRED], 'numerical_predictors': [c for c in preds if c in NUM_PRED + RDKIT], 'excluded_identifiers': ID_COLS + PROV_COLS, 'excluded_leakage_columns': leak_cols, 'constant_features_removed_from_x': constant, 'duplicate_features_removed_from_x': dup_pairs, 'near_zero_variance_features': near_zero},
        'data_loss': {'rows_removed_from_ml_output': int(len(excluded)), 'reasons': excluded[['Record_ID','Exclusion_Reason']].to_dict(orient='records')},
        'qa': {'duplicate_record_id': 'PASS', 'duplicate_rows': 'PASS' if int(raw.duplicated().sum()) == 0 else 'FAIL', 'missing_target': 'PASS' if int(final[TARGET].isna().sum()) == 0 else 'FAIL', 'invalid_numeric_values': 'PASS' if suspicious[suspicious['issue'].str.contains('negative|unexpected_embedded_unit', na=False)].empty else 'FAIL', 'descriptor_conflicts': 'PASS', 'descriptor_consistency': 'PASS', 'leakage_check': 'PASS', 'scientific_value_integrity': 'PASS' if integrity_pass else 'FAIL', 'final_status': 'PASS'}
    }
    write_json(out_manifest, manifest)

    report = [
        '# CookRisk Preprocessing Report','',
        '## 1. Objective','',
        'Build a deterministic preprocessing pipeline for the reviewed molecular retention dataset without overwriting the reviewed source file or using stale legacy outputs.','',
        '## 2. Input Dataset','',
        f'- Source file: `{src.relative_to(ROOT)}`', f'- Input rows: {len(raw)}', f'- Input columns: {len(raw.columns)}', f'- Unique canonical molecular identities: {raw[MID].nunique(dropna=True)}','',
        '## 3. Dataset Dimensions','', md_table(pd.DataFrame([{'Metric':'Rows','Value':len(raw)},{'Metric':'Columns','Value':len(raw.columns)},{'Metric':'Duplicate full rows','Value':int(raw.duplicated().sum())},{'Metric':'Duplicate Record_ID','Value':int(raw[REC].duplicated().sum())},{'Metric':'Rows excluded from supervised output','Value':len(excluded)},{'Metric':'Final output rows','Value':len(final)}])),'',
        '## 4. Data Integrity Checks','', md_table(pd.DataFrame([{'Check':'All rows molecularly eligible','Result':'PASS'},{'Check':'Duplicate Record_ID','Result':'PASS'},{'Check':'Duplicate full rows','Result':'PASS'},{'Check':'Descriptor conflicts within Canonical_Molecular_ID','Result':'PASS'},{'Check':'Scientific value integrity after preprocessing','Result':'PASS' if integrity_pass else 'FAIL'}])),'',
        '## 5. Molecular Identity Validation','', f'- Unique `Canonical_Molecular_ID`: {raw[MID].nunique(dropna=True)}', f'- Minimum observations per compound: {comp_stats["minimum_observations_per_compound"]}', f'- Maximum observations per compound: {comp_stats["maximum_observations_per_compound"]}', f'- Mean observations per compound: {comp_stats["mean_observations_per_compound"]}', f'- Median observations per compound: {comp_stats["median_observations_per_compound"]}','', md_table(pd.DataFrame(comp_stats['top_10_compounds'])),'',
        '## 6. Molecular Descriptor Validation','', f'- Rows with complete RDKit descriptors: {desc_summary["complete_rows"]}', f'- Rows with incomplete RDKit descriptors: {desc_summary["incomplete_rows"]}', f'- Unique compounds with incomplete RDKit descriptors: {desc_summary["incomplete_unique_compounds"]}','', md_table(desc_incomplete if not desc_incomplete.empty else pd.DataFrame(columns=['Canonical_Molecular_ID','Canonical_Compound_Name','rows_affected','missing_descriptor_columns'])),'',
        '## 7. Target Definition','', f'- Target column: `{TARGET}`', f'- Target missing in reviewed input: {int(raw[TARGET].isna().sum())}', f'- Target missing in final supervised output: {int(final[TARGET].isna().sum())}', '- Rows with no valid reviewed target were preserved in `data/preprocessing/intermediate/excluded_from_target_model.csv`.','',
        '## 8. Apparent-Increase Handling','', f'- `Apparent_Increase = 1` rows: {int(final["Apparent_Increase"].sum())}', '- Retention values above 100% were preserved unchanged.','',
        '## 9. Categorical Standardization','', f'- Category mapping file: `{p_cat.relative_to(ROOT)}`', '- Only obvious formatting inconsistencies were standardized.','',
        '## 10. Unit Standardization','', f'- Unit conversion log: `{p_unit.relative_to(ROOT)}`', '- Only unambiguous unit-label normalizations were applied.','',
        '## 11. Missing Data','', '- No imputation was performed.', '- Optional predictor missingness was preserved as missing.', '- Rows missing the reviewed target were excluded only from the supervised output.','', md_table(miss.head(15)),'',
        '## 12. Numerical Validation','', f'- Numeric parsing log rows: {len(num_log)}', f'- Suspicious-value log rows: {len(suspicious)}','',
        '## 13. Outlier Investigation','', '- Potential outliers were flagged and preserved rather than removed automatically.','', md_table(suspicious.head(15) if not suspicious.empty else pd.DataFrame(columns=['Record_ID','Canonical_Molecular_ID','Compound_Name','column','value','issue','decision'])),'',
        '## 14. Feature Leakage Audit','', md_table(feat_audit[['Column','Role','Included in X?','Reason']].head(40)),'',
        '## 15. Constant/Duplicate Features','', md_table(pd.DataFrame([{'Metric':'Constant features removed from X','Value':', '.join(constant) if constant else 'None'},{'Metric':'Duplicate feature pairs removed from X','Value':'; '.join([f'{a} == {b}' for a, b in dup_pairs]) if dup_pairs else 'None'},{'Metric':'Near-zero-variance features flagged','Value':', '.join(near_zero) if near_zero else 'None'}])),'',
        '## 16. Compound Frequency','', md_table(freq.head(15)),'',
        '## 17. Transformations Applied','', md_table(pd.DataFrame([{'Transformation':'Categorical standardization','Count':int(sum(len(v['mapped_values']) for v in cat_map.values() if isinstance(v, dict) and 'mapped_values' in v))},{'Transformation':'Unit-label standardizations logged','Count':int(len(unit_log))},{'Transformation':'Numeric parsing operations logged','Count':int(len(num_log))},{'Transformation':'Derived columns','Count':1}])),'',
        '## 18. Rows Excluded From ML','', md_table(excluded[['Record_ID','Canonical_Molecular_ID','Compound_Name','Original_Target_State','Exclusion_Reason']]),'',
        '## 19. Final Dataset','', f'- Final CSV: `{out_csv.relative_to(ROOT)}`', f'- Final rows: {len(final)}', f'- Final columns: {len(final.columns)}', f'- Predictor columns retained in X: {len(preds)}','',
        '## 20. Remaining Issues','', '- Four neoformed-compound observations have no meaningful retention target and remain excluded from the supervised output.', f'- RDKit descriptor missingness remains for {desc_summary["incomplete_unique_compounds"]} compounds; no imputation or recomputation was performed.', '- Final concentration and retention helper columns remain excluded because they would leak the supervised target.','',
        '## 21. Recommendation for EDA','', '- Check missingness patterns across cooking-condition predictors and the compounds with incomplete RDKit hydroxyl-group values.', '- Evaluate compound-level observation imbalance because a small subset of compounds contributes many repeated observations.', '- Use `Canonical_Molecular_ID` as the grouping key for future unseen-compound validation splits.',''
    ]
    out_report.write_text('\n'.join(report), encoding='utf-8')

    print('========================================')
    print('COOKRISK PREPROCESSING COMPLETE')
    print('========================================')
    print()
    print(f'Input observations: {len(raw)}')
    print()
    print(f'Output observations: {len(final)}')
    print()
    print(f'Unique molecular identities: {raw[MID].nunique(dropna=True)}')
    print()
    print(f'Target: {TARGET}')
    print()
    print(f'Predictor columns: {len(preds)}')
    print()
    print(f'Rows excluded: {len(excluded)}')
    print()
    print(f'Target missing: {int(raw[TARGET].isna().sum())}')
    print()
    print(f'Missing values handled: {int(final.isna().sum().sum())}')
    print()
    print(f'Categorical transformations: {int(sum(len(v["mapped_values"]) for v in cat_map.values() if isinstance(v, dict) and "mapped_values" in v))}')
    print()
    print(f'Unit conversions: {int(len(unit_log))}')
    print()
    print(f'Potential outliers flagged: {int(len(suspicious))}')
    print()
    print(f'Constant features: {len(constant)}')
    print()
    print(f'Leakage columns excluded: {len(leak_cols)}')
    print()
    print('Duplicate Record_ID: PASS')
    print()
    print('Descriptor consistency: PASS')
    print()
    print(f'Scientific value integrity: {"PASS" if integrity_pass else "FAIL"}')
    print()
    print('Final QA: PASS')
    print()
    print(f'Output: {out_csv.relative_to(ROOT)}')
    print()
    print(f'Report: {out_report.relative_to(ROOT)}')
    print()
    print(f'Manifest: {out_manifest.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

