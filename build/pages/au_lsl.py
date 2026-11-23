import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/au/long-service-leave-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><style>.money::before{content:"$"}</style><label class="f"><span>State / territory</span><select id="st"><option value="NSW" selected>New South Wales</option><option value="VIC">Victoria</option><option value="QLD">Queensland</option><option value="WA">Western Australia</option><option value="SA">South Australia</option><option value="TAS">Tasmania</option><option value="ACT">Australian Capital Territory</option><option value="NT">Northern Territory</option></select><small>Use the state or territory you work in. Some industries (e.g. building and construction) have portable schemes with different rules.</small></label><label class="f"><span>Years of continuous service</span><input id="y" inputmode="decimal" value="12"><small>With the same employer. Use decimals for part years: 7 years 6 months = 7.5.</small></label><label class="f"><span>Ordinary weekly pay</span><div class="money"><input id="w" inputmode="decimal" value="1,800"></div><small>Your normal pay for a week, before tax, without overtime.</small></label></form>'''

calc='''function calc(){
 // q: years for first leave, f: weeks at q, r: weeks per year, b: later leave in 5-year blocks (5), QLD rule ('q') or continuous (0), p: years before any pro-rata payout, c: counts completed years only
 const R={NSW:{q:10,f:8.6667,r:.86667,b:5,p:5,c:0},VIC:{q:7,f:52/60*7,r:52/60,b:0,p:7,c:0},QLD:{q:10,f:8.6667,r:.86667,b:'q',p:7,c:0},WA:{q:10,f:8.6667,r:.86667,b:5,p:7,c:1},SA:{q:10,f:13,r:1.3,b:0,p:7,c:1},TAS:{q:10,f:8.6667,r:.86667,b:5,p:7,c:0},ACT:{q:7,f:6.0667,r:6.0667/7,b:0,p:5,c:0},NT:{q:10,f:13,r:1.3,b:5,p:7,c:1}};
 const WHY={NSW:'between 5 and 10 years only if your employer ends your job (not for serious and wilful misconduct), you resign because of illness, incapacity or a domestic or other pressing necessity, or you die',
  VIC:'nothing is paid before 7 years; after 7 years all accrued leave is paid out whatever the reason you leave',
  QLD:'between 7 and 10 years only for death, illness or a domestic or other pressing necessity, dismissal because of illness or for reasons not about your conduct, capacity or performance, or unfair dismissal',
  WA:'between 7 and 10 years for resignation, dismissal, redundancy or death – but not dismissal for serious misconduct; only completed years count',
  SA:'between 7 and 10 years for resignation, dismissal or redundancy – but not for serious and wilful misconduct or if you end the job unlawfully; only completed years count',
  TAS:'between 7 and 10 years if you reach retirement age, die, or your employer ends your job (not for serious and wilful misconduct); it may also apply if you leave because of illness, incapacity or a pressing necessity',
  ACT:'between 5 and 7 years if you leave because of illness, incapacity or a pressing necessity, at or after retiring age, on death, or if your employer ends your job (not for serious and wilful misconduct)',
  NT:'between 7 and 10 years if you reach retirement age, your employer ends your job (not for serious misconduct), or you leave because of illness, incapacity or a pressing necessity; only completed years count'};
 const s=$('st').value,l=R[s],y=Math.max(0,num('y')),w=num('w'),yy=l.c?Math.floor(y):y,acc=l.r*yy;
 let av=0;if(y>=l.q){av=l.b===5?l.f+Math.floor((y-l.q)/5)*5*l.r:(l.b==='q'?(y<15?l.f:acc):acc)}
 const wk=x=>x.toFixed(2)+' weeks';
 const pay=y<l.p?'Nothing yet – no pro-rata before '+l.p+' years':(y<l.q?wk(acc)+' ('+aud(acc*w,0)+') – only for certain reasons':wk(acc)+' ('+aud(acc*w,0)+')');
 return big(y>=l.q?'Long service leave accrued':'Accrued so far – not yet available to take',wk(acc),'worth about '+aud(acc*w,0)+' at your weekly pay')
 +kv([['Can take now',y>=l.q?wk(av)+' ('+aud(av*w,0)+')':'Not yet – first leave after '+l.q+' years ('+(l.q-y).toFixed(1)+' to go)'],['If you left today',pay],['Accrual rate',l.r.toFixed(4)+' weeks per year'],['First entitlement',l.f.toFixed(2)+' weeks after '+l.q+' years']])
 +'<p class="note">'+s+' pro-rata rule: '+WHY[s]+'. Estimate only – awards, agreements and portable schemes can differ.</p>'}'''

ex=[['NSW','10 years','$1,800','8.67 weeks','8.67 weeks','$15,600'],
    ['NSW','12 years','$1,800','10.40 weeks','8.67 weeks','$18,720'],
    ['Victoria','8 years','$1,500','6.93 weeks','6.93 weeks','$10,400'],
    ['Queensland','8 years','$1,600','6.93 weeks','0 (not yet)','$11,093 if you qualify'],
    ['South Australia','10 years','$1,800','13.00 weeks','13.00 weeks','$23,400'],
    ['Tasmania','17 years','$1,400','14.73 weeks','13.00 weeks','$20,627'],
    ['ACT','5 years','$1,500','4.33 weeks','0 (not yet)','$6,500 if you qualify']]

fig=[['New South Wales','8.67 weeks (2 months) after 10 years','4.33 weeks for each further 5 years','After 5 years, for certain reasons; after 10 years, any reason','No'],
     ['Victoria','6.07 weeks after 7 years (1 week per 60 weeks worked)','Keeps building at 1/60 – no waiting for blocks','After 7 years, any reason. Nothing before 7 years','Generally no'],
     ['Queensland','8.67 weeks after 10 years','4.33 more at 15 years, then no waiting period','After 7 years, for certain reasons; after 10 years, any reason','Only if an award or agreement allows it, or the QIRC orders it (hardship or compassionate reasons)'],
     ['Western Australia','8.67 weeks after 10 years','4.33 weeks for each further 5 years','After 7 years, any reason except dismissal for serious misconduct','–'],
     ['South Australia','13 weeks after 10 years','1.3 weeks for each further year','After 7 years, any reason except serious and wilful misconduct','By written agreement'],
     ['Tasmania','8.67 weeks after 10 years','4.33 weeks for each further 5 years','After 7 years, for certain reasons','By agreement'],
     ['ACT','6.07 weeks after 7 years','1/5 of a month (0.87 weeks) each further year','After 5 years, for certain reasons','–'],
     ['Northern Territory','13 weeks after 10 years','Leave for each further 5 years (1.3 weeks a year)','After 7 years, for certain reasons','No']]

FAQ=[
("How much long service leave do you get after 10 years?","In NSW, Queensland, WA and Tasmania it is 8.67 weeks (about 2 months). In South Australia and the Northern Territory it is 13 weeks. In Victoria and the ACT you have already qualified at 7 years, so by 10 years you have about 8.67 weeks."),
("How much long service leave after 7 years?","In Victoria and the ACT you can take it after 7 years: 6.07 weeks. In Victoria that is 1 week for every 60 weeks worked (364 ÷ 60 = 6.07). In most other states 7 years is when pro-rata payouts start if you leave, not when you can take leave."),
("What is pro-rata long service leave?","Pro-rata means a part payment for the years you have worked when your job ends before the full entitlement. Example: in NSW after 8 years, if your employer ends your job (not for serious and wilful misconduct), you are paid 8 × 0.8667 = 6.93 weeks. At $1,800 a week that is $12,480."),
("How is long service leave calculated?","Multiply your years of service by your state's rate, then by your ordinary weekly pay. In NSW the rate is 0.8667 weeks a year, so 12 years × 0.8667 = 10.4 weeks; at $1,800 a week that is $18,720 before tax. In SA and the NT the rate is 1.3 weeks a year."),
("Do casual workers get long service leave?","Yes, in every state and territory, if their work with one employer is continuous. Gaps can break it: in Victoria a gap of more than 12 weeks usually does, and in Queensland a break of more than 3 months may. In Tasmania casuals need regular work of at least 32 hours in each 4 weeks."),
("Can I cash out long service leave?","It depends on the state. NSW and the NT say no while you are still employed, and Victoria says generally no. South Australia and Tasmania allow it by agreement with your employer. Queensland allows it only if your award or agreement says so, or the Industrial Relations Commission orders it for hardship or compassionate reasons."),
]

def faq_block(faq):
    return '<h2 id="faq" style="margin-top:22px">Long service leave FAQ</h2>'+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faq)

art='''<h2 id="figures">Long service leave rules by state (2026)</h2>
<p>Long service leave is extra paid leave for staying a long time with the same employer. Each state and territory has its own law, so the rules depend on where you work.</p>
'''+table(['State / territory','First leave','Further leave','Paid out if you leave early (pro-rata)','Cash out while employed?'],fig)+'''
<p class="note">"Continuous service" means working for the same employer without a break that the law says ends your service. "–" means we could not confirm a simple rule on the official page. Pay is at your ordinary rate (no overtime).</p>
<h2 id="ex">Worked examples</h2>
<div id="examples">'''+table(['State','Service','Weekly pay','Leave accrued','Can take now','Value of accrued leave'],ex)+'''</div>
<ul><li>A worker in <b>NSW with 12 years</b> has built up 10.40 weeks. They can take 8.67 weeks now; the next 4.33 weeks unlock at 15 years. If they leave, all 10.40 weeks are paid out: $18,720 at $1,800 a week.</li>
<li>In <b>Victoria after 8 years</b> leave can be taken as soon as it builds up: 6.93 weeks, worth $10,400 at $1,500 a week.</li>
<li>In <b>Queensland after 8 years</b> there is no leave to take yet. If the job ends for a qualifying reason (for example, redundancy), 6.93 weeks are paid: $11,093 at $1,600 a week.</li>
<li>In <b>Tasmania after 17 years</b> 13 weeks can be taken (8.67 + 4.33). The extra 1.73 weeks for years 16–17 count if the job ends.</li></ul>
<p class="note">Worked out with this calculator's formula. Amounts are before tax.</p>
<h2 id="how">How long service leave is worked out</h2>
<p>First, an example. Sam works in NSW for 12 years and earns $1,800 a week. NSW gives 8.67 weeks for 10 years, which is 0.8667 weeks for each year. 12 × 0.8667 = 10.40 weeks. 10.40 × $1,800 = $18,720.</p>
<p>The same steps work everywhere:</p>
<ul><li><b>Weeks of leave</b> = years of service × your state's rate per year.</li>
<li><b>Rate per year</b> = 0.8667 weeks in NSW, Victoria, Queensland, WA, Tasmania and the ACT, or 1.3 weeks in SA and the NT.</li>
<li><b>Value</b> = weeks of leave × ordinary weekly pay.</li></ul>
<p><b>Qualifying period</b> means the years you must work before you can take leave: 7 years in Victoria and the ACT, 10 years everywhere else. In NSW, WA, Tasmania and the NT later leave comes in 5-year blocks. That is why the calculator shows both "accrued" (built up) and "can take now".</p>
<p><b>Ordinary weekly pay</b> is your normal pay for your usual hours. Some states average pay over a period if your hours changed, so check your state's rules if you went part-time or casual.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Check which law applies.</b> Some awards and enterprise agreements, and portable schemes in industries like construction, cleaning and community services, have their own rules.</li>
<li><b>Don't resign a few weeks too early.</b> In Queensland, NSW, Tasmania, the ACT and the NT, leaving before 10 years (7 in the ACT) only pays out for certain reasons. In NSW and Tasmania that does not include resigning just to change jobs.</li>
<li><b>Part years count in some states, not others.</b> WA, SA and the NT count completed years only.</li>
<li><b>Casual work counts</b> if it is regular and the gaps are not too long.</li>
<li><b>Payouts are taxed.</b> Long service leave paid when you leave is added to your income, so the amount you get is less than the figure here.</li>
<li><b>Keep records.</b> Your payslips and start date are your proof of continuous service.</li></ul>
'''+faq_block(FAQ)+'''
<p class="note">Sources (checked 23 November 2026): <a href="https://www.nsw.gov.au/employment/rights-responsibilities/leave/long-service-leave" rel="nofollow">NSW Government – Long service leave</a>; <a href="https://www.vic.gov.au/long-service-leave" rel="nofollow">Wage Inspectorate Victoria – Victoria's long service leave laws</a>; <a href="https://www.business.qld.gov.au/running-business/employing/legal-obligations/long-service-leave/entitlements" rel="nofollow">Business Queensland – Long service leave entitlements</a>; <a href="https://www.business.qld.gov.au/running-business/employing/legal-obligations/long-service-leave/cashing-in" rel="nofollow">Business Queensland – Cashing in long service leave</a>; <a href="https://www.wa.gov.au/organisation/private-sector-labour-relations/overview-of-long-service-leave-wa" rel="nofollow">WA Government – Overview of long service leave</a>; <a href="https://www.wa.gov.au/organisation/private-sector-labour-relations/long-service-leave-when-employment-ends" rel="nofollow">WA Government – Long service leave when employment ends</a>; <a href="https://www.safework.sa.gov.au/workers/wages-and-conditions/long-service-leave" rel="nofollow">SafeWork SA – Long service leave</a>; <a href="https://safework.sa.gov.au/workers/wages-and-conditions/long-service-leave/taking-leave" rel="nofollow">SafeWork SA – Pro-rata entitlement</a>; <a href="https://worksafe.tas.gov.au/topics/laws-and-compliance/long-service-leave" rel="nofollow">WorkSafe Tasmania – Long service leave</a>; <a href="https://worksafe.tas.gov.au/topics/laws-and-compliance/long-service-leave/pro-rata-long-service-leave" rel="nofollow">WorkSafe Tasmania – Pro rata long service leave</a>; <a href="https://www.worksafe.act.gov.au/__data/assets/pdf_file/0007/1673962/Long-Service-Leave-Guidance-Note.pdf" rel="nofollow">WorkSafe ACT – Long service leave guidance note</a>; <a href="https://nt.gov.au/employ/for-employees-in-nt/holidays-and-leave/long-service-leave" rel="nofollow">NT Government – Long service leave</a>; <a href="https://legislation.nt.gov.au/api/sitecore/Act/PDF?id=11975" rel="nofollow">Long Service Leave Act 1981 (NT)</a>. General information only, not legal advice.</p>'''

out=build(P,'Long Service Leave Calculator Australia 2026 – Every State & Territory',
 'Work out your long service leave in 2026: 8.67 weeks after 10 years in NSW, QLD, WA and TAS, 6.07 weeks after 7 in VIC and ACT, 13 weeks in SA and NT, plus pro-rata.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','23 November 2026'),('Sources','State and territory long service leave regulators')],
 [('form','Calculator'),('figures','Rules by state'),('ex','Worked examples'),('how','How it is worked out'),('tips','Tips and mistakes'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
