"""Assemble an organized, deduplicated StageB_Final package from immutable V12."""
import csv, hashlib, json, shutil, sys
from pathlib import Path

if len(sys.argv) not in (3,4):
    raise SystemExit('usage: python consolidate_final.py <release_v12> <StageB_Final> [--internal]')
SRC, DST = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
INTERNAL=len(sys.argv)==4 and sys.argv[3]=='--internal'
if not SRC.is_dir(): raise SystemExit(f'V12 source not found: {SRC}')
if DST.exists() and any(DST.iterdir()): raise SystemExit(f'destination must be absent or empty: {DST}')
DST.mkdir(parents=True, exist_ok=True)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p, rows, fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    if fields is None: fields=list(rows[0]) if rows else []
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def copy(src_rel,dst_rel):
    s=SRC/src_rel; d=DST/dst_rel; d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,d)
    return d

# One canonical, unversioned copy of every current Stage B data table.
canonical={
 'outputs/compound_registry_v12.csv':'data/compound_registry.csv',
 'outputs/stageB_food_drug_interactions_v12.csv':'data/interaction_evidence.csv',
 'outputs/drug_probe_registry_v12.csv':'data/drug_probe_registry.csv',
 'outputs/study_registry_v12.csv':'data/study_registry.csv',
 'outputs/source_bibliography_v12.csv':'data/publication_bibliography.csv',
 'outputs/warning_resolution_ledger_v12.csv':'data/warning_ledger.csv',
 'outputs/cooking_retention_evidence_v9.csv':'data/cooking_retention_evidence.csv',
 'outputs/identity_structure_audit_v12.csv':'identity/identity_structure_audit.csv',
 'outputs/selection_decisions_v12.csv':'provenance/selection_decisions.csv',
 'outputs/candidate_screening_log_v12.csv':'provenance/candidate_screening_log.csv',
 'outputs/source_audit_v12.csv':'provenance/source_audit.csv',
 'outputs/claim_support_and_verification_v12.csv':'provenance/claim_support_and_verification.csv',
 'sources/source_register_v12.csv':'provenance/source_register.csv',
 'outputs/v12_food_context_audit.csv':'provenance/food_context_audit.csv',
 'outputs/v12_change_log.csv':'history/v12_change_log.csv',
}
seen={}; disposition=[]
for s,d in canonical.items():
    out=copy(s,d); h=sha(out); seen.setdefault(h,d)
    disposition.append({'V12_relative_path':s,'Final_path':d,'SHA256':h,'Disposition':'Canonical current dataset or audit copy'})

# Preserve the principal handoffs while making the final handoff the entry point.
docs={
 'reports/V12_HANDOFF.md':'documentation/history/V12_HANDOFF.md',
 'reports/V11_HANDOFF.md':'documentation/history/V11_HANDOFF.md',
 'reports/v11_test_plan.md':'documentation/history/V11_test_plan.md',
 'README_V12.md':'documentation/history/README_V12.md',
 'README_V11.md':'documentation/history/README_V11.md',
 'README_V10.md':'documentation/history/README_V10.md',
 'README_V9.md':'documentation/history/README_V9.md',
 'V10_HANDOFF.md':'documentation/history/V10_HANDOFF.md',
 'reports/CookRisk_StageB_V8_Handoff.pdf':'documentation/history/V8_HANDOFF.pdf',
 'SHA256SUMS_V12.json':'history/SHA256SUMS_V12.json',
}
for s,d in docs.items():
    if (SRC/s).exists():
        out=copy(s,d);h=sha(out);seen.setdefault(h,d)
        disposition.append({'V12_relative_path':s,'Final_path':d,'SHA256':h,'Disposition':'Historical handoff or V12 source manifest'})

# Preserve all non-identical V12 supporting files exactly once. Original paths
# are recorded for traceability; the original V12 release remains untouched.
skip=set(canonical)|set(docs)|{'SHA256SUMS_V12.json'}
for p in sorted(x for x in SRC.rglob('*') if x.is_file()):
    rel=p.relative_to(SRC).as_posix()
    if rel in skip: continue
    h=sha(p)
    if h in seen:
        disposition.append({'V12_relative_path':rel,'Final_path':seen[h],'SHA256':h,'Disposition':'Exact duplicate represented by the first identical file'})
        continue
    if rel.startswith(('sources/','inherited_sources/')):
        area='provenance/source_archive'
    elif rel.startswith('inherited_audits/'):
        area='history/inherited_audits'
    elif rel.startswith('inputs/'):
        area='history/inputs'
    elif rel.startswith('audit/rebuild_check/'):
        area='history/rebuild_artifacts'
    elif rel.startswith('audit/'):
        area='validation/audit'
    elif rel.startswith('reports/'):
        area='documentation/history/reports'
    elif rel.startswith('outputs/'):
        area='history/previous_outputs'
    else:
        area='history/support_archive'
    dest=f'{area}/{h}_{p.name}'
    out=DST/dest;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
    seen[h]=dest
    disposition.append({'V12_relative_path':rel,'Final_path':dest,'SHA256':h,'Disposition':'Unique V12 artifact retained verbatim'})
