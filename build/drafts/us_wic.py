import sys, math; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/us/benefits/wic.html'

G={'48':(15960,5680),'AK':(19950,7100),'HI':(18360,6530)}

form='''<form class="card" id="form" onsubmit="return false"><h2>Check your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>People in your household</span><input id="n" inputmode="decimal" value="3"><small>If you are pregnant, count each unborn baby as one more person.</small></label><label class="f"><span>Household income per year (before tax)</span><div class="money"><input id="i" inputmode="decimal" value="45,000"></div></label><label class="f"><span>Already on SNAP, Medicaid or TANF?</span><select id="p"><option value="0" selected>No</option><option value="1">Yes</option></select><small>If yes, you meet the income test automatically.</small></label><label class="f"><span>Where do you live?</span><select id="st"><option value="48" selected>48 states, DC or a territory</option><option value="AK">Alaska</option><option value="HI">Hawaii</option></select></label></form>'''

calc='''function calc(){const G={'48':[15960,5680],'AK':[19950,7100],'HI':[18360,6530]},g=G[$('st').value]||G['48'];
 const n=Math.max(1,Math.round(num('n'))),lim=Math.ceil((g[0]+g[1]*(n-1))*1.85),inc=num('i'),prog=$('p').value==='1',ok=prog||inc<=lim;
 const nt='<p class="note">Uses 185% of the 2026 HHS poverty guidelines (WIC limits for 1 July 2026 – 30 June 2027). The WIC clinic makes the final decision.</p>';
 return big(ok?'Income-eligible for WIC':'Income above the WIC limit',usd(lim)+' a year',n+(n>1?' people':' person')+' · '+usd(Math.ceil(lim/12))+' a month · '+usd(Math.ceil(lim/52))+' a week')+
  kv([['How you meet the income test',prog?'Through SNAP, Medicaid or TANF':(ok?'Through income':'Not met')],...(ok||prog?[]:[['Over the limit by',usd(inc-lim)]]),['Who can get WIC','pregnant women, new mothers, babies and children under 5'],['Also needed','a free nutrition check at the WIC clinic']])+nt}'''

lim=lambda n,k='48': math.ceil((G[k][0]+G[k][1]*(n-1))*1.85)
usd=lambda x:f"${x:,.0f}"
rows=[[str(n),usd(lim(n)),usd(math.ceil(lim(n)/12)),usd(math.ceil(lim(n)/52)),usd(lim(n,'AK')),usd(lim(n,'HI'))] for n in range(1,9)]
print(rows[:3], lim(4), lim(3), lim(2))
exs=[['Pregnant woman living alone (counts as 2)','$35,000','$40,034','Eligible'],
     ['Couple with a baby (3 people)','$48,000','$50,542','Eligible'],
     ['Family of 4','$65,000','$61,050','Not by income – $3,950 over'],
     ['Family of 4 on Medicaid','$65,000','$61,050','Eligible through Medicaid']]

FAQ=[
("What is the WIC income limit for a family of 4?","$61,050 a year from 1 July 2026 to 30 June 2027. That is $5,088 a month or $1,175 a week, before tax. Alaska and Hawaii have higher limits."),
("What is the WIC income limit for a family of 3?","$50,542 a year, $4,212 a month or $972 a week (48 states and DC). For 2 people it is $40,034 a year."),
("Does a pregnant woman count as two people for WIC?","Yes. A pregnant woman's household is counted with the unborn baby, so a pregnant woman living alone uses the limit for 2 people ($40,034). With twins, count 3."),
("If I get Medicaid or SNAP, do I qualify for WIC?","You meet the income test automatically if you get SNAP, Medicaid or TANF. You still need to be in a WIC group (pregnant, a new mother, a baby or a child under 5) and have a nutrition check at the clinic."),
("Who can get WIC?","Pregnant women, women up to 6 months after the baby is born, breastfeeding women up to the baby's first birthday, babies, and children up to their 5th birthday. Dads, grandparents and foster parents can apply for children in their care."),
("Is WIC income before or after tax?","Before tax (gross income). Count income from everyone in the household."),
]

art='''<p class="note" style="margin-top:0">Hong Life is an independent guide, <b>not a government website</b>. Apply and confirm with your local WIC clinic.</p>
<h2 id="limits">WIC income limits 1 July 2026 – 30 June 2027</h2>
<div id="examples">'''+table(['People in household','Per year','Per month','Per week','Alaska per year','Hawaii per year'],rows)+'''</div>
<p class="note">185% of the 2026 HHS poverty guidelines, rounded up. For each extra person above 8, add $10,508 a year (48 states and DC).</p>
<h2 id="ex">Examples: do I qualify?</h2>
'''+table(['Household','Income per year','WIC limit','Result'],exs)+'''
<ul><li><b>Pregnant woman living alone earning $35,000.</b> She counts as 2 people, so her limit is $40,034. She qualifies.</li>
<li><b>Couple with a baby earning $48,000.</b> The limit for 3 is $50,542, so they are $2,542 under it.</li>
<li><b>Family of 4 earning $65,000.</b> They are $3,950 over the $61,050 limit, so they don't qualify by income.</li>
<li><b>The same family on Medicaid.</b> Medicaid meets the income test, so their children under 5 can still get WIC.</li></ul>
<p class="note">Examples use this calculator's own formula with the 2026 guidelines.</p>
<h2 id="how">How WIC works (in plain words)</h2>
<p>WIC stands for the Special Supplemental Nutrition Program for Women, Infants, and Children. It is run by the U.S. Department of Agriculture (USDA) through state and local clinics. It is free.</p>
<ul><li><b>You need three things:</b> you are in a WIC group, your income is under the limit (or you get SNAP, Medicaid or TANF), and a clinic finds a nutrition need. A "nutrition need" can be things like low iron or poor weight gain. Many people meet it.</li>
<li><b>What you get:</b> a monthly benefit card for healthy foods such as milk, eggs, fruit and vegetables, whole grains and infant formula, plus breastfeeding help and nutrition advice.</li>
<li><b>The limit is 185%</b> of the poverty guideline. So for 4 people: $33,000 × 1.85 = $61,050.</li></ul>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Count the unborn baby.</b> Pregnant women often forget, and use too small a household.</li>
<li><b>Apply even if you are close.</b> Clinics check income carefully, and recent pay cuts may count.</li>
<li><b>Working families qualify too.</b> Many families with jobs are under 185% of the poverty line.</li>
<li><b>Bring proof.</b> ID, proof of address and proof of income or of SNAP, Medicaid or TANF.</li></ul>
<h2 id="faq" style="margin-top:22px">WIC FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://www.fns.usda.gov/wic/iegs" rel="nofollow">USDA FNS – WIC Income Eligibility Guidelines</a>; <a href="https://www.fns.usda.gov/wic/wic-eligibility-requirements" rel="nofollow">USDA FNS – WIC eligibility requirements</a>; <a href="https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines" rel="nofollow">HHS ASPE – 2026 Poverty Guidelines</a>. General information, not legal advice.</p>'''

out=build(P,'WIC Income Limits 2026–27 – Am I Eligible? Calculator by Family Size',
 'WIC income limits from 1 July 2026: $50,542 a year for 3, $61,050 for 4. Check if you qualify, who counts, and how SNAP or Medicaid helps.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','USDA FNS, HHS poverty guidelines')],
 [('form','Calculator'),('limits','2026–27 income limits'),('ex','Examples'),('how','How WIC works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
