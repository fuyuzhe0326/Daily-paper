Exit code: 0
Wall time: 0.6 seconds
Output:
# Daily Literature Brief Skill

A reusable Codex skill for a daily bilingual literature digest. It searches the previous natural day's papers for **your own research direction**, ranks authoritative Chinese and English journals, creates a dated archive and RIS file, optionally imports lawful full text into Zotero, and emails a plain-text report.

## What it delivers

- A maximum of 10 de-duplicated A/B-tier records each day.
- English title and Chinese translation, original abstract and Chinese translation, authors, journal, metric, DOI/publisher link, methods, findings, topic relevance, and full-text status.
- `YYYY-MM-DD/` archive folders containing `daily_report.txt`, `references.ris`, `daily_index.json`, and `candidates.json`.
- Optional Zotero collection import and Outlook email delivery.

## Install

Copy the `daily-proppant-literature-brief` folder into your Codex skills directory (normally `~/.codex/skills/`) and restart or refresh Codex skills.

## First-use prompt

Paste the following into Codex and replace the brackets:

```text
Use $daily-proppant-literature-brief to configure a daily literature brief.
Research direction: [your research direction and key terms].
Include Chinese journals: [yes/no]. Exclude: [topics to exclude].
Recipient email: [your email].
Send time and timezone: [for example, 08:00 Asia/Shanghai].
Archive directory: [your local directory].
Zotero parent collection: [collection name].
Use my already-authorized Outlook connection and already-authorized institutional access only.
```

Codex should confirm the settings and send a test email before enabling the schedule.

## Access and privacy

The skill never stores account passwords, cookies, access tokens, institutional credentials, or email addresses. It must stop rather than bypass logins, CAPTCHAs, MFA, payments, or copyright restrictions. For unavailable papers, it records a lawful publisher or institutional-access link and the manual next action.

## Local report generator

Run the generator with explicit, user-owned locations:

```powershell
python scripts/daily_digest.py --input candidates.json --run-date 2026-01-31 --archive-root "D:\LiteratureBrief" --recipient "you@example.edu"
```

Validate the generator:

```powershell
python scripts/daily_digest.py --self-test
```