write_csv(DST/'history/v12_file_disposition.csv',disposition)

# Reconcile version counts from the actual release tables where the releases
# expose the relevant files. Report-only legacy figures are kept separate.
base=SRC.parent
release_specs=[
 ('V2','expansion_v2','stageB_food_drug_interactions_expanded.csv','compound_registry.csv'),
 ('V3','expansion_v3_20261014','stageB_food_drug_interactions_v3.csv','compound_registry.csv'),
 ('V4','release_v4_20261014','stageB_food_drug_interactions_v4.csv','compound_registry.csv'),
 ('V5','release_v5_20261014','stageB_food_drug_interactions_v5.csv','compound_registry.csv'),
 ('V6','release_v6_20261014','stageB_food_drug_interactions_v6.csv','compound_registry.csv'),
 ('V7','release_v7_20261014','stageB_food_drug_interactions_v7.csv','compound_registry.csv'),
 ('V7-clean','release_v7_20261015_clean','stageB_food_drug_interactions_v7.csv','compound_registry.csv'),
 ('V8','release_v8_20261015_quality','stageB_food_drug_interactions_v8.csv','compound_registry.csv'),
 ('V9','release_v9_20261029','stageB_food_drug_interactions_v9.csv','compound_registry_v9.csv'),
 ('V10','release_v10_20261030','stageB_food_drug_interactions_v10.csv','compound_registry_v10.csv'),
 ('V11','release_v11_20261030','stageB_food_drug_interactions_v11.csv','compound_registry_v11.csv'),
 ('V12','release_v12_20261030','stageB_food_drug_interactions_v12.csv','compound_registry_v12.csv'),
]
counts=[]
for ver,folder,evname,cmpname in release_specs:
    root=base/folder; evp=root/'outputs'/evname; cp=root/'outputs'/cmpname
    # V7/V8 used the shorter release schema names in their final tables.
    if not evp.exists():
        hits=list((root/'outputs').glob('stageB_food_drug_interactions*.csv')) if (root/'outputs').exists() else []
        evp=hits[-1] if hits else evp
    if not cp.exists():
        hits=list((root/'outputs').glob('compound_registry*.csv')) if (root/'outputs').exists() else []
        cp=hits[-1] if hits else cp
    e=read_csv(evp) if evp.exists() else []
    c=read_csv(cp) if cp.exists() else []
    if ver=='V2' and not c:
        summary=root/'outputs/evidence_summary.json'
        if summary.exists():
            anchor_total=json.loads(summary.read_text(encoding='utf-8')).get('unique_anchor_compounds',0)
            counts.append({'Release':ver,'Directory':folder,'Anchor_rows':anchor_total,'Evidence_rows':len(e),
              'Distinct_anchor_IDs':0,'Distinct_evidence_IDs':len({x.get('Evidence_ID','') for x in e if x.get('Evidence_ID')}),
              'Evidence_file':str(evp.relative_to(root)).replace('\\','/'),
              'Anchor_file':'','Counts_from':'V2 release summary; no compound registry available'})
            continue
    counts.append({'Release':ver,'Directory':folder,'Anchor_rows':len(c),'Evidence_rows':len(e),
      'Distinct_anchor_IDs':len({x.get('Compound_ID','') for x in c if x.get('Compound_ID')}),
      'Distinct_evidence_IDs':len({x.get('Evidence_ID','') for x in e if x.get('Evidence_ID')}),
      'Evidence_file':str(evp.relative_to(root)).replace('\\','/') if evp.exists() else '',
      'Anchor_file':str(cp.relative_to(root)).replace('\\','/') if cp.exists() else '',
      'Counts_from':'Underlying release CSVs' if e and c else 'No matching tables found; see source release summary'})
write_csv(DST/'history/release_counts_recalculated.csv',counts)

# Exact row-level change inventory across the comparable V9–V12 core tables.
comparable=[('V9','release_v9_20261029','compound_registry_v9.csv','stageB_food_drug_interactions_v9.csv'),
 ('V10','release_v10_20261030','compound_registry_v10.csv','stageB_food_drug_interactions_v10.csv'),
 ('V11','release_v11_20261030','compound_registry_v11.csv','stageB_food_drug_interactions_v11.csv'),
 ('V12','release_v12_20261030','compound_registry_v12.csv','stageB_food_drug_interactions_v12.csv')]
