import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/au/super-co-contribution-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>Total income (assessable + reportable fringe benefits + RESC)</span><div class="money"><input id="i" inputmode="decimal" value="42,000"></div><small>RESC = reportable employer super contributions, such as salary sacrifice. Take off any business deductions.</small></label><label class="f"><span>Personal after-tax contributions you will make</span><div class="money"><input id="n" inputmode="decimal" value="1,000"></div><small>Money you put into super from your take-home pay and don't claim a tax deduction for.</small></label><label class="f"><span>Concessional contributions (employer SG etc.)</span><div class="money"><input id="cc" inputmode="decimal" value="5,040"></div><small>Before-tax contributions: your employer's super guarantee, salary sacrifice and any personal contributions you claim as a deduction. Used only to tell you if LISTO may apply.</small></label></form>'''

calc='''function calc(){const i=Math.max(0,num('i')),n=Math.max(0,num('n')),c=Math.max(0,num('cc'));
 const mx=i<=49293?500:i>=64293?0:Math.max(0,500-(i-49293)*0.03333);
 let co=Math.min(mx,n*.5);if(co>0&&co<20)co=20;
 const li=i<=37000&&c>0;
 const rows=[['Maximum co-contribution at your income',aud(mx,0)],['After-tax contribution needed to get it',aud(mx*2,0)],['Co-contribution on your amount',aud(co,0),'pos'],['LISTO (low income super tax offset)',li?'You may also get up to $500':'Not likely (income over $37,000 or no before-tax contributions)',li?'pos':'']];
 if(n>mx*2&&mx>0)rows.push(['Contribution above what earns a match',aud(n-mx*2,0)]);
 return big('Government co-contribution',aud(co,0),li?'plus LISTO of up to $500 may apply':'for 2026-27')+kv(rows)+'<p class="note">2026-27 thresholds. You also need: 10% or more of your total income from work or a business, a lodged tax return, age under 71 at the end of the year, no temporary visa during the year (some exceptions), a total super balance below the general transfer balance cap on 30 June last year, and non-concessional contributions within the cap. The LISTO check uses your total income as a stand-in for adjusted taxable income. The ATO works out the amounts after you lodge and pays them into your fund.</p>'}'''

def co(i,n):
    mx=500 if i<=49293 else 0 if i>=64293 else max(0,500-(i-49293)*0.03333)
    c=min(mx,n*.5)
    if 0<c<20: c=20
    return mx,c
a=lambda x:f"${x:,.0f}"
rows=[]
for i,n in [(35000,1000),(42000,1000),(55000,1000),(60000,500),(64000,1000)]:
    mx,cc=co(i,n)
    rows.append([a(i),a(n),a(mx),a(cc),'May apply (up to $500)' if i<=37000 else 'No'])
print(rows)

fig=[['Co-contribution: matching rate','50 cents for every $1 of personal after-tax contributions','You put in $1,000, the government adds up to $500.'],
     ['Co-contribution: maximum','$500','Full amount if your total income is $49,293 or less (2026-27).'],
     ['Lower income threshold 2026-27','$49,293','Above this the maximum falls steadily: $500 ÷ ($64,293 − $49,293) = about 3.33 cents per $1 of extra income.'],
     ['Higher income threshold 2026-27','$64,293','At or above this you get no co-contribution.'],
     ['Smallest co-contribution paid','$20','If your entitlement works out lower, the ATO pays $20.'],
     ['10% eligible income test','10% or more of total income from work or a business','Income from employment-related activities, carrying on a business, or both.'],
     ['Age limit','Under 71 at the end of the financial year','You also need to lodge a tax return for the year.'],
     ['LISTO','Up to $500','Refunds the tax paid on your before-tax (concessional) super contributions if your adjusted taxable income is $37,000 or less.']]

FAQ=[
("How much is the super co-contribution in 2026-27?","Up to $500. You get 50 cents for each $1 you put into super after tax. If your total income is $49,293 or less, $1,000 earns the full $500. Above that the maximum shrinks, and at $64,293 it reaches $0."),
("How much should I put in to get the full $500?","$1,000 of personal after-tax contributions, if your total income is $49,293 or less. Putting in more doesn't increase the co-contribution. At $55,000 income the maximum is about $310, so $620 is enough."),
("Do I need to apply for the co-contribution?","No. Lodge your tax return and make sure your fund has your tax file number – the fund needs it before it can accept the payment. The ATO works out the amount and pays it into your super fund."),
("What is LISTO?","LISTO (low income super tax offset) gives back the tax paid on your before-tax super contributions, up to $500 a year. You can get it if your adjusted taxable income is $37,000 or less. The ATO pays it into your fund."),
("Can I get both the co-contribution and LISTO?","Yes. Someone earning $35,000 who puts in $1,000 after tax can get the full $500 co-contribution, and LISTO of up to $500 on top."),
("Does salary sacrifice count for the co-contribution?","No. Salary sacrifice is a before-tax (concessional) contribution. Only personal after-tax contributions you don't claim a deduction for earn the co-contribution. Salary sacrifice is added to your total income for the income test."),
("Why did I get less than I expected?","Common reasons: your total income was above $49,293, you claimed a tax deduction for the contribution, less than 10% of your income came from work or a business, your total super balance was too high, or you haven't lodged your tax return yet."),
]

art='''<h2 id="figures">2026-27 co-contribution and LISTO figures</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<h2 id="ex">Examples: free super at different incomes</h2>
<div id="examples">'''+table(['Total income','After-tax contribution','Max co-contribution','Co-contribution','LISTO'],rows)+'''</div>
<ul><li>At <b>$35,000</b>, putting in $1,000 gets the full <b>$500</b> co-contribution, and LISTO may add up to $500 more.</li>
<li>At <b>$42,000</b> you still get the full $500 co-contribution, but not LISTO, because income is over $37,000.</li>
<li>At <b>$55,000</b> the maximum drops to about <b>$310</b>: $500 − ($55,000 − $49,293) × 0.03333.</li>
<li>At <b>$64,000</b> the formula gives under $10, so the $20 minimum applies.</li></ul>
<p class="note">Examples use this calculator's own formula. The 0.03333 taper is our arithmetic: $500 spread evenly over the $15,000 between the two thresholds.</p>
<h2 id="how">How it works</h2>
<p>Example first. You earn $55,000 and put $1,000 of your own after-tax money into super. Your income is $5,707 over $49,293. The maximum falls by 3.333 cents for each of those dollars: $5,707 × 0.03333 = $190. So the maximum is $500 − $190 = <b>$310</b>. Half of your $1,000 is $500, which is more than $310, so you get <b>$310</b>.</p>
<ul><li><b>Total income</b> = assessable income + reportable fringe benefits + reportable employer super contributions, minus business deductions.</li>
<li><b>Maximum</b> = $500 − (total income − $49,293) × 0.03333, never below $0.</li>
<li><b>Co-contribution</b> = the smaller of half your after-tax contribution and the maximum.</li>
<li><b>LISTO</b> = a refund of the tax on before-tax contributions, up to $500, if adjusted taxable income is $37,000 or less.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Contribute before 30 June.</b> The money must reach your fund by the end of the financial year.</li>
<li><b>Don't claim a deduction for it.</b> If you claim a tax deduction, the contribution no longer counts for the co-contribution.</li>
<li><b>Lodge your tax return.</b> Nothing is paid until you do.</li>
<li><b>Give your fund your TFN.</b> Without your tax file number the fund can't accept the payment.</li>
<li><b>Only put in what you need.</b> Above the amount that earns the maximum, extra money gets no match (it still helps your super).</li></ul>
<h2 id="faq" style="margin-top:22px">Super co-contribution FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds/government-contributions" rel="nofollow">ATO – key super rates: government contributions</a>; <a href="https://www.ato.gov.au/individuals-and-families/super-for-individuals-and-families/super/growing-and-keeping-track-of-your-super/how-to-save-more-in-your-super/government-super-contributions/super-co-contribution" rel="nofollow">ATO – super co-contribution</a>; LISTO figures from the same ATO pages. Examples use this calculator's own formula. General information, not financial advice.</p>'''

out=build(P,'Super Co-contribution Calculator 2026-27 – Up to $500 Free',
 'Work out your government super co-contribution (up to $500) for 2026-27 and whether LISTO applies. Income thresholds $49,293 and $64,293, with examples.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','ATO')],
 [('form','Calculator'),('figures','2026-27 figures'),('ex','Examples'),('how','How it works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
