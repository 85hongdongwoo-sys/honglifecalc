import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
import math
P='/au/savings-goal-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Savings goal ($)</span><input id="T" inputmode="decimal" value="30,000"></label><label class="f"><span>Already saved ($)</span><input id="C" inputmode="decimal" value="3,000"></label><label class="f"><span>Years to reach the goal</span><input id="y" inputmode="decimal" value="3"><small>Use decimals for months: 18 months = 1.5.</small></label><label class="f"><span>Interest rate on savings (% a year)</span><input id="r" inputmode="decimal" value="4.5"><small>An example rate – use the rate your own account pays. Enter 0 for no interest.</small></label></form>'''

calc='''function calc(){const T=num('T'),C=num('C'),i=num('r')/1200,n=Math.round(num('y')*12);
 const nt='<p class="note">Assumes a deposit at the end of each month, interest added monthly at a steady rate, and no tax taken out. Interest is taxable income.</p>';
 if(n<1)return big(O.need,'–','Enter a time of at least 1 month (0.08 years)');
 const g=Math.pow(1+i,n),grow=C*g;
 if(grow>=T)return big('You are already on track',mf(0,0),O.per)+kv([['What you have saved grows to',mf(grow)],['Interest earned',mf(grow-C,0),'pos'],['Months',String(n)]])+nt;
 const need=i?(T-grow)*i/(g-1):(T-C)/n,dep=need*n;
 return big(O.need,mf(need),O.per)+kv([['About per fortnight',mf(need*12/26)],['About per week',mf(need*12/52)],[O.tot,mf(dep)],['Already saved',mf(C,0)],[O.int,mf(Math.max(0,T-C-dep),0),'pos'],['Months',String(n)]])+nt}'''

def need(T,C,y,r):
    i=r/1200;n=round(y*12);g=(1+i)**n
    if C*g>=T: return 0
    return (T-C*g)*i/(g-1) if i else (T-C)/n
d=lambda x:f"${x:,.0f}"
rows=[]
for T,y,lab in [(10000,1,'$10,000'),(10000,2,'$10,000'),(20000,2,'$20,000'),(20000,3,'$20,000'),(50000,3,'$50,000'),(50000,5,'$50,000'),(100000,3,'$100,000 (house deposit)'),(100000,5,'$100,000 (house deposit)')]:
    a=[need(T,0,y,r) for r in (0,4,5)]
    rows.append([lab,f"{y} year{'s' if y>1 else ''}",d(a[0]),d(a[1]),d(a[2]),d(T-a[2]*y*12)])
assert rows[0][2:]==['$833','$818','$814','$227'], rows[0]
dflt=need(30000,3000,3,4.5); assert round(dflt)==691
hd=need(100000,20000,5,4.5)

fig=[['RBA cash rate target','4.85% (from 4 November 2026)','The Reserve Bank\'s main interest rate. Savings account rates often move when it changes.'],
     ['Financial Claims Scheme','Up to $250,000 per account holder per bank','Government protection for deposits in Australian banks, building societies and credit unions if one fails.'],
     ['Tax on interest','Interest must be declared as income','It is added to your taxable income and taxed at your normal rate.'],
     ['Resident tax rates 2026-27','0% to $18,200 · 15% to $45,000 · 30% to $135,000 · 37% to $190,000 · 45% above','Plus the 2% Medicare levy.']]

FAQ=[
("How much do I need to save each month?","Divide what is still needed by the number of months, then take off a little for interest. For $20,000 in 2 years from zero: $20,000 ÷ 24 = $833 a month with no interest, or $794 a month if your account pays 5% a year."),
("How long does it take to save $10,000?","At $500 a month it takes 20 months – with no interest you hit exactly $10,000, and at 4.5% a year you have about $10,364. At $1,000 a month it takes 10 months; at $250 a month, about 3 years and 4 months without interest."),
("How much should I save each month for a house deposit?","For a $100,000 deposit in 5 years from zero, about $1,667 a month with no interest, or $1,470 a month at 5% a year. If you already have $20,000 and earn 4.5%, you need about $1,116 a month."),
("Does interest make a big difference?","Over a short time, not much: saving $10,000 in a year at 5% only saves you about $19 a month. Over 5 years it adds up: $1,000 a month at 5% grows to about $68,006 instead of $60,000."),
("Is the interest on my savings taxed?","Yes. The ATO says Australian residents must declare interest as income. It is added to your taxable income for the year, so at a 30% tax rate $1,000 of interest leaves you about $700 (less the 2% Medicare levy)."),
("Is my money safe in a savings account?","Deposits in Australian banks, building societies and credit unions are protected by the government's Financial Claims Scheme up to $250,000 per account holder per institution."),
]

