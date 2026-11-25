import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/au/fhss-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>Salary (before tax, a year)</span><div class="money"><input id="s" inputmode="decimal" value="90,000"></div></label><label class="f"><span>Extra before-tax (salary sacrifice) contributions per year (max $15,000 counts)</span><div class="money"><input id="c" inputmode="decimal" value="15,000"></div><small>Your employer's super guarantee does not count. Keep the total under the $32,500 concessional cap.</small></label><label class="f"><span>Years of contributions</span><input id="y" inputmode="decimal" value="3"><small>Only $50,000 of contributions in total can count.</small></label><label class="f"><span>Associated earnings rate (% a year)</span><input id="r" inputmode="decimal" value="7.51"><small>The ATO shortfall interest charge (SIC) rate. 7.51% for October to December 2026; it changes every quarter.</small></label><label class="f"><span>Bank savings rate to compare (% a year)</span><input id="b" inputmode="decimal" value="4"><small>An example rate, not an official figure – use the rate your own savings account pays.</small></label></form>'''

calc='''function calc(){const s=num('s'),c=Math.min(15000,num('c')),y=Math.max(1,Math.round(num('y'))),r=num('r')/100,b=num('b')/100;let tot=0,dep=0,bank=0;
 const m=mr(s);
 for(let k=0;k<y;k++){const add=Math.min(c,50000-tot);if(add<=0)break;tot+=add;dep=(dep+add*.85)*(1+r);bank=(bank+add-(itx(s)-itx(s-add)))*(1+b*(1-m))}
 const rel=dep,wh=Math.max(0,rel*(m-.30));
 return big('FHSS money paid to you',aud(rel-wh,0),'vs '+aud(bank,0)+' saving the same pay in a bank')+kv([['Contributions',aud(tot,0)],['Released (85% + associated earnings)',aud(rel,0)],['Withheld at release (rate '+pc(Math.max(0,m-.30),0)+')',aud(-wh,0),'neg'],['Bank savings (after tax on pay and interest)',aud(bank,0)],['Extra from FHSS',aud(rel-wh-bank,0),'t']])+'<p class="note">Estimate. Before-tax contributions are taxed 15% in the fund, so 85% is released. The ATO nominates a withholding rate based on your expected marginal rate including the 2% Medicare levy ('+pc(m,0)+' here) minus a 30% tax offset, or 17% if it cannot estimate your rate. What is withheld counts towards your end-of-year tax, so your final tax can be higher or lower.</p>'}'''

# python copy of au.js 2026-27 + page formula
BR=[(18200,0),(45000,.15),(135000,.30),(190000,.37),(float('inf'),.45)]
def bands(x):
    t=0;lo=0
    for hi,r in BR:
        if x>lo: t+=(min(x,hi)-lo)*r
        lo=hi
    return t
def lito(ti):
    if ti<=37500: return 700
    if ti<=45000: return 700-(ti-37500)*.05
    if ti<=66667: return max(0,325-(ti-45000)*.015)
    return 0
def med(ti):
    if ti<=28011: return 0
    if ti<=35014: return (ti-28011)*.10
    return ti*.02
def itx(ti): ti=max(0,ti); return max(0,bands(ti)-lito(ti))+med(ti)
def mr(ti): return (itx(ti+100)-itx(ti))/100
def fhss(s,c,y,r,b):
    c=min(15000,c);tot=dep=bank=0;m=mr(s)
    for k in range(y):
        add=min(c,50000-tot)
        if add<=0: break
        tot+=add;dep=(dep+add*.85)*(1+r);bank=(bank+add-(itx(s)-itx(s-add)))*(1+b*(1-m))
    wh=max(0,dep*(m-.3))
    return tot,dep,wh,dep-wh,bank,m
a=lambda x:f"${x:,.0f}"
EX=[(40000,10000,5),(60000,10000,5),(90000,15000,3),(150000,10000,5)]
rows=[]
for s,c,y in EX:
    tot,rel,wh,net,bank,m=fhss(s,c,y,.0751,.04)
    rows.append([a(s),f"{a(c)} × {y} yrs",a(rel),a(wh),a(net),a(bank),a(net-bank),f"{m*100:.0f}%"])
for r_ in rows: print(r_)

