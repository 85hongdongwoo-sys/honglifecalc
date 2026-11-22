"""Weekly Search Console keyword pass (2026-11-22).
Adds answers for queries that pages were shown for but did not answer (titles, FAQ + FAQPage JSON-LD, example tables).
Numbers are computed with each page's own formula (see comments). Writes overlay/<path>.
Run: HL_ORIG=/tmp/hl_orig python3 build/pages/kw_20261122.py"""
import json, os, re

ORIG = os.environ.get('HL_ORIG', '/tmp/hl_orig')
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(ROOT, 'overlay')
MARK = '<!--kw1122-->'
TW = ('<div class="tw" style="overflow-x:auto;max-width:100%">{}</div>')


def tbl(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td data-l="{head[i]}">{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return TW.format(f'<table class="tbl kwt"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>')


def load(path):
    ov = os.path.join(OUT, path)
    src = ov if os.path.exists(ov) else os.path.join(ORIG, path)
    s = open(src, encoding='utf-8').read()
    if MARK in s:
        return None
    return s


KWCSS = ('<style id="kwt-css">.kwt{width:100%;border-collapse:collapse}.kwt th,.kwt td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line,#E3E7EE)}'
         '@media(max-width:640px){.kwt thead{display:none}.kwt,.kwt tbody,.kwt tr{display:block;width:100%}.kwt tr{padding:6px 0;border-bottom:1px solid var(--line,#E3E7EE)}'
         '.kwt td{display:flex;justify-content:space-between;gap:12px;border:0;padding:3px 2px;text-align:right}'
         '.kwt td::before{content:attr(data-l);font-weight:700;color:var(--muted,#5B6B82);text-align:left;flex:0 0 44%}}</style>')


def save(path, s):
    if 'kwt' in s and 'kwt-css' not in s:
        s = s.replace('</head>', KWCSS + '</head>', 1)
    out = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)
    print('wrote', path)


def head(s, title=None, desc=None):
    if title:
        s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{title}</title>', s, count=1, flags=re.S)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, s, count=1)
        s = re.sub(r'(<meta name="twitter:title" content=")[^"]*', lambda m: m.group(1) + title, s, count=1)
    if desc:
        s = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{desc}">', s, count=1)
        s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, s, count=1)
        s = re.sub(r'(<meta name="twitter:description" content=")[^"]*', lambda m: m.group(1) + desc, s, count=1)
    return s


