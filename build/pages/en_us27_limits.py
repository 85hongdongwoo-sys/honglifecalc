"""US money pages (noindexed, /en/money/) → 2027 official figures + year switch + answer-first box (2026-11-27).
Sources checked 2026-11-27:
- IRS IR-2026-136 (12 Nov 2026) + Notice 2026-66: 401(k)/403(b)/457 25,500; catch-up 8,500; 60–63 11,750; 415(c) 75,000;
  IRA 7,500 (+1,100 at 50+); Roth IRA phase-out 158k–173k single/HOH, 250k–260k MFJ.
- IRS IR-2026-133 (5 Nov 2026) + Rev. Proc. 2026-35: 2027 brackets, AMT exemption 93,000/144,700/72,350,
  phase-out 515,950/1,031,900/515,950, 28% break 252,500 (126,250 MFS).
- FHFA news release 24 Nov 2026: 2027 baseline CLL 855,400; ceiling 1,283,100; AK/HI/Guam/USVI 1,283,100 / 1,924,650.
Usage: HL_ORIG=/tmp/claude-0/orig python3 build/pages/en_us27_limits.py"""
import html, json, os, re

ORIG = os.environ.get('HL_ORIG', '/tmp/claude-0/orig')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECK = '27 Nov 2026'
YR_SEL = ('<label class="f"><span>Tax year</span><select id="yr"><option value="2027" selected>2027 (new IRS figures)</option>'
          '<option value="2026">2026</option></select></label>')
YR_JS = "const YR=()=>{const e=document.getElementById('yr');return e&&e.value==='2026'?2026:2027};\n"


def money(x, d=0):
    return '$' + format(round(x, d), ',.%df' % d)


def tbl(head, rows, cls=''):
    h = '<div class="y27t"><table%s><thead><tr>%s</tr></thead><tbody>' % (' class="%s"' % cls if cls else '', ''.join('<th>%s</th>' % x for x in head))
    h += ''.join('<tr>%s</tr>' % ''.join('<td data-l="%s">%s</td>' % (html.escape(plain(head[i])), c) for i, c in enumerate(r)) for r in rows)
    return h + '</tbody></table></div>'


def css(accent, bg, layout):
    base = ('.y27{margin:0 0 22px;padding:16px 16px 6px;border-radius:16px;background:%s;border:1px solid %s33}'
            '.y27 h2{margin:0 0 8px;font-size:21px}.y27 .lead{font-size:16.5px;line-height:1.7;margin:0 0 10px}'
            '.y27 .lead b{color:%s}.y27 h3{font-size:17px;margin:18px 0 6px}.y27t{max-width:100%%;overflow-x:auto}'
            '.y27 table{width:100%%;border-collapse:collapse;font-size:14.5px;margin:6px 0 10px}'
            '.y27 th,.y27 td{padding:7px 6px;border-bottom:1px solid %s26;text-align:left;vertical-align:top;white-space:normal!important;font-weight:400}'
            '@media(max-width:600px){.y27 table,.y27 tbody,.y27 tr,.y27 td{display:block;width:auto}.y27 thead{display:none}'
            '.y27 tr{background:#fff;border-radius:12px;padding:8px 12px;margin:0 0 8px}.y27 td{display:flex;justify-content:space-between;gap:10px;border:0;padding:3px 0;text-align:right}'
            '.y27 td::before{content:attr(data-l);color:#6b6253;font-size:13px;text-align:left;font-weight:400}.y27 td:first-child{display:block;text-align:left;font-size:15.5px;padding-bottom:5px}'
            '.y27 td:first-child::before{display:none}}'
            '.y27 thead th{font-size:13px;background:transparent;color:#5b5446;font-weight:700}'
            '#form select{max-width:100%%;min-width:0;text-overflow:ellipsis}#form label.f{min-width:0}.y27 td:first-child{font-weight:700!important}.y27 p{line-height:1.75}.y27 .src{font-size:13px;color:#6b6253}'
            ) % (bg, accent, accent, accent)
    if layout == 'chips':
        base += ('.y27 .chips{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:8px;margin:8px 0 12px}'
                 '.y27 .chips div{background:#fff;border-radius:12px;padding:10px;border-left:4px solid %s}'
                 '.y27 .chips b{display:block;font-size:20px}.y27 .chips span{font-size:13px;color:#5b5446}') % accent
    if layout == 'steps':
        base += ('.y27 ol.yst{margin:6px 0 12px;padding-left:22px;line-height:1.75}.y27 ol.yst li{margin:4px 0}'
                 '.y27 ol.yst li::marker{color:%s;font-weight:800}') % accent
    if layout == 'split':
        base += ('.y27 .two{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:8px 0}'
                 '.y27 .two div{background:#fff;border-radius:12px;padding:10px 12px;border-top:4px solid %s}'
                 '@media(max-width:520px){.y27 .two{grid-template-columns:1fr}}') % accent
    return '<style id="y27-css">%s</style>' % base


