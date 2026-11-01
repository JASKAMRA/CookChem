import json,urllib.request,urllib.parse,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'sources'
ids=['16133554','18928093','1815977','16767797','11808866','19283724','17963429','30611786','31321577','19190249','23920278','34303263','29480324','10606838','14725610','8807660','17442681','22725836','19221726','21680781','25624269']
queries=['EXT_ID:'+i+' AND SRC:MED' for i in ids]+['TITLE:"Repeated administration of berberine inhibits cytochromes P450 in humans"','TITLE:"Impact of Curcumin" AND TITLE:Tamoxifen','TITLE:"The effect of piperine on midazolam plasma"','TITLE:"Fluvoxamine impairs single-dose caffeine"','TITLE:"Interaction between oral ciprofloxacin and caffeine"','TITLE:"Preclinical evaluation" AND TITLE:bortezomib AND TITLE:epigallocatechin','DOI:10.1002/jps.24500','DOI:10.3390/molecules26175171','DOI:10.1631/jzus.B0920051','DOI:10.1002/jsfa.6546']
queries+=['EXT_ID:31060206 AND SRC:MED','EXT_ID:27981349 AND SRC:MED','EXT_ID:22512082 AND SRC:MED','DOI:10.1016/j.jfca.2006.10.002','DOI:10.1016/0308-8146(92)90211-J','DOI:10.1016/j.jfoodeng.2008.10.018']
for n,q in enumerate(queries):
    p=C/f'selected_{n:02}.json'
    if not p.exists():
        u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':5})
        try:
            with urllib.request.urlopen(u,timeout=40) as r: result=json.load(r)
            p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        except Exception as e: print(q,str(e)); continue
    result=json.loads(p.read_text(encoding='utf-8'))
    for r in result.get('resultList',{}).get('result',[]):
        pmc=r.get('pmcid')
        if pmc and r.get('isOpenAccess')=='Y' and not (C/(pmc+'.xml')).exists():
            try:
                with urllib.request.urlopen(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML',timeout=40) as response: xml=response.read()
                (C/(pmc+'.xml')).write_bytes(xml)
            except Exception: pass
print('Selected-source cache ready')
