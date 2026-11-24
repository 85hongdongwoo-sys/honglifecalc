import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/uk/savings-goal-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Savings goal (£)</span><input id="T" inputmode="decimal" value="16,000"></label><label class="f"><span>Already saved (£)</span><input id="C" inputmode="decimal" value="1,600"></label><label class="f"><span>Years to reach the goal</span><input id="y" inputmode="decimal" value="3"><small>Use decimals for months: 18 months = 1.5.</small></label><label class="f"><span>Interest rate on savings (% a year)</span><input id="r" inputmode="decimal" value="4"><small>An example rate – use the rate your own account pays. Enter 0 for no interest.</small></label></form>'''

calc='''function calc(){const T=num('T'),C=num('C'),i=num('r')/1200,n=Math.round(num('y')*12);
 const nt='<p class="note">Assumes a deposit at the end of each month, interest added monthly at a steady rate, and no tax taken off. Most people pay no tax on savings interest thanks to the Personal Savings Allowance, and ISA interest is always tax-free.</p>';
 if(n<1)return big(O.need,'–','Enter a time of at least 1 month (0.08 years)');
 const g=Math.pow(1+i,n),grow=C*g;
 if(grow>=T)return big('You are already on track',mf(0,0),O.per)+kv([['What you have saved grows to',mf(grow)],['Interest earned',mf(grow-C,0),'pos'],['Months',String(n)]])+nt;
 const need=i?(T-grow)*i/(g-1):(T-C)/n,dep=need*n;
 return big(O.need,mf(need),O.per)+kv([['About per week',mf(need*12/52)],[O.tot,mf(dep)],['Already saved',mf(C,0)],[O.int,mf(Math.max(0,T-C-dep),0),'pos'],['Months',String(n)]])+nt}'''

def need(T,C,y,r):
    i=r/1200;n=round(y*12);g=(1+i)**n
    if C*g>=T: return 0
    return (T-C*g)*i/(g-1) if i else (T-C)/n
p=lambda x:f"£{x:,.0f}"
rows=[]
for T,y,lab in [(5000,1,'£5,000'),(10000,2,'£10,000'),(20000,3,'£20,000'),(30000,5,'£30,000 (house deposit)')]:
    a=[need(T,0,y,r) for r in (0,3,4)]
    rows.append([lab,f"{y} year{'s' if y>1 else ''}",p(a[0]),p(a[1]),p(a[2]),p(T-a[2]*y*12)])
dflt=need(16000,1600,3,4)
print(rows, round(dflt,2))

fig=[['Bank of England Bank Rate','4% (raised from 3.75%, announced 5 November 2026)','The Bank\'s main interest rate. Savings rates often move after it changes. Next decision: 17 December 2026.'],
     ['FSCS protection','£120,000 per person, per authorised bank or building society','If your bank fails, your savings are paid back up to this amount.'],
     ['ISA allowance 2026/27','£20,000 a year','Interest in a cash ISA is tax-free. Budget 2026 keeps the cash ISA limit at £20,000 from April 2027.'],
     ['Lifetime ISA','Up to £4,000 a year, 25% government bonus (max £1,000)','Open at 18–39. For a first home or later life; other withdrawals lose 25%.'],
     ['Personal Savings Allowance','£1,000 basic rate · £500 higher rate · £0 additional rate','Interest you can earn each tax year outside an ISA without paying tax.'],
     ['Starting rate for savings','Up to £5,000 of interest tax-free','Only if your other taxable income is under £17,570.'],
     ['Tax on savings interest from 2027/28','24% basic · 44% higher · 49% additional','New savings tax rates confirmed at Budget 2026. Interest inside the allowances stays tax-free.']]

FAQ=[
("How much do I need to save each month to reach my goal?","Take what you still need and divide it by the number of months. Interest then lowers the amount a little. For £10,000 in 2 years from zero: £10,000 ÷ 24 = £417 a month with no interest, or £401 a month at 4% a year."),
("How long does it take to save £10,000?","At £500 a month it takes 20 months (with no interest you reach exactly £10,000). At £250 a month it takes 40 months, or about 3 years and 4 months. Interest makes it a little quicker."),
("How much should I save a month for a house deposit?","For a £30,000 deposit in 5 years from zero you need £500 a month with no interest, or £452 a month at 4% a year. A Lifetime ISA can help: the government adds 25% on up to £4,000 a year, so £4,000 becomes £5,000."),
("Do I pay tax on the interest from my savings?","Most people don't. Basic-rate taxpayers can earn £1,000 of interest a year tax-free and higher-rate taxpayers £500. Interest in a cash ISA is always tax-free. From April 2027 interest above the allowances is taxed at 24%, 44% or 49%."),
("Is my money safe in a UK savings account?","Yes, up to £120,000 per person at each authorised bank or building society, through the Financial Services Compensation Scheme (FSCS). Some banks share one licence, so check before you split money between brands."),
("Why does the Bank of England rate matter for my savings?","Banks often change their savings rates after Bank Rate moves. Bank Rate went up to 4% on 5 November 2026. If it changes again, re-run the calculator with your new rate."),
]

art='''<h2 id="figures">Official UK figures for savers (November 2026)</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<p class="note">We don't list bank savings rates. They change often and differ by bank and account. Use the rate your own account pays.</p>
<h2 id="ex">How much to save each month: examples</h2>
<div id="examples">'''+table(['Goal','Time','Per month, no interest','Per month at 3% a year','Per month at 4% a year','Interest earned at 4%'],rows)+'''</div>
<ul><li>To save <b>£5,000 in 1 year</b> you need about £417 a month. At 4% interest it is £409.</li>
<li>To save <b>£20,000 in 3 years</b> you need £556 a month with no interest, or £524 at 4%. Interest adds about £1,143.</li>
<li>For a <b>£30,000 house deposit in 5 years</b> you need £452 a month at 4%. Interest adds about £2,850 – more than six months of saving.</li></ul>
<p class="note">All examples start from £0 and use this calculator's formula. 3% and 4% are example rates, not bank quotes.</p>
<h2 id="how">How the calculator works</h2>
<p>Example first. You want £16,000 in 3 years. You already have £1,600 and your account pays 4% a year. The £1,600 grows on its own to about £1,804. You still need about £14,196. Saving <b>£372 a month</b> gets you there, because interest on your deposits adds about £1,015 along the way.</p>
<ul><li><b>Monthly rate</b> = yearly rate ÷ 12. So 4% a year is about 0.33% a month.</li>
<li><b>Compound interest</b> means you also earn interest on your interest. The calculator adds interest every month.</li>
<li><b>Gap</b> = goal − what your current savings will grow to.</li>
<li><b>Monthly saving</b> = gap × i ÷ ((1 + i)<sup>n</sup> − 1). Here i is the monthly rate and n is the number of months.</li></ul>
<p>With no interest it is simply (goal − already saved) ÷ months. If your savings already grow past the goal, you need £0 a month.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Pay yourself first.</b> Set up a standing order on payday so the money moves before you can spend it.</li>
<li><b>Check the real rate.</b> Some accounts pay a bonus rate only for 12 months, or only if you make no withdrawals. Enter the rate you will actually get.</li>
<li><b>Use your ISA allowance.</b> If your interest could go over £1,000 (or £500 as a higher-rate taxpayer), a cash ISA keeps it tax-free.</li>
<li><b>Saving for a first home?</b> Look at a Lifetime ISA. The 25% bonus beats most interest rates, but other withdrawals lose 25%.</li>
<li><b>Keep an emergency buffer too.</b> Then a surprise bill doesn't empty your goal pot.</li></ul>
<h2 id="faq" style="margin-top:22px">Savings goal FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 24 November 2026): <a href="https://www.bankofengland.co.uk/monetary-policy/the-interest-rate-bank-rate" rel="nofollow">Bank of England – Bank Rate</a>; <a href="https://www.fscs.org.uk/what-we-cover/banks-building-societies-credit-unions/deposit-limit/" rel="nofollow">FSCS – deposit limit</a>; <a href="https://www.gov.uk/individual-savings-accounts" rel="nofollow">GOV.UK – ISAs</a>; <a href="https://www.gov.uk/lifetime-isa" rel="nofollow">GOV.UK – Lifetime ISA</a>; <a href="https://www.gov.uk/government/publications/tax-free-savings-newsletter-24/tax-free-savings-newsletter-24-october-2026" rel="nofollow">HMRC – Tax-free savings newsletter 24</a>; <a href="https://www.gov.uk/apply-tax-free-interest-on-savings/how-much-is-tax-free" rel="nofollow">GOV.UK – Tax-free interest on savings</a>; <a href="https://www.gov.uk/government/publications/budget-2026-overview-of-tax-legislation-and-rates-ootlar/budget-2026-overview-of-tax-legislation-and-rates-ootlar" rel="nofollow">HM Treasury – Budget 2026 overview of tax legislation and rates</a>. Examples use this calculator's own formula. General information, not financial advice.</p>'''

out=build(P,'Savings Goal Calculator UK 2026 – How Much to Save Each Month',
 'Work out how much to save each month or week to reach a savings goal or house deposit, with interest. UK examples, ISA, FSCS and savings tax figures for 2026/27.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','24 November 2026'),('Sources','Bank of England, FSCS, HMRC, GOV.UK')],
 [('form','Calculator'),('figures','Official figures'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
