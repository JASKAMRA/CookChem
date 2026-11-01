"""Validate the authoritative Stage B release without modifying it."""
from pathlib import Path
import importlib.util, json, shutil, tempfile
ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT/"release"/"StageB_Final"
LEGACY=ROOT/"archive"/"scripts"/"validate_final.py"
def main():
    spec=importlib.util.spec_from_file_location("stageb_validator", LEGACY)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="stageb_validate_",dir=ROOT/"validation") as td:
        work=Path(td)/"StageB_Final"; shutil.copytree(RELEASE,work)
        status=module.main(str(work))
        for name in ("final_validation_results.json","final_validation_results.csv"):
            shutil.copy2(work/"validation"/name,ROOT/"validation"/name)
    return status
if __name__=="__main__": raise SystemExit(main())

