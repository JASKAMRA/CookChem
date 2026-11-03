"""Append the source-verified Batch 101 records after baseline hash checks."""
import csv, hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'stageC'/'src'))
from stage_c.food_composition import FIELDS, normalize_record, validate_food_record
from stage_c.compound_mapping import MAPPING_FIELDS, build_mappings

BASE_FOOD='aa15fd49be4afd30d1f61fe06de9039d0a925c22a6c56e970ddc75033b04f127'
BASE_MAP='9dcaadf0821aee15f1666ca26c88c592bb1e98a781eb533e246ddd94dab9ca97'
FP=ROOT/'stageC/data/food_composition/food_composition.csv'
MP=ROOT/'stageC/data/compound_food_mapping/compound_food_mapping.csv'
old_f,old_m=FP.read_bytes(),MP.read_bytes()
assert hashlib.sha256(old_f).hexdigest()==BASE_FOOD
assert hashlib.sha256(old_m).hexdigest()==BASE_MAP

compound={
 'phloridzin':('MOL-V17-CID-6072','Phloridzin','6072','IOUVKUPGCMBWBT-QNDFHXLGSA-N'),
 'quercitrin':('MOL-V17-CID-5280459','Quercitrin','5280459','OXGUCUVFOIWWQJ-HQBVPOQASA-N'),
 'sequol':('MOL-V17-CID-91469','S-equol','91469','ADFCQWZHKCXPAJ-GFCCVEGCSA-N'),
 'sunset':('MOL-V17-CID-17730','Sunset Yellow FCF','17730','OIQPTROHQCGFEF-UHFFFAOYSA-L')}
source={
 'phloridzin':('Electroactive Phenolic Contributors and Antioxidant Capacity of Flesh and Peel of 11 Apple Cultivars Measured by Cyclic Voltammetry and HPLC-DAD-MS/MS','10.3390/antiox9111054','https://www.mdpi.com/2076-3921/9/11/1054','2020','Table 3; Table 1 MS/MS identity','HPLC-DAD quantification with MS/MS identification','80% methanol extraction of separately pooled ripe apple peel/flesh; results explicitly stated per fresh weight.'),
 'quercitrin':('Phenolic Content and Antioxidant Activity in Apples of the Galaval Cultivar Grown on 17 Different Rootstocks','10.3390/antiox11020266','https://www.mdpi.com/2076-3921/11/2/266','2022','Results §3.1, Figure 4; value also stated in text','HPLC-PDA with authentic quercitrin standard','Apple flesh lyophilizate/extract prepared under Methods §§2.3-2.4; Figure 4 axis gives dry-weight basis.'),
 'sequol':('Stinky tofu as a rich source of bioavailable S-equol in Asian diets','10.1016/j.jff.2013.01.006','https://doi.org/10.1016/j.jff.2013.01.006','2013','Table 1, concentration per 100 g commercial stinky tofu','Chiral HPLC; S-equol enantiomer confirmed','Ready-to-serve commercial dishes homogenized and analyzed; source reports wet-weight concentrations.'),
 'sunset':('Determination of Six Synthetic Dyes in Sports Drinks by Dispersive Solid-Phase Extraction and HPLC-UV-Vis','10.21577/0103-5053.20170173','https://www.scielo.br/j/jbchs/a/VzpDPnjj3XtvSDYKyGqNpLJ/?lang=en','2018','Table 3; Table 1 E110/CAS 2783-94-0','Dispersive solid-phase extraction and HPLC-UV-Vis external calibration','Sports-drink liquid sample processed by d-SPE; volume basis retained without density conversion.')}