def chips(items):
    return '<div class="chips">%s</div>' % ''.join('<div><b>%s</b><span>%s</span></div>' % (a, b) for a, b in items)


# ---------- worked-example engines (same formulas as the pages) ----------
B27S = [12800, 52025, 109125, 208325, 264550, 661375]
B27J = [25600, 104050, 218250, 416650, 529100, 793650]
RATES = [10, 12, 22, 24, 32, 35, 37]


def btax(x, b):
    t, lo = 0, 0
    for k in range(7):
        hi = b[k] if k < 6 else float('inf')
        if x > lo:
            t += (min(x, hi) - lo) * RATES[k] / 100
        lo = hi
    return t


def amt27(fs, ti, adj):
    ex0 = [93000, 144700, 93000, 72350][fs]
    th = 1031900 if fs == 1 else 515950
    bk = 126250 if fs == 3 else 252500
    ai = ti + adj
    exm = max(0, ex0 - 0.5 * max(0, ai - th))
    bs = max(0, ai - exm)
    tmt = 0.26 * bs if bs <= bk else 0.26 * bk + 0.28 * (bs - bk)
    rg = btax(ti, B27J if fs == 1 else B27S)
    return ai, exm, tmt, rg, max(0, tmt - rg)


def pmt(L, rate, yrs):
    i = rate / 1200
    n = yrs * 12
    return L * i / (1 - (1 + i) ** -n)


# ---------- page definitions ----------
PAGES = {}

# 401(k) match
ex = []
for sal, c, m1, m2 in [(50000, 6, 50, 6), (80000, 6, 50, 6), (80000, 4, 100, 4), (120000, 10, 100, 3), (200000, 12.75, 50, 6)]:
    you = min(sal * c / 100, 25500)
    er = min(c, m2) / 100 * m1 / 100 * sal
    ex.append([money(sal), '%g%%' % c, '%g%% up to %g%%' % (m1, m2), money(you), money(er), money(you + er)])