diff=[]; prev=None
for ver,folder,cn,en in comparable:
    root=base/folder
    c=read_csv(root/'outputs'/cn);e=read_csv(root/'outputs'/en)
    current={'compound':{x.get('Compound_ID',''):x for x in c if x.get('Compound_ID')},'evidence':{x.get('Evidence_ID',''):x for x in e if x.get('Evidence_ID')}}
    if prev:
        for kind in ('compound','evidence'):
            a,b=prev[kind],current[kind]
            for ident in sorted(b.keys()-a.keys()):diff.append({'From':prev['version'],'To':ver,'Entity':kind,'Stable_ID':ident,'Change':'introduced','Changed_fields':''})
            for ident in sorted(a.keys()-b.keys()):diff.append({'From':prev['version'],'To':ver,'Entity':kind,'Stable_ID':ident,'Change':'removed; inspect source release before interpreting','Changed_fields':''})
            for ident in sorted(a.keys()&b.keys()):
                fields=[k for k in sorted(set(a[ident])|set(b[ident])) if a[ident].get(k,'')!=b[ident].get(k,'')]
                if fields:diff.append({'From':prev['version'],'To':ver,'Entity':kind,'Stable_ID':ident,'Change':'corrected_or_reclassified','Changed_fields':'|'.join(fields)})
    prev={'version':ver,**current}
write_csv(DST/'history/cross_release_record_diff_v9_v12.csv',diff)

# Check every available earlier evidence registry against V12 by stable ID;
# compare V2 compound names because that export has no compound registry.
legacy_evidence=[('V2','expansion_v2','stageB_food_drug_interactions_expanded.csv'),('V3','expansion_v3_20261014','stageB_food_drug_interactions_v3.csv'),('V4','release_v4_20261014','stageB_food_drug_interactions_v4.csv'),('V5','release_v5_20261014','stageB_food_drug_interactions_v5.csv'),('V6','release_v6_20261014','stageB_food_drug_interactions_v6.csv'),('V7','release_v7_20261014','stageB_food_drug_interactions_v7.csv'),('V7-clean','release_v7_20261015_clean','stageB_food_drug_interactions_v7.csv'),('V8','release_v8_20261015_quality','stageB_food_drug_interactions_v8.csv'),('V9','release_v9_20261029','stageB_food_drug_interactions_v9.csv'),('V10','release_v10_20261030','stageB_food_drug_interactions_v10.csv'),('V11','release_v11_20261030','stageB_food_drug_interactions_v11.csv')]
final_e={x.get('Evidence_ID',''):x for x in read_csv(DST/'data/interaction_evidence.csv') if x.get('Evidence_ID','')}
final_c=read_csv(DST/'data/compound_registry.csv');final_c_by_id={x.get('Compound_ID',''):x for x in final_c if x.get('Compound_ID','')}
legacy_recon=[]
for ver,folder,fn in legacy_evidence:
    root=base/folder; rows=read_csv(root/'outputs'/fn); by={x.get('Evidence_ID',''):x for x in rows if x.get('Evidence_ID','')}
    missing=sorted(set(by)-set(final_e)); common=set(by)&set(final_e); exact=[i for i in common if by[i]==final_e[i]]
    changed=[i for i in common if by[i]!=final_e[i]]; fields={}
    for i in changed:
        for fld in set(by[i])|set(final_e[i]):
            if by[i].get(fld,'')!=final_e[i].get(fld,''):fields[fld]=fields.get(fld,0)+1
    legacy_recon.append({'Release':ver,'Entity':'Evidence','Source_rows':len(rows),'Stable_IDs_found_in_V12':len(common),'Missing_from_V12':len(missing),'Exact_row_matches':len(exact),'Common_rows_with_field_differences':len(changed),'Changed_fields':'|'.join(f'{k}:{v}' for k,v in sorted(fields.items())),'Disposition':'All stable IDs retained; field differences listed for review.' if not missing else 'Missing IDs require review.'})
