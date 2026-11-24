import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/au/bonus-tax-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>Annual salary (taxable income without the bonus)</span><div class="money"><input id="s" inputmode="decimal" value="90,000"></div></label><label class="f"><span>Bonus (before tax)</span><div class="money"><input id="b" inputmode="decimal" value="10,000"></div></label><label class="f"><span>HELP / study loan debt?</span><select id="hp"><option value="n" selected>No</option><option value="y">Yes</option></select></label></form>'''

calc='''function calc(){const s=Math.max(0,num('s')),b=Math.max(0,num('b')),h=$('hp')&&$('hp').value==='y',hl=x=>h?X.help(x):0,t=itx(s+b)-itx(s),hr=hl(s+b)-hl(s),all=t+hr;
 if(b<=0)return big('Bonus after tax',aud(0,0),'Enter a bonus amount');
 const rows=[['Bonus',aud(b,0)],['Income tax + Medicare levy on the bonus',aud(-t,0),'neg']];
 if(h)rows.push(['Extra HELP repayment',aud(-hr,0),'neg']);
 rows.push(['You keep',aud(b-all,0),'t'],['Your top tax rate (incl. 2% Medicare)',pc(mr(s+b),0)],['Max your employer can withhold (47%)',aud(b*.47,0)],['Super on the bonus (12%, if it counts as qualifying earnings)',aud(b*.12,0),'pos']);
 return big('Bonus after tax',aud(b-all,0),'tax '+aud(all,0)+' ('+pc(b?all/b:0)+')')+kv(rows)+'<p class="note">This is the tax you finally pay on the bonus for 2026-27 (Australian resident, full year): income tax, low income tax offset and Medicare levy, worked out as the extra tax on salary + bonus. The amount your employer withholds can be a little different; the difference is settled in your tax return.</p>'}'''

BR=[(18200,0),(45000,.15),(135000,.30),(190000,.37),(float('inf'),.45)]
def bands(x):
    t=0;lo=0
    for hi,r in BR:
        if x>lo: t+=(min(x,hi)-lo)*r
        lo=hi
    return t
def lito(x):
    if x<=37500: return 700
    if x<=45000: return 700-(x-37500)*.05
    if x<=66667: return max(0,325-(x-45000)*.015)
    return 0
def med(x):
    if x<=28011: return 0
    if x<=35014: return (x-28011)*.10
    return x*.02
def itx(x): return max(0,bands(x)-lito(x))+med(x)
def helpr(x):
    if x<=69528: return 0
    if x<=129717: return (x-69528)*.15
    if x<=186050: return 9028+(x-129717)*.17
    return x*.10
a=lambda x:f"${x:,.0f}"
rows=[]
for s,b in [(60000,5000),(90000,10000),(120000,10000),(150000,20000),(200000,30000)]:
    t=itx(s+b)-itx(s); hr=helpr(s+b)-helpr(s)
    rows.append([a(s),a(b),a(t),f"{t/b*100:.0f}%",a(b-t),a(b-t-hr)])
print(rows)
ex9=itx(100000)-itx(90000)

fig=[['$0 – $18,200','Nil',''],['$18,201 – $45,000','15c for each $1 over $18,200','Down from 16c in 2025-26'],['$45,001 – $135,000','$4,020 + 30c for each $1 over $45,000',''],['$135,001 – $190,000','$31,020 + 37c for each $1 over $135,000',''],['$190,001 and over','$51,370 + 45c for each $1 over $190,000','']]
oth=[['Medicare levy','2% of taxable income','Lower or nil on low incomes (2025-26 singles: nil up to $28,011).'],
     ['Low income tax offset','Up to $700','Full $700 up to $37,500, phasing out to $0 at $66,667.'],
     ['Withholding cap on bonuses','47% of the bonus','Schedule 5 (from 1 July 2026): with Method A or B(ii), tax withheld can\'t be more than 47%.'],
     ['Super guarantee','12%','Paid on bonuses that count as qualifying earnings (from 1 July 2026) – for example performance and Christmas bonuses.'],
     ['Concessional super cap 2026-27','$32,500','Limit for before-tax super contributions, including salary sacrifice and employer super.'],
     ['HELP repayment 2026-27','Starts above $69,528','15c for each $1 over $69,528, up to $129,717; then $9,028 + 17c; 10% of all repayment income from $186,051.']]

FAQ=[
("How much tax will I pay on a $10,000 bonus?","It depends on your salary. On $90,000 a year, a $10,000 bonus is taxed at 30% plus the 2% Medicare levy, so you pay about $3,200 and keep $6,800. On $60,000, a $5,000 bonus costs about $1,675 (34%), because the low income tax offset shrinks as your income rises."),
("Why does my bonus look so heavily taxed on my payslip?","Your employer works out withholding with the ATO's Schedule 5 methods, which spread the bonus across your pay periods. The amount held back can differ from your final tax, but it can't be more than 47% of the bonus. Your tax return settles the real amount."),
("Is a bonus taxed at a higher rate than my salary?","No. A bonus is ordinary income. It's added to your salary and taxed at the rates for your total income. Only the part of the bonus that pushes you into a higher bracket is taxed at that higher rate."),
("Do I get super on my bonus?","Usually yes. From 1 July 2026 super is paid on 'qualifying earnings'. The ATO lists performance, Christmas, sign-on and referral bonuses as qualifying. A bonus only for work done entirely outside ordinary hours is not. The super guarantee rate is 12%."),
("Can I salary sacrifice my bonus into super?","Yes, if you agree it with your employer before you do the work the bonus is for. Bonuses already earned can't be sacrificed. Salary-sacrificed amounts count towards the $32,500 concessional cap for 2026-27."),
("Does a bonus increase my HELP repayment?","It can. HELP repayments are based on your total repayment income, so a bonus can push you into a higher repayment band. In 2026-27 repayments start above $69,528. Choose 'Yes' for HELP debt in the calculator to see it."),
]

art='''<h2 id="figures">Tax rates for 2026-27 (Australian residents)</h2>
'''+table(['Taxable income','Tax on this income','Note'],fig)+'''
<p class="note">These rates don't include the 2% Medicare levy.</p>
'''+table(['Item','Figure','What it means'],oth)+'''
<h2 id="ex">Bonus tax examples (2026-27)</h2>
<div id="examples">'''+table(['Salary','Bonus','Tax + Medicare on bonus','Share of bonus','You keep','You keep with HELP debt'],rows)+'''</div>
<p class="note">Australian resident for the full year, no other income or deductions. Calculated with this page's formula: tax on salary + bonus minus tax on salary alone.</p>
<h2 id="how">How bonus tax works</h2>
<p>Example first. You earn $90,000 and get a $10,000 bonus. Your income becomes $100,000. All of that bonus falls in the 30% bracket ($45,001 – $135,000). Add the 2% Medicare levy and the bonus is taxed at 32%: <b>$3,200 tax, $6,800 to keep</b>.</p>
<ul><li><b>Marginal rate</b> means the tax rate on your next dollar. It is the rate that matters for a bonus.</li>
<li><b>Bonus tax</b> = tax on (salary + bonus) − tax on salary.</li>
<li>If the bonus crosses a bracket line, part is taxed at the lower rate and part at the higher one. Example: $120,000 + $20,000 = $140,000. $15,000 is taxed at 32% and $5,000 at 39%, so the tax is $6,750.</li>
<li><b>Withholding</b> is the tax your employer takes out when it pays you. It's an estimate; your tax return works out the real figure.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Don't panic about the payslip.</b> Withholding on a bonus can look high or low. What counts is your total income for the year.</li>
<li><b>Ask about salary sacrifice early.</b> It must be agreed before you do the work.</li>
<li><b>Watch the Medicare levy surcharge.</b> If a bonus lifts your income above $105,000 (singles, 2026-27) and you have no private hospital cover, a surcharge of 1% to 1.5% may apply.</li>
<li><b>Check your super.</b> Make sure 12% super was paid on a qualifying bonus.</li>
<li><b>Remember HELP.</b> A bonus can raise your study-loan repayment for the year.</li></ul>
<h2 id="faq" style="margin-top:22px">Bonus tax FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 24 November 2026): <a href="https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents" rel="nofollow">ATO – Tax rates for Australian residents</a>; <a href="https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/what-is-the-medicare-levy" rel="nofollow">ATO – Medicare levy</a>; <a href="https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners" rel="nofollow">ATO – Medicare levy reduction for low-income earners</a>; <a href="https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy-surcharge/medicare-levy-surcharge-income-thresholds-and-rates" rel="nofollow">ATO – Medicare levy surcharge thresholds</a>; <a href="https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/tax-offsets/low-income-tax-offset" rel="nofollow">ATO – Low income tax offset</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/schedule-5-tax-table-for-back-payments-commissions-bonuses-and-similar-payments/about-this-schedule" rel="nofollow">ATO – Schedule 5 (bonuses)</a>; <a href="https://www.ato.gov.au/businesses-and-organisations/super-for-employers/paying-super-on-payday/what-payments-are-qualifying-earnings" rel="nofollow">ATO – What payments are qualifying earnings</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds/super-guarantee" rel="nofollow">ATO – Super guarantee rate</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds/contributions-caps" rel="nofollow">ATO – Contributions caps</a>; <a href="https://www.ato.gov.au/individuals-and-families/jobs-and-employment-types/working-as-an-employee/salary-sacrificing-for-employees" rel="nofollow">ATO – Salary sacrificing</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/study-and-training-support-loans-rates-and-repayment-thresholds" rel="nofollow">ATO – Study and training loan repayment thresholds</a>. General information only.</p>'''

out=build(P,'Bonus Tax Calculator Australia 2026-27 – How Much of My Bonus Do I Keep?',
 'See how much tax you pay on a bonus in Australia in 2026-27 and how much you keep. Marginal rates, Medicare levy, HELP, the 47% withholding cap and super on bonuses.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','24 November 2026'),('Sources','ATO')],
 [('form','Calculator'),('figures','2026-27 tax rates'),('ex','Examples'),('how','How bonus tax works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out, ex9)
