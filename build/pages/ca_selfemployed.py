import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/ca/self-employed-tax-calculator.html'

calc='''function calc(){const p=Math.max(0,num('p')),o=Math.max(0,num('o')),c=$('pv').value;
 const pe=Math.max(0,Math.min(o+p,C.ympe)-Math.max(o,C.ybe)),pe2=Math.max(0,Math.min(o+p,C.yampe)-Math.max(o,C.ympe));
 const base=pe*.0495*2,enh=pe*.01*2,cpp2=pe2*.08,cpp=base+enh+cpp2,ded=base/2+enh+cpp2;
 const ni=Math.max(0,p+o-ded),t=itax(ni,c,base/2).tot;
 const eb=.0495*Math.max(0,Math.min(o,C.ympe)-C.ybe),ee=.01*Math.max(0,Math.min(o,C.ympe)-C.ybe),e2=.04*Math.max(0,Math.min(o,C.yampe)-C.ympe);
 const tE=o?itax(Math.max(0,o-ee-e2),c,eb).tot:0,xt=Math.max(0,t-tE),due=xt+cpp;
 const nt='<p class="note">2026 rules, outside Quebec. Other employment income is assumed to have its own tax and CPP taken off by the employer, so only the extra caused by self-employment is shown as "to set aside". Estimates only.</p>';
 return big('Tax + CPP to set aside',cad(due,0),pc(p?due/p:0)+' of your self-employment income')+kv([['CPP on self-employment (both halves, 11.9%)',cad(base+enh,0),'neg'],['CPP2 (both halves, 8%)',cad(cpp2,0),'neg'],['Income tax caused by self-employment (federal + '+pname(c)+')',cad(xt,0),'neg'],...(o?[['Income tax on all income',cad(t,0)]]:[]),['CPP deduction from income',cad(ded,0)],['Kept from self-employment',cad(p-due,0),'t'],['Per quarter, if instalments apply',cad(due/4,0)],['Set aside each month',cad(due/12,0)]])+nt}'''

usd=lambda x:f"${x:,.0f}"
# outputs read from the page's own engine (Playwright, runF1.js)
exs=[['Ontario','$80,000','$8,893','$13,234','$22,126','$57,874'],
     ['British Columbia','$50,000','$5,534','$5,672','$11,206','$38,794'],
     ['Alberta','$120,000','$9,293','$24,912','$34,205','$85,795'],
     ['Nova Scotia','$30,000','$3,154','$2,766','$5,920','$24,080']]

FAQ=[
("How much tax does a self-employed person pay on $80,000 in Ontario?","About $22,126 in 2026: $8,893 of CPP (both halves plus CPP2) and $13,234 of income tax. That is 27.7% of the $80,000, so you keep about $57,874. Setting aside about $1,844 a month covers it."),
("What percentage should I set aside for taxes when self-employed in Canada?","Many people need 20–30% of their profit. In our examples it is 19.7% on $30,000 in Nova Scotia, 22.4% on $50,000 in B.C. and 28.5% on $120,000 in Alberta. Use the calculator with your own province."),
("How much CPP does a self-employed person pay in 2026?","11.9% of net self-employment income between $3,500 and $74,600 – up to $8,460.90. Above that you pay 8% CPP2 on income up to $85,000, up to $832 more. You pay both the employee and the employer part."),
("Do self-employed people have to pay tax quarterly in Canada?","Only if the CRA asks. You must pay instalments when your net tax owing is more than $3,000 in 2026 and in either 2025 or 2024. The due dates are March 15, June 15, September 15 and December 15."),
("When is the tax deadline for self-employed people?","For 2026 income you have until June 15, 2027 to file your return. But any balance owing must still be paid by April 30, 2027, or interest starts."),
("Do self-employed people pay EI?","Not by default. You can sign up to pay EI premiums to get special benefits: maternity, parental, sickness, compassionate care and family caregiver benefits. In 2026 the premium is $1.63 for every $100 you earn, up to $1,123.07 a year. The program is for these special benefits, not job-loss (regular) EI."),
("When do I need to register for GST/HST?","When your taxable sales go over $30,000 in a single calendar quarter or over the last four calendar quarters in a row. Sales of associated businesses count too. Below that you are a small supplier and registering is optional."),
]

fig=[['Basic exemption (YBE)','$3,500','No CPP on the first $3,500 of earnings.'],
     ['Maximum pensionable earnings (YMPE)','$74,600','11.9% CPP is charged up to here.'],
     ['Additional maximum (YAMPE)','$85,000','8% CPP2 is charged between $74,600 and $85,000.'],
     ['Maximum CPP, self-employed','$8,460.90','11.9% × ($74,600 − $3,500).'],
     ['Maximum CPP2, self-employed','$832','8% × ($85,000 − $74,600).'],
     ['Federal tax rates 2026','14% · 20.5% · 26% · 29% · 33%','Brackets start at $58,523.01, $117,045.01, $181,440.01 and $258,482.01.'],
     ['Instalment threshold','$3,000 net tax owing','In 2026 and in 2025 or 2024. Quebec: $1,800.'],
     ['Instalment dates','March 15 · June 15 · September 15 · December 15','Quarterly payments if the CRA asks.'],
     ['Filing and payment','File by June 15, 2027 · pay by April 30, 2027','For 2026 self-employment income.'],
     ['EI special benefits (optional)','$1.63 per $100 of earnings, max $1,123.07','2026 premium if you opt in (outside Quebec).']]

