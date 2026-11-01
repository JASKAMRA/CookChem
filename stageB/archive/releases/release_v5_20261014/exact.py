from pathlib import Path
import json,csv,urllib.request,urllib.parse,concurrent.futures
O=Path(__file__).resolve().parent
IDS=['21442417','28185989','22132944','21380815','27875319','28766866','21704146','33435470','15592332','16003560','21697612','27396204','18446505','26530401','27098862','23883365','11792681','12554070','34144662','30678660','24472704','22114872','23422925','17468862','30590119','34138683','12587952']
def get(url,p,xml=False):
    if p.exists():return p.read_bytes() if xml else json.loads(p.read_text(encoding='utf8'))
    try:
        with urllib.request.urlopen(url,timeout=45) as f:b=f.read()
        if xml:p.write_bytes(b);return b
        d=json.loads(b)
    except Exception as e:d={'retrieval_error':str(e),'url':url}
    (p.with_suffix(p.suffix+'.error.json') if xml else p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8');return d
def work(pmid):
    q=f'EXT_ID:{pmid} AND SRC:MED';url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'resultType':'core','format':'json'});p=O/'sources'/f'pmid_{pmid}.json';d=get(url,p);hits=d.get('resultList',{}).get('result',[])
    if hits:
        m=hits[0];doi=m.get('doi','')
        if doi:get('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''),O/'sources'/f'crossref_{pmid}.json')
        if m.get('pmcid'):get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+m['pmcid']+'/fullTextXML',O/'sources'/(m['pmcid']+'.xml'),True)
    return dict(PMID=pmid,Query=q,Date='2026-10-14',URL=url,Cache=p.relative_to(O).as_posix(),Level='Exact primary metadata; XML availability is not review')
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:logs=list(pool.map(work,IDS))
    with (O/'outputs/exact_source_log.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(logs[0]));w.writeheader();w.writerows(logs)
    get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/932/property/IUPACName,MolecularFormula,InChI,InChIKey,CanonicalSMILES/JSON',O/'sources/identity_naringenin_parent.json')
    get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/932/synonyms/JSON',O/'sources/synonyms_naringenin_parent.json')
    print('Exact sources',len(logs))
