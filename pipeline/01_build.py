"""Join the book reviews to their settings and write the atlas dataset.

Sources, all local:
  travel-in-books.github.io/_posts      191 Persian reviews (title, author, year, country, rating)
  temporal_literature_investigator/data books.jsonl, per-book profiles, per-country-decade history
"""
import json, os, re, sys, glob, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gazetteer

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TLI = os.path.abspath(os.path.join(ROOT, "..", "temporal_literature_investigator", "data"))
POSTS = os.path.abspath(os.path.join(ROOT, "..", "travel-in-books.github.io", "_posts"))
OUT = os.path.join(ROOT, "docs", "data")
os.makedirs(OUT, exist_ok=True)

FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")


def fa_int(s):
    if not s:
        return None
    m = re.search(r"[\d۰-۹]{3,4}", s.translate(FA_DIGITS))
    return int(m.group()) if m else None


def parse_post(path):
    """Pull the metadata table and front matter out of one review."""
    raw = open(path, encoding="utf-8").read()
    fm = {}
    if raw.startswith("---"):
        end = raw.index("---", 3)
        head, body = raw[3:end], raw[end + 3:]
        for line in head.split("\n"):
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
    else:
        body = raw

    row = {}
    for m in re.finditer(r"^\|\s*([^|\n]+?)\s*\|\s*([^|\n]*?)\s*\|\s*$", body, re.M):
        row[m.group(1).strip()] = m.group(2).strip()

    tags = fm.get("tags", "")
    rating = None
    rm = re.search(r"(\d+)\s*/\s*10", tags)
    if rm:
        rating = int(rm.group(1))
    else:
        rm2 = re.search(r"score=(\d+)", body)
        if rm2:
            rating = int(rm2.group(1))

    slug = os.path.basename(path)[:-3]
    return {
        "slug": slug,
        "date": slug[:10],
        "title_fa": fm.get("title", "").strip(),
        "title_en": row.get("نام اصلی اثر", "").strip(),
        "author": row.get("نویسنده", "").strip(),
        "year": fa_int(row.get("سال چاپ", "")),
        "country": row.get("کشور", "").strip(),
        "genre": row.get("ژانر", "").strip(),
        "pages": fa_int(row.get("تعداد صفحات", "")),
        "rating": rating,
        "url": "https://travel-in-books.github.io/posts/" + slug[11:] + "/",
    }


def clip(s, n):
    if not s:
        return ""
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def main():
    books = [parse_post(p) for p in sorted(glob.glob(os.path.join(POSTS, "*.md")))]
    print(f"parsed {len(books)} reviews")

    profiles = {}
    for p in glob.glob(os.path.join(TLI, "profiles", "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        profiles[d.get("slug") or os.path.basename(p)[:-5]] = d
    print(f"loaded {len(profiles)} setting profiles")

    history = {}
    for p in glob.glob(os.path.join(TLI, "history", "*.json")):
        key = os.path.basename(p)[:-5]
        try:
            history[key] = json.load(open(p, encoding="utf-8"))
        except Exception:
            pass
    print(f"loaded {len(history)} country/decade history files")

    placed = unplaced = noprofile = 0
    out = []
    for b in books:
        pr = profiles.get(b["slug"], {})
        setting = pr.get("setting_place")
        loc = None
        if setting and not gazetteer.is_unplaceable(setting):
            loc = gazetteer.locate(setting)
        if loc is None and setting:
            loc = gazetteer.locate(setting)     # try anyway; fiction often names a real anchor
        if loc is None and b["country"]:
            loc = None                           # publication country is not a setting; leave it

        rec = dict(b)
        rec.update({
            "setting": clip(setting, 150) if setting else None,
            "setting_start": pr.get("setting_start"),
            "setting_end": pr.get("setting_end"),
            "themes": (pr.get("themes") or [])[:5],
            "backdrop": clip(pr.get("historical_backdrop"), 420),
            "synopsis": clip(pr.get("plot_synopsis"), 420),
            "confidence": pr.get("confidence"),
        })
        if loc:
            rec.update(loc); placed += 1
        else:
            rec["place"] = None
            if not pr:
                noprofile += 1
            else:
                unplaced += 1
        out.append(rec)

    print(f"placed on the map: {placed}")
    print(f"has a profile but no findable place: {unplaced}")
    print(f"no profile at all: {noprofile}")

    json.dump({"books": out, "history": history},
              open(os.path.join(OUT, "atlas.json"), "w"),
              ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(os.path.join(OUT, "atlas.json"))
    print(f"wrote atlas.json: {size/1e6:.2f} MB")

    # a quick look at what the map will show
    from collections import Counter
    c = Counter(r["place"] for r in out if r.get("place"))
    print("\nmost-visited settings:", ", ".join(f"{k} ({v})" for k, v in c.most_common(8)))
    gaps = [(r["year"] - r["setting_start"], r["title_en"]) for r in out
            if r.get("setting_start") and r.get("year")]
    gaps.sort(reverse=True)
    print("\nlargest gap between when a book is set and when it was written:")
    for g, t in gaps[:5]:
        print(f"   {g:4d} years   {clip(t, 60)}")


if __name__ == "__main__":
    main()
