# Drafts waiting for official-source verification (2026-11-25)

These page scripts are finished drafts (layout and calculator fixes checked at 1280/390), but their
official figures could NOT be verified on 2026-11-25 because the official sites could not be opened.
They are NOT built into overlay/ and their paths stay in enrich_queue.json "queue".

Next run: verify each claim in the claims_*.json files (same folder) on the official page, fix the
script, move it back to build/pages/, run it, check rendering, then follow the runbook Finish steps.

- au_atar.py: /au/atar-selection-rank-calculator.html (UAC: ATAR range, age group, "less than 30", max selection rank)
- us_lifeline.py, us_section8.py, us_wic.py: claims_F1.json (FCC/USAC, eCFR + HUD 2026 HOTMA deductions, FNS 2026-27 IEGs)
- ca_selfemployed.py: claims_F1.json (CRA 2026 CPP, instalments, deadlines, GST/HST, EI). Contains a real calculator bug fix (employment-income tax double counted).
- de_teilzeit.py, de_abiturnote.py: claims_F3.json / KMK (Midijob formula, SV rates, BBG, Mindestlohn, TzBfG; KMK formula)
- it_giorni_date.py: holiday list (Legge 260/1949 as amended; 4 Oct from 2026 is confirmed by Legge 151/2025)
- ru_usn_ip.py, ru_transport_tax.py, ru_bmi.py: claims_F5.json (nalog.gov.ru, WHO)
- tw_lump15.py, tw_liformula.py: 勞工保險條例 / 勞工退休金條例, MOL 2026 wage and grade tables
