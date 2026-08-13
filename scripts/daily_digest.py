Exit code: 0
Wall time: 0.6 seconds
Output:
#!/usr/bin/env python3
"""Create a configurable dated literature report from normalized JSON."""
from __future__ import annotations

import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

MAX_RECORDS = 10

def norm_doi(value: str) -> str:
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", value.strip(), flags=re.I).lower()

def key(record: dict[str, Any]) -> tuple[str, str]:
    doi = norm_doi(str(record.get("doi", "")))
    title = re.sub(r"\W+", " ", str(record.get("title", "")).lower()).strip()
    return ("doi", doi) if doi else ("title", title)

def score(record: dict[str, Any]) -> int:
    return int(record.get("topic_score", 0)) + {"A": 25, "B": 18}.get(str(record.get("tier", "C")).upper(), 0) + int(record.get("method_score", 0)) + int(record.get("access_score", 0))

def deduplicate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        if record.get("title") and (key(record) not in best or score(record) > score(best[key(record)])):
            best[key(record)] = record
    return list(best.values())

def ris(records: list[dict[str, Any]]) -> str:
    blocks = []
    for r in records:
        lines = ["TY  - JOUR", f"TI  - {r['title']}"]
        lines += [f"AU  - {author}" for author in r.get("authors", [])]
        for tag, field in (("JO", "journal"), ("PY", "online_date"), ("DO", "doi"), ("UR", "url"), ("AB", "abstract")):
            if r.get(field): lines.append(f"{tag}  - {str(r[field]).replace(chr(10), ' ')}")
        blocks.append("\n".join(lines + ["ER  - "]))
    return "\n\n".join(blocks) + ("\n" if blocks else "")

def record_text(r: dict[str, Any], n: int) -> str:
    metric = f"{r.get('impact_metric', 'unavailable')}: {r.get('impact_value', 'unavailable')}" + (f" ({r['impact_year']})" if r.get("impact_year") else "")
    return "\n".join([f"{n}. 鑻辨枃鏍囬锛歿r['title']}", f"銆€ 涓枃鏍囬瀵圭収锛歿r.get('chinese_title', '寰呯炕璇?)}", "", f"銆€ 鏈熷垔鍚嶇О锛歿r.get('journal', '鏈彁渚?)}", f"銆€ 鏈熷垔绫诲瀷鍙婃寚鏍囷細{r.get('journal_type', '鏈彁渚?)}锛泏metric}", f"銆€ 浣滆€咃細{'; '.join(r.get('authors', [])) or '鏈彁渚?}", f"銆€ 棣栨鍦ㄧ嚎鍙戣〃锛歿r.get('online_date', '鏈牳瀹?)}锛涙潵婧愶細{r.get('source', '鏈彁渚?)}", f"銆€ 璁烘枃閾炬帴锛歿r.get('url', '鏈彁渚?)}", "", "銆€ English abstract:", f"銆€銆€{r.get('abstract', '鏈彁渚?)}", "", "銆€ 涓枃鎽樿瀵圭収锛?, f"銆€銆€{r.get('chinese_summary', '寰呯炕璇?)}", "", f"銆€ 鏂规硶锛歿r.get('methods', '鎽樿鏈槑纭?)}", f"銆€ 涓昏鍙戠幇锛歿r.get('key_results', '鎽樿鏈槑纭?)}", f"銆€ 瀵规湰鐮旂┒鏂瑰悜鐨勬帹鍔細{r.get('advance', '寰呭垽瀹?)}", f"銆€ 鍏ㄦ枃鐘舵€侊細{r.get('fulltext_status', 'metadata_only')}"])

def report(run_date: str, recipient: str, records: list[dict[str, Any]]) -> str:
    english = [r for r in records if str(r.get("language", "")).lower().startswith("en")]
    chinese = [r for r in records if r not in english]
    lines = [f"鏂囩尞鏃ユ姤 | {run_date}", "", f"鏀朵欢浜猴細{recipient}", "", "浠婃棩鐮旂┒杩涘睍", "", "鏈彂鐜扮鍚堟潯浠剁殑鍓嶄竴鏃ラ娆″湪绾垮彂琛ㄨ鏂囥€? if not records else "鏈棩鎶ヤ粎鎹鏂囧厓鏁版嵁涓庢憳瑕佹鎷紱鏈哄埗鎬х粨璁轰互鍘熸枃涓哄噯銆?]
    for label, group in (("鑻辨枃鏈熷垔", english), ("涓枃鏈熷垔", chinese)):
        lines += ["", label, "", "鏃犵鍚堟潯浠惰褰曘€? if not group else "\n\n".join(record_text(r, i + 1) for i, r in enumerate(group))]
    pending = [r for r in records if r.get("fulltext_status") not in {"open_access_downloaded", "school_downloaded"}]
    lines += ["", "寰呭鐞嗗叏鏂?, "", "鏃犮€? if not pending else "\n".join(f"{r['title']}锛歿r.get('fulltext_status', 'manual_required')}锛泏r.get('school_access_url') or r.get('open_access_url') or r.get('url', '鏈彁渚涢摼鎺?)}" for r in pending)]
    return "\n".join(lines) + "\n"

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path); p.add_argument("--run-date", default=(date.today() - timedelta(days=1)).isoformat())
    p.add_argument("--archive-root", type=Path, required=False, default=Path("literature-daily-archive")); p.add_argument("--recipient", required=False, default="configured-recipient")
    p.add_argument("--self-test", action="store_true"); args = p.parse_args()
    if args.self_test:
        assert norm_doi("https://doi.org/10.1/ABC") == "10.1/abc"; assert len(deduplicate([{ "title": "One", "doi": "10.1/a"}, {"title": "Two", "doi": "10.1/A", "topic_score": 1}])) == 1; print("self-test passed"); return
    if not args.input: p.error("--input is required unless --self-test is used")
    raw = json.loads(args.input.read_text(encoding="utf-8-sig")); records = raw["records"] if isinstance(raw, dict) else raw
    records = sorted([r for r in deduplicate(records) if str(r.get("online_date", "")) == args.run_date and str(r.get("tier", "C")).upper() in {"A", "B"}], key=score, reverse=True)[:MAX_RECORDS]
    out = args.archive_root / args.run_date; out.mkdir(parents=True, exist_ok=True)
    (out / "candidates.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "daily_index.json").write_text(json.dumps({"run_date": args.run_date, "recipient": args.recipient, "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "references.ris").write_text(ris(records), encoding="utf-8"); (out / "daily_report.txt").write_text(report(args.run_date, args.recipient, records), encoding="utf-8"); print(out)

if __name__ == "__main__": main()

