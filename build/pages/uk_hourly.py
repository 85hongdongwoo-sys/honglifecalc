import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
H=37.5*52
rows=[[f'£{s:,}',f'£{s/H:,.2f}',f'£{s/(40*52):,.2f}',f'£{s/52:,.2f}',f'£{s/12:,.2f}'] for s in (20000,25000,30000,32000,35000,40000,45000,50000,60000,75000,100000)]
nmw=[['21 and over (National Living Wage)','£12.71','£13.21'],['18 to 20','£10.85','£11.27'],['16 to 17','£8.00','to be confirmed'],['Apprentice (under 19 or first year)','£8.00','to be confirmed']]
calc='''function calc(){const s=num('s'),h=num('h'),w=num('w'),hr=s/(h*w);return big('Hourly rate',gbp2(hr),'')+kv([['Daily (5 days)',gbp2(s/w/5)],['Weekly',gbp2(s/w)],['Monthly',gbp2(s/12)],['National Living Wage (21+, April 2026)','£12.71'],['National Living Wage (21+, from April 2027)','£13.21'],['Above the 2026 NLW?',hr>=12.71?'Yes':'No','t']])}'''
FAQ=[
("What is £30,000 a year per hour?","£15.38 an hour on a 37.5-hour week (1,950 hours a year), or £14.42 on a 40-hour week."),
("What is £32,000 a year per hour?","£16.41 an hour at 37.5 hours a week, £15.38 at 40 hours. Weekly pay is £615.38 and monthly pay £2,666.67 before tax."),
("How many working hours are in a year in the UK?","A 37.5-hour week is 1,950 paid hours (37.5 × 52) and a 40-hour week is 2,080. Paid holiday is included in these figures because an annual salary covers holiday pay."),
("What is the minimum wage in 2026 and 2027?","From 1 April 2026 the National Living Wage for workers aged 21 and over is £12.71 an hour and the 18–20 rate is £10.85. The government has announced £13.21 and £11.27 from April 2027."),
("What salary is the National Living Wage?","£12.71 × 1,950 hours = £24,784.50 a year on a 37.5-hour week, or £26,436.80 on a 40-hour week (2026/27 rate).")]
art='''<h2>How to convert a salary to an hourly rate</h2>
<p><b>Hourly rate = annual salary ÷ (hours per week × weeks paid per year).</b> In the UK an annual salary normally pays for all 52 weeks, including your paid holiday, so you divide by 52 — not by the weeks you actually work. A 37.5-hour week therefore has 1,950 paid hours a year; a 40-hour week has 2,080.</p>
<p>To go the other way, <b>salary = hourly rate × hours per week × 52</b>. Weekly pay is salary ÷ 52 and monthly pay is salary ÷ 12.</p>
<h3>Salary to hourly, weekly and monthly (before tax)</h3>
'''+table(['Annual salary','Hourly (37.5 h/wk)','Hourly (40 h/wk)','Weekly','Monthly'],rows)+'''
<h3>Minimum wage rates</h3>
'''+table(['Age band','From 1 April 2026','From April 2027 (announced)'],nmw)+'''
<p class="note">2027 rates for 21+ and 18–20 were announced in the Autumn Budget on 28 October 2026. Check GOV.UK for confirmed 16–17 and apprentice rates.</p>
<h3>Worked example</h3>
<p>£32,000 a year, 37.5 hours a week: 37.5 × 52 = 1,950 hours. £32,000 ÷ 1,950 = <b>£16.41 an hour</b>. Weekly: £32,000 ÷ 52 = £615.38. Monthly: £32,000 ÷ 12 = £2,666.67. Daily (5-day week): £123.08.</p>
<h3>Things that change the comparison</h3>
<ul><li><b>Paid holiday.</b> Full-time workers get at least 5.6 weeks (28 days including bank holidays). An hourly or day-rate job without holiday pay is worth less than the same rate on a salary.</li><li><b>Unpaid breaks.</b> If your contract is 40 hours on site with a 30-minute unpaid lunch, your paid hours are 37.5.</li><li><b>Overtime.</b> Paid overtime isn't included in salary; add it separately.</li><li><b>Pension and benefits.</b> Employer pension contributions (minimum 3% of qualifying earnings under auto-enrolment) and other benefits add to the value of a salaried job.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 20 Nov 2026): <a href="https://www.gov.uk/government/news/national-living-wage-increases-to-1271-per-hour" rel="nofollow">GOV.UK — National Living Wage increases to £12.71 per hour</a> (rates from 1 April 2026); Autumn Budget 28 October 2026 (£13.21 and £11.27 from April 2027); GOV.UK holiday entitlement (5.6 weeks). Gross figures before tax and National Insurance.</p>'''
print(build('/uk/salary-to-hourly-calculator.html','Salary to Hourly Calculator UK 2026 – Hourly, Weekly & Monthly Pay (and Back)',
 'Convert an annual UK salary to hourly, daily, weekly and monthly pay at 37.5 or 40 hours, with a full conversion table and the 2026 and 2027 National Living Wage.',art,FAQ,calc=calc))
print(rows[3])
