# Drafts waiting for official-source verification (2026-11-25)

These page scripts are finished drafts (layout and calculator fixes checked at 1280/390), but their
official figures could NOT be verified on 2026-11-25 because the official sites could not be opened.
They are NOT built into overlay/ and their paths stay in enrich_queue.json "queue".

Next run: verify each claim in the claims_*.json files (same folder) on the official page, fix the
script, move it back to build/pages/, run it, check rendering, then follow the runbook Finish steps.

- de_teilzeit.py: claims_F3.json / KMK (Midijob formula, SV rates, BBG, Mindestlohn, TzBfG; KMK formula)
- ru_usn_ip.py, ru_transport_tax.py, ru_bmi.py: claims_F5.json (nalog.gov.ru, WHO)
- tw_liformula.py: 勞工保險條例 / 勞工退休金條例, MOL 2026 wage and grade tables

2026-11-27: au_atar, us_lifeline, us_section8, us_wic, ca_selfemployed, it_giorni_date, tw_lump15, de_abiturnote verified and moved to build/pages/.