fig=[['Yearly FHSS limit','$15,000 of total contributions in any one financial year','Counts contributions made in a single financial year starting on or after 1 July 2017.'],
     ['Total FHSS limit','$50,000 of total contributions from 1 July 2017','Across all years. Associated earnings come on top.'],
     ['Maximum release','100% of after-tax (non-concessional) contributions · 85% of before-tax (concessional) contributions · plus associated earnings','Before-tax contributions lose 15% to contributions tax in the fund.'],
     ['Associated earnings','A notional amount worked out at the ATO shortfall interest charge (SIC) rate','Not what your fund really earned. 7.51% a year for October to December 2026 (7.43% for July to September 2026).'],
     ['Withholding at release','Your expected marginal rate including the 2% Medicare levy, minus a 30% tax offset – or 17% if the ATO cannot estimate your rate','Withheld from the before-tax part and the earnings. It counts towards your end-of-year tax.'],
     ['How long a release takes','Between 15 and 20 business days','Ask well before you need the money.'],
     ['If you do not buy and do not recontribute in time','FHSS tax of 20% of your assessable FHSS released amount','Instead you can put the money back into super as a non-concessional contribution.'],
     ['Concessional (before-tax) cap','$32,500 a year from 1 July 2026','Includes your employer’s super guarantee and salary sacrifice.'],
     ['Non-concessional (after-tax) cap 2026-27','$130,000 a year','After-tax contributions can also be released under FHSS.'],
     ['Super guarantee 1 July 2026 to 30 June 2027','12.00% of ordinary pay (maximum contribution base $270,830)','Paid by your employer. It does not count towards FHSS.'],
     ['Income tax 2026-27 (residents, before the 2% Medicare levy)','Nil to $18,200 · 15c per $1 over $18,200 to $45,000 · $4,020 + 30c to $135,000 · $31,020 + 37c to $190,000 · $51,370 + 45c above','The calculator also applies the low income tax offset.']]

FAQ=[
("How much can I save with the First Home Super Saver scheme?","Up to $15,000 of voluntary contributions from any one financial year and $50,000 in total, plus associated earnings. If all $50,000 is salary sacrifice, 85% ($42,500) plus earnings can be released. On a $90,000 salary, $15,000 a year for 3 years pays out about $43,400 in our example."),
("How much better is FHSS than saving in a bank?","It depends on your tax rate. On a $90,000 salary (32% marginal rate with the Medicare levy), $15,000 of pay a year for 3 years pays out about $43,400 through FHSS and about $32,300 in a bank at 4% – roughly $11,100 more in our example. Part of that is the tax saving (15% in the fund instead of 32% on your pay). The rest is the 7.51% associated earnings rate being higher than the bank rate."),
("How is the FHSS release taxed?","The ATO does not take a final tax at release. It nominates a withholding rate for your release: your expected marginal rate including the 2% Medicare levy, minus a 30% tax offset, or 17% if it cannot estimate your rate. At a 32% expected rate the withholding is about 2%. The before-tax part and the earnings then go in your tax return, and what was withheld counts towards your end-of-year tax."),
("What are associated earnings for FHSS?","They are a notional amount of earnings the ATO works out for you, not what your super fund really earned. The ATO uses its shortfall interest charge rate, which is 7.51% a year for October to December 2026 and changes every quarter. Enter a different rate in the calculator to see the effect."),
("When do I need to apply for FHSS?","Ask the ATO for an FHSS determination and request the release before ownership of any property transfers to you. You must be 18 or older when you request the determination. A release takes between 15 and 20 business days, so plan ahead."),
("What happens if I do not buy a home after the release?","In the ATO's example you have 12 months to sign a contract and can ask for a further 12 months. If you still do not buy, you can recontribute the money to super as a non-concessional contribution, or keep it and pay FHSS tax of 20% of your assessable FHSS released amount."),
("Who is eligible for FHSS?","You must be 18 or older when you request a determination, be a first home buyer who has never owned property in Australia, have your name going on the title, and not have asked for an FHSS release before."),
("Does my employer super count towards FHSS?","No. Only voluntary contributions count: salary sacrifice, personal contributions you claim a deduction for, and after-tax contributions. Your employer's 12% super guarantee cannot be released."),
]

