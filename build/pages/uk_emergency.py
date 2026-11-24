import sys,math; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
P='/uk/emergency-fund-calculator.html'
def ex(e,m,h,s):
    t=e*m;g=max(0,t-h);n=math.ceil(g/s) if g else 0
    return [f'£{e:,}',str(m),f'£{h:,}',f'£{s:,}',f'£{t:,}',f'{n} months']
rows=[ex(1500,3,0,250),ex(2000,3,1000,300),ex(2000,6,2400,320),ex(2500,6,5000,400),ex(3000,6,0,500),ex(3000,9,10000,600)]
FAQ=[
("How much should I have in an emergency fund in the UK?","MoneyHelper, the government-backed money guidance service, suggests three to six months' essential outgoings, kept in an instant-access savings account. With essential costs of £2,000 a month that is £6,000 to £12,000."),
("How long will it take to build a £12,000 emergency fund?","Starting from £2,400 and saving £320 a month, the remaining £9,600 takes 30 months. Saving £500 a month instead cuts it to 20 months."),
("Should I pay off debt or build an emergency fund first?","Many people keep a small buffer first (for example one month of essentials) so a surprise bill doesn't go on a credit card, then clear expensive debt, then build up to three to six months. Credit card interest is usually far higher than savings interest."),
("Where should I keep my emergency fund?","In an easy-access savings account or easy-access cash ISA, so you can withdraw without notice or penalty. Deposits are protected by the FSCS up to £120,000 per person per authorised bank or building society (from 1 December 2025)."),
("Is interest on my emergency fund taxed?","Basic-rate taxpayers can earn £1,000 of savings interest a year tax-free (higher-rate £500, additional-rate £0), and interest in a cash ISA is always tax-free. The ISA allowance is £20,000 in 2026/27."),
("Why is 6 months recommended for self-employed people?","Income is less predictable and there is no employer sick pay. As a comparison, Statutory Sick Pay for employees is only £123.25 a week in 2026/27, so even employees on SSP usually need savings to cover the gap."),
]
art='''<h2>How the emergency fund target is calculated</h2>
<p><b>Target = essential monthly expenses × months to cover.</b> <b>Still to save = target − already saved.</b> <b>Months to reach it = still to save ÷ monthly saving</b>, rounded up. Essential expenses are what you must pay even in a bad month: rent or mortgage, council tax, energy, water, food, transport, insurance, phone and minimum debt repayments.</p>
<h3>How many months?</h3>
'''+table(['Your situation','Suggested cover'],[
['Stable job, two incomes, few dependants','3 months'],
['Single income, renting, or children','4–6 months'],
['Self-employed, contractor or irregular income','6 months or more'],
['Near retirement or in a volatile sector','6+ months'],
])+'''
<p class="note">MoneyHelper suggests three to six months' essential outgoings. The split above is a rule of thumb for where you might sit in that range, not an official rule.</p>
<h3>Worked examples</h3>
'''+table(['Essentials / month','Months','Already saved','Save / month','Target','Time to reach'],rows)+'''
<p class="note">Calculated with this page's formula (interest ignored).</p>
<h3>2026/27 figures worth knowing</h3>
'''+table(['Item','Figure'],[
['FSCS deposit protection','£120,000 per person, per authorised firm (from 1 Dec 2025)'],
['ISA allowance 2026/27','£20,000 (Budget 2026 keeps the cash ISA limit at £20,000 from April 2027 – the planned cut to £12,000 was reversed)'],
['Personal Savings Allowance','£1,000 basic rate · £500 higher rate · £0 additional rate'],
['Bank of England Bank Rate','4% (raised by 0.25 points, announced 5 November 2026)'],
['Statutory Sick Pay','£123.25 a week (2026/27)'],
['Universal Credit standard allowance, single 25+','£424.90 a month (2026/27)'],
])+'''
<h3>Common mistakes</h3>
<ul><li><b>Using total spending instead of essentials</b> — in an emergency you would cut takeaways, holidays and subscriptions, so the fund only needs to cover the essentials.</li>
<li><b>Locking it away</b> — fixed-term bonds and notice accounts pay more but you can't get the money immediately.</li>
<li><b>Investing it in shares</b> — markets can fall exactly when you lose your job.</li>
<li><b>Never topping it back up</b> — after using it, restart the monthly saving until you are back on target.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 21 November 2026): <a href="https://www.moneyhelper.org.uk/en/savings/types-of-savings/emergency-savings-how-much-is-enough" rel="nofollow">MoneyHelper — Emergency savings: how much is enough?</a>; <a href="https://www.fscs.org.uk/what-we-cover/banks-building-societies-credit-unions/deposit-limit-increase/" rel="nofollow">FSCS — deposit limit £120,000</a>; <a href="https://www.gov.uk/individual-savings-accounts/who-can-open-an-isa" rel="nofollow">GOV.UK — ISAs</a>; <a href="https://www.gov.uk/government/publications/tax-free-savings-newsletter-24/tax-free-savings-newsletter-24-october-2026" rel="nofollow">HMRC — Tax-free savings newsletter 24 (cash ISA limit kept at £20,000)</a>; <a href="https://www.gov.uk/apply-tax-free-interest-on-savings/how-much-is-tax-free" rel="nofollow">GOV.UK — tax-free interest on savings</a>; <a href="https://www.bankofengland.co.uk/monetary-policy-report/2026/November-2026" rel="nofollow">Bank of England — November 2026</a>; <a href="https://www.gov.uk/government/publications/benefit-and-pension-rates-2026-to-2027/proposed-benefit-and-pension-rates-2026-to-2027" rel="nofollow">DWP — benefit and pension rates 2026 to 2027</a>. Not financial advice.</p>'''
print(build(P,'Emergency Fund Calculator UK 2026 – How Much Cash to Keep Aside',
 'Work out your emergency fund target (3–6 months of essentials, as MoneyHelper suggests), what is still to save and how many months it takes. 2026/27 ISA, FSCS and savings tax figures.',art,FAQ))