pct = [[money(s), '%.1f%%' % (25500 / s * 100), '%.1f%%' % (34000 / s * 100)] for s in (60000, 80000, 100000, 150000, 200000)]
PAGES['en/money/401k-match-calculator.html'] = dict(
    title='401(k) Employer Match Calculator (2027 limit $25,500, catch-ups)',
    desc='2027 401(k) limit is $25,500 (+$8,500 at 50+, $11,750 at 60–63). See your employer match, the match you miss and growth — 2026 or 2027.',
    h1='401(k) Employer Match <b>Calculator</b> (2027 limits)',
    accent='#2F6DB5', bg='#F1F6FC', layout='chips',
    box=lambda: ('<h2>2027 401(k) limits at a glance</h2>'
                 '<p class="lead">For 2027 you can put up to <b>$25,500</b> of your own pay into a 401(k) — $1,000 more than in 2026. '
                 'At age 50+ the catch-up is <b>$8,500</b> (total $34,000), and at ages 60–63 it is <b>$11,750</b> instead (total $37,250). '
                 'Employer match does not count toward $25,500; it counts toward the overall $75,000 cap.</p>'
                 + chips([('$25,500', 'employee deferral limit 2027'), ('$8,500', 'catch-up at 50+'), ('$11,750', 'catch-up at ages 60–63'),
                          ('$75,000', 'you + employer total (415(c))'), ('$155,000', 'Roth catch-up wage threshold (Notice 2026-66)')])
                 + '<h3>What common match formulas add (2027)</h3>'
                 + tbl(['Salary', 'You put in', 'Match formula', 'Your money', 'Employer adds', 'Total a year'], ex)
                 + '<h3>Share of pay needed to reach the 2027 maximum</h3>'
                 + tbl(['Salary', 'Under 50 ($25,500)', '50+ ($34,000)'], pct)
                 + '<p>Contributing beyond the match cap gets no extra employer money, but it still lowers taxable pay (traditional) '
                   'or grows tax-free (Roth). Higher earners should also check the Roth catch-up rule: if your prior-year FICA wages from this employer were above '
                   'the IRS threshold (listed as $155,000 in Notice 2026-66), catch-up contributions must be made as Roth.</p>'),
    faq=[('What is the 401(k) limit for 2027?', 'The employee deferral limit for 2027 is $25,500, up from $24,500 in 2026. Workers aged 50 and over can add $8,500 (total $34,000), and those aged 60–63 can add $11,750 instead (total $37,250).'),
         ('What is the total 401(k) limit including the employer match in 2027?', 'Your contributions plus employer contributions (match and profit sharing) are capped at $75,000 in 2027, or 100% of pay if lower. Catch-up contributions come on top of that cap.'),
         ('How much do I need to contribute to max out my 401(k) on an $80,000 salary?', 'About 31.9% of pay ($25,500 ÷ $80,000). At 50+, $34,000 is 42.5% of an $80,000 salary.')],
    js=[("const lim=24500+(age>=60&&age<=63?11250:age>=50?8000:0)",
         "const Y6=YR()===2026,lim=(Y6?24500:25500)+(age>=60&&age<=63?(Y6?11250:11750):age>=50?(Y6?8000:8500):0)"),
        ("'2026 employee limit for your age'", "(YR()+' employee limit for your age')")],
    txt=[('<li>Limit: $24,500 in 2026, plus an $8,000 catch-up at 50+, or $11,250 instead at ages 60–63</li>',
          '<li>Limit: $25,500 in 2027 ($24,500 in 2026), plus an $8,500 catch-up at 50+ ($8,000 in 2026), or $11,750 instead at ages 60–63 ($11,250 in 2026)</li>'),
         ('the 2026 employee deferral limit for your age', 'the 2027 (or 2026) employee deferral limit for your age')],
    src='IRS News Release IR-2026-136 (12 Nov 2026) and Notice 2026-66 (2027 limits)',
    srcurl='https://www.irs.gov/newsroom/401k-limit-increases-to-25500-for-2027-ira-limit-remains-7500')

# 403(b)
def c403(age, q15, ys, pdf, pc, y=2027):
    base, a50, a60 = (25500, 8500, 11750) if y == 2027 else (24500, 8000, 11250)
    c15 = max(0, min(3000, 15000 - pc, 5000 * ys - pdf)) if (q15 and ys >= 15) else 0
    acu = a60 if 60 <= age <= 63 else a50 if age >= 50 else 0
    return c15, acu, base + c15 + acu
rows = []
for lab, age, q15, ys, pdf, pc in [('Age 40, 8 years of service', 40, 0, 8, 0, 0), ('Age 45, 18 years, low past deferrals', 45, 1, 18, 60000, 0),
                                   ('Age 52, 16 years, $70,000 past deferrals', 52, 1, 16, 70000, 0), ('Age 61, 25 years, $15,000 already used', 61, 1, 25, 200000, 15000),
                                   ('Age 61, 25 years, $9,000 used, low past deferrals', 61, 1, 25, 90000, 9000)]:
    c15, acu, tot = c403(age, q15, ys, pdf, pc)
    rows.append([lab, money(25500), money(c15), money(acu), '<b>%s</b>' % money(tot)])
