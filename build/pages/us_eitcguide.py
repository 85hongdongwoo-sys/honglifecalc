import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/us/benefits/earned-income-tax-credit-guide.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Check your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>Earned income (wages, self-employment)</span><div class="money"><input id="i" inputmode="decimal" value="25,000"></div><small>We assume your AGI is the same as your earned income.</small></label><label class="f"><span>Qualifying children</span><select id="k"><option value="0">None</option><option value="1">1</option><option value="2" selected>2</option><option value="3">3 or more</option></select></label><label class="f"><span>Filing status</span><select id="fs"><option value="s" selected>Single, head of household or surviving spouse</option><option value="m">Married filing jointly</option></select></label><label class="f"><span>Tax year</span><select id="yr"><option value="2026" selected>2026 (file in 2027)</option><option value="2025">2025 (file in 2026)</option></select></label></form>'''

calc='''function calc(){const P={2026:{ea:[8680,13020,18290,18290],mx:[664,4427,7316,8231],ps:[10860,23890,23890,23890],pm:[18140,31160,31160,31160],inv:12200},2025:{ea:[8490,12730,17880,17880],mx:[649,4328,7152,8046],ps:[10620,23350,23350,23350],pm:[17730,30470,30470,30470],inv:11950}},
 PO=[.0765,.1598,.2106,.2106];const y=P[$('yr')?$('yr').value:'2026'],k=+$('k').value,mj=$('fs')&&$('fs').value==='m',e=Math.max(0,num('i')),th=(mj?y.pm:y.ps)[k],mx=y.mx[k],ea=y.ea[k];
 const up=Math.min(mx,mx*e/ea),cr=Math.max(0,Math.round(up-Math.max(0,e-th)*PO[k])),end=Math.round(th+mx/PO[k]);
 const ph=e<ea?'Phase-in: the credit grows as you earn more':e<=th?'Plateau: you get the maximum credit':e<end?'Phase-out: the credit shrinks as income rises':'Income is above the limit';
 return big('Estimated EITC',usd(cr),$('yr').value+' tax year · '+ph)+kv([['Maximum credit with '+['no children','1 child','2 children','3 or more children'][k],usd(mx)],['Earn this to reach the maximum',usd(ea)],['Credit starts to fall above',usd(th)],['Income limit (credit ends)',usd(end)],['Investment income limit',usd(y.inv)],['IRS EITC Assistant','<a href="https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/use-the-eitc-assistant" rel="nofollow">Check eligibility →</a>','t']])+'<p class="note">Estimate from the IRS amounts and the credit and phase-out rates in the tax code. The IRS EIC table works in $50 steps, so your exact credit can differ by a few dollars. If your AGI is higher than your earned income, the credit can be lower.</p>'}'''

PO=[.0765,.1598,.2106,.2106]
Y={2026:dict(ea=[8680,13020,18290,18290],mx=[664,4427,7316,8231],ps=[10860,23890,23890,23890],pm=[18140,31160,31160,31160],inv=12200,lim=[19540,51593,58629,62974],limm=[26820,58863,65899,70244]),
   2025:dict(ea=[8490,12730,17880,17880],mx=[649,4328,7152,8046],ps=[10620,23350,23350,23350],pm=[17730,30470,30470,30470],inv=11950,lim=[19104,50434,57310,61555],limm=[26214,57554,64430,68675])}
def eitc(e,k,mj=False,yr=2026):
    y=Y[yr];mx=y['mx'][k];th=(y['pm'] if mj else y['ps'])[k]
    up=min(mx,mx*e/y['ea'][k]);return max(0,round(up-max(0,e-th)*PO[k]))
# check derived income limits match IRS published limits
for yr in (2025,2026):
    for k in range(4):
        y=Y[yr]
        assert abs(y['ps'][k]+y['mx'][k]/PO[k]-y['lim'][k])<=1.5,(yr,k)
        assert abs(y['pm'][k]+y['mx'][k]/PO[k]-y['limm'][k])<=1.5,(yr,k)
u=lambda x:f"${x:,.0f}"
ex=[]
for e,k,mj,lab in [(9000,0,False,'Single, no children'),(15000,1,False,'Single parent, 1 child'),(25000,2,False,'Single parent, 2 children'),(40000,2,False,'Single parent, 2 children'),(40000,2,True,'Married couple, 2 children'),(30000,3,True,'Married couple, 3 children')]:
    ex.append([lab,u(e),u(eitc(e,k,mj)),u(eitc(e,k,mj,2025))])
print(ex)
t26=[[['None','1','2','3 or more'][k],u(Y[2026]['mx'][k]),u(Y[2026]['ea'][k]),u(Y[2026]['lim'][k]),u(Y[2026]['limm'][k])] for k in range(4)]
t25=[[['None','1','2','3 or more'][k],u(Y[2025]['mx'][k]),u(Y[2025]['lim'][k]),u(Y[2025]['limm'][k])] for k in range(4)]

FAQ=[
("How much is the Earned Income Tax Credit in 2026?","For tax year 2026 the most you can get is $8,231 with three or more children, $7,316 with two, $4,427 with one and $664 with no qualifying children. For tax year 2025 (returns filed in 2026) the maximums are $8,046, $7,152, $4,328 and $649."),
("What is the income limit for EITC?","For tax year 2026, single filers with two children must earn under $58,629, and married couples filing jointly under $65,899. With no children the limits are $19,540 and $26,820. Your investment income must also be $12,200 or less ($11,950 for 2025)."),
("How much EITC will I get with $25,000 income and 2 kids?","For a single parent in tax year 2026, about $7,082. You are past the $23,890 point where the credit starts to fall, so the $7,316 maximum drops by about 21 cents for each extra dollar."),
("When will I get my refund if I claim EITC?","By law the IRS can't issue EITC or ACTC refunds before mid-February – and that holds up your whole refund, not just the credit. For the 2026 filing season the IRS said most early filers who chose direct deposit and had no problems would get their refund by March 2."),
("Can I get EITC without children?","Yes, if you are at least 25 but under 65 at the end of the year, have a valid Social Security number, and earn under $19,540 (single) or $26,820 (married filing jointly) in 2026. The most you can get is $664."),
("Can I claim EITC for past years?","Yes. The IRS says you have three years from your return's due date to claim a refund. If you filed but didn't claim the EITC, file an amended return on Form 1040-X."),
]

art='''<p class="note" style="margin-top:0">ℹ️ Hong Life is an independent guide, <b>not a government website</b>. Always apply and confirm through the official agency linked on this page.</p>
<h2 id="figures">EITC amounts and income limits</h2>
<h3>Tax year 2026 (returns filed in 2027)</h3>
'''+table(['Qualifying children','Maximum credit','Earned income to get the maximum','Income limit: single / HoH','Income limit: married filing jointly'],t26)+'''
<h3>Tax year 2025 (returns filed in 2026)</h3>
'''+table(['Qualifying children','Maximum credit','Income limit: single / HoH','Income limit: married filing jointly'],t25)+'''
<p class="note">Investment income limit: $12,200 for 2026 and $11,950 for 2025. Married filing separately uses the single limits if you meet the separated-spouse rules.</p>
<h2 id="ex">EITC examples</h2>
<div id="examples">'''+table(['Household','Earned income','EITC 2026','EITC 2025'],ex)+'''</div>
<p class="note">Estimated with this page's formula, assuming AGI equals earned income and no investment income. The IRS table works in $50 income steps, so official amounts can differ by a few dollars.</p>
<h2 id="how">How the EITC is worked out</h2>
<p>Example first. A single parent with two children earns $25,000 in 2026.</p>
<ul><li><b>Phase-in:</b> the credit is 40% of what you earn until it reaches the maximum. With two children you hit the $7,316 maximum at $18,290.</li>
<li><b>Plateau:</b> you keep the maximum until income reaches $23,890 (single) or $31,160 (married filing jointly).</li>
<li><b>Phase-out:</b> above that, the credit falls by 21.06 cents for each extra dollar. $25,000 − $23,890 = $1,110, and $1,110 × 21.06% = $234. So the credit is $7,316 − $234 = <b>$7,082</b>.</li></ul>
<p>The credit rates are 7.65% (no children), 34% (1), 40% (2) and 45% (3 or more). The phase-out rates are 7.65%, 15.98%, 21.06% and 21.06%. <b>Refundable</b> means you get the credit even if you owe no tax – it can come back to you as a refund.</p>
<h3>Who can claim</h3>
<ul><li>You have earned income (wages or self-employment) under the limit.</li>
<li>You, your spouse and any qualifying child have a valid Social Security number issued by the return's due date.</li>
<li>Married people usually must file jointly. A separated spouse can claim in some cases.</li>
<li>A qualifying child must meet the age, relationship, residency and joint return tests.</li>
<li>Without a qualifying child, you must be at least 25 but under 65 at the end of the year.</li></ul>
<h2 id="tips">How to claim and common mistakes</h2>
<ul><li><b>Claim on your return.</b> File Form 1040 and add Schedule EIC if you have a qualifying child.</li>
<li><b>Free help:</b> IRS Volunteer Income Tax Assistance (VITA) sites and IRS Free File.</li>
<li><b>Don't miss it.</b> The IRS estimates about one in five eligible taxpayers don't claim the EITC.</li>
<li><b>Only one person can claim a child.</b> Agree with anyone else in the household who could claim the same child.</li>
<li><b>Expect a wait.</b> Refunds with EITC can't be issued before mid-February.</li></ul>
<h2 id="faq" style="margin-top:22px">EITC FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 24 November 2026): <a href="https://www.irs.gov/pub/irs-drop/rp-25-32.pdf" rel="nofollow">IRS Rev. Proc. 2025-32 (2026 amounts)</a>; <a href="https://www.irs.gov/pub/irs-drop/rp-24-40.pdf" rel="nofollow">IRS Rev. Proc. 2024-40 (2025 amounts)</a>; <a href="https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/earned-income-and-earned-income-tax-credit-eitc-tables" rel="nofollow">IRS – EITC tables</a>; <a href="https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section32&amp;num=0&amp;edition=prelim" rel="nofollow">26 U.S.C. §32 (credit and phase-out rates)</a>; <a href="https://www.irs.gov/taxtopics/tc601" rel="nofollow">IRS Topic 601</a>; <a href="https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/when-to-expect-your-refund-if-you-claimed-the-earned-income-tax-credit-or-additional-child-tax-credit" rel="nofollow">IRS – When to expect your refund</a>; <a href="https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/how-to-claim-the-earned-income-tax-credit-eitc" rel="nofollow">IRS – How to claim the EITC</a>; <a href="https://www.irs.gov/newsroom/earned-income-tax-credit-a-valuable-credit-that-supports-millions-of-families" rel="nofollow">IRS Tax Tip 2026-09</a>. Not tax advice.</p>'''

out=build(P,'Earned Income Tax Credit 2026 – Who Qualifies and How Much (up to $8,231)',
 'EITC 2026 and 2025: maximum credits, income limits for single and married filers, a quick estimate for your income, worked examples and refund timing.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','24 November 2026'),('Sources','IRS, U.S. Code')],
 [('form','Estimate your credit'),('figures','Amounts and limits'),('ex','Examples'),('how','How it works'),('tips','How to claim'),('faq','FAQ')],'On this page',('#examples','en'))
print(out, eitc(25000,2))
