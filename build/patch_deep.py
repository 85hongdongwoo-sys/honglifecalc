#!/usr/bin/env python3
"""Deepen top pages Omni-style: byline + table of contents near the top,
static (crawlable) tables, worked examples, more FAQ (+FAQPage JSON-LD).
Idempotent: skips pages already carrying the hl:deep marker."""
import json, re, sys, pathlib

SITE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
MARK = "<!--hl:deep-->"

CSS = """<style id="hl-deep-css">
.hl-by{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:13px;color:#6e6e73;margin:6px 2px 12px}
.hl-by b{color:#1d1d1f;font-weight:600}
.hl-toc{padding:14px 18px}
.hl-toc summary{font-weight:600;cursor:pointer;font-size:15px}
.hl-toc ol{margin:10px 0 2px;padding-left:20px;columns:2;column-gap:28px}
.hl-toc li{margin:3px 0;break-inside:avoid;font-size:14px}
.hl-toc a{text-decoration:none}
.hl-ex{border-left:3px solid #34c759;padding:2px 0 2px 12px;margin:12px 0}
.hl-ex p{margin:4px 0}
td.hl-rng{text-align:left!important;white-space:normal!important}
td.hl-rng small{display:block;font-size:12px;color:#6e6e73;font-family:inherit}
@media (max-width:560px){.hl-toc ol{columns:1}
#btTable th,#btTable td{white-space:normal!important;font-size:12px!important;padding-left:4px!important;padding-right:4px!important}}
</style>"""

R = [.10, .12, .22, .24, .32, .35, .37]
B27 = {"single": [12800, 52025, 109125, 208325, 264550, 661375],
       "mfj": [25600, 104050, 218250, 416650, 529100, 793650],
       "hoh": [18250, 69650, 109100, 208300, 264550, 661350],
       "mfs": [12800, 52025, 109125, 208325, 264550, 396825]}
NAMES = {"single": "Single", "mfj": "Married filing jointly",
         "hoh": "Head of household", "mfs": "Married filing separately"}


def usd(x):
    return "${:,.0f}".format(x) if x == int(x) else "${:,.2f}".format(x)


def tax_rows(st):
    b = B27[st]; rows = []; lo = 0; base = 0.0
    for i, r in enumerate(R):
        hi = b[i] if i < 6 else None
        rng = f"{usd(lo + (1 if lo else 0))} – {usd(hi)}" if hi else f"Over {usd(lo)}"
        owe = f"{usd(r*(hi-lo))}" if hi else "—"
        cum = (f"{usd(base)} + {int(r*100)}% over {usd(lo)}" if lo else f"{int(r*100)}% of taxable income")
        rows.append(f'<tr><td>{int(r*100)}%</td><td class="hl-rng">{rng}<small>{cum}</small></td></tr>')
        if hi:
            base += r * (hi - lo); lo = hi
    return "".join(rows)


def tables():
    out = []
    for st in ("single", "mfj", "hoh", "mfs"):
        out.append(f'<h3 id="t-{st}">2027 tax brackets: {NAMES[st]}</h3>'
                   '<div class="tblwrap"><table class="tbl"><thead><tr><th>Rate</th>'
                   '<th>Taxable income · tax owed</th></tr></thead><tbody>'
                   + tax_rows(st) + "</tbody></table></div>")
    return "".join(out)


