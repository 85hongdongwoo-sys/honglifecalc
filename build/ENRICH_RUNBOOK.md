# Thin-page enrichment runbook (honglifecalc.com)

Goal: make thin country calculator pages genuinely useful so Google indexes and ranks them.
Accuracy beats volume: never guess a figure. Every number is either computed by the page's own
calculator or checked today against an official / primary source that you cite on the page.

## Setup
1. Clone this repo (85hongdongwoo-sys/honglifecalc). Work in it.
2. `mkdir -p /tmp/hl_orig && cat pkg/site.tar.gz.part* | tar -xzf - -C /tmp/hl_orig` then `export HL_ORIG=/tmp/hl_orig`.
   (Assets for previews are in the same folder.)
3. Read `build/enrich_lib.py` (build(), table(), faq_html()) and 2–3 finished examples in `build/pages/`
   (e.g. `uk_pension.py`, `us_pmi.py`, `ca_cg.py`) — copy their structure and depth.

## For each page (take the first N from `build/enrich_queue.json` → "queue")
1. Read the original page (`$HL_ORIG/<path>`): title, description, form inputs, help article, and the calc
   function (it may live in a shared JS file such as `/us/us.js`, `/ca/ca.js`, `/<cc>/salary/calc.js`).
   If the page already has a substantial article (several sections, tables, worked examples, sources),
   move it to "done" with note "already rich" and skip.
2. Find what people search: Search Console data is optional; otherwise use the obvious intents
   (how much / how long / when / rates for this year / examples at common amounts).
3. Verify every rule and rate that applies in the page's country for the current year with WebSearch +
   WebFetch on official sources (tax authority, statistics office, central bank, legislation, regulator).
   Note the date checked. If you cannot verify a figure, leave it out.
4. Compute worked examples with the page's own formula (re-implement it in Python, or run the page in
   Playwright and read `#out`). Cross-check one example against the live calculator output.
5. Write `build/pages/<cc>_<slug>.py` that calls `build(path, title, description, article, faq, form=?, calc=?)`:
   - Article in the page's own language (local language for country pages).
   - Sections: how it works + formula; current official figures table; 3–6 worked examples table;
     practical tips / common mistakes; FAQ (4–6 Q&A that answer real search questions with numbers);
     Sources line with links (rel="nofollow") and "checked <date>".
   - Title ≤ ~70 chars, description ≤ ~160 chars, both naming the year where relevant.
   - Fix calculator bugs or outdated defaults you find (e.g. old prices/rates) — keep input ids.
6. Run it → writes `overlay/<path>`.
7. Check rendering (desktop 1280 and mobile 390): no JS errors, `document.documentElement.scrollWidth`
   equals the viewport, no element in `main` extends past the right edge, `#out` shows sensible numbers
   that match your examples. Mobile tables already stack via enrich_lib CSS. Fix anything clipped.
8. Re-read the page text once for wrong numbers, wrong year, wrong currency, and language mistakes.

## Finish
- Move finished paths from "queue" to "done" in `build/enrich_queue.json`, and set each finished path to today's date (YYYY-MM-DD) in `build/lastmod.json` (sitemap lastmod + schema dateModified).
- Put a 2–3 sentence answer-first summary at the very top of the article (the key number or rule people search for, with the year), before the explanation.
- Commit `overlay/`, `build/pages/`, `build/enrich_queue.json` and push to main (message ends with the
  Co-Authored-By line). Wait for the "Deploy site" workflow to succeed and spot-check one live page.
- Add the finished URLs to the front of `com.queue` in `gsc_queue.json` of repo
  85hongdongwoo-sys/honglife-src-backup (the daily Search Console task requests indexing from it); push.
- Report in Korean (해요체), organised: pages done (with the key official figures used), bugs fixed,
  figures left out because they could not be verified, pages remaining.

Never: invent numbers, copy text from other sites, add third-party logos, touch `pkg/` or `tpkg/`.
