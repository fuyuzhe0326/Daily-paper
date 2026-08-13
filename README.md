Exit code: 0
Wall time: 0.6 seconds
Output:
# Daily paper

> A configurable Codex skill that turns the previous day's high-quality literature into a bilingual, research-relevant email brief.

```mermaid
flowchart LR
    A["检索<br/>前一自然日文献"] --> B["筛选与去重<br/>期刊等级 · DOI · 相关性"]
    B --> C["双语解读<br/>摘要 · 方法 · 研究推动"]
    C --> D["邮件与归档<br/>Outlook · RIS · Zotero"]
```

`Daily paper` searches the previous natural day's papers for **your own research direction**, ranks authoritative Chinese and English journals, creates a dated archive and RIS file, optionally imports lawfully available full text into Zotero, and emails a readable plain-text report.

## What it delivers

- A maximum of 10 de-duplicated A/B-tier records each day.
- English title and Chinese translation, original abstract and Chinese translation, authors, journal, metric, DOI/publisher link, methods, findings, a specific “how this advances my direction” statement, and full-text status.
- `YYYY-MM-DD/` archive folders containing `daily_report.txt`, `references.ris`, `daily_index.json`, and `candidates.json`.
- Optional Zotero collection import and Outlook email delivery.

## Example from a real run (de-identified)

```text
DAILY LITERATURE BRIEF                         去标识化实际效果示例
────────────────────────────────────────────────────────────────
ENGLISH JOURNALS

题名：Investigation of key parameters controlling microfracture propagation
中文：控制页岩微裂缝扩展关键参数的研究
期刊：International Journal of Coal Science & Technology
分级：SCI/SCIE Q1 · JCR IF 10.1 (2025)

方法：DEM–FVM 水力—力学耦合；比较应力、干酪根几何与 TOC 情景。
发现：应力区间、干酪根间距与 TOC 阈值会重塑微裂缝连通性。

对研究方向的推动：
  该文并非直接的支撑剂运移证据；但可将储层结构因素作为 CFD–DEM
  支撑剂运移模型的裂缝几何与分流输入，再独立验证颗粒铺置行为。

全文状态：需通过学校已授权会话核验；未绕过访问控制。
```

The workflow was used for a petroleum hydraulic-fracturing/proppant-transport topic across nine consecutive dated runs. It created one self-contained archive folder on each run: seven days contained a selected high-tier English record, while two days truthfully reported no qualifying new record instead of padding the brief with older papers.

One selected paper used a coupled DEM–FVM model to study how differential stress, kerogen geometry, and TOC shape shale microfracture connectivity. The report did not overstate it as a proppant-transport result. Instead, it explained the practical bridge: use those reservoir-structure factors as fracture-geometry and flow-split inputs for a CFD–DEM proppant-transport model, then validate the particle behavior separately. Its publisher page was marked for a lawful institutional-access check rather than attempting to bypass access controls.

This is the intended experience: a compact daily answer to **what was published, what it says, whether it is accessible, and what it changes for my next research decision**.

## Install

Download or clone this repository, then place its contents at `~/.codex/skills/daily-proppant-literature-brief/`. Restart or refresh Codex skills.

## First-use prompt

Paste the following into Codex and replace the brackets:

```text
Use $daily-proppant-literature-brief to configure a daily literature brief.
Research direction: [your research direction and key terms].
Include Chinese journals: [yes/no]. Exclude: [topics to exclude].
Recipient email: [your email].
Archive directory: [your local directory].
Zotero parent collection: [collection name].
Use my already-authorized Outlook connection and already-authorized institutional access only.
```

Codex should confirm the settings, send a test email, and then enable the schedule. The skill asks for the delivery time when scheduling, so no separate export-time field is needed.

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

