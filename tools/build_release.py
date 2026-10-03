"""Build an identical source ZIP on every run, with SHA-256 integrity metadata."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def build(target):
    target=Path(target); target.mkdir(parents=True,exist_ok=True)
    archive=target/'data-job.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in ['data_job.py','README.md']:
            info=zipfile.ZipInfo(name,date_time=(2020,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(ROOT/name).read_bytes())
    manifest={'artifact':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
if __name__=='__main__':
    import sys
    print(build(sys.argv[1] if len(sys.argv)>1 else ROOT/'dist'))