for ver,folder,fn in [('V3','expansion_v3_20261014','compound_registry.csv'),('V4','release_v4_20261014','compound_registry.csv'),('V5','release_v5_20261014','compound_registry.csv'),('V6','release_v6_20261014','compound_registry.csv'),('V7','release_v7_20261014','compound_registry.csv'),('V7-clean','release_v7_20261015_clean','compound_registry.csv'),('V8','release_v8_20261015_quality','compound_registry.csv'),('V9','release_v9_20261029','compound_registry_v9.csv'),('V10','release_v10_20261030','compound_registry_v10.csv'),('V11','release_v11_20261030','compound_registry_v11.csv')]:
    rows=read_csv(base/folder/'outputs'/fn);by={x.get('Compound_ID',''):x for x in rows if x.get('Compound_ID','')};missing=sorted(set(by)-set(final_c_by_id));common=set(by)&set(final_c_by_id);exact=[i for i in common if by[i]==final_c_by_id[i]];changed=[i for i in common if by[i]!=final_c_by_id[i]];fields={}
    for i in changed:
        for fld in set(by[i])|set(final_c_by_id[i]):
            if by[i].get(fld,'')!=final_c_by_id[i].get(fld,''):fields[fld]=fields.get(fld,0)+1
    legacy_recon.append({'Release':ver,'Entity':'Compound','Source_rows':len(rows),'Stable_IDs_found_in_V12':len(common),'Missing_from_V12':len(missing),'Exact_row_matches':len(exact),'Common_rows_with_field_differences':len(changed),'Changed_fields':'|'.join(f'{k}:{v}' for k,v in sorted(fields.items())),'Disposition':'All stable IDs retained; schema/metadata differences listed for review.' if not missing else 'Missing IDs require review.'})
v2=read_csv(base/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv')
v2names={x.get('Compound','').strip().casefold() for x in v2 if x.get('Compound','').strip()}
aliases={n.casefold() for c in final_c for n in [c.get('Canonical_Name','')]+c.get('Aliases','').split('|') if n.strip()}
legacy_recon.append({'Release':'V2','Entity':'Compound_Name','Source_rows':len(v2names),'Stable_IDs_found_in_V12':sum(x in aliases for x in v2names),'Missing_from_V12':sum(x not in aliases for x in v2names),'Exact_row_matches':'not comparable; V2 has no compound registry','Common_rows_with_field_differences':'','Changed_fields':'','Disposition':'Name/alias check only; V2 has no stable compound IDs.'})
write_csv(DST/'history/legacy_release_record_reconciliation.csv',legacy_recon)

# Adjacent-version record diffs attribute introductions and field changes to
# the transition where they first appear, rather than only comparing endpoints.
seq_specs=[('V2','expansion_v2','stageB_food_drug_interactions_expanded.csv',None),('V3','expansion_v3_20261014','stageB_food_drug_interactions_v3.csv','compound_registry.csv'),('V4','release_v4_20261014','stageB_food_drug_interactions_v4.csv','compound_registry.csv'),('V5','release_v5_20261014','stageB_food_drug_interactions_v5.csv','compound_registry.csv'),('V6','release_v6_20261014','stageB_food_drug_interactions_v6.csv','compound_registry.csv'),('V7','release_v7_20261014','stageB_food_drug_interactions_v7.csv','compound_registry.csv'),('V7-clean','release_v7_20261015_clean','stageB_food_drug_interactions_v7.csv','compound_registry.csv'),('V8','release_v8_20261015_quality','stageB_food_drug_interactions_v8.csv','compound_registry.csv'),('V9','release_v9_20261029','stageB_food_drug_interactions_v9.csv','compound_registry_v9.csv'),('V10','release_v10_20261030','stageB_food_drug_interactions_v10.csv','compound_registry_v10.csv'),('V11','release_v11_20261030','stageB_food_drug_interactions_v11.csv','compound_registry_v11.csv'),('V12','release_v12_20261030','stageB_food_drug_interactions_v12.csv','compound_registry_v12.csv')]
snapshots=[]
for ver,folder,en,cn in seq_specs:
    root=base/folder; evrows=read_csv(root/'outputs'/en); e={x.get('Evidence_ID',''):x for x in evrows if x.get('Evidence_ID','')}
    c={}
    if cn and (root/'outputs'/cn).exists():c={x.get('Compound_ID',''):x for x in read_csv(root/'outputs'/cn) if x.get('Compound_ID','')}
    snapshots.append({'version':ver,'evidence':e,'compound':c})
transition_rows=[];transition_summary=[]
for old,newer in zip(snapshots,snapshots[1:]):
    for kind in ('evidence','compound'):
        a,b=old[kind],newer[kind]
        if not a or not b:
            transition_summary.append({'From':old['version'],'To':newer['version'],'Entity':kind.title(),'Previous_rows':len(a) if a else 'not available','Current_rows':len(b) if b else 'not available','Introduced':'not comparable','Removed':'not comparable','Common_changed':'not comparable','Common_exact':'not comparable','Numeric_outcomes_changed':'not comparable','Verification_fields_changed':'not comparable','Identity_fields_changed':'not comparable','Note':'Stable-ID table not available in one version; V2 has no compound registry.'})
            continue
        introduced=sorted(b.keys()-a.keys());removed=sorted(a.keys()-b.keys());common=a.keys()&b.keys();changed=[];num=verif=identity=0
        for key in sorted(common):
            fields=[fld for fld in sorted(set(a[key])|set(b[key])) if a[key].get(fld,'')!=b[key].get(fld,'')]
            if not fields:continue
            changed.append(key)
            if kind=='evidence' and any(f in {'Quantitative_Outcome','Outcome','Direction','Dose','Sample_Size','Route','Endpoint'} for f in fields):num+=1
            if any('Verification' in f or f in {'Identity_Status','Status'} for f in fields):verif+=1
            if kind=='compound' and any(f in {'PubChem_CID','SMILES','InChI','InChIKey','Canonical_Name'} for f in fields):identity+=1
            transition_rows.append({'From':old['version'],'To':newer['version'],'Entity':kind.title(),'Stable_ID':key,'Change':'field_values_changed','Changed_fields':'|'.join(fields)})
        for key in introduced:transition_rows.append({'From':old['version'],'To':newer['version'],'Entity':kind.title(),'Stable_ID':key,'Change':'introduced','Changed_fields':''})
        for key in removed:transition_rows.append({'From':old['version'],'To':newer['version'],'Entity':kind.title(),'Stable_ID':key,'Change':'removed','Changed_fields':''})
        transition_summary.append({'From':old['version'],'To':newer['version'],'Entity':kind.title(),'Previous_rows':len(a),'Current_rows':len(b),'Introduced':len(introduced),'Removed':len(removed),'Common_changed':len(changed),'Common_exact':len(common)-len(changed),'Numeric_outcomes_changed':num,'Verification_fields_changed':verif,'Identity_fields_changed':identity,'Note':'V2 has no compound registry; V2→V3 compound-ID diff unavailable.' if kind=='compound' and old['version']=='V2' else ''})
write_csv(DST/'history/release_transition_record_changes.csv',transition_rows)
write_csv(DST/'history/release_transition_summary.csv',transition_summary)

# A compact lineage table draws on actual tables plus release records; explain
# non-data-only snapshots instead of treating them as new scientific releases.
lineage=[]
notes={'V2':'Initial nine-anchor evidence baseline with research-priority export.','V3':'Added five anchors and nine evidence records; total 14/73.','V4':'No count change; one record corrected and verification work recorded.','V5':'Expanded to 26 anchors/118 records; controlled evidence additions and null findings retained.','V6':'Expanded to 44 anchors/147 records; warning and provenance audits added.','V7':'Quality/preservation release family; lineage counts must be read from the actual CSV tables.','V7-clean':'Clean-copy snapshot of the V7 release family.','V8':'Quality release with preservation and source-review material; not a separate expansion target.','V9':'Expanded baseline independently recalculated by V10 as 74/210.','V10':'100 anchors/263 evidence rows; preserved V9 inherited rows.','V11':'105 anchors/272 evidence rows; six manual reviews remain pending/partial.','V12':'119 anchors/286 evidence rows; 14 additions, target gap 31; PASS_WITH_WARNINGS.'}
for x in counts:lineage.append({**x,'Summary':notes[x['Release']]})
write_csv(DST/'history/release_lineage.csv',lineage)

# Copy the V12 audit tools into the history with unambiguous labels. The final
# package has its own portable validator and mutation suite generated below.
for name in ('build_v12.py','mutation_test_v12.py','finalize_v12.py'):
    p=SRC/name
    if p.exists():
        d=DST/'history'/'v12_scripts'/name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)