TAX_FAQ = [
    ("Will a raise push all my income into a higher tax bracket?",
     "No. Brackets are marginal, so only the dollars above a threshold are taxed at the higher rate. "
     "A single filer with $110,125 of taxable income in 2027 crosses the 24% line by $1,000 and pays "
     "24% on just that $1,000 ($240 more than at $109,125), not on the whole income."),
    ("How much tax does a married couple pay on $120,000 of taxable income in 2027?",
     "$15,483 filing jointly with the official 2027 brackets: 10% on the first $25,600 ($2,560), "
     "12% up to $104,050 ($9,414) and 22% on the last $15,950 ($3,509). That is $341 less than "
     "the same income would owe under the 2026 brackets."),
    ("What is the difference between marginal and effective tax rate?",
     "The marginal rate is the rate on your next dollar of income — the top bracket you reach. "
     "The effective rate is total tax divided by taxable income. A single filer with $150,000 of "
     "taxable income in 2027 is in the 24% bracket but pays $28,359, an effective rate of about 18.9%."),
    ("When do the 2027 tax brackets apply?",
     "To income earned from January 1 to December 31, 2027. You use them on the federal return "
     "filed in 2028. Paycheck withholding switches to the 2027 tables in January 2027."),
    ("How can I lower my taxable income in 2027?",
     "Common ways are pre-tax contributions to a traditional 401(k) or IRA, HSA contributions, "
     "and the OBBBA deductions for qualified tips, overtime premium, car-loan interest and the "
     "senior deduction where you qualify. Each dollar deducted saves tax at your marginal rate."),
]

TAX_BODY = f"""
<section class="card help" id="tables"><h2>2027 federal tax bracket tables</h2>
<p>Official IRS figures from Rev. Proc. 2026-35. "Tax owed" shows the tax on all lower brackets plus the rate on income above the start of your bracket.</p>
{tables()}
</section>
<section class="card help" id="examples"><h2>Worked examples with the 2027 brackets</h2>
<div class="hl-ex"><p><b>Single, $100,000 salary, standard deduction</b></p>
<p>Taxable income = $100,000 − $16,600 = $83,400. Tax = $1,280 (10%) + $4,707 (12%) + $6,902.50 (22% on $31,375) = <b>$12,889.50</b>. Effective rate on salary: 12.9%. In 2026 the same salary owed $13,170, so 2027 saves about $280.</p></div>
<div class="hl-ex"><p><b>Married filing jointly, $120,000 taxable income</b></p>
<p>$2,560 (10% on $25,600) + $9,414 (12% up to $104,050) + $3,509 (22% on $15,950) = <b>$15,483</b>. Marginal rate 22%, effective 12.9%. 2026: $15,824.</p></div>
<div class="hl-ex"><p><b>Head of household, $80,000 taxable income</b></p>
<p>$1,825 (10% on $18,250) + $6,168 (12% up to $69,650) + $2,277 (22% on $10,350) = <b>$10,270</b>, effective 12.8%. 2026: $10,501.</p></div>
<div class="hl-ex"><p><b>Single, $150,000 taxable income</b></p>
<p>$1,280 + $4,707 + $12,562 (22% up to $109,125) + $9,810 (24% on $40,875) = <b>$28,359</b>. You are "in the 24% bracket", but the effective rate is 18.9%.</p></div>
</section>
<section class="card help" id="marginal"><h2>Marginal vs. effective tax rate</h2>
<p>Your <b>marginal rate</b> is the bracket your last dollar falls in. It tells you what an extra dollar of income — or an extra dollar of deduction — is worth. Your <b>effective rate</b> is total tax divided by income, and it is always lower than the marginal rate once you pass the first bracket.</p>
<p>That is why a raise never lowers your take-home pay: moving into a higher bracket only changes the rate on the dollars above the threshold. Example: at $109,125 of taxable income a single filer owes $18,549; at $110,125 the tax is $18,789 — exactly $240 more, or 24% of the extra $1,000.</p>
</section>
<section class="card help" id="lower"><h2>Ways to lower your 2027 taxable income</h2>
<ul>
<li><b>Traditional 401(k) / 403(b) / IRA</b> — pre-tax contributions come off taxable income. See the <a href="401k-calculator.html">401(k) calculator</a>.</li>
<li><b>HSA</b> — contributions are deductible if you have a high-deductible health plan.</li>
<li><b>OBBBA deductions (2025–2028)</b> — qualified tips, overtime premium, new-car loan interest and the $6,000 senior deduction. Try the <a href="no-tax-on-tips-calculator.html">tips</a> and <a href="no-tax-on-overtime-calculator.html">overtime</a> calculators.</li>
<li><b>Itemizing</b> — worth it only when mortgage interest, state and local taxes (SALT cap about $40,804 for 2027), charity and medical costs beat the $16,600 / $33,200 standard deduction.</li>
<li><b>Timing</b> — moving a bonus or deductible expense between 2026 and 2027 can change which year's brackets apply.</li>
</ul>
<p>Each $1,000 you deduct saves $1,000 × your marginal rate: $220 in the 22% bracket, $240 in the 24% bracket.</p>
</section>
"""

