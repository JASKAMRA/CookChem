import csv, json, hashlib, collections, re
from pathlib import Path

SRC = Path(r'C:\Users\dakshant\Documents\CookChem\stageB\release_v10_20261030')
O, A, S = SRC/'outputs', SRC/'audit', SRC/'sources'
A.mkdir(exist_ok=True); S.mkdir(exist_ok=True)
def read(name):
    with open(O/name, encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))
def write(name, rows):
    with open(O/name, 'w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def save(p, x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')

base=read('compound_registry_v9.csv'); old_e=read('stageB_food_drug_interactions_v9.csv')
reg={x['Compound_ID']:x for x in base}; byname={x['Canonical_Name'].casefold():x for x in base}
props={}
for fn in ['all_v9_pubchem_structures.json','candidate_pubchem_structures.json']:
    for x in json.loads((SRC/fn).read_text(encoding='utf-8-sig')): props[str(x['CID'])]=x
candidate=json.loads((SRC/'candidate_pubchem_cids.json').read_text(encoding='utf-8-sig'))
cidbyname={x['Name']:str(x['CID']) for x in candidate}

# Complete inherited structure strings and independently audit each CID against PubChem.
ident=[]
for x in base:
    p=props.get(x['PubChem_CID'])
    for k in ['SMILES','InChI','InChIKey']:
        if not x[k] and p: x[k]=p[k]
    same=bool(p and p['InChIKey']==x['InChIKey']) if x['InChIKey'] else False
    if p: x['Identity_Status']='PubChem CID/name and returned structure checked in V10; missing fields completed' if same else 'PubChem structure returned; inherited InChIKey mismatch requires review'
    ident.append({'Compound_ID':x['Compound_ID'],'Canonical_Name':x['Canonical_Name'],'PubChem_CID':x['PubChem_CID'],'Returned_InChIKey':p['InChIKey'] if p else '', 'Registry_InChIKey':x['InChIKey'],'Exact_Key_Match':str(same),'SMILES':x['SMILES'],'InChI':x['InChI'],'Structure_Source':f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{x['PubChem_CID']}/property/CanonicalSMILES,IsomericSMILES,InChI,InChIKey/JSON",'Status':'Complete' if p and same else 'Review required','Note':'PubChem standardized representation; tautomer/protonation conventions may differ across databases.'})

rawmeta=json.loads((SRC/'selected_pubmed_metadata.json').read_text(encoding='utf-8-sig'))
meta={}
for pmid in rawmeta['uids']:
    x=rawmeta[pmid]; ids=x.get('articleids',[])
    meta[pmid]={'PMID':pmid,'Title':x['title'].strip(),'Authors':'; '.join(z['name'] for z in x.get('authors',[])),'Year':x.get('pubdate','')[:4], 'DOI':next((z['value'] for z in ids if z.get('idtype')=='doi'),''),'PMCID':next((z['value'] for z in ids if z.get('idtype') in ('pmc','pmcid')),''),'URL':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'}

new=[]; anchors=[]; eid=211
def add_anchor(name, food, rationale, pmid, gap):
    cid=cidbyname[name]; p=props.get(cid,{})
    row={k:'' for k in base[0]}; m=meta.get(pmid,{})
    row.update({'Compound_ID':'MOL-V10-'+cid,'Canonical_Name':name,'Aliases':name,'PubChem_CID':cid,'SMILES':p.get('SMILES',''),'InChI':p.get('InChI',''),'InChIKey':p.get('InChIKey',''),'Identity_Status':'PubChem CID and structure fields retrieved; exact InChIKey screened','Identity_Source':f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}','Origin':'v10_new_anchor','Selection_Rationale':rationale,'Selection_Source':'Retrospective evidence-led V10 selection; primary source cited in selection decisions','Selection_DOI':m.get('DOI','10.7783/KJMCS.2016.24.1.7' if name=='6-Shogaol' else ''),'Selection_PMID':pmid,'Selection_URL':m.get('URL','https://medicinalcrop.org/xml/18895/18895.pdf' if name=='6-Shogaol' else ''),'Date_Added':'2026-10-30','First_Documented_Release_Date':'2026-10-30','Date_Status':'V10 addition date, not historical discovery date','Coverage_Status':'Abstract-level primary-source review unless evidence row states otherwise','Provenance_Status':'v10_retrospective_selection_documented','Original_Molecular_Group':'MOL-V10-'+cid,'Retention_Status':'No cooking-retention evidence inferred','Food_Context':food,'Evidence_Records':'0','Link_Restriction':'No Stage C exposure integration','Release_Reviewed':'v10_20261030','Selection_Verification':'Retrospective; source and food context documented','Selection_Temporality':'retrospective selection on 2026-10-30','Remaining_Provenance_Gap':gap})
    anchors.append(row); byname[name.casefold()]=row
    ident.append({'Compound_ID':row['Compound_ID'],'Canonical_Name':name,'PubChem_CID':cid,'Returned_InChIKey':p.get('InChIKey',''),'Registry_InChIKey':p.get('InChIKey',''),'Exact_Key_Match':'new anchor; screened against inherited keys','SMILES':p.get('SMILES',''),'InChI':p.get('InChI',''),'Structure_Source':f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES,IsomericSMILES,InChI,InChIKey/JSON','Status':'Complete' if p else 'Review required','Note':'PubChem-standardized structure; dietary abundance and bioavailability not established.'})

def add(comp, probe, effect, outcome, pmid, dose='', loc='PubMed abstract: Results', limits='In vitro finding; clinical interaction and exposure not established.', mech='Direct assay; mechanism otherwise unspecified', doi='', title='', authors='', year='', url='', typ='In vitro'):
    global eid
    m=meta.get(pmid,{})
    r={k:'' for k in old_e[0]}; r.update({'Evidence_ID':f'SB-{eid:04d}','Compound':comp,'Compound_ID':byname[comp.casefold()]['Compound_ID'],'Drug':probe,'Interaction_Effect':effect,'Mechanism':mech,'Evidence_Type':typ,'Evidence_Level':'Mechanistic','Direction':'Inhibition' if 'inhibit' in effect.lower() else ('No significant effect' if 'no significant' in effect.lower() else 'Modulation'),'Quantitative_Outcome':outcome,'Dose':dose,'Population':'Human-derived in-vitro enzyme/transporter system','Study_Design':'In-vitro enzyme or cell assay','Source_Title':title or m.get('Title',''),'Authors':authors or m.get('Authors',''),'Year':year or m.get('Year',''),'DOI':doi or m.get('DOI',''),'PMID':pmid,'Source_Type':'Primary article; abstract-level extraction','Limitations':limits,'Confidence':'Moderate for reported assay; low for clinical extrapolation','Notes':'V10 addition. Values not reported in inspected abstract remain unstated.','Study_ID':'PMID:'+pmid if pmid else 'DOI:'+doi,'Source_URL':url or m.get('URL',''),'Source_Cache':'v10_pmid_'+pmid+'.json' if pmid else '', 'Source_Locator':loc,'Preparation':'Purified compound; detailed assay formulation not transcribed','Affected_Entity':probe,'Perpetrator':comp,'Outcome':effect,'Identity_Status':'Structure checked; see identity_structure_audit_v10.csv','Release_Origin':'v10_new_record','Clinical_Extrapolation':'Not established','CookRisk_Exposure_Link':'No Stage C exposure integration'})
    new.append(r); eid+=1

# Evidence-led expansion; botanical supplement findings are labeled in selection provenance.
groups=[
('p-Coumaric acid','Fruits, vegetables, grains','Food-derived phenolic acid tested against human OAT3.','22877817','Food compound; in-vitro transporter evidence.'),
('Gentisic acid','Plant foods; also a salicylate metabolite','Direct hOAT3 evidence; dietary and drug-metabolite origins distinguished.','22877817','Not all systemic gentisic acid is food-derived.'),
('4-Hydroxybenzoic acid','Fruits, vegetables, plant foods','Food-derived phenolic acid tested against hOAT3.','22877817','In-vitro transporter evidence.'),
('Protocatechuic acid','Berries and other plant foods','Food-derived phenolic acid tested against hOAT1 and hOAT3.','22877817','In-vitro transporter evidence.'),
('Sinapinic acid','Grains, seeds, plant foods','Food-derived phenolic acid tested against hOAT1, hOAT3 and hOAT4.','22877817','In-vitro transporter evidence.'),
('Syringic acid','Fruits, grains and plant foods','Food-derived phenolic acid tested against hOAT3.','22877817','In-vitro transporter evidence.'),
('Hyperoside','Plant foods and herbal teas; quercetin glycoside','Named dietary compound screened against OATP4C1; null finding retained.','38256064','Null finding in one transporter screen; limited inclusion basis.'),
('Isoquercetin','Fruits and vegetables; quercetin glycoside','Named dietary compound screened against OATP4C1; null finding retained.','38256064','Null finding in one transporter screen; limited inclusion basis.'),
('Neohesperidin','Citrus foods and peel','Citrus glycoside screened against OATP4C1; null finding retained.','38256064','Null finding in one transporter screen; limited inclusion basis.'),
('Theaflavin','Black tea oxidation product','Tea polyphenol screened against OATP4C1 with a reported test concentration.','38256064','One null in-vitro assay; not evidence of clinical interaction.'),
('Baicalein','Scutellaria root; medicinal botanical/supplement','Direct CYP2C9 and CYP1A assay evidence.','19074529','Primarily medicinal-botanical context; in vitro only.'),
('Baicalin','Scutellaria root; medicinal botanical/supplement','Named flavonoid tested against human CYP1A.','30989924','Primarily medicinal-botanical context.'),
('Scutellarein','Scutellaria and related medicinal botanicals','Direct CYP2C9 and CYP1A assay evidence.','19074529','Primarily medicinal-botanical context.'),
('Wogonin','Scutellaria root; medicinal botanical/supplement','Direct human CYP2C9 and CYP1A assay evidence.','19074529','Primarily medicinal-botanical context.'),
('Oroxylin A','Scutellaria root; medicinal botanical/supplement','Named Scutellaria flavonoid reported as potent CYP1A inhibitor.','30989924','Medicinal botanical; abstract reports potency range.'),
('7-Methoxyflavanone','Scutellaria-related botanical constituent','Named Scutellaria flavonoid reported as potent CYP1A inhibitor.','30989924','Medicinal botanical; ordinary food abundance unestablished.'),
('Wogonoside','Scutellaria root; medicinal botanical/supplement','Named Scutellaria flavonoid tested against human CYP1A.','30989924','Primarily medicinal-botanical context.'),
('Carnosic acid','Rosemary and rosemary-derived food antioxidant','Human hepatocyte and liver microsome CYP experiments with reported Ki values.','22531045','In-vitro; supplement levels may exceed food exposure.'),
('Carnosol','Rosemary and rosemary-derived food antioxidant','Rosemary diterpene tested in mouse PK and human CYP inhibition profile.','34592323','Abstract does not identify all inhibited isoforms; limited extraction.'),
('6-Shogaol','Dried/heated ginger and ginger supplements','Purified ginger constituent tested against human CYP enzymes.','','DOI-only source; full-text extraction remains incomplete.'),
('Xanthohumol','Hops, beer and hop supplements','Hop prenylphenol tested in a human CYP panel at specified concentrations.','24342125','In-vitro concentrations do not establish dietary exposure.'),
('Glycitein','Soy foods; isoflavone','Direct CYP2A6 nicotine C-oxidation evidence; mixture human study not attributed to it.','16490810','Human intervention involved a mixture of isoflavones.'),
('Genistin','Soy foods and soy beverages','Isolated isoflavone glycoside tested in a P-glycoprotein assay.','24295672','Rat mixture PK outcomes not attributed to isolated genistin.'),
('Daidzin','Soy foods and soy beverages','Isolated isoflavone glycoside tested in a P-glycoprotein assay.','24295672','Rat mixture PK outcomes not attributed to isolated daidzin.'),
('Coumestrol','Legumes and alfalfa/clover sprouts','PXR/CYP target response tested in primary human hepatocytes and humanized mice.','18096694','Mechanistic, not clinical DDI evidence.'),
('Galangin','Propolis, honey, some plant foods','Direct CYP2C9 inhibition assay evidence.','19074529','Propolis/supplement relevance stronger than ordinary-food relevance.')]
for x in groups: add_anchor(*x)

# Phenolic acid transporters; aggregate IC50 ranges are not assigned to individual acids.
for c in ['p-Coumaric acid','Gentisic acid','4-Hydroxybenzoic acid','Protocatechuic acid','Sinapinic acid','Syringic acid']:
    add(c,'hOAT3 transport assay','Inhibited hOAT3-mediated transport','Significant inhibition at 100 μM; abstract gives selected-compound IC50 range 7.35–87.36 μM, not a per-compound value.','22877817','Compound 100 μM; probe substrate 1 μM',limits='In vitro; aggregate IC50 range not assigned to each compound.',mech='Transporter-mediated uptake inhibition')
for c in ['Protocatechuic acid','Sinapinic acid']:
    add(c,'hOAT1 transport assay','Inhibited hOAT1-mediated transport','Significant inhibition at 100 μM; individual potency not stated in inspected abstract.','22877817','Compound 100 μM; probe substrate 1 μM',limits='In vitro; exact compound-level potency requires full-text table review.',mech='Transporter-mediated uptake inhibition')
add('Sinapinic acid','hOAT4 transport assay','Inhibited hOAT4-mediated transport','Approximately 35% inhibition at 100 μM.','22877817','Compound 100 μM; probe substrate 1 μM',mech='Transporter-mediated uptake inhibition')
# OATP4C1 screening compounds. V9 anchors receive evidence rows too.
for c,pct,dose in [('Apigenin','66%','100 μM'),('Daidzein','40%','100 μM'),('Fisetin','24%','100 μM'),('Genistein','42%','100 μM'),('Isorhamnetin','18%','100 μM'),('Kaempferol','75%','100 μM'),('Luteolin','52%','100 μM'),('Morin','57%','100 μM'),('Quercetin','50%','100 μM'),('Curcumin','72%','100 μM'),('Resveratrol','46%','100 μM'),('Theaflavin','no significant effect','50 μM'),('Hyperoside','no significant effect','100 μM'),('Isoquercetin','no significant effect','100 μM'),('Neohesperidin','no significant effect','100 μM')]:
    if c.casefold() in byname:
        add(c,'OATP4C1-mediated T3 uptake','Inhibited T3 uptake' if '%' in pct else 'No significant effect on T3 uptake',pct+' inhibition' if '%' in pct else 'No significant effect reported','38256064',f'T3 1 μM; compound {dose}; 10 min at 37°C',loc='PMC10815578: Results; dietary compound screen',limits='Single in-vitro screen, n=3; no human exposure inference. Curcumin oxidation was limited by ascorbic acid in the source.')
# CYP2C9 panel and CYP1A study.
for c in ['Baicalein','Scutellarein','Wogonin','Galangin']:
    add(c,'CYP2C9; diclofenac 4′-hydroxylation','Inhibited CYP2C9-mediated metabolism','Flavonoid panel except flavone had Ki ≤2.2 μM; individual value not assigned here.','19074529',loc='PubMed abstract: Results; Table 2 required for exact compound value',limits='Aggregate bound not a substitute for per-compound Ki.',mech='Competitive inhibition reported for these flavonoids')
for c,q in [('Wogonin','IC50 <1 μM'),('7-Methoxyflavanone','IC50 <1 μM'),('Oroxylin A','IC50 <1 μM'),('Baicalein','IC50 1–10 μM'),('Baicalin','IC50 10–25 μM'),('Scutellarein','IC50 10–25 μM'),('Wogonoside','IC50 10–25 μM')]:
    add(c,'CYP1A; phenacetin O-deethylation','Inhibited CYP1A activity',q,'30989924',loc='PubMed abstract: Methods and Results',limits='Chinese-language primary article; abstract-level, no exact IC50 within range.',mech='Direct CYP1A inhibition')
# Rosemary carnosic acid, abstract-reported in vitro results.
for probe,effect,q,dose in [('CYP2C9','Inhibited','Ki = 9.2 μM','Human liver microsomes'),('CYP3A4','Inhibited','Ki = 4.3 μM','Human liver microsomes'),('CYP2B6 activity','Induced','At 10 μM: +61.6% and +49.3% in two donors vs phenobarbital','10 μM; primary human hepatocytes'),('CYP3A activity','Induced','At 10 μM: +82.6% and +142% in two donors vs rifampicin','10 μM; primary human hepatocytes')]:
    add('Carnosic acid',probe,effect+' '+probe,q,'22531045',dose,limits='In-vitro only; not a clinical interaction.')
add('Carnosol','Human CYP enzyme panel','CYP inhibition profile reported; abstract does not name affected isoforms','No isoform-specific numeric result entered; requires full-text extraction.','34592323',limits='Primary abstract does not support named isoform-level claims.',loc='PubMed abstract: summary')
# DOI-only ginger study; values from its published abstract; follow-up full-text check is flagged.
for probe,ic,ki,mech in [('CYP2C9','29.20','29.02','Noncompetitive'),('CYP1A2','20.68','6.33','Competitive'),('CYP2C19','18.78','19.26','Noncompetitive')]:
    add('6-Shogaol',probe,'Inhibited '+probe+' activity',f'IC50 = {ic} μM; Ki = {ki} μM.','',loc='Article abstract: Methods and Results',limits='In vitro only; DOI-only source; full-text table follow-up required.',mech=mech+' inhibition',doi='10.7783/KJMCS.2016.24.1.7',title='Effects of 6-Shogaol, a Major Component of Zingiber officinale Roscoe, on Human Cytochrome P450 Enzymes in vitro',authors='Jin Kim et al.',year='2016',url='https://medicinalcrop.org/xml/18895/18895.pdf')
# Hop prenylphenol CYP panel.
for probe,q in [('CYP1A2','11.8%'),('CYP2B6','43.9%'),('CYP2C8','92.9%'),('CYP2C9','69.7%'),('CYP2C19','15.0%')]:
    add('Xanthohumol',probe,'Inhibited '+probe+' activity',q+' inhibition at 10 μM.','24342125',dose='Xanthohumol 10 μM',loc='PMC3987852: Results, CYP activity panel')
add('Xanthohumol','CYP2C8','Inhibited CYP2C8 activity','47.8 ± 5.1% inhibition at 1 μM.','24342125',dose='Xanthohumol 1 μM',loc='PMC3987852: Results, CYP activity panel')
add('Glycitein','CYP2A6; nicotine C-oxidation','Inhibited nicotine C-oxidation','Ki = 5.2 ± 0.8 μM; uncompetitive. No effect on coumarin 7-hydroxylation.','16490810',limits='Human supplement study used a mixture and is not attributed to glycitein.',mech='Substrate-dependent uncompetitive inhibition')
for c,pct in [('Genistin','6%'),('Daidzin','17%')]:
    add(c,'P-glycoprotein; rhodamine 123','Reduced intracellular rhodamine 123, consistent with increased P-gp efflux',f'Intracellular rhodamine 123 decreased {pct} at 50 μM.','24295672','Compound 50 μM',limits='Cell assay; rat cyclosporine changes used whole soymilk/miso and are not attributed to isolated compound.',loc='Article abstract: in-vitro results')
add('Coumestrol','PXR-regulated CYP3A4/CYP2B6 expression','Antagonized PXR agonist-mediated CYP3A4/CYP2B6 induction','Qualitative suppression reported; numeric outcome not transcribed.','18096694',limits='Mechanistic cell and humanized mouse study; not clinical DDI evidence.',mech='PXR antagonism')

# Finish V10 registries and review files.
allreg=base+anchors; alle=old_e+new
for a in anchors:a['Evidence_Records']=str(sum(x['Compound_ID']==a['Compound_ID'] for x in new))
write('compound_registry_v10.csv',allreg); write('stageB_food_drug_interactions_v10.csv',alle); write('identity_structure_audit_v10.csv',ident)
for x in ident:
    if x['Status'] in ('Complete','Review required') and x['Compound_ID'] in {a['Compound_ID'] for a in anchors}:
        keys={z['InChIKey'] for z in base}
        if x['Final_Key'] if 'Final_Key' in x else x.get('Registry_InChIKey'): pass

sel=read('v9_selection_decisions.csv'); screen=read('v9_candidate_screening_log.csv')
for a in anchors:
    m=meta.get(a['Selection_PMID'],{}); sel.append({'Candidate':a['Canonical_Name'],'Decision':'Included as V10 anchor','Identity':f"PubChem CID {a['PubChem_CID']}; structure in V10 identity audit",'Food_Context':a['Food_Context'],'Interaction_Rationale':a['Selection_Rationale'],'Primary_Source_PMID':a['Selection_PMID'],'Primary_Source_DOI':a['Selection_DOI'],'Verification':'Abstract-level unless evidence locator specifies article full text','Date':'2026-10-30','Residual_Limitation':a['Remaining_Provenance_Gap']})
    screen.append({'Search_Date':'2026-10-30','Database':'PubMed/PMC, PubChem PUG REST','Query_or_Candidate':a['Canonical_Name'],'Decision':'Included; retrospective evidence-led V10 decision','Reason':a['Selection_Rationale'],'Full_Text_Availability':'Abstract examined; relevant PMC/article text located where cited','Verification_Status':'Abstract verified; full-text extraction not claimed unless explicitly stated','Reviewer_Note':'Targeted search; not systematic or exhaustive.'})
write('v10_selection_decisions.csv',sel); write('v10_candidate_screening_log.csv',screen)

# Source metadata cache, bibliography, study index and claim audit.
bib=read('source_bibliography_v9.csv'); seen={x['PMID'] for x in bib}
for pmid,m in meta.items():
    if any(x['PMID']==pmid for x in new) and pmid not in seen:
        bib.append({'PMID':pmid,'Title':m['Title'],'Authors':m['Authors'],'Year':m['Year'],'DOI':m['DOI'],'PMCID':m['PMCID'],'Source':'sources/v10_pmid_'+pmid+'.json','Count_Unit':'Unique PMID publication; not an independent cohort','DOI_Status':'PubMed ESummary metadata captured'})
        save(S/('v10_pmid_'+pmid+'.json'),rawmeta[pmid])
# Preserve the DOI-only primary article in the bibliography even though no PMID was confirmed.
if not any(x.get('DOI','').lower()=='10.7783/kjmcs.2016.24.1.7' for x in bib):
    bib.append({'PMID':'','Title':'Effects of 6-Shogaol, a Major Component of Zingiber officinale Roscoe, on Human Cytochrome P450 Enzymes in vitro','Authors':'Jin Kim et al.','Year':'2016','DOI':'10.7783/KJMCS.2016.24.1.7','PMCID':'','Source':'https://medicinalcrop.org/xml/18895/18895.pdf','Count_Unit':'Unique DOI-only publication; PMID not confirmed','DOI_Status':'DOI-only source; full-text extraction pending'})
write('source_bibliography_v10.csv',bib)
studies=read('study_registry_v9.csv'); seen={x['PMID'] for x in studies}
for pmid,m in meta.items():
    rs=[x for x in new if x['PMID']==pmid]
    if rs and pmid not in seen: studies.append({'Study_ID':'PMID:'+pmid,'PMID':pmid,'DOI':m['DOI'],'Title':m['Title'],'Authors':m['Authors'],'Year':m['Year'],'Evidence_Record_IDs':' | '.join(x['Evidence_ID'] for x in rs),'Evidence_Record_Count':str(len(rs)),'Evidence_Classes':'In vitro','Verification_Status':'Abstract verified; see record locators','Independence':'Unique PMID publication; cohort count not assumed'})
rs=[x for x in new if x['DOI']=='10.7783/KJMCS.2016.24.1.7']
if rs: studies.append({'Study_ID':'DOI:10.7783/KJMCS.2016.24.1.7','PMID':'','DOI':'10.7783/KJMCS.2016.24.1.7','Title':rs[0]['Source_Title'],'Authors':rs[0]['Authors'],'Year':'2016','Evidence_Record_IDs':' | '.join(x['Evidence_ID'] for x in rs),'Evidence_Record_Count':str(len(rs)),'Evidence_Classes':'In vitro','Verification_Status':'DOI-only article abstract, full-text follow-up needed','Independence':'One DOI publication; cohort count not applicable'})
write('study_registry_v10.csv',studies)
claims=read('claim_support_and_verification_v9.csv')
for x in new: claims.append({'Evidence_ID':x['Evidence_ID'],'Compound_ID':x['Compound_ID'],'PMID':x['PMID'],'Source_Locator':x['Source_Locator'],'Verification_Status':'Abstract verified' if x['PMID'] else 'Article abstract located; full extraction not completed','Numerical_Use':'In-vitro descriptive evidence only; no exposure integration','Attribution':x['Compound']+' / '+x['Drug'],'Limitations':x['Limitations']})
write('claim_support_and_verification_v10.csv',claims)

# Rebuild combined drug/probe index.
drugs=read('drug_probe_registry_v9.csv'); dm={x['Drug_Probe']:x for x in drugs}
for x in new:
    if x['Drug'] not in dm: dm[x['Drug']]={'Drug_ID':'DRUG-V10-'+str(len(dm)+1).zfill(4),'Drug_Probe':x['Drug'],'Evidence_Records':'0','Primary_PMIDs':'','Scope':'V10 assay probe/target; may not be a clinical drug'}
for name,x in dm.items():
    rr=[z for z in alle if z['Drug']==name]; x['Evidence_Records']=str(len(rr)); x['Primary_PMIDs']=' | '.join(sorted({z['PMID'] for z in rr if z['PMID']}))
write('drug_probe_registry_v10.csv',list(dm.values()))

# Preserve all inherited warnings and append V10 scientific/traceability warnings.
warn=read('warning_resolution_ledger_v9.csv')
extra=[
('V10-W01','structure_standardization','PubChem structures retrieved for all anchors; cross-database tautomer/protonation normalization not performed.','All 100 anchors','Exact InChIKey comparison completed; PubChem structure identifiers recorded.','PubChem standardization may differ across databases.','outputs/identity_structure_audit_v10.csv'),
('V10-W02','candidate_scope','Several additions are medicinal botanicals or supplement constituents, not established common-food exposures.','Scutellaria flavonoids','Botanical/supplement context stated for each; no ordinary-food abundance inferred.','May not satisfy a strict common-food-only scope.','outputs/v10_selection_decisions.csv'),
('V10-W03','null_only_anchor_evidence','Four anchors admitted from one OATP4C1 screen with no significant effect.','Hyperoside | Isoquercetin | Neohesperidin | Theaflavin','Null results retained and weak anchor basis disclosed.','Single concentration/screen; evidence does not show positive interaction.','PMID 38256064; PMC10815578'),
('V10-W04','abstract_only_extraction','Most new rows are abstract-level; primary article tables not independently extracted for every endpoint.','New V10 records','Only stated values included; unresolved values left blank or qualitative.','Do not interpret as clinically quantitative claims.','outputs/claim_support_and_verification_v10.csv'),
('V10-W05','doi_pmid_reconciliation','V9 has 130 unique PMIDs but 125 unique nonblank DOI strings and six records without DOI.','V9 evidence/publication index','Counts reported separately; PMID/DOI mapping is not assumed one-to-one.','Record-level collision crosswalk remains incomplete.','outputs/v10_baseline_recalculation.json'),
('V10-W06','primary_source_extraction','Carnosol and DOI-only shogaol exact full-text extraction remains incomplete.','Carnosol; 6-Shogaol','Qualitative/abstract-reported findings only; no unverified carnosol isoform claims.','Shogaol PMID not confirmed; table details require follow-up.','PMID 34592323; DOI 10.7783/KJMCS.2016.24.1.7'),
('V10-W07','historical_selection_provenance','Original nine historical selection triggers and dates remain unrecoverable.','Original nine anchors','Prior history search retained; no date or rationale invented.','V10 decisions are retrospective and do not repair original history.','outputs/original_nine_selection_provenance.csv')]
for wid,code,desc,aff,act,lim,src in extra: warn.append({'Warning_ID':wid,'Code':code,'Description':desc,'Affected':aff,'Classification':'scientific or provenance limitation','Before':'New in V10','Action':act,'After':'Partially resolved' if wid=='V10-W01' else 'Unresolved','Remaining_Limitations':lim,'Resolution_Source':src,'Review_Date':'2026-10-30'})
write('warning_resolution_ledger_v10.csv',warn)

# Machine-readable change log.
changes=[]
for x in base:
    for k in ['SMILES','InChI','InChIKey']:
        orig=read('compound_registry_v9.csv'); old=next(z for z in orig if z['Compound_ID']==x['Compound_ID'])
        if old[k]!=x[k]: changes.append({'Entity_Type':'compound','Entity_ID':x['Compound_ID'],'Change_Type':'structure_completion','Field':k,'Before':old[k],'After':x[k],'Reason':'PubChem PUG REST retrieval; exact InChIKey compared','Source':x['Identity_Source']})
for x in anchors: changes.append({'Entity_Type':'compound','Entity_ID':x['Compound_ID'],'Change_Type':'addition','Field':'registry','Before':'','After':x['Canonical_Name'],'Reason':x['Selection_Rationale'],'Source':x['Selection_URL']})
for x in new: changes.append({'Entity_Type':'evidence','Entity_ID':x['Evidence_ID'],'Change_Type':'addition','Field':'record','Before':'','After':x['Compound']+' / '+x['Drug']+' / '+x['Quantitative_Outcome'],'Reason':'Primary-source evidence; limitations recorded in row','Source':x['Source_URL']})
write('v10_change_log.csv',changes)

# Baseline recalculation and preservation hashes.
classes=collections.Counter(x['Evidence_Type'] for x in old_e); v9warn=read('warning_resolution_ledger_v9.csv')
counts={'v9':{'anchors':len(base),'records':len(old_e),'distinct_drugs_probes':len({x['Drug'] for x in old_e}),'unique_PMID':len({x['PMID'] for x in old_e if x['PMID']}),'unique_nonblank_DOI':len({x['DOI'].strip().lower() for x in old_e if x['DOI'].strip()}),'DOI_blank_records':sum(not x['DOI'].strip() for x in old_e),'evidence_classes':dict(classes),'numerical_outcomes':sum(bool(re.search(r'\d',x['Quantitative_Outcome'])) for x in old_e),'warning_rows':len(v9warn),'warning_codes':len({x['Code'] for x in v9warn}),'warning_status':dict(collections.Counter(x['After'] for x in v9warn))},'v10':{'anchors':len(allreg),'records':len(alle),'new_anchors':len(anchors),'new_records':len(new),'unique_PMID':len({x['PMID'] for x in alle if x['PMID']}),'unique_nonblank_DOI':len({x['DOI'].strip().lower() for x in alle if x['DOI'].strip()}),'warning_rows':len(warn),'warning_codes':len({x['Code'] for x in warn})}}
save(A/'v10_baseline_recalculation.json',counts)
hashes={}
for rel in ['outputs/compound_registry_v9.csv','outputs/stageB_food_drug_interactions_v9.csv','outputs/v9_selection_decisions.csv','outputs/v9_candidate_screening_log.csv','outputs/warning_resolution_ledger_v9.csv','outputs/cooking_retention_evidence_v9.csv','audit/v9_validation_report.json']:
    p=SRC/rel; hashes[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
save(A/'v10_inherited_v9_hashes.json',hashes)
dup={k:[x['Canonical_Name'] for x in allreg if x['InChIKey']==k] for k,n in collections.Counter(x['InChIKey'] for x in allreg).items() if k and n>1}
print(json.dumps({'new_anchors':len(anchors),'new_records':len(new),'v10_anchors':len(allreg),'v10_records':len(alle),'unique_new_keys':len({x['InChIKey'] for x in anchors}),'duplicate_keys':dup,'incomplete_identity':sum(x['Status']!='Complete' for x in ident),'baseline':counts['v9']},indent=2))