# Schema and integration contract: literature descriptions are never exposure.
data_map={
 'compound_registry.csv':'One row per stable Compound_ID; identity, food-context, selection and record-count fields.',
 'interaction_evidence.csv':'One row per stable Evidence_ID; Compound_ID, Study_ID, PMID/DOI, evidence class, direction, outcome and source location.',
 'drug_probe_registry.csv':'Probe labels and their evidence-record counts; label identity is descriptive and not a prescribing recommendation.',
 'study_registry.csv':'Study_ID to publication and evidence-row relationship; one publication may have multiple rows and is not assumed to represent independent cohorts.',
 'publication_bibliography.csv':'PMID/DOI indexed publication metadata; PMID and DOI counts are separate measures.',
 'warning_ledger.csv':'Warnings and residual uncertainties; unresolved and inherited issues remain visible.',
 'cooking_retention_evidence.csv':'Stage A cooking/retention evidence kept separate from drug-interaction evidence.',
}
with (DST/'documentation/data_dictionary.md').open('w',encoding='utf-8') as f:
    f.write('# Stage B data dictionary and downstream interface\n\n')
    f.write('## Authoritative files\n\n| File | Meaning |\n|---|---|\n')
    for n,meaning in data_map.items():f.write(f'| `data/{n}` | {meaning} |\n')
    f.write('\n## Stable relationships\n\nUse `Compound_ID`, `Evidence_ID`, `Study_ID`, PMID, and DOI as stored. Preserve IDs exactly. Join evidence to compounds by `Compound_ID`, to studies by `Study_ID`, and to publication metadata using PMID/DOI. Drug/probe labels are values in `drug_probe_registry.csv`; do not reinterpret them as clinical treatment recommendations.\n\nStage B is a literature evidence resource. It does not calculate dietary exposure, retained doses, or patient-specific clinical risk. In-vitro and animal findings are not demonstrated human clinical interactions. Verification status and warning limitations must travel with any downstream record. Descriptive fields and assay outcomes are suitable for evidence retrieval; they are not exposure estimates or risk scores.\n')
    f.write('\n## Evidence classes\n\n- `Human pharmacokinetic`: pharmacokinetic measurements in human participants.\n- `Controlled clinical`: controlled intervention in human participants.\n- `Other human clinical`: human evidence not classified as pharmacokinetic or controlled clinical in this schema.\n- `Animal`: nonhuman in-vivo evidence.\n- `In vitro`: enzyme, cell, microsome, or transporter assay.\n\nThese classes describe study design and must not be collapsed into a single clinical-evidence category.\n\n## Verification levels\n\nVerification status describes how the source was checked; it is not a confidence score. Current values include `Full-text table verified`, `Abstract verified`, `Abstract verified; numeric/claim-level review limited to stated locator`, `Article abstract located; full extraction not completed`, `Partially verified`, and inherited V8 review status. The latter directs users to the inherited claim-level audit. Only two records are marked full-text/table verified in the V12 baseline. Unverified and abstract-only claims must remain identifiable downstream.\n\n## Open audit flags\n\nThe warning ledger contains 55 entries. The final structural audit separately emitted 313 review flags: 210 evidence rows lack a separate source-audit row, 90 have a blank quantitative-outcome field, and 13 numeric outcome strings lack a readily identified unit/statistic. Claim-support rows exist for all 286 evidence IDs, but source-audit coverage is partial. These counts are audit flags, not extra entries in the warning ledger.\n')

