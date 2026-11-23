import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top

PATH='/uk/shared-ownership-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"£"}</style><label class="f"><span>Full market value</span><div class="money"><input id="v" inputmode="decimal" value="300,000"></div><small>The price of the whole home (100%).</small></label><label class="f"><span>Share you buy (%)</span><input id="s" inputmode="decimal" value="40"><small>Usually 25%–75%; some homes allow 10%.</small></label><label class="f"><span>Deposit (% of your share)</span><input id="dep" inputmode="decimal" value="10"><small>Usually 5%–10% of the share price.</small></label><label class="f"><span>Mortgage rate (%)</span><input id="r" inputmode="decimal" value="5"><small>Example rate only – use the rate your lender or adviser quotes.</small></label><label class="f"><span>Mortgage term (years)</span><input id="t" inputmode="decimal" value="25"></label><label class="f"><span>Rent on unowned share (%/yr)</span><input id="rr" inputmode="decimal" value="2.75"><small>New homes: no more than 3% a year; 2.75% is typical. Check the key information document.</small></label><label class="f"><span>Service charge per month</span><div class="money"><input id="sc" inputmode="decimal" value="120"></div></label></form>'''

calc='''function calc(){const V=num('v'),sp=Math.min(100,Math.max(0,num('s'))),sh=V*sp/100,dep=sh*num('dep')/100,L=Math.max(0,sh-dep),yrs=Math.max(1,num('t')||25),n=Math.round(yrs*12),i=num('r')/1200,m=L>0?(i?L*i/(1-Math.pow(1+i,-n)):L/n):0,rent=(V-sh)*num('rr')/1200,sc=num('sc'),t=m+rent+sc,nx=Math.min(10,100-sp),st=V*nx/100,stR=st*num('rr')/1200;
 const rows=[['Your share ('+sp+'%)',gbp(sh,0)],['Deposit',gbp(dep,0)],['Mortgage ('+gbp(L,0)+' over '+yrs+' yrs)',gbp2(m)],['Rent on the '+(100-sp)+'% you don’t own',gbp2(rent)],['Service charge',gbp2(sc)],['Total per month',gbp2(t),'t']];
 if(nx>0)rows.push(['Buy another '+nx+'% at today’s value',gbp(st,0)],['Rent saved after that',gbp2(stR)+' a month','pos']);
 return big('Monthly cost',gbp(t,0),'Share '+gbp(sh,0))+kv(rows)+'<p class="note">The staircasing price uses today’s full market value. In real life the price is set by a new valuation, so it will be higher if prices have gone up.</p>'}'''

ex=[['£300,000','40%','10% (£12,000)','£631.36','£412.50','£120','<b>£1,163.86</b>'],
    ['£300,000','25%','10% (£7,500)','£394.60','£515.62','£120','<b>£1,030.22</b>'],
    ['£300,000','10%','5% (£1,500)','£166.61','£618.75','£120','<b>£905.36</b>'],
    ['£200,000','40%','5% (£4,000)','£444.29','£275.00','£100','<b>£819.29</b>'],
    ['£400,000','40%','10% (£16,000)','£841.81','£550.00','£150','<b>£1,541.81</b>']]

FAQ=[
("How much is rent on shared ownership?","Rent is a percentage of the value of the share you don’t own. On new homes it can be no more than 3% a year, and 2.75% is typical. On a £300,000 home where you own 40%, you rent the other £180,000: 2.75% of that is £4,950 a year, or £412.50 a month."),
("What is the monthly cost of shared ownership on a £300,000 home?","With a 40% share, a 10% deposit, a 5% mortgage over 25 years, 2.75% rent and a £120 service charge, it comes to about £1,164 a month: £631 mortgage, £413 rent and £120 service charge. With a 35-year mortgage the total drops to about £1,078, but you pay more interest overall."),
("How does staircasing work?","Staircasing means buying more of your home. You can usually buy 10% or more at any time, at the home’s value on the day you buy. On a home now worth £300,000, another 10% costs £30,000 and cuts rent at 2.75% by £68.75 a month. Homes bought from April 2021 may also let you buy 1% a year for the first 15 years, priced using the House Price Index, with no admin fee."),
("Who can buy a shared ownership home?","Your household income must be £80,000 a year or less (£90,000 in London), and you must be unable to afford a suitable home on the open market. You also need to be a first-time buyer, a former owner who can’t afford to buy now, a new household, or an existing shared owner moving home."),
("Do I pay stamp duty on shared ownership?","You can choose. With a market value election you pay once, on the full market value, and never again when you staircase. If you don’t elect, you pay only if your share price is above the threshold, and nothing more until you own over 80%. First-time buyers who elect pay 0% on a home worth up to £300,000."),
("Is shared ownership worth it?","It lowers the deposit: 10% of a 40% share of £300,000 is £12,000, against £30,000 for 10% of the whole home. But you pay rent that usually rises every year, a service charge, and all repairs after any initial repair period. Buying more shares later costs more if prices rise. Compare the total monthly cost with renting and with buying outright before you decide."),
]

