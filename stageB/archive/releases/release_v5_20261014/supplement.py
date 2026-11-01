import sys,json,csv,concurrent.futures
sys.dont_write_bytecode=True
from exact import work,O
IDS=['26884726','27765854','26692948','12920504']
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:logs=list(pool.map(work,IDS))
with (O/'outputs/exact_source_log.csv').open(encoding='utf-8-sig',newline='') as f:old=list(csv.DictReader(f))
with (O/'outputs/exact_source_log.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(logs[0]));w.writeheader();w.writerows(old+logs)
print('Additional primary papers',len(logs))