# Build README and final handoff directly from recalculated V12 tables.
data={k:read_csv(DST/v) for k,v in {
 'compounds':'data/compound_registry.csv','evidence':'data/interaction_evidence.csv','drugs':'data/drug_probe_registry.csv',
 'studies':'data/study_registry.csv','bibliography':'data/publication_bibliography.csv','warnings':'data/warning_ledger.csv'}.items()}
pmids={x.get('PMID','').strip() for x in data['evidence'] if x.get('PMID','').strip()}
dois={x.get('DOI','').strip().lower() for x in data['evidence'] if x.get('DOI','').strip()}
classes={k:sum(x.get('Evidence_Type','')==k for x in data['evidence']) for k in sorted({x.get('Evidence_Type','') for x in data['evidence']})}
source_audit=read_csv(DST/'provenance/source_audit.csv')
source_audit_ids={x.get('Evidence_ID','') for x in source_audit if x.get('Evidence_ID','')}
claim_support_ids={x.get('Evidence_ID','') for x in read_csv(DST/'provenance/claim_support_and_verification.csv') if x.get('Evidence_ID','')}
(DST/'README.md').write_text(f'''# CookRisk Stage B — authoritative final release\n\n**Authoritative release:** this directory (`StageB_Final`).\n\nThis is the consolidated Stage B literature-evidence package, based on the immutable V12 release. It contains {len(data['compounds'])} compound anchors, {len(data['evidence'])} interaction-evidence rows, {len(data['drugs'])} probe labels, {len(pmids)} PMID publications, {len(dois)} distinct nonblank DOIs, and {len(data['warnings'])} warning-ledger rows. Evidence classes: {', '.join(f'{k}: {v}' for k,v in classes.items())}. The final audit also flags 210 missing source-audit rows, 90 blank quantitative-outcome fields, and 13 numeric/unit review items.\n\n## Structure\n\n- `data/` — canonical registries, evidence, bibliography, warning ledger, and cooking-retention table.\n- `provenance/` — selection decisions, candidate screening, source audit, claim support, and source register.\n- `identity/` — chemical identity/structure audit.\n- `validation/` — final audit reports, machine-readable tests, mutation results, and inherited audit outputs.\n- `documentation/` — handoff, data dictionary, integration interface, and relevant historical handoffs.\n- `scripts/` — portable final validation and mutation-testing scripts.\n- `history/` — version lineage, V2–V12 reconciliation and adjacent-version changes, V12 file disposition map, and unique historical/support artifacts.\n- `manifests/` — SHA-256 file manifest.\n\n## Validate, test, and reproduce\n\nUse Python 3 with only its standard library:\n\n```powershell\npython scripts/validate_final.py .\npython scripts/mutation_test_final.py .\n```\n\nTo rebuild into a new sibling directory, run from `Documents/CookChem/stageB/`:\n\n```powershell\npython StageB_Final/scripts/consolidate_final.py release_v12_20261030 StageB_Final_Rebuilt\n```\n\nThe destination must be new or empty. The build runs a clean-copy comparison and creates its own checksum manifest.\n\nThe validator checks structure and relationships; it does not certify scientific truth. See `documentation/FINAL_HANDOFF.md` and `validation/manual_review_status.csv` for unresolved work. Original V2–V12 releases remain preserved beside this release under `Documents/CookChem/stageB/`; V12 remains unchanged.\n''',encoding='utf-8')
(DST/'documentation/FINAL_HANDOFF.md').write_text(f'''# CookRisk Stage B final consolidation handoff\n\n**Authoritative directory:** `StageB_Final`  \n**Baseline:** immutable V12 release, independently recounted during consolidation.  \n**Release state:** `PASS_WITH_WARNINGS` for structural/reproducibility checks; scientific review remains incomplete.\n\n## Verified dataset counts\n\n- {len(data['compounds'])} compound anchors; {len(data['evidence'])} interaction-evidence records.\n- {len(data['drugs'])} drug/probe labels; {len(data['studies'])} study-registry rows.\n- {len(pmids)} PMID-linked publications and {len(dois)} distinct nonblank DOIs among evidence rows.\n- {len(data['warnings'])} warning rows; warning statuses and source notes are retained.\n- Evidence classes: {json.dumps(classes,ensure_ascii=False)}.\n- Claim-support registry covers {len(claim_support_ids)} distinct evidence IDs; the inherited source-audit file contains {len(source_audit_ids)} distinct evidence IDs, leaving {len(data['evidence'])-len(source_audit_ids)} rows without a separate source-audit row.\n\nV12 handoff reports target 150 and is 31 anchors short. This consolidation did not add research records.\n\n## Consolidation decisions\n\nV12 current data tables were copied to one canonical location each under `data/`, `provenance/`, and `identity/`. V12 source/audit artifacts not represented by canonical tables were retained verbatim once; exact duplicate files were mapped to their retained copy in `history/v12_file_disposition.csv`. The full original V12 release and V2–V11 releases remain in place, untouched. No older data rows were reintroduced. The V12 change log and direct V9–V12 stable-ID diff are under `history/`. `history/legacy_release_record_reconciliation.csv` compares available V2–V11 evidence and compound IDs against V12; all available evidence IDs and compound IDs were found in V12, with non-identical historical rows and schema differences listed. V2 compound coverage is name/alias-only because it has no compound registry. V7 contains 188 evidence rows while its clean-copy snapshot has 189; both counts are preserved as observed. `history/release_transition_summary.csv` and `history/release_transition_record_changes.csv` attribute adjacent-version additions and field changes, including changes to quantitative outcomes and verification fields. An inherited `v10_release_summary.json` in V12 contains stale V10/V9 labels and counts; it is archived as a historical artifact and was not used for authoritative counts.\n\n## Validation and mutation results\n\nThe packaged validator checks identifier uniqueness, core foreign keys, study/publication links, evidence classes, source/claim/selection coverage, duplicate structures and contexts, warning identifiers, and separation of cooking-retention data. It records warnings separately from structural failures. Twelve isolated mutations are run against temporary copies; each must trigger its intended validation code. Clean-copy results are reported in `validation/clean_copy_comparison.csv`.\n\nThe V12 baseline reported 32/32 automated checks, 34/34 mutations, 15/15 preservation checks, and 12/12 byte-identical clean-copy outputs. Those results are preserved in `validation/audit/`. The final package also reports its own 16 structural checks and 12 mutation cases. The final package flags 210 missing source-audit rows, 90 blank quantitative-outcome fields, and 13 numeric/unit review items; these are recorded separately from the 55-row warning ledger.\n\n## Remaining scientific limitations\n\nV12 reports only two claims as full-text/table verified. Its six inherited manual checks are partial or incomplete, including inherited food-occurrence review, chemical-form/stereochemistry adjudication, numerical/table verification, source-to-claim review, warning-source review, and cohort overlap. Three inherited automated review signals concern direction/text mismatches, repeated contexts, and missing numeric units. Eleven inherited compound evidence-count fields did not reconcile and were preserved with discrepancies documented. See `validation/manual_review_status.csv` and `validation/audit/`.\n\nThe consolidation found no basis to declare all historical publication records independent studies; PMID/DOI identifiers are not cohort identifiers. No inherited warning was artificially closed. No data correction or historical rationale was invented. Exact duplicates are documented; non-identical observations remain separate.\n\n## Stage C / Stage D interface\n\nUse stable `Compound_ID`, `Evidence_ID`, and `Study_ID` values and preserve PMID/DOI, source locators, evidence class, direction, outcomes/units, verification status, limitations, and warning flags. Stage B does not calculate dietary exposure, cooking-retained dose, or patient-specific risk. In-vitro and animal results must remain distinguishable from clinical evidence. No Stage C or Stage D code is included.\n\n## File map\n\nSee `README.md`, `documentation/data_dictionary.md`, `history/release_lineage.csv`, `history/legacy_release_record_reconciliation.csv`, `history/release_transition_summary.csv`, `history/release_transition_record_changes.csv`, `history/cross_release_record_diff_v9_v12.csv`, `history/v12_file_disposition.csv`, and `manifests/SHA256SUMS.json`.\n''',encoding='utf-8')