art='''<h2 id="figures">FHSS rules and tax figures for 2026-27</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<h2 id="ex">FHSS examples: how much bigger is the deposit?</h2>
<div id="examples">'''+table(['Salary','Salary sacrifice','Released','Withheld','Paid to you','Bank (4%)','Extra from FHSS','Marginal rate'],rows)+'''</div>
<ul><li><b>$90,000 salary, $15,000 a year for 3 years:</b> $45,000 goes in. About $44,300 comes out, including about $6,000 of associated earnings. Withholding at 32% − 30% = 2% is about $890, so you receive <b>about $43,400</b>. The same pay saved in a bank at 4% gives about $32,300.</li>
<li><b>$60,000 salary, $10,000 a year for 5 years:</b> the full $50,000 is used. About $53,100 is released and about $1,860 is withheld (34% − 30%, because the low income tax offset is phasing out). You receive <b>about $51,200</b>, against about $36,000 in a bank.</li>
<li><b>$150,000 salary, $10,000 a year for 5 years:</b> the withholding is higher (39% − 30% = 9%, about $4,780), but your pay is also taxed at 39% if you save it in a bank. You receive <b>about $48,300</b>, against about $32,800 in a bank.</li>
<li><b>$40,000 salary:</b> your rate (22% here) is below 30%, so nothing is withheld, and it is close to the fund's 15%, so the tax saving is small. Most of the extra in the table comes from the 7.51% earnings rate versus 4% in the bank.</li></ul>
<p class="note">Examples use this calculator's formula with the official 7.51% associated earnings rate for October to December 2026 and a 4% bank rate as an example. The ATO works out real associated earnings day by day, and the rate changes every quarter.</p>
<h2 id="how">How the FHSS scheme works</h2>
<p>Example first. You earn $90,000 and salary sacrifice $15,000 into super each year. Your fund takes 15% contributions tax, so $12,750 stays in. If you saved that $15,000 of pay yourself, you would lose 32% to tax and keep only $10,200. That 15% versus 32% gap is the whole idea.</p>
<ul><li><b>Salary sacrifice</b> means part of your pay goes straight into super before income tax.</li>
<li><b>Concessional contributions</b> are these before-tax contributions. They are taxed 15% in the fund.</li>
<li><b>Non-concessional contributions</b> are made from money you have already paid tax on. All of them can be released.</li>
<li><b>Released amount</b> = 85% of concessional contributions + 100% of non-concessional contributions + associated earnings.</li>
<li><b>Withheld at release</b> = (concessional part + earnings) × (your expected marginal rate including Medicare − 30%), or 17% if the ATO cannot estimate your rate. It can't go below zero, and it is not your final tax.</li></ul>
<p>The steps: 1) make voluntary contributions; 2) ask the ATO for an FHSS determination, which tells you how much you can get; 3) request the release before ownership of any property transfers to you; 4) wait 15 to 20 business days for the money; 5) buy your home, or recontribute the money to super.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Stay under the cap.</b> Employer super plus salary sacrifice must stay under $32,500. At $150,000 your employer already pays $18,000, so about $14,500 is your room.</li>
<li><b>Low income?</b> Below $45,000 your rate is 15% plus the Medicare levy, close to the fund's 15%. The tax saving is small. After-tax contributions still work, but give no tax saving.</li>
<li><b>Couples can both use it.</b> Each person has their own $50,000 limit.</li>
<li><b>Request the release in time.</b> It has to be before ownership of the property transfers to you, and the money takes 15 to 20 business days.</li>
<li><b>Check your fund.</b> Ask your fund if it will release FHSS amounts. Most do.</li></ul>
<h2 id="faq" style="margin-top:22px">FHSS FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.ato.gov.au/individuals-and-families/super-for-individuals-and-families/super/withdrawing-and-using-your-super/early-access-to-super/first-home-super-saver-scheme" rel="nofollow">ATO – First home super saver scheme</a>; <a href="https://www.ato.gov.au/individuals-and-families/super-for-individuals-and-families/super/withdrawing-and-using-your-super/early-access-to-super/first-home-super-saver-scheme/about-fhss-release-amounts" rel="nofollow">ATO – About FHSS release amounts</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/shortfall-interest-charge-rates" rel="nofollow">ATO – Shortfall interest charge rates</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds/contributions-caps" rel="nofollow">ATO – Contributions caps</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds/super-guarantee" rel="nofollow">ATO – Super guarantee</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents" rel="nofollow">ATO – Tax rates for residents</a>. Examples use this calculator's own formula. General information, not financial advice.</p>'''

out=build(P,'FHSS Calculator 2026-27 – First Home Super Saver Deposit vs Bank',
 'First Home Super Saver in 2026-27: $15,000 a year, $50,000 limit, 85% of before-tax contributions, 7.51% earnings rate, with worked examples.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','ATO')],
 [('form','Calculator'),('figures','Rules and figures'),('ex','Examples'),('how','How it works'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
