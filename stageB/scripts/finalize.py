"""Finalize an explicitly named staging copy using the archived V12 finalizer."""
from pathlib import Path
import argparse, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]; FINALIZER=ROOT/"archive"/"scripts"/"finalize_v12.py"; AUTHORITATIVE=(ROOT/"release"/"StageB_Final").resolve()
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("candidate",type=Path,help="staging release directory to finalize in place"); a=ap.parse_args()
    candidate=a.candidate.resolve()
    if candidate==AUTHORITATIVE or AUTHORITATIVE in candidate.parents: ap.error("refusing to modify the authoritative release")
    if not candidate.is_dir(): ap.error("candidate directory must already exist")
    return subprocess.run([sys.executable,str(FINALIZER),str(candidate),str(ROOT/"archive"/"scripts")],check=False).returncode
if __name__=="__main__": raise SystemExit(main())