records=[]
def add(key,rid,food,common,species,part,cultivar,origin,state,use,value,unit,basis,n,unc,notes,extra='',sampleid=''):
 cid,name,pubchem,inchi=compound[key]; title,doi,url,year,locator,method,extraction=source[key]
 r={f:'' for f in FIELDS}; r.update({'food_record_id':rid,'food_name':food,'common_name':common,'scientific_name':species,'food_database':'Primary analytical food-composition study','food_database_record_id':sampleid or locator,'food_part':part,'cultivar_or_variety':cultivar,'geographical_origin':origin,'raw_or_processed_state':state,'compound_id':cid,'compound_name':name,'food_use_classification':use,'pubchem_cid':pubchem,'inchikey':inchi,'reported_concentration':str(value),'reported_unit':unit,'moisture_basis':basis,'analytical_method':method,'extraction_method':extra or extraction,'sample_size':n,'source_title':title,'doi':doi,'source_url':url,'publication_year':year,'source_classification':'Primary analytical measurement','source_verification_status':'Full-text verified','extraction_notes':notes,'uncertainty_notes':unc})
 r=normalize_record(r); errors=validate_food_record(r)
 if errors: raise ValueError((rid,errors))
 records.append(r)

cultivars=['Quinte','Jonagored','Early Geneva','Paulared','Sunrise','Gloster','Delikates','Papierowka','Rubinola','Antonowka','Ligol']
peel=[23.91,24.65,24.45,16.43,48.08,43.45,18.30,84.10,42.90,23.37,16.51]
flesh=[18.89,7.17,20.63,10.37,14.68,5.86,9.14,23.46,18.09,45.05,6.61]
psd=[.48,1.63,.49,.76,.80,2.59,1.74,1.60,3.21,.45,.73]
fsd=[.98,.17,.80,.36,.84,.16,.06,.77,.22,1.79,.14]
for i,c in enumerate(cultivars):
 code=c.upper().replace(' ','').replace('Ó','O')
 for part,value,sd in [('peel',peel[i],psd[i]),('flesh',flesh[i],fsd[i])]:
  add('phloridzin',f'PHLORIDZIN-ANTIOX2020-{code}-{part.upper()}',f'Apple (Malus domestica), {part}, cv. {c}','Apple','Malus domestica',part,c,'Olsztyn, Poland','raw','ordinary food',f'{value:.2f}','\u00b5g/g','fresh weight (FW)','Mean of n=4 source replicates; 10 randomly selected ripe apples per cultivar, tissue pooled',f'Source reports mean +/- SD {sd:.2f} (n=4).','Table 3; phloridzin identified in both tissues by HPLC-DAD-MS/MS. Values are fresh-weight despite lyophilized analytical extracts; no conversion applied.')
add('quercitrin','QUERCITRIN-ANTIOX2022-GALAVAL-G11-FLESH',"Apple (Malus domestica), flesh, cv. Galaval, rootstock G.11",'Apple','Malus domestica','flesh','Galaval; rootstock G.11','Babtai, Lithuania','raw','ordinary food','148','\u00b5g/g','dry weight (DW)','Mean of n=3 consecutive HPLC determinations; field design 4 plots x 3 trees/rootstock; pooling structure not stated','Source reports 148 +/- 18; HPLC method says mean and SD of three consecutive tests. Figure 4 axis specifies dry weight.','Figure 4 and Results §3.1; textual result, not graph reconstruction; authentic quercitrin standard.',extra='Lyophilized apple flesh prepared/extracted under Methods §§2.3-2.4; concentration reported on dry-weight basis.')
add('sequol','SEQUOL-JFF2013-STINKYTOFU-ALL138','Commercial stinky tofu, ready-to-serve aggregate (138 dishes; mixed preparation methods)','Stinky tofu','Glycine max (soybean)','fermented soy food','','Taipei and Taichung, Taiwan','processed','ordinary food','1.2','mg/100 g','wet weight','n=138 commercial dishes; 126/138 (91.3%) detectable; Table 1 mean +/- SD','Source Table 1 reports 1.2 +/- 1.0 mg/100 g, n=138. Mixed ready-to-serve methods; handling of nondetects in the mean not stated. All measured equol was S-enantiomer.','Table 1. Aggregate includes mostly deep-fried and boiled-in-hot-pot dishes, plus other preparations; not assigned to a single cooking method.')
for sid,flavor,value,spread in [('S1','Tangerine',11.49,1.14),('S4','Orange',9.06,.77),('S6','Tangerine',11.84,.91),('S7','Passion fruit',3.79,.33)]:
 add('sunset',f'SUNSETYELLOW-FLORIANO2018-{sid}',f'Commercial sports drink, {flavor.lower()} flavor, sample {sid}','Sports drink','','beverage','', 'Santa Maria, Rio Grande do Sul, Brazil','processed','prepared beverage',f'{value:.2f}','mg/L','volume basis; beverage concentration (mg/L), mass moisture basis not applicable',f'One product identified as {sid}; independent product/assay replicate count not stated',f'Source Table 3 reports {value:.2f} +/- {spread:.2f} mg/L; dispersion type and replicate count not stated. LOQ 0.5 mg/L.',f'Table 3 sample {sid}; E110/Sunset Yellow identified and measured by HPLC-UV-Vis after d-SPE. No density-based conversion.','',sid)

