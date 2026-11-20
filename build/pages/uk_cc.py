import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
def cc(b,apr,p):
    i=(1+apr/100)**(1/12)-1;m=0;t=0
    while b>0 and m<1200:
        ii=b*i
        if p<=ii: return None
        t+=ii;b=b+ii-p;m+=1
    return m,t
def minpay(b,apr):
    i=(1+apr/100)**(1/12)-1;m=0;t=0
    while b>0.005 and m<1200:
        ii=b*i;p=max(25,ii+0.01*b);p=min(p,b+ii);t+=ii;b=b+ii-p;m+=1
    return m,t
def ym(m): return f'{m//12} yr {m%12} mo' if m>=12 else f'{m} mo'
rows=[]
for p in (100,150,200,250,350):
    m,t=cc(3500,24.9,p); rows.append([f'£{p}',f'{m} months ({ym(m)})',f'£{t:,.0f}',f'£{3500+t:,.0f}'])
mm,mt=minpay(3500,24.9)
rows.append(['Minimum only (interest + 1%, at least £25)',f'{mm} months ({ym(mm)})',f'£{mt:,.0f}',f'£{3500+mt:,.0f}'])
apr=[]
for a in (0,19.9,24.9,29.9,34.9):
    r=cc(3500,a,150) if a else (round(3500/150+.4999),0)
    m,t=r if a else (24,0)
    apr.append([f'{a}%' if a else '0% (balance transfer, no fee)',f'{m} months',f'£{t:,.0f}'])
FAQ=[
("How long will it take to pay off £3,500 on a credit card?","At 24.9% APR, paying £150 a month clears it in 31 months with about £1,142 of interest. Paying £250 a month cuts that to 17 months and about £596 of interest."),
("Why does paying the minimum take so long?","UK minimum payments must cover at least the interest, fees and 1% of the balance, so most of each payment goes on interest. On £3,500 at 24.9%, paying only that minimum (at least £25) takes about "+ym(mm)+" and costs around £"+f"{mt:,.0f}"+" in interest."),
("What is persistent debt?","If over 18 months you pay more in interest, fees and charges than you repay of the balance, your card is in persistent debt. The lender must contact you then, again at 27 months, and at 36 months offer ways to clear the balance in a reasonable period — typically 3 to 4 years. If you can't, it may suspend the card."),
("Is a 0% balance transfer worth it?","Usually, if you clear the balance before the 0% period ends. On £3,500 a 3% transfer fee is £105, against about £1,142 of interest at 24.9% when paying £150 a month. Missing a payment can end the 0% rate early."),
("How is credit card interest worked out?","This calculator converts the APR to a monthly rate ((1 + APR)<sup>1/12</sup> − 1, about 1.87% a month at 24.9%) and adds interest to the remaining balance each month. Card issuers usually charge daily interest on the balance, so their figures differ slightly.")]
art='''<h2>How long to clear your card — and what it costs</h2>
<p>Each month the card adds interest to what you owe, then your payment comes off. The bigger the share of your payment that goes to the balance rather than interest, the faster you clear it. This calculator repeats that month by month until the balance reaches zero, and warns you if your payment doesn't even cover the interest.</p>
<h3>£3,500 at 24.9% APR: effect of the monthly payment</h3>
'''+table(['Monthly payment','Time to clear','Total interest','Total paid'],rows)+'''
<h3>£150 a month on £3,500: effect of the APR</h3>
'''+table(['APR','Time to clear','Total interest'],apr)+'''
<p class="note">0% row ignores any transfer fee (commonly around 2–4% of the balance) and assumes the 0% lasts the whole time.</p>
<h3>UK rules that protect you</h3>
<ul><li><b>Minimum payment floor.</b> The FCA requires the minimum payment to cover at least interest, fees and charges plus 1% of the balance, so the balance always goes down a little.</li>
<li><b>Persistent debt reviews.</b> After 18 months of paying more in interest and charges than in capital, the lender must tell you and suggest increasing payments. It checks again at 27 months. At 36 months it must offer a way to repay within a reasonable period (typically 3–4 years) — and may suspend the card if you can't.</li></ul>
<h3>Fastest ways to clear a card</h3>
<ul><li><b>Fix a payment amount</b> rather than paying the minimum — the minimum falls as the balance falls, which stretches the debt out.</li><li><b>Move it to 0%</b> with a balance transfer card, then divide the balance by the number of 0% months and pay at least that.</li><li><b>Avalanche method</b>: clear the highest-APR card first while paying minimums on the rest.</li><li>If you're struggling, free debt advice is available from MoneyHelper, StepChange and Citizens Advice.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 20 Nov 2026): <a href="https://www.fca.org.uk/publication/policy/ps18-04.pdf" rel="nofollow">FCA PS18/4 — Credit card market study: persistent debt and earlier intervention</a> (18/27/36-month steps, repayment over a reasonable period); FCA Consumer Credit sourcebook CONC 6.7 (minimum repayment covering interest, fees and 1% of the balance); <a href="https://www.tescobank.com/help/persistent-debt/" rel="nofollow">Example lender explanation of persistent debt</a>. Calculations use a monthly rate derived from the APR; your statement may differ slightly. Not financial advice.</p>'''
print(build('/uk/credit-card-repayment-calculator.html','Credit Card Repayment Calculator UK 2026 – How Long to Pay Off & Total Interest',
 'How long will it take to clear your credit card? Months to pay off and total interest by payment and APR, minimum-payment trap, persistent debt rules and 0% balance transfers.',art,FAQ))
print(rows,apr)
