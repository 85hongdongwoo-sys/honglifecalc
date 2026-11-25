import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/us/benefits/head-start.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Check your numbers</h2><label class="f"><span>People in your household</span><input id="n" inputmode="decimal" value="3"><small>Count everyone in the family you live with, including the child.</small></label><label class="f"><span>Household income per year (before tax)</span><div class="money"><input id="i" inputmode="decimal" value="27,000"></div></label><label class="f"><span>On public assistance, homeless, or child in foster care?</span><select id="p"><option value="0" selected>No</option><option value="1">Yes</option></select><small>Any one of these makes a child eligible whatever the income.</small></label></form>'''

calc='''function calc(){const n=Math.max(1,Math.round(num('n'))),f=FPL(n),inc=num('i'),p=inc/f,cat=$('p').value==='1',ok=cat||p<=1;
 const head=cat?'Eligible (public assistance, homeless or foster care)':p<=1?'Income-eligible':p<=1.3?'May qualify (100–130% group)':'Over the income limit';
 const sub=cat?'Income does not matter in these cases':pc(p)+' of the 2026 poverty guideline';
 const nt='<p class="note">Uses the 2026 HHS poverty guidelines for the 48 contiguous states and DC. Alaska and Hawaii have higher guidelines – see the table below. The local program makes the final decision.</p>';
 return big(head,cat?'Yes':pc(p),sub)+kv([['100% poverty line for '+n,usd(f)],['130% of poverty line for '+n,usd(Math.round(f*1.3))],...(ok?[]:[['Above the 100% line by',usd(inc-f)]]),['Ages','Early Head Start: under 3 · Head Start Preschool: 3 until school age'],['Cost to families','Free'],['Over 130%?','Children who meet none of the rules can still fill up to 10% of a program\\'s enrollment']])+nt}'''

F=lambda n:15960+5680*(n-1)
AK=lambda n:19950+7100*(n-1)
HI=lambda n:18360+6530*(n-1)
usd=lambda x:f"${x:,.0f}"
lim=[[str(n),usd(F(n)),usd(round(F(n)*1.3)),f"{usd(round(F(n)/12))} a month"] for n in range(1,9)]
akhi=[[str(n),usd(AK(n)),usd(round(AK(n)*1.3)),usd(HI(n)),usd(round(HI(n)*1.3))] for n in range(1,9)]
def ex(n,i,note):
    p=i/F(n); return [f"{n} people",usd(i),f"{p*100:.0f}%",note]
exs=[ex(3,26000,'Eligible'),ex(5,30000,'Eligible'),
     ex(4,40000,'May qualify'),ex(2,30000,'Over the limit')]

FAQ=[
("What is the Head Start income limit for a family of 3 in 2026?","$27,320 a year, which is 100% of the 2026 federal poverty guideline (48 states and DC). That is about $2,277 a month before tax. Families earning up to $35,516 (130%) may still get a place if the program has room."),
("What is the income limit for a family of 4?","$33,000 a year at 100% of the poverty guideline, or $42,900 at 130%. For each extra person, add $5,680 to the 100% limit. Alaska and Hawaii use higher figures."),
("Does my child qualify for Head Start if we get public assistance?","Yes. A child is eligible if the family gets public assistance, including TANF child-only payments, or would be able to get it if it were not for child care. Income does not matter in that case. The same is true if the child is homeless or in foster care."),
("Does SNAP (food stamps) make my child eligible for Head Start?","The rules name public assistance, homelessness and foster care, but they do not list each program, so ask your local program whether your benefit counts. Families on SNAP often have income under the limit anyway, so apply either way."),
("What age does a child have to be for Head Start?","Early Head Start is for babies and toddlers under 3 years old. Head Start Preschool is for children who are at least 3, or who turn 3 by the date your public school uses, and who are not yet old enough to have to be in school."),
("Which income counts for Head Start?","Gross income (money before tax) over the time period set in the rules. The program will tell you which months it needs and ask for proof, such as pay stubs or a tax return. If you cannot get proof, the program can use a written statement from your employer and work out the yearly amount from it."),
("How much does Head Start cost?","Nothing. Head Start and Early Head Start are free for eligible families."),
("Can I apply if my income is over the limit?","Yes. Children who meet none of the rules can fill up to 10% of a program's enrollment, and a program can take an extra 35% of families under 130% of the poverty line once it has served the families who qualify. Ask the local program – it decides who gets the places it has."),
("Does my child have to re-qualify every year?","No. A child who is taking part stays eligible through the end of the next program year, even if your income goes up. A program can still decide not to enroll a child again if it has a compelling reason."),
]

art='''<p class="note" style="margin-top:0">Hong Life is an independent guide, <b>not a government website</b>. Apply and confirm with your local Head Start program.</p>
<h2 id="limits">Head Start income limits 2026 (48 states and DC)</h2>
'''+table(['People in household','100% poverty line (income-eligible)','130% (may qualify)','100% line per month'],lim)+'''
<p class="note">From the 2026 HHS poverty guidelines: $15,960 for one person plus $5,680 for each extra person.</p>
<h2 id="akhi">Alaska and Hawaii limits 2026</h2>
'''+table(['People in household','Alaska 100%','Alaska 130%','Hawaii 100%','Hawaii 130%'],akhi)+'''
<p class="note">Alaska: $19,950 for one person plus $7,100 for each extra person. Hawaii: $18,360 plus $6,530. The calculator above uses the 48-state figures.</p>
<h2 id="ex">Examples: does my family qualify?</h2>
<div id="examples">'''+table(['Household','Income per year','% of poverty line','Result'],exs)+'''</div>
<ul><li><b>Family of 3 earning $26,000.</b> The limit is $27,320, so they are at 95% of the poverty line. The child is income-eligible.</li>
<li><b>Family of 5 earning $30,000.</b> The limit is $38,680. They are at 78%, well inside the limit.</li>
<li><b>Family of 4 earning $40,000.</b> That is 121% – over the 100% line of $33,000 but under the 130% line of $42,900. The program may enroll them once it has served the families who qualify.</li>
<li><b>Family of 2 earning $30,000.</b> That is 139%, above both lines. The child can still get in through the 10% allowance, or automatically if the family is on public assistance.</li></ul>
<p class="note">Examples use this calculator's own formula with the 2026 guidelines.</p>
<h2 id="how">Who qualifies (in plain words)</h2>
<p>A child can get a Head Start place in one of these ways:</p>
<ul><li><b>Low income.</b> Family income is at or below the poverty line (the "100% line" in the table).</li>
<li><b>Public assistance.</b> The family gets it, or would be able to get it if it were not for child care. This includes <b>TANF</b> child-only payments. TANF (Temporary Assistance for Needy Families) is cash help paid by your state.</li>
<li><b>Homeless</b> – for example, staying with others because you lost your home, or living in a shelter, motel or car.</li>
<li><b>Foster care.</b> Children in foster care are eligible.</li></ul>
<p>Programs can also fill places in two extra ways. A child who meets none of the rules above can still be enrolled if they would benefit from the program, as long as such children stay within <b>10% of the program's enrollment</b>. On top of that, a program can enroll <b>an extra 35%</b> of children from families under <b>130%</b> of the poverty line, but only after it has set up its outreach rules and served the families who qualify first.</p>
<p>There is a separate rule about disability. At least <b>10% of the places a program actually fills</b> must go to children who qualify for help under <b>IDEA</b> – the federal law that pays for special education and early intervention for children with disabilities.</p>
<h2 id="apply">How to apply</h2>
<ul><li>Find a program near you with the <a href="https://headstart.gov/center-locator" rel="nofollow">Head Start Center Locator</a>, then apply directly to that program.</li>
<li>Bring proof of income (pay stubs or a tax return), proof of public assistance if you get it, and the child's birth certificate or other proof of age.</li>
<li>Places are limited. If the program is full, ask to be put on the waiting list. Programs pick children by need, not first come first served.</li>
<li>Once a child is taking part, they stay eligible through the end of the next program year, even if your income goes up.</li></ul>
<h2 id="faq" style="margin-top:22px">Head Start FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines" rel="nofollow">HHS ASPE – 2026 Poverty Guidelines</a>; <a href="https://headstart.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibility" rel="nofollow">45 CFR 1302.12 – Determining, verifying and documenting eligibility</a>; <a href="https://www.headstart.gov/policy/45-cfr-chap-xiii/1302-14-selection-process" rel="nofollow">45 CFR 1302.14 – Selection process</a>. General information, not legal advice.</p>'''

out=build(P,'Head Start Income Limits 2026 – Eligibility Calculator by Family Size',
 'Does your child qualify for free Head Start? 2026 income limits by family size ($27,320 for 3), the 130% rule, ages and how to apply.',
 art,FAQ,form=form,calc=calc)
import re
_s=open(out,encoding='utf-8').read()
# the page's WebApplication JSON-LD and hero still carried the old (wrong) eligibility wording
_s=_s.replace('household income at or below the poverty level, or receiving SSI, TANF or SNAP-type public assistance.',
              'household income at or below the poverty line, or the family is on public assistance, homeless, or the child is in foster care.')
_s=re.sub(r'<p>Head Start serves children from birth to age 5[^<]*</p>',
          '<p>Head Start serves children from birth until they are old enough for school.</p>',_s,count=1)
open(out,'w',encoding='utf-8').write(_s)

add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','HHS poverty guidelines, 45 CFR 1302')],
 [('form','Calculator'),('limits','2026 income limits'),('akhi','Alaska and Hawaii'),('ex','Examples'),('how','Who qualifies'),('apply','How to apply'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
