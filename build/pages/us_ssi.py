import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
FAQ=[
("How much is SSI in 2027?","The federal maximum is $1,029 a month for an eligible individual and $1,544 for an eligible couple, after the 3.6% cost-of-living adjustment announced on October 14, 2026. In 2026 it was $994 and $1,491. Many states add a supplement."),
("When is the first 2027 SSI payment?","SSI is normally paid on the 1st of the month. Because January 1, 2027 is a holiday, the January payment — the first at the new rate — is paid on December 31, 2026."),
("How much can I earn and still get SSI?","SSA ignores the first $20 of most income, the next $65 of earnings and half of the earnings above that. With no other income, an individual's federal SSI only reaches zero at about $2,143 a month of wages in 2027 ($1,029 × 2 + $85)."),
("Does Social Security reduce my SSI?","Yes. Social Security retirement or disability benefits are unearned income, so after the $20 general exclusion they reduce SSI dollar for dollar. $400 of Social Security leaves about $649 of federal SSI in 2027."),
("What is the SSI resource limit?","$2,000 for an individual and $3,000 for a couple. Your home, one vehicle, household goods and some other items don't count.")]
ex=[['None','$0','$0','$1,029'],['$400 Social Security','$380','$0','$649'],['$800 Social Security','$780','$0','$249'],['$800 wages','$0','$357.50','$671.50'],['$1,500 wages','$0','$707.50','$321.50'],['$300 Social Security + $600 wages','$280','$267.50','$481.50']]
art='''<p class="note" style="margin-top:0">ℹ️ Hong Life is an independent guide, <b>not a government website</b>. Always apply and confirm through the Social Security Administration.</p>
<h2>How the SSI payment is calculated</h2>
<p>Supplemental Security Income pays the <b>federal benefit rate</b> minus your <b>countable income</b>. Countable income is worked out in this order:</p>
<ol><li>Take unearned income (Social Security, pensions, unemployment, support from others) and subtract the <b>$20 general exclusion</b>.</li><li>From earned income (wages, self-employment) subtract any unused part of the $20, then <b>$65</b>, then <b>half of the rest</b>.</li><li>Add the two countable amounts and subtract them from $1,029 (individual) or $1,544 (couple).</li></ol>
<h3>2026 and 2027 federal SSI amounts</h3>
'''+table(['','2026','2027 (3.6% COLA)'],[['Eligible individual','$994','$1,029'],['Eligible couple','$1,491','$1,544'],['Resource limit — individual','$2,000','$2,000'],['Resource limit — couple','$3,000','$3,000']])+'''
<h3>Worked examples — individual, 2027</h3>
'''+table(['Other monthly income','Countable unearned','Countable earned','Federal SSI'],ex)+'''
<p class="note">$800 of wages: (800 − 20 − 65) ÷ 2 = $357.50 countable, so SSI = 1,029 − 357.50. A state supplement, if any, is added on top.</p>
<h3>Things that can lower or stop the payment</h3>
<ul><li><b>Living in someone else's household</b> and not paying your share of shelter costs can cut the federal rate by one-third.</li><li><b>Free shelter</b> from others can be counted as in-kind support (food is no longer counted since September 30, 2024).</li><li><b>Deeming</b>: part of a spouse's or (for a child) parents' income and resources counts as yours.</li><li><b>Resources over the limit</b> on the first day of the month mean no SSI for that month.</li><li>Living in a public institution or medical facility usually limits SSI to $30 a month.</li></ul>
<h3>Who can get SSI</h3>
<ul><li>People aged 65 or older, or blind, or disabled (adults and children).</li><li>Limited income and resources (see above).</li><li>U.S. citizens or certain qualified non-citizens, living in the U.S.</li></ul>
<h3>How to apply</h3>
<p>Apply at <a href="https://www.ssa.gov/ssi" rel="nofollow">ssa.gov/ssi</a>, call 1-800-772-1213 (TTY 1-800-325-0778), or visit a local Social Security office. Report changes in income, resources or living arrangements by the 10th of the following month.</p>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 20 Nov 2026): <a href="https://www.ssa.gov/news/en/press/releases/2026-10-14.html" rel="nofollow">SSA press release, October 14, 2026 — 3.6% benefit increase for 2027</a>; <a href="https://www.ssa.gov/OACT/COLA/SSI.html" rel="nofollow">SSA — SSI federal payment amounts</a>; SSA Understanding SSI (income exclusions, resources, living arrangements, in-kind support rule effective September 30, 2024). Federal amounts only; state supplements vary.</p>'''
print(build('/us/benefits/ssi-benefit.html','SSI Payment Calculator 2027 – $1,029 a Month (3.6% COLA) and How Income Reduces It',
 'Estimate your 2027 Supplemental Security Income: $1,029 individual / $1,544 couple, the $20 and $65 income exclusions, worked examples with Social Security and wages, resource limits and how to apply.',art,FAQ))
