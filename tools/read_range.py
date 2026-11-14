"""Read Gedimat's range from its sitemap files as fetched: python tools/read_range.py <folder of sitemap files>.
Writes gedimat_unofficial/range.json, and the entries the rows come from, with the sha256 of each sitemap file, to the
private copy in xag/furniture (sources/gedimat/sitemap-entries.json)."""

import hashlib
import json
import os
import sys
from pathlib import Path

from wood_panels.shops import entries, rows_of

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path(os.environ.get("FURNITURE_REPO", ROOT.parent / "furniture")) / "sources" / "gedimat"
SKIP = None

found, shas = [], {}
for f in sorted(Path(sys.argv[1]).glob("*")):
    data = f.read_bytes()
    shas[f.name] = hashlib.sha256(data).hexdigest()
    found += entries(data.decode("utf-8", "ignore"), f.name)
rows, kept = rows_of(found, (lambda u: SKIP in u) if SKIP else (lambda u: False))
used = {r["sitemap"] for r in rows}
(ROOT / "gedimat_unofficial" / "range.json").write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
PRIVATE.mkdir(parents=True, exist_ok=True)
(PRIVATE / "sitemap-entries.json").write_text(json.dumps(
    {"fetched": sys.argv[2] if len(sys.argv) > 2 else "", "index": "https://www.gedimat.fr/sitemap.php",
     "sitemaps": {k: v for k, v in shas.items() if k in used}, "entries": kept}, ensure_ascii=False, indent=0),
    encoding="utf-8")
print(len(rows), "products")
