import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/au/super-guarantee-calculator.html'
RATE=.12; MCB=270830; CAP=32500

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Qualifying earnings per year</span><div class="money"><input id="o" inputmode="decimal" value="85,000"></div><small>Your normal pay for ordinary hours, plus most allowances, commissions, shift loadings and any salary you sacrifice into super. Not overtime.</small></label><label class="f"><span>Paid</span><select id="f"><option value="52">Weekly</option><option value="26" selected>Fortnightly</option><option value="12">Monthly</option></select></label><label class="f"><span>Is your salary quoted</span><select id="pk"><option value="x" selected>Plus super</option><option value="i">Including super (package)</option></select></label></form>'''

calc='''function calc(){const A=x=>Math.round(x*100)%100?aud2(x):aud(x,0),R=.12,M=270830,C=32500,v=num('o'),f=+$('f').value,pk=$('pk').value==='i';
 if(v<=0)return big('Employer super per pay','—','Enter your yearly earnings');
 let o=pk?v/(1+R):v;if(pk&&o>M)o=v-M*R;const sg=Math.min(o,M)*R;
 const rows=[['Qualifying earnings',aud(o,0)+' a year'],['Super guarantee rate','12%'],['Employer super a year',A(sg),'pos'],['After 15% contributions tax in the fund',aud(sg*.85,0)+' a year'],['Concessional cap 2026-27 left after SG',A(Math.max(0,C-sg))+' of $32,500'],['Due date','Must reach your fund within 7 business days of each payday']];
 if(pk)rows.splice(1,0,['Package entered',A(v)+' = '+A(o)+' pay + '+A(sg)+' super']);
 return big('Employer super per pay',aud2(sg/f),A(sg)+' a year · '+(f===52?'weekly':f===26?'fortnightly':'monthly')+' pay '+aud2(o/f))+kv(rows)
 +(o>M?'<p class="note">Your earnings are above the 2026-27 maximum contribution base of $270,830. Your employer only has to pay 12% on the first $270,830 ($32,499.60). Once that is reached in a year, no more SG is due until 1 July.</p>':'')
 +(o+sg>250000?'<p class="note">Income plus concessional contributions over $250,000 may mean an extra 15% Division 293 tax on your contributions.</p>':'')
 +'<p class="note">Rates for 1 July 2026 – 30 June 2027. Some awards and agreements require more than 12%.</p>'}'''

def sg(v,pk=False):
    o=v/(1+RATE) if pk else v
    if pk and o>MCB: o=v-MCB*RATE
    return o,min(o,MCB)*RATE
a2=lambda x:f"${x:,.2f}"; a=lambda x:(a2(x) if abs(x-round(x))>0.004 else f"${x:,.0f}")
rows=[]
for v in (45000,65000,85000,120000,180000,300000):
    o,s=sg(v)
    rows.append([a(v),a(s),a2(s/52),a2(s/26),a2(s/12),a(s*.85),a(max(0,CAP-s))])
for r in rows: print(r)
pkrows=[]
for v in (67200,95200,134400,310000):
    o,s=sg(v,True); pkrows.append([a(v),a(o),a(s),a2(s/26)])
for r in pkrows: print(r)

fig=[['Super guarantee (SG) rate','12%','For 2025-26, 2026-27 and later years. It was 11.5% in 2024-25.'],
     ['What SG is paid on (from 1 July 2026)','Qualifying earnings (QE)','Ordinary time earnings plus all commissions and salary-sacrificed amounts. Overtime is not included.'],
     ['Payday Super start','1 July 2026','Super must be paid every payday, not every quarter. Pay up to 30 June 2026 followed the old quarterly rules.'],
     ['When super must arrive','Within 7 business days of payday','It must be received by your fund, not just sent. 20 business days for a new employee\'s first payment or a new fund. Weekends and state-wide public holidays don\'t count.'],
     ['Maximum contribution base 2026-27','$270,830 a year','No SG is needed on earnings above this in one financial year. 12% × $270,830 = $32,499.60. In 2025-26 it was $62,500 a quarter.'],
     ['Concessional contributions cap 2026-27','$32,500','The most before-tax super (employer SG + salary sacrifice + claimed personal contributions) at the normal 15% tax. Was $30,000 in 2025-26.'],
     ['Non-concessional cap 2026-27','$130,000','After-tax contributions. Was $120,000 in 2025-26.'],
     ['Tax inside the fund','15%','Taken from concessional contributions by your fund.'],
     ['Division 293 tax','Extra 15% above $250,000','If your income plus concessional contributions is over $250,000.'],
     ['Under 18s','More than 30 hours a week','Under 18s only get SG for weeks they work more than 30 hours. Most other employees get it no matter how much they earn.']]

FAQ=[
("How much super is paid on $85,000?","12% of $85,000 = $10,200 a year. That is $196.15 a week, $392.31 a fortnight or $850 a month. After the 15% tax in the fund, $8,670 a year goes into your account."),
("What is the super guarantee rate for 2026-27?","12% of your qualifying earnings. It went up from 11.5% to 12% on 1 July 2025 and stays at 12% for 2026-27 and later years."),
("What is Payday Super?","From 1 July 2026 your employer must pay your super each time they pay your wages, not once a quarter. The money has to reach your super fund within 7 business days of payday (20 business days for a new employee's first payment)."),
("What is the maximum super contribution base for 2026-27?","$270,830 a year. It is now a yearly limit, not $62,500 a quarter as in 2025-26. On $300,000 your employer only has to pay 12% of $270,830, which is $32,499.60, instead of $36,000."),
("My salary is $95,200 including super. How much is super?","$95,200 ÷ 1.12 = $85,000 pay and $10,200 super (12%). Choose “Including super (package)” in the calculator to split a package like this."),
("Does employer super count toward the concessional cap?","Yes. SG, salary sacrifice and personal contributions you claim a deduction for all count toward the $32,500 cap for 2026-27. On $85,000, SG uses $10,200, so about $22,300 is left for salary sacrifice."),
("Is super paid on overtime?","Usually not. Overtime is not part of qualifying earnings. Super is paid on ordinary hours pay, most allowances, commissions, shift loadings and salary-sacrificed amounts."),
]

art='''<h2 id="figures">Super guarantee figures for 2026-27</h2>
<p>The <b>super guarantee (SG)</b> is the money your employer must pay into your super fund on top of your pay. These are the official ATO figures for 1 July 2026 to 30 June 2027.</p>
'''+table(['Item','Figure','What it means'],fig)+'''
<h2 id="ex">How much super your employer pays: examples</h2>
<div id="examples">'''+table(['Earnings a year','Super a year (12%)','Per week','Per fortnight','Per month','After 15% fund tax','Concessional cap left'],rows)+'''</div>
<ul><li><b>The calculator's starting example:</b> $85,000 plus super, paid fortnightly. Your employer pays $392.31 every payday – $10,200 a year.</li>
<li><b>$300,000:</b> super stops at the maximum contribution base. 12% of $270,830 = $32,499.60, so the cap is almost used up by SG alone.</li></ul>
<h3 id="package">If your salary includes super</h3>
<p>A “package” or “total remuneration” figure already has super inside it. Divide by 1.12 to find your pay.</p>
'''+table(['Package','Pay (before tax)','Super (12%)','Super per fortnight'],pkrows)+'''
<p class="note">Above the maximum contribution base the split is package − $32,499.60, because super stops growing at $270,830 of earnings.</p>
<h2 id="how">How the calculator works</h2>
<p>Example first: $85,000 × 12% = $10,200 a year. Paid fortnightly, that is $10,200 ÷ 26 = $392.31 each payday.</p>
<ul><li><b>Super a year</b> = 12% × the smaller of your qualifying earnings and $270,830.</li>
<li><b>Super per pay</b> = super a year ÷ number of paydays (52, 26 or 12).</li>
<li><b>Package</b>: pay = package ÷ 1.12 (or package − $32,499.60 above the base).</li>
<li><b>After fund tax</b> = super × 85%. Your fund takes 15% contributions tax.</li></ul>
<p><b>Qualifying earnings</b> is the new name (from 1 July 2026) for the pay super is worked out on. It is your <b>ordinary time earnings</b> – pay for your normal hours – plus commissions and amounts you salary sacrifice. <b>Salary sacrifice</b> means paying some of your before-tax salary into super.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Check your fund, not just your payslip.</b> Since 1 July 2026 super should show up in your account within about 7 business days of each payday. Look in your fund's app or in myGov (ATO online services).</li>
<li><b>Package or plus super?</b> A $90,000 job “plus super” is worth $10,800 more a year in total than a $90,000 package.</li>
<li><b>Salary sacrifice must not cut your SG.</b> From 1 July 2026 salary-sacrificed amounts count in your qualifying earnings, so your employer still pays 12% on your full pre-sacrifice pay.</li>
<li><b>Watch the $32,500 cap.</b> SG + salary sacrifice + deducted personal contributions over $32,500 are taxed extra.</li>
<li><b>Missing super?</b> Ask your employer first. If it is still missing, the ATO has an unpaid super process.</li></ul>
<h2 id="faq" style="margin-top:22px">Super guarantee FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 28 November 2026): <a href="https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds/super-guarantee" rel="nofollow">ATO – Super guarantee rates and maximum contribution base</a>; <a href="https://www.ato.gov.au/businesses-and-organisations/super-for-employers/paying-super-on-payday/what-payments-are-qualifying-earnings/maximum-contributions-base" rel="nofollow">ATO – Maximum contribution base (Payday Super)</a>; <a href="https://www.ato.gov.au/businesses-and-organisations/super-for-employers/paying-super-on-payday/payment-deadlines-for-payday-super" rel="nofollow">ATO – Payment deadlines for Payday Super</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds/contributions-caps" rel="nofollow">ATO – Contributions caps</a>; <a href="https://www.ato.gov.au/individuals-and-families/super-for-individuals-and-families/super/growing-and-keeping-track-of-your-super/super-from-your-employer" rel="nofollow">ATO – Super from your employer</a>; <a href="https://www.ato.gov.au/individuals-and-families/super-for-individuals-and-families/super/growing-and-keeping-track-of-your-super/caps-limits-and-tax-on-super-contributions/understanding-concessional-and-non-concessional-contributions" rel="nofollow">ATO – Concessional and non-concessional contributions</a>. General information only – not financial advice.</p>'''

out=build(P,'Super Guarantee Calculator 2026-27 – 12% Per Pay With Payday Super',
 'Work out 12% super guarantee per week, fortnight or month in 2026-27. Payday Super from 1 July 2026, $270,830 maximum base and $32,500 cap.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','28 November 2026'),('Sources','ATO')],
 [('form','Calculator'),('figures','2026-27 super figures'),('ex','Examples per pay'),('package','Salary including super'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
