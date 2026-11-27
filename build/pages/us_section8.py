import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/us/benefits/section-8-housing-voucher.html'

# HUD CY2026 inflation-adjusted amounts (HOTMA, 24 CFR 5.611): $500 / $550; CY2027: $525 / $575; pre-HOTMA base $480 / $525
DEP=500
ELD=550

form='''<form class="card" id="form" onsubmit="return false"><h2>Check your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>Which deduction amounts?</span><select id="yr"><option value="26" selected>2026 ($500 per dependent, $550 elderly/disabled)</option><option value="27">From 1 Jan 2027 ($525 / $575)</option><option value="old">Agency still on old rules ($480 / $525)</option></select><small>Ask your housing agency which amounts it uses.</small></label><label class="f"><span>Household income per year (before tax)</span><div class="money"><input id="i" inputmode="decimal" value="24,000"></div></label><label class="f"><span>Dependents (children under 18, disabled or full-time students)</span><input id="d" inputmode="decimal" value="2"><small>Do not count the head of household, spouse, or foster children and foster adults.</small></label><label class="f"><span>Head or spouse 62+ or disabled?</span><select id="el"><option value="0" selected>No</option><option value="1">Yes</option></select></label><label class="f"><span>Child care costs per year (optional)</span><div class="money"><input id="cc" inputmode="decimal" value="0"></div><small>For children 12 and under, so an adult can work, study or look for work.</small></label><label class="f"><span>Rent + utilities for the unit (per month)</span><div class="money"><input id="r" inputmode="decimal" value="1,500"></div></label><label class="f"><span>Local payment standard for this unit size</span><div class="money"><input id="ps" inputmode="decimal" value="1,600"></div><small>Ask your housing agency. It is the most the voucher is based on for this bedroom size.</small></label></form>'''

calc=('''function calc(){const Y={'26':[500,550],'27':[525,575],'old':[480,525]}[$('yr').value]||[%d,%d],DEP=Y[0],ELD=Y[1],inc=num('i'),dn=Math.max(0,Math.round(num('d'))),el=$('el').value==='1',cc=Math.max(0,num('cc'));
 const adjY=Math.max(0,inc-DEP*dn-(el?ELD:0)-cc),adj=adjY/12,gross=inc/12,ttp=Math.max(adj*.3,gross*.1),rent=num('r'),ps=num('ps'),cap=Math.min(rent,ps),hap=Math.max(0,cap-ttp),you=rent-hap,over40=rent>ps&&you>adj*.4;
 const nt='<p class="note">Simplified: your housing agency may also use a minimum rent, utility allowances and other deductions. The agency makes the final calculation.</p>';
 return big('You would pay about',usd(you)+'/month','voucher pays '+usd(hap))+kv([['Deductions used',usd(DEP)+' per dependent'+(el?', '+usd(ELD)+' elderly/disabled':'')],['Adjusted income per year',usd(adjY)],['30%% of adjusted monthly income',usd(adj*.3)],['10%% of gross monthly income',usd(gross*.1)],['Your basic share (the higher one)',usd(ttp)],['Rent the voucher is based on',usd(cap)],...(rent>ps?[['Rent above the payment standard',usd(rent-ps),'neg']]:[]),['Your share of income',pc(adj?you/adj:0)+' of adjusted income'],...(over40?[['40%% rule','At move-in your share may not be over 40%% of adjusted income ('+usd(adj*.4)+'). Look for a cheaper unit.','neg']]:[])])+nt}''' % (DEP,ELD))

usd=lambda x:f"${x:,.0f}"
def calcpy(inc,dn,el,cc,rent,ps):
    adjY=max(0,inc-DEP*dn-(ELD if el else 0)-cc);adj=adjY/12
    ttp=max(adj*.3,inc/12*.1);hap=max(0,min(rent,ps)-ttp);you=rent-hap
    return adjY,ttp,hap,you,adj
