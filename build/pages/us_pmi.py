import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
FAQ=[
("How much is PMI per month?","Freddie Mac puts typical PMI at about $30–$70 a month for every $100,000 borrowed (roughly 0.36%–0.84% a year). Your quote depends mainly on credit score, down payment and loan type. On a $360,000 loan at 0.6% a year, PMI is $180 a month."),
("When does PMI go away?","You can ask your servicer in writing to cancel it once the balance is scheduled to reach 80% of the home's original value, if you are current and have a good payment history. It ends automatically when the balance is scheduled to reach 78%, and no later than the midpoint of the loan term (month 181 of a 30-year loan) if you are current."),
("How long will I pay PMI with 10% down?","At 6.4% on a 30-year loan, about 7 years 10 months until you can request removal (80%) and 9 years until automatic removal (78%). Extra principal payments shorten this."),
("Is PMI tax deductible in 2026?","Yes again from tax year 2026. The 2025 tax law (P.L. 119-21) treats mortgage insurance premiums on acquisition debt as deductible mortgage interest for people who itemize. The deduction shrinks by 10% for each $1,000 of AGI above $100,000 and is gone above $109,000 ($50,000 / $54,500 if married filing separately)."),
("Does an FHA loan have PMI?","No — FHA loans have their own mortgage insurance premium (MIP): an upfront premium plus an annual premium. With less than 10% down the annual MIP generally lasts for the life of the loan, so it does not drop off at 78% like PMI.")]
art='''<h2>How PMI works</h2>
<p><b>Private mortgage insurance (PMI)</b> protects the lender, not you, when a conventional loan has less than 20% down. It is usually added to your monthly payment as an annual percentage of the loan amount divided by 12. This calculator takes your home price, down payment, rate and PMI rate, builds the 30-year amortization schedule and finds the month when the balance reaches 80% and 78% of the purchase price.</p>
<p><b>Monthly PMI = loan amount × annual PMI rate ÷ 12.</b> Loan-to-value (LTV) = loan ÷ home price. PMI applies while LTV is above 80%.</p>
<h3>Typical monthly PMI by loan size</h3>
'''+table(['Loan amount','0.3% a year','0.6% a year','1.0% a year'],[['$200,000','$50','$100','$166.67'],['$300,000','$75','$150','$250'],['$400,000','$100','$200','$333.33'],['$500,000','$125','$250','$416.67']])+'''
<p class="note">Freddie Mac's guide: about $30–$70 a month per $100,000 borrowed. Higher credit scores and bigger down payments get the lower rates.</p>
<h3>Worked examples (30-year fixed at 6.4%)</h3>
'''+table(['Home price · down','Loan','PMI rate','Monthly PMI','Request removal (80%)','Automatic end (78%)','PMI paid in total'],[
['$400,000 · 10%','$360,000','0.6%','$180','7 yr 10 mo','9 yr 0 mo','$19,440'],
['$400,000 · 5%','$380,000','0.8%','$253.33','10 yr 3 mo','11 yr 2 mo','$33,947'],
['$400,000 · 15%','$340,000','0.45%','$127.50','4 yr 8 mo','6 yr 2 mo','$9,435'],
['$300,000 · 5%','$285,000','0.8%','$190','10 yr 3 mo','11 yr 2 mo','$25,460']])+'''
<p class="note">"Total" counts PMI until the automatic end at 78%. Asking for cancellation at 80% saves the months in between — about $2,520 in the first example.</p>
<h3>The three ways PMI ends (Homeowners Protection Act)</h3>
<ul><li><b>You ask at 80%.</b> Once the balance reaches (or is scheduled to reach) 80% of the original value, send the servicer a written request. You must be current, have a good payment history, and may have to show the home has not lost value and that there is no second mortgage on it.</li>
<li><b>Automatic at 78%.</b> PMI must end on the date the balance is first scheduled to reach 78% of the original value, if you are current on payments.</li>
<li><b>Final termination at the midpoint.</b> PMI can't be charged past the first month after the midpoint of the loan term (after 15 years on a 30-year loan) if you are current.</li></ul>
<p>"Original value" is the lower of the purchase price or the appraised value when you bought. Some lenders also let you remove PMI earlier based on a new appraisal after the home has risen in value — that is a lender policy, not the federal rule, and usually requires 2–5 years of seasoning.</p>
<h3>PMI vs. FHA mortgage insurance</h3>
'''+table(['','Conventional loan PMI','FHA loan MIP'],[['Who needs it','Less than 20% down','All FHA borrowers'],['Cost','Annual % of loan, priced by credit and down payment','Upfront premium plus annual premium'],['When it ends','Request at 80%, automatic at 78%','With under 10% down, usually the life of the loan; with 10%+ down, after 11 years'],['Usual way out','Pay down or ask for removal','Refinance into a conventional loan']])+'''
<h3>Ways to pay less PMI</h3>
<ul><li>Put down 20% if you can, or use a "piggyback" second loan (80-10-10) — compare the rate on the second loan with the PMI cost.</li><li>Improve your credit score before applying; PMI pricing tiers are steep below about 740.</li><li>Ask about lender-paid PMI (folded into a higher rate) if you expect to sell or refinance within a few years.</li><li>Make extra principal payments to reach 80% sooner, then request cancellation in writing.</li></ul>
<h3>Common mistakes</h3>
<ul><li>Waiting for automatic removal at 78% instead of asking at 80%.</li><li>Using today's market value — the federal rules use the original value.</li><li>Assuming FHA mortgage insurance drops off like PMI.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked Nov 20, 2026): <a href="https://law.justia.com/codes/us/title-12/chapter-49/sec-4902/" rel="nofollow">Homeowners Protection Act, 12 U.S.C. §4902</a> (borrower cancellation, automatic termination, final termination); <a href="https://myhome.freddiemac.com/buying/breaking-down-pmi" rel="nofollow">Freddie Mac — Breaking down PMI</a> ($30–$70 per $100,000 a month, automatic termination at 78%); P.L. 119-21 as summarized by <a href="https://tax.thomsonreuters.com/news/what-obbb-means-for-your-clients-itemized-deductions/" rel="nofollow">Thomson Reuters Tax</a> (mortgage insurance premiums deductible from 2026, AGI phase-out $100,000–$109,000). Estimates only — your lender's PMI quote and servicer records decide the actual dates.</p>'''
print(build('/us/pmi-calculator.html','PMI Calculator 2026 – Monthly PMI Cost & When PMI Ends (80% / 78% LTV)',
 'Estimate monthly private mortgage insurance on a conventional loan, the month you can cancel it (80%) and when it ends automatically (78%) — with 2026 rules and examples.',art,FAQ))
