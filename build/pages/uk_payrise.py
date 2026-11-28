import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/uk/pay-rise-calculator.html'
CPI=3.6  # ONS CPI, 12 months to October 2026 (released 18 November 2026)

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Current salary (per year, before tax)</span><div class="money"><input id="s" inputmode="decimal" value="45,000"></div></label><label class="f"><span>Pay rise (%)</span><input id="p" inputmode="decimal" value="5"></label><label class="f"><span>Where you live</span><select id="rg"><option value="e" selected>England, Wales or Northern Ireland</option><option value="s">Scotland</option></select></label><label class="f"><span>Student loan</span><select id="sl"><option value="0">None</option><option value="26900">Plan 1</option><option value="29385" selected>Plan 2</option><option value="33795">Plan 4</option><option value="25000">Plan 5</option></select></label><label class="f"><span>Inflation to compare with (%)</span><input id="cpi" inputmode="decimal" value="3.6"><small>3.6% = CPI for the 12 months to October 2026 (ONS).</small></label></form>'''

calc='''function itx(x,sc){const p=pa(x),t=Math.max(0,x-p),B=sc?[[3967,.19],[16956,.2],[31092,.21],[62430,.42],[125140,.45],[1e18,.48]]:[[37700,.2],[125140,.4],[1e18,.45]];let tax=0,lo=0;for(const [hi,r] of B){tax+=Math.max(0,Math.min(t,hi)-lo)*r;lo=hi}return tax}
function nt(x){const sl=+$('sl').value,sc=$('rg').value==='s';return x-itx(x,sc)-ni(x)-(sl?Math.max(0,x-sl)*.09:0)}
function calc(){const s=num('s'),p=num('p'),n=s*(1+p/100),g=n-s,d=nt(n)-nt(s),c=num('cpi')/100;
 if(s<=0||g<=0)return big('Extra take-home','—','Enter your salary and a pay rise above 0%');
 const a=nt(s),tp=a>0?d/a:0,real=(1+tp)/(1+c)-1;
 const rows=[['New salary',gbp(n,0)],['Gross rise',gbp(g,0)+' a year · '+gbp(g/12,0)+' a month'],['Taken in tax, NI, loan',gbp(g-d,0)+' ('+pc((g-d)/g,0)+')','neg'],['Extra in your pocket',gbp(d,0)+' a year · '+gbp(d/12,0)+' a month','t'],['Take-home pay before → after',gbp(a,0)+' → '+gbp(a+d,0)+' (+'+pc(tp,1)+')'],['Real change after '+pc(c,1)+' inflation',(real>=0?'+':'')+pc(real,1)+(real<0?' · prices rose faster':' · ahead of prices'),real<0?'neg':'pos']];
 const trap=(n>100000&&s<125140)?'<p class="note">Part of this rise is between £100,000 and £125,140, where the personal allowance is taken away. You lose about 60% in income tax there, plus 2% NI.</p>':'';
 return big('Extra take-home',gbp(d,0)+' a year',gbp(d/12,0)+' a month · you keep '+pc(d/g,0)+' of the rise')+kv(rows)+trap+'<p class="note">2026/27 rates (6 April 2026 – 5 April 2027), PAYE employee, NI category A, tax code 1257L. Pension contributions, benefits in kind and the postgraduate loan are not included.</p>'}'''

def pa(x): return max(0,12570-max(0,x-100000)/2)
RUK=[(37700,.2),(125140,.4),(1e18,.45)]
SCO=[(3967,.19),(16956,.2),(31092,.21),(62430,.42),(125140,.45),(1e18,.48)]
def itax(x,sc=False):
    t=max(0,x-pa(x));tax=0;lo=0
    for hi,r in (SCO if sc else RUK):
        tax+=max(0,min(t,hi)-lo)*r;lo=hi
    return tax
def ni(e): return max(0,min(e,50270)-12570)*.08+max(0,e-50270)*.02
def net(x,sl=0,sc=False): return x-itax(x,sc)-ni(x)-(max(0,x-sl)*.09 if sl else 0)
def rise(s,p,sl=0,sc=False):
    n=s*(1+p/100);return n-s,net(n,sl,sc)-net(s,sl,sc)
g=lambda x:f"£{x:,.0f}"
pcs=lambda x:f"{x*100:.0f}%"

rows=[]
for s in (25000,35000,45000,60000,105000):
    g3,d3=rise(s,3);g5,d5=rise(s,5);gs,ds=rise(s,5,0,True);gl,dl=rise(s,5,29385)
    rows.append([g(s),f"{g(g3)} → {g(d3)} ({pcs(d3/g3)})",f"{g(g5)} → {g(d5)} ({pcs(d5/g5)})",f"{g(dl)} ({pcs(dl/gl)})",f"{g(ds)} ({pcs(ds/gs)})"])
for r in rows: print(r)
dflt=rise(45000,5,29385)
print('default',dflt)

# inflation examples (England, no loan)
inf=[]
for s,p in ((30000,3),(30000,5),(45000,3.6),(60000,6)):
    gg,d=rise(s,p);a=net(s);tp=d/a;real=(1+tp)/(1+CPI/100)-1
    inf.append([g(s),f"{p:g}%",g(d),f"+{tp*100:.1f}%",f"{'+' if real>=0 else ''}{real*100:.1f}%"])
for r in inf: print(r)

fig=[['Personal allowance','£12,570','Income you can earn each year with no income tax. It shrinks by £1 for every £2 you earn over £100,000, and is gone at £125,140.'],
     ['Income tax (England, Wales, NI)','20% basic · 40% higher · 45% additional','Basic rate on the first £37,700 above the allowance (up to £50,270 salary). 40% up to £125,140. 45% above.'],
     ['Income tax (Scotland)','19% · 20% · 21% · 42% · 45% · 48%','Six bands on income above the allowance: £3,967, £16,956, £31,092, £62,430 and £125,140 are the band tops. 42% starts at a £43,663 salary.'],
     ['National Insurance (employee, category A)','8% · 2%','8% on pay between £12,570 and £50,270 a year, 2% on pay above £50,270. Same in all four nations.'],
     ['Student loan repayments','9% above the threshold','Plan 1: £26,900 · Plan 2: £29,385 · Plan 4: £33,795 · Plan 5: £25,000. Postgraduate loan: 6% above £21,000.'],
     ['National Living Wage (21+)','£12.71 an hour','From 1 April 2026. It rises to £13.21 an hour from April 2027.'],
     ['CPI inflation','3.6%','Prices rose 3.6% in the 12 months to October 2026 (ONS, published 18 November 2026). September 2026: 3.5%.']]

marg=[['£12,570 – £50,270 (no loan)','20%','8%','—','72%'],
      ['£29,385 – £50,270 (Plan 2 loan)','20%','8%','9%','63%'],
      ['£50,270 – £100,000 (no loan)','40%','2%','—','58%'],
      ['£50,270 – £100,000 (Plan 2 loan)','40%','2%','9%','49%'],
      ['£100,000 – £125,140','60% (40% + lost allowance)','2%','—','38%'],
      ['Over £125,140','45%','2%','—','53%']]

FAQ=[
("How much is a 5% pay rise after tax on £45,000?","A 5% rise is £2,250 a year before tax. In England with no student loan you keep £1,620 a year (£135 a month), which is 72%. With a Plan 2 student loan you keep £1,418 (63%). In Scotland with no loan you keep £1,125 (50%), because the 42% rate starts at £43,663."),
("How much is a 3% pay rise after tax?","On £30,000 a 3% rise is £900 a year. You keep £648 (£54 a month) in England, Wales or Northern Ireland with no student loan. On £60,000 a 3% rise is £1,800 and you keep £1,044, because higher-rate tax is 40%."),
("Is my pay rise above inflation?","Compare the rise in your take-home pay with CPI inflation, which was 3.6% for the 12 months to October 2026. Example: £30,000 with a 3% rise gives take-home pay about 2.6% higher, so in real terms you are about 1.0% worse off. A 5% rise gives about 4.3% more take-home pay, about 0.7% ahead of prices."),
("Why do I keep less of a rise than my tax band suggests?","Because NI and student loan come out too. On £30,000 with a Plan 2 loan, each extra £100 loses £20 tax, £8 NI and £9 loan, so you keep £63. Your tax band only tells you the income tax part."),
("What is the 60% tax trap?","Between £100,000 and £125,140 you lose £1 of personal allowance for every £2 you earn. So each extra £100 costs £40 tax plus £20 tax on the lost allowance, plus £2 NI. You keep about £38. Paying more into a pension can bring your income back under £100,000."),
("Will a pay rise move me into a higher tax band?","Only the part of your salary above the line is taxed at the higher rate. If a rise takes you from £49,000 to £52,000, only the £1,730 above £50,270 is taxed at 40%. You never take home less in total because of a rise, except when you lose a benefit such as Child Benefit or free childcare."),
]

art='''<h2 id="figures">2026/27 tax, NI and pay figures</h2>
<p>These are the official figures for the 2026/27 tax year (6 April 2026 to 5 April 2027). The calculator uses all of them except the National Living Wage.</p>
'''+table(['Item','Figure','What it means'],fig)+'''
<h2 id="ex">How much of a pay rise you keep: examples</h2>
<p>Each cell shows the gross rise per year → what you keep after tax, NI and student loan, and the share you keep.</p>
<div id="examples">'''+table(['Salary','3% rise (England, no loan)','5% rise (England, no loan)','5% rise, Plan 2 loan','5% rise, Scotland, no loan'],rows)+'''</div>
<ul><li><b>The calculator's starting example:</b> £45,000 with a 5% rise and a Plan 2 loan. The rise is £2,250. You keep about £1,418 a year, or £118 a month.</li>
<li><b>£105,000 with a 5% rise</b> keeps only 38% (£1,995 of £5,250), because the whole rise falls in the £100,000 – £125,140 trap.</li></ul>
<h3 id="inflation">Pay rise vs inflation</h3>
<p>“Real terms” means after taking rising prices into account. If your take-home pay rises by less than prices, you can buy less than before. Examples for England with no student loan, using CPI of 3.6%:</p>
'''+table(['Salary','Pay rise','Extra take-home a year','Take-home pay rises by','Real change after 3.6% inflation'],inf)+'''
<p class="note">Your take-home pay grows a little slower than your gross pay when you pay tax on it, because the allowance stays at £12,570. So a 3.6% gross rise is still a small real-terms cut.</p>
<h2 id="how">How the calculator works</h2>
<p>It works out your take-home pay twice – on your old salary and on your new salary – and shows the difference.</p>
<ul><li><b>Take-home pay</b> = salary − income tax − National Insurance − student loan.</li>
<li><b>Income tax</b>: tax on salary above your personal allowance, band by band.</li>
<li><b>National Insurance (NI)</b>: a separate deduction that pays for the State Pension and some benefits.</li>
<li><b>Student loan</b>: 9% of everything above your plan's threshold.</li>
<li><b>Real change</b> = (1 + take-home rise) ÷ (1 + inflation) − 1.</li></ul>
<p>The share of each extra £1 you lose is called your <b>marginal rate</b>. This decides how much of a rise you keep:</p>
'''+table(['Salary range (England, Wales, NI)','Income tax','NI','Plan 2 loan','You keep of each extra £1'],marg)+'''
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Ask for the rise as a percentage and a figure.</b> 4% of £35,000 is £1,400 before tax, about £1,008 after tax and NI.</li>
<li><b>Check your tax code on your next payslip.</b> 1257L is the usual code. A wrong code can make a rise look smaller or bigger for a few months.</li>
<li><b>Near £50,270 or £100,000?</b> Paying some of the rise into your pension can save 40% or 60% tax.</li>
<li><b>A one-off bonus is taxed the same way.</b> It goes through PAYE like normal pay. See the <a href="/uk/bonus-tax-calculator.html">bonus tax calculator</a>.</li>
<li><b>Scotland is different.</b> If your main home is in Scotland, choose Scotland in the calculator. The 42% band starts at £43,663, so mid-salary rises keep less.</li></ul>
<h2 id="faq" style="margin-top:22px">Pay rise FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 28 November 2026): <a href="https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027" rel="nofollow">GOV.UK – Rates and thresholds for employers 2026 to 2027</a> (income tax incl. Scotland, NI, student loans); <a href="https://www.gov.uk/government/publications/budget-2026-overview-of-tax-legislation-and-rates-ootlar/annex-a-rates-and-allowances" rel="nofollow">HM Treasury – Budget 2026, Annex A rates and allowances</a>; <a href="https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/october2026" rel="nofollow">ONS – Consumer price inflation, UK: October 2026</a>; <a href="https://www.gov.uk/national-minimum-wage-rates" rel="nofollow">GOV.UK – National Minimum Wage and National Living Wage rates</a>. Estimates only – not tax advice.</p>'''

out=build(P,'Pay Rise Calculator UK 2026/27 – How Much Will I Take Home?',
 'How much of a 3% or 5% pay rise do you keep after tax, NI and student loan in 2026/27? Scotland included, plus pay rise vs 3.6% inflation.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','28 November 2026'),('Sources','GOV.UK, HMRC, HM Treasury, ONS')],
 [('form','Calculator'),('figures','2026/27 figures'),('ex','Examples: what you keep'),('inflation','Pay rise vs inflation'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
