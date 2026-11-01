import sys,csv,concurrent.futures
sys.dont_write_bytecode=True
from exact import work,O
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:logs=list(pool.map(work,['10794622','11032486','15309458']))
with (O/'outputs/food_processing_source_log.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(logs[0]));w.writeheader();w.writerows(logs)
