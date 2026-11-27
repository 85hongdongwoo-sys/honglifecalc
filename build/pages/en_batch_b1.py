"""Waiting-room batch 1 (2026-11-27): 5 /en/money/ pages with low similarity but no impressions.
Search-term titles + verified official figures + worked examples, then removed from noindex_list.
Sources checked 2026-11-27:
- IRS IR-2026-136 (12 Nov 2026): 2027 IRA $7,500 (+$1,100), traditional IRA deduction phase-outs.
- IRS IR-2026-133 / Rev. Proc. 2026-35: 2027 brackets. IRS Topic 559: NIIT 3.8%, $200,000/$250,000/$125,000.
- HUD Mortgagee Letter 2023-05: UFMIP 1.75%, annual MIP table. HUD No. 25-145: 2026 FHA floor $541,287, ceiling $1,249,125.
- Illinois Comptroller Payroll Bulletin 1-26: 4.95%, 2026 exemption $2,925.
- California FTB Tax News October 2026: 2026 brackets (single, joint), standard deduction $5,900/$11,800, credits $158/$316/$491.
Usage: HL_ORIG=/tmp/claude-0/orig python3 build/pages/en_batch_b1.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en_us27_limits import build, tbl, chips, money, btax, B27S, B27J, YR_SEL, YR_JS  # noqa: E402

PAGES = {}

# ---------- Traditional IRA deduction (2027) ----------
def ira_ded(magi, lo, hi, con=7500):
    if magi >= hi: return 0
    if magi <= lo: return con
    d = con * (hi - magi) / (hi - lo)
    d = -(-d // 10) * 10
    if 0 < d < 200: d = 200
    return min(d, con)
rows = []
for magi in (80000, 85000, 88000, 91000, 93000):
    rows.append([money(magi), money(ira_ded(magi, 83000, 93000)), money(7500 - ira_ded(magi, 83000, 93000))])
rowsj = []
for magi in (130000, 140000, 145000, 150000, 255000):
    a = ira_ded(magi, 133000, 153000); b = ira_ded(magi, 250000, 260000)
    rowsj.append([money(magi), money(a), money(b)])
PAGES['en/money/traditional-ira-deduction-calculator.html'] = dict(
    title='Traditional IRA Deduction Limits 2027 – Income Limit & Phase-Out Calculator',
    desc='Traditional IRA deduction income limit 2027 (and 2026): phase-out $83,000–$93,000 single, $133,000–$153,000 joint if covered at work. See how much of $7,500 you can deduct.',
    h1='Traditional IRA Deduction Limits 2027: Income Limit &amp; Phase-Out <b>Calculator</b>',
    accent='#2B6CB0', bg='#F0F5FB', layout='split',
    box=lambda: ('<h2>Can you deduct your IRA contribution in 2027?</h2>'
                 '<p class="lead">If you are <b>not covered</b> by a workplace plan (and neither is your spouse), the whole contribution — up to <b>$7,500</b>, or $8,600 at 50+ — is deductible at any income. '
                 'If you <b>are covered</b>, the 2027 deduction shrinks between <b>$83,000 and $93,000</b> of modified AGI (single) or <b>$133,000 and $153,000</b> (married filing jointly).</p>'
                 '<div class="two"><div><b>You are covered at work</b><br>Single / HOH: $83,000 – $93,000<br>Joint: $133,000 – $153,000<br>Separate: $0 – $10,000<br><small>2026: $81,000–$91,000 · $129,000–$149,000</small></div>'
                 '<div><b>Only your spouse is covered</b><br>Joint: $250,000 – $260,000<br><small>2026: $242,000–$252,000</small></div></div>'
                 '<h3>Single, covered at work: deductible part of a $7,500 contribution (2027)</h3>'
                 + tbl(['Modified AGI', 'Deductible', 'Non-deductible (Form 8606)'], rows)
                 + '<h3>Married filing jointly (2027)</h3>'
                 + tbl(['Modified AGI', 'You are covered', 'Only spouse covered'], rowsj)
                 + '<p>Inside the range the IRS rounds the deductible amount up to the next $10, and any amount above $0 is at least $200. '
                   'The non-deductible part still grows tax-deferred; report it on Form 8606 so you are not taxed on it twice later.</p>'),
    faq=[('What are the 2027 traditional IRA deduction limits?', 'If you are covered by a workplace plan, the deduction phases out between $83,000 and $93,000 of modified AGI for single filers and between $133,000 and $153,000 for married couples filing jointly. If only your spouse is covered, the joint range is $250,000 to $260,000.'),
         ('How much can I contribute to an IRA in 2027?', '$7,500, or $8,600 if you are 50 or older ($7,500 plus a $1,100 catch-up). The limit is shared between traditional and Roth IRAs.'),
         ('Can I deduct an IRA if I have a 401(k)?', 'Yes, fully if your modified AGI is below the bottom of the 2027 range ($83,000 single, $133,000 joint), partly inside the range and not at all above it.')],
    js=[("lim=7500+(age>=50?1100:0)", "lim=7500+(age>=50?1100:0),Y6=YR()===2026"),
        ("r=st==='mfj'?[129000,149000]:[81000,91000]", "r=st==='mfj'?(Y6?[129000,149000]:[133000,153000]):(Y6?[81000,91000]:[83000,93000])"),
        ("r=st==='mfj'?[242000,252000]:[Infinity,Infinity]", "r=st==='mfj'?(Y6?[242000,252000]:[250000,260000]):[Infinity,Infinity]"),
        ("'2026 contribution limit'", "(YR()+' contribution limit')")],
    txt=[('This calculator applies the 2026 rules', 'This calculator applies the 2027 rules (or 2026, if you choose)'),
         ('<li>Contribution limit for 2026: $7,500, plus a $1,100 catch-up if you are 50 or older ($8,600).', '<li>Contribution limit for 2027 and 2026: $7,500, plus a $1,100 catch-up if you are 50 or older ($8,600).')],
    src='IRS News Release IR-2026-136 (12 Nov 2026): 2027 IRA limit and deduction phase-out ranges',
    srcurl='https://www.irs.gov/newsroom/401k-limit-increases-to-25500-for-2027-ira-limit-remains-7500')

# ---------- Tax-equivalent yield (2027 brackets) ----------
trow = []
for rate, single, joint in [(12, '$12,801 – $52,025', '$25,601 – $104,050'), (22, '$52,026 – $109,125', '$104,051 – $218,250'),
                            (24, '$109,126 – $208,325', '$218,251 – $416,650'), (32, '$208,326 – $264,550', '$416,651 – $529,100'),
                            (35, '$264,551 – $661,375', '$529,101 – $793,650'), (37, 'over $661,375', 'over $793,650')]:
    niit = rate >= 32
    tt = rate + (3.8 if niit else 0)
    trow.append(['%d%%' % rate, single, joint, '%.2f%%' % (3.5 / (1 - tt / 100)) + (' (with 3.8% NIIT)' if niit else '')])
PAGES['en/money/tax-equivalent-yield-calculator.html'] = dict(
    title='Tax Equivalent Yield Calculator – Formula for Municipal Bonds (2027)',
    desc='Tax equivalent yield formula: muni yield ÷ (1 − tax rate). Compare municipal bonds with taxable bonds. 2027 brackets: a 3.5% muni equals 4.61% taxable at 24% and 6.13% at 37% + 3.8% NIIT.',
    h1='Tax Equivalent Yield <b>Calculator</b> and Formula for Municipal Bonds',
    accent='#7B5EA7', bg='#F6F3FB', layout='steps',
    box=lambda: ('<h2>What a tax-free yield is worth in 2027</h2>'
                 '<p class="lead">Tax-equivalent yield = tax-free yield ÷ (1 − your tax rate). With the 2027 federal brackets, a <b>3.5%</b> municipal bond is worth '
                 '<b>4.61%</b> taxable in the 24% bracket and <b>6.13%</b> in the 37% bracket once the 3.8% net investment income tax is added.</p>'
                 '<ol class="yst"><li>Find your federal bracket for 2027 in the table below (taxable income, after deductions).</li>'
                 '<li>Add 3.8% if your modified AGI is above $200,000 (single), $250,000 (joint) or $125,000 (separate) — the NIIT applies to taxable interest above those amounts.</li>'
                 '<li>Add your state rate only if the muni is from your own state (out-of-state munis are usually state-taxable).</li>'
                 '<li>Divide the muni yield by (1 − total rate) and compare with the taxable bond’s yield.</li></ol>'
                 '<h3>3.5% muni: taxable equivalent by 2027 federal bracket (no state tax)</h3>'
                 + tbl(['Bracket', 'Single taxable income', 'Joint taxable income', 'Equivalent taxable yield'], trow)
                 + '<p>The NIIT column assumes income above the NIIT threshold from the 32% bracket up; below that, use the bracket rate alone. '
                   'In the 10% and 12% brackets a muni rarely wins: at 12%, 3.5% tax-free equals only 3.98% taxable.</p>'),
    faq=[('What is the tax-equivalent yield formula?', 'Tax-equivalent yield = tax-free yield ÷ (1 − tax rate). For example, 3.5% ÷ (1 − 0.24) = 4.61%.'),
         ('Which tax rate should I use for 2027?', 'Your 2027 federal marginal bracket (10% to 37%; the 24% bracket covers $109,126–$208,325 for single filers), plus 3.8% NIIT if your modified AGI is above $200,000 single or $250,000 joint, plus your state rate for in-state bonds.'),
         ('Is the NIIT threshold adjusted for inflation?', 'The IRS lists fixed thresholds of $200,000 (single or head of household), $250,000 (married filing jointly) and $125,000 (married filing separately).')],
    js=[], txt=[],
    src='IRS Rev. Proc. 2026-35 / IR-2026-133 (2027 brackets) and IRS Topic 559 (net investment income tax)',
    srcurl='https://www.irs.gov/taxtopics/tc559')

# ---------- FHA loan ----------
def fha(price, down_pct, rate, years=30):
    base = price * (1 - down_pct / 100)
    uf = base * 0.0175
    loan = base + uf
    i = rate / 1200; n = years * 12
    pi = loan * i / (1 - (1 + i) ** -n)
    mip_m = base * 0.0055 / 12  # simple first-year approximation on the base loan (LTV > 95%, ≤ $726,200)
    return base, uf, loan, pi, mip_m
frow = []
for price in (250000, 350000, 450000, 550000):
    base, uf, loan, pi, mip = fha(price, 3.5, 6.5)
    frow.append([money(price), money(price * 0.035), money(uf), money(loan), money(pi), money(mip), money(pi + mip)])
PAGES['en/money/fha-loan-calculator.html'] = dict(
    title='FHA Loan Calculator with MIP – FHA MIP Chart 2026 & Loan Limits',
    desc='FHA loan calculator with MIP: upfront 1.75%, annual 0.55% (FHA MIP chart 2026). 2026 FHA loan limits: $541,287 floor, $1,249,125 ceiling. Examples at 3.5% down.',
    h1='FHA Loan <b>Calculator</b> with MIP (2026 MIP chart &amp; FHA loan limits)',
    accent='#2F7D6B', bg='#EFF7F5', layout='chips',
    box=lambda: ('<h2>FHA loan costs at a glance</h2>'
                 '<p class="lead">Most FHA buyers put <b>3.5%</b> down. HUD then adds an <b>upfront MIP of 1.75%</b> of the base loan (usually financed) and an <b>annual MIP of 0.55%</b> '
                 '(30-year loan, over 95% LTV, base loan up to $726,200), paid monthly for the life of the loan. In 2026 the FHA one-unit loan limit runs from <b>$541,287</b> to <b>$1,249,125</b> depending on the county.</p>'
                 + chips([('1.75%', 'upfront MIP (UFMIP)'), ('0.55%', 'annual MIP, 30 yr, >95% LTV'), ('0.50%', 'annual MIP with 5–10% down'),
                          ('$541,287', '2026 limit, low-cost areas'), ('$1,249,125', '2026 limit, high-cost areas')])
                 + '<h3>FHA MIP chart (annual MIP, in force for 2026)</h3>'
                 + tbl(['Loan term', 'Base loan', 'LTV (down payment)', 'Annual MIP', 'How long'],
                       [['Over 15 years', 'up to $726,200', 'over 95% (under 5% down)', '0.55%', 'life of loan'],
                        ['Over 15 years', 'up to $726,200', '90–95% (5–10% down)', '0.50%', 'life of loan'],
                        ['Over 15 years', 'up to $726,200', '90% or less (10%+ down)', '0.50%', '11 years'],
                        ['Over 15 years', 'over $726,200', 'over 95%', '0.75%', 'life of loan'],
                        ['Over 15 years', 'over $726,200', '95% or less', '0.70%', '11 years if LTV ≤ 90%'],
                        ['15 years or less', 'up to $726,200', 'over 90%', '0.40%', 'life of loan'],
                        ['15 years or less', 'up to $726,200', '90% or less', '0.15%', '11 years']])
                 + '<h3>3.5% down, 6.5% interest, 30 years (first-year monthly figures)</h3>'
                 + tbl(['Home price', 'Down payment', 'UFMIP financed', 'Total loan', 'Principal + interest', 'Monthly MIP', 'P&amp;I + MIP'], frow)
                 + '<p>Taxes, homeowners insurance and HOA come on top. With 10% or more down, annual MIP drops off after 11 years; with less than 10% down it stays '
                   'until the loan is paid off or refinanced. The 6.5% rate is only an example — use your lender’s quote.</p>'),
    faq=[('How much is FHA mortgage insurance?', 'Upfront MIP is 1.75% of the base loan. Annual MIP on a 30-year loan of up to $726,200 is 0.55% with less than 5% down and 0.50% with 5% or more down (HUD Mortgagee Letter 2023-05).'),
         ('What are the FHA loan limits for 2026?', 'For a one-unit home, from $541,287 in low-cost areas to $1,249,125 in high-cost areas, for case numbers assigned from 1 January 2026. Your county’s exact limit can be in between.'),
         ('When does FHA MIP go away?', 'With at least 10% down (LTV 90% or less) annual MIP ends after 11 years. With less than 10% down it lasts for the whole term unless you refinance out of FHA.')],
    js=[], txt=[],
    src='HUD Mortgagee Letter 2023-05 (MIP) and HUD No. 25-145 (2026 FHA loan limits)',
    srcurl='https://www.hud.gov/news/hud-no-25-145')

# ---------- Illinois ----------
irow = []
for inc in (40000, 60000, 80000, 100000, 150000):
    tx = max(0, inc - 2925) * 0.0495
    irow.append([money(inc), money(tx), '%.2f%%' % (tx / inc * 100), money(tx / 26, 2), money(tx / 12, 2)])
PAGES['en/money/illinois-tax-calculator.html'] = dict(
    title='Illinois Income Tax Calculator 2026 – Rate 4.95%, Brackets & Exemption',
    desc='Illinois state income tax 2026: flat 4.95% after a $2,925 exemption per person. $60,000 pays about $2,825 a year ($108.66 per biweekly paycheck).',
    h1='Illinois Income Tax <b>Calculator</b> 2026 (rate 4.95%, $2,925 exemption)',
    accent='#B5472F', bg='#FBF2EF', layout='steps',
    box=lambda: ('<h2>Illinois state tax in 2026, in one line</h2>'
                 '<p class="lead">Illinois taxes income at a flat <b>4.95%</b> after an exemption of <b>$2,925</b> per person claimed (up from $2,850 in 2025). '
                 'One exemption on $60,000 leaves $57,075 taxed, so the state tax is about <b>$2,825</b> a year.</p>'
                 '<ol class="yst"><li>Start from Illinois base income (federal AGI with Illinois additions and subtractions).</li>'
                 '<li>Subtract $2,925 for yourself, your spouse if filing jointly, and each dependent.</li>'
                 '<li>Multiply what is left by 4.95%.</li></ol>'
                 '<h3>One exemption, 2026</h3>'
                 + tbl(['Income', 'Illinois tax', 'Effective rate', 'Per biweekly paycheck', 'Per month'], irow)
                 + '<p>Employers withhold using the same 4.95% rate and the exemptions you claim on Form IL-W-4 ($112.50 per exemption per biweekly paycheck in 2026). '
                   'The 2027 exemption amount has not been published yet.</p>'),
    faq=[('What is the Illinois income tax rate for 2026?', 'A flat 4.95% on net income.'),
         ('Does Illinois have income tax brackets?', 'No. Illinois has one flat rate, 4.95%, for every income level; only the $2,925 exemption per person makes the effective rate lower on small incomes.'),
         ('How much is the Illinois exemption for 2026?', '$2,925 per exemption (you, your spouse on a joint return, and each dependent), up from $2,850 in 2025.'),
         ('How much Illinois tax is taken from a biweekly paycheck?', 'On $60,000 a year with one exemption, about $108.66 per biweekly paycheck: ($60,000 − $2,925) × 4.95% ÷ 26.')],
    js=[], txt=[],
    src='Office of the Illinois Comptroller, Payroll Bulletin 1-26 (2026 exemption $2,925, rate 4.95%)',
    srcurl='https://illinoiscomptroller.gov/__media/sites/comptroller/assets/File/PayrollBulletins/Payroll%20Bulletin%201-26%20-%20Illinois%20State%20Income%20Tax%20Exemptions%20-%202026.pdf')

# ---------- California (2026 FTB brackets) ----------
CB26 = {0: [0, 11456, 27157, 42861, 59498, 75197, 384109, 460927, 768213], 1: [0, 22912, 54314, 85722, 118996, 150394, 768218, 921854, 1536426]}
CR = [1, 2, 4, 6, 8, 9.3, 10.3, 11.3, 12.3]
def ca26(agi, fs):
    ti = max(0, agi - (5900 if fs == 0 else 11800)); t = 0; cb = CB26[fs]
    for k in range(9):
        hi = cb[k + 1] if k < 8 else float('inf')
        if ti > cb[k]: t += (min(ti, hi) - cb[k]) * CR[k] / 100
    return max(0, t - (158 if fs == 0 else 316))
crow = [[money(a), money(ca26(a, 0)), '%.2f%%' % (ca26(a, 0) / a * 100), money(ca26(a, 1))] for a in (50000, 75000, 100000, 150000, 250000)]
brow = [['%g%%' % CR[k], money(CB26[0][k]) + (' – ' + money(CB26[0][k + 1]) if k < 8 else '+'), money(CB26[1][k]) + (' – ' + money(CB26[1][k + 1]) if k < 8 else '+')] for k in range(9)]
PAGES['en/money/california-tax-calculator.html'] = dict(
    title='California Tax Brackets 2026 (Single & Married Jointly) + Tax Calculator',
    desc='California tax brackets 2026 for single and married filing jointly (FTB): 9.3% from $75,197 single, standard deduction $5,900. Estimate your California income tax for 2026 or 2025.',
    h1='California Tax Brackets 2026 and Income Tax <b>Calculator</b>',
    accent='#C0841A', bg='#FCF7EC', layout='chips',
    box=lambda: ('<h2>California income tax for 2026</h2>'
                 '<p class="lead">The Franchise Tax Board’s 2026 schedule runs from <b>1%</b> to <b>12.3%</b>, plus 1% on taxable income over $1 million. '
                 'A single filer with $100,000 of California AGI pays about <b>' + money(ca26(100000, 0)) + '</b> after the $5,900 standard deduction and the $158 personal credit.</p>'
                 + chips([('$5,900', 'standard deduction, single'), ('$11,800', 'standard deduction, joint / HOH'), ('$158', 'personal credit, single'),
                          ('$316', 'personal credit, joint'), ('$491', 'credit per dependent')])
                 + '<h3>2026 brackets (taxable income)</h3>'
                 + tbl(['Rate', 'Single / separate', 'Married filing jointly'], brow)
                 + '<h3>Estimated 2026 tax (standard deduction, personal credit, no dependents)</h3>'
                 + tbl(['California AGI', 'Single', 'Single, effective', 'Joint'], crow)
                 + '<p>The FTB says the complete 2026 tables, including head of household, are published in late December; for head of household the calculator still uses the 2025 schedule until then.</p>'),
    faq=[('What are the California tax brackets for 2026?', 'For single filers: 1% up to $11,456, 2% to $27,157, 4% to $42,861, 6% to $59,498, 8% to $75,197, 9.3% to $384,109, 10.3% to $460,927, 11.3% to $768,213 and 12.3% above. Joint brackets are twice as wide.'),
         ('What is the California standard deduction for 2026?', '$5,900 for single or married filing separately and $11,800 for married filing jointly, surviving spouses and heads of household.'),
         ('What are the California tax brackets for 2026 married filing jointly?', '1% up to $22,912, 2% to $54,314, 4% to $85,722, 6% to $118,996, 8% to $150,394, 9.3% to $768,218, 10.3% to $921,854, 11.3% to $1,536,426 and 12.3% above, plus 1% on taxable income over $1 million.'),
         ('How much California tax on $100,000?', 'About ' + money(ca26(100000, 0)) + ' for a single filer in 2026 using the standard deduction and the $158 personal exemption credit.')],
    js=[("const CB=[[0,11079,26264,41452,57542,72724,371479,445771,742953],[0,22158,52528,82904,115084,145448,742958,891542,1485906],[0,22173,52530,67716,83805,98990,505208,606251,1010417]][fs]",
         "const Y6=YR()!==2027,CB=(Y6?[[0,11079,26264,41452,57542,72724,371479,445771,742953],[0,22158,52528,82904,115084,145448,742958,891542,1485906],[0,22173,52530,67716,83805,98990,505208,606251,1010417]]:[[0,11456,27157,42861,59498,75197,384109,460927,768213],[0,22912,54314,85722,118996,150394,768218,921854,1536426],[0,22173,52530,67716,83805,98990,505208,606251,1010417]])[fs]"),
        ("du=Math.max(fs===0?5706:11412,ded)", "du=Math.max(Y6?(fs===0?5706:11412):(fs===0?5900:11800),ded)")],
    yr_opts=('2027', '2026 (new FTB brackets)', '2026', '2025'),
    txt=[('Figures use the 2025 tax-year schedules (returns filed in 2026).', 'Figures use the 2026 FTB schedules by default; switch to 2025 for returns filed in 2026.')],
    src='California Franchise Tax Board, Tax News October 2026 (2026 inflation-adjusted brackets, deductions and credits)',
    srcurl='https://www.ftb.ca.gov/about-ftb/newsroom/tax-news/2026/10.html')

if __name__ == '__main__':
    import en_us27_limits as L
    for p, d in PAGES.items():
        yo = d.pop('yr_opts', None)
        if yo:  # this page's years are 2026/2025: relabel the selector (values stay 2027=new, 2026=old)
            L.YR_SEL = ('<label class="f"><span>Tax year</span><select id="yr"><option value="2027" selected>%s</option>'
                        '<option value="2026">%s</option></select></label>') % (yo[1], yo[3])
        else:
            L.YR_SEL = YR_SEL
        if d['js'] and not any('YR()' in n for _, n in d['js']):
            pass
        L.build(p, d)
