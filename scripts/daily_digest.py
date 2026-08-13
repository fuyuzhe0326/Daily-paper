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
CHINESE_SOURCES = ("CNKI", "Wanfang", "VIP")

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

def normalize_source_status(value: Any) -> list[dict[str, Any]]:
    """Preserve a per-source audit trail; missing Chinese searches are never zero results."""
    supplied = value if isinstance(value, list) else []
    by_source = {str(item.get("source", "")).strip(): item for item in supplied if isinstance(item, dict)}
    result = []
    for source in CHINESE_SOURCES:
        item = dict(by_source.get(source, {}))
        item.setdefault("source", source)
        item.setdefault("status", "not_run")
        item.setdefault("queries", [])
        item.setdefault("raw_hit_count", None)
        item.setdefault("checked_at", None)
        item.setdefault("reason", "No authorized-session search record was supplied.")
        result.append(item)
    result.extend(item for name, item in by_source.items() if name not in CHINESE_SOURCES)
    return result

def chinese_search_complete(statuses: list[dict[str, Any]]) -> bool:
    chinese = [s for s in statuses if s.get("source") in CHINESE_SOURCES]
    return bool(chinese) and all(str(s.get("status", "")).lower() in {"searched", "zero_results"} for s in chinese)

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
    return "\n".join([f"{n}. 英文标题：{r['title']}", f"　 中文标题对照：{r.get('chinese_title', '待翻译')}", "", f"　 期刊名称：{r.get('journal', '未提供')}", f"　 期刊类型及指标：{r.get('journal_type', '未提供')}；{metric}", f"　 作者：{'; '.join(r.get('authors', [])) or '未提供'}", f"　 首次在线发表：{r.get('online_date', '未核实')}；来源：{r.get('source', '未提供')}", f"　 论文链接：{r.get('url', '未提供')}", "", "　 English abstract:", f"　　{r.get('abstract', '未提供')}", "", "　 中文摘要对照：", f"　　{r.get('chinese_summary', '待翻译')}", "", f"　 方法：{r.get('methods', '摘要未明确')}", f"　 主要发现：{r.get('key_results', '摘要未明确')}", f"　 对本研究方向的推动：{r.get('advance', '待判定')}", f"　 全文状态：{r.get('fulltext_status', 'metadata_only')}"])

def source_status_text(statuses: list[dict[str, Any]]) -> str:
    rows = []
    for status in statuses:
        if status.get("source") not in CHINESE_SOURCES:
            continue
        detail = status.get("reason") or ""
        hits = status.get("raw_hit_count")
        if hits is not None:
            detail = f"{detail} Raw hits: {hits}.".strip()
        rows.append(f"　{status['source']}：{status.get('status', 'not_run')}；{detail}".rstrip("；"))
    return "\n".join(rows)

def report(run_date: str, recipient: str, records: list[dict[str, Any]], statuses: list[dict[str, Any]]) -> str:
    english = [r for r in records if str(r.get("language", "")).lower().startswith("en")]
    chinese = [r for r in records if r not in english]
    lines = [f"文献日报 | {run_date}", "", f"收件人：{recipient}", "", "今日研究进展", "", "未发现符合条件的前一日首次在线发表论文。" if not records else "本日报仅据论文元数据与摘要概括；机制性结论以原文为准。"]
    lines += ["", "中文来源检索状态", "", source_status_text(statuses)]
    for label, group in (("英文期刊", english), ("中文期刊", chinese)):
        if label == "中文期刊" and not group and not chinese_search_complete(statuses):
            empty = "中文检索未完成，不能据此判断无中文文献。请查看上方来源状态并在已授权学校会话中完成检索。"
        else:
            empty = "无符合条件记录。"
        lines += ["", label, "", empty if not group else "\n\n".join(record_text(r, i + 1) for i, r in enumerate(group))]
    pending = [r for r in records if r.get("fulltext_status") not in {"open_access_downloaded", "school_downloaded"}]
    lines += ["", "待处理全文", "", "无。" if not pending else "\n".join(f"{r['title']}：{r.get('fulltext_status', 'manual_required')}；{r.get('school_access_url') or r.get('open_access_url') or r.get('url', '未提供链接')}" for r in pending)]
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
    statuses = normalize_source_status(raw.get("source_status", [])) if isinstance(raw, dict) else normalize_source_status([])
    records = sorted([r for r in deduplicate(records) if str(r.get("online_date", "")) == args.run_date and str(r.get("tier", "C")).upper() in {"A", "B"}], key=score, reverse=True)[:MAX_RECORDS]
    out = args.archive_root / args.run_date; out.mkdir(parents=True, exist_ok=True)
    (out / "candidates.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    index = {"run_date": args.run_date, "recipient": args.recipient, "records": records,
             "source_status": statuses,
             "chinese_search_complete": chinese_search_complete(statuses)}
    (out / "daily_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "references.ris").write_text(ris(records), encoding="utf-8"); (out / "daily_report.txt").write_text(report(args.run_date, args.recipient, records, statuses), encoding="utf-8"); print(out)

if __name__ == "__main__": main()

