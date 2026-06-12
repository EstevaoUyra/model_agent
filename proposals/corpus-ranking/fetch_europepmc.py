import json, os, subprocess, urllib.request, urllib.parse, time
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15"
OUT = "paper_candidates"
papers = json.load(open("proposals/corpus-candidates-200.json"))["papers"]
def on_disk(fn):
    p = os.path.join(OUT, fn)
    return os.path.exists(p) and os.path.getsize(p) > 20000 and open(p,'rb').read(4).startswith(b'%PDF')
def get(url, t=25):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":UA}), timeout=t).read()
    except Exception: return None
def pmcid(doi):
    if not doi: return None
    q = urllib.parse.quote(f'DOI:"{doi}"')
    d = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&pageSize=1")
    if not d: return None
    try:
        res = json.loads(d).get("resultList",{}).get("result",[])
        return res[0].get("pmcid") if res else None
    except Exception: return None
def try_dl(url, dest):
    subprocess.run(["curl","-sL","--max-time","90","-A",UA,"-o",dest,url], capture_output=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 20000 and open(dest,"rb").read(5).startswith(b"%PDF"):
        return True
    if os.path.exists(dest): os.remove(dest)
    return False

targets = [p for p in papers if p["is_open_access"] and not on_disk(p["pdf_filename"])]
print(f"OA still-missing: {len(targets)}")
ok, fail = [], []
for i,p in enumerate(targets,1):
    fn=p["pdf_filename"]; dest=os.path.join(OUT,fn)
    pid = pmcid(p.get("doi"))
    got=False
    if pid:
        for u in [f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pid}/fullTextPDF",
                  f"https://europepmc.org/articles/{pid}?pdf=render"]:
            if try_dl(u,dest): got=True; break
    if got: ok.append(fn); print(f"  [{i}/{len(targets)}] OK   {fn}  ({pid})")
    else: fail.append(fn); print(f"  [{i}/{len(targets)}] miss {fn}  (pmcid={pid})")
    time.sleep(0.25)
print(f"\n=== EuropePMC recovered {len(ok)} more ===")