def faq_block(faq):
    return '<h2 id="faq" style="margin-top:22px">Savings goal FAQ</h2>'+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faq)

art='''<h2 id="figures">Official figures for savers (November 2026)</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<p class="note">We do not list bank savings rates – they change often and differ by bank and account. Use the rate your account actually pays.</p>
<h2 id="ex">How much to save each month: examples</h2>
<div id="examples">'''+table(['Goal','Time','Per month, no interest','Per month at 4% a year','Per month at 5% a year','Interest earned at 5%'],rows)+'''</div>
<ul><li>To save <b>$10,000 in 1 year</b> you need about $833 a month. At 5% interest it is $814, because interest adds about $227.</li>
<li>To save <b>$50,000 in 5 years</b> you need $735 a month at 5%. Interest adds about $5,886 – more than 7 months of deposits.</li>
<li>For a <b>$100,000 house deposit in 5 years</b> you need $1,470 a month at 5%, or $1,667 with no interest.</li></ul>
<p class="note">All examples start from $0 saved and use this calculator's formula. 4% and 5% are example rates, not bank quotes. Interest is before tax.</p>
<h2 id="how">How the calculator works</h2>
<p>Example first. You want $30,000 in 3 years. You already have $3,000, and your account pays 4.5% a year. The $3,000 grows on its own to about $3,431. You still need about $26,569. Saving <b>$691 a month</b> gets you there, because interest on your deposits adds about $2,136 along the way.</p>
<p>The steps are:</p>
<ul><li><b>Monthly rate</b> = yearly rate ÷ 12. So 4.5% a year is 0.375% a month.</li>
<li><b>Compound interest</b> means you earn interest on your interest too. The calculator adds interest every month.</li>
<li><b>Gap</b> = goal − what your current savings will grow to.</li>
<li><b>Monthly deposit</b> = gap × i ÷ ((1 + i)<sup>n</sup> − 1), where i is the monthly rate and n is the number of months.</li></ul>
<p>With no interest it is simply: (goal − already saved) ÷ months. If your current savings already grow past the goal, you need $0 a month.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Pay yourself first.</b> Set up an automatic transfer on payday, so the money moves before you can spend it.</li>
<li><b>Split weekly or fortnightly.</b> The calculator shows about how much that is if you are paid weekly or fortnightly.</li>
<li><b>Check bonus-interest conditions.</b> Many accounts only pay the top rate if you deposit a set amount or make no withdrawals that month. Enter the rate you will really get.</li>
<li><b>Don't forget tax.</b> Interest is taxable, so your real return is lower than the rate shown.</li>
<li><b>Keep a buffer.</b> Saving for a goal works best when you also have money set aside for emergencies.</li>
<li><b>Rates change.</b> If the RBA cash rate moves, savings rates often follow. Re-run the numbers every few months.</li></ul>
'''+faq_block(FAQ)+'''
<p class="note">Sources (checked 23 November 2026): <a href="https://www.rba.gov.au/statistics/cash-rate/" rel="nofollow">Reserve Bank of Australia – Cash rate target</a>; <a href="https://www.apra.gov.au/about-financial-claims-scheme" rel="nofollow">APRA – Overview of the Financial Claims Scheme</a>; <a href="https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/income-you-must-declare/investment-income" rel="nofollow">ATO – Investment income</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents" rel="nofollow">ATO – Tax rates for Australian residents</a>; <a href="https://moneysmart.gov.au/saving" rel="nofollow">Moneysmart (ASIC) – Saving</a>. Examples use this calculator's own formula. General information only.</p>'''

out=build(P,'Savings Goal Calculator Australia 2026 – How Much to Save a Month',
 'See how much to save each month, fortnight or week to reach a savings goal or house deposit, with interest. Examples for $10k, $20k, $50k and $100k goals.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','23 November 2026'),('Sources','RBA, APRA, ATO, Moneysmart')],
 [('form','Calculator'),('figures','Official figures'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out, round(dflt,2), round(hd,2))