# Record the inherited V11 six-check status without upgrading partial reviews.
manual=read_csv(DST/'validation/audit/v12_manual_check_disposition.csv') if (DST/'validation/audit/v12_manual_check_disposition.csv').exists() else []
if not manual:
    manual=[{'Test_ID':i,'Status':s,'Remaining_gap':gap} for i,s,gap in [
      ('FC-01','PARTIAL','Inherited food occurrence contexts were not independently re-sourced one by one.'),
      ('CH-05','PARTIAL','Complete structure graph and stereochemistry adjudication remains pending.'),
      ('NX-05','PARTIAL','Full-text/table verification for every inherited numerical claim remains incomplete.'),
      ('CL-03','PARTIAL','Every inherited claim was not individually verified against primary source text.'),
      ('PV-07','NOT COMPLETED','Publication/cohort overlap was not adjudicated.'),
      ('WA-03','PARTIAL','Every warning closure was not revalidated against full primary sources.')]]
write_csv(DST/'validation/manual_review_status.csv',manual)

# Package portable QA utilities and the deterministic consolidation builder.
DST.joinpath('scripts').mkdir(parents=True,exist_ok=True)
for name in ('validate_final.py','mutation_test_final.py'):
    shutil.copy2(Path(__file__).with_name(name),DST/'scripts'/name)