art='''<h2 id="figures">2026 figures for self-employed Canadians</h2>
'''+table(['Item','Amount','What it means'],fig)+'''
<h2 id="ex">How much tax will I pay? Examples</h2>
<div id="examples">'''+table(['Province','Net self-employment income','CPP + CPP2','Income tax','Total to set aside','You keep'],exs)+'''</div>
<ul><li><b>$80,000 in Ontario.</b> CPP is $8,461 plus $432 CPP2. Income tax is $13,234. In total about $22,126, or 27.7%.</li>
<li><b>$50,000 in B.C.</b> CPP is $5,534 and income tax $5,672. About $934 a month to set aside.</li>
<li><b>$120,000 in Alberta.</b> CPP and CPP2 are at their maximum ($9,293). Income tax is $24,912.</li>
<li><b>$30,000 in Nova Scotia.</b> About $5,920 in total. CPP ($3,154) is more than the income tax.</li></ul>
<p class="note">Examples use this calculator's own 2026 engine (federal and provincial brackets and credits) with no other income and no other deductions.</p>
<h2 id="how">How self-employed tax works (in plain words)</h2>
<p>Example first. You earn $80,000 profit in Ontario. CPP is 11.9% of your earnings between $3,500 and $74,600: $71,100 × 11.9% = $8,461. Then 8% CPP2 on $5,400 = $432. Part of that CPP is taken off your income before tax, and the rest gives you a tax credit. Income tax comes to $13,234.</p>
<ul><li><b>Net income</b> means what you earned minus business expenses. Tax and CPP are worked out on this, not on your sales.</li>
<li><b>CPP</b> (Canada Pension Plan) builds your future pension. An employee pays half and the employer pays half. When you work for yourself, you pay both halves.</li>
<li><b>Part of your CPP is deducted</b> from your income (line 22200): the employer half, plus the enhanced parts and CPP2. For the employee base part (4.95%) you get a tax credit instead (line 31000). Schedule 8 works this out.</li>
<li><b>Instalments</b> are tax payments in advance, four times a year, so you don't owe a big amount in spring.</li></ul>
<p>Quebec is different: you pay QPP and QPIP and file a separate Quebec return, so this calculator leaves Quebec out.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Set money aside every month.</b> Put the "set aside each month" amount into a separate savings account.</li>
<li><b>Keep receipts.</b> Business expenses lower your net income, and so lower both tax and CPP.</li>
<li><b>Don't forget CPP.</b> At lower incomes it can be bigger than the income tax.</li>
<li><b>Pay by April 30.</b> The June 15 filing date does not delay the payment date.</li>
<li><b>Watch the $30,000 GST/HST line.</b> Once you pass it, you must register and charge GST/HST.</li></ul>
<h2 id="faq" style="margin-top:22px">Self-employed tax FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 27 November 2026): <a href="https://www.canada.ca/en/revenue-agency/services/tax/individuals/tax-rates-brackets/current-year.html" rel="nofollow">CRA – Tax rates and income brackets 2026</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/payroll-deductions-contributions/canada-pension-plan-cpp/cpp-contribution-rates-maximums.html" rel="nofollow">CRA – CPP contribution rates and maximums</a>; <a href="https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/calculating-deductions/making-deductions/second-additional-cpp-contribution-rates-maximums.html" rel="nofollow">CRA – CPP2 rates and maximums</a>; <a href="https://www.canada.ca/en/revenue-agency/services/payments/payments-cra/individual-payments/income-tax-instalments/who-pays-instalments.html" rel="nofollow">CRA – Who pays instalments</a>; <a href="https://www.canada.ca/en/services/taxes/resources-for-small-and-medium-businesses/2026-tax-deadlines-canadian-businesses-self-employed-individuals.html" rel="nofollow">Canada.ca – 2026 tax deadlines for self-employed individuals</a>; <a href="https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/rc4022/general-information-gst-hst-registrants.html" rel="nofollow">CRA – RC4022 GST/HST registrants</a>; <a href="https://www.canada.ca/en/services/benefits/ei/ei-self-employed-workers/premiums.html" rel="nofollow">Canada.ca – EI premiums for self-employed people</a>. General information, not tax advice.</p>'''

out=build(P,'Self-Employed Tax Calculator Canada 2026 – Income Tax + CPP',
 'How much tax and CPP a self-employed Canadian pays in 2026, how much to set aside each month, CPP and CPP2 maximums, and instalment dates.',
 art,FAQ,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','27 November 2026'),('Sources','CRA, ESDC')],
 [('form','Calculator'),('figures','2026 figures'),('ex','Examples'),('how','How it works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
