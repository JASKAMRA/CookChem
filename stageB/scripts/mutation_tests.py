"""Run integrity mutation checks on an isolated copy of the final release."""
from pathlib import Path
import runpy, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]; RELEASE=ROOT/"release"/"StageB_Final"
LEGACY=ROOT/"archive"/"scripts"
def main():
    sys.path.insert(0,str(LEGACY))
    with tempfile.TemporaryDirectory(prefix="stageb_mutation_",dir=ROOT/"validation") as td:
        work=Path(td)/"StageB_Final"; shutil.copytree(RELEASE,work)
        namespace=runpy.run_path(str(LEGACY/"mutation_test_final.py"),run_name="stageb_mutation_runner")
        status=namespace["main"](str(work))
        for name in ("final_mutation_test_results.json","final_mutation_test_results.csv"):
            shutil.copy2(work/"validation"/name,ROOT/"validation"/name)
    return status
if __name__=="__main__": raise SystemExit(main())

