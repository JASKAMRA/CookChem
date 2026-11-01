import csv,json,urllib.request,concurrent.futures,time
from pathlib import Path
C=Path(__file__).resolve().parents[1]/'sources'
def work(p):
    cid=p.stem.split('_')[1]; out=C/f'synonyms_{cid}.json'
    if out.exists(): return
    try:
        with urllib.request.urlopen(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON',timeout=35) as r: x=json.load(r)
        out.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception as e: out.write_text(json.dumps({'retrieval_error':str(e)}),encoding='utf-8')
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(work,C.glob('pubchem_*.json')))
print('Synonym retrieval finished')
