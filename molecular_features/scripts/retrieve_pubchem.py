from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

CACHE_COLUMNS = ["compound_name_input", "normalized_lookup_name", "pubchem_cid", "canonical_smiles", "molecular_formula", "molecular_weight_pubchem", "retrieval_status", "retrieval_timestamp", "error_message"]
PROPERTY_FIELDS = "CanonicalSMILES,MolecularFormula,MolecularWeight"
PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

def normalize_lookup_name(value: Any) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().lower().split())

def first_unique_nonmissing(series: pd.Series) -> Any:
    values = [v for v in series.dropna().unique().tolist() if str(v).strip()]
    if len(values) == 1:
        return values[0]
    return pd.NA

def collect_unique_compounds(df: pd.DataFrame) -> pd.DataFrame:
    name_col = "Compound_Name_Standardized" if "Compound_Name_Standardized" in df.columns else "Compound_Name"
    rows = []
    for normalized_name, group in df.groupby(df[name_col].map(normalize_lookup_name), dropna=False):
        if not normalized_name:
            continue
        original_names = sorted({str(v).strip() for v in group["Compound_Name"].dropna() if str(v).strip()})
        standard_names = sorted({str(v).strip() for v in group[name_col].dropna() if str(v).strip()})
        primary = standard_names[0] if standard_names else original_names[0]
        rows.append({
            "Compound_Key": "compound_" + urllib.parse.quote(normalized_name, safe="").replace("%", "_"),
            "Compound_Name": primary,
            "Original_Compound_Names": " | ".join(original_names),
            "normalized_lookup_name": normalized_name,
            "Existing_PubChem_CID": first_unique_nonmissing(group.get("PubChem_CID", pd.Series(dtype="object"))),
            "Existing_SMILES": first_unique_nonmissing(group.get("SMILES", pd.Series(dtype="object"))),
            "Existing_Molecular_Formula": first_unique_nonmissing(group.get("Molecular_Formula", pd.Series(dtype="object"))),
            "Existing_Molecular_Weight": first_unique_nonmissing(group.get("Molecular_Weight", pd.Series(dtype="object"))),
            "Observation_Count": int(len(group)),
        })
    return pd.DataFrame(rows).sort_values("Compound_Name").reset_index(drop=True)

def read_pubchem_cache(cache_path: Path) -> pd.DataFrame:
    cache = pd.read_csv(cache_path) if cache_path.exists() else pd.DataFrame(columns=CACHE_COLUMNS)
    for col in CACHE_COLUMNS:
        if col not in cache.columns:
            cache[col] = pd.NA
    cache["normalized_lookup_name"] = cache["normalized_lookup_name"].map(normalize_lookup_name)
    return cache[CACHE_COLUMNS].drop_duplicates("normalized_lookup_name", keep="last")

def write_pubchem_cache(cache: pd.DataFrame, cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache[CACHE_COLUMNS].drop_duplicates("normalized_lookup_name", keep="last").to_csv(cache_path, index=False)

def pubchem_json(url: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "CookChem-BTP/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def retrieve_from_pubchem(name: str, timeout: int = 12, delay_seconds: float = 0.25) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    normalized = normalize_lookup_name(name)
    try:
        cid_payload = pubchem_json(f"{PUBCHEM_BASE}/compound/name/{urllib.parse.quote(name)}/cids/JSON", timeout)
        cids = cid_payload.get("IdentifierList", {}).get("CID", [])
        if not cids:
            status, err = "not_found", ""
            cid = smiles = formula = mw = pd.NA
        elif len(cids) > 1:
            status, err = "ambiguous", f"Multiple PubChem CIDs returned: {cids[:10]}"
            cid = smiles = formula = mw = pd.NA
        else:
            time.sleep(delay_seconds)
            cid = cids[0]
            props = pubchem_json(f"{PUBCHEM_BASE}/compound/cid/{cid}/property/{PROPERTY_FIELDS}/JSON", timeout).get("PropertyTable", {}).get("Properties", [{}])[0]
            smiles = props.get("CanonicalSMILES", pd.NA)
            formula = props.get("MolecularFormula", pd.NA)
            mw = props.get("MolecularWeight", pd.NA)
            status, err = "retrieved", ""
    except urllib.error.HTTPError as exc:
        status, err = ("not_found" if exc.code == 404 else "api_error"), f"HTTPError {exc.code}: {exc.reason}"
        cid = smiles = formula = mw = pd.NA
    except Exception as exc:
        status, err = "api_error", str(exc)
        cid = smiles = formula = mw = pd.NA
    return {"compound_name_input": name, "normalized_lookup_name": normalized, "pubchem_cid": cid, "canonical_smiles": smiles, "molecular_formula": formula, "molecular_weight_pubchem": mw, "retrieval_status": status, "retrieval_timestamp": timestamp, "error_message": err}

def resolve_pubchem_identities(compounds: pd.DataFrame, cache_path: Path, enable_pubchem: bool = True, timeout: int = 12, delay_seconds: float = 0.25):
    cache = read_pubchem_cache(cache_path)
    cache_by_name = {r["normalized_lookup_name"]: r.to_dict() for _, r in cache.iterrows()}
    rows, new_cache = [], []
    retrieval_attempts = 0
    cache_hits = 0
    api_blocked = False
    for _, compound in compounds.iterrows():
        row = compound.to_dict()
        key = row["normalized_lookup_name"]
        if pd.notna(row.get("Existing_PubChem_CID")) or pd.notna(row.get("Existing_SMILES")):
            retrieval = {"compound_name_input": row["Compound_Name"], "normalized_lookup_name": key, "pubchem_cid": row.get("Existing_PubChem_CID"), "canonical_smiles": row.get("Existing_SMILES"), "molecular_formula": row.get("Existing_Molecular_Formula"), "molecular_weight_pubchem": pd.NA, "retrieval_status": "already_present", "retrieval_timestamp": datetime.now(timezone.utc).isoformat(), "error_message": ""}
        elif key in cache_by_name and cache_by_name[key].get("retrieval_status") != "api_error":
            retrieval = cache_by_name[key]
            cache_hits += 1
        elif not enable_pubchem or api_blocked:
            retrieval = {"compound_name_input": row["Compound_Name"], "normalized_lookup_name": key, "pubchem_cid": pd.NA, "canonical_smiles": pd.NA, "molecular_formula": pd.NA, "molecular_weight_pubchem": pd.NA, "retrieval_status": "manual_review_required", "retrieval_timestamp": datetime.now(timezone.utc).isoformat(), "error_message": "PubChem retrieval unavailable or disabled."}
        else:
            retrieval_attempts += 1
            retrieval = retrieve_from_pubchem(row["Compound_Name"], timeout, delay_seconds)
            if retrieval["retrieval_status"] == "api_error":
                api_blocked = True
        new_cache.append(retrieval)
        row.update({"PubChem_CID": retrieval["pubchem_cid"], "SMILES": retrieval["canonical_smiles"], "Molecular_Formula": retrieval["molecular_formula"], "Molecular_Weight_PubChem": retrieval["molecular_weight_pubchem"], "Molecular_Identity_Status": retrieval["retrieval_status"], "PubChem_Retrieval_Status": retrieval["retrieval_status"], "PubChem_Error_Message": retrieval["error_message"]})
        rows.append(row)
    updated = pd.concat([cache, pd.DataFrame(new_cache)], ignore_index=True)
    write_pubchem_cache(updated, cache_path)
    return pd.DataFrame(rows), read_pubchem_cache(cache_path), {"pubchem_retrieval_attempts": retrieval_attempts, "pubchem_cache_hits": cache_hits}