PAGES['en/money/403b-calculator.html'] = dict(
    title='403(b) Calculator 2027 ($25,500 limit, 15-year & age catch-ups)',
    desc='2027 403(b) limit $25,500, age catch-up $8,500 ($11,750 at 60–63) and the 15-year catch-up up to $3,000. Check your maximum and growth.',
    h1='403(b) <b>Calculator</b> (2027 limits with 15-year &amp; age catch-ups)',
    accent='#7A4FB3', bg='#F6F2FB', layout='steps',
    box=lambda: ('<h2>2027 403(b) limits in one minute</h2>'
                 '<p class="lead">In 2027 a 403(b) takes up to <b>$25,500</b> of elective deferrals. On top you may add the <b>age catch-up</b> '
                 '($8,500 at 50+, or $11,750 at ages 60–63) and, with 15+ years at a qualifying employer, the <b>15-year catch-up</b> of up to $3,000. '
                 'The most one person can defer is therefore $37,000 (50+) or $40,250 (ages 60–63).</p>'
                 '<ol class="yst"><li>Start with the base limit: $25,500.</li>'
                 '<li>15-year catch-up = the smallest of $3,000; $15,000 minus 15-year catch-ups used before; $5,000 × years of service minus earlier deferrals to this employer.</li>'
                 '<li>Add the age catch-up for your age on 31 December 2027.</li>'
                 '<li>Your deferrals plus employer money must stay within $75,000 or 100% of includible pay (catch-ups are outside this cap).</li></ol>'
                 '<h3>2027 maximum deferral in five situations</h3>'
                 + tbl(['Situation', 'Base', '15-year', 'Age catch-up', 'Maximum'], rows)
                 + '<p>The 15-year catch-up is used before the age catch-up, so a deferral above the base limit first eats into the $15,000 lifetime 15-year allowance. '
                   'Check that your plan document actually offers it — not every 403(b) does.</p>'),
    faq=[('What is the 403(b) limit for 2027?', 'The 2027 elective deferral limit is $25,500. Add $8,500 at age 50+ (or $11,750 at ages 60–63), plus up to $3,000 more under the 15-year rule if you qualify.'),
         ('What is the maximum 403(b) contribution with both catch-ups in 2027?', '$37,000 if you are 50–59 or 64+ ($25,500 + $3,000 + $8,500), or $40,250 at ages 60–63 ($25,500 + $3,000 + $11,750).'),
         ('Is the 2027 annual additions limit for a 403(b) still $72,000?', 'No. For 2027 the limit on your deferrals plus employer contributions rises to $75,000 (from $72,000), or 100% of includible compensation if lower.')],
    js=[("acu=(age>=60&&age<=63)?11250:age>=50?8000:0,cap=Math.min(24500+c15+acu,sal)",
         "acu=(age>=60&&age<=63)?(YR()===2026?11250:11750):age>=50?(YR()===2026?8000:8500):0,cap=Math.min((YR()===2026?24500:25500)+c15+acu,sal)"),
        ("Math.min(72000", "Math.min(YR()===2026?72000:75000"),
        ("for 2026 (USD)", "for the year (USD)"), ("Age at the end of 2026", "Age at the end of the year")],
    txt=[('<li>2026 base elective deferral limit: $24,500.', '<li>Base elective deferral limit: $25,500 in 2027 ($24,500 in 2026).'),
         ('Age catch-up: $8,000 at age 50 or over at year-end, or $11,250 at ages 60–63.', 'Age catch-up: $8,500 in 2027 ($8,000 in 2026) at age 50 or over at year-end, or $11,750 in 2027 ($11,250 in 2026) at ages 60–63.'),
         ('lesser of $72,000 or your includible pay', 'lesser of $75,000 in 2027 ($72,000 in 2026) or your includible pay')],
    src='IRS News Release IR-2026-136 (12 Nov 2026) and Notice 2026-66 (2027 limits)',
    srcurl='https://www.irs.gov/newsroom/401k-limit-increases-to-25500-for-2027-ira-limit-remains-7500')

# Backdoor Roth
brow = []
for pre in (0, 7500, 22500, 67500, 142500):
    sh = min(1, 7500 / (pre + 7500))
    tx = 7500 * (1 - sh)
    brow.append([money(pre), '%.0f%%' % (sh * 100), money(tx), money(tx * 0.24), money(tx * 0.32)])
