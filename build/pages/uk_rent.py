import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/uk/rent-affordability-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"£"}</style><label class="f"><span>Annual gross income (all tenants together)</span><div class="money"><input id="i" inputmode="decimal" value="40,000"></div><small>Before tax. Add up everyone who will be on the tenancy.</small></label><label class="f"><span>How many people earn that income?</span><select id="ne"><option value="1" selected>1</option><option value="2">2 (split equally)</option><option value="3">3 (split equally)</option></select></label><label class="f"><span>Rent you are looking at (£ a month, optional)</span><div class="money"><input id="rt" inputmode="decimal" value="1,000"></div></label></form>'''

calc='''function calc(){const i=num('i'),ne=Math.max(1,+($('ne')?$('ne').value:1)),rt=num('rt'),each=i/ne,net=ne*(each-itax(each).tax-ni(each)),mh=i*.3/12,r30=i/30,tk=net*.35/12;
 if(i<=0)return big('Rent you can afford','–','Enter your yearly income before tax');
 let h=big('Rent you can afford',gbp(mh,0)+' a month','30% of income before tax (MoneyHelper\\'s guide)')+kv([['Letting agent "30× rent" check',gbp(r30,0)+' max'],['35% of take-home pay',gbp(tk,0)],['Take-home pay a month (all earners)',gbp(net/12,0)]]);
 if(rt>0){const wk=rt*12/52,dep=rt*12<50000?5:6;h+=kv([['Rent you entered',gbp(rt,0)+' a month','t'],['Share of income before tax',Math.round(rt*12/i*100)+'%',rt*12/i>.3?'neg':'pos'],['Share of take-home pay',Math.round(rt*12/net*100)+'%'],['Income needed for the 30× check',gbp(rt*30,0)],['Income needed for the 30% guide',gbp(rt*40,0)],['Holding deposit (max 1 week)',gbp(wk,2)],['Tenancy deposit (max '+dep+' weeks)',gbp(wk*dep,2)],['Rent in advance (max 1 month)',gbp(rt,0)]]);
  if(rt*12>=100000)h+='<p class="note">The 5- and 6-week deposit caps only cover rents up to £100,000 a year.</p>'}
 return h+'<p class="note">Take-home uses 2026/27 income tax (England, Wales and Northern Ireland bands) and employee National Insurance, with income split equally between earners. Deposit and rent-in-advance limits are the rules for private renting in England.</p>'}'''

def pa(a): return max(0,12570-max(0,a-100000)/2)
def it(x):
    p=pa(x);t=max(0,x-p);b=min(t,37700);h=min(max(0,t-37700),125140-37700-(12570-p));a=max(0,t-b-h);return b*.2+h*.4+a*.45
def ni(e): return max(0,min(e,50270)-12570)*.08+max(0,e-50270)*.02
def net(i,ne): e=i/ne; return ne*(e-it(e)-ni(e))
g=lambda x:f"£{x:,.0f}"
rows=[]
for i,ne,lab in [(25000,1,'£25,000 (1 earner)'),(30000,1,'£30,000 (1 earner)'),(40000,1,'£40,000 (1 earner)'),(60000,1,'£60,000 (1 earner)'),(60000,2,'£60,000 (2 earners, £30,000 each)')]:
    rows.append([lab,g(net(i,ne)/12),g(i*.3/12),g(i/30),g(net(i,ne)*.35/12)])
up=[]
for r in (800,1000,1411,2350):
    wk=r*12/52
    up.append([g(r),f"£{wk:,.2f}",f"£{wk*5:,.2f}",g(r),f"£{wk*5+r:,.2f}",g(r*30),g(r*40)])
print(rows);print(up)

FAQ=[
("How much rent can I afford on £30,000?","MoneyHelper's 30% guide gives £750 a month (30% of £30,000 ÷ 12). A letting agent's 30× check allows up to £1,000. After 2026/27 tax and National Insurance you take home about £2,093 a month, and 35% of that is £733."),
("What is the 30% rule for rent?","MoneyHelper, the government-backed money guidance service, describes the 30% rule: spend up to 30% of your income before tax on rent. It says the rule is just a guide and keeping to 30% isn't always possible."),
("What does '30 times the rent' mean?","Many letting agents check that your yearly income is at least 30 times the monthly rent. For £1,000 a month you would need £30,000 a year. This is an agent practice, not a law, and agents can use different multiples or ask for a guarantor."),
("How much deposit can a landlord ask for in England?","Up to 5 weeks' rent if the yearly rent is under £50,000, or 6 weeks' rent if it is between £50,000 and £100,000. For £1,000 a month that is £1,153.85. A holding deposit can be up to 1 week's rent (£230.77)."),
("Can a landlord ask for 6 months' rent in advance?","Not in England since 1 May 2026. Under the Renters' Rights Act, a landlord can't ask for or accept rent before you sign the tenancy agreement, and after signing can ask for at most 1 month's rent in advance."),
("How often can my rent go up?","In England, from 1 May 2026, only once a year and not in the first 12 months of a new tenancy. The landlord must use Form 4A and give at least 2 months' notice. You can challenge an increase above the market rent."),
]

art='''<h2 id="figures">Official rules and figures for renters (England, 2026)</h2>
'''+table(['Item','Figure','What it means'],[
['MoneyHelper rent guide','Up to 30% of income before tax','A guide, not a rule. MoneyHelper says keeping to 30% isn\'t always possible.'],
['Tenancy deposit cap','5 weeks\' rent (yearly rent under £50,000) · 6 weeks\' (£50,000–£100,000)','Tenant Fees Act 2019.'],
['Holding deposit cap','1 week\'s rent','Paid to reserve a home while checks are done.'],
['Rent in advance','Max 1 month, and only after signing','Renters\' Rights Act, from 1 May 2026.'],
['Rent increases','Once a year, not in the first 12 months, 2 months\' notice (Form 4A)','You can challenge a rise above market rent.'],
['Rental bidding','Banned','Landlords must show a price and can\'t accept offers above it.'],
['Benefits or children','Landlords can\'t refuse you for this','Renters\' Rights Act protection.'],
['Average private rent (October 2026)','UK £1,411 · England £1,472 · London £2,350 · Wales £849 · Scotland £1,015 a month','ONS, provisional. UK rents rose 3.8% in a year.']])+'''
<h2 id="ex">How much rent can I afford? Examples</h2>
<div id="examples">'''+table(['Yearly income','Take-home a month','30% of gross (MoneyHelper)','30× agent check (max)','35% of take-home'],rows)+'''</div>
<p class="note">Take-home is after 2026/27 income tax and employee National Insurance (England, Wales and NI bands), with no pension or student loan. Two earners pay less tax than one person on the same total, so they take home more.</p>
<h3>Money you need upfront</h3>
'''+table(['Monthly rent','Holding deposit (1 week)','Tenancy deposit (5 weeks)','First month\'s rent','Deposit + first month','Income for 30× check','Income for 30% guide'],up)+'''
<p class="note">One week's rent = monthly rent × 12 ÷ 52. The holding deposit is not added to the total. £1,411 and £2,350 are the ONS average rents for the UK and London.</p>
<h2 id="how">How the calculator works</h2>
<p>Example first. You earn £40,000 a year.</p>
<ul><li><b>30% guide:</b> £40,000 × 30% ÷ 12 = <b>£1,000 a month</b>.</li>
<li><b>Agent 30× check:</b> £40,000 ÷ 30 = £1,333 a month at most.</li>
<li><b>35% of take-home:</b> you take home about £2,693 a month, and 35% of that is £943.</li></ul>
<p><b>Gross income</b> means pay before tax. <b>Take-home pay</b> is what reaches your bank after income tax and National Insurance. The 30× check is what many agents use to pass you; the 30% guide and the take-home figure are better for checking you can really live on what's left.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Count bills too.</b> Council tax, energy, water and broadband can add hundreds a month on top of rent.</li>
<li><b>Use everyone's income.</b> On a joint tenancy, add up all tenants' incomes in the calculator.</li>
<li><b>Don't pay before you sign.</b> In England a landlord can't take rent before the tenancy agreement is signed.</li>
<li><b>In Scotland or Wales</b> the renting rules and tax bands are different.</li></ul>
<h2 id="faq" style="margin-top:22px">Rent affordability FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 24 November 2026): <a href="https://www.moneyhelper.org.uk/en/homes/renting/how-much-rent-can-you-afford" rel="nofollow">MoneyHelper – How much rent can you afford?</a>; <a href="https://www.gov.uk/guidance/tenant-fees-act-2019-guidance-for-tenants" rel="nofollow">GOV.UK – Tenant Fees Act 2019: guidance for tenants</a>; <a href="https://www.gov.uk/guidance/renters-rights-act-overview-for-tenants" rel="nofollow">GOV.UK – Renters' Rights Act: overview for tenants</a>; <a href="https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/privaterentandhousepricesuk/november2026" rel="nofollow">ONS – Private rent and house prices, UK: November 2026</a>; <a href="https://www.gov.uk/income-tax-rates" rel="nofollow">GOV.UK – Income Tax rates</a>; <a href="https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027" rel="nofollow">GOV.UK – Rates and thresholds 2026 to 2027</a>. The 30× check is a common letting-agent practice, not a law. Not financial or legal advice.</p>'''

out=build(P,'How Much Rent Can I Afford? UK Rent Calculator 2026 (30% Rule)',
 'Check how much rent you can afford in the UK: MoneyHelper 30% guide, the agent 30× check and take-home pay. Deposit caps, rent in advance and 2026 renting rules.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','24 November 2026'),('Sources','MoneyHelper, GOV.UK, ONS')],
 [('form','Calculator'),('figures','Rules and figures'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
