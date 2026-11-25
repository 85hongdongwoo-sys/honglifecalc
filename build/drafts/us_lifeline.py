import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/us/benefits/lifeline-phone-internet.html'

# 2026 HHS poverty guidelines (48 states + DC, Alaska, Hawaii) – Lifeline uses 135% of these
G={'48':(15960,5680),'AK':(19950,7100),'HI':(18360,6530)}
DISC=9.25; TRIBAL=34.25

form='''<form class="card" id="form" onsubmit="return false"><h2>Check your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>People in your household</span><input id="n" inputmode="decimal" value="3"><small>Everyone who lives with you and shares money for bills and food.</small></label><label class="f"><span>Household income per year (before tax)</span><div class="money"><input id="i" inputmode="decimal" value="30,000"></div></label><label class="f"><span>Do you or someone in your home get SNAP, Medicaid, SSI, Federal Public Housing Assistance or the Veterans Pension and Survivors Benefit?</span><select id="p"><option value="0" selected>No</option><option value="1">Yes</option></select><small>Any one of these qualifies you whatever your income.</small></label><label class="f"><span>Where do you live?</span><select id="st"><option value="48" selected>48 states, DC or a territory</option><option value="AK">Alaska</option><option value="HI">Hawaii</option></select></label><label class="f"><span>Do you live on Tribal lands?</span><select id="tr"><option value="0" selected>No</option><option value="1">Yes</option></select><small>Tribal lands get a bigger discount.</small></label></form>'''

calc='''function calc(){const G={'48':[15960,5680],'AK':[19950,7100],'HI':[18360,6530]},g=G[$('st').value]||G['48'];
 const n=Math.max(1,Math.round(num('n'))),f=g[0]+g[1]*(n-1),lim=Math.floor(f*1.35),inc=num('i'),prog=$('p').value==='1',ok=prog||inc<=lim,tr=$('tr').value==='1',d=tr?34.25:9.25;
 const nt='<p class="note">Uses 135% of the 2026 HHS poverty guidelines. The National Verifier makes the final decision. One Lifeline discount per household.</p>';
 return big(ok?'Likely eligible for Lifeline':'Income above the limit',ok?usd(d)+'/month':usd(lim),ok?'about '+usd(Math.round(d*12))+' a year off your phone or internet bill':'income limit for '+n+(n>1?' people':' person'))+
  kv([['How you qualify',prog?'Through a benefit program (income does not matter)':(ok?'Through income':'Not yet – check the programs above')],['135% income limit for '+n,usd(lim)],['Per month',usd(Math.round(lim/12))],...(ok||prog?[]:[['Over the limit by',usd(inc-lim)]]),['Your discount',usd(d)+'/month'+(tr?' (Tribal lands)':'')],['Limit','one Lifeline benefit per household']])+nt}'''

lim=lambda n,k='48': int((G[k][0]+G[k][1]*(n-1))*1.35)
usd=lambda x:f"${x:,.0f}"
rows=[[str(n),usd(lim(n)),usd(round(lim(n)/12)),usd(lim(n,'AK')),usd(lim(n,'HI'))] for n in range(1,9)]
exs=[['1 person, $20,000, no benefits','$21,546','Eligible','$111 a year'],
     ['3 people, $30,000, no benefits','$36,882','Eligible','$111 a year'],
     ['4 people, $50,000, gets SNAP','$44,550','Eligible (SNAP)','$111 a year'],
     ['2 people, $32,000, no benefits','$29,214','Not eligible','–'],
     ['3 people on Tribal lands, $30,000','$36,882','Eligible','$411 a year']]
print([r for r in rows][:3], lim(3), lim(4), lim(2), round(TRIBAL*12))

FAQ=[
("What is the Lifeline income limit for 2026?","135% of the federal poverty guideline. For 1 person that is $21,546 a year, for 2 it is $29,214, for 3 it is $36,882 and for 4 it is $44,550 (48 states and DC). Add $7,668 for each extra person. Alaska and Hawaii have higher limits."),
("How much is the Lifeline discount?","$9.25 a month off one phone or internet service, about $111 a year. On Tribal lands it can be up to $34.25 a month, about $411 a year."),
("Which programs qualify me for Lifeline?","SNAP (food stamps), Medicaid, Supplemental Security Income (SSI), Federal Public Housing Assistance (such as Section 8) and the Veterans Pension and Survivors Benefit. If anyone in your household gets one of these, you qualify whatever your income. On Tribal lands some Tribal programs also count."),
("Can I get Lifeline for both my phone and my internet?","No. You get one Lifeline discount per household, on either a phone service or an internet service (or a bundle of both from one company)."),
("Did the Affordable Connectivity Program come back?","No. The Affordable Connectivity Program (ACP) stopped giving discounts in 2024 when its money ran out. Lifeline is the federal program that is still running."),
("How do I apply for Lifeline?","Apply online through the National Verifier at lifelinesupport.org, by mail, or through a phone or internet company that offers Lifeline. You need proof of income or proof that you get a qualifying benefit. Then pick a participating company to get the discount."),
("Do I need to renew Lifeline every year?","Yes. You must recertify every year to show you still qualify. If you don't, your discount stops."),
]

