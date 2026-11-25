import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/ca/fhsa-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>Contribution per year (max $8,000)</span><div class="money"><input id="a" inputmode="decimal" value="8,000"></div></label><label class="f"><span>Years contributing (max 15)</span><input id="y" inputmode="decimal" value="5"><small>At $8,000 a year you reach the $40,000 lifetime limit in 5 years.</small></label><label class="f"><span>Annual return (%)</span><input id="r" inputmode="decimal" value="4"><small>An example rate. Use 0 for cash, or the rate your GIC or fund pays.</small></label><label class="f"><span>Taxable income</span><div class="money"><input id="i" inputmode="decimal" value="70,000"></div></label><label class="f"><span>Province or territory</span><select id="pv"><option value="AB">Alberta</option><option value="BC">British Columbia</option><option value="MB">Manitoba</option><option value="NB">New Brunswick</option><option value="NL">Newfoundland and Labrador</option><option value="NT">Northwest Territories</option><option value="NS">Nova Scotia</option><option value="NU">Nunavut</option><option value="ON" selected>Ontario</option><option value="PE">Prince Edward Island</option><option value="QC">Quebec</option><option value="SK">Saskatchewan</option><option value="YT">Yukon</option></select></label></form>'''

calc='''function calc(){const a=Math.max(0,Math.min(8000,num('a'))),y=Math.min(15,Math.max(1,Math.round(num('y')))),r=num('r')/100,i=num('i'),c=$('pv').value;let b=0,paid=0,ref=0,ref1=0;
 for(let k=0;k<y;k++){const add=Math.min(a,40000-paid);if(add<=0){b*=1+r;continue}paid+=add;const t=itax(i,c).tot-itax(i-add,c).tot;if(!k)ref1=t;ref+=t;b=(b+add)*(1+r)}
 return big('FHSA balance after '+y+' years',cad(b,0),'tax-free for a qualifying first home')+kv([['Total contributions',cad(paid,0)],['Investment growth',cad(b-paid,0),'pos'],['Tax refund in year 1 (est.)',cad(ref1,0),'pos'],['Total tax refunds (est.)',cad(ref,0),'pos'],['Effective cost of your contributions',cad(paid-ref,0),'t']])+'<p class="note">Assumes you put money in at the start of each year, claim the deduction the same year, and your income stays the same. Uses 2026 federal and provincial tax rates. The account can stay open for at most 15 years.</p>'}'''

def bal(a,y,r):
    b=paid=0
    for k in range(y):
        add=min(a,40000-paid)
        if add<=0: b*=1+r; continue
        paid+=add; b=(b+add)*(1+r)
    return b
for args in [(8000,5,.04),(8000,5,0),(8000,5,.05),(4000,10,.04)]: print(args, round(bal(*args)))

fig=[['Yearly limit','$8,000','The most new room you get each calendar year.'],
     ['Lifetime limit','$40,000','The most you can ever put in, across all your FHSAs.'],
     ['Carry-forward','Up to $8,000 of unused room','If you skip a year, you can add up to $16,000 the next year. Room only starts once you open an account, and money your FHSA earns does not use up room.'],
     ['Who can open one','Canadian resident, 18 or older (19 where that is the age of majority), and 71 or younger on 31 December of that year','You also have to be a first-time buyer: you did not live in a home you or your spouse or common-law partner owned, as your main home, this calendar year or in the previous 4 calendar years.'],
     ['How long it can stay open','Until 31 December of the earliest of three years','The 15th anniversary of opening your first FHSA; the year you turn 71; or the year after your first qualifying withdrawal. Whichever comes first.'],
     ['Tax on money going in','Deductible, like an RRSP','You can claim the deduction this year or save it for a later year.'],
     ['Tax on money coming out','None for a qualifying first home','A home withdrawal is tax-free, like a TFSA. Other withdrawals are taxed as income.'],
     ['If you don\'t buy','Move it to an RRSP or RRIF tax-free','The transfer does not use your RRSP room.'],
     ['Home Buyers\' Plan (HBP)','Can be used as well','You can use the HBP, which lets you borrow from your RRSP, and the FHSA for the same home.'],
     ['Federal tax rates 2026','14% up to $58,523 · 20.5% · 26% · 29% · 33% over $258,482','Your refund depends on your top rate. 20.5% applies from $58,523.01, 26% from $117,045.01, 29% from $181,440.01.']]

refund=[['$45,000','$1,614','$1,851','$1,760','$2,055'],
        ['$70,000','$2,372','$2,256','$2,440','$2,889'],
        ['$100,000','$2,465','$2,256','$2,440','$2,889'],
        ['$130,000','$3,473','$3,063','$2,880','$3,657']]

ex=[['Ontario, $70,000 income','$8,000 × 5 years at 4%','$45,064','$11,860','$28,140'],
    ['B.C., $55,000 income','$8,000 × 5 years in cash (0%)','$40,000','$8,327','$31,673'],
    ['Alberta, $100,000 income','$8,000 × 5 years at 5%','$46,415','$12,200','$27,800'],
    ['Quebec, $45,000 income','$4,000 × 10 years at 4%','$49,945','$10,276','$29,724']]

FAQ=[
("How much tax refund do I get for an FHSA contribution?","It depends on your income and province. In 2026, $8,000 at $70,000 of income saves about $2,372 in Ontario, $2,440 in Alberta, $2,256 in B.C. and $2,889 in Quebec. At $45,000 in Ontario it is about $1,614."),
("How much can I put in an FHSA in 2026?","$8,000 a year, up to $40,000 for life. If you opened your account last year and didn't use all your room, up to $8,000 carries forward. So the most you can add in one year is $16,000."),
("What happens to my FHSA if I don't buy a house?","You can move the money to your RRSP or RRIF with no tax, and it doesn't use your RRSP room. You must do this before the account has to close: 31 December of the 15th year after you opened it, or of the year you turn 71, whichever comes first. If you just withdraw it as cash, it is taxed as income."),
("Can I use the FHSA and the Home Buyers' Plan together?","Yes. For the same qualifying home you can take your FHSA money out tax-free and also borrow from your RRSP under the Home Buyers' Plan. The HBP money must be paid back to your RRSP; the FHSA money does not."),
("Who counts as a first-time home buyer for the FHSA?","You count if, this calendar year or in the previous 4 calendar years, you did not live as your main home in a home that you, or your spouse or common-law partner, owned or jointly owned. You also need to be a Canadian resident, 18 or older (19 in provinces where that is the age of majority), and 71 or younger on 31 December of the year you open it."),
("Should I use an FHSA or a TFSA for a down payment?","If you qualify, the FHSA is usually better. Money going in cuts your tax, like an RRSP, and money coming out for a home is tax-free, like a TFSA. A TFSA gives no deduction, but you can take money out for anything."),
("Do I have to claim my FHSA deduction in the same year?","No. You can carry the deduction forward and claim it in a later year, for example when your income, and so your tax rate, is higher."),
]

art='''<h2 id="figures">FHSA rules and 2026 figures</h2>
<p>An <b>FHSA</b> (First Home Savings Account) is a registered account for buying your first home in Canada. Money going in lowers your tax. Money coming out for a first home is tax-free.</p>
'''+table(['Rule','Figure','What it means'],fig)+'''
<h2 id="refund">FHSA tax refund for $8,000 in 2026</h2>
<p>Your refund is the tax you no longer pay because $8,000 comes off your taxable income. The higher your income, the bigger the refund.</p>
'''+table(['Taxable income','Ontario','British Columbia','Alberta','Quebec'],refund)+'''
<p class="note">These amounts are what this page's own 2026 tax engine works out, not figures published province by province. It uses the CRA federal brackets above plus each province's own brackets, and for Quebec the federal abatement (a federal tax cut for Quebec residents). CPP and EI are not changed by the deduction.</p>
<h2 id="ex">FHSA growth examples</h2>
<div id="examples">'''+table(['Who','Plan','Balance at the end','Total tax refunds','Real cost to you'],ex)+'''</div>
<ul><li>An Ontario saver on <b>$70,000</b> who puts in $8,000 a year for 5 years ends up with <b>$45,064</b>. The refunds give back $11,860, so the $40,000 really cost about $28,140.</li>
<li>Even in <b>cash at 0%</b>, a B.C. saver on $55,000 gets $8,327 back in refunds. That is like a 21% bonus on the $40,000.</li>
<li>Putting in <b>$4,000 a year for 10 years</b> still reaches the $40,000 limit. More years of growth give a bigger balance ($49,945 at 4%).</li></ul>
<p class="note">Examples use this calculator's own formula. 4% and 5% are example returns, not quotes.</p>
<h2 id="how">How the FHSA calculator works</h2>
<p>Example first. You earn $70,000 in Ontario and put in $8,000. Your taxable income drops to $62,000. All of that $8,000 was taxed at 20.5% federal (the rate above $58,523) and 9.15% Ontario (the rate above $53,891). So you save $8,000 × 20.5% = $1,640 plus $8,000 × 9.15% = $732. Altogether about <b>$2,372</b>.</p>
<ul><li><b>Balance:</b> each year the calculator adds your contribution, then grows the whole balance by your return. It stops adding once you hit $40,000.</li>
<li><b>Tax refund:</b> tax on your income − tax on (income − contribution), each year.</li>
<li><b>Real cost:</b> what you put in − all the refunds.</li>
<li><b>Marginal rate</b> means the tax rate on your last dollar of income. It is the rate your deduction saves.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Open the account early.</b> Room only starts the year you open your first FHSA. Opening one with $0 still starts the clock on your $8,000.</li>
<li><b>Don't over-contribute.</b> Going over your room costs you an extra tax for every month the extra money sits in the account. Check your room in CRA My Account first.</li>
<li><b>Save the deduction for a higher-income year</b> if you expect a big raise soon.</li>
<li><b>Match the investment to your timeline.</b> If you buy in 1–2 years, a GIC or savings account is safer than stocks.</li>
<li><b>Get a written agreement first.</b> A tax-free withdrawal needs a written agreement to buy or build the home, and you have to intend to live in it. Ask your bank for the withdrawal form and the exact dates that apply to you.</li></ul>
<h2 id="faq" style="margin-top:22px">FHSA FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/first-home-savings-account.html" rel="nofollow">CRA – First Home Savings Account (FHSA)</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/first-home-savings-account/contributing-your-fhsa.html" rel="nofollow">CRA – Participating in your FHSAs</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/first-home-savings-account/opening-your-fhsas.html" rel="nofollow">CRA – Opening your FHSAs</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/first-home-savings-account/tax-deductions-fhsa-contributions.html" rel="nofollow">CRA – Tax deductions for FHSA contributions</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/first-home-savings-account/definitions.html" rel="nofollow">CRA – Definitions for FHSAs</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/tax-rates-brackets/current-year.html" rel="nofollow">CRA – 2026 tax rates and brackets</a>; Income Tax Act s. 146.6. Estimates only, not tax advice.</p>'''

out=build(P,'FHSA Calculator 2026 – Tax Refund and Growth by Province',
 'How much tax refund does an $8,000 FHSA contribution give in 2026? Refunds by province and income, growth to $40,000+, rules, carry-forward and examples.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','CRA, Income Tax Act')],
 [('form','Calculator'),('figures','Rules and figures'),('refund','Tax refund by province'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
