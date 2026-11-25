import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/uk/savings-interest-tax-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"£"}</style><label class="f"><span>Salary, pension and other non-savings income (a year)</span><div class="money"><input id="o" inputmode="decimal" value="35,000"></div><small>Before tax. Include wages, self-employed profit, pensions and rent.</small></label><label class="f"><span>Savings interest outside ISAs (a year)</span><div class="money"><input id="i" inputmode="decimal" value="2,400"></div><small>Interest from bank and building society accounts. Leave out ISA interest – it is always tax-free.</small></label></form>'''

calc='''function calc(){const o=num('o'),i=num('i');
 function t(R){const p=pa(o+i),ns=Math.max(0,o-p),i1=Math.max(0,i-Math.max(0,p-o)),T=ns+i1;
  const band=T>125140?'a':T>37700?'h':'b',psa=band=='b'?1000:band=='h'?500:0,sr=Math.min(i1,Math.max(0,5000-ns)),ps=Math.min(i1-sr,psa);
  let lo=ns+sr+ps,hi=ns+i1,tax=0;const B=[[37700,R[0]],[125140,R[1]],[Infinity,R[2]]];let a=0;
  for(const [u,r] of B){const x=Math.max(0,Math.min(hi,u)-Math.max(lo,a));tax+=x*r;a=u}
  return {p,paUsed:i-i1,sr,psa,ps,taxable:hi-lo,tax,band}}
 const a=t([.20,.40,.45]),b=t([.24,.44,.49]),nm={b:'a basic-rate',h:'a higher-rate',a:'an additional-rate'}[a.band];
 return big('Tax on your interest (2026/27)',gbp2(a.tax),'You are '+nm+' taxpayer')+kv([['Covered by unused Personal Allowance',gbp(a.paUsed,0)],['Starting rate for savings (0%)',gbp(a.sr,0)],['Personal Savings Allowance used',gbp(a.ps,0)+' of '+gbp(a.psa,0)],['Taxable interest',gbp(a.taxable,0),'t'],['Tax 2026/27 (20% / 40% / 45%)',gbp2(a.tax),'neg'],['Same interest from April 2027 (24% / 44% / 49%)',gbp2(b.tax),'neg']])+'<p class="note">Rules for England, Wales and Northern Ireland. From 6 April 2027 savings interest above your tax-free amounts is taxed 4 percentage points higher.</p>'}'''

# --- python re-implementation of the same formula ---
def pa(ani): return max(0,12570-max(0,ani-100000)/2)
def t(o,i,R):
    p=pa(o+i);ns=max(0,o-p);i1=max(0,i-max(0,p-o));T=ns+i1
    band='a' if T>125140 else 'h' if T>37700 else 'b';psa={'b':1000,'h':500,'a':0}[band]
    sr=min(i1,max(0,5000-ns));ps=min(i1-sr,psa);lo=ns+sr+ps;hi=ns+i1;tax=0;a=0
    for u,r in [(37700,R[0]),(125140,R[1]),(float('inf'),R[2])]:
        x=max(0,min(hi,u)-max(lo,a));tax+=x*r;a=u
    return tax,psa,sr
g=lambda x:f"£{x:,.0f}" if abs(x-round(x))<0.005 else f"£{x:,.2f}"
EX=[(35000,2400),(15000,3000),(60000,1500),(140000,4000)]
rows=[]
for o,i in EX:
    a,psa,sr=t(o,i,(.2,.4,.45));b,_,_=t(o,i,(.24,.44,.49))
    rows.append([g(o),g(i),g(min(sr+psa,i)),g(a),g(b)])
for r in rows: print(r)

fig=[['Personal Allowance','£12,570','Income you can get each year before any tax. It shrinks by £1 for every £2 of income over £100,000.'],
     ['Starting rate for savings','Up to £5,000 of interest at 0%','Cut by £1 for every £1 of other income over £12,570. Gone once other income reaches £17,570.'],
     ['Personal Savings Allowance','£1,000 basic rate · £500 higher rate · £0 additional rate','Interest you can earn tax-free on top of the above.'],
     ['Basic rate band','First £37,700 of taxable income','Taxable income = income minus your Personal Allowance. Up to £50,270 total income for most people.'],
     ['Additional rate','Taxable income over £125,140','No Personal Allowance and no Personal Savings Allowance at this level.'],
     ['Tax on savings interest 2026/27','20% · 40% · 45%','Same rates as on wages for basic, higher and additional rate.'],
     ['Tax on savings interest from 6 April 2027','24% · 44% · 49%','Savings rates for 2027/28 in Budget 2026 Annex A (rates and allowances). The tax-free amounts above stay.'],
     ['ISA allowance 2026/27','£20,000','Interest in a cash ISA is always tax-free and does not use your allowances.']]

FAQ=[
("How much interest can I earn before paying tax?","It depends on your other income. A basic-rate taxpayer can earn £1,000 of interest tax-free, a higher-rate taxpayer £500 and an additional-rate taxpayer £0. If your other income is under £17,570 you can also get up to £5,000 extra at 0% (the starting rate for savings). So someone on £15,000 can earn up to £3,570 of interest tax-free."),
("Do I pay tax on £2,400 of interest on a £35,000 salary?","Yes, £280 in 2026/27. The first £1,000 is covered by the Personal Savings Allowance. The other £1,400 is taxed at 20%. With the same interest from April 2027 it would be £336 (24%)."),
("How much tax will I pay on savings from April 2027?","Interest above your tax-free amounts will be taxed at 24% (basic), 44% (higher) or 49% (additional), up from 20%, 40% and 45%. The £1,000 and £500 allowances and the £5,000 starting rate stay. A higher-rate taxpayer with £1,500 of interest pays £400 now and £440 from April 2027."),
("Does savings interest push me into the higher rate?","It can. Interest counts as income. If your salary plus interest takes your taxable income over £37,700 (about £50,270 in total), you become a higher-rate taxpayer and your Personal Savings Allowance drops from £1,000 to £500."),
("How does HMRC collect tax on savings interest?","Banks tell HMRC how much interest you earned. If you are employed or get a pension, HMRC usually changes your tax code to collect it. If you already fill in a Self Assessment return, you add it there."),
("Is ISA interest counted towards the Personal Savings Allowance?","No. Interest in a cash ISA is tax-free and is ignored. You can put up to £20,000 a year into ISAs in 2026/27. Moving savings into an ISA is the simplest way to stop paying tax on interest."),
]

art='''<h2 id="figures">UK savings tax figures for 2026/27 (and April 2027)</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<h2 id="ex">Tax on savings interest: examples</h2>
<div id="examples">'''+table(['Other income','Interest','Tax-free part','Tax 2026/27','Tax from April 2027'],rows)+'''</div>
<ul><li><b>£35,000 salary, £2,400 interest:</b> £1,000 is tax-free. You pay 20% on £1,400 = <b>£280</b>. From April 2027: 24% = £336.</li>
<li><b>£15,000 pension, £3,000 interest:</b> the £15,000 is £2,430 over the Personal Allowance, so the starting rate is £5,000 − £2,430 = £2,570. Add the £1,000 allowance and all £3,000 is tax-free: <b>£0</b>.</li>
<li><b>£60,000 salary, £1,500 interest:</b> you are a higher-rate taxpayer, so only £500 is tax-free. 40% on £1,000 = <b>£400</b> (£440 from April 2027).</li>
<li><b>£140,000 income, £4,000 interest:</b> no allowances at all. 45% on £4,000 = <b>£1,800</b> (£1,960 from April 2027).</li></ul>
<p class="note">All examples use this calculator's formula for England, Wales and Northern Ireland and ignore ISA interest.</p>
<h2 id="how">How tax on savings works</h2>
<p>Think of it as three free layers, used in this order. Whatever is left is taxed.</p>
<ul><li><b>1. Unused Personal Allowance.</b> If your wages or pension are under £12,570, interest first fills the gap at 0%.</li>
<li><b>2. Starting rate for savings.</b> Up to £5,000 of interest at 0%. Every £1 of other income over £12,570 cuts it by £1. A £15,000 pension leaves £2,570.</li>
<li><b>3. Personal Savings Allowance (PSA).</b> £1,000 if all your taxable income stays in the basic rate band, £500 in the higher rate band, £0 in the additional rate band.</li>
<li><b>The rest</b> is taxed at your rate: 20%, 40% or 45% in 2026/27. Interest sits on top of your other income, so part of it can fall into a higher band.</li></ul>
<p>Interest that is tax-free under the PSA still counts as income. It can still move you into the higher rate band.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Count interest when it is paid.</b> For a fixed-rate bond that pays all its interest at the end, the whole amount counts in the tax year it is paid.</li>
<li><b>Joint accounts:</b> each of you usually counts half the interest.</li>
<li><b>Fill your ISA first</b> if your interest is near your allowance. The rate rise in April 2027 makes this more valuable.</li>
<li><b>Check your tax code.</b> HMRC estimates interest from last year. If your interest has gone down, ask HMRC to update it.</li>
<li><b>Near £100,000?</b> Interest counts towards it too. Above £100,000 you start to lose your Personal Allowance.</li></ul>
<h2 id="faq" style="margin-top:22px">Savings tax FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.gov.uk/apply-tax-free-interest-on-savings/how-much-is-tax-free" rel="nofollow">GOV.UK – Tax on savings interest</a>; <a href="https://www.gov.uk/income-tax-rates" rel="nofollow">GOV.UK – Income Tax rates and Personal Allowances</a>; <a href="https://www.gov.uk/government/publications/budget-2026-overview-of-tax-legislation-and-rates-ootlar/annex-a-rates-and-allowances" rel="nofollow">HM Treasury – Budget 2026 rates and allowances</a>; <a href="https://www.gov.uk/government/publications/income-tax-changes-to-tax-rates-for-property-and-savings-income" rel="nofollow">HMRC – Changes to tax rates for property and savings income</a>; <a href="https://www.gov.uk/individual-savings-accounts" rel="nofollow">GOV.UK – ISAs</a>. Examples use this calculator's own formula. General information, not tax advice.</p>'''

out=build(P,'Tax on Savings Interest Calculator UK 2026/27 – and April 2027 Rates',
 'How much tax you pay on savings interest in 2026/27: Personal Savings Allowance, £5,000 starting rate and the new 24%/44%/49% savings rates from April 2027.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','GOV.UK, HMRC, HM Treasury')],
 [('form','Calculator'),('figures','Official figures'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
