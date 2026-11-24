import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/uk/isa-calculator.html'

calc='''function calc(){const m0=num('m'),m=Math.min(m0,20000/12),r=num('r')/1200,n=Math.round(num('y')*12),b0=num('b');let b=b0;const mark={};for(let i=1;i<=n;i++){b=b*(1+r)+m;if(i%60===0)mark[i/12]=b}const put=b0+m*n;
 const rows=[['Paid in',gbp(put,0)],['Growth',gbp(b-put,0),'pos'],['Yearly contributions',gbp(m*12,0)+' of £20,000']];
 Object.keys(mark).forEach(k=>{if(+k<n/12)rows.push(['Value after '+k+' years',gbp(mark[k],0)])});
 return big('Projected ISA value',gbp(b,0),'after '+(n/12).toLocaleString('en-GB',{maximumFractionDigits:1})+' years · tax-free')+kv(rows)+(m0>20000/12?'<p class="note">Capped at £20,000 a year (£1,666.67 a month), the 2026/27 ISA allowance.</p>':'')+'<p class="note">Assumes a deposit at the end of each month and a steady return, compounded monthly. Stocks and shares can fall as well as rise – the return is not guaranteed.</p>'}'''

def isa(b,m,r,y):
    m=min(m,20000/12);r=r/1200
    for i in range(round(y*12)): b=b*(1+r)+m
    return b
g=lambda x:f"£{x:,.0f}"
rows=[]
for m in (100,250,500,1000):
    rows.append([g(m),g(m*12),g(isa(0,m,3,10)),g(isa(0,m,5,10)),g(isa(0,m,5,20)),g(m*240)])
rows.append(['£1,667 (full £20,000)','£20,000',g(isa(0,20000/12,3,10)),g(isa(0,20000/12,5,10)),g(isa(0,20000/12,5,20)),'£400,000'])
dflt=isa(5000,400,5,15)
print(rows, round(dflt))

fig=[['ISA allowance 2026/27','£20,000','The most you can put into all your ISAs from 6 April 2026 to 5 April 2027. You can split it between cash, stocks and shares, innovative finance and Lifetime ISAs.'],
     ['Cash ISA limit from April 2027','£20,000 (kept)','A cut to £12,000 for under-65s had been planned. Budget 2026 (28 October 2026) reversed it.'],
     ['Lifetime ISA','£4,000 a year + 25% bonus (up to £1,000)','Open at 18–39, pay in until 50. Counts towards the £20,000. Withdrawals for other reasons lose 25%.'],
     ['Junior ISA 2026/27','£9,000 a year','For children under 18. Does not use your own allowance.'],
     ['Personal Savings Allowance','£1,000 basic · £500 higher · £0 additional','Interest you can earn outside an ISA without tax.'],
     ['Dividend allowance','£500 a year','Dividends above this outside an ISA are taxed at 10.75%, 35.75% or 39.35% (2026/27).'],
     ['Capital gains tax-free amount','£3,000 a year','Gains above this outside an ISA can be taxed. Gains inside an ISA are tax-free.'],
     ['Savings tax rates from 2027/28','24% · 44% · 49%','New rates for interest above the allowances, confirmed at Budget 2026.']]

def tax(interest,psa,rate): return max(0,interest-psa)*rate
ex2=[['Basic rate','£30,000','£1,200','£1,000',f"£{tax(1200,1000,.2):,.0f}",f"£{tax(1200,1000,.24):,.0f}"],
     ['Higher rate','£30,000','£1,200','£500',f"£{tax(1200,500,.4):,.0f}",f"£{tax(1200,500,.44):,.0f}"],
     ['Higher rate','£60,000','£2,400','£500',f"£{tax(2400,500,.4):,.0f}",f"£{tax(2400,500,.44):,.0f}"],
     ['Additional rate','£30,000','£1,200','£0',f"£{tax(1200,0,.45):,.0f}",f"£{tax(1200,0,.49):,.0f}"]]

FAQ=[
("How much can I put in an ISA in 2026/27?","£20,000 in total between 6 April 2026 and 5 April 2027. You can put it all in one ISA or split it, for example £15,000 in a cash ISA and £5,000 in a stocks and shares ISA. A Lifetime ISA can take up to £4,000 of it."),
("Is the cash ISA limit still going down to £12,000?","No. A cut to £12,000 for under-65s from April 2027 had been announced, but Budget 2026 on 28 October 2026 reversed it. HMRC says the £20,000 cash ISA limit will be kept from 6 April 2027."),
("How much will £500 a month in an ISA be worth?","After 10 years about £69,871 at 3% a year, or £77,641 at 5% a year. After 20 years at 5% it is about £205,517 – you paid in £120,000 and growth added about £85,517. Returns on shares are not guaranteed."),
("Do I need an ISA if I have the Personal Savings Allowance?","Maybe not for small amounts. A basic-rate taxpayer can earn £1,000 of interest a year tax-free anyway. But with £30,000 at 4%, a higher-rate taxpayer earns £1,200 of interest and pays £280 tax outside an ISA (£308 from 2027/28). Inside an ISA they pay nothing."),
("Can I pay more than £20,000 into ISAs?","No. £20,000 is the most you can pay into all your ISAs in one tax year, and it does not roll over. This calculator caps payments at £20,000 a year (£1,666.67 a month). If you think you have paid in too much, contact your ISA provider."),
("Is the Lifetime ISA worth it?","For a first home or retirement it can be: the government adds 25%, so £4,000 becomes £5,000. But taking money out for anything else costs 25% of what you take out, which is more than the bonus. For a first home over £450,000 the charge is 20%."),
]

