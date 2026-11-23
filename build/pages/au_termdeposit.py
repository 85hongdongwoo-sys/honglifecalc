import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top

PATH='/au/term-deposit-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>Deposit</span><div class="money"><input id="a" inputmode="decimal" value="50,000"></div></label><label class="f"><span>Interest rate (% p.a.)</span><input id="r" inputmode="decimal" value="4.5"><small>Example rate only – enter the rate your bank offers you.</small></label><label class="f"><span>Term (months)</span><input id="m" inputmode="decimal" value="12"></label><label class="f"><span>Interest paid</span><select id="c"><option value="0" selected>At maturity</option><option value="-12">Monthly, paid to your account</option><option value="12">Monthly, reinvested</option><option value="1">Annually, reinvested</option></select></label><label class="f"><span>Your taxable income (without this interest)</span><div class="money"><input id="s" inputmode="decimal" value="85,000"></div><small>Used to work out the tax on the interest at 2026-27 resident rates plus the 2% Medicare levy.</small></label></form>'''

calc='''function calc(){const a=num('a'),r=num('r')/100,m=Math.max(0,num('m')),c=+$('c').value||0,s=num('s'),v=c>0?a*Math.pow(1+r/c,c*m/12):a*(1+r*m/12),int=v-a,y=Math.max(1,m/12),t=(itx(s+int/y)-itx(s))*y,er=int>0?t/int:0;
 const rows=[['Tax on interest (about '+pc(er)+')',aud(-t,0),'neg'],['After-tax interest',aud(int-t,0),'pos']];
 if(c<0)rows.unshift(['Paid to you each month',aud2(a*r/12)]);
 if(m>0&&a>0)rows.push(['Yearly return before tax',pc(Math.pow(v/a,12/m)-1,2)]);
 return big('Interest earned',aud2(int),c<0?'your $'+Math.round(a).toLocaleString('en-AU')+' is returned at maturity':'balance at maturity '+aud(v,0))+kv(rows)+(m>12?'<p class="note">For terms over 12 months the tax is worked out as if the interest were spread evenly over the years.</p>':'')}'''

ex=[['$10,000','12 months','$450.00','$144','$306'],
    ['$50,000','6 months','$1,125.00','$360','$765'],
    ['$50,000','12 months','$2,250.00','$720','$1,530'],
    ['$100,000','12 months','$4,500.00','$1,440','$3,060'],
    ['$250,000','12 months','$11,250.00','$3,600','$7,650']]

taxrows=[['$20,000','$245','$4,255'],['$40,000','$990','$3,510'],['$85,000','$1,440','$3,060'],['$150,000','$1,755','$2,745'],['$200,000','$2,115','$2,385']]

FAQ=[
("How much interest will I earn on $50,000 in a term deposit?","At an example rate of 4.5% a year, $50,000 for 12 months earns $2,250 paid at maturity. For 6 months it earns $1,125. If your taxable income is $85,000, tax and Medicare levy take about 32%, leaving $1,530 from the 12-month deposit."),
("How much interest on a $100,000 term deposit?","At an example rate of 4.5% a year, $100,000 earns $4,500 over 12 months. After tax at 32% (30% plus the 2% Medicare levy) you keep $3,060. Over 3 years with interest added each year, it earns $14,116.61 before tax."),
("Is term deposit interest taxed?","Yes. Interest is part of your taxable income and is taxed at your marginal rate (the rate on your last dollar of income) plus the 2% Medicare levy. For 2026-27 that is 32% on income between $45,001 and $135,000. Declare it in the year it is credited or paid to you – for a term deposit, usually the year it matures."),
("Is it better to get interest monthly or at maturity?","If you take monthly interest out, you earn the same as interest at maturity: $50,000 at 4.5% pays $187.50 a month, or $2,250 a year. If the monthly interest stays in and earns interest too, you get a bit more: $2,296.99. Banks often pay a lower rate for monthly interest, so compare the dollar amounts."),
("What happens if I don’t give my bank my tax file number?","The bank must withhold tax from your interest at the top rate plus the Medicare levy – 45% + 2% = 47% – once the interest is $120 or more a year. You get it back as a credit when you lodge your tax return, but your money is tied up until then."),
("Is my term deposit safe if the bank fails?","Deposits with an Australian bank, building society or credit union (an ADI – authorised deposit-taking institution) are protected by the government’s Financial Claims Scheme up to $250,000 per account holder per ADI. Term deposits are covered. Above $250,000, you can split your money across different ADIs."),
]

faq_block='<h2 id="faq" style="margin-top:22px">Term deposit questions</h2>'+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)

