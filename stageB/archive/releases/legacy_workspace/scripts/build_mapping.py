"""Conservative identity comparison. Requires RDKit; never changes historical files."""
import csv,json,re
from pathlib import Path
from collections import defaultdict,Counter
from rdkit import Chem
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
DATA=(ROOT/'inputs'/'cookchem_master_expanded_round11.csv') if (ROOT/'inputs'/'cookchem_master_expanded_round11.csv').exists() else Path('C:/Users/dakshant/Downloads/cookchem_master_expanded_round11.csv')
def read(p): return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(name,rows,fields=None):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0])); w.writeheader(); w.writerows(rows)
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
def canon(s,stereo=True):
    m=Chem.MolFromSmiles(s)
    return Chem.MolToSmiles(m,isomericSmiles=stereo) if m else None
data=read(DATA); groups=defaultdict(list)
for r in data:
    if r['Canonical_Molecular_ID']: groups[r['Canonical_Molecular_ID']].append(r)
write('stageB_unassigned_observations.csv',[r for r in data if not r['Canonical_Molecular_ID']])
mapping=[]; identity_audit=[]
for key,rs in sorted(groups.items()):
    vals=lambda c:sorted({r.get(c,'').strip() for r in rs if r.get(c,'').strip()})
    names=vals('Compound_Name'); original_cids=vals('PubChem_CID')
    cids=sorted({r[c].split('.')[0] for r in rs for c in ['Resolved_PubChem_CID','PubChem_CID_Resolved'] if r[c]}) or sorted({v.split('.')[0] for v in original_cids})
    smiles=vals('Canonical_SMILES') or vals('SMILES'); matches=[]; reasons=[]
    for cid in cids:
        p=ROOT/'sources'/f'pubchem_{cid}.json'; props=json.loads(p.read_text(encoding='utf-8')).get('PropertyTable',{}).get('Properties',[]) if p.exists() else []
        if not props: reasons.append(f'CID {cid}: retrieval unavailable'); continue
        prop=props[0]; synp=ROOT/'sources'/f'synonyms_{cid}.json'
        synonyms=json.loads(synp.read_text(encoding='utf-8')).get('InformationList',{}).get('Information',[{}])[0].get('Synonym',[]) if synp.exists() else []
        aliases={norm(s) for s in synonyms+[prop.get('Title','')]}
        # Parenthetical vitamin labels are tested by their chemical-name prefix too.
        nameok=all(norm(n) in aliases or norm(n.split(' (')[0]) in aliases for n in names)
        match='mismatch'
        if len(smiles)==1 and prop.get('SMILES'):
            if canon(smiles[0])==canon(prop['SMILES']): match='exact_structure'
            elif canon(smiles[0],False)==canon(prop['SMILES'],False): match='connectivity_only'
        identity_audit.append({'Canonical_Molecular_ID':key,'candidate_CID':cid,'PubChem_title':prop.get('Title',''),'structure_comparison':match,'all_observed_names_verified':nameok,'observed_names':' | '.join(names),'source_url':f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}'})
        if match!='mismatch' and nameok: matches.append((cid,prop,synonyms,match))
        else: reasons.append(f'CID {cid}: {match}; all names verified={nameok}')
    status='uncertain'; title=cid=inchi=inchikey=formula=cas=stdsmiles=''; syn=[]
    if len(matches)==1 and len(cids)==1:
        cid,prop,syn,comparison=matches[0]; status='verified_exact' if comparison=='exact_structure' else 'verified_connectivity'
        title=prop['Title']; inchi=prop['InChI']; inchikey=prop['InChIKey']; formula=prop['MolecularFormula']; stdsmiles=prop['SMILES']
        # A bare CAS-like synonym is retained only when the checksum is valid, and remains source-reported.
        def validcas(x):
            if not re.fullmatch(r'\d{2,7}-\d{2}-\d',x): return False
            digits=x.replace('-',''); return sum(int(d)*i for i,d in enumerate(reversed(digits[:-1]),1))%10==int(digits[-1])
        cas=' | '.join(s for s in syn if validcas(s))
        if comparison=='connectivity_only': reasons.append('Connectivity and source-reported name/CID agree; supplied SMILES does not establish all source stereochemistry. No stereochemical form transfer or group merging is authorized.')
    elif len(matches)>1 or len(cids)>1: reasons.append('Multiple candidate identities; no forced match')
    else: reasons.append('No concordant structure + externally reported name/synonym match')
    mapping.append({'Canonical_Molecular_ID':key,'CookRisk_compound_name':' | '.join(names),'standardized_compound_name':title,'synonyms':' | '.join(syn[:20]),'SMILES':' | '.join(smiles),'CAS':cas,'PubChem_CID':cid,'InChI':inchi,'InChIKey':inchikey,'compound_class':' | '.join(vals('Canonical_Compound_Class') or vals('Compound_Class')),'food_sources':' | '.join(vals('Canonical_Food_Name') or vals('Food_Name')),'mapping_status':status,'mapping_source':f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}' if cid else 'Supplied dataset; candidate audit in stageB_identity_audit.csv','notes':'; '.join(reasons),'observation_count':len(rs),'molecular_formula':formula,'original_PubChem_CIDs':' | '.join(original_cids),'candidate_PubChem_CIDs':' | '.join(cids),'standardized_source_SMILES':stdsmiles,'search_status':'searched_candidates_not_exhaustively_screened','interaction_evidence_status':'No qualifying evidence retained in this release; search coverage limited'})
write('stageB_compound_mapping.csv',mapping); write('stageB_identity_audit.csv',identity_audit)
print('Mapping statuses:',dict(Counter(r['mapping_status'] for r in mapping)))
