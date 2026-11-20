import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
def pr(f,h,fh=37.5,w=52): return f*h/fh*w/52
rows=[[f'£{f:,}']+[f'£{pr(f,h):,.0f}' for h in (15,18.75,22.5,30)] for f in (25000,30000,36000,40000,50000)]
FAQ=[
("What is £36,000 pro rata for 22.5 hours?","£21,600 a year if full time is 37.5 hours: £36,000 × 22.5 ÷ 37.5. That is £1,800 a month before tax and the same £18.46 hourly rate as the full-time job."),
("How do I calculate pro rata salary?","Divide your contracted hours by the full-time hours for the job and multiply by the full-time salary. For a role that only runs part of the year, also multiply by the weeks you are employed ÷ 52."),
("What does 0.6 FTE mean?","FTE (full-time equivalent) is your hours as a share of full time. 0.6 FTE on a 37.5-hour week is 22.5 hours, and you are paid 60% of the full-time salary."),
("How is holiday worked out for part-time workers?","Everyone is entitled to 5.6 weeks of paid holiday. For a regular pattern, multiply 5.6 by the days you work a week: 3 days a week gives 16.8 days (including bank holidays, pro rata)."),
("Do part-time workers have to be paid the same rate?","Yes. Under the Part-time Workers Regulations 2000 part-timers must not be treated less favourably than comparable full-timers on pay rates, holiday, pension and training, unless the employer can objectively justify it.")]
art='''<h2>How pro rata salary works</h2>
<p>"Pro rata" means in proportion. A job advertised at "£36,000 pro rata" pays £36,000 for full-time hours; you receive the share that matches your hours.</p>
<p><b>Pro rata salary = full-time salary × your weekly hours ÷ full-time weekly hours × weeks employed ÷ 52.</b> The hourly rate stays the same as the full-time job: full-time salary ÷ (full-time hours × 52).</p>
<h3>Pro rata salaries at a 37.5-hour full-time week</h3>
'''+table(['Full-time salary','15 h (0.4 FTE)','18.75 h (0.5 FTE)','22.5 h (0.6 FTE)','30 h (0.8 FTE)'],rows)+'''
<h3>Worked examples</h3>
<ul><li><b>Part-time hours:</b> £36,000 full time, 37.5-hour week, you work 22.5 hours → £36,000 × 22.5 ÷ 37.5 = <b>£21,600</b> a year (£1,800 a month).</li><li><b>Days instead of hours:</b> 3 days of a 5-day week → £36,000 × 3 ÷ 5 = £21,600.</li><li><b>Part of the year:</b> a 37.5-hour fixed-term contract for 26 weeks at £36,000 pro rata → £36,000 × 26 ÷ 52 = £18,000 for the contract.</li><li><b>Term-time only:</b> often paid as weeks worked plus holiday entitlement, spread over 12 months — check how your employer calculates it.</li></ul>
<h3>Pro rata holiday</h3>
'''+table(['Days worked per week','Statutory holiday (5.6 weeks)'],[['5','28 days'],['4','22.4 days'],['3','16.8 days'],['2','11.2 days'],['1','5.6 days']])+'''
<p class="note">Statutory entitlement can include bank holidays. Many employers give more; the extra is pro-rated in the same way.</p>
<h3>Things to check in a part-time offer</h3>
<ul><li>What full-time hours the employer uses (35, 37.5 or 40) — it changes your pay.</li><li>Whether bank holidays are pro-rated or given on the days they fall.</li><li>Pension: auto-enrolment applies once you earn over £10,000 a year with one employer.</li><li>Tax: your personal allowance (£12,570) isn't pro-rated, so a lower salary means a smaller share goes in tax.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 20 Nov 2026): ACAS — part-time workers' rights; Part-time Workers (Prevention of Less Favourable Treatment) Regulations 2000; GOV.UK holiday entitlement (5.6 weeks); GOV.UK workplace pensions (auto-enrolment earnings trigger £10,000). Gross pay before tax.</p>'''
print(build('/uk/pro-rata-salary-calculator.html','Pro Rata Salary Calculator UK – Part-Time Pay, FTE & Holiday',
 'Work out a pro rata salary for part-time hours or part of the year: formula, FTE table for common hours, monthly and hourly pay, and pro rata holiday entitlement.',art,FAQ))
print(rows)
