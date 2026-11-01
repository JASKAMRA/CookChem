"""Consolidate an explicit V12 source into a new release directory."""
from pathlib import Path
import argparse, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]; TOOL=ROOT/"archive"/"scripts"/"consolidate_final.py"; AUTHORITATIVE=(ROOT/"release"/"StageB_Final").resolve()
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("v12_source",type=Path); ap.add_argument("destination",type=Path); a=ap.parse_args()
    src=a.v12_source.resolve(); dst=a.destination.resolve()
    if not src.is_dir(): ap.error("V12 source directory not found")
    if dst==AUTHORITATIVE or AUTHORITATIVE in dst.parents: ap.error("refusing to overwrite or nest in the authoritative release")
    if dst.exists() and any(dst.iterdir()): ap.error("destination must be absent or empty")
    return subprocess.run([sys.executable,str(TOOL),str(src),str(dst)],check=False).returncode
if __name__=="__main__": raise SystemExit(main())