art='''<h2 id="figures">ISA rules and allowances 2026/27</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<h2 id="ex">What regular ISA saving could grow to</h2>
<div id="examples">'''+table(['Per month','Per year','10 years at 3%','10 years at 5%','20 years at 5%','Paid in over 20 years'],rows)+'''</div>
<ul><li><b>£250 a month</b> for 10 years at 5% grows to about £38,821. You paid in £30,000.</li>
<li><b>£1,000 a month</b> for 20 years at 5% grows to about £411,034. Growth is more than the £240,000 you paid in.</li>
<li>The calculator's starting example: £5,000 already saved plus £400 a month for 15 years at 5% grows to about £117,484.</li></ul>
<p class="note">Calculated with this page's formula: a deposit at the end of each month and a steady yearly return, compounded monthly. 3% and 5% are example returns, not forecasts.</p>
<h2 id="tax">How much tax an ISA saves on interest</h2>
<p>Outside an ISA, interest above your Personal Savings Allowance is taxed. Inside an ISA it is not. Example: £30,000 earning 4% a year makes £1,200 of interest.</p>
'''+table(['Taxpayer','Savings','Interest at 4%','Tax-free allowance','Tax outside an ISA 2026/27','Tax from 2027/28'],ex2)+'''
<p class="note">Assumes no starting rate for savings (that only helps if your other income is under £17,570). Tax rates on savings interest are 20%/40%/45% in 2026/27 and 24%/44%/49% from 2027/28.</p>
<h2 id="how">How the calculator works</h2>
<p>Each month the calculator adds growth to your balance, then adds your monthly payment. It repeats this for every month.</p>
<ul><li><b>Monthly growth</b> = balance × (yearly return ÷ 12).</li>
<li><b>Paid in</b> = starting balance + monthly payment × number of months.</li>
<li><b>Growth</b> = final value − paid in.</li>
<li><b>Allowance cap</b>: payments over £1,666.67 a month (£20,000 a year) are cut back to that amount.</li></ul>
<p>A <b>cash ISA</b> is like a savings account with tax-free interest. A <b>stocks and shares ISA</b> holds investments such as funds. They can earn more over long periods, but their value can also fall.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Use it or lose it.</b> Unused allowance does not carry over to the next tax year.</li>
<li><b>Transfer, don't withdraw.</b> To move an ISA to a new provider, ask the new provider to transfer it. Taking the money out yourself can lose its ISA status.</li>
<li><b>Check fees.</b> On a stocks and shares ISA, a 1% yearly fee takes a big bite out of a 5% return.</li>
<li><b>Money protection.</b> Cash in a cash ISA is covered by the FSCS up to £120,000 per person, per authorised firm.</li></ul>
<h2 id="faq" style="margin-top:22px">ISA FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 24 November 2026): <a href="https://www.gov.uk/individual-savings-accounts" rel="nofollow">GOV.UK – Individual Savings Accounts</a>; <a href="https://www.gov.uk/lifetime-isa" rel="nofollow">GOV.UK – Lifetime ISA</a>; <a href="https://www.gov.uk/junior-individual-savings-accounts" rel="nofollow">GOV.UK – Junior ISAs</a>; <a href="https://www.gov.uk/government/publications/tax-free-savings-newsletter-24/tax-free-savings-newsletter-24-october-2026" rel="nofollow">HMRC – Tax-free savings newsletter 24 (October 2026)</a>; <a href="https://www.gov.uk/government/publications/budget-2026-overview-of-tax-legislation-and-rates-ootlar/budget-2026-overview-of-tax-legislation-and-rates-ootlar" rel="nofollow">HM Treasury – Budget 2026 overview of tax legislation and rates</a>; <a href="https://www.gov.uk/apply-tax-free-interest-on-savings/how-much-is-tax-free" rel="nofollow">GOV.UK – Tax-free interest on savings</a>; <a href="https://www.gov.uk/tax-on-dividends" rel="nofollow">GOV.UK – Tax on dividends</a>; <a href="https://www.gov.uk/capital-gains-tax/allowances" rel="nofollow">GOV.UK – Capital Gains Tax allowances</a>; <a href="https://www.fscs.org.uk/what-we-cover/banks-building-societies-credit-unions/deposit-limit/" rel="nofollow">FSCS – deposit limit</a>. Not financial advice.</p>'''

out=build(P,'ISA Calculator 2026/27 – Cash & Stocks and Shares ISA Growth (£20,000)',
 'See what your ISA could grow to with monthly payments. 2026/27 £20,000 allowance, cash ISA limit kept at £20,000 from 2027, Lifetime ISA rules and tax saved.',
 art,FAQ,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','24 November 2026'),('Sources','GOV.UK, HMRC, HM Treasury, FSCS')],
 [('form','Calculator'),('figures','ISA allowances 2026/27'),('ex','Growth examples'),('tax','Tax an ISA saves'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
