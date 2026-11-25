import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/sg/retirement-savings-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Yearly spending in retirement ($)</span><input id="E" inputmode="decimal" value="52,000"><small>In today's dollars.</small></label><label class="f"><span>Expected CPF LIFE payout ($ a month)</span><input id="cp" inputmode="decimal" value="0"><small>Optional. Use the estimate from the CPF Board for your own account. Leave 0 to ignore it.</small></label><label class="f"><span>Withdrawal rate (%)</span><input id="w" inputmode="decimal" value="4"><small>How much of your savings you take out in the first year. 4% is a common rule of thumb; 3–3.5% is more careful.</small></label><label class="f"><span>Current savings ($)</span><input id="S" inputmode="decimal" value="65,000"></label><label class="f"><span>Monthly saving ($)</span><input id="m" inputmode="decimal" value="1,300"></label><label class="f"><span>Expected annual return (%)</span><input id="r" inputmode="decimal" value="6"><small>An example rate, not a promise. Lower it to be safe.</small></label></form>'''

calc='''function calc(){const E=Math.max(0,num('E')),cpy=Math.max(0,num('cp'))*12,w=num('w')/100,S=Math.max(0,num('S')),m=Math.max(0,num('m')),i=num('r')/1200;
 if(w<=0)return big(O.tgt,'—','Enter a withdrawal rate above 0%');
 const need=Math.max(0,E-cpy),tgt=need/w;let b=S,k=0;while(b<tgt&&k<1200){b=b*(1+i)+m;k++}
 const rows=[[O.rule,pc(w,1)],['Spending you need from savings',mf(need)+' a year']];
 if(cpy>0)rows.push(['Covered by CPF LIFE',mf(Math.min(cpy,E))+' a year','pos']);
 rows.push([O.mtgt,mf(tgt*w/12)]);
 if(k<1200&&k>0)rows.push(['Savings when you reach it',mf(b)]);
 const sub=tgt<=S?'You have already reached it':k>=1200?O.never:O.yrs+': '+nn(k/12,1);
 return big(O.tgt,mf(tgt),sub)+kv(rows)+'<p class="note">Target = yearly spending you need from savings ÷ withdrawal rate. Savings grow monthly at your return, with your saving added at the end of each month. No inflation or tax is included, so use today\\'s dollars and a modest return.</p>'}'''

def years(tgt,S,m,r):
    i=r/1200;b=S;k=0
    while b<tgt and k<1200: b=b*(1+i)+m;k+=1
    return k
a=lambda x:f"${x:,.0f}"
ex=[('Simple lifestyle',36000,0,4,65000,1300,6),
    ('Simple lifestyle + CPF LIFE $1,500 a month',36000,1500,4,65000,1300,6),
    ('Default example',52000,0,4,65000,1300,6),
    ('Careful 3.5% withdrawal',60000,0,3.5,100000,2000,5)]
rows=[]
for lab,E,cp,w,S,m,r in ex:
    need=max(0,E-cp*12);tgt=need/(w/100);k=years(tgt,S,m,r)
    rows.append([lab,a(E),a(cp*12),f"{w:g}%",a(tgt),f"{k/12+1e-9:.1f}"])
print(rows)

fig=[['CPF LIFE payouts','Can start from age 65','The CPF Board shows estimated monthly payouts from age 65.'],
     ['Basic Retirement Sum (turning 55 in 2026)','$110,200','The lowest of the three CPF retirement sums.'],
     ['Full Retirement Sum (turning 55 in 2026)','$220,400','Twice the Basic Retirement Sum.'],
     ['Enhanced Retirement Sum (2026)','$440,800','The most you can set aside for higher payouts. It increases yearly and applies to everyone, whenever you turn 55.']]