TAX_TOC = [("brackets", "2027 vs 2026 brackets & standard deduction"),
           ("tables", "Bracket tables by filing status"),
           ("examples", "Worked examples"),
           ("marginal", "Marginal vs. effective rate"),
           ("lower", "Ways to lower taxable income"),
           ("how", "How the brackets work & OBBBA changes"),
           ("faq", "FAQ & sources")]


SLOPE_FAQ = [
    ("How do you find the slope from two points?",
     "Subtract the y-values and divide by the difference of the x-values in the same order: m = (y2 - y1) / (x2 - x1). "
     "For (1, 2) and (5, 10): (10 - 2) / (5 - 1) = 8 / 4 = 2."),
    ("What is a 1:2 slope?",
     "Read as rise:run, a 1:2 slope rises 1 unit for every 2 units across: slope 0.5, a 50% grade, about 26.57 degrees. "
     "In earthwork and embankment drawings the same notation is often written run:rise (horizontal:vertical), "
     "so a 2:1 side slope there also means 26.57 degrees. Check which order the drawing uses."),
    ("What is a 3:12 roof pitch in degrees?",
     "A 3:12 (3-in-12) pitch rises 3 inches per 12 inches of run: slope 0.25, a 25% grade, about 14.0 degrees. "
     "A 6:12 pitch is about 26.6 degrees and 12:12 is 45 degrees."),
    ("What is a 5% slope in degrees?",
     "About 2.86 degrees. Convert a grade to an angle with angle = arctan(grade / 100). A 10% grade is 5.71 degrees and a 100% grade is 45 degrees."),
    ("What is the maximum slope for a wheelchair ramp?",
     "Under the 2010 ADA Standards (section 405.2) a ramp's running slope may not be steeper than 1:12, "
     "which is 8.33% or about 4.76 degrees: 1 inch of rise needs at least 12 inches of run. Local codes can be stricter."),
    ("What is an undefined slope?",
     "A vertical line has an undefined slope because the run (x2 - x1) is zero and you cannot divide by zero. "
     "A horizontal line is different: its slope is 0."),
    ("Is slope the same as gradient or grade?",
     "Yes, they describe the same ratio of rise to run. Gradient is common in math and British English; "
     "grade usually means the slope written as a percent (slope x 100), as on road signs."),
]

