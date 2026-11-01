"""Create a new V12 staging build from an explicit V11 release copy."""
from pathlib import Path
import argparse, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]; BUILDER=ROOT/"archive"/"scripts"/"build_v12.py"; AUTHORITATIVE=(ROOT/"release"/"StageB_Final").resolve()
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("v11_source",type=Path); ap.add_argument("destination",type=Path); a=ap.parse_args()
    src=a.v11_source.resolve(); dst=a.destination.resolve()
    if not src.is_dir(): ap.error("V11 source directory not found")
    if dst==AUTHORITATIVE or AUTHORITATIVE in dst.parents: ap.error("refusing to overwrite or nest in the authoritative release")
    if dst.exists(): ap.error("destination must not already exist")
    shutil.copytree(src,dst)
    result=subprocess.run([sys.executable,str(BUILDER),str(dst)],check=False)
    if result.returncode: print(f"Build failed; staging copy retained at {dst}",file=sys.stderr)
    return result.returncode
if __name__=="__main__": raise SystemExit(main())
