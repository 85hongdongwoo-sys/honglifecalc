import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/au/net-worth-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Cash and savings ($)</span><input id="c" inputmode="decimal" value="15,000"><small>Bank accounts, term deposits and offset account balances.</small></label><label class="f"><span>Investments and super ($)</span><input id="i" inputmode="decimal" value="38,000"><small>Shares, ETFs, managed funds and your super balance.</small></label><label class="f"><span>Home and property value ($)</span><input id="h" inputmode="decimal" value="450,000"><small>What it would sell for today, not what you paid.</small></label><label class="f"><span>Other assets (car etc.) ($)</span><input id="o" inputmode="decimal" value="7,500"><small>Use a realistic resale value.</small></label><label class="f"><span>Mortgage balance ($)</span><input id="mo" inputmode="decimal" value="300,000"></label><label class="f"><span>Other loans ($)</span><input id="l" inputmode="decimal" value="15,000"><small>Car and personal loans, buy now pay later, and your HELP study debt.</small></label><label class="f"><span>Credit card balances ($)</span><input id="cc" inputmode="decimal" value="3,000"></label></form>'''

calc='''function calc(){const c=Math.max(0,num('c')),i=Math.max(0,num('i')),h=Math.max(0,num('h')),o=Math.max(0,num('o')),mo=Math.max(0,num('mo')),l=Math.max(0,num('l')),cc=Math.max(0,num('cc'));
 const a=c+i+h+o,d=mo+l+cc,nw=a-d,eq=h-mo,ex=(c+i+o)-(l+cc);
 return big(O.nw,mf(nw),nw<0?'You owe more than you own':'Assets minus debts')+kv([[O.a,mf(a),'pos'],[O.d,mf(d),'neg'],['Home equity (home value − mortgage)',mf(eq)],['Net worth without your home and mortgage',mf(ex)],[O.r,a?pc(d/a,1):'—']])+'<p class="note">Debt-to-asset ratio = all debts ÷ all assets. Lower is safer. Super is included, but you usually can\\'t touch it until you retire.</p>'}'''

def nw(c,i,h,o,mo,l,cc):
    a=c+i+h+o; d=mo+l+cc; return a,d,a-d,h-mo,(c+i+o)-(l+cc),(d/a*100 if a else 0)
ex=[('Renter in their 20s',12000,45000,0,15000,0,30000,2000),
    ('Default example (first home)',15000,38000,450000,7500,300000,15000,3000),
    ('Couple close to retirement',40000,650000,900000,20000,50000,0,0),
    ('Starting out with debts',3000,0,0,8000,0,25000,6000)]
a=lambda x:('−' if x<0 else '')+f"${abs(x):,.0f}"
rows=[]
for lab,*v in ex:
    A,D,N,E,X,R=nw(*v)
    rows.append([lab,a(A),a(D),a(N),a(X),f"{R:.1f}%"])
print(rows)

FAQ=[
("How do I work out my net worth?","Add up everything you own, then take away everything you owe. Example: $510,500 of assets − $318,000 of debts = <b>$192,500</b> net worth."),
("Should I include my super in my net worth?","Yes, because it is your money. But keep in mind you usually can't use it until you retire. That is why the calculator also shows your net worth without your home, so you can see how much you could actually reach."),
("Does my HELP debt count?","Yes, add it under other loans. It is money you will have to repay, even though it has no interest charge like a normal loan."),
("Should I count my car?","Yes, but at what it would sell for today. Cars lose value fast, so a car bought for $30,000 may only be worth $15,000 after a few years."),
("What is home equity?","Home equity is the part of your home you really own: its value minus the mortgage. A $450,000 home with a $300,000 mortgage gives $150,000 of equity."),
("Can my net worth be negative?","Yes. If you owe more than you own, your net worth is below zero. That is common when you are starting out or after study. Paying off high-interest debts first is usually the fastest way back above zero."),
("How often should I check my net worth?","Once or twice a year is enough for most people – for example every July after tax time. The trend matters more than any single number."),
]

art='''<h2 id="ex">Net worth examples</h2>
<div id="examples">'''+table(['Situation','Assets','Debts','Net worth','Without home and mortgage','Debt-to-asset ratio'],rows)+'''</div>
<ul><li>A <b>renter in their 20s</b> with $45,000 in super and shares but a $30,000 loan has a net worth of <b>$40,000</b>.</li>
<li>The <b>default example</b> owns $510,500 and owes $318,000: net worth <b>$192,500</b>, of which $150,000 is home equity.</li>
<li>A <b>couple close to retirement</b> with a $900,000 home and $650,000 in super has a net worth of <b>$1,560,000</b>.</li>
<li>Someone <b>starting out</b> with a $25,000 loan and a $6,000 credit card is <b>−$20,000</b>. That is fixable.</li></ul>
<p class="note">Example numbers only, worked out with this calculator's own formula.</p>
<h2 id="how">How it works</h2>
<p>Example first. You have $15,000 in the bank, $38,000 in super and shares, a home worth $450,000 and a car worth $7,500. That is <b>$510,500</b> of assets. You owe $300,000 on the mortgage, $15,000 on a car loan and $3,000 on a credit card: <b>$318,000</b> of debts. Net worth = $510,500 − $318,000 = <b>$192,500</b>.</p>
<ul><li><b>Assets</b> = things you own that have a money value.</li>
<li><b>Debts</b> (liabilities) = money you owe.</li>
<li><b>Net worth</b> = assets − debts.</li>
<li><b>Debt-to-asset ratio</b> = debts ÷ assets. 62% means you owe 62 cents for every dollar you own.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Use today's values.</b> Not what you paid for the house or car.</li>
<li><b>Don't forget small debts.</b> Buy now pay later, phone plans with device repayments and tax you still owe all count.</li>
<li><b>Count your offset account as cash.</b> Don't also take it off the mortgage, or you count it twice.</li>
<li><b>Track the same way each time.</b> Then the change from year to year is meaningful.</li>
<li><b>Pay off the most expensive debt first.</b> Credit cards usually cost the most interest, so clearing them grows your net worth fastest.</li></ul>
<h2 id="faq" style="margin-top:22px">Net worth FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">This page uses simple arithmetic (assets − debts) and no official rates. All examples are made-up numbers worked out with this calculator's own formula. General information, not financial advice.</p>'''

out=build(P,'Net Worth Calculator Australia – Assets Minus Debts',
 'Add up what you own and what you owe to find your net worth, home equity and debt-to-asset ratio. Includes super and HELP debt, with worked examples.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Method','Assets − debts')],
 [('form','Calculator'),('ex','Examples'),('how','How it works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
