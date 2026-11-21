import sys,math; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
P='/us/benefits/free-school-meals.html'
calc='''function calc(){const n=Math.max(1,Math.round(num('n'))),f=FPL(n),i=num('i'),fr=Math.ceil(f*1.3),rp=Math.ceil(f*1.85);const t=i<=fr?'Free meals':i<=rp?'Reduced-price meals':'Full price';
 return big(t,pc(i/f)+' of the 2026 poverty guideline','Household of '+n+' · 48 states & DC')+kv([['Free (130%) — per year','up to '+usd(fr)],['Free — per month','up to '+usd(Math.ceil(fr/12))],['Reduced price (185%) — per year','up to '+usd(rp)],['Reduced price — per month','up to '+usd(Math.ceil(rp/12))],['Reduced price','no more than 40¢ for lunch, 30¢ for breakfast'],['Automatic','children in SNAP, TANF or FDPIR households, and foster, homeless, migrant, runaway or Head Start children','t']])+'<p class="note">Alaska and Hawaii have higher limits (see the table below). Use gross income before tax and deductions.</p>'}'''
FPL=lambda n:15960+5680*(n-1)
def r(n):
    fr=math.ceil(FPL(n)*1.3);rp=math.ceil(FPL(n)*1.85)
    return [str(n),f'${fr:,}',f'${math.ceil(fr/12):,}',f'${math.ceil(fr/52):,}',f'${rp:,}',f'${math.ceil(rp/12):,}',f'${math.ceil(rp/52):,}']
rows=[r(n) for n in range(1,9)]+[['Each extra person','+$7,384','+$616','+$142','+$10,508','+$876','+$203']]
FAQ=[
("What is the income limit for free school lunch for a family of 4 in 2026–27?","$42,900 a year ($3,575 a month) in the 48 states and DC. Up to $61,050 a year ($5,088 a month) qualifies for reduced-price meals. These limits apply from July 1, 2026 to June 30, 2027."),
("What is the free lunch income limit for a family of 3?","$35,516 a year or $2,960 a month (130% of the 2026 poverty guideline of $27,320). Reduced price: up to $50,542 a year or $4,212 a month."),
("How much do reduced-price meals cost?","Schools can charge no more than 40 cents for a lunch and 30 cents for a breakfast. Many states and districts cover that amount, so reduced-price students may pay nothing."),
("Do we qualify automatically if we get SNAP?","Yes. Children in households receiving SNAP, TANF or FDPIR are categorically eligible for free meals, and most are directly certified by the school district without an application. Foster, homeless, migrant, runaway and Head Start children also qualify."),
("Can I apply in the middle of the school year?","Yes. Federal rules require schools to accept an application at any time during the school year, for example after a job loss. Last year's status carries over for up to 30 operating days of the new school year."),
("Why does my school give free meals to everyone?","Schools using the Community Eligibility Provision (CEP) serve free breakfast and lunch to all students without applications. A school, group of schools or district can choose CEP when at least 25% of students are identified through programs like SNAP."),
]
art='''<h2>How eligibility is worked out</h2>
<p>USDA sets the limits each year from the HHS poverty guidelines: <b>free meals = household income up to 130% of the poverty guideline</b>, <b>reduced-price meals = up to 185%</b>, with the annual result rounded up to the next dollar. Monthly, twice-monthly, biweekly and weekly limits are the annual limit ÷ 12, 24, 26 or 52, also rounded up. The 2026 guideline for the 48 states and DC is $15,960 for one person plus $5,680 for each extra person.</p>
<h3>Income eligibility guidelines, July 1, 2026 – June 30, 2027 (48 states, DC, Guam and territories)</h3>
'''+table(['Household size','Free: year','Free: month','Free: week','Reduced: year','Reduced: month','Reduced: week'],rows)+'''
<p class="note">USDA Food and Nutrition Service, Federal Register notice of April 9, 2026. Family-of-four limits are 2.6% higher than last year.</p>
<h3>Alaska and Hawaii</h3>
'''+table(['State','2026 poverty guideline (1 person / each extra)','Free, 1 person (year)','Reduced, 1 person (year)'],[['Alaska','$19,950 / $7,100','$25,935','$36,908'],['Hawaii','$18,360 / $6,530','$23,868','$33,966']])+'''
<h3>Examples</h3>
'''+table(['Household','Income per year','% of poverty guideline','Result'],[
['2 people','$27,000','125%','Free meals'],
['3 people','$40,000','146%','Reduced-price meals'],
['4 people','$42,900','130%','Free meals (exactly at the limit)'],
['4 people','$60,000','182%','Reduced-price meals'],
['5 people','$75,000','194%','Full price'],
['6 people','$55,000','124%','Free meals'],
])+'''
<p class="note">Calculated with this page's formula for the 48 states and DC.</p>
<h3>What counts as income and household</h3>
<ul><li><b>Household</b>: everyone living together who shares income and expenses, related or not — not just parents and children.</li>
<li><b>Income</b>: gross income before taxes and deductions — wages, self-employment net income, child support, alimony, pensions, Social Security, unemployment benefits.</li>
<li><b>Pay frequency</b>: if your income varies, the school converts it to a yearly amount; you can compare your paycheck directly with the monthly or weekly column above.</li>
<li><b>No application needed</b> if your district directly certifies your children through SNAP, TANF or FDPIR — check with the school first.</li></ul>
<h3>How to apply</h3>
<p>Fill in the free and reduced-price meal application from your child’s school district (online or paper) at the start of the school year or any time your income drops. One application usually covers all children in the household at schools in the same district.</p>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked November 21, 2026): <a href="https://www.fna.usda.gov/schoolmeals/fr-040926" rel="nofollow">USDA FNS — Child Nutrition Programs: Income Eligibility Guidelines 2026–27</a>; <a href="https://www.govinfo.gov/content/pkg/FR-2026-01-15/html/2026-00755.htm" rel="nofollow">HHS — 2026 Poverty Guidelines (Federal Register, Jan 15, 2026)</a>; 7 CFR Part 245 (reduced-price charges, categorical eligibility, applications and carryover); <a href="https://www.fna.usda.gov/cn/cep-final-rule-summary" rel="nofollow">USDA FNS — Community Eligibility Provision (25% ISP)</a>. Hong Life is an independent guide, not a government website.</p>'''
print(build(P,'Free & Reduced Lunch Income Guidelines 2026–27 (Calculator)',
 'Check if your child qualifies for free or reduced-price school meals in 2026–27: USDA income limits by household size (yearly, monthly, weekly), Alaska and Hawaii, examples.',art,FAQ,calc=calc))