def _slope_tables():
    ratio = [("1:1","1","100%","45°"),("1:2","0.5","50%","26.57°"),("1:3","0.333","33.33%","18.43°"),
             ("1:4","0.25","25%","14.04°"),("1:8","0.125","12.5%","7.13°"),("1:10","0.1","10%","5.71°"),
             ("1:12","0.0833","8.33%","4.76°"),("1:20","0.05","5%","2.86°"),("1:48","0.0208","2.08%","1.19°"),
             ("1:100","0.01","1%","0.57°"),("2:1","2","200%","63.43°"),("3:1","3","300%","71.57°")]
    pitch = [(1,"8.3%","4.8°"),(2,"16.7%","9.5°"),(3,"25%","14.0°"),(4,"33.3%","18.4°"),(5,"41.7%","22.6°"),
             (6,"50%","26.6°"),(7,"58.3%","30.3°"),(8,"66.7%","33.7°"),(9,"75%","36.9°"),(10,"83.3%","39.8°"),(12,"100%","45°")]
    grade = [("1%","0.57°"),("2%","1.15°"),("5%","2.86°"),("8.33%","4.76°"),("10%","5.71°"),("15%","8.53°"),
             ("25%","14.04°"),("50%","26.57°"),("100%","45°")]
    h = ('<section class="card help" id="conv"><h2>Slope conversion table: ratio, percent and degrees</h2>'
         '<p>Ratios are written rise:run. Slope = rise ÷ run, grade = slope × 100, angle = arctan(slope).</p>'
         '<div class="tblwrap"><table class="tbl"><thead><tr><th>Ratio (rise:run)</th><th>Slope</th><th>Grade</th><th>Angle</th></tr></thead><tbody>'
         + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a,b,c,d in ratio)
         + '</tbody></table></div>'
         '<h3 id="grade">Percent grade to degrees</h3><div class="tblwrap"><table class="tbl"><thead><tr><th>Grade</th><th>Angle</th></tr></thead><tbody>'
         + "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a,b in grade) + '</tbody></table></div></section>'
         '<section class="card help" id="roof"><h2>Roof pitch to degrees and percent</h2>'
         '<p>Roof pitch is rise in inches per 12 inches of run, so a pitch of x:12 is a slope of x ÷ 12.</p>'
         '<div class="tblwrap"><table class="tbl"><thead><tr><th>Pitch</th><th>Grade</th><th>Angle</th></tr></thead><tbody>'
         + "".join(f"<tr><td>{p}:12</td><td>{g}</td><td>{d}</td></tr>" for p,g,d in pitch) + '</tbody></table></div></section>')
    return h

SLOPE_BODY = _slope_tables() + """
<section class="card help" id="uses"><h2>Slope in real life: ramps, drains, roads</h2>
<ul>
<li><b>Wheelchair ramps</b> — the 2010 ADA Standards (405.2) cap the running slope at <b>1:12</b> (8.33%, 4.76°). A 24-inch rise needs at least 24 ft of ramp run.</li>
<li><b>Drain pipes</b> — small horizontal drains are commonly laid at <b>1/4 inch per foot</b>, a slope of 1:48 (about 2.08%, 1.19°). Check your local plumbing code for the pipe size.</li>
<li><b>Roads</b> — road signs show grade in percent. A 6% grade drops 6 ft for every 100 ft of road, about 3.4°.</li>
<li><b>Graphs and data</b> — slope is the rate of change: dollars per month, km per hour, degrees per day.</li>
</ul></section>
<section class="card help" id="examples"><h2>More worked examples</h2>
<div class="hl-ex"><p><b>Negative slope: (−2, 7) and (4, −5)</b></p><p>m = (−5 − 7) ÷ (4 − (−2)) = −12 ÷ 6 = <b>−2</b>. b = 7 − (−2)(−2) = 3, so y = −2x + 3. The line falls 2 units for each unit to the right.</p></div>
<div class="hl-ex"><p><b>Fraction slope: (0, 1) and (6, 4)</b></p><p>m = 3 ÷ 6 = <b>1/2 = 0.5</b>, a 1:2 slope, 50% grade, 26.57°. Equation y = 0.5x + 1.</p></div>
<div class="hl-ex"><p><b>Horizontal line: (2, 5) and (9, 5)</b></p><p>Rise = 0, so m = 0 ÷ 7 = <b>0</b>. Equation y = 5.</p></div>
<div class="hl-ex"><p><b>Ramp check: 30-inch rise over 30 ft</b></p><p>30 ft = 360 in, so slope = 30 ÷ 360 = 1:12 = 8.33% — exactly at the ADA limit.</p></div>
</section>
"""