with (ROOT/'stageC/data/stage_b_snapshot_20261103/compound_registry.csv').open(encoding='utf-8-sig',newline='') as f: compounds=list(csv.DictReader(f))
with (ROOT/'stageC/data/stage_b_snapshot_20261103/identity_structure_audit.csv').open(encoding='utf-8-sig',newline='') as f: audits=list(csv.DictReader(f))
audit={x['Compound_ID']:x for x in audits}
for r in records:
 c=next(c for c in compounds if c['Compound_ID']==r['compound_id'])
 assert audit[r['compound_id']]['Status']=='Complete' and c['PubChem_CID']==r['pubchem_cid'] and c['InChIKey']==r['inchikey']
maps=build_mappings(compounds,records)
assert len(records)==28 and len(maps)==28
assert all(m['mapping_status'] in {'Exact identity match','Structure-supported match'} and m['quantitative_data_available']=='true' for m in maps)

batch=pathlib.Path(__file__).resolve().parent
def writecsv(path,fields,rows,bom=True):
 with path.open('w',encoding='utf-8-sig' if bom else 'utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(rows)
writecsv(batch/'accepted_rows.csv',FIELDS,records); writecsv(batch/'accepted_mappings.csv',MAPPING_FIELDS,maps)
for path,fields,rows in [(FP,FIELDS,records),(MP,MAPPING_FIELDS,maps)]:
 with path.open('a',encoding='utf-8',newline='') as f:
  csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n').writerows(rows)
assert FP.read_bytes().startswith(old_f) and MP.read_bytes().startswith(old_m)

# Post-append integrity and independent coverage count.
with FP.open(encoding='utf-8-sig',newline='') as f: foods=list(csv.DictReader(f))
with MP.open(encoding='utf-8-sig',newline='') as f: allmaps=list(csv.DictReader(f))
complete={x['Compound_ID'] for x in audits if x['Status']=='Complete'}
valid={'Exact identity match','Verified synonym match','Structure-supported match'}
quant={x['compound_id'] for x in allmaps if x['mapping_status'] in valid and x['quantitative_data_available'].lower()=='true'}
covered=quant&complete
assert len(foods)==len(allmaps)==539 and len(covered)==97 and len(complete)==107 and len(audits)==143
assert len({x['food_record_id'] for x in foods})==539 and len({x['mapping_id'] for x in allmaps})==539
assert not ({x['food_record_id'] for x in allmaps}-{x['food_record_id'] for x in foods})
print(json.dumps({'records_added':28,'mappings_added':28,'new_identity_complete_compounds':sorted({x['compound_id'] for x in maps}),'food_records':len(foods),'mapping_rows':len(allmaps),'identity_complete_coverage':len(covered),'identity_complete_gaps':len(complete-covered),'food_sha256':hashlib.sha256(FP.read_bytes()).hexdigest(),'mapping_sha256':hashlib.sha256(MP.read_bytes()).hexdigest()},indent=2))