PAGES['en/money/backdoor-roth-tax-calculator.html'] = dict(
    title='Backdoor Roth IRA Pro-Rata Tax Calculator (2027 limits)',
    desc='2027: Roth IRA phase-out starts at $158,000 single / $250,000 joint; IRA limit $7,500 (+$1,100 at 50+). See the tax on a backdoor Roth.',
    h1='Backdoor Roth IRA Pro-Rata Tax <b>Calculator</b> (2027)',
    accent='#B5602F', bg='#FCF4EE', layout='split',
    box=lambda: ('<h2>Who needs a backdoor Roth in 2027?</h2>'
                 '<p class="lead">For 2027 you cannot contribute directly to a Roth IRA once your modified AGI reaches <b>$173,000</b> (single or head of household) '
                 'or <b>$260,000</b> (married filing jointly); the reduction starts at $158,000 and $250,000. The 2027 IRA limit stays <b>$7,500</b>, '
                 'plus a <b>$1,100</b> catch-up at 50+ — that is the amount people usually put in non-deductibly and convert.</p>'
                 '<div class="two"><div><b>Single / head of household</b><br>Phase-out $158,000 – $173,000<br><small>2026: $153,000 – $168,000</small></div>'
                 '<div><b>Married filing jointly</b><br>Phase-out $250,000 – $260,000<br><small>2026: $242,000 – $252,000</small></div></div>'
                 '<h3>How other pre-tax IRA money changes the tax on a $7,500 conversion</h3>'
                 + tbl(['Other pre-tax IRAs on 31 Dec', 'Tax-free share', 'Taxable', 'Tax at 24%', 'Tax at 32%'], brow)
                 + '<p>Married filing separately, if you lived with your spouse at any time in the year, the Roth phase-out range is $0 – $10,000, '
                   'so almost everyone in that status needs the backdoor route. Report the non-deductible contribution and the conversion on Form 8606.</p>'),
    faq=[('What is the Roth IRA income limit for 2027?', 'The 2027 phase-out range is $158,000–$173,000 of modified AGI for single and head-of-household filers and $250,000–$260,000 for married couples filing jointly. Above the top of the range you cannot contribute directly.'),
         ('How much can I put in a backdoor Roth in 2027?', 'The 2027 IRA contribution limit is $7,500, or $8,600 if you are 50 or older ($7,500 + $1,100 catch-up). The limit is shared across all your traditional and Roth IRAs.'),
         ('Does a 401(k) count in the pro-rata rule?', 'No. Only traditional, SEP and SIMPLE IRA balances on 31 December count, which is why people roll pre-tax IRA money into a workplace plan before year-end.')],
    js=[], txt=[],
    src='IRS News Release IR-2026-136 (12 Nov 2026): 2027 IRA limit and Roth IRA phase-out ranges',
    srcurl='https://www.irs.gov/newsroom/401k-limit-increases-to-25500-for-2027-ira-limit-remains-7500')

# AMT
arows = []
for lab, fs, ti, adj in [('Single, $200,000 income, $50,000 ISO spread', 0, 200000, 50000),
                         ('Single, $250,000 income, $200,000 adjustments', 0, 250000, 200000),
                         ('Joint, $400,000 income, $150,000 adjustments', 1, 400000, 150000),
                         ('Joint, $300,000 income, $400,000 ISO spread', 1, 300000, 400000),
                         ('Single, $150,000 income, $400,000 ISO spread', 0, 150000, 400000)]:
    ai, exm, tmt, rg, amt = amt27(fs, ti, adj)
    arows.append([lab, money(ai), money(exm), money(rg), '<b>%s</b>' % money(amt)])
