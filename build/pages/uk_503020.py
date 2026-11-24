import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/uk/50-30-20-budget-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Monthly take-home pay (£)</span><input id="inc" inputmode="decimal" value="3,200"><small>What lands in your bank account after tax, National Insurance and pension. Not sure? Use the <a href="/uk/take-home-pay-calculator.html">take-home pay calculator</a>.</small></label><label class="f"><span>What your needs cost now (£ a month, optional)</span><input id="nd" inputmode="decimal" value=""><small>Rent or mortgage, council tax, energy, water, food, travel to work, insurance, minimum debt payments.</small></label></form>'''

calc='''function calc(){const x=num('inc'),nd=num('nd');if(x<=0)return big(O.s,'–','Enter your monthly take-home pay');
 let h=big(O.s,mf(x*.2),'20% a month')+kv([[O.n+' (50%)',mf(x*.5)],[O.w+' (30%)',mf(x*.3)],[O.s+' (20%)',mf(x*.2),'pos'],[O.yr,mf(x*.2*12)]]);
 if(nd>0){const p=nd/x,left=x-nd;h+=kv([['Your needs now',mf(nd)+' ('+Math.round(p*100)+'% of pay)',p>.5?'neg':'pos'],[p>.5?'Over the 50% guide by':'Under the 50% guide by',mf(Math.abs(nd-x*.5))],['Left for wants and savings',mf(left)],['20% savings would leave for wants',mf(Math.max(0,left-x*.2))]]);
  if(p>.5)h+='<p class="note">Your needs take more than half your pay. That is common with high rents. Try to keep saving something – even 10% – and trim wants first.</p>'}
 return h+'<p class="note">50/30/20 is a rule of thumb, not an official rule. Adjust the split to your life.</p>'}'''

def pa(a): return max(0,12570-max(0,a-100000)/2)
def it(x):
    p=pa(x);t=max(0,x-p);b=min(t,37700);h=min(max(0,t-37700),125140-37700-(12570-p));a=max(0,t-b-h);return b*.2+h*.4+a*.45
def ni(e): return max(0,min(e,50270)-12570)*.08+max(0,e-50270)*.02
g=lambda x:f"£{x:,.0f}"
rows=[]
for s in (25000,30000,35000,45000,60000):
    n=(s-it(s)-ni(s))/12
    rows.append([g(s),g(n),g(n*.5),g(n*.3),g(n*.2),g(n*.2*12)])
d=3200
print(rows)

FAQ=[
("What is the 50/30/20 rule?","It splits your take-home pay into three parts: 50% for needs, 30% for wants and 20% for savings and paying off debt. On £3,200 a month that is £1,600 for needs, £960 for wants and £640 for savings."),
("How do I use 50/30/20 on a £30,000 salary?","In 2026/27 a £30,000 salary in England, Wales or Northern Ireland gives about £2,093 a month after income tax and National Insurance (no pension or student loan). That splits into £1,047 for needs, £628 for wants and £419 for savings – about £5,024 a year."),
("What counts as a need and what is a want?","A need is something you must pay even in a bad month: rent or mortgage, council tax, energy, water, basic food, getting to work, insurance and minimum debt payments. A want is something you could cut: takeaways, holidays, streaming, new clothes you don't need, gym upgrades."),
("Is 50/30/20 realistic with UK rents?","Often not. The ONS says average private rent was £1,411 a month in the UK and £2,350 in London in October 2026. On £2,093 take-home, average UK rent alone is 67% of pay. Many people use 60/20/20 or 70/20/10 instead – the key is to save something every month."),
("Does the 20% include pension?","Workplace pension is usually taken off before your take-home pay, so it's already counted. The 20% is extra: emergency fund, savings goals, and overpaying debt like credit cards."),
("Should I save or pay off debt first?","Pay at least the minimum on every debt (that's a need). Then many people build a small emergency fund first, then put the 20% towards the most expensive debt, such as credit cards, before saving more."),
]

art='''<h2 id="figures">Official figures that affect your budget</h2>
'''+table(['Item','Figure (2026/27)','Why it matters'],[
['Personal Allowance','£12,570','Income you can earn each year before income tax.'],
['Income tax (England, Wales, NI)','20% to £50,270 · 40% to £125,140 · 45% above','Taken from your pay before it reaches you.'],
['Employee National Insurance','8% from £12,570 to £50,270 · 2% above','Also taken before your take-home pay.'],
['Average private rent (October 2026)','UK £1,411 · England £1,472 · London £2,350 a month','Rent is usually the biggest "need". ONS figures are provisional.'],
['Bank of England Bank Rate','4% (from 5 November 2026)','Affects savings rates and mortgage rates.'],
['FSCS protection','£120,000 per person, per authorised firm','Your savings are protected up to this amount if a bank fails.']])+'''
<h2 id="ex">50/30/20 on common UK salaries (2026/27)</h2>
<div id="examples">'''+table(['Salary a year','Take-home a month','Needs 50%','Wants 30%','Savings 20%','Saved in a year'],rows)+'''</div>
<p class="note">Take-home is after 2026/27 income tax and employee National Insurance for England, Wales and Northern Ireland, with no pension, student loan or other deductions. Scotland has different income tax bands. Splits use this page's formula.</p>
<h2 id="how">How the 50/30/20 split works</h2>
<p>Example first. Your take-home pay is £3,200 a month.</p>
<ul><li><b>Needs: £3,200 × 50% = £1,600.</b> Rent, bills, food, travel to work, minimum debt payments.</li>
<li><b>Wants: £3,200 × 30% = £960.</b> Eating out, hobbies, subscriptions, holidays.</li>
<li><b>Savings and debt: £3,200 × 20% = £640.</b> That is £7,680 in a year.</li></ul>
<p><b>Take-home pay</b> means the money that arrives in your account after tax, National Insurance and pension. Always start from that number, not your salary.</p>
<p>If you enter what your needs cost now, the calculator shows how far you are from the 50% guide and what is left for wants once you save 20%.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Using your salary instead of take-home pay.</b> The split only works on money you actually receive.</li>
<li><b>Hiding wants inside needs.</b> A basic phone plan is a need; the newest phone on contract is partly a want.</li>
<li><b>Forgetting yearly bills.</b> Car insurance, TV licence and birthdays: divide by 12 and add them to your monthly budget.</li>
<li><b>Giving up when needs are over 50%.</b> Change the split instead – 60/30/10 still gets you saving.</li>
<li><b>Saving what's left at the end of the month.</b> Move the 20% on payday with a standing order.</li></ul>
<h2 id="faq" style="margin-top:22px">50/30/20 budget FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 24 November 2026): <a href="https://www.gov.uk/income-tax-rates" rel="nofollow">GOV.UK – Income Tax rates and Personal Allowances</a>; <a href="https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027" rel="nofollow">GOV.UK – Rates and thresholds for employers 2026 to 2027</a>; <a href="https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/privaterentandhousepricesuk/november2026" rel="nofollow">ONS – Private rent and house prices, UK: November 2026</a>; <a href="https://www.bankofengland.co.uk/monetary-policy/the-interest-rate-bank-rate" rel="nofollow">Bank of England – Bank Rate</a>; <a href="https://www.fscs.org.uk/what-we-cover/banks-building-societies-credit-unions/deposit-limit/" rel="nofollow">FSCS – deposit limit</a>. The 50/30/20 rule is a common budgeting guide, not an official rule. Not financial advice.</p>'''

out=build(P,'50/30/20 Budget Calculator UK 2026 – Split Your Take-Home Pay',
 'Split your monthly take-home pay into needs, wants and savings with the 50/30/20 rule. 2026/27 UK salary examples, average rents and what to do if needs are over 50%.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','24 November 2026'),('Sources','GOV.UK, HMRC, ONS, Bank of England')],
 [('form','Calculator'),('figures','Official figures'),('ex','Salary examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
