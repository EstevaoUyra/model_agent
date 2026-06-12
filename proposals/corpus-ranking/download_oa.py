import csv, json, subprocess, urllib.request, urllib.parse, os, re

# map key->doi from the build data
import importlib.util
spec = importlib.util.spec_from_file_location("b","proposals/corpus-ranking/build_ranking.py")
# build_ranking writes files on import; avoid that by reading ROWS via exec of just the data is hard.
# Simpler: reread DOIs from the 200 md is messy; instead parse build script ROWS.
src = open("proposals/corpus-ranking/build_ranking.py").read()
ns = {}
# execute up to the ROWS definition by exec'ing whole file but suppressing file writes via cwd trick is risky;
# instead extract ROWS list literally:
m = re.search(r"ROWS = \[(.*?)\n\]\n", src, re.S)
rows = eval("[" + m.group(1) + "]")
COLS = ["key","label","venue","year","doi","cluster","cites","oa","link","code","fig","compute","repro","corpus","lineage"]
doi = {r[0]: r[4] for r in rows}

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
def openalex_pdf(d):
    if not d: return None
    try:
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(d)}?mailto=estevao.uyra.pv@gmail.com"
        req = urllib.request.Request(url, headers={"User-Agent":UA})
        j = json.load(urllib.request.urlopen(req, timeout=30))
        loc = j.get("best_oa_location") or j.get("primary_location") or {}
        return loc.get("pdf_url") or (j.get("open_access") or {}).get("oa_url")
    except Exception as e:
        return None

ok, fail = [], []
with open("proposals/corpus-ranking/downloads.tsv") as f:
    items = [l.strip().split("\t") for l in f if l.strip()]

for rank, key, link in items:
    out = f"paper_candidates/{rank}_{key}.pdf"
    if os.path.exists(out) and os.path.getsize(out) > 20000:
        ok.append((rank,key,"cached")); continue
    pdf = openalex_pdf(doi.get(key)) or (link if link.endswith(".pdf") else None)
    tried = []
    for u in [pdf, link]:
        if not u: continue
        tried.append(u)
        r = subprocess.run(["curl","-sL","--max-time","60","-A",UA,"-o",out,u])
        if os.path.exists(out) and os.path.getsize(out) > 20000:
            # verify PDF magic
            with open(out,"rb") as fh: head = fh.read(5)
            if head.startswith(b"%PDF"):
                ok.append((rank,key,u)); break
            else:
                os.remove(out)
    else:
        fail.append((rank,key,doi.get(key)))

print(f"DOWNLOADED {len(ok)} / {len(items)}")
for r,k,u in ok: print(f"  ok  {r} {k}")
print(f"FAILED {len(fail)} (fetch via institution or manually):")
for r,k,d in fail: print(f"  --  {r} {k}  doi:{d}")