art='''<h2 id="figures">Official figures for 2026-27</h2>
'''+table(['Item','Figure'],[
 ['RBA cash rate target','4.85% (raised from 4.60% on 3 November 2026)'],
 ['Financial Claims Scheme','Up to $250,000 per account holder per ADI; term deposits covered'],
 ['Tax on interest','Your marginal rate, in the year interest is credited or paid'],
 ['Income tax rates 2026-27 (residents)','0% to $18,200; 15% to $45,000; 30% to $135,000; 37% to $190,000; 45% above'],
 ['Medicare levy','2% (reduced for low incomes)'],
 ['Low income tax offset','Up to $700, phasing out by $66,667'],
 ['No TFN given to your bank','Tax withheld at 47% (top rate 45% + Medicare levy 2%) if interest is $120+ a year']])+'''
<p class="note">The cash rate is the Reserve Bank’s target for overnight lending between banks. Banks set their own term deposit rates, which can be higher or lower. The Medicare levy low-income threshold used ($28,011 for singles) is the latest ATO figure, for 2025-26; the 2026-27 figure is not yet published.</p>

<h2 id="ex">Term deposit interest: examples</h2>
<p>These examples use an <b>example rate of 4.5% a year</b>, interest paid at maturity, and a taxable income of $85,000 (tax 30% + 2% Medicare levy = 32%). They are not bank offers.</p>
<div id="examples">'''+table(['Deposit','Term','Interest','Tax','You keep'],ex)+'''</div>
<ul><li>$50,000 for 12 months at 4.5% earns <b>$2,250</b>. After tax you keep <b>$1,530</b>.</li>
<li>Half the time means half the interest: 6 months earns $1,125.</li>
<li>$100,000 left for 3 years, with interest added each year, earns <b>$14,116.61</b> before tax.</li></ul>
<h3>Tax on $4,500 of interest at different incomes</h3>
'''+table(['Taxable income','Tax and Medicare levy','You keep'],taxrows)+'''
<p class="note">Interest of $4,500 = $100,000 at 4.5% for 12 months. At $40,000 the rate is about 22% because the low income tax offset shrinks as income rises.</p>

<h2 id="how">How term deposit interest works</h2>
<p>A <b>term deposit</b> locks your money with a bank for a set time (the term) at a fixed interest rate. Here is a real example first: $50,000 at 4.5% a year for 6 months earns $50,000 × 4.5% × 6 ÷ 12 = $1,125.</p>
<ul><li><b>Interest at maturity:</b> deposit × rate × months ÷ 12. You get it all at the end.</li>
<li><b>Monthly, paid to you:</b> the same total, paid in 12 parts. $50,000 at 4.5% pays $187.50 a month.</li>
<li><b>Reinvested (compounding):</b> each payment is added to the balance and also earns interest. Monthly compounding turns 4.5% into $2,296.99 on $50,000 in a year.</li></ul>
<p><b>Tax:</b> interest is added to your other income. The calculator works out your tax with and without the interest, so the “about %” figure is the real extra tax, including the Medicare levy and any change to the low income tax offset.</p>

<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Watch the rollover.</b> Many term deposits renew automatically at maturity, sometimes at a lower rate. Set a reminder a week before.</li>
<li><b>Breaking early costs you.</b> Banks usually cut the interest if you withdraw before the end and may ask for notice. Only lock away money you won’t need.</li>
<li><b>Give your TFN.</b> Otherwise 47% may be withheld from interest of $120 or more a year.</li>
<li><b>Stay under $250,000 per bank.</b> The Financial Claims Scheme limit is per account holder per ADI, not per account. Some brands share one banking licence, so check APRA’s list.</li>
<li><b>Compare dollars, not just rates.</b> A higher rate for 6 months can earn less than a slightly lower rate for 12 months.</li>
<li><b>Don’t forget the tax year.</b> A deposit maturing on 1 July instead of 30 June moves the interest into the next income year.</li></ul>

'''+faq_block+'''
<p class="note">Sources (checked 23 November 2026): <a href="https://www.rba.gov.au/media-releases/2026/mr-26-30.html" rel="nofollow">RBA – Monetary Policy Decision, 3 November 2026</a>; <a href="https://www.apra.gov.au/about-financial-claims-scheme" rel="nofollow">APRA – Financial Claims Scheme</a>; <a href="https://www.apra.gov.au/types-accounts-covered-under-financial-claims-scheme" rel="nofollow">APRA – Accounts covered by the FCS</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents" rel="nofollow">ATO – Tax rates for Australian residents</a>; <a href="https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners" rel="nofollow">ATO – Medicare levy reduction for low-income earners</a>; <a href="https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/tax-offsets/low-income-tax-offset" rel="nofollow">ATO – Low income tax offset</a>; <a href="https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/income-you-must-declare/investment-income" rel="nofollow">ATO – Investment income</a>; <a href="https://www.ato.gov.au/forms-and-instructions/tfn-and-abn-information-for-savings-accounts-and-investments" rel="nofollow">ATO – TFN and ABN information for savings accounts</a>; <a href="https://www.ato.gov.au/businesses-and-organisations/hiring-and-paying-your-workers/payg-withholding/payments-you-need-to-withhold-from/withholding-from-investment-income" rel="nofollow">ATO – Withholding from investment income</a>. Interest rates in the examples are examples only.</p>'''

out=build(PATH,'Term Deposit Calculator Australia 2026-27 – Interest & Tax',
 'Work out term deposit interest on $50,000 or $100,000, monthly or at maturity, and what you keep after 2026-27 tax and Medicare levy. FCS $250,000 cover explained.',
 art,FAQ,form=form,calc=calc)
add_top(out,[("By","Hong Life Calculators"),("Checked","23 November 2026"),("Sources","RBA, APRA, ATO")],
 [("form","Calculator"),("figures","2026-27 figures"),("ex","Interest examples"),("how","How it works"),("tips","Tips and mistakes"),("faq","Questions")],
 'On this page',("#examples","en"))
print(out)
