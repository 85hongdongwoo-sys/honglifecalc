import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
P='/au/hourly-to-salary-calculator.html'
FAQ=[
("How much is $35 an hour per year in Australia?","$69,160 a year at 38 hours a week for 52 weeks ($2,660 a fortnight). After 2026-27 income tax, the low income tax offset and the 2% Medicare levy, take-home pay is about $56,509 a year or $2,173 a fortnight. Super of $8,299 (12%) is paid on top."),
("What is the minimum wage in Australia from 1 July 2026?","The national minimum wage is $26.44 an hour or $1,004.90 for a 38-hour week, up from $948.00 a week. Award- and agreement-free casual employees get at least a 25% casual loading on top. Many award rates are higher."),
("How many working hours are in a year in Australia?","A full-time week under the National Employment Standards is up to 38 hours, so a full year is 38 × 52 = 1,976 paid hours. Paid annual leave and public holidays are included in the 52 weeks."),
("Is $30 an hour a good wage?","$30 an hour full-time is $59,280 a year or $2,280 a fortnight before tax — about 13% above the national minimum wage of $26.44. Take-home is about $49,901 a year."),
("How do I convert a salary to an hourly rate?","Divide the annual salary by 1,976 (38 × 52). For example, $80,000 ÷ 1,976 = $40.49 an hour. If your package includes super, first divide by 1.12 to get the base salary."),
("What tax rates apply in 2026-27?","Resident rates: nil up to $18,200; 15% from $18,201 to $45,000 (down from 16%); 30% to $135,000; 37% to $190,000; 45% above. The Medicare levy of 2% is extra."),
]
art='''<h2>How to convert an hourly rate to a salary</h2>
<p><b>Annual salary = hourly rate × hours per week × paid weeks per year.</b> Monthly = annual ÷ 12, fortnightly = annual ÷ 26, weekly = annual ÷ 52. A full-time year is 38 × 52 = <b>1,976 hours</b>. Take-home pay uses 2026-27 resident tax rates, the low income tax offset and the Medicare levy. Super (12%) is paid by your employer on top unless your package is quoted “including super”.</p>
<h3>Hourly rates at 38 hours a week (2026-27)</h3>
'''+table(['Hourly rate','Per year','Per fortnight','Per week','Take-home per year','Take-home per fortnight','Super (12%)'],[
['$26.44 (minimum wage)','$52,245','$2,009','$1,005','$45,223','$1,739','$6,269'],
['$30','$59,280','$2,280','$1,140','$49,901','$1,919','$7,114'],
['$35','$69,160','$2,660','$1,330','$56,509','$2,173','$8,299'],
['$40','$79,040','$3,040','$1,520','$63,227','$2,432','$9,485'],
['$45','$88,920','$3,420','$1,710','$69,946','$2,690','$10,670'],
['$50','$98,800','$3,800','$1,900','$76,664','$2,949','$11,856'],
['$60','$118,560','$4,560','$2,280','$90,101','$3,465','$14,227'],
])+'''
<p class="note">Calculated with this page's formula (52 paid weeks, Australian resident, no HELP debt, no other income or deductions). Part-time example: $35 an hour for 20 hours a week is $36,400 a year, about $33,642 after tax. The official weekly minimum of $1,004.90 is set per week, so $26.44 × 38 rounds to $1,004.72.</p>
<h3>2026-27 official figures</h3>
'''+table(['Item','Figure'],[
['National minimum wage (from 1 July 2026)','$26.44 an hour · $1,004.90 a week (was $948.00)'],
['Award wage increase (Annual Wage Review 2025-26)','4.75%'],
['Casual loading (award/agreement-free)','at least 25%'],
['Full-time hours (National Employment Standards)','38 a week plus reasonable additional hours'],
['Tax-free threshold','$18,200'],
['15% bracket','$18,201 – $45,000 (16% in 2025-26)'],
['Medicare levy','2% (single low-income threshold $28,011 for 2025-26)'],
['Low income tax offset','up to $700, phased out by $66,667'],
['Super guarantee','12%'],
['Maximum contribution base 2026-27','$270,830 a year (replaces the quarterly base under Payday Super)'],
])+'''
<h3>Common mistakes</h3>
<ul><li><b>Using 40 hours instead of 38</b> — Australian full-time is usually 38 hours; check your award or agreement.</li>
<li><b>Comparing a casual rate with a permanent salary</b> — the 25% casual loading replaces paid leave and other entitlements, so a casual hourly rate should be higher.</li>
<li><b>Forgetting whether super is included</b> — “$80,000 including super” is a base salary of about $71,429.</li>
<li><b>Ignoring penalty rates and overtime</b> — weekend, night and overtime rates under awards are paid at higher multiples; add those hours separately.</li>
<li><b>Fewer paid weeks</b> — contractors without paid leave or public holidays should enter fewer weeks (for example 46–48).</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 21 November 2026): <a href="https://www.fairwork.gov.au/tools-and-resources/fact-sheets/minimum-workplace-entitlements/minimum-wages" rel="nofollow">Fair Work Ombudsman — Minimum wages</a>; <a href="https://www.fwc.gov.au/documents/resources/annual-wage-review-2026-decision-announcement.pdf" rel="nofollow">Fair Work Commission — Annual Wage Review 2025-26 decision announcement</a>; <a href="https://www.fairwork.gov.au/employment-conditions/hours-of-work-breaks-and-rosters/hours-of-work" rel="nofollow">Fair Work Ombudsman — Hours of work</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents" rel="nofollow">ATO — Tax rates for Australian residents</a>; <a href="https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/tax-offsets/low-income-tax-offset" rel="nofollow">ATO — Low income tax offset</a>; <a href="https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners" rel="nofollow">ATO — Medicare levy reduction</a>; <a href="https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds/super-guarantee" rel="nofollow">ATO — Super guarantee</a>; <a href="https://www.ato.gov.au/businesses-and-organisations/super-for-employers/paying-super-on-payday/what-payments-are-qualifying-earnings/maximum-contributions-base" rel="nofollow">ATO — Maximum contribution base</a>. Estimates only.</p>'''
print(build(P,'Hourly to Salary Calculator Australia 2026-27 – Annual, Fortnightly, Weekly Pay',
 'Convert an hourly rate to annual, monthly, fortnightly and weekly pay, with 2026-27 take-home pay after tax and Medicare, super on top, and the $26.44 minimum wage.',art,FAQ))
