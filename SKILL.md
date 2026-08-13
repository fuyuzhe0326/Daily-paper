Exit code: 0
Wall time: 0.7 seconds
Output:
---
name: daily-proppant-literature-brief
description: Create a configurable daily Chinese-English literature brief for a user-defined research topic. Use when Codex needs to discover previous-day papers, rank high-authority Chinese and English journals, archive RIS and a daily index, obtain lawful full text, import into Zotero, or email a literature digest at a user-selected local time.
---

# Configurable daily literature brief

## First use

Ask for and confirm the following before creating an automation:

- Research topic, required and excluded terms, and whether Chinese journals are required.
- Recipient email address.
- Archive directory and Zotero parent collection name.
- Whether an already-authorized Outlook connection is available.

Never put these values, passwords, cookies, institutional account details, or tokens in this skill. Store only non-sensitive settings in a user-local configuration file.

## Daily procedure

1. Compute the preceding natural day in the configured timezone.
2. Search Crossref and publisher metadata first, using the configured bilingual terms. Search CNKI, Wanfang, and VIP only through an already-authorized institutional session. For each Chinese source, record the query, URL, check time, raw hit count, and exactly one status: `searched`, `zero_results`, `session_unavailable`, `login_required`, `captcha_blocked`, `access_denied`, or `not_run`.
3. Retain peer-reviewed journal articles directly matching the configured topic. Verify the publisher's first online date; do not substitute issue or database dates.
4. Rank by topic match, journal tier, method/result specificity, and lawful full-text availability. Retain A/B-tier journals by default and at most ten articles.
5. For each retained record, provide title translation, authors, journal/type, a traceable JCR impact factor or clearly named proxy metric, DOI/publisher URL, source abstract, Chinese abstract translation, methods, findings, and a bounded statement of relevance to the configured topic.
6. Save the per-source records beside `records` in the input JSON as `source_status`, then run `scripts/daily_digest.py` with explicit `--archive-root` and `--recipient`. Inspect `daily_report.txt`, `daily_index.json`, and `references.ris`. Never describe a day as having no Chinese literature unless every configured Chinese source completed as `searched` or `zero_results`.
7. Download only lawfully available OA PDFs. Use an existing institutional browser session only; stop at login, CAPTCHA, MFA, payment, or licensing barriers. Use a document-delivery service only in an existing permitted session.
8. Import RIS and lawful PDFs into the configured Zotero parent/date collection only after the local API is confirmed available. Create or verify the parent collection before the date subcollection; record imported item keys in the daily index and avoid repeat items after a failed retry. If the local API is unavailable, retain `references.ris` and clearly state that manual Zotero import is pending.
9. Send the complete plain-text report in the Outlook email body only after authorization is available. Do not attach the report unless the user asks.

## Reporting rules

- Separate English and Chinese journal records; give English title plus Chinese title, then English abstract followed by Chinese translation.
- Begin prose paragraphs with two full-width spaces and leave blank lines between records.
- State zero results honestly; do not fill a day with older articles.
- If Chinese-source status is incomplete, state that the Chinese search was not completed and that no conclusion about Chinese literature can be drawn. Do not silently display `鏃犵鍚堟潯浠惰褰昤.
- Mark unverified indexing/metrics, unavailable full text, and manual steps explicitly.
- Do not claim a paper proves a mechanism beyond its reported methods and results.

Read `references/workflow.md` for ranking and access rules. Use `scripts/daily_digest.py --self-test` to validate the bundled generator.

Read `references/example-output.md` only when the user asks what a finished brief looks like. Keep examples de-identified and distinguish direct study evidence from a proposed application to the user's direction.

