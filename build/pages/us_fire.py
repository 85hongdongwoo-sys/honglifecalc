import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
sr=[['10%','52','42'],['15%','43','36'],['20%','37','31'],['25%','32','28'],['30%','28','25'],['40%','22','20'],['50%','17','15'],['60%','13','12'],['70%','9','9']]
fn=[[f'${sp:,}',f'${sp*25:,}',f'${round(sp/.035):,}',f'${round(sp/.0325):,}'] for sp in (30000,40000,50000,60000,80000,100000)]
FAQ=[
("What is my FIRE number?","Your yearly retirement spending divided by your safe withdrawal rate. At 4% that is 25 times spending: $1,000,000 for $40,000 a year, $1,250,000 for $50,000. At a more cautious 3.5% it is about 28.6 times."),
("How many years until I can retire early?","It depends mostly on your savings rate. Starting from zero with a 5% real return and a 4% withdrawal rate, saving 25% of take-home pay takes about 32 years, 50% about 17 years and 70% about 9 years."),
("Is the 4% rule safe for early retirement?","It was designed for 30-year retirements using U.S. historical returns. Retirements of 40–50 years have had more failures at 4%, so many early retirees plan on 3.25%–3.5%, keep flexible spending, or plan to earn some income."),
("What is Coast FI?","The point where your current investments, with no more contributions, will grow to your FIRE number by a traditional retirement age. With a $1.25 million target, 5% real growth and 33 years to age 65, that is about $250,000 today."),
("How do early retirees access 401(k) money before 59½?","Common routes are a Roth conversion ladder (converted amounts can be withdrawn after five years), substantially equal periodic payments under section 72(t), the Rule of 55 for a 401(k) from an employer you leave in or after the year you turn 55, and taxable brokerage accounts.")]
art='''<h2>The FIRE number</h2>
<p>Your FIRE (Financial Independence, Retire Early) number is the portfolio that can pay your yearly spending for a long retirement: <b>FIRE number = annual spending ÷ safe withdrawal rate</b>. At 4%, that is 25× your annual spending — $1.25 million for $50,000 a year.</p>
<p>This calculator grows your current investments at your real (after-inflation) return, adds your yearly savings at the end of each year, and counts the years until the balance reaches the FIRE number. Working in real returns keeps every figure in today's dollars.</p>
<h3>FIRE number by spending and withdrawal rate</h3>
'''+table(['Yearly spending','4% (25×)','3.5% (28.6×)','3.25% (30.8×)'],fn)+'''
<h3>Years to FIRE by savings rate (starting from $0)</h3>
'''+table(['Savings rate (of take-home pay)','Years at 5% real return','Years at 7% real return'],sr)+'''
<p class="note">Assumes you spend everything you don't save, both before and after retiring, and a 4% withdrawal rate. A higher savings rate helps twice: more goes in, and the spending you must replace is smaller.</p>
<h3>Worked example (the default inputs)</h3>
<ul><li>Spending $50,000 a year at 4% → FIRE number <b>$1,250,000</b>.</li><li>$120,000 invested today is 9.6% of the goal.</li><li>Saving $30,000 a year at a 5% real return reaches the goal in about <b>20 years</b> — age 52 for a 32-year-old.</li><li>Coast FI: $1,250,000 ÷ 1.05<sup>33</sup> ≈ $250,000 would grow to the target by 65 with no further saving.</li></ul>
<h3>Lean, regular, Fat and Barista FIRE</h3>
'''+table(['Type','Idea','Target at 4%'],[['Lean FIRE','Bare-bones budget','About 25× a minimal budget (this calculator shows 0.7 × your spending)'],['FIRE','Your normal spending','25× spending'],['Fat FIRE','Comfortable, higher spending','This calculator shows 1.5 × your spending'],['Barista FIRE','Part-time work covers some costs (often health insurance)','25× the gap your part-time income doesn’t cover'],['Coast FI','Stop saving, let growth finish the job by 65','FIRE number ÷ (1 + real return)<sup>years to 65</sup>']])+'''
<h3>What the 4% rule is based on</h3>
<p>The rule comes from William Bengen's 1994 study and the 1998 "Trinity study" (Cooley, Hubbard and Walz), which tested withdrawing a fixed inflation-adjusted amount from U.S. stock and bond portfolios. A 4% initial withdrawal survived nearly all historical 30-year periods with a stock-heavy mix. For 40–50-year early retirements, lower rates (3.25%–3.5%) or flexible spending rules give a bigger margin, mainly because of <b>sequence-of-returns risk</b> — a market crash in the first years of retirement does the most damage.</p>
<h3>Costs early retirees often underestimate</h3>
<ul><li><b>Health insurance before Medicare at 65</b> — usually an ACA marketplace plan, where premium tax credits depend on your income.</li><li><b>Taxes on withdrawals</b> from traditional 401(k)/IRA money; Roth and long-term capital gains can be taxed lower.</li><li><b>Early-withdrawal penalty</b>: 10% on retirement-account withdrawals before 59½ unless an exception applies.</li><li>Big irregular costs: cars, home repairs, helping family.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources: Bengen, W. P. (1994), "Determining Withdrawal Rates Using Historical Data", Journal of Financial Planning; Cooley, Hubbard &amp; Walz (1998), "Retirement Savings: Choosing a Withdrawal Rate That Is Sustainable", AAII Journal; IRS — exceptions to the 10% additional tax on early distributions (72(t), age-55 separation); IRS Publication 590-B (Roth conversions and the five-year rule). Projections assume a constant return; real markets vary. Not investment advice.</p>'''
print(build('/us/fire-calculator.html','FIRE Calculator – Your FIRE Number, Years to Retire Early & Coast FI (4% Rule)',
 'Find your FIRE number (25× spending at 4%), how many years until you can retire early at your savings rate, Coast FI, Lean and Fat FIRE targets — with savings-rate tables and the research behind the 4% rule.',art,FAQ))
