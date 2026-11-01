from pathlib import Path
import hashlib,subprocess,sys,json
O=Path(__file__).resolve().parent
def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((O/'outputs').glob('*')) if p.suffix in ['.csv','.json']}
before=hashes();subprocess.run([sys.executable,'-X','utf8',str(O/'build.py')],check=True,stdout=subprocess.DEVNULL);after=hashes()
changed=[k for k in before if before[k]!=after.get(k)]
(O/'audit/rebuild_verification.json').write_text(json.dumps(dict(status='PASS' if before==after else 'FAIL',output_files_compared=len(before),changed=changed,scope='Offline rebuild from cached sources; byte-identical generated CSV and JSON outputs'),indent=2),encoding='utf8')
print('Offline rebuild:',len(before),'files, changes:',changed);assert before==after
