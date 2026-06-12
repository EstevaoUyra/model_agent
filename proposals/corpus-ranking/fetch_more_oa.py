import json, os, subprocess, urllib.request, urllib.parse, time

EMAIL = "estevao.uyra.pv@gmail.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15"
OUT = "paper_candidates"
os.makedirs(OUT, exist_ok=True)

papers = json.load(open("proposals/corpus-candidates-200.json"))["papers"]
# target: open-access papers not already on disk
def on_disk(fn):
    p = os.path.join(OUT, fn)
    if os.path.exists(p) and os.path.getsize(p) > 20000:
        return open(p,'rb').read(4).startswith(b'%PDF')
    return False

def get(url, timeout=25):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        return urllib.request.urlopen(req, timeout=timeout).read()
    except Exception:
        return None

def unpaywall_pdfs(doi):
    if not doi: return []
    data = get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={EMAIL}")
    if not data: return []
    try: j = json.loads(data)
    except Exception: return []
    urls = []
    locs = (j.get("oa_locations") or [])
    best = j.get("best_oa_location")
    if best: locs = [best] + locs
    for loc in locs:
        if not loc: continue
        for k in ("url_for_pdf", "url"):
            u = loc.get(k)
            if u and u not in urls: urls.append(u)
    return urls

def try_download(urls, dest):
    for u in urls:
        if not u: continue
        r = subprocess.run(["curl","-sL","--max-time","60","-A",UA,"-o",dest,u],
                           capture_output=True)
        if os.path.exists(dest) and os.path.getsize(dest) > 20000:
            with open(dest,"rb") as fh:
                if fh.read(5).startswith(b"%PDF"):
                    return u
        if os.path.exists(dest): os.remove(dest)
    return None

targets = [p for p in papers if p["is_open_access"] and not on_disk(p["pdf_filename"])]
print(f"OA papers not yet on disk: {len(targets)}")
ok, fail = [], []
for i, p in enumerate(targets, 1):
    fn = p["pdf_filename"]; dest = os.path.join(OUT, fn)
    cands = unpaywall_pdfs(p.get("doi"))
    # fall back to the stored OA link
    if p.get("url"): cands.append(p["url"])
    got = try_download(cands, dest)
    if got:
        ok.append((fn, got)); print(f"  [{i}/{len(targets)}] OK   {fn}")
    else:
        fail.append((fn, p.get("doi"))); print(f"  [{i}/{len(targets)}] miss {fn}  ({len(cands)} urls tried)")
    time.sleep(0.3)

print(f"\n=== fetched {len(ok)} new / {len(targets)} OA-not-on-disk ===")
print(f"still missing ({len(fail)}):")
for fn, doi in fail: print(f"  -- {fn}  doi:{doi}")