FAQ=[
("How much do I need to retire in Singapore?","Start from what you will spend in a year and divide by your withdrawal rate. With the 4% rule, $36,000 a year needs $900,000 of savings. If CPF LIFE pays you $1,500 a month ($18,000 a year), you only need to cover $18,000 from savings: $450,000."),
("What is the 4% rule?","It is a rule of thumb. You take out 4% of your savings in the first year of retirement, then roughly the same amount each year after, adjusted for prices. Savings of $1,300,000 give $52,000 in the first year. It came from US market data, so many people use 3–3.5% to be safer."),
("Does CPF LIFE reduce how much I need to save?","Yes. CPF LIFE pays you a monthly income for life, and payouts can start from 65. Every $1,000 a month it pays covers $12,000 a year, which at 4% is $300,000 less you need to save yourself. Use your own estimate from the CPF Board."),
("What are the CPF retirement sums for 2026?","For members turning 55 in 2026: Basic Retirement Sum $110,200 and Full Retirement Sum $220,400. The Enhanced Retirement Sum is $440,800 in 2026, whenever you turn 55. They set how much is kept in your Retirement Account for CPF LIFE payouts."),
("How long will it take to reach my target?","With the default numbers – $65,000 saved, $1,300 a month and 6% a year – it takes about 26 years to reach $1,300,000. Saving more each month or starting earlier shortens this a lot."),
("Is a 6% return realistic?","Nobody can promise it. Returns go up and down, and inflation lowers what your money can buy. Try 4% or 5% as well to see a more careful result."),
]

art='''<h2 id="figures">Official CPF and retirement figures (2026)</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<p class="note">CPF LIFE payouts depend on your own savings, the plan you choose and your age. We don't estimate them here. Check your own figure with the CPF Board.</p>
<h2 id="ex">Retirement savings examples</h2>
<div id="examples">'''+table(['Case','Yearly spending','CPF LIFE a year','Withdrawal rate','Savings target','Years to reach it'],rows)+'''</div>
<ul><li>To spend <b>$36,000 a year</b> at 4%, you need <b>$900,000</b>.</li>
<li>If <b>CPF LIFE pays $1,500 a month</b>, the target halves to <b>$450,000</b> and you get there much sooner.</li>
<li>The <b>default example</b> ($52,000 a year) needs <b>$1,300,000</b>.</li>
<li>Using a <b>careful 3.5%</b> rate for $60,000 a year raises the target to about <b>$1,714,286</b>.</li></ul>
<p class="note">Years assume the savings, monthly amount and return in each case: $65,000, $1,300 a month and 6% for the first three; $100,000, $2,000 a month and 5% for the last. CPF LIFE amounts are examples only. Worked out with this calculator's own formula.</p>
<h2 id="how">How it works</h2>
<p>Example first. You want to spend $52,000 a year. At a 4% withdrawal rate you need $52,000 ÷ 0.04 = <b>$1,300,000</b>. You have $65,000 now and save $1,300 a month at 6% a year. The calculator adds interest every month and finds you reach the target in about <b>26 years</b>.</p>
<ul><li><b>Withdrawal rate</b> = the share of your savings you spend in the first year.</li>
<li><b>Target</b> = yearly spending you need from savings ÷ withdrawal rate.</li>
<li><b>CPF LIFE</b> = a monthly payout for life from the CPF Board. It lowers the spending your own savings must cover.</li>
<li><b>Compound growth</b> = you earn returns on your returns. The calculator adds them monthly.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Count CPF LIFE.</b> Leaving it out can make your target look far bigger than it is.</li>
<li><b>Use today's dollars.</b> The calculator doesn't add inflation, so enter spending at today's prices and a return after inflation.</li>
<li><b>Plan for healthcare.</b> Medical costs usually rise with age.</li>
<li><b>Test a lower return.</b> Try 4% to see how much later you would reach the target.</li>
<li><b>Housing matters.</b> A paid-off home lowers how much you need each year.</li></ul>
<h2 id="faq" style="margin-top:22px">Retirement savings FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.cpf.gov.sg/member/infohub/educational-resources/what-is-the-cpf-retirement-sum" rel="nofollow">CPF Board – what is the CPF retirement sum</a>. Examples use this calculator's own formula. General information, not financial advice.</p>'''

out=build(P,'Retirement Savings Calculator Singapore 2026 – With CPF LIFE',
 'How much do you need to retire in Singapore? Work out your nest egg with the 4% rule and CPF LIFE payouts, with 2026 CPF retirement sums and examples.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','CPF Board')],
 [('form','Calculator'),('figures','CPF figures'),('ex','Examples'),('how','How it works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