E=[('Family of 4, $24,000, 2 children',24000,2,0,0,1500,1600),
   ('Single parent, $18,000, 1 child, $2,700 child care',18000,1,0,2700,1300,1400),
   ('Senior living alone, $14,400 Social Security',14400,0,1,0,1100,1200),
   ('Family of 3, $29,700, 1 child, rent $200 over standard',29700,1,0,0,1800,1600)]
exs=[]
for lab,*a in E:
    adjY,ttp,hap,you,adj=calcpy(*a)
    exs.append([lab,usd(a[4])+' (standard '+usd(a[5])+')',usd(adjY),usd(ttp),usd(hap),usd(you)])
    print(lab,adjY,round(ttp,2),round(hap,2),round(you,2),round(you/adj*100,1) if adj else 0)

FAQ=[
("How much rent do you pay with Section 8?","Usually about 30% of your adjusted monthly income. For example, a family of 4 earning $24,000 with 2 children has adjusted income of $23,000 in 2026 ($24,000 − 2 × $500), so their share is $575 a month. The voucher pays the rest, up to the local payment standard."),
("What counts as adjusted income for Section 8?","Your yearly income before tax, minus deductions. In 2026 these are $500 for each dependent and $550 if the head or spouse is 62 or older or disabled (from 1 January 2027: $525 and $575). Child care costs for children under 13 also come off, and medical or disability costs above 10% of your yearly income for elderly or disabled families. Agencies not yet on the new HUD rules still use $480 and $525."),
("What is the income limit for a Section 8 voucher?","Most families must be under 50% of the area median income (AMI) for their county and family size. Each housing agency must give at least 75% of new vouchers each year to families under 30% of AMI. The limits differ by area, so check with your local agency or HUD."),
("Can I rent a place that costs more than the payment standard?","Yes, but you pay the extra. When you first rent the unit, your share of rent and utilities cannot be more than 40% of your adjusted monthly income. This 40% limit is checked at move-in (initial occupancy)."),
("Why do I pay more than 30%?","Because the rent is above the payment standard, or because 10% of your gross monthly income is higher than 30% of your adjusted income. The higher of the two is used. Your agency can also set a minimum rent of up to $50."),
("How long is the Section 8 waiting list?","It depends on the area. Many agencies have long waiting lists and open them only for a short time. Ask your local public housing agency (PHA) when its list opens."),
("Does the voucher pay utilities?","The voucher is based on rent plus utilities. If you pay utilities yourself, the agency gives a utility allowance, which lowers the rent you pay to the landlord."),
]

