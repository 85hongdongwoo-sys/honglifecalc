import sys, json, subprocess, re; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
D='/home/claude/honglifecalc/build/pages/'
P='/en/korea-salary-calculator.html'
ENG=open(D+'kr_engine.js').read(); REN=open(D+'hl_render_local.js').read()
def run(**v):
    js=("const m={exports:{}};new Function('module',"+json.dumps(ENG+'})();')+")(m);"
        "process.stdout.write(JSON.stringify(m.exports.run("+json.dumps(v)+")._n))")
    return json.loads(subprocess.check_output(['node','-e',js]))
W=lambda n:'₩'+f'{round(n):,}'
def M(n): return f'₩{n/1e6:.2f}M'
ex=[]
for g in (30e6,42e6,60e6,100e6):
    r=run(g=g,nt=200000,deps=0,yr='2026',flat=False)
    ded=r['pen']+r['h']+r['care']+r['emp']+r['tax']
    ex.append([f'₩{g/1e6:.0f}M',W(r['pen']+r['h']+r['care']+r['emp']),W(r['tax']),W(r['net']),W(r['net']/12),f"{r['net']/g*100:.1f}%"])
r42=run(g=42e6,nt=200000,deps=0,yr='2026',flat=False); r42b=run(g=42e6,nt=200000,deps=0,yr='2027',flat=False)
r42d=run(g=42e6,nt=200000,deps=1,yr='2026',flat=False)
r30=run(g=30e6,nt=200000,deps=0,yr='2026',flat=False)
r60=run(g=60e6,nt=200000,deps=0,yr='2026',flat=False); r100=run(g=100e6,nt=200000,deps=0,yr='2026',flat=False)
flat=[]
for g in (60e6,100e6,150e6,200e6,300e6):
    r=run(g=g,nt=200000,deps=0,yr='2026',flat=True)
    flat.append([f'₩{g/1e6:.0f}M',W(r['net']/12),W(r['netFlat']/12),'Flat 19%' if r['netFlat']>r['net'] else 'Progressive'])
br42=[['National Pension (4.75%)',W(r42['pen'])],['Health insurance (3.595%)',W(r42['h'])],['Long-term care (13.14% of health)',W(r42['care'])],['Employment insurance (0.9%)',W(r42['emp'])],['Income tax + 10% local tax',W(r42['tax'])],['<b>Take-home per year</b>','<b>'+W(r42['net'])+'</b>'],['<b>Per month</b>','<b>'+W(r42['net']/12)+'</b>']]

FAQ=[
("What is the take-home pay on a 42 million won salary in Korea?",f"About {W(r42['net']/12)} a month in 2026 for a single employee with the ₩200,000 non-taxable meal allowance ({W(r42['net'])} a year, {r42['net']/42e6*100:.1f}% of gross). In 2027 it is about {W(r42b['net']/12)} a month because the National Pension rate rises by the legislated 0.5-point annual step (employee 5%) and the long-term care rate goes up."),
("How much is deducted from a Korean salary?","Employees pay National Pension 4.75% (2026; the total rate rises 0.5 points a year, so 5% for employees in 2027), health insurance 3.595%, long-term care insurance (13.14% of the health premium in 2026) and employment insurance 0.9%, plus income tax and local income tax (10% of the income tax). Social insurance alone is about 9.4% of taxable pay in 2026."),
("Do foreigners pay National Pension in Korea?","Foreign employees are generally covered in the same way as Koreans, unless their home country has a social security agreement or does not offer reciprocal coverage. Depending on nationality, contributions can be refunded as a lump sum when you leave Korea — see the pension refund calculator."),
("When is the 19% flat tax better for foreigners?",f"Only at high salaries. Because the flat rate (20.9% with local tax) applies to total pay with no deductions or credits, in this calculator's own computation it beats the progressive rates from about ₩168 million a year for a single employee (2026). At ₩100 million the progressive system leaves about {W((r100['net'])/12)} a month versus {W(run(g=100e6,nt=200000,deps=0,yr='2026',flat=True)['netFlat']/12)} under the flat rate."),
("Is the meal allowance taxable in Korea?","A meal allowance of up to ₩200,000 a month is non-taxable for employees who are not also given free meals at work, so it is also excluded from National Pension, health and employment insurance in this calculator. Anything above ₩200,000 is taxable."),
("Why is my monthly payslip different from the calculator?","Employers withhold income tax each month using the simplified withholding table (간이세액표), and the true figure is settled in the year-end tax settlement in February, when credits such as the child tax credit, card spending deductions and rent credits are applied. Social insurance is also based on the previous year's reported pay until it is recalculated.")]

