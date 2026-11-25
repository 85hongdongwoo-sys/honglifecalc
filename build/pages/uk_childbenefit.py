import sys,math; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/uk/child-benefit-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"£"}</style><label class="f"><span>Number of children</span><input id="k" inputmode="decimal" value="2"></label><label class="f"><span>Higher earner’s adjusted net income</span><div class="money"><input id="ani" inputmode="decimal" value="68,000"></div><small>Taxable income for the year (salary, self-employed profit, rent, interest) after pension contributions taken by your employer before tax.</small></label><label class="f"><span>Extra pension contributions or Gift Aid (gross)</span><div class="money"><input id="pen" inputmode="decimal" value="0"></div><small>Gross means including the 20% tax relief: paying £800 into a personal pension counts as £1,000.</small></label></form>'''

calc='''function calc(){const k=Math.max(0,Math.floor(num('k')));if(!k)return big('Child Benefit',gbp(0),'');const wk=27.05+17.90*(k-1),cb=wk*52,ani=Math.max(0,num('ani')-num('pen')),pct=Math.min(1,Math.floor(Math.max(0,ani-60000)/200)/100),ch=Math.floor(cb*pct);
 return big('Child Benefit you keep',gbp(cb-ch,0),'per year')+kv([['Weekly Child Benefit',gbp(wk,2)],['Per month (average)',gbp(wk*52/12,0)],['Child Benefit (52 weeks)',gbp(cb,0)],['Adjusted net income used',gbp(ani,0)],['Charge rate',(pct*100).toFixed(0)+'%'],['High Income Child Benefit Charge',gbp(-ch,0),'neg'],['Net benefit',gbp(cb-ch,0),'t']])+(pct>=1?'<p class="note">Over £80,000 you pay it all back. It is still worth being registered: you can choose not to receive the payments, which means no charge, and you keep the National Insurance credits that count towards your State Pension.</p>':(pct>0?'<p class="note">The charge goes up by 1% for every £200 over £60,000. Each £200 you add to a pension saves 1% of the benefit.</p>':''))}'''

W1,W2=27.05,17.90
def keep(k,ani):
    cb=(W1+W2*(k-1))*52; pct=min(1,math.floor(max(0,ani-60000)/200)/100); ch=math.floor(cb*pct); return cb,pct,ch,cb-ch
p=lambda x:f"£{x:,.0f}"
rates=[]
for k in (1,2,3,4):
    wk=W1+W2*(k-1); rates.append([str(k),f"£{wk:.2f}",p(wk*52/12),p(wk*52)])
ex=[]
for k,ani in [(2,55000),(2,65000),(2,70000),(1,75000),(3,79000),(2,85000)]:
    cb,pct,ch,net=keep(k,ani); ex.append([str(k),p(ani),p(cb),f"{pct*100:.0f}%",p(ch),p(net)])
print(rates,ex,keep(2,68000))

fig=[['Eldest or only child','£27.05 a week','Up from £26.05 in 2025/26. Rises to £28.00 in 2027/28.'],
     ['Each extra child','£17.90 a week','Up from £17.25 in 2025/26. Rises to £18.55 in 2027/28. No limit on the number of children.'],
     ['Charge starts','£60,000 adjusted net income','The threshold has been £60,000 since the 2024/25 tax year.'],
     ['Who pays the charge','The partner with the higher income','Even if the other partner makes the claim.'],
     ['Charge rate','1% of the benefit for every £200 over £60,000','At £70,000 you pay back 50%.'],
     ['Benefit fully paid back','£80,000 or more','Over £80,000 you pay all of it back.'],
     ['How the charge is paid','Through your tax code (PAYE) or Self Assessment','Self Assessment is needed if you already file a return, or if you pay after 31 January following the tax year.']]

FAQ=[
("How much is Child Benefit in 2026/27?","£27.05 a week for the eldest or only child and £17.90 a week for each other child, from 6 April 2026. For one child that is £1,407 a year; for two children £2,337 a year."),
("How much Child Benefit do you get for 2 children?","£44.95 a week (£27.05 + £17.90). Over a year that is £2,337, or about £195 a month."),
("At what income do you lose Child Benefit?","You start paying it back when the higher earner's adjusted net income is over £60,000. The charge is 1% for every £200 above that, so at £80,000 or more all of it is paid back."),
("How much High Income Child Benefit Charge will I pay on £70,000?","At £70,000 the charge is 50%. With two children you get £2,337 and pay back £1,168, so you keep £1,169. With one child you keep £704."),
("Can paying into a pension stop the Child Benefit charge?","Yes. Pension contributions and Gift Aid lower your adjusted net income. Someone on £70,000 with two children who adds £10,000 (gross) to a pension drops to £60,000 and keeps all £2,337."),
("Should I still claim Child Benefit if I earn over £80,000?","Usually yes. You can stay registered but choose not to receive the payments. Then you pay no charge, and you still get the National Insurance credits that count towards your State Pension, plus a National Insurance number for your child."),
("Is Child Benefit going up in 2027?","Yes. Budget 2026 set the 2027/28 rates at £28.00 a week for the eldest child and £18.55 for each other child, from April 2027. For two children that is £2,420 a year."),
("Does the charge use household income?","No. It looks at each person's own adjusted net income. Only the partner with the higher income pays the charge, even if the other partner claims the benefit."),
]

art='''<h2 id="figures">Child Benefit and the charge in 2026/27</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<h3>Child Benefit by number of children (2026/27)</h3>
'''+table(['Children','Per week','Per month (average)','Per year (52 weeks)'],rates)+'''
<h2 id="ex">How much do I keep? Examples</h2>
<div id="examples">'''+table(['Children','Higher earner\'s income','Child Benefit a year','Charge rate','Charge paid back','You keep'],ex)+'''</div>
<ul><li>On <b>£55,000</b> there is no charge. Two children get the full £2,337.</li>
<li>On <b>£65,000</b> the charge is 25%. Two children: pay back £584, keep £1,753.</li>
<li>On <b>£79,000</b> the charge is 95%. Three children get £3,268 but keep only £164.</li>
<li>On <b>£85,000</b> the charge is 100%. Everything is paid back.</li></ul>
<p class="note">Examples use this calculator's formula: 52 weeks of benefit, charge rounded down to a whole percent and a whole pound.</p>
<h2 id="how">How it works, in plain words</h2>
<p>Example first. You have two children and earn £68,000. Child Benefit is £44.95 a week, or £2,337 a year. You are £8,000 over £60,000. £8,000 ÷ £200 = 40, so the charge is <b>40%</b>: £934. You keep about <b>£1,403</b>.</p>
<ul><li><b>Adjusted net income</b> is worked out before any Personal Allowance and after certain tax reliefs, such as pension contributions and Gift Aid (use the gross amounts).</li>
<li><b>High Income Child Benefit Charge</b> is an extra tax the higher earner pays to give back some or all of the benefit.</li>
<li><b>Charge %</b> = (income − £60,000) ÷ £200, rounded down, up to 100%.</li>
<li><b>Charge</b> = yearly Child Benefit × charge %.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Always claim for a new baby.</b> Even if you won't keep the money, the claim protects the stay-at-home parent's State Pension record.</li>
<li><b>Tell HMRC if you go over £60,000.</b> The higher earner pays the charge through their tax code (PAYE) or through Self Assessment. Self Assessment is needed if you already file a return, or if you pay later than 31 January after the tax year.</li>
<li><b>Use pension contributions.</b> Between £60,000 and £80,000, every £200 into a pension saves 1% of the benefit on top of normal tax relief.</li>
<li><b>Count all income.</b> Bonuses, rental profit and savings interest all count towards adjusted net income.</li>
<li><b>Earning over £80,000?</b> Don't just stop the claim. Stay registered and opt out of the payments instead, so you keep the National Insurance credits.</li></ul>
<h2 id="faq" style="margin-top:22px">Child Benefit FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.gov.uk/child-benefit/what-youll-get" rel="nofollow">GOV.UK – Child Benefit: what you'll get</a>; <a href="https://www.gov.uk/child-benefit-tax-charge" rel="nofollow">GOV.UK – High Income Child Benefit Charge</a>; HM Treasury – Budget 2026, Annex A (updated 5 November 2026) for the 2027/28 rates. Examples use this calculator's own formula. General information, not tax advice.</p>'''

out=build(P,'Child Benefit Calculator 2026/27 – £27.05 a Week and the £60k Charge',
 'Child Benefit 2026/27: £27.05 a week for the eldest child, £17.90 for others, and how much the High Income Charge takes between £60,000 and £80,000.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','GOV.UK, HM Treasury')],
 [('form','Calculator'),('figures','2026/27 rates'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