faq_block='<h2 id="faq" style="margin-top:22px">Shared ownership questions</h2>'+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)

art='''<h2 id="figures">Shared ownership rules in 2026 (England)</h2>
'''+table(['Rule','2026 figure'],[
 ['Share you buy at the start','Usually 25%–75%; 10% on some homes'],
 ['Deposit','Usually 5%–10% of the share you buy'],
 ['Rent on the share you don’t own (new homes)','No more than 3% of its value a year; 2.75% is typical'],
 ['Household income limit','£80,000 a year, or £90,000 in London'],
 ['Buying more (staircasing)','Usually 10% or more at any time; some newer leases 5%'],
 ['1% staircasing','Homes bought from 1 April 2021 may allow 1% a year for the first 15 years'],
 ['Staircasing admin fee (5% or more)','Set by the landlord, about £150–£500; none for 1% shares'],
 ['Initial repair period','Usually 10 years, up to £500 a year for some repairs'],
 ['Lease length','Homes funded 2021–2026: at least 990 years'],
 ['Rent rises (leases from 12 Oct 2023)','Usually CPI + 1% or RPI + up to 0.5% a year, as the lease says'],
 ['Stamp duty first-time buyer rates','0% up to £300,000; 5% from £300,001 to £500,000'],
 ['Bank of England Bank Rate','4% (from 5 November 2026)']])+'''
<p class="note">Figures from GOV.UK, the Homes England Capital Funding Guide, HMRC and the Bank of England. Your own lease and key information document always come first. Bank Rate is not your mortgage rate – lenders set their own.</p>

<h2 id="ex">Shared ownership monthly costs: examples</h2>
<p>All examples use a 5% mortgage rate over 25 years and rent of 2.75% a year. The 5% rate is only an example.</p>
<div id="examples">'''+table(['Home value','Share','Deposit','Mortgage','Rent','Service charge','Total a month'],ex)+'''</div>
<ul><li><b>£300,000 home, 40% share:</b> your share costs £120,000. You put down £12,000 and borrow £108,000. Rent on the other £180,000 is £412.50 a month. Total: about £1,164.</li>
<li><b>Smaller share, more rent:</b> with 25% instead of 40%, the mortgage falls by £237 but the rent rises by £103.</li>
<li><b>Longer mortgage:</b> the same 40% share over 35 years costs about £1,078 a month (mortgage £545.06), but you pay interest for 10 more years.</li>
<li><b>Staircasing:</b> on a home worth £300,000, buying another 10% costs £30,000 and cuts the rent by £68.75 a month.</li></ul>

<h2 id="how">How shared ownership works</h2>
<p>You buy part of a home – your <b>share</b> – usually with a mortgage. A housing association or other landlord owns the rest. You pay <b>rent</b> on the part they own.</p>
<p>Take a £300,000 home. You buy 40%, which is £120,000. The landlord owns 60%, worth £180,000. At 2.75% a year, the rent is £4,950 a year, or £412.50 a month. Then add your mortgage and the service charge.</p>
<p>The calculator does this for you:</p>
<ul><li><b>Your share</b> = full value × share %</li>
<li><b>Mortgage</b> = share − deposit, paid back monthly over the term you choose</li>
<li><b>Rent a month</b> = (full value − your share) × rent % ÷ 12</li>
<li><b>Total</b> = mortgage + rent + service charge</li></ul>
<h3>Staircasing: buying more of your home</h3>
<p><b>Staircasing</b> means buying extra shares. Each time, you own more and pay less rent. The price depends on what your home is worth when you buy, not what you first paid. If a £300,000 home is now worth £330,000, another 10% costs £33,000, not £30,000.</p>
<p>For shares of 5% or more, a surveyor registered with RICS (the Royal Institution of Chartered Surveyors) values the home. You must buy within 3 months of that valuation. For 1% shares, the landlord uses the House Price Index (an official measure of how house prices change) instead.</p>
<h3>Stamp duty on shared ownership</h3>
<p>Stamp Duty Land Tax (SDLT) is a tax on buying property in England and Northern Ireland. With shared ownership you choose one of two ways:</p>
<ul><li><b>Market value election:</b> pay once on the full value of the home. GOV.UK’s example: a 50% share of a £280,000 home costs £4,000 in SDLT (0% on £125,000, 2% on the next £125,000, 5% on £30,000). You pay nothing more when you staircase. First-time buyers can use first-time buyer rates: 0% on a home worth up to £300,000.</li>
<li><b>Paying in stages:</b> pay only if your share price is above the threshold. You may also owe 1% on the rent if its value over the lease is above the threshold. You then pay nothing more until you own more than 80%.</li></ul>

<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Rent goes up every year.</b> It is usually reviewed once a year and can rise but not fall. On a newer lease with CPI + 1%, CPI of 2.1% means a 3.1% rise.</li>
<li><b>Don’t forget repairs.</b> After any initial repair period ends, all repairs are your job, even if you own only 25%.</li>
<li><b>Check the service charge.</b> Flats often have high and rising service charges. Ask for a breakdown.</li>
<li><b>Staircasing gets dearer as prices rise.</b> Use the calculator’s “buy another 10%” line as a starting point only.</li>
<li><b>1% shares can’t be saved up.</b> If you skip a year, you can’t buy 2% the next year.</li>
<li><b>A smaller share isn’t always cheaper each month.</b> Less mortgage means more rent. Try 25%, 40% and 50% in the calculator.</li></ul>

'''+faq_block+'''
<p class="note">Sources (checked 23 Nov 2026): <a href="https://www.gov.uk/shared-ownership-scheme" rel="nofollow">GOV.UK – Shared ownership homes</a>; <a href="https://www.gov.uk/shared-ownership-scheme/who-can-apply" rel="nofollow">GOV.UK – Who can apply</a>; <a href="https://www.gov.uk/shared-ownership-scheme/paying-rent" rel="nofollow">GOV.UK – Paying rent</a>; <a href="https://www.gov.uk/shared-ownership-scheme/buying-more-shares-staircasing" rel="nofollow">GOV.UK – Buying more shares</a>; <a href="https://www.gov.uk/shared-ownership-scheme/repairs-home-improvements" rel="nofollow">GOV.UK – Repairs</a>; <a href="https://www.gov.uk/guidance/capital-funding-guide/1-shared-ownership" rel="nofollow">Homes England – Capital Funding Guide: Shared Ownership</a>; <a href="https://www.gov.uk/stamp-duty-land-tax/shared-ownership-property" rel="nofollow">GOV.UK – SDLT: shared ownership property</a>; <a href="https://www.gov.uk/stamp-duty-land-tax/residential-property-rates" rel="nofollow">GOV.UK – SDLT residential rates</a>; <a href="https://www.gov.uk/hmrc-internal-manuals/stamp-duty-land-tax-manual/sdltm29880" rel="nofollow">HMRC – SDLTM29880</a>; <a href="https://www.bankofengland.co.uk/monetary-policy/the-interest-rate-bank-rate" rel="nofollow">Bank of England – Bank Rate</a>. Examples use this calculator’s own formula.</p>'''

out=build(PATH,'Shared Ownership Calculator 2026 – Rent, Mortgage & Staircasing',
 'Shared ownership costs for 2026: mortgage on your share, rent on the rest (max 3%, typically 2.75%), service charge, staircasing price and stamp duty options.',
 art,FAQ,form=form,calc=calc)
add_top(out,[("By","Hong Life Calculators"),("Checked","23 November 2026"),("Sources","GOV.UK, Homes England, HMRC, Bank of England")],
 [("form","Calculator"),("figures","2026 rules"),("ex","Monthly cost examples"),("how","How it works"),("tips","Tips and mistakes"),("faq","Questions")],
 'On this page',("#examples","en"))
print(out)
