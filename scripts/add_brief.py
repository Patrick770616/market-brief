#!/usr/bin/env python3
"""Add one brief to the site: copies it into briefs/ and updates briefs/index.json.

Usage: python3 scripts/add_brief.py path/to/<id>.json
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
brief = json.load(open(src, encoding="utf-8"))
bid = brief.get("id", "")
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-(pre|post)", bid):
    sys.exit(f"bad id: {bid!r}")
for s in brief.get("sections") or []:
    for it in s.get("items") or []:
        it["ticker"] = str(it.get("ticker", "")).strip().upper()

os.makedirs(os.path.join(ROOT, "briefs"), exist_ok=True)
with open(os.path.join(ROOT, "briefs", bid + ".json"), "w", encoding="utf-8") as f:
    json.dump(brief, f, ensure_ascii=False, indent=1)

idx_path = os.path.join(ROOT, "briefs", "index.json")
try:
    idx = json.load(open(idx_path, encoding="utf-8"))
except FileNotFoundError:
    idx = {"briefs": []}
entries = [e for e in idx.get("briefs", []) if e.get("id") != bid and not e.get("sample")]
entries.append({"id": bid, "date": brief.get("date", ""), "edition": brief.get("edition", ""),
                "headline": (brief.get("lead") or {}).get("headline", "")})
entries.sort(key=lambda e: e["id"], reverse=True)
# 只保留和這一期同一天的快訊（盤前、盤後），其他日期的刪掉
day = bid[:10]
keep = [e for e in entries if e["id"].startswith(day)]
drop = [e for e in entries if not e["id"].startswith(day)]
for e in drop:
    try: os.remove(os.path.join(ROOT, "briefs", e["id"] + ".json"))
    except FileNotFoundError: pass
with open(idx_path, "w", encoding="utf-8") as f:
    json.dump({"briefs": keep}, f, ensure_ascii=False, indent=1)
print(f"added {bid}; {len(keep)} briefs listed")
