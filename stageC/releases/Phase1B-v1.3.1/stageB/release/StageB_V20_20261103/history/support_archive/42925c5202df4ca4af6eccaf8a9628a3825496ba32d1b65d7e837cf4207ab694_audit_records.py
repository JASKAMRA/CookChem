from pathlib import Path
import csv,json,re,html,collections
from decimal import Decimal
O=Path(__file__).resolve().parent;B=O.parent;V=B/'release_v7_20261015_clean'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def nums(t):return {str(Decimal(x).normalize()) for x in re.findall(r'(?:\d+(?:\.\d+)?|\.\d+)',html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',t)).replace(',',''))}
def norm(t):return re.sub('[^a-z0-9]','',html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',str(t))).lower())
e=read(V/'outputs/stageB_food_drug_interactions_v7.csv');rev={x['Evidence_ID']:x for x in read(V/'outputs/all_record_review_audit.csv')};audit=[]
for x in e:
 p=B/x['Source_Cache'];d=json.loads(p.read_text(encoding='utf8'));h=next((a for a in d.get('resultList',{}).get('result',[]) if str(a.get('id'))==x['PMID']),{})
 miss=nums(x['Quantitative_Outcome'])-nums(h.get('abstractText',''));audit.append(dict(Evidence_ID=x['Evidence_ID'],Compound=x['Compound'],Drug=x['Drug'],PMID=x['PMID'],PMCID=h.get('pmcid',''),Type=x['Evidence_Type'],Previous_Review=rev[x['Evidence_ID']]['Verification_Level'],Metadata_Matches=all(norm(x[k])==norm(h.get(v,'')) for k,v in [('Source_Title','title'),('Authors','authorString'),('Year','pubYear'),('DOI','doi')]),Quantity=x['Quantitative_Outcome'],Abstract_Numeric_Tokens_Missing=' | '.join(sorted(miss)),Diagnostic='Missing numeric tokens are review flags, not automatic proof of unsupported outcome',Source=x['Source_Cache']))
with (O/'outputs/all_record_pre_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
print('Metadata mismatches',[(x['Evidence_ID'],x['PMID']) for x in audit if not x['Metadata_Matches']]);print('Numerical flags')
for x in audit:
 if x['Abstract_Numeric_Tokens_Missing']:print(x['Evidence_ID'],x['Compound'],x['Drug'],x['PMID'],x['PMCID'],x['Abstract_Numeric_Tokens_Missing'],x['Quantity'])
print('Human records with full-text candidate metadata')
for x in audit:
 if x['Type'] in ['Human pharmacokinetic','Controlled clinical'] and x['PMCID'] and x['Previous_Review']!='full_text_selected':print(x['Evidence_ID'],x['Compound'],x['Drug'],x['PMID'],x['PMCID'])