PAGES = {
    "us/2027-tax-brackets.html": {
        "byline": ("Hong Life Calculators", "November 10, 2026",
                   "IRS Rev. Proc. 2026-35 &amp; Rev. Proc. 2025-32"),
        "toc": TAX_TOC, "body": TAX_BODY, "faq": TAX_FAQ,
        "ids": [('<article class="card help"><h2>How the 2027 tax brackets work',
                 '<article class="card help" id="how"><h2>How the 2027 tax brackets work'),
                ('<h2 style="margin-top:22px">FAQ</h2>',
                 '<h2 style="margin-top:22px" id="faq">FAQ</h2>')],
        "before": '<section class="card help" id="brackets">',
        "after_body": '<article class="card help" id="how">',
        "faq_anchor": "<h3>Sources</h3>",
        "views": ("#out", "en"),
    },
    "en/math/slope-calculator.html": {
        "byline": ("Hong Life Calculators", "November 22, 2026",
                   "OpenStax College Algebra 2e §4.1; 2010 ADA Standards §405.2"),
        "toc": [("hl-explain", "How slope is calculated"), ("conv", "Ratio, percent & degrees table"),
                ("roof", "Roof pitch table"), ("uses", "Ramps, drains & roads"),
                ("examples", "More worked examples"), ("faq", "FAQ")],
        "body": SLOPE_BODY, "faq": SLOPE_FAQ, "faq_fmt": "h4",
        "ids": [("<h3>Frequently asked questions</h3>", '<h3 id="faq">Frequently asked questions</h3>')],
        "before": '<section class="app">',
        "after_body": '<article class="card help"><p class="note">Checked',
        "faq_anchor": '<p class="src">Sources:',
        "views": ("#conv,#roof", "en", "last"),
    },
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def patch(path, cfg):
    t = path.read_text(encoding="utf-8")
    if MARK in t:
        return False
    for a, b in cfg["ids"]:
        if a not in t:
            print("  anchor missing:", a[:50]); return False
        t = t.replace(a, b, 1)
    who, date, src = cfg["byline"]
    top = (MARK + f'<div class="hl-by"><span>By <b>{who}</b></span><span>Last checked <b>{date}</b></span>'
           f'<span>Source: {src}</span></div>'
           '<details class="card hl-toc" open><summary>On this page</summary><ol>'
           + "".join(f'<li><a href="#{i}">{n}</a></li>' for i, n in cfg["toc"]) + "</ol></details>")
    if cfg["before"] not in t:
        print("  before anchor missing"); return False
    # TOC goes above the calculator app so it shows near the top
    app = '<section class="app">'
    t = t.replace(app, top + app, 1) if app in t else t.replace(cfg["before"], top + cfg["before"], 1)
    t = t.replace(cfg["after_body"], cfg["body"] + cfg["after_body"], 1)
    if cfg.get("faq_fmt") == "h4":
        faq_html = "".join(f'<h4 class="q">{esc(q)}</h4><p class="a">{esc(a)}</p>' for q, a in cfg["faq"])
    else:
        faq_html = "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in cfg["faq"])
    t = t.replace(cfg["faq_anchor"], faq_html + cfg["faq_anchor"], 1)
    # extend FAQPage JSON-LD
    for m in re.finditer(r'(<script type="application/ld\+json">)(.*?)(</script>)', t, re.S):
        try:
            d = json.loads(m.group(2))
        except Exception:
            continue
        if isinstance(d, dict) and d.get("@type") == "FAQPage":
            d["mainEntity"] += [{"@type": "Question", "name": q,
                                 "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in cfg["faq"]]
            t = t[:m.start(2)] + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + t[m.end(2):]
            break
    t = t.replace("</head>", CSS + "</head>", 1)
    v = cfg.get("views")
    if v:
        t = t.replace("</body>", f'<script src="/assets/hl-views.js?v=3" defer data-target="{v[0]}" data-lang="{v[1]}"{' data-series="last"' if len(v) > 2 and v[2] == 'last' else ''}></script></body>', 1)
    path.write_text(t, encoding="utf-8")
    return True


n = 0
for rel, cfg in PAGES.items():
    p = SITE / rel
    if p.exists() and patch(p, cfg):
        n += 1; print("deepened", rel)
print(f"patch_deep: {n} page(s)")
