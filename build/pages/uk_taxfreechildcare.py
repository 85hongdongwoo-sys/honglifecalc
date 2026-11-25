import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/uk/tax-free-childcare-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"£"}</style><label class="f"><span>Yearly childcare costs (all children)</span><div class="money"><input id="c" inputmode="decimal" value="9,000"></div><small>The full bill from your nursery, childminder, club or nanny for a year.</small></label><label class="f"><span>Children (under 12, or under 17 if disabled)</span><input id="k" inputmode="decimal" value="1"></label><label class="f"><span>Of which disabled</span><input id="dk" inputmode="decimal" value="0"><small>A child who gets Disability Living Allowance, PIP, Adult Disability Payment, Child Disability Payment, or is certified blind.</small></label></form>'''

calc='''function calc(){const k=Math.max(1,Math.floor(num('k'))),dk=Math.min(k,Math.max(0,Math.floor(num('dk')))),cap=2000*(k-dk)+4000*dk,c=num('c'),top=Math.min(c*.2,cap),pay=c-top;
 return big('Government top-up',gbp(top,0),'You pay '+gbp(pay,0)+' a year')+kv([['Your payments in',gbp(pay,0)],['Top-up (20%)',gbp(top,0),'pos'],['Top-up per month (average)',gbp(top/12,0)],['Maximum top-up for your children',gbp(cap,0)],['Childcare bill that uses the full top-up',gbp(cap*5,0)]])+(c*.2>cap?'<p class="note">Your bill is above the yearly limit, so you pay the rest yourself.</p>':'')+'<p class="note">Assumes costs are spread evenly across children and quarters. The limit is £500 per child every 3 months (£1,000 if disabled). Each parent must expect to earn at least the National Minimum or Living Wage for 16 hours a week over the next 3 months (£2,643.68 if you are 21 or over) and under £100,000 adjusted net income.</p>'}'''

def tfc(c,k=1,dk=0):
    cap=2000*(k-dk)+4000*dk; top=min(c*.2,cap); return top,c-top,cap
p=lambda x:f"£{x:,.0f}"
ex=[]
for c,k,dk,lab in [(3000,1,0,'1 child, after-school club'),(9000,1,0,'1 child, 3 days at nursery'),(15000,1,0,'1 child, full-time nursery'),(18000,2,0,'2 children'),(20000,1,1,'1 disabled child')]:
    t,pay,cap=tfc(c,k,dk); ex.append([lab,p(c),p(pay),p(t),p(cap)])
print(ex)
fig=[['Government top-up','£2 for every £8 you pay in','That is 20% of your childcare bill.'],
     ['Limit per child','£500 every 3 months (up to £2,000 a year)','You reach it when you pay in £8,000 a year (a £10,000 bill).'],
     ['Limit for a disabled child','£1,000 every 3 months (up to £4,000 a year)','You reach it at a £20,000 bill.'],
     ['Child age','11 or younger (16 or younger if disabled)',''],
     ['Minimum earnings, age 21+','£2,643.68 over the next 3 months','£203.36 a week. That is the National Living Wage (£12.71 an hour from April 2026) for 16 hours a week.'],
     ['Minimum earnings, age 18–20','£2,256.80 over the next 3 months','£173.60 a week, at the £10.85 minimum wage.'],
     ['Minimum earnings, under 18 or apprentice','£1,664 over the next 3 months','£128 a week, at the £8 minimum wage.'],
     ['Maximum income','£100,000 adjusted net income','If you or your partner expects to go over £100,000 this tax year, you can\'t get it.'],
     ['Reconfirm','Every 3 months','Sign in to your childcare account and confirm you are still eligible, or your Tax-Free Childcare stops.']]

FAQ=[
("How much does Tax-Free Childcare give?","For every £8 you pay in, the government adds £2. That is up to £2,000 a year for each child, or £4,000 for a disabled child. A £9,000 childcare bill gets £1,800 of top-up, so you pay £7,200."),
("How much do I need to pay in to get the full £2,000?","£8,000 a year per child. The government then adds £2,000, which covers a £10,000 childcare bill. The limit works every 3 months: pay in £2,000 and get £500."),
("Who can get Tax-Free Childcare?","Working parents of children aged 11 or under (16 or under if disabled). Each parent must expect to earn at least the minimum wage for 16 hours a week on average over the next 3 months: £2,643.68 if aged 21 or over, £2,256.80 at 18–20, or £1,664 under 18 or on an apprenticeship. Neither of you can expect adjusted net income over £100,000."),
("Can I get Tax-Free Childcare and 30 hours free childcare?","Yes. You can use both at the same time. The free hours lower your bill, and Tax-Free Childcare helps pay for the extra hours, meals or holiday clubs."),
("Can I get Tax-Free Childcare with Universal Credit?","No. If you claim Universal Credit or childcare vouchers you cannot have Tax-Free Childcare at the same time, so you must choose. Wait until you get the Tax-Free Childcare decision before you cancel Universal Credit."),
("What can I spend Tax-Free Childcare on?","Approved childcare only: registered nurseries, childminders, nannies, after-school clubs and holiday clubs. The provider must be signed up to receive Tax-Free Childcare payments. You can't use it for school fees."),
("Is the top-up paid straight away?","The government adds its 20% when you pay into your childcare account. You then pay the provider from that account. Unused money stays in the account, and you can take your own money out."),
("What if my income goes up and down?","If you are self-employed and don't expect to earn enough in the next 3 months, you can use an average of what you expect over the tax year. The same applies if you are paid irregularly. If you started your business less than 12 months ago, it doesn't matter how little you earn."),
]

art='''<h2 id="figures">Tax-Free Childcare rules in 2026/27</h2>
'''+table(['Rule','Figure','What it means'],fig)+'''
<h2 id="ex">How much will I get? Examples</h2>
<div id="examples">'''+table(['Family','Childcare bill a year','You pay','Government adds','Yearly limit'],ex)+'''</div>
<ul><li>An after-school club costing <b>£3,000 a year</b>: you pay £2,400 and the government adds <b>£600</b>.</li>
<li>Full-time nursery at <b>£15,000 a year</b>: the government adds the full <b>£2,000</b>. You pay £13,000 because 20% (£3,000) is over the limit.</li>
<li>Two children with <b>£18,000</b> of childcare: each child has its own £2,000 limit, so the top-up is <b>£3,600</b>.</li>
<li>A disabled child with a <b>£20,000</b> bill: the top-up is the full <b>£4,000</b>.</li></ul>
<p class="note">Examples use this calculator's formula and assume costs are spread evenly over the year.</p>
<h2 id="how">How it works, in plain words</h2>
<p>Say your nursery bill is £900 a month. You pay £720 into your online childcare account. The government adds £180. The account now has £900, and you pay the nursery from it. So you save <b>20%</b> on every bill, until you hit the limit.</p>
<ul><li><b>Top-up</b> = childcare bill × 20%. Another way to see it: your payment ÷ 4.</li>
<li><b>Limit</b> = £500 per child every 3 months (£1,000 for a disabled child), up to £2,000 a year (£4,000).</li>
<li><b>Adjusted net income</b> means your taxable income minus things like pension contributions and Gift Aid. If you or your partner expects to go over £100,000 (including foreign income), neither of you can use the scheme.</li>
<li><b>Minimum wage test</b>: each of you must expect to earn at least £2,643.68 over the next 3 months if aged 21 or over (£203.36 a week). It is less at younger ages. Someone who started a business under 12 months ago is exempt.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Set a reminder to reconfirm.</b> You must confirm your details every 3 months. If you forget, the top-ups stop until you do.</li>
<li><b>Spread payments across the quarters.</b> The limit is £500 every 3 months, so paying one huge amount in a single quarter can waste part of the top-up.</li>
<li><b>Check your provider is signed up.</b> Your nursery or club must be registered to accept Tax-Free Childcare.</li>
<li><b>Compare with Universal Credit.</b> You can't have both, so work out which pays you more before you switch. If you use childcare vouchers, tell your employer to stop them within 90 days of applying.</li>
<li><b>Near £100,000?</b> Extra pension contributions lower your adjusted net income and can keep you eligible.</li></ul>
<h2 id="faq" style="margin-top:22px">Tax-Free Childcare FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.gov.uk/tax-free-childcare" rel="nofollow">GOV.UK – Tax-Free Childcare</a>; <a href="https://www.gov.uk/tax-free-childcare/check-if-youre-eligible" rel="nofollow">GOV.UK – Check if you're eligible for Tax-Free Childcare</a>; <a href="https://www.gov.uk/national-minimum-wage-rates" rel="nofollow">GOV.UK – National Minimum Wage and National Living Wage rates</a>. Examples use this calculator's own formula. General information, not financial advice.</p>'''

out=build(P,'Tax-Free Childcare Calculator 2026/27 – £2 for Every £8, up to £2,000',
 'See how much Tax-Free Childcare adds to your childcare bill: 20%, up to £2,000 per child a year (£4,000 if disabled). 2026/27 earnings rules and worked examples.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','GOV.UK, HMRC')],
 [('form','Calculator'),('figures','2026/27 rules'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
