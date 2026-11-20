import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
def pay(L,r,n=300):
    i=r/1200; return L*i/(1-(1+i)**-n)
inc=[30000,40000,50000,60000,70000,80000,100000]
rows=[[f'£{x:,}',f'£{int(x*4):,}',f'£{int(x*4.5):,}',f'£{int(x*5):,}',f'£{int(x*5.5):,}'] for x in inc]
pr=[[f'£{L:,}',f'£{pay(L,4.4):,.2f}',f'£{pay(L,4.4,360):,.2f}',f'£{pay(L,7.4):,.2f}'] for L in (150000,200000,250000,315000,400000)]
FAQ=[
("How much can I borrow on a £70,000 salary?","Most lenders cap lending at about 4–4.5 times income, so roughly £280,000–£315,000 with no other debts. Some lenders go to 5–5.5 times for higher earners or certain professions, which would be £350,000–£385,000. Loans, car finance and credit card balances reduce the figure."),
("How much can I borrow on a £50,000 salary?","About £200,000 at 4 times income and £225,000 at 4.5 times. At 4.4% over 25 years, a £225,000 mortgage costs about £1,238 a month."),
("Do lenders use joint income?","Yes. For a joint application most lenders add both gross incomes and apply the multiple to the total, then reduce it for each applicant's committed spending such as loans, childcare and credit cards."),
("Is 4.5 times salary the maximum?","Not by law. The Bank of England's Financial Policy Committee limits lending at 4.5 times income or more to 15% of new mortgages across the market. Since 28 October 2026 that 15% applies to the market as a whole rather than to each lender, so some lenders can offer more high-multiple loans as long as the total stays near 15%."),
("Why is my offer lower than 4.5 times my income?","Lenders run an affordability check on your actual spending and test whether you could still pay if rates rose. Debts, dependants, a small deposit, variable income (bonus, overtime, self-employed profits) and your credit file can all lower the amount.")]
art='''<h2>How much can you borrow? The two tests lenders use</h2>
<p><b>1. Income multiple.</b> Lenders usually start from a multiple of your gross annual income — most commonly 4 to 4.5 times. Higher multiples (5 to 5.5 times) are offered by some lenders for larger incomes, certain professions or bigger deposits.</p>
<p><b>2. Affordability.</b> They then check your real budget: committed spending (loans, car finance, credit cards, childcare), living costs and a "stress" interest rate above the product rate, to make sure the payment stays affordable if rates rise. Each lender sets its own stress rate.</p>
<p>This calculator applies your chosen multiple, then reduces the result by 24 months of your existing monthly credit payments — a simple stand-in for how commitments cut the amount a lender offers. It adds your deposit to show a property price, and works out the monthly repayment over 25 years at your rate and at a rate 3 points higher.</p>
<h3>Borrowing by income and multiple</h3>
'''+table(['Gross household income','4×','4.5×','5×','5.5×'],rows)+'''
<p class="note">Before deducting debts. Not every lender offers 5× or 5.5×; most applicants get 4–4.5×.</p>
<h3>Monthly repayment on common loan sizes (capital and interest)</h3>
'''+table(['Mortgage','4.4% over 25 years','4.4% over 30 years','Stress test: 7.4% over 25 years'],pr)+'''
<h3>Worked example</h3>
<p>Household income £70,000, £200 a month of loan payments, £40,000 deposit, 4.5× income, 4.4% rate:</p>
<ul><li>Income × 4.5 = £315,000.</li><li>Commitments: £200 × 24 = £4,800, so borrowing ≈ <b>£310,200</b>.</li><li>Property up to £350,200, loan-to-value 89% (a 90% LTV mortgage).</li><li>Repayment over 25 years ≈ <b>£1,706.63</b> a month; at 7.4% it would be about £2,272.21.</li></ul>
<h3>Deposit and loan-to-value (LTV)</h3>
'''+table(['Deposit','LTV','What it usually means'],[['5%','95%','Fewer products and higher rates; lenders are stricter on affordability'],['10%','90%','Wide choice; rates still above lower-LTV deals'],['15%','85%','Noticeably better rates'],['25% or more','75% or lower','Best rates; often more flexibility on income multiples']])+'''
<h3>The Bank of England 4.5× rule (updated October 2026)</h3>
<p>The Financial Policy Committee limits mortgages at <b>4.5 times income or more</b> to <b>15% of new mortgage lending</b>. From <b>28 October 2026</b> the regulators removed the separate 15% cap on each lender: the 15% now applies to the market in aggregate, measured each quarter, and lenders above 15% may be asked to bring their share down gradually if the total drifts above the limit. Lenders lending under £150 million a year (or fewer than 300 mortgages) are exempt. In practice this lets some lenders offer more high-multiple mortgages than before.</p>
<h3>How to improve what you can borrow</h3>
<ul><li>Clear or reduce loans and credit card balances before applying — each £100 a month of commitments can cut the offer by thousands of pounds.</li><li>Save a bigger deposit to drop into a lower LTV band.</li><li>Check your credit files with the main agencies and fix errors.</li><li>Show regular overtime, bonus or commission with payslips; many lenders count only part of variable pay.</li><li>Consider a longer term (30–35 years) to lower the monthly payment — you will pay more interest overall.</li><li>Speak to a whole-of-market mortgage broker; criteria differ widely between lenders.</li></ul>
<h3>Common mistakes</h3>
<ul><li>Assuming the income multiple is guaranteed — affordability checks often bring it down.</li><li>Forgetting buying costs: stamp duty, legal fees, survey and lender fees come on top of the deposit.</li><li>Using net (take-home) pay — lenders quote multiples of gross income.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 20 Nov 2026): <a href="https://www.bankofengland.co.uk/prudential-regulation/publication/2026/october/high-loan-to-income-lending-policy-statement" rel="nofollow">PRA/FCA PS19/26 — High loan to income lending</a> (15% aggregate limit at 4.5×+ income, firm-level cap removed from 28 October 2026, de minimis £150m / 300 loans); <a href="https://www.bankofengland.co.uk/prudential-regulation/key-initiatives/high-loan-to-income-lending" rel="nofollow">Bank of England — High LTI lending</a>; FCA Mortgage Conduct of Business (MCOB 11) responsible lending. Repayments use standard monthly amortisation. Estimates only — not mortgage advice.</p>'''
print(build('/uk/mortgage-affordability-calculator.html','Mortgage Affordability Calculator UK 2026 – How Much Can I Borrow? (4–5.5× Income)',
 'How much can I borrow for a mortgage in the UK? Income multiples (4×–5.5×), affordability and stress tests, monthly repayments and the Bank of England 4.5× rule as updated in October 2026.',art,FAQ))