art='''<p class="note" style="margin-top:0">Hong Life is an independent guide, <b>not a government website</b>. Apply and confirm through the official Lifeline National Verifier.</p>
<h2 id="limits">Lifeline income limits 2026 (135% of poverty guidelines)</h2>
<div id="examples">'''+table(['People in household','48 states and DC, per year','Per month','Alaska','Hawaii'],rows)+'''</div>
<p class="note">135% of the 2026 HHS poverty guidelines ($15,960 for one person plus $5,680 for each extra person in the 48 states and DC), rounded down to whole dollars.</p>
<h2 id="figures">Key Lifeline figures</h2>
'''+table(['Item','Amount','What it means'],[
 ['Standard discount','$9.25 a month','Taken off your phone or internet bill each month.'],
 ['Tribal lands discount','Up to $34.25 a month','For people who live on qualifying Tribal lands.'],
 ['Income limit','135% of the poverty guideline','$36,882 a year for 3 people in 2026.'],
 ['Benefit programs','SNAP, Medicaid, SSI, Federal Public Housing Assistance, Veterans Pension and Survivors Benefit','Getting any one of these qualifies you.'],
 ['Per household','One discount','Phone or internet, not both.'],
 ['Renewal','Every year','You must recertify or the discount stops.']])+'''
<h2 id="ex">Examples: do I qualify?</h2>
'''+table(['Household','Income limit','Result','Savings'],exs)+'''
<ul><li><b>One person earning $20,000.</b> The limit is $21,546, so they qualify through income and save $9.25 a month.</li>
<li><b>Family of 3 earning $30,000.</b> The limit is $36,882. They are $6,882 under it, so they qualify.</li>
<li><b>Family of 4 earning $50,000 who get SNAP.</b> Their income is over the $44,550 limit, but SNAP qualifies them anyway.</li>
<li><b>Couple earning $32,000 with no benefits.</b> The limit for 2 is $29,214. They are $2,786 over, so they don't qualify unless they join a benefit program.</li></ul>
<p class="note">Examples use this calculator's own formula with the 2026 guidelines.</p>
<h2 id="how">How Lifeline works (in plain words)</h2>
<p>Lifeline is a federal program run by the FCC (the Federal Communications Commission, which regulates phone and internet). It makes phone or internet service cheaper for people with low income. The money comes from a fund that phone companies pay into.</p>
<ul><li><b>Step 1 – check you qualify.</b> Either your household income is at or below 135% of the poverty guideline, or someone in your home gets a qualifying benefit.</li>
<li><b>Step 2 – apply.</b> The National Verifier checks your proof. It is the official system that decides who qualifies.</li>
<li><b>Step 3 – choose a company.</b> Pick a phone or internet company that offers Lifeline. It takes the discount off your bill.</li></ul>
<p>"Household" means the people you live with and share money with. Two families at one address who keep their money apart can each count as a household.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Use your gross income.</b> Count income before tax, from everyone in the household.</li>
<li><b>Benefits are the fast route.</b> If you get SNAP or Medicaid, show that letter. You don't need to prove your income then.</li>
<li><b>Only one per home.</b> If someone else in your household already has Lifeline, you can't get a second one.</li>
<li><b>Don't miss recertification.</b> Watch for the yearly notice. If you don't answer, the discount ends.</li>
<li><b>Never pay to apply.</b> Applying for Lifeline is free.</li></ul>
<h2 id="faq" style="margin-top:22px">Lifeline FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.fcc.gov/lifeline-consumers" rel="nofollow">FCC – Lifeline Support for Affordable Communications</a>; <a href="https://www.lifelinesupport.org/do-i-qualify/" rel="nofollow">USAC – Do I qualify?</a>; <a href="https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines" rel="nofollow">HHS ASPE – 2026 Poverty Guidelines</a>. General information, not legal advice.</p>'''

out=build(P,'Lifeline Program 2026 – Income Limits and $9.25 Phone or Internet Discount',
 'Do you qualify for Lifeline in 2026? Income limits by household size ($36,882 for 3), qualifying programs, the $9.25 discount and how to apply.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','FCC, USAC, HHS poverty guidelines')],
 [('form','Calculator'),('limits','2026 income limits'),('figures','Key figures'),('ex','Examples'),('how','How it works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
