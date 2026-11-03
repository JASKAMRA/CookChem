import csv, json, hashlib, collections, copy, re
from pathlib import Path
BASE=Path(__file__).resolve().parent
O=BASE/'outputs'; S=BASE/'sources'; A=BASE/'audit'; I=BASE/'inputs'
for p in (O,S,A,I): p.mkdir(exist_ok=True)
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields=None):
 if fields is None: fields=list(rows[0]) if rows else []
 with open(p,'w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base_e=read(O/'stageB_food_drug_interactions_v8.csv'); base_r=read(O/'compound_registry.csv')
base_hash=digest(O/'stageB_food_drug_interactions_v8.csv')
# Candidate identifiers resolve to distinct PubChem CIDs; structural strings are intentionally not copied from secondary mirrors.
compounds=[
('6\',7\'-Dihydroxybergamottin','6,7-DHB|DHB',6440498,'Grapefruit; grapefruit juice','Named component of grapefruit juice; purified compound tested against CYP3A4 in a primary mechanistic study. Human juice-serum PK is not treated as isolated-compound evidence.','15179411','10.1016/j.clpt.2004.02.007'),
('Astaxanthin','',5281224,'Foods and dietary supplements; seafood/algal sources','Food/supplement-associated xanthophyll with direct human CYP enzyme-panel testing and a separate human UGT panel; weak/null findings retained.','23669408|27529203','10.1016/j.fct.2013.04.053|10.3390/molecules21081052'),
('β-Cryptoxanthin','Beta-cryptoxanthin',5281235,'Tangerines, red peppers, pumpkin and other produce','Food carotenoid with direct CYP and UGT interaction screening, including quantitative weak inhibition and a null/low-risk interpretation.','23669408|27529203','10.1016/j.fct.2013.04.053|10.3390/molecules21081052'),
('Canthaxanthin','Cantaxanthin',5281227,'Food pigment; dietary supplements','Food colorant/nutritional supplement carotenoid with direct CYP and UGT inhibition screening; effects were weak in vitro.','23669408|27529203','10.1016/j.fct.2013.04.053|10.3390/molecules21081052'),
('Biochanin A','',5280373,'Red clover; legumes; herbal dietary supplements','Principal red-clover isoflavone with CYP1A2 data and independent P-gp cell-transport evidence; rat P-gp substrate PK publication is not added here because metadata was ambiguous.','26278343|12604704','10.1016/j.toxlet.2015.08.202|10.1124/jpet.102.044412'),
('Formononetin','',5280378,'Red clover; legumes','Principal red-clover isoflavone with direct human/rat microsomal CYP inhibition results; predicted in-vivo statements remain labeled as predictions.','26278343','10.1016/j.toxlet.2015.08.202'),
('Puerarin','Kakonein',5281807,'Kudzu (Pueraria lobata) root; traditional dietary/herbal preparations','Major kudzu-root isoflavone with human probe-drug observations, human/rat microsomal CYP3A work, rat buspirone PK, and cell-model CYP2D6 evidence. Herbal preparation and isolated compound are not equated.','20195825|24710899|24786236','10.1007/s12272-010-0209-2|10.1055/s-0034-1368350|10.1038/aps.2013.202'),
('Phloretin','Phloretol',4788,'Apples and pears','Diet-associated apple/pear chalcone with direct cellular P-gp efflux evidence; no human PK interaction is inferred.','12604704','10.1124/jpet.102.044412'),
('Acacetin','5,7-Dihydroxy-4-methoxyflavone',5280442,'Parsley and other plant foods','Food-associated flavonoid directly screened against CYP3A4; strongest reported screening result in the source (95% inhibition at 1 μM).','30301254','10.3390/molecules23102553'),
('Pinocembrin','',68071,'Honey and propolis; plant foods','Food-associated flavanone with qualitative irreversible CYP3A4 inhibition in a primary aglycone screen; no numerical potency is claimed.','30301254','10.3390/molecules23102553'),
('Isorhamnetin','',5281654,'Onion, pear and other plant foods','Food-associated flavonol with qualitative irreversible CYP3A4 inhibition in a primary aglycone screen; no numerical potency is claimed.','30301254','10.3390/molecules23102553'),
('Tectochrysin','Chrysin dimethyl ether',5281954,'Propolis and honey-associated products','Food-associated flavonoid tested as a pure aglycone and reported to irreversibly inhibit CYP3A4; no numerical potency is claimed.','30301254','10.3390/molecules23102553'),
('β-Sitosterol','Beta-sitosterol',222284,'Nuts, seeds, vegetable oils, grains and produce','Common dietary phytosterol with direct rat-microsome CYP3A4/CYP2D6 screening; weak activity is retained as in-vitro evidence only.','26139922','10.1007/s13197-014-1472-x'),
('Stigmasterol','',5280794,'Vegetable oils, legumes, nuts and seeds','Common dietary phytosterol with direct rat-microsome CYP3A4/CYP2D6 screening; weak activity is retained as in-vitro evidence only.','26139922','10.1007/s13197-014-1472-x'),
]
meta={
'15179411':("6'7'-Dihydroxybergamottin contributes to the grapefruit juice effect",'Kakar SM, Paine MF, Stewart PW, Watkins PB',2004,'10.1016/j.clpt.2004.02.007','Abstract verified; purified-DHB in-vitro arm distinguished from grapefruit-serum human PK.'),
'23669408':('Inhibitory effects of astaxanthin, β-cryptoxanthin, canthaxanthin, lutein, and zeaxanthin on cytochrome P450 enzyme activities','Zheng YF, Bae SH, Kwon MJ, Park JB, Choi HD, Shin WG, Bae SK',2013,'10.1016/j.fct.2013.04.053','Abstract verified; substrate-level detail not fully captured for every CYP endpoint.'),
'27529203':('In Vitro Inhibition of Human UDP-Glucuronosyl-Transferase (UGT) Isoforms by Astaxanthin, β-Cryptoxanthin, Canthaxanthin, Lutein, and Zeaxanthin: Prediction of in Vivo Dietary Supplement-Drug Interactions','Zheng YF, Min JS, Kim D, Park JB, Choi SW, Lee ES, Na K, Bae SK',2016,'10.3390/molecules21081052','Abstract and figure-caption substrate list verified; in-vitro study, not an observed clinical interaction.'),
'26278343':('In vivo prediction of CYP-mediated metabolic interaction potential of formononetin and biochanin A using in vitro human and rat CYP450 inhibition data','Arora S, Taneja I, Challagundla M, Raju KS, Singh SP, Wahajuddin',2015,'10.1016/j.toxlet.2015.08.202','Abstract verified; predicted R values are not observed clinical outcomes.'),
'12604704':('Effects of the flavonoids biochanin A, morin, phloretin, and silymarin on P-glycoprotein-mediated transport','Zhang S, Morris ME',2003,'10.1124/jpet.102.044412','Abstract verified; human breast-cancer cell-line experiments, not human PK.'),
'20195825':('The effects of puerarin on CYP2D6 and CYP1A2 activities in vivo','Zheng J, Chen B, Jiang B, Zeng L, Tang ZR, Fan L, Zhou HH',2010,'10.1007/s12272-010-0209-2','Abstract verified; 18 male volunteers; abstract does not report puerarin dose.'),
'24710899':('In vitro and in vivo evaluation of the effect of puerarin on hepatic cytochrome p450-mediated drug metabolism','Kim H, Kim S, Lee G, Jang YP, Kim YM, Kim RB, Lee MG, Shin JG',2014,'10.1055/s-0034-1368350','Abstract verified; microsomal and rat PK arms recorded separately; dose and full numerical PK not in abstract.'),
'24786236':('Inhibitory effects of phytochemicals on metabolic capabilities of CYP2D6(*)1 and CYP2D6(*)10 using cell-based models in vitro','Qu Q, Qu J, Han L, Zhan M, Wu LX, Zhang YW, Zhang W, Zhou HH',2014,'10.1038/aps.2013.202','Abstract verified; HepG2 cell models and one 100 μM screen concentration reported.'),
'30301254':('The Inhibitory Effect of Flavonoid Aglycones on the Metabolic Activity of CYP3A4 Enzyme','Mustapić DŠ, Debeljak Ž, Maleš Ž, Bojić M',2018,'10.3390/molecules23102553','Abstract verified; testosterone 6β-hydroxylation marker; full text available, but extracted candidate-specific numerical details only when stated in abstract.'),
'26139922':('Comparative inhibitory potential of selected dietary bioactive polyphenols, phytosterols on CYP3A4 and CYP2D6 with fluorometric high-throughput screening','Vijayakumar TM, Kumar RM, Agrawal A, Dubey GP, Ilango K',2015,'10.1007/s13197-014-1472-x','Abstract and PMC full-text table checked; rat-microsome screen; weak phytosterol activity and unit retained as reported.'),
}
# Interaction rows: (compound, PMID, drug/probe, class, effect, mechanism, direction, outcome, dose, population, design, preparation, limitation, locator)
items=[]
def add(c,p,d,cl,e,m,di,q,do='',pop='',design='',prep='',lim='',loc='PubMed abstract: Results'):
 items.append(dict(c=c,p=str(p),d=d,cl=cl,e=e,m=m,di=di,q=q,do=do,pop=pop,design=design,prep=prep,lim=lim,loc=loc))
add("6',7'-Dihydroxybergamottin",15179411,'CYP3A4','In vitro','Purified DHB inhibited CYP3A4 activity; DHB and grapefruit serum produced similar effects.','Reversible and mechanism-based inhibition demonstrated in vitro','inhibition','At matched study serum concentrations, reversible inhibition: DHB 75% ± 4.5%; serum 85% ± 5.7%. After 15-min preincubation, mechanism-based inhibition: DHB 78% ± 5.7%; serum 79% ± 6.8%.','Purified DHB at concentration matched to study serum; exact concentration arm 38 μmol/L','Recombinant CYP3A4; modified Caco-2 cells','Comparative in-vitro assays','Purified DHB; grapefruit serum comparator','The human felodipine outcome was from grapefruit-derived serum, not isolated DHB; not assigned to the compound row.','Abstract: Methods and Results')
for c,d,q in [
('Astaxanthin','CYP2C19','IC50 16.2 μM; weak inhibition; no significant time-dependent IC50 shift; authors considered diet/supplement effects unlikely.'),
('β-Cryptoxanthin','CYP2C8','IC50 13.8 μM; weak inhibition; no significant time-dependent IC50 shift; authors considered diet/supplement effects unlikely.'),
('Canthaxanthin','CYP2C19 and CYP3A4/5','IC50 10.9 μM (CYP2C19) and 13.9 μM (CYP3A4/5); weak inhibition; no significant time-dependent IC50 shift.')]: add(c,23669408,d,'In vitro','Weak inhibition in a nine-isozyme panel.','CYP inhibition; time-dependent shift not significant','inhibition',q,pop='In-vitro enzyme panel',design='Reversible and time-dependent inhibition screening',prep='Purified xanthophyll',lim='IC50 values exceeded reported human Cmax; source concluded dietary or supplement intake unlikely to alter drug PK. Marker-substrate detail omitted here.')
for c,d,q,effect in [
('Astaxanthin','Human UGT panel','No apparent inhibition across tested UGTs.', 'No apparent inhibition reported.'),
('β-Cryptoxanthin','UGT1A1 / UGT1A3 / UGT1A4','IC50 18.8 ± 2.07 / 28.3 ± 4.40 / 34.9 ± 5.98 μM; UGT1A1 Ki 12.2 ± 0.985 μM.','Weak inhibition; competitive UGT1A1 inhibition.'),
('Canthaxanthin','UGT1A1 / UGT1A3','IC50 38.5 ± 4.65 / 41.2 ± 3.14 μM.','Weak inhibition.')]: add(c,27529203,d,'In vitro',effect,'Human UGT marker-reaction inhibition; β-cryptoxanthin UGT1A1 competitive','inhibition or no apparent inhibition',q,pop='Human liver microsomes; recombinant UGT2B15 supersomes for that isoform',design='In-vitro UGT isoform inhibition panel',prep='Purified xanthophyll',lim='Authors concluded unlikely hepatic UGT-mediated supplement-drug interaction; predicted risk is not observed clinical evidence.')
add('Formononetin',26278343,'CYP1A2','In vitro','Concentration-dependent inhibition in human and rat liver microsomes.','Human CYP1A2 competitive inhibition; other CYP effects also reported','inhibition','Human IC50 13.42 μM; rat IC50 38.57 μM; human Ki 10.13 ± 1.96 μM. CYP2D6 also inhibited; source describes minimal effects elsewhere.','In-vitro concentration series','Human and rat liver microsomes','In-vitro CYP inhibition and prediction','Purified formononetin','R<1.1 hepatic and R>11 intestinal are author predictions, not clinical outcomes.')
add('Biochanin A',26278343,'CYP1A2','In vitro','Concentration-dependent inhibition in human and rat liver microsomes.','Moderate human CYP2C9 inhibition also reported','inhibition','Human CYP1A2 IC50 24.98 μM; rat IC50 11.86 μM.','In-vitro concentration series','Human and rat liver microsomes','In-vitro CYP inhibition and prediction','Purified biochanin A','Author-predicted intestinal CYP1A2 signal is not an observed interaction.')
add('Biochanin A',12604704,'P-glycoprotein; [3H]daunomycin; doxorubicin','In vitro','Increased daunomycin accumulation in P-gp-positive cells and potentiated doxorubicin cytotoxicity.','P-gp efflux inhibition; stimulated P-gp ATPase','inhibition of transporter-mediated efflux','Qualitative abstract result; no effect in P-gp-negative cells.','Concentration-dependent cell exposure; exact concentrations not in abstract','Human MCF-7 and MDA435/LCC6 cell lines','Cellular transport and cytotoxicity experiments','Biochanin A','In-vitro cancer-cell model; not clinical drug exposure.')
add('Puerarin',20195825,'Metoprolol (CYP2D6 probe); caffeine (CYP1A2 probe)','Human pharmacokinetic','CYP2D6 metabolic ratio decreased; caffeine/paraxanthine ratio increased.','CYP2D6 inhibition and CYP1A2 induction inferred from probe ratios','mixed: CYP2D6 inhibition; CYP1A2 induction','CYP2D6 metabolic rate log value changed from −0.0055 ± 0.1887 to −0.1754 ± 0.2411; paraxanthin/caffeine ratio increased 30 ± 47% (p=0.003).','Puerarin dose not reported in abstract; probes metoprolol and caffeine','18 male volunteers; CYP2D6 *1/*1, *1/*10, *10/*10 genotypes','Human probe-drug study; sampling at 6 h and urine 0–8 h','Puerarin administration; formulation not stated in abstract','Opposite CYP directions; dose/formulation missing in abstract.')
add('Puerarin',24710899,'Testosterone (CYP3A marker)','In vitro','Puerarin reduced testosterone disappearance in human and rat liver microsomes; other probe substrate turnover was not significantly affected.','CYP3A-mediated metabolism inhibition','inhibition','CYP3A IC50 15.5 ± 3.9 μM; significant reduction reported at 10 μM puerarin.','10 μM for stated significant effect; full concentration series for IC50','Human and rat liver microsomes','In-vitro probe-substrate assay','Puerarin','Abstract does not give every assay concentration or CYP probe outcome.')
add('Puerarin',24710899,'Buspirone (CYP3A probe)','Animal','Intravenous puerarin increased buspirone AUC and decreased time-averaged clearance; oral buspirone AUC and absolute bioavailability significantly increased.','Possible hepatic CYP3A inhibition','increased buspirone exposure','Direction significant; exact AUC and clearance values not reported in abstract.','Puerarin 10 mg/kg IV, single coadministration','Rats','Single-dose IV and oral buspirone PK','Intravenous puerarin','No human clinical interaction established; abstract lacks exact effect sizes.')
add('Puerarin',24786236,'AMMC (CYP2D6*1/*10 cell-model probe)','In vitro','Puerarin inhibited CYP2D6*1- and *10-mediated AMMC O-demethylation in a dose-dependent, competitive manner.','Competitive CYP2D6 inhibition','inhibition','At 100 μmol/L, inhibition exceeded 50% for both variants; Ki values described as close but not specified in abstract.','100 μmol/L screening concentration','HepG2 cells stably expressing CYP2D6*1 or *10','Cell-based in-vitro screening','Puerarin','Screening concentration is high; no clinical exposure inference.')
add('Phloretin',12604704,'P-glycoprotein; [3H]daunomycin','In vitro','Increased daunomycin accumulation in P-gp-positive but not P-gp-negative cells; stimulated P-gp ATPase.','P-gp-mediated cellular efflux inhibition','inhibition of transporter-mediated efflux','Qualitative abstract result; concentration dependent; no numeric effect size in abstract.','','Human MCF-7 and MDA435/LCC6 cell lines','Cellular transport experiments','Phloretin','In-vitro cancer-cell model; not clinical drug exposure.')
for c,q in [('Acacetin','95% inhibition of CYP3A4 activity at 1 μM; reversible and irreversible components reported.'),('Pinocembrin','Reported as pure irreversible CYP3A4 inhibitor; candidate-specific potency not given in abstract.'),('Isorhamnetin','Reported as pure irreversible CYP3A4 inhibitor; candidate-specific potency not given in abstract.'),('Tectochrysin','Reported as pure irreversible CYP3A4 inhibitor; candidate-specific potency not given in abstract.')]: add(c,30301254,'Testosterone 6β-hydroxylation (CYP3A4 marker)','In vitro','CYP3A4 inhibition observed in a screen of 30 flavonoid aglycones.','CYP3A4 inhibition; irreversibility as stated in source', 'inhibition',q,pop='In-vitro CYP3A4 assay',design='Flavonoid-aglycone screening; testosterone 6β-hydroxylation',prep='Tested purified aglycone',lim='Abstract provides candidate-specific numeric result only for acacetin; no clinical drug-interaction magnitude inferred.')
# Phytosterol numeric values transcribed from the article table (PMC4486538), with source units retained.
add('β-Sitosterol',26139922,'CYP3A4 / CYP2D6','In vitro','Weak inhibitory activity in high-throughput assay.','CYP450 enzyme inhibition screen','inhibition','IC50: 174.54 ± 0.54 μg/mL (CYP3A4); 189.42 ± 2.12 μg/mL (CYP2D6).','Concentration-response in vitro','Rat liver microsomes','Fluorometric high-throughput screen','β-Sitosterol','Rat-microsome screening; units are mass concentration; no human clinical inference.','Full-text table: CYP3A4/CYP2D6 IC50 values')
add('Stigmasterol',26139922,'CYP3A4 / CYP2D6','In vitro','Weak inhibitory activity in high-throughput assay.','CYP450 enzyme inhibition screen','inhibition','IC50: 86.24 ± 2.42 μg/mL (CYP3A4); 98.72 ± 1.62 μg/mL (CYP2D6).','Concentration-response in vitro','Rat liver microsomes','Fluorometric high-throughput screen','Stigmasterol','Rat-microsome screening; units are mass concentration; no human clinical inference.','Full-text table: CYP3A4/CYP2D6 IC50 values')
# Map literature rows to confirmed selected CIDs/registry IDs, and enforce no duplicate identities.
old_by_cid={x['PubChem_CID']:x for x in base_r if x.get('PubChem_CID')}
old_by_name={x['Canonical_Name'].casefold():x for x in base_r}
new_comp=[]; added=[]; cid_to_id={}
for name,alias,cid,food,reason,pmids,dois in compounds:
 cid=str(cid)
 if cid in old_by_cid or name.casefold() in old_by_name:
  continue
 cid_to_id[name]='MOL-V9-'+cid
 row={k:'' for k in base_r[0]}
 row.update(Compound_ID=cid_to_id[name],Canonical_Name=name,Aliases=' | '.join([name]+([x for x in alias.split('|') if x])),PubChem_CID=cid,Identity_Status='PubChem CID/name mapped; structural strings not re-extracted',Identity_Source=f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}',Origin='v9_new_anchor',Selection_Rationale=reason,Selection_Source='Primary interaction publication(s) plus PubChem CID record; retrospective Stage B admission rationale',Selection_DOI=dois,Selection_PMID=pmids,Selection_URL=' | '.join('https://pubmed.ncbi.nlm.nih.gov/'+x+'/' for x in pmids.split('|')),Date_Added='2026-10-29',First_Documented_Release_Date='2026-10-29',Date_Status='V9 release addition date; not a historical discovery date',Coverage_Status='Primary abstract verified; full-text status listed by evidence record',Provenance_Status='v9_retrospective_selection_documented',Original_Molecular_Group=cid_to_id[name],Retention_Status='No master retention evidence added in this interaction release',Food_Context=food,Evidence_Records='0',Link_Restriction='No Stage C exposure integration',Release_Reviewed='v9_20261029',Selection_Verification='Retrospective rationale; primary interaction study linked; food context separately documented',Selection_Temporality='retrospective selection on 2026-10-29',Remaining_Provenance_Gap='Original historical selection does not apply; exact PubChem structure strings need structured-source capture.')
 if name == 'Phloretin':
  row.update(SMILES='C1=CC(=CC=C1CCC(=O)C2=C(C=C(C=C2O)O)O)O',InChI='InChI=1S/C15H14O5/c16-10-4-1-9(2-5-10)3-6-12(18)15-13(19)7-11(17)8-14(15)20/h1-2,4-5,7-8,16-17,19-20H,3,6H2',InChIKey='VGEREEWJJVICBM-UHFFFAOYSA-N',Identity_Status='verified_exact')
 new_comp.append(row); added.append((name,cid,reason))
# Create V9 source records (abstract snapshots with explicit verification scope).
source_names={}
for p,(title,authors,year,doi,verif) in meta.items():
 cache=f'v9_pmid_{p}.json'; source_names[p]=cache
 obj={'pmid':p,'doi':doi,'title':title,'authors':authors,'year':year,'source_url':f'https://pubmed.ncbi.nlm.nih.gov/{p}/','verification_status':verif,'retrieved_for_release':'2026-10-29','source_locator':'PubMed abstract unless evidence row specifies full-text table','scope_note':'Abstract-level claims are not promoted to full-text verification.'}
 (S/cache).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
# New evidence rows preserve the 36-field inherited schema and stable IDs.
reg_by_name={x['Canonical_Name']:x for x in base_r+new_comp}
new_e=[]
for idx,x in enumerate(items,190):
 if x['c'] not in reg_by_name: continue
 m=meta[x['p']]; r=reg_by_name[x['c']]
 row={k:'' for k in base_e[0]}
 row.update(Evidence_ID=f'SB-{idx:04d}',Compound=x['c'],Compound_ID=r['Compound_ID'],Drug=x['d'],Interaction_Effect=x['e'],Mechanism=x['m'],Evidence_Type=x['cl'],Evidence_Level='compound',Direction=x['di'],Quantitative_Outcome=x['q'],Dose=x['do'],Population=x['pop'],Study_Design=x['design'],Source_Title=m[0],Authors=m[1],Year=str(m[2]),DOI=m[3],PMID=x['p'],Source_Type='Primary research',Limitations=x['lim'],Confidence=('Low-to-moderate: primary in-vitro or animal evidence; clinical relevance limited' if x['cl'] in ('In vitro','Animal') else 'Low-to-moderate: abstract-level human probe study; regimen details incomplete'),Notes='V9 addition; abstract-level extraction unless Source_Locator explicitly identifies a reviewed full-text table. No exposure or clinical risk inference.',Study_ID='PMID:'+x['p'],Source_URL=f'https://pubmed.ncbi.nlm.nih.gov/{x["p"]}/',Source_Cache=source_names[x['p']],Source_Locator=x['loc'],Preparation=x['prep'],Affected_Entity='drug/probe/enzyme/transporter',Perpetrator='compound',Outcome='observed experimental result',Identity_Status=r['Identity_Status'],Release_Origin='v9_new_record',Clinical_Extrapolation='No automatic clinical risk classification',CookRisk_Exposure_Link='No Stage C exposure integration; food amount and compound-form linkage not validated')
 new_e.append(row)
# If candidates overlap baseline identity, do not force an unsupported new anchor.
new_e=[e for e in new_e if e['Compound_ID'] in {c['Compound_ID'] for c in new_comp}]
# Prepare final V9 outputs without altering frozen V8 files.
final_r=base_r+new_comp; final_e=base_e+new_e
counts=collections.Counter(e['Compound_ID'] for e in new_e)
for r in final_r:
 if r['Compound_ID'] in counts:r['Evidence_Records']=str(int(r.get('Evidence_Records') or 0)+counts[r['Compound_ID']])
write(O/'compound_registry_v9.csv',final_r,list(base_r[0]))
write(O/'stageB_food_drug_interactions_v9.csv',final_e,list(base_e[0]))
# Unique publication bibliography.
bib=read(O/'source_bibliography.csv'); bmap={x['PMID']:x for x in bib}
for p,(title,authors,year,doi,verif) in meta.items():
 if p not in bmap:
  bmap[p]={'PMID':p,'Title':title,'Authors':authors,'Year':str(year),'DOI':doi,'PMCID':'PMC4486538' if p=='26139922' else ('PMC6272861' if p=='27529203' else ''),'Source':f'sources/{source_names[p]}','Count_Unit':'Unique PMID-indexed publication; not independent cohort','DOI_Status':'PubMed checked; primary source linked'}
write(O/'source_bibliography_v9.csv',list(bmap.values()))
# Drug/probe registry: update counts, add new probes with stable registry IDs.
drug=read(I/'v7_drug_probe_registry.csv'); dmap={x['Drug_Probe'].casefold():x for x in drug}
for e in new_e:
 name=e['Drug']; key=name.casefold()
 if key not in dmap:
  row={k:'' for k in drug[0]};row.update(Drug_ID=f'DRUG-V9-{len(dmap)+1:04d}',Drug_Probe=name,Evidence_Records='0',Primary_PMIDs='',Scope='V9 named drug/probe, enzyme, or transporter endpoint; not necessarily a clinical drug')
  drug.append(row);dmap[key]=row
for e in new_e:
 dmap[e['Drug'].casefold()]['Evidence_Records']=str(int(dmap[e['Drug'].casefold()].get('Evidence_Records') or 0)+1)
 ids= set(filter(None,dmap[e['Drug'].casefold()].get('Primary_PMIDs','').split(' | ')));ids.add(e['PMID']);dmap[e['Drug'].casefold()]['Primary_PMIDs']=' | '.join(sorted(ids,key=int))
write(O/'drug_probe_registry_v9.csv',drug)
# Primary source registry and source audit.
study=read(I/'v7_study_registry.csv'); new_study=[]
for e in new_e:
 new_study.append({'Evidence_ID':e['Evidence_ID'],'PMID':e['PMID'],'DOI':e['DOI'],'Source_Title':e['Source_Title'],'Source_URL':e['Source_URL'],'Source_Cache':e['Source_Cache'],'Source_Locator':e['Source_Locator'],'Verification_Status':'Abstract verified' if 'Full-text table' not in e['Source_Locator'] else 'Full-text table verified','Extracted_Fields':'design; compound; probe; direction; reported quantitative result where available','Limitations':e['Limitations']})
write(O/'v9_source_audit.csv',new_study)
# Search/screening rationale for selected candidates.
selection=[]
for r in new_comp:
 selection.append({'Candidate':r['Canonical_Name'],'Decision':'Included as V9 anchor','Identity':'PubChem CID '+r['PubChem_CID']+'; structure link recorded; SMILES/InChIKey not recopied','Food_Context':r['Food_Context'],'Interaction_Rationale':r['Selection_Rationale'],'Primary_Source_PMID':r['Selection_PMID'],'Primary_Source_DOI':r['Selection_DOI'],'Verification':'Abstract verified; record-level full text only where stated','Date':'2026-10-29','Residual_Limitation':r['Remaining_Provenance_Gap']})
write(O/'v9_selection_decisions.csv',selection)
reviewed=[('Theaflavin','Deferred','No newly verified compound-specific primary interaction result in this rapid focused search.'),('Sesamolin','Deferred','Identity/compound-specific qualifying primary interaction evidence not verified in the focused evidence set.'),('Scutellaria flavonoid panel','Deferred','Candidate source concerns medicinal-herb constituents; dietary food-context threshold not established for this release.'),('DHB','Included','Purified-component CYP3A4 assays; grapefruit-serum human PK kept distinct.'),('Xanthophylls','Included','Direct CYP and human UGT enzyme panels; weak/null results retained.'),('Red-clover isoflavones','Included','Compound-specific CYP inhibition; predictions distinguished from observed data.'),('Puerarin','Included','Human probe study plus rat and cellular CYP studies; dietary/herbal preparation caveat retained.'),('Flavonoid aglycones','Included','Primary CYP3A4 screen; qualitative claims kept qualitative.'),('Dietary phytosterols','Included','Primary rat-microsome screen; only weak in-vitro evidence.')]
write(O/'v9_candidate_screening_log.csv',[{'Search_Date':'2026-10-29','Database':'PubMed/PMC and PubChem','Query_or_Candidate':c,'Decision':d,'Reason':why,'Full_Text_Availability':'PMCID/primary page checked where noted','Verification_Status':'Abstract verified; selected table for PMID 26139922','Reviewer_Note':'Focused search; not systematic or exhaustive.'} for c,d,why in reviewed])
# Carry forward warning ledger; add V9 limitations without closing inherited items.
warn=read(O/'warning_resolution_ledger.csv')
newwarn=[
{'Warning_ID':'V9-W01','Code':'new_anchor_structure_fields','Description':'New V9 compound rows are resolved by PubChem CID but SMILES/InChI/InChIKey strings were not re-extracted into registry.','Affected':'14 V9 candidate anchors','Classification':'identity traceability','Before':'Not applicable','Action':'PubChem CID/name links checked; no structure string invented.','After':'Partially resolved','Remaining_Limitations':'Follow-up structured PubChem metadata capture and duplicate structure-key audit remain needed.','Resolution_Source':'outputs/v9_selection_decisions.csv','Review_Date':'2026-10-29'},
{'Warning_ID':'V9-W02','Code':'anchor_target_gap','Description':'V9 reaches fewer than 100 defensible anchors after the focused primary-source screen.','Affected':'Stage B anchor registry','Classification':'coverage limitation','Before':'60 anchors','Action':'Added only compounds with direct primary interaction evidence and a documented food/dietary context.','After':'Unresolved','Remaining_Limitations':'26 additional defensible anchors still needed; broader candidate screening remains future work.','Resolution_Source':'outputs/v9_candidate_screening_log.csv','Review_Date':'2026-10-29'},
{'Warning_ID':'V9-W03','Code':'abstract_level_source_verification','Description':'Most new claims were verified from PubMed abstracts; no claim of full-text review is made except the PMID 26139922 table values.','Affected':'V9 evidence rows except table-located items','Classification':'source verification','Before':'Not applicable','Action':'Record-level source locators and verification statuses added.','After':'Partially resolved','Remaining_Limitations':'Full-text review remains appropriate before quantitative integration or clinical interpretation.','Resolution_Source':'outputs/v9_source_audit.csv','Review_Date':'2026-10-29'}]
write(O/'warning_resolution_ledger_v9.csv',warn+newwarn)
# Machine-readable change log.
changes=[]
for r in new_comp: changes.append({'Action':'add_anchor','Record_ID':r['Compound_ID'],'Field':'*','Old_Value':'','New_Value':r['Canonical_Name']+'; PubChem CID '+r['PubChem_CID'],'Reason':r['Selection_Rationale'],'Source':r['Selection_PMID']})
for e in new_e: changes.append({'Action':'add_evidence','Record_ID':e['Evidence_ID'],'Field':'*','Old_Value':'','New_Value':e['Compound']+' / '+e['Drug']+' / PMID '+e['PMID'],'Reason':'Primary-source evidence extraction; limitations captured in row.','Source':e['Source_URL']})
write(O/'v9_change_log.csv',changes)
# Immutable baseline copy and hash control.
if digest(O/'stageB_food_drug_interactions_v8.csv') != base_hash: raise RuntimeError('V8 source table changed during build')
(A/'v9_baseline_hash.json').write_text(json.dumps({'v8_evidence_sha256':base_hash,'v8_rows':len(base_e),'v8_anchors':len(base_r)},indent=2),encoding='utf-8')
print(json.dumps({'baseline_anchors':len(base_r),'baseline_evidence':len(base_e),'new_anchors':len(new_comp),'new_evidence':len(new_e),'final_anchors':len(final_r),'final_evidence':len(final_e),'unique_publications':len(bmap),'new_anchor_names':[r['Canonical_Name'] for r in new_comp],'new_pmids':sorted(meta,key=int),'base_v8_sha256_unchanged':digest(O/'stageB_food_drug_interactions_v8.csv')==base_hash},ensure_ascii=False,indent=2))