shutil.copy2(Path(__file__),DST/'scripts/consolidate_final.py')

# Run the structural validator and 12 isolated adversarial cases.
import subprocess, tempfile
for script in ('validate_final.py','mutation_test_final.py'):
    proc=subprocess.run([sys.executable,str(DST/'scripts'/script),str(DST)],capture_output=True,text=True,timeout=300)
    if proc.returncode: raise SystemExit(f'{script} failed: {proc.stdout}\n{proc.stderr}')

# Rebuild into a clean temporary copy from the same immutable V12 inputs.
if not INTERNAL:
    with tempfile.TemporaryDirectory(prefix='stageb_final_rebuild_',dir=DST.parent) as td:
        rebuilt=Path(td)/'StageB_Final'
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),str(SRC),str(rebuilt),'--internal'],capture_output=True,text=True,timeout=900)
        if proc.returncode: raise SystemExit(f'clean-copy assembly failed: {proc.stdout}\n{proc.stderr}')
        excluded={'manifests/SHA256SUMS.json','validation/clean_copy_comparison.csv'}
        a={p.relative_to(DST).as_posix():sha(p) for p in DST.rglob('*') if p.is_file() and p.relative_to(DST).as_posix() not in excluded}
        b={p.relative_to(rebuilt).as_posix():sha(p) for p in rebuilt.rglob('*') if p.is_file() and p.relative_to(rebuilt).as_posix() not in excluded}
        rows=[{'Path':k,'Release_SHA256':a.get(k,''),'Clean_Copy_SHA256':b.get(k,''),'Match':str(k in b and a.get(k)==b.get(k))} for k in sorted(set(a)|set(b))]
        write_csv(DST/'validation/clean_copy_comparison.csv',rows)
        if set(a)!=set(b) or any(x['Match']!='True' for x in rows):raise SystemExit('clean-copy rebuild did not reproduce all package files')

# Final package manifest excludes itself.
manifest={p.relative_to(DST).as_posix():sha(p) for p in sorted(DST.rglob('*')) if p.is_file() and p.relative_to(DST).as_posix()!='manifests/SHA256SUMS.json'}
(DST/'manifests').mkdir(parents=True,exist_ok=True)
(DST/'manifests/SHA256SUMS.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

print(json.dumps({'destination':str(DST),'canonical_files':len(canonical),'unique_v12_hashes':len(seen),'source_files_mapped':len(disposition),'anchors':len(data['compounds']),'evidence':len(data['evidence']),'probe_labels':len(data['drugs']),'pmids':len(pmids),'dois':len(dois),'warnings':len(data['warnings'])},indent=2))
