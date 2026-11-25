import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/ca/gic-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>Deposit</span><div class="money"><input id="a" inputmode="decimal" value="20,000"></div></label><label class="f"><span>Interest rate (%)</span><input id="r" inputmode="decimal" value="3.5"><small>An example rate. Enter the rate your bank quotes.</small></label><label class="f"><span>Term (years)</span><input id="y" inputmode="decimal" value="3"><small>Use decimals for months: 18 months = 1.5.</small></label><label class="f"><span>Compounding</span><select id="cp"><option value="1" selected>Annually</option><option value="2">Semi-annually</option><option value="12">Monthly</option><option value="0">Simple interest (paid out yearly)</option></select></label><label class="f"><span>Account</span><select id="ac"><option value="n" selected>Non-registered (taxable)</option><option value="t">TFSA / RRSP / FHSA (no tax now)</option></select></label><label class="f"><span>Your taxable income</span><div class="money"><input id="i" inputmode="decimal" value="70,000"></div></label><label class="f"><span>Province or territory</span><select id="pv"><option value="AB">Alberta</option><option value="BC">British Columbia</option><option value="MB">Manitoba</option><option value="NB">New Brunswick</option><option value="NL">Newfoundland and Labrador</option><option value="NT">Northwest Territories</option><option value="NS">Nova Scotia</option><option value="NU">Nunavut</option><option value="ON" selected>Ontario</option><option value="PE">Prince Edward Island</option><option value="QC">Quebec</option><option value="SK">Saskatchewan</option><option value="YT">Yukon</option></select></label></form>'''

calc='''function calc(){const a=num('a'),r=num('r')/100,y=num('y'),cp=+$('cp').value;
 if(!(a>0)||!(y>0))return big('Value at maturity','–','Enter a deposit and a term above 0');
 const val=t=>cp?a*Math.pow(1+r/cp,cp*t):a*(1+r*t),v=val(y),int=v-a,c=$('pv').value,inc=num('i'),sh=$('ac').value!=='n';
 let tax=0;if(!sh)for(let k=0;k<Math.ceil(y);k++){const yi=val(Math.min(k+1,y))-val(k);tax+=itax(inc+yi,c).tot-itax(inc,c).tot}
 const m=int>0?tax/int:0,nt='<p class="note">'+(sh?'In a TFSA or a home withdrawal from an FHSA, interest is never taxed. In an RRSP it is taxed only when you take money out.':'Interest in a regular account is taxed every year as it builds up, even if the GIC pays it only at maturity. Tax uses 2026 federal and provincial rates on top of your other income.')+'</p>';
 return big('Value at maturity',cad2(v),'interest '+cad2(int))+kv([['Interest in the first year',cad2(val(Math.min(1,y))-a)],['Tax on interest ('+pc(m)+')',cad(-tax,0),'neg'],['After-tax interest',cad(int-tax,0),'pos'],['After-tax yearly return',pc(Math.pow((a+int-tax)/a,1/y)-1,2)]])+nt}'''

def val(a,r,y,cp): return a*(1+r/cp)**(cp*y) if cp else a*(1+r*y)
for args in [(10000,.03,1,1),(20000,.035,3,1),(25000,.03,2,12),(25000,.03,2,0),(50000,.0325,5,1),(10000,.035,5,2)]:
    print(args, round(val(*args),2), round(val(*args)-args[0],2))

fig=[['Bank of Canada policy rate','2.5% (raised from 2.25% on 28 October 2026)','The Bank\'s main interest rate. GIC rates often move after it changes. The Bank Rate is 2.75% and the deposit rate 2.45%.'],
     ['Next Bank of Canada decision','9 December 2026','The next scheduled announcement of the overnight rate target.'],
     ['CDIC deposit insurance','Up to $100,000 per insured category, per member bank','Principal and interest together. If your bank fails, your GIC is paid back up to this amount. GICs and other term deposits are eligible, with no limit on the term.'],
     ['Separate CDIC categories','One name · joint · TFSA · RRSP · RRIF · FHSA · RDSP · RESP · trust','Each category is insured on its own, so one person can have more than $100,000 covered at one bank.'],
     ['Tax on GIC interest (regular account)','Taxed every year at your marginal rate','You report interest as it builds up each year, not only when it is paid. Banks send a T5 slip.'],
     ['Tax in a TFSA','None','Interest on a GIC inside a TFSA is tax-free.'],
     ['FHSA limit','$8,000 a year, $40,000 for life','A GIC can sit inside an FHSA. Money taken out for a first home is tax-free.'],
     ['Federal tax rates 2026','14% up to $58,523 · 20.5% · 26% · 29% · 33% over $258,482','Add your province\'s rate to get the rate on your interest. 20.5% applies from $58,523.01, 26% from $117,045.01, 29% from $181,440.01.']]

ex=[['$10,000','3% · 1 year · annual','Regular, Ontario, $70,000','$300.00','$89','$211'],
    ['$20,000','3.5% · 3 years · annual','Regular, Ontario, $70,000','$2,174.36','$645','$1,530'],
    ['$25,000','3% · 2 years · monthly','TFSA','$1,543.93','$0','$1,544'],
    ['$50,000','3.25% · 5 years · annual','Regular, Alberta, $60,000','$8,670.57','$2,525','$6,146']]

FAQ=[
("How much interest will $10,000 earn in a GIC?","At 3% for 1 year it earns $300. At 3.5% for 5 years with yearly compounding it earns about $1,877. In a regular account you pay tax on that interest; in a TFSA you don't."),
("How much does $20,000 earn in a 3-year GIC at 3.5%?","$2,174.36 with yearly compounding, so you get back $22,174.36. In Ontario at $70,000 income, about $645 of that goes to tax, leaving about $1,530."),
("Is GIC interest taxable in Canada?","Yes, in a regular (non-registered) account. It is taxed as income at your full marginal rate, every year as it builds up, even if the GIC pays only at maturity. In a TFSA it is tax-free. In an RRSP it is taxed only when you withdraw."),
("Are GICs insured by CDIC?","GICs and other term deposits at CDIC member banks are eligible, covered up to $100,000 of principal and interest per insured category at each bank, with no limit on the term. Deposits in one name, joint deposits, and TFSA, RRSP, RRIF, FHSA, RDSP, RESP and trust deposits are each a separate category, so you can be covered for more than $100,000 at one bank. Credit union GICs are covered by provincial insurers instead."),
("What is the difference between annual and monthly compounding?","Compounding means you earn interest on your interest. Monthly adds interest 12 times a year, so it earns a little more. $25,000 at 3% for 2 years earns $1,543.93 monthly, versus $1,500 with simple interest paid out each year."),
("Why did GIC rates change in 2026?","GIC rates follow the Bank of Canada. On 28 October 2026 it raised its policy rate by 25 basis points (a quarter of a percentage point) to 2.5%, from 2.25%. The next decision is on 9 December 2026. Banks set their own GIC rates, so compare offers."),
]

art='''<h2 id="figures">GIC figures for 2026</h2>
<p>A <b>GIC</b> (Guaranteed Investment Certificate) is a deposit you lock in at a bank for a set time. In return you get a fixed interest rate, and your money is guaranteed.</p>
'''+table(['Item','Figure','What it means'],fig)+'''
<p class="note">We don't list bank GIC rates. They change often and differ by bank and term. Use the rate you are offered.</p>
<h2 id="ex">GIC interest examples</h2>
<div id="examples">'''+table(['Deposit','Rate · term · compounding','Account','Interest','Tax','Interest after tax'],ex)+'''</div>
<ul><li><b>$10,000 at 3% for 1 year</b> earns $300. In a regular account in Ontario at $70,000 income you keep about $211.</li>
<li><b>$20,000 at 3.5% for 3 years</b> grows to $22,174.36. After tax you keep about $1,530, which is a 2.49% yearly return.</li>
<li><b>$25,000 at 3% for 2 years in a TFSA</b> earns $1,543.93 with monthly compounding, and none of it is taxed.</li>
<li><b>$50,000 at 3.25% for 5 years</b> in Alberta at $60,000 income earns $8,670.57; about $2,525 goes to tax, because part of the interest falls into the next Alberta tax bracket.</li></ul>
<p class="note">Examples use this calculator's own formula. The tax amounts are what this page's own 2026 tax engine works out from the CRA federal brackets above plus each province's own brackets, not figures published province by province. The interest rates are examples, not bank quotes.</p>
<h2 id="how">How the GIC calculator works</h2>
<p>Example first. You put $20,000 in a 3-year GIC at 3.5%, compounded once a year. After year 1 you have $20,700. After year 2, $21,424.50. After year 3, <b>$22,174.36</b>. Each year you earn 3.5% on a bigger amount.</p>
<ul><li><b>Compound interest:</b> value = deposit × (1 + rate ÷ n)<sup>n × years</sup>. Here n is how many times a year interest is added (1, 2 or 12).</li>
<li><b>Simple interest:</b> value = deposit × (1 + rate × years). Interest is paid out, so it doesn't grow.</li>
<li><b>Tax:</b> for a regular account, the calculator works out each year's interest and adds it to your income. The extra tax is your tax on the interest.</li>
<li><b>Marginal rate</b> means the tax rate on your last dollar of income. GIC interest is taxed at this rate.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Use your TFSA first</b> if you have room. The same GIC keeps all its interest there.</li>
<li><b>Stay under $100,000 per category per bank</b> to keep all of it CDIC-insured.</li>
<li><b>Check if it's cashable.</b> Most GICs lock your money until the end. Cashable ones pay less.</li>
<li><b>Ladder your GICs.</b> Split money across 1- to 5-year terms so some comes due every year.</li>
<li><b>Don't forget the tax each year.</b> A 5-year GIC that pays at the end is still taxed every year.</li></ul>
<h2 id="faq" style="margin-top:22px">GIC FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.bankofcanada.ca/2026/10/fad-press-release-2026-10-28/" rel="nofollow">Bank of Canada – policy rate decision, 28 October 2026</a>; <a href="https://www.cdic.ca/depositors/whats-covered/" rel="nofollow">CDIC – What's covered</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/first-home-savings-account.html" rel="nofollow">CRA – FHSA</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/tax-rates-brackets/current-year.html" rel="nofollow">CRA – 2026 tax rates and brackets</a>. Estimates only, not financial advice.</p>'''

out=build(P,'GIC Calculator Canada 2026 – Interest, Compounding and Tax',
 'How much interest will your GIC earn? Compound or simple interest, tax in a regular account vs TFSA, 2026 examples from $10,000 to $50,000, CDIC limits.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','Bank of Canada, CDIC, CRA')],
 [('form','Calculator'),('figures','2026 figures'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