PAGES['en/money/amt-calculator.html'] = dict(
    title='AMT Calculator 2027 (exemption $93,000 / $144,700, 26% / 28%)',
    desc='2027 AMT exemption: $93,000 single, $144,700 joint; phase-out from $515,950 / $1,031,900; 28% above $252,500. Estimate your AMT for 2027 or 2026.',
    h1='AMT <b>Calculator</b> 2027 (alternative minimum tax: exemption, phase-out, 26% / 28%)',
    accent='#9B2F45', bg='#FBF1F3', layout='chips',
    box=lambda: ('<h2>2027 AMT numbers, then five examples</h2>'
                 '<p class="lead">For 2027 the AMT exemption is <b>$93,000</b> for single filers and <b>$144,700</b> for married couples filing jointly ($72,350 married filing separately). '
                 'It shrinks by 50 cents per dollar of AMTI above <b>$515,950</b> ($1,031,900 joint), and the 28% rate starts at $252,500 of AMT base ($126,250 separately).</p>'
                 + chips([('$93,000', 'exemption, single / HOH'), ('$144,700', 'exemption, joint'), ('$515,950', 'phase-out start, single'),
                          ('$1,031,900', 'phase-out start, joint'), ('$252,500', '28% rate starts (AMT base)')])
                 + '<h3>Five 2027 examples (regular tax estimated from the 2027 brackets)</h3>'
                 + tbl(['Situation', 'AMTI', 'Exemption left', 'Regular tax', 'AMT owed'], arows)
                 + '<p>The pattern: ordinary wage earners rarely owe AMT because the exemption is large and the regular 32–37% brackets already exceed 26–28%. '
                   'The usual trigger is a big incentive-stock-option exercise held past year-end, which adds the bargain element to AMTI but not to regular income.</p>'
                 + '<table style="display:none"></table>'),
    faq=[('What is the AMT exemption for 2027?', '$93,000 for single and head-of-household filers, $144,700 for married filing jointly and $72,350 for married filing separately (Rev. Proc. 2026-35).'),
         ('When does the AMT exemption phase out in 2027?', 'It is reduced by 25% of AMTI above $515,950 for single filers (gone at $701,950) and above $1,031,900 for joint filers (gone at $1,321,300).'),
         ('At what amount does the 28% AMT rate apply in 2027?', 'On AMT base (AMTI minus exemption) above $252,500, or above $126,250 if married filing separately. Below that the rate is 26%.')],
    js=[("const FBS=[12400,50400,105700,201775,256225,640600],FBJ=[24800,100800,211400,403550,512450,768700];",
         "const Y6=YR()===2026,FBS=Y6?[12400,50400,105700,201775,256225,640600]:[12800,52025,109125,208325,264550,661375],FBJ=Y6?[24800,100800,211400,403550,512450,768700]:[25600,104050,218250,416650,529100,793650];"),
        ("const ex0=[90100,140200,90100,70100][fs],th=fs===1?1000000:500000,bk=fs===3?122250:244500",
         "const ex0=(YR()===2026?[90100,140200,90100,70100]:[93000,144700,93000,72350])[fs],th=YR()===2026?(fs===1?1000000:500000):(fs===1?1031900:515950),bk=YR()===2026?(fs===3?122250:244500):(fs===3?126250:252500)")],
    txt=[('estimates the US alternative minimum tax (AMT) for 2026.', 'estimates the US alternative minimum tax (AMT) for 2027 or 2026 (choose the tax year).'),
         ('0 estimates it from the 2026 brackets', '0 estimates it from that year’s brackets')],
    src='IRS News Release IR-2026-133 (5 Nov 2026) and Rev. Proc. 2026-35, sections on AMT exemption and brackets (2027)',
    srcurl='https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts')

# Jumbo
jrows = []
for price in (900000, 1069250, 1100000, 1300000, 1600000):
    L = price * 0.8
    jrows.append([money(price), money(L), 'Jumbo' if L > 855400 else 'Conforming', money(max(0, price - 855400)) + (' (%.1f%%)' % (max(0, price - 855400) / price * 100)), money(pmt(L, 6.5, 30))])
PAGES['en/money/jumbo-loan-calculator.html'] = dict(
    title='Jumbo Loan Calculator 2027 (conforming limit $855,400)',
    desc='2027 conforming loan limit is $855,400 (high-cost ceiling $1,283,100). Check if your mortgage is jumbo, the payment and the down payment to stay conforming.',
    h1='Jumbo Loan <b>Calculator</b> (2027 conforming limit $855,400)',
    accent='#1F7A8C', bg='#EEF7F9', layout='split',
    box=lambda: ('<h2>Is it a jumbo loan in 2027?</h2>'
                 '<p class="lead">From 1 January 2027 a one-unit mortgage above <b>$855,400</b> is a jumbo loan in most US counties (2026: $832,750, +2.72%). '
                 'In high-cost areas the limit can go up to <b>$1,283,100</b>; in Alaska, Hawaii, Guam and the US Virgin Islands the baseline is $1,283,100 and the ceiling $1,924,650.</p>'
                 '<div class="two"><div><b>Most counties</b><br>$855,400 (one unit)<br><small>With 20% down, homes up to $1,069,250 stay conforming.</small></div>'
                 '<div><b>Highest-cost counties</b><br>up to $1,283,100<br><small>Look up your county’s exact limit on FHFA’s map before you apply.</small></div></div>'
                 '<h3>20% down at the 2027 baseline limit (6.5%, 30 years)</h3>'
                 + tbl(['Home price', 'Loan (80%)', 'Type', 'Minimum down payment to stay conforming', 'Monthly P&amp;I'], jrows)
                 + '<p>Rates in the table are only an example. Jumbo lenders set their own rules, often asking for a higher credit score, '
                   'more cash reserves and a lower debt-to-income ratio than conforming loans.</p>'),
    faq=[('What is the conforming loan limit for 2027?', 'FHFA set the 2027 baseline one-unit conforming loan limit at $855,400, up from $832,750 in 2026. The high-cost ceiling is $1,283,100.'),
         ('What home price makes a loan jumbo with 20% down in 2027?', 'Above $1,069,250 in a baseline county, because 80% of $1,069,250 equals the $855,400 limit.'),
         ('When do the 2027 loan limits take effect?', 'For loans delivered to Fannie Mae and Freddie Mac from 1 January 2027 (FHFA announcement of 24 November 2026).')],
    js=[('value="832750"', 'value="855400"'), ('2026 one-unit limit: 832,750', '2027 one-unit limit: 855,400 (2026: 832,750)')],
    txt=[('For 2026 the one-unit baseline is 832,750 USD, and in high-cost areas it can reach 1,249,125 USD (150% of the baseline).',
          'For 2027 the one-unit baseline is 855,400 USD, and in high-cost areas it can reach 1,283,100 USD (150% of the baseline); for 2026 they were 832,750 and 1,249,125 USD.'),
         ('Default inputs: price 1,100,000 USD, 20% down, limit 832,750 USD', 'Example with the 2026 limit: price 1,100,000 USD, 20% down, limit 832,750 USD')],
    src='Federal Housing Finance Agency, “FHFA Announces Conforming Loan Limit for 2027” (24 Nov 2026)',
    srcurl='https://www.fhfa.gov/news/news-release/fhfa-announces-conforming-loan-limit-for-2027')

