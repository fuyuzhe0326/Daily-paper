Exit code: 0
Wall time: 0.6 seconds
Output:
# Workflow reference

## Search and selection

Build bilingual query terms from the user's configured topic. Use Crossref and publisher metadata first. Match the publisher's first online publication date exactly. De-duplicate by DOI, title, and preprint identifier.

Classify journals as A (field flagship/SCI Q1), B (SCI Q2 or direct Chinese 北大核心/CSCD/EI), or C. Keep A/B by default; report C only as a clearly labelled user-approved exception. Prefer traceable JCR metrics; otherwise label CiteScore or SJR as a proxy.

## Access

Download OA content only from legitimate publisher/repository links. Institutional access, Chinese databases, and document delivery require an already-authorized browser session. Never request or save credentials, and stop on authentication, CAPTCHA, MFA, payment, robots, or copyright barriers.

## Email

Use the configured recipient and send time only after the user has authorized an Outlook connection. Put the complete report in plain text in the email body. Never hard-code an address in a reusable skill.

## Zotero

Use a configured parent collection and a `YYYY-MM-DD` child collection for each run. Confirm the local API before writing. Import generated RIS records first; attach only lawful OA PDFs or files obtained in an already-authorized institutional session. Record the Zotero item key, attachment path, and import/full-text status in the daily index. When the API is unavailable or an import fails, preserve the RIS and state the manual next action; never silently create duplicates on retry.