def ld_add(s, faq):
    m = re.search(r'(<script type="application/ld\+json">)(\{"@context": ?"https://schema.org", ?"@type": ?"FAQPage".*?)(</script>)', s, re.S)
    assert m, 'no FAQPage'
    d = json.loads(m.group(2))
    have = {q['name'] for q in d['mainEntity']}
    for q, a in faq:
        qn = re.sub('<[^>]+>', '', q)
        if qn in have:
            continue
        d['mainEntity'].append({"@type": "Question", "name": qn,
                                "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}})
    return s[:m.start(2)] + json.dumps(d, ensure_ascii=False) + s[m.end(2):]


def ins_before(s, marker, html, start=0):
    i = s.find(marker, start)
    assert i >= 0, marker
    return s[:i] + html + s[i:]


def dl_faq(s, faq, after):
    i = s.find(after)
    assert i >= 0, after
    j = s.find('</dl>', i)
    return s[:j] + ''.join(f'<div><dt>{q}</dt><dd>{a}</dd></div>' for q, a in faq) + s[j:]


# ---------- 1. US bonus tax (overlay; page formula: 22% federal, 6.2% SS to $184,500, 1.45% Medicare, state x bonus)
def us_bonus():
    p = 'us/bonus-tax-calculator.html'
    s = load(p)
    if s is None: return
    s = head(s, 'Bonus Tax Calculator 2026: Calculate Your Bonus After Tax (22% + FICA)',
             'Calculate taxes on a bonus in 2026: 22% federal (37% over $1M), 7.65% FICA and state. A $1,000 bonus nets $703.50; $10,000 nets $7,035 with no state tax.')
    rows = [['$500 (e.g. Christmas bonus)', '$110', '$31', '$7.25', '–', '<b>$351.75</b>'],
            ['$1,000', '$220', '$62', '$14.50', '–', '<b>$703.50</b>'],
            ['$5,000 in Illinois (4.95%)', '$1,100', '$310', '$72.50', '$247.50', '<b>$3,270</b>'],
            ['$60,000 (wages before it $100,000)', '$13,200', '$3,720', '$870', '–', '<b>$42,210</b>']]
    yrs = [['2018 – 2026 (incl. 2021, 2022, 2023, 2024, 2025)', '22%', '37%'], ['2017 and earlier', '25%', '39.6%']]
    sec = (MARK + '<h3>More bonus after-tax examples</h3>'
           '<p>Same method as the calculator (flat 22% federal, 6.2% Social Security, 1.45% Medicare; wages before the bonus $50,000 unless shown):</p>'
           + tbl(['Bonus', 'Federal 22%', 'Social Security', 'Medicare', 'State', 'You receive'], rows) +
           '<h3>Federal bonus tax rate by year</h3>'
           + tbl(['Year', 'Supplemental rate', 'Above $1 million'], yrs) +
           '<p>The flat rate has been 22% every year since the Tax Cuts and Jobs Act took effect in 2018, so the 2022, 2023, 2024 and 2026 federal bonus tax rate is the same 22%.</p>')
    s = ins_before(s, '<h3>Withheld 22% vs. the tax you really owe</h3>', sec)
    faq = [('How much is a $1,000 bonus after taxes?',
            'About $703.50 with no state income tax: $220 federal (22%), $62 Social Security and $14.50 Medicare are withheld. In a state that withholds 5%, another $50 comes off, leaving $653.50.'),
           ('What was the federal bonus tax rate in 2022, 2023 and 2024?',
            '22% in each of those years (37% on supplemental pay above $1 million). The same rates apply in 2025 and 2026; before 2018 the flat rate was 25%.'),
           ('How much is a $60,000 bonus after tax?',
            'About $42,210 with no state tax if your wages before it were $100,000: $13,200 federal, $3,720 Social Security and $870 Medicare. If your wages already passed $184,500, no Social Security is withheld and you receive about $45,930.'),
           ('How are bonuses taxed in Florida or Texas?',
            'Florida and Texas have no state income tax, so only the 22% federal rate, 6.2% Social Security and 1.45% Medicare apply: a $5,000 bonus nets about $3,517.50 (with wages before it of $50,000).'),
           ('What is the aggregate method for bonus tax?',
            'The employer adds the bonus to a regular paycheck and withholds as if the total were your normal pay for that period, then subtracts the tax already withheld on regular pay. It often withholds more than 22% on a large bonus; the final tax on your return is the same either way.')]
    k = s.find('<h2 style="margin-top:22px">FAQ</h2>')
    j = s.find('<p', s.find('Does Social Security tax apply to my bonus?', k))
    j = s.find('<p', j + 2)  # the Sources paragraph after the last answer
    s = s[:j] + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in faq) + s[j:]
    s = ld_add(s, faq)
    save(p, s)


# ---------- 2. Slope (formula: m = rise/run, grade = m*100, angle = atan m)
def slope():
    p = 'en/math/slope-calculator.html'
    s = load(p)
    if s is None: return
    s = head(s, 'Slope Calculator – Slope, Equation, Angle &amp; Grade from Two Points',
             'Enter two points to get the slope m = (y₂ − y₁) ÷ (x₂ − x₁), line equation, angle, grade % and distance. A 1:2 slope = 0.5 = 50% = 26.57°.')
    rows = [['1:1', '1', '100%', '45°'], ['1:2', '0.5', '50%', '26.57°'], ['1:3', '0.3333', '33.33%', '18.43°'],
            ['1:4', '0.25', '25%', '14.04°'], ['1:12', '0.0833', '8.33%', '4.76°']]
    sec = (MARK + '<h3>Slope ratios (1:2, 1:3 …) as slope, grade and angle</h3>'
           '<p>A ratio rise:run of 1:2 means the line goes up 1 for every 2 across — the same as points (0, 0) and (2, 1) in the calculator.</p>'
           + tbl(['Ratio (rise:run)', 'Slope m', 'Grade', 'Angle'], rows))
    s = ins_before(s, '<h3>Frequently asked questions</h3>', sec)
    faq = [('What is a 1:2 slope?', 'A 1:2 slope rises 1 unit for every 2 units across: slope 0.5, a 50% grade, an angle of about 26.57°. In earthworks a bank is often written horizontal:vertical, so “2:1” there describes the same 0.5 slope.'),
           ('How do I turn a slope ratio into degrees?', 'Divide rise by run, then take the arctangent: 1:3 → 1 ÷ 3 = 0.3333 → arctan 0.3333 ≈ 18.43°.')]
    i = s.find('<h3>Frequently asked questions</h3>')
    s = ins_before(s, '<p class="src">', ''.join(f'<h4 class="q">{q}</h4><p class="a">{a}</p>' for q, a in faq), i)
    s = ld_add(s, faq)
    save(p, s)


# ---------- 3. Drive time (driving = distance/speed; breaks = ceil(drive/interval)-1)
def drive():
    p = 'en/home/drive-time-calculator.html'
    s = load(p)
    if s is None: return
    s = head(s, 'Drive Time Calculator – How Long to Drive &amp; Arrival Time with Breaks',
             'How long will the drive take? Enter distance, average speed and departure time to get driving time and arrival time with breaks. 1,800 miles at 60 mph = 30 h.')
    rows = [['300 miles', '5 h', '4 h 37 min', '4 h 17 min'], ['500 miles', '8 h 20 min', '7 h 42 min', '7 h 09 min'],
            ['1,000 miles', '16 h 40 min', '15 h 23 min', '14 h 17 min'], ['1,800 miles', '30 h', '27 h 42 min', '25 h 43 min'],
            ['13,000 miles', '216 h 40 min', '200 h', '185 h 43 min']]
    sec = (MARK + '<h3>How long does it take to drive …? (driving time only, no breaks)</h3>'
           + tbl(['Distance', 'At 60 mph', 'At 65 mph', 'At 70 mph'], rows) +
           '<p>Add your stops on top: with a 15-minute break every 2 hours, a 300-mile trip at 60 mph takes 5 h 30 min, so leaving at 4:00 am you arrive at 9:30 am.</p>')
    s = ins_before(s, '<h3>Frequently asked questions</h3>', sec)
    faq = [('How long would it take to drive 13,000 miles at 60 mph?', '216 hours 40 minutes of driving (13,000 ÷ 60 = 216.7 h) — about 9 days nonstop, or about 27 days at 8 hours of driving a day.'),
           ('How long does it take to drive 1,800 miles?', '30 hours at an average of 60 mph, 27 h 42 min at 65 mph and 25 h 43 min at 70 mph, before breaks and overnight stops.'),
           ('If I leave at 4 am, what time will I arrive?', 'Add the total trip time to 4:00. For example, 300 miles at 60 mph with a 15-minute break every 2 hours takes 5 h 30 min, so you arrive at 9:30 am. Enter 04:00 as the departure time to get your own arrival time.')]
    i = s.find('<h3>Frequently asked questions</h3>')
    j = s.find('</article>', i)
    k = s.find('<p class="src">', i)
    at = k if 0 <= k < j else j
    s = s[:at] + ''.join(f'<h4 class="q">{q}</h4><p class="a">{a}</p>' for q, a in faq) + s[at:]
    s = ld_add(s, faq)
    save(p, s)


# ---------- 4. Korea severance (g.js krsev: daily = monthly*3/91, pay = daily*30*days/365)
def severance():
    p = 'en/korea-severance-pay-calculator.html'
    s = load(p)
    if s is None: return
    s = head(s, 'Korea Severance Pay Calculator 2026 — Severance Pay in Korea (Toejikgeum)',
             'Korea severance pay calculator: about one month of average pay per year worked. 3 years at ₩3.2 million a month ≈ ₩9.49 million before tax. For foreign workers too.')
    fm = lambda n: '₩' + format(n, ',')
    data = {2500000: [2472527, 7417582, 12362637], 3000000: [2967033, 8901099, 14835165], 3200000: [3164835, 9494505, 15824176],
            3500000: [3461538, 10384615, 17307692], 4000000: [3956044, 11868132, 19780220]}
    rows = [[fm(m)] + [fm(x) for x in v] for m, v in data.items()]
    sec = (MARK + '<h2>Severance pay in Korea: examples</h2>'
           '<p>Calculated with this page\'s formula (last 3 months of pay ÷ 91 days × 30 days × years of service, no bonus), before retirement income tax:</p>'
           + tbl(['Monthly pay', '1 year', '3 years', '5 years'], rows))
    s = ins_before(s, '<h3>Frequently asked questions</h3>', sec)
    faq = [('How much is severance pay in Korea per year of service?', 'About one month of average pay for each year: 30 days of average daily wage. At ₩3,000,000 a month that is about ₩2,967,033 per year, or ₩8,901,099 for 3 years.'),
           ('Do I get severance if I worked less than one year?', 'No. You need at least 1 year (365 days) of service at 15 or more hours a week; under that, the calculator shows “not eligible yet”.')]
    s = dl_faq(s, faq, '<h3>Frequently asked questions</h3>')
    s = ld_add(s, faq)
    save(p, s)


# ---------- 5. Russian saju (title/FAQ for "саджу рассчитать", "саджу по дате рождения")
def ru_saju():
    p = 'ru/korean-saju-calculator.html'
    s = load(p)
    if s is None: return
    s = head(s, 'Саджу: рассчитать онлайн по дате рождения — Четыре столпа (사주팔자)')
    faq = [('Как рассчитать саджу по дате рождения?', 'Введите дату, время и город рождения — калькулятор сам переводит их в восемь знаков: столпы года, месяца, дня и часа (по небесному стволу и земной ветви в каждом), затем показывает баланс пяти стихий, десять божеств и 10-летние циклы удачи. Расчёт бесплатный, онлайн.'),
           ('Можно ли рассчитать саджу без времени рождения?', 'Да, столпы года, месяца и дня (шесть знаков из восьми) считаются только по дате. Без времени не будет столпа часа, поэтому часть толкования будет менее точной.')]
    s = dl_faq(s, faq, '<h3>Частые вопросы</h3>')
    s = ld_add(s, faq)
    s = s.replace('<dl><div><dt>Что такое корейский саджу?', MARK + '<dl><div><dt>Что такое корейский саджу?', 1)
    save(p, s)


# ---------- 6. Chinese loan: add 等额本金 to the calculator (monthly principal P/n, interest on remaining balance)
def zh_loan():
    p = 'zh/loan-calculator.html'
    s = load(p)
    if s is None: return
    s = head(s, '贷款计算器 — 等额本息、等额本金月供与利息总额计算',
             '计算房贷、车贷和消费贷的每月还款额、利息总额和剩余本金，支持等额本息和等额本金两种还款方式，默认以人民币（元）计。')
    s = s.replace("['type','还款方式','select',[['ann','等额本息（每月还款额固定）'],['flat','固定费率（按本金计息）']]]",
                  "['type','还款方式','select',[['ann','等额本息（每月还款额固定）'],['eqp','等额本金（每月本金固定，月供逐月递减）'],['flat','固定费率（按本金计息）']]]", 1)
    old = "    if(v.type==='flat'){pay=v.amt/n+v.amt*v.rate/100/12;total=pay*n;}"
    assert old in s
    s = s.replace(old, old + "\n    else if(v.type==='eqp'){const pp=v.amt/n;let bal2=v.amt,tot2=0;const rows2=[];const ys=[1,2,3,5,10,15,20,25,30].filter(y=>y<=v.yrs);"
                  "for(let m=1;m<=n;m++){tot2+=pp+bal2*r;bal2-=pp;if(ys.includes(m/12))rows2.push(['第 '+(m/12)+' 年末剩余本金','',money(Math.max(bal2,0))]);}"
                  "const first=pp+v.amt*r,last=pp+pp*r,int2=tot2-v.amt;"
                  "return{k:'首月还款额（等额本金）',big:money(first),sub:'每月本金 '+money(pp)+' · 每月递减 '+money(pp*r)+' · 末月 '+money(last),"
                  "rows:[['贷款本金','',money(v.amt)],['利息总额','',money(int2)],['__t','还款总额',money(tot2)],...rows2],"
                  "note:'等额本金每月偿还相同的本金，利息按剩余本金计算，所以月供逐月减少，利息总额比等额本息少。'};}", 1)
    sec = (MARK + '<h3>等额本息与等额本金对比（贷款 100 万元）</h3>'
           + tbl(['条件', '等额本息', '等额本金'],
                 [['3.5%，30 年', '月供 4,490.45 元<br>利息总额 616,560.88 元', '首月 5,694.44 元 → 末月 2,785.88 元<br>利息总额 526,458.33 元'],
                  ['3.5%，20 年', '月供 5,799.60 元<br>利息总额 391,903.32 元', '首月 7,083.33 元 → 末月 4,178.82 元<br>利息总额 351,458.33 元'],
                  ['3.0%，30 年', '月供 4,216.04 元<br>利息总额 517,774.52 元', '首月 5,277.78 元 → 末月 2,784.72 元<br>利息总额 451,250.00 元']]) +
           '<p>等额本金：每月本金 = 贷款金额 ÷ 还款月数；每月利息 = 剩余本金 × 月利率；利息总额 = 贷款金额 × 月利率 × （月数 + 1）÷ 2。</p>')
    s = ins_before(s, '<h3>常见问题</h3>', sec)
    faq = [('等额本金的利息怎么计算？', '每月利息 = 剩余本金 × 月利率，利息总额 = 贷款金额 × 月利率 × （还款月数 + 1）÷ 2。例如 100 万元、年利率 3.5%、30 年，利息总额为 526,458.33 元，首月还 5,694.44 元，之后每月减少约 8.10 元。'),
           ('等额本息和等额本金哪个更划算？', '同样 100 万元、3.5%、30 年：等额本息每月固定 4,490.45 元，利息总额 616,560.88 元；等额本金利息总额 526,458.33 元，少约 9 万元，但前期月供更高（首月 5,694.44 元）。'),
           ('每月还的本金怎么算？', '等额本金每月本金固定 = 贷款金额 ÷ 还款月数，100 万元 30 年（360 个月）即每月 2,777.78 元；等额本息前期本金少、利息多，可在上方选择还款方式查看各年末剩余本金。')]
    s = dl_faq(s, faq, '<h3>常见问题</h3>')
    s = ld_add(s, faq)
    save(p, s)


# ---------- 7. IQ 70 (normal curve mean 100, SD 15: P(X<=70)=2.28%, 1 in 44)
def iq70():
    p = 'en/iq/iq-70.html'
    s = load(p)
    if s is None: return
    faq = [('Ile to 70 IQ? (How much is an IQ of 70?)',
            'An IQ of 70 is 30 points, or two standard deviations, below the average of 100: about the 2.3rd percentile, so roughly 1 in 44 people score 70 or lower. In Polish: <a href="/pl/iq/iq-70-co-oznacza.html" hreflang="pl">IQ 70 – co oznacza?</a>')]
    i = s.find('<section class="faq">')
    j = s.find('</section>', i)
    s = s[:j] + MARK + ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq) + s[j:]
    s = ld_add(s, faq)
    save(p, s)


if __name__ == '__main__':
    for f in (us_bonus, slope, drive, severance, ru_saju, zh_loan, iq70):
        f()