# Lottery
lrows = []
for prize in (10000, 100000, 1000000, 10000000, 100000000):
    w = prize - 2
    fed = btax(60000 + w, B27S) - btax(60000, B27S)
    whd = 0.24 * w if w > 5000 else 0
    lrows.append([money(prize), money(fed), money(whd), money(fed - whd) if fed >= whd else '−%s (over-withheld)' % money(whd - fed), '%.1f%%' % (fed / prize * 100)])
PAGES['en/money/lottery-tax-calculator.html'] = dict(
    title='Lottery Tax Calculator 2027 (US federal + state, Korea 22%/33%)',
    desc='Federal tax on lottery winnings with 2027 brackets (37% above $661,375 single): see what is withheld (24%), what is still owed and what you keep.',
    h1='Lottery Tax <b>Calculator</b> (2027 US brackets, state, Korea or a flat rate)',
    accent='#B58A1F', bg='#FCF8EC', layout='steps',
    box=lambda: ('<h2>Lottery tax in 2027: the short answer</h2>'
                 '<p class="lead">A US lottery prize over $5,000 has <b>24%</b> federal tax withheld at payout, but the prize is ordinary income, so a large win is taxed mostly at '
                 '<b>37%</b> — the 2027 top rate starts above <b>$661,375</b> (single) or <b>$793,650</b> (married filing jointly). The gap is due when you file.</p>'
                 '<ol class="yst"><li>Subtract the ticket price from the prize.</li><li>Add the winnings to your other taxable income for the year.</li>'
                 '<li>Federal tax on the prize = tax on the total − tax on your other income alone (2027 brackets).</li>'
                 '<li>Add your state rate (0% in states such as Florida or Texas, which have no state income tax).</li></ol>'
                 '<h3>Federal tax on a prize in 2027 (single, $60,000 other income, $2 ticket)</h3>'
                 + tbl(['Prize', 'Federal tax', 'Withheld (24%)', 'Still owed at filing', 'Effective'], lrows)
                 + '<p>Taking an annuity spreads the prize over many years, so less of each payment may reach the 37% bracket — but each year’s payment is still taxed as ordinary income in that year.</p>'),
    faq=[('How much federal tax is taken from lottery winnings in 2027?', 'The payer withholds 24% of winnings over $5,000. Your final federal tax uses the 2027 brackets, so for large prizes most of the money is taxed at 37% and you owe the difference when you file.'),
         ('At what income does the 37% bracket start in 2027?', 'Above $661,375 of taxable income for single filers and above $793,650 for married couples filing jointly (Rev. Proc. 2026-35).'),
         ('How much would I owe on a $1 million lottery win in 2027?', 'With $60,000 of other income as a single filer, federal tax on the prize is about $339,000 (33.9%), of which $240,000 is withheld at payout; state tax comes on top.')],
    js=[("BRK=fs==0?[[12400,10],[50400,12],[105700,22],[201775,24],[256225,32],[640600,35],[Infinity,37]]:[[24800,10],[100800,12],[211400,22],[403550,24],[512450,32],[768700,35],[Infinity,37]]",
         "BRK=YR()===2026?(fs==0?[[12400,10],[50400,12],[105700,22],[201775,24],[256225,32],[640600,35],[Infinity,37]]:[[24800,10],[100800,12],[211400,22],[403550,24],[512450,32],[768700,35],[Infinity,37]]):(fs==0?[[12800,10],[52025,12],[109125,22],[208325,24],[264550,32],[661375,35],[Infinity,37]]:[[25600,10],[104050,12],[218250,22],[416650,24],[529100,32],[793650,35],[Infinity,37]])")],
    txt=[('(federal income tax at 2026 rates plus your state rate)', '(federal income tax at 2027 or 2026 rates plus your state rate)')],
    src='IRS News Release IR-2026-133 (5 Nov 2026) and Rev. Proc. 2026-35 (2027 tax rate tables)',
    srcurl='https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts')


