import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
P='/uk/net-worth-calculator.html'
FAQ=[
("What is the average net worth in the UK?","The latest ONS Wealth and Assets Survey (April 2020 to March 2022, published January 2025) puts median household total wealth in Great Britain at £293,700. That figure includes property, private pensions, financial and physical wealth, minus debts."),
("What net worth puts you in the top 10% in the UK?","According to the ONS, the wealthiest 10% of households had total wealth of £1,200,500 or more in April 2020 to March 2022; the top 1% had at least £3,121,500. The least wealthy 10% had £16,500 or less."),
("Should I include my pension in my net worth?","Yes, if you want a figure comparable with the ONS: private pension wealth is about 35% of all household wealth in Great Britain. Use the current transfer value or pot value from your latest pension statement. The State Pension is not included in ONS total wealth."),
("Should I include my home?","Include the current market value of your home as an asset and the mortgage balance as a debt — the difference is your home equity. Net property wealth makes up about 40% of household wealth in Great Britain."),
("What is a good debt-to-asset ratio?","There is no official target, but a falling ratio over time means you own more of what you have. With the default numbers above, debts of £169,600 against assets of £272,000 give a ratio of 62.4%, mostly the mortgage."),
("How often should I calculate my net worth?","Once or twice a year is enough for most people — for example at the start of each tax year (6 April). Use the same valuation method each time so the change is meaningful."),
]
art='''<h2>How net worth is calculated</h2>
<p><b>Net worth = total assets − total debts.</b> Assets are cash and savings, investments and pensions, the value of your home and other property, and other things you could sell (such as a car). Debts are your mortgage, loans and credit card balances. The calculator also shows your <b>debt-to-asset ratio</b> (debts ÷ assets).</p>
<h3>How UK households compare (ONS)</h3>
'''+table(['Measure (Great Britain, April 2020 – March 2022)','Household total wealth'],[
['Median household','£293,700'],
['Least wealthy 10%','£16,500 or less'],
['Wealthiest 10%','£1,200,500 or more'],
['Wealthiest 1%','£3,121,500 or more'],
['Median, household head aged 16–24','£15,200'],
['Median, household head aged 65–74 (peak)','£502,500'],
])+'''
'''+table(['Component','Share of all household wealth'],[['Net property wealth','40%'],['Private pension wealth','35%'],['Net financial wealth','14%'],['Physical wealth (contents, vehicles etc.)','10%']])+'''
<p class="note">ONS, Household total wealth in Great Britain: April 2020 to March 2022 (published 24 January 2025) — the latest release. ONS notes that accreditation of the Wealth and Assets Survey has been suspended from Round 8 and that pension wealth methods changed, so compare with earlier rounds carefully. Shares are rounded.</p>
<h3>Worked examples</h3>
'''+table(['Situation','Assets','Debts','Net worth','Debt-to-asset'],[
['Renter, 25, savings + workplace pension','£6,000 + £9,000 + car £3,000 = £18,000','Car loan £4,000 + card £1,000 = £5,000','£13,000','27.8%'],
['First-time buyer, 32','£5,000 + £30,000 + home £250,000 + £5,000 = £290,000','Mortgage £215,000 + loan £6,000 = £221,000','£69,000','76.2%'],
['Default figures above','£8,000 + £20,000 + £240,000 + £4,000 = £272,000','£160,000 + £8,000 + £1,600 = £169,600','£102,400','62.4%'],
['Homeowner, 55','£25,000 + £180,000 + home £400,000 + £10,000 = £615,000','Mortgage £60,000','£555,000','9.8%'],
['Retired, 68, mortgage-free','£40,000 + £150,000 + home £350,000 + £8,000 = £548,000','£0','£548,000','0%'],
])+'''
<p class="note">Calculated with this page's formula. Ages are illustrative.</p>
<h3>Tips for an accurate figure</h3>
<ul><li><b>Value your home realistically</b> — use recent sale prices of similar homes nearby, not the asking price.</li>
<li><b>Use pension pot values</b> from your latest statement or provider app (defined contribution). For a final-salary (defined benefit) pension, a transfer value is only an estimate.</li>
<li><b>Include every debt</b>: student loan balances are often left out; whether to include them is your choice, but be consistent.</li>
<li><b>Don't count the car at what you paid</b> — use a current trade-in value.</li>
<li><b>Cash is protected up to £120,000</b> per person per authorised bank or building society by the FSCS (from 1 December 2025), so spread larger sums across separately authorised firms.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 21 November 2026): <a href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest" rel="nofollow">ONS — Household total wealth in Great Britain: April 2020 to March 2022</a>; <a href="https://www.fscs.org.uk/what-we-cover/banks-building-societies-credit-unions/deposit-limit-increase/" rel="nofollow">FSCS — deposit limit increase to £120,000</a>. Not financial advice.</p>'''
print(build(P,'Net Worth Calculator UK 2026 – Assets Minus Debts vs ONS Median',
 'Work out your net worth (assets minus debts) and debt-to-asset ratio, and compare with ONS figures: median UK household wealth £293,700, top 10% from £1.2m. With examples.',art,FAQ))
