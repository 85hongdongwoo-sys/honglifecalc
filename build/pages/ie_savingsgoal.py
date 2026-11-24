import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/ie/savings-goal-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Savings goal (€)</span><input id="T" inputmode="decimal" value="18,000"></label><label class="f"><span>Already saved (€)</span><input id="C" inputmode="decimal" value="1,800"></label><label class="f"><span>Years to reach the goal</span><input id="y" inputmode="decimal" value="3"><small>Use decimals for months: 18 months = 1.5.</small></label><label class="f"><span>Interest rate on savings (% a year, before tax)</span><input id="r" inputmode="decimal" value="2.5"><small>An example rate – use the rate your own account pays. Enter 0 for no interest.</small></label><label class="f"><span>Take off DIRT (33%)?</span><select id="dirt"><option value="1" selected>Yes – bank deposit account</option><option value="0">No – tax-free (e.g. State Savings)</option></select></label></form>'''

calc='''function calc(){const T=num('T'),C=num('C'),tx=$('dirt')&&$('dirt').value==='1',rn=num('r')*(tx?0.67:1),i=rn/1200,n=Math.round(num('y')*12);
 const nt='<p class="note">Assumes a deposit at the end of each month and interest added monthly at a steady rate'+(tx?', with 33% DIRT taken off the interest (so '+num('r').toLocaleString('en-IE')+'% becomes about '+rn.toLocaleString('en-IE',{maximumFractionDigits:2})+'% after tax)':', with no tax taken off')+'.</p>';
 if(n<1)return big(O.need,'–','Enter a time of at least 1 month (0.08 years)');
 const g=Math.pow(1+i,n),grow=C*g;
 if(grow>=T)return big('You are already on track',mf(0,0),O.per)+kv([['What you have saved grows to',mf(grow)],['Interest earned'+(tx?' after DIRT':''),mf(grow-C,0),'pos'],['Months',String(n)]])+nt;
 const need=i?(T-grow)*i/(g-1):(T-C)/n,dep=need*n;
 return big(O.need,mf(need),O.per)+kv([['About per week',mf(need*12/52)],[O.tot,mf(dep)],['Already saved',mf(C,0)],[O.int+(tx?' (after DIRT)':''),mf(Math.max(0,T-C-dep),0),'pos'],['Months',String(n)]])+nt}'''

def need(T,C,y,r):
    i=r/1200;n=round(y*12);g=(1+i)**n
    if C*g>=T: return 0
    return (T-C*g)*i/(g-1) if i else (T-C)/n
e=lambda x:f"€{x:,.0f}"
rows=[]
for T,y,lab in [(5000,1,'€5,000'),(10000,2,'€10,000'),(20000,3,'€20,000'),(30000,5,'€30,000 (house deposit)')]:
    a0=need(T,0,y,0);a1=need(T,0,y,2.5);a2=need(T,0,y,2.5*0.67)
    rows.append([lab,f"{y} year{'s' if y>1 else ''}",e(a0),e(a1),e(a2),e(T-a2*y*12)])
dflt=need(18000,1800,3,2.5*0.67); dflt_gross=need(18000,1800,3,2.5)
print(rows, round(dflt,2), round(dflt_gross,2))

fig=[['DIRT (tax on deposit interest)','33%','Your bank takes 33% of the interest before paying it. €100 of interest becomes €67.'],
     ['Deposit Guarantee Scheme','Up to €100,000 per person, per bank','If an Irish bank, building society or credit union fails, your deposits are paid back up to this amount.'],
     ['ECB deposit facility rate','2.50% (since 16 September 2026, kept on 29 October 2026)','The European Central Bank\'s key rate. Bank savings rates often follow it.'],
     ['State Savings 3-Year Savings Bond','6% total over 3 years (1.96% AER), tax-free','Rates for new issues from 30 August 2026.'],
     ['State Savings 5-Year Savings Certificate','12% total over 5 years (2.29% AER), tax-free',''],
     ['State Savings 10-Year National Solidarity Bond','30% total over 10 years (2.66% AER), tax-free',''],
     ['Inflation (CSO, October 2026)','4.3% a year (CPI)','Prices rose 4.3% in a year, so money that earns less than that buys a little less over time.']]

FAQ=[
("How much do I need to save each month in Ireland?","Divide what you still need by the number of months, then take off a little for interest. For €10,000 in 2 years from zero: €10,000 ÷ 24 = €417 a month with no interest, or €410 a month at 2.5% after 33% DIRT."),
("How much is DIRT on savings in Ireland?","DIRT is 33% of the interest. The bank takes it off before paying you. So 2.5% interest is about 1.68% after tax, and €300 of interest leaves you €201."),
("Are State Savings tax-free?","Yes. State Savings bonds and certificates from An Post and the NTMA are tax-free and 100% State-protected. For new issues from 30 August 2026, the 3-year bond pays 6% in total (1.96% AER) and the 5-year certificate 12% (2.29% AER). You must keep the money in for the full term to get the full return."),
("Is my money safe in an Irish bank?","Deposits are protected up to €100,000 per person, per bank, by the Deposit Guarantee Scheme run by the Central Bank of Ireland. A joint account counts €100,000 for each holder."),
("How much should I keep in an emergency fund?","The Competition and Consumer Protection Commission (CCPC) says to aim for at least three to six months' income, and that three months' income is a good starting point. Build that before saving for other goals."),
("Does inflation matter for my savings goal?","Yes. Prices rose 4.3% in the year to October 2026 (CSO). If your goal is a price that rises, such as a car or a house deposit, aim a little higher than today's price."),
]

art='''<h2 id="figures">Official Irish figures for savers (November 2026)</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<p class="note">We don't list bank savings rates. They change often and differ by bank. Use the rate your own account pays.</p>
<h2 id="ex">How much to save each month: examples</h2>
<div id="examples">'''+table(['Goal','Time','Per month, no interest','Per month at 2.5% (no tax)','Per month at 2.5% after DIRT','Interest kept after DIRT'],rows)+'''</div>
<ul><li>To save <b>€5,000 in 1 year</b> you need about €417 a month. Interest at 2.5% after DIRT only saves you about €3 a month.</li>
<li>To save <b>€20,000 in 3 years</b> you need €556 a month with no interest, or €542 at 2.5% after DIRT.</li>
<li>For a <b>€30,000 house deposit in 5 years</b> you need €500 a month with no interest, or €480 at 2.5% after DIRT.</li></ul>
<p class="note">All examples start from €0 and use this calculator's formula. 2.5% is an example rate, not a bank quote. "After DIRT" means 2.5% × 0.67 = 1.675% a year.</p>
<h2 id="how">How the calculator works</h2>
<p>Example first. You want €18,000 in 3 years. You already have €1,800, and your bank pays 2.5% a year. After 33% DIRT that is about 1.68%. Saving <b>€437 a month</b> gets you there. If the interest were tax-free, you would need about €430 a month.</p>
<ul><li><b>DIRT</b> (Deposit Interest Retention Tax) is the tax on bank interest. The calculator takes 33% off the rate if you choose "Yes".</li>
<li><b>Monthly rate</b> = yearly rate ÷ 12.</li>
<li><b>Compound interest</b> means you also earn interest on your interest. The calculator adds it every month.</li>
<li><b>Monthly saving</b> = (goal − what your savings grow to) × i ÷ ((1 + i)<sup>n</sup> − 1). Here i is the monthly rate and n is the number of months.</li></ul>
<p>With no interest it is simply (goal − already saved) ÷ months.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Pay yourself first.</b> Set up a standing order for payday.</li>
<li><b>Compare after-tax rates.</b> 2.5% from a bank is about 1.68% after DIRT. A tax-free State Savings product with a lower headline rate can be better.</li>
<li><b>Check lock-in rules.</b> Fixed-term accounts and State Savings pay less if you cash in early.</li>
<li><b>Don't put over €100,000 in one bank</b> if you want it all covered by the Deposit Guarantee Scheme.</li>
<li><b>Re-check your rate</b> after ECB rate changes. Banks often follow.</li></ul>
<h2 id="faq" style="margin-top:22px">Savings goal FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 24 November 2026): <a href="https://www.revenue.ie/en/additional-incomes/dirt/what-dirt-rate-is-applicable.aspx" rel="nofollow">Revenue – DIRT rate</a>; <a href="https://www.citizensinformation.ie/en/money-and-tax/tax/tax-on-savings-and-investments/deposit-interest-retention-tax/" rel="nofollow">Citizens Information – DIRT</a>; <a href="https://www.centralbank.ie/consumer-hub/deposit-guarantee-scheme" rel="nofollow">Central Bank of Ireland – Deposit Guarantee Scheme</a>; <a href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html" rel="nofollow">ECB – key interest rates</a>; <a href="https://www.statesavings.ie/our-products" rel="nofollow">State Savings – products and rates</a>; <a href="https://www.cso.ie/en/releasesandpublications/ep/p-cpi/consumerpriceindexoctober2026/" rel="nofollow">CSO – Consumer Price Index October 2026</a>; <a href="https://www.ccpc.ie/manage-your-money/planning-for-the-future/moving-in-with-your-partner" rel="nofollow">CCPC – emergency fund guidance</a>. Examples use this calculator's own formula. General information, not financial advice.</p>'''

out=build(P,'Savings Goal Calculator Ireland 2026 – How Much to Save a Month',
 'See how much to save each month to reach a savings goal in Ireland, with interest before or after 33% DIRT. Examples, State Savings rates and deposit protection.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','24 November 2026'),('Sources','Revenue, Central Bank, ECB, State Savings, CSO')],
 [('form','Calculator'),('figures','Official figures'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