def esc(s):
    return html.escape(s, quote=True)


def plain(s):
    return re.sub(r'<[^>]+>', '', s)


def build(path, d):
    s = open(os.path.join(ORIG, path), encoding='utf-8').read()
    old_core = html.unescape(re.search(r'<title>(.*?) – Free Calculator</title>', s).group(1))
    new = d['title']
    # titles everywhere (escaped html and raw json)
    for o, n in ((esc(old_core), esc(new)), (old_core, new)):
        s = s.replace(o, n)
    s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(d['desc']), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(d['desc']), s, count=1)
    s = re.sub(r'(<meta name="twitter:description" content=")[^"]*', lambda m: m.group(1) + esc(d['desc']), s, count=1)
    s = re.sub(r'("@type": "WebApplication".*?"description": ")[^"]*', lambda m: m.group(1) + d['desc'].replace('"', '\\"'), s, count=1, flags=re.S)
    s = re.sub(r'<h1>.*?</h1>', '<h1>%s</h1>' % d['h1'], s, count=1, flags=re.S)
    # year selector + JS
    if d['js'] and 'YR()' in ''.join(n for _, n in d['js']):
        s = s.replace('<h2>Your numbers</h2>', '<h2>Your numbers</h2>' + YR_SEL, 1)
        i = s.find('function calc(')
        s = s[:i] + YR_JS + s[i:]
    for o, n in d['js']:
        assert o in s, (path, o)
        s = s.replace(o, n)
    for o, n in d['txt']:
        assert o in s, (path, o)
        s = s.replace(o, n)
    # answer-first box
    box = '<section class="y27" id="y27">%s<p class="src">Source: <a href="%s" rel="nofollow">%s</a> · checked %s.</p></section>' % (
        d['box'](), d['srcurl'], d['src'], CHECK)
    s = s.replace('<article class="card hl-explain" id="hl-explain">', '<article class="card hl-explain" id="hl-explain">' + box, 1)
    s = s.replace('</head>', css(d['accent'], d['bg'], d['layout']) + '</head>', 1)
    # FAQ visible + JSON-LD
    fq = ''.join('<h4 class="q">%s</h4><p class="a">%s</p>' % (q, a) for q, a in d['faq'])
    s = re.sub(r'(<h3>Frequently asked questions</h3>)', lambda m: m.group(1) + fq, s, count=1)
    m = re.search(r'<script type="application/ld\+json">(\{[^<]*?"@type":\s*"FAQPage".*?)</script>', s, re.S)
    j = json.loads(m.group(1))
    j['mainEntity'] = [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in d['faq']] + j['mainEntity']
    s = s[:m.start(1)] + json.dumps(j, ensure_ascii=False) + s[m.end(1):]
    s = s.replace('<article class="card help"><p class="note">', '<article class="card help"><p class="note">Updated %s for 2027: %s. ' % (CHECK, esc(d['src'])), 1)
    s = s.replace('Last reviewed: November 2026', 'Last reviewed: 27 November 2026')
    s = s.replace('<table style="display:none"></table>', '')
    out = os.path.join(ROOT, 'overlay', path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)
    print('ok', path, len(plain(re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S))))


if __name__ == '__main__':
    for p, d in PAGES.items():
        build(p, d)