art='''<p class="note" style="margin-top:0">Hong Life is an independent guide, <b>not a government website</b>. Apply and confirm with your local public housing agency.</p>
<h2 id="figures">Key Section 8 rules</h2>
'''+table(['Rule','Amount','What it means'],[
 ['Your basic share','The higher of 30% of adjusted monthly income or 10% of gross monthly income','This is called the total tenant payment.'],
 ['Dependent deduction','$500 a year in 2026 ($525 from 1 Jan 2027)','For each child under 18, or a family member who is disabled or a full-time student. Not the head, spouse or foster members.'],
 ['Elderly or disabled family deduction','$550 a year in 2026 ($575 from 1 Jan 2027)','If the head or spouse is 62+ or disabled.'],
 ['Older amounts','$480 and $525','Used by agencies that have not yet switched to the new HUD (HOTMA) income rules.'],
 ['Child care deduction','Reasonable costs for children under 13','So an adult can work, study or look for work, if nobody pays you back.'],
 ['Medical and disability costs','The part above 10% of yearly income','For elderly or disabled families (new HUD rules).'],
 ['Minimum rent','Up to $50 a month','Set by your agency.'],
 ['40% rule','Your share at move-in','Cannot be over 40% of adjusted monthly income if rent is above the payment standard.'],
 ['Income limit','Usually under 50% of area median income','75% of new vouchers go to families under 30%.']])+'''
<h2 id="ex">Examples: how much rent will I pay?</h2>
<div id="examples">'''+table(['Household','Rent + utilities','Adjusted income per year','Your basic share','Voucher pays','You pay per month'],exs)+'''</div>
<ul><li><b>Family of 4 on $24,000.</b> Adjusted income is $24,000 − 2 × $500 = $23,000, or about $1,917 a month. 30% of that is $575. The voucher pays $925 of the $1,500 rent.</li>
<li><b>Single parent on $18,000 with $2,700 child care.</b> Adjusted income is $18,000 − $500 − $2,700 = $14,800. Their share is $370 a month, and the voucher pays $930.</li>
<li><b>Senior on $14,400.</b> The $550 deduction gives adjusted income of $13,850. Their share is $346 a month.</li>
<li><b>Family of 3 on $29,700 renting $200 above the standard.</b> Their basic share is $730, plus the $200 extra, so they pay $930. That is 38% of adjusted income – under the 40% move-in limit.</li></ul>
<p class="note">Examples use this calculator's own formula with the 2026 amounts. Real amounts also depend on utility allowances and any other deductions your agency uses.</p>
<h2 id="how">How the voucher works (in plain words)</h2>
<p>A Housing Choice Voucher (often called Section 8) helps you rent a home from a private landlord. You pay part of the rent. The local public housing agency (PHA) pays the rest straight to the landlord.</p>
<ul><li><b>Step 1 – adjusted income.</b> Start with yearly income before tax. Take off the deductions above. Divide by 12.</li>
<li><b>Step 2 – your share.</b> Take 30% of adjusted monthly income. Compare it with 10% of gross monthly income. Your share is the higher one.</li>
<li><b>Step 3 – the voucher.</b> The voucher pays the rent (or the payment standard, if that is lower) minus your share.</li>
<li><b>Step 4 – anything above the standard</b> is yours to pay too.</li></ul>
<p>The <b>payment standard</b> is the amount the agency uses for each unit size in your area. It is usually close to the local fair market rent.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Ask for the payment standard first.</b> Then look for homes at or under it.</li>
<li><b>Count utilities.</b> A cheap rent with high bills can push you over the standard.</li>
<li><b>Report income changes.</b> Your share is recalculated when your income changes.</li>
<li><b>Get on several lists.</b> You can apply to more than one agency.</li>
<li><b>Never pay to apply.</b> Applying for a voucher is free.</li></ul>
<h2 id="faq" style="margin-top:22px">Section 8 FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 27 November 2026): <a href="https://www.huduser.gov/portal/sites/default/files/datasets/inflationary-adjustments/CY2026-Revised-Amounts-And-Passbook-Rate.pdf" rel="nofollow">HUD – CY2026 inflation-adjusted amounts</a>; <a href="https://www.huduser.gov/portal/sites/default/files/datasets/inflationary-adjustments/CY2027-Revised-Amounts-And-Passbook-Rate.pdf" rel="nofollow">HUD – CY2027 amounts</a>; <a href="https://www.ecfr.gov/current/title-24/subtitle-A/part-5/subpart-F/section-5.611" rel="nofollow">24 CFR 5.611 – Adjusted income</a>; <a href="https://www.ecfr.gov/current/title-24/subtitle-A/part-5/subpart-F/section-5.628" rel="nofollow">24 CFR 5.628 – Total tenant payment</a>; <a href="https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-982/subpart-K/section-982.508" rel="nofollow">24 CFR 982.508 – Maximum family share at initial occupancy</a>; <a href="https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-982/subpart-E/section-982.201" rel="nofollow">24 CFR 982.201 – Eligibility and targeting</a>; <a href="https://www.hud.gov/topics/housing_choice_voucher_program_section_8" rel="nofollow">HUD – Housing Choice Voucher Program</a>. General information, not legal advice.</p>'''

out=build(P,'Section 8 Rent Calculator 2026 – How Much Rent Will I Pay?',
 'Work out your Section 8 rent share: 30% of adjusted income, 2026 deductions ($500 per dependent, $550 elderly), the 40% move-in rule and examples.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','27 November 2026'),('Sources','HUD, 24 CFR 5 and 982')],
 [('form','Calculator'),('figures','Key rules'),('ex','Examples'),('how','How it works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