art='''<h2>How Korean take-home pay is calculated (2026–2027)</h2>
<p>Take-home pay = gross salary − four social insurances − income tax − local income tax. Social insurance is charged on taxable pay (salary minus non-taxable items such as the meal allowance of up to ₩200,000 a month). Income tax is worked out on the year: earned income deduction → personal and insurance deductions → progressive tax rates → earned income tax credit, then 10% local income tax is added on top.</p>
<h3>Employee contribution rates</h3>
'''+table(['Deduction','2026 employee rate','2027 employee rate','Notes'],[
['National Pension','4.75%','5.0% (legislated +0.5%p step)','Total rate 9.5% in 2026 (from 9%), rising 0.5 percentage points a year to 13% in 2033. Monthly income floor/ceiling ₩410,000 / ₩6,590,000 from July 2026 to June 2027 (previously ₩400,000 / ₩6,370,000)'],
['Health insurance','3.595%','3.595%','Total 7.19%, half paid by the employer; frozen for 2027'],
['Long-term care insurance','13.14% of the health premium','13.90% of the health premium','0.9448% of pay in total in 2026; 0.9994% for 2027 (decided 30 October 2026)'],
['Employment insurance','0.9%','0.9%','Unemployment-benefit rate 1.8% split equally. A rise to 2.0% (0.1 point more each) from 2027 has been proposed but is not yet enacted, so 0.9% is used for both years'],
['Local income tax','10% of income tax','10% of income tax','Paid with the income tax']])+'''
<h3>Income tax</h3>
<p>Income tax is a progressive national income tax on taxable earned income, after the earned income deduction, a basic deduction for you and each dependent, and your pension and insurance contributions; the earned income tax credit is then subtracted. A local income tax of 10% of the income tax is added on top. The calculator applies the current rate schedule internally.</p>
<h3>Example: ₩42 million salary, single, 2026</h3>
'''+table(['Item','Per year'],br42)+'''
<h3>Take-home pay at common salaries (2026, single, ₩200,000 meal allowance)</h3>
'''+table(['Gross salary','Social insurance','Income tax + local','Take-home per year','Per month','Share kept'],ex)+f'''
<p class="note">Dependents lower the tax: at ₩42M, one dependent (₩1.5M extra basic deduction) raises take-home pay to about {W(r42d['net']/12)} a month. Child tax credits are not included.</p>
<h3>19% flat tax for foreign employees</h3>
<p>Foreign employees can elect a single 19% income tax rate (20.9% with local tax) on their total pay — including non-taxable allowances — for a limited period after they first start work in Korea. No deductions or credits apply, so it only pays off at high salaries. You choose it each year on the withholding application and in the year-end settlement.</p>
'''+table(['Gross salary','Monthly, progressive','Monthly, 19% flat','Better option'],flat)+'''
<h3>Tips and common mistakes</h3>
<ul><li><b>Use annual pay including bonuses.</b> Social insurance and tax are calculated on everything you are paid in the year; a monthly figure × 12 understates take-home pay if bonuses are paid separately.</li>
<li><b>The meal allowance is capped.</b> Only ₩200,000 a month is non-taxable, and not if the company also provides free meals.</li>
<li><b>Payslip tax is provisional.</b> The monthly withholding can be set at 80%, 100% or 120% of the table amount; the year-end settlement in February corrects it.</li>
<li><b>Pension refunds depend on nationality.</b> Check whether your country has a lump-sum refund arrangement before counting National Pension as a pure cost.</li></ul>
'''+faq_html(FAQ,'Frequently asked questions')+'''
<p class="note">Sources (checked 22 Nov 2026): <a href="https://www.newsis.com/view/NISX20251229_0003457395" rel="nofollow">Ministry of Health and Welfare via Newsis — National Pension 9.5% from 2026</a>; <a href="https://www.nps.or.kr/pnsgdnc/newgdnc/getOHAE0001M1.do?pstId=ZZ202600000000000147" rel="nofollow">National Pension Service — income floor and ceiling from July 2026</a>; <a href="https://www.korea.kr/policy/civilView.do?newsId=156780681" rel="nofollow">korea.kr — health insurance rate 7.19%, frozen for 2027</a>; <a href="https://www.mohw.go.kr/board.es?mid=a10503010100&amp;bid=0027&amp;act=view&amp;list_no=1487817" rel="nofollow">Ministry of Health and Welfare — 2026 long-term care rate 0.9448%</a>; <a href="https://www.korea.kr/news/policyNewsView.do?newsId=148974757" rel="nofollow">korea.kr — 2027 long-term care rate 0.9994%</a>; Income Tax Act and Restriction of Special Taxation Act on <a href="https://www.law.go.kr" rel="nofollow">law.go.kr</a>. Estimates only; not tax advice.</p>'''

html_engine='<script>\n'+ENG+REN+'build(spec);\n})();\n</script>'
out=build(P,'Korea Salary Calculator 2026–2027 – Take-Home Pay for Foreigners',
 'Work out monthly take-home pay in Korea for 2026 and 2027: National Pension 4.75%/5%, health 3.595%, long-term care, employment 0.9%, income tax and the 19% flat tax.',art,FAQ)
s=open(out,encoding='utf-8').read()
# remove the old short help section, engine: page-local instead of shared g.js spec
s=re.sub(r'<section class="card help">.*?</section>\n','',s,count=1,flags=re.S)
s=s.replace('data-calc="krsalary"','data-calc-local="krsalary"',1)
s=s.replace('<script src="../g.js"></script>','<script src="../g.js"></script>'+html_engine,1)
assert 'data-calc-local' in s and 'krTax' in s
open(out,'w',encoding='utf-8').write(s); print(out)
