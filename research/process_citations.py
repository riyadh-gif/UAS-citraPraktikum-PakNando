"""Dedupe S2 raw results, select 20 diverse high-quality refs, emit bib/md/json."""
import json, re, glob, os, unicodedata

THEMES = [
    "stair detection", "stair-climbing robot", "RANSAC plane segmentation",
    "RANSAC 3D fitting", "PCA normal estimation", "DBSCAN clustering",
    "Euclidean clustering", "region growing", "LiDAR ground segmentation",
    "traversability legged robot", "deep point-cloud segmentation",
    "elevation mapping", "plane detection LiDAR SLAM", "semantic 3D segmentation",
]

raw_files = sorted(glob.glob("research/raw/q*.json"),
                   key=lambda p: int(re.findall(r"q(\d+)", p)[0]))
papers = {}  # paperId -> record (with theme index of first appearance)
for qi, fp in enumerate(raw_files):
    data = json.load(open(fp, encoding="utf-8"))
    for p in data.get("data", []):
        pid = p.get("paperId")
        if not pid or not p.get("title") or not p.get("year") or not p.get("authors"):
            continue
        if pid not in papers:
            p["_theme"] = qi
            papers[pid] = p

pool = list(papers.values())

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())

def first_author_last(p):
    name = p["authors"][0]["name"]
    return slug(name.split()[-1]) or "anon"

def title_word(p):
    stop = {"a","an","the","of","for","and","on","in","to","using","based",
            "with","from","via","towards","toward"}
    for w in re.findall(r"[A-Za-z]+", p["title"]):
        if w.lower() not in stop and len(w) > 2:
            return slug(w)
    return "paper"

# Score: citation count (log-damped) + recency nudge; keep per-theme coverage.
import math
def score(p):
    cc = p.get("citationCount", 0) or 0
    return math.log1p(cc) + 0.02 * (p.get("year", 2000) - 2000)

# 1) ensure >=1 per theme (best-scored), 2) fill remaining by global score.
by_theme = {}
for p in pool:
    by_theme.setdefault(p["_theme"], []).append(p)
for t in by_theme:
    by_theme[t].sort(key=score, reverse=True)

selected, seen = [], set()
for t in sorted(by_theme):
    for p in by_theme[t]:
        if p["paperId"] not in seen:
            selected.append(p); seen.add(p["paperId"]); break

remaining = sorted((p for p in pool if p["paperId"] not in seen),
                   key=score, reverse=True)
for p in remaining:
    if len(selected) >= 20:
        break
    selected.append(p); seen.add(p["paperId"])

selected = selected[:20]
selected.sort(key=lambda p: (p.get("year", 0), score(p)), reverse=True)

# Build unique cite keys.
keys = {}
def make_key(p):
    base = f"{first_author_last(p)}{p['year']}{title_word(p)}"
    k = base; n = 1
    while k in keys:
        n += 1; k = f"{base}{chr(96+n)}"
    keys[k] = p
    return k

def bib_type(p):
    pts = p.get("publicationTypes") or []
    ven = (p.get("venue") or "").lower()
    if "JournalArticle" in pts or any(w in ven for w in ["journal","transactions","access","letters","sensors","remote sensing"]):
        return "article", "journal"
    if "Conference" in pts or any(w in ven for w in ["conference","proceedings","symposium","icra","iros","cvpr","workshop"]):
        return "inproceedings", "booktitle"
    return "misc", "howpublished"

def esc(s):
    return (s or "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_")

bib_lines, md_lines, json_out = [], [], []
md_lines.append("# Citation pool (20 refs) — use ONLY these \\cite keys\n")
for p in selected:
    key = make_key(p)
    btype, vfield = bib_type(p)
    authors = " and ".join(a["name"] for a in p["authors"])
    doi = (p.get("externalIds") or {}).get("DOI", "")
    venue = p.get("venue") or "Preprint / unpublished"
    entry = [f"@{btype}{{{key},",
             f"  author = {{{esc(authors)}}},",
             f"  title = {{{esc(p['title'])}}},",
             f"  {vfield} = {{{esc(venue)}}},",
             f"  year = {{{p['year']}}},"]
    if doi:
        entry.append(f"  doi = {{{doi}}},")
    entry.append("}")
    bib_lines.append("\n".join(entry))

    abst = (p.get("abstract") or "").strip().replace("\n", " ")
    abst = (abst[:240] + "…") if len(abst) > 240 else abst
    md_lines.append(
        f"- **{key}** ({p['year']}, {venue}; cites={p.get('citationCount',0)}) "
        f"[theme: {THEMES[p['_theme']]}]\n  - {p['title']}\n  - {abst or 'no abstract'}")
    json_out.append({"key": key, "title": p["title"], "authors": authors,
                     "year": p["year"], "venue": venue, "doi": doi,
                     "citationCount": p.get("citationCount", 0),
                     "theme": THEMES[p["_theme"]], "abstract": p.get("abstract")})

os.makedirs("report", exist_ok=True)
open("report/refs.bib", "w", encoding="utf-8").write("\n\n".join(bib_lines) + "\n")
open("research/citations.md", "w", encoding="utf-8").write("\n".join(md_lines) + "\n")
json.dump(json_out, open("research/citations.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print(f"Selected {len(selected)} refs. Themes covered: "
      f"{len(set(p['_theme'] for p in selected))}/{len(THEMES)}")
print("Keys:", ", ".join(keys))
