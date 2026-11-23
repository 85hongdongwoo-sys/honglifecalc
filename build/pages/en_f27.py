"""New page: Korea F-2-7 visa points calculator (English).
Source of every score: Ministry of Justice notice 법무부고시 제2025-408호 (effective 24 Oct 2025, still current
on law.go.kr when checked 23 Nov 2026). Template = /en/korea-severance-pay-calculator.html (head, brand bar,
tabs, footer kept). Writes overlay/en/korea-f-2-7-visa-points-calculator.html."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table

SLUG = 'korea-f-2-7-visa-points-calculator.html'
URL = 'https://honglifecalc.com/en/' + SLUG
TITLE = 'Korea F-2-7 Visa Points Calculator 2026 – Check Your Score (80 to Pass)'
DESC = ('Free F-2-7 points calculator using the current Ministry of Justice table: age, degree, TOPIK/KIIP, '
        'income, bonus and deductions. You need 80 of 170 points. With worked examples.')

# ---------- scoring (same rules as the JS below) ----------
def age_pts(a):
    if a < 18: return 0
    for hi, p in ((24, 23), (29, 25), (34, 23), (39, 20), (44, 12), (50, 8)):
        if a <= hi: return p
    return 3

EDU = {'none': (0, 0), 'assoc': (15, 10), 'ba': (17, 15), 'ma': (20, 17), 'phd': (25, 20)}
KOR = {'0': 0, '1': 3, '2': 5, '3': 10, '4': 15, '5': 20}
MINW_YEAR = 10320 * 209 * 12  # 2026 minimum wage, annualised (₩25,882,560)

def inc_pts(w):
    if w < MINW_YEAR: return 0
    for lo, p in ((1e8, 60), (9e7, 58), (8e7, 56), (7e7, 53), (6e7, 50), (5e7, 45), (4e7, 40), (3e7, 30)):
        if w >= lo: return p
    return 10

def score(age, edu, stem, kor, inc, bonus=0, ded=0):
    base = age_pts(age) + EDU[edu][0 if stem else 1] + KOR[kor] + inc_pts(inc)
    return base, min(40, bonus), min(70, ded), base + min(40, bonus) - min(70, ded)

def won(x): return '₩' + f'{x:,.0f}'

EX = [  # label, age, edu, stem, korean, income, bonus, deduction, bonus text
    ('Engineer, 29, Korean master’s in engineering', 29, 'ma', True, '4', 42_000_000, 0, 0, '—'),
    ('Marketer, 33, bachelor’s in business', 33, 'ba', False, '2', 34_000_000, 0, 0, '—'),
    ('Same marketer after passing TOPIK 4', 33, 'ba', False, '4', 34_000_000, 0, 0, '—'),
    ('Researcher, 41, PhD in chemistry, no TOPIK', 41, 'phd', True, '0', 95_000_000, 0, 0, '—'),
    ('Developer, 27, CS degree from a QS top-500 university', 27, 'ba', True, '3', 31_000_000, 15, 0, '+15 (top-500 bachelor’s)'),
    ('Teacher, 36, master’s in education, ₩1.5M immigration fine', 36, 'ma', False, '5', 52_000_000, 0, 20, '−20 (fine ₩1M–₩3M)'),
]
ex_rows = []
for lab, a, e, st, k, w, b, d, bt in EX:
    base, bb, dd, tot = score(a, e, st, k, w, b, d)
    ex_rows.append([lab, f'{age_pts(a)} + {EDU[e][0 if st else 1]} + {KOR[k]} + {inc_pts(w)} = {base}', bt,
                    f'{tot} points', 'Passes' if tot >= 80 else f'Short by {80 - tot}'])
assert [r[3] for r in ex_rows] == ['100 points', '73 points', '83 points', '95 points', '97 points', '82 points'], [r[3] for r in ex_rows]

# ---------- form + calculator ----------
def sel(id_, label, opts, hint=''):
    o = ''.join(f'<option value="{v}"{" selected" if s else ""}>{t}</option>' for v, t, s in opts)
    h = f'<small class="hint">{hint}</small>' if hint else ''
    return f'<div class="field"><label for="{id_}">{label}</label><select id="{id_}">{o}</select>{h}</div>'

def chk(id_, label):
    return f'<label class="check"><input type="checkbox" id="{id_}"><span>{label}</span></label>'

FORM = ('<div class="card form" id="form">'
        + sel('trk', 'Which group are you in?', [
            ('3', 'Professional: 3+ years on E-1 to E-7 or D-5 to D-9', True),
            ('1', 'Employee of a KOSPI/KOSDAQ-listed company (manager or professional job)', False),
            ('2', 'High-tech industry worker (income ≥ 1.5 × GNI)', False),
            ('4', 'Korean master’s/PhD graduate with a job (within 5 years)', False),
            ('5', 'STEM master’s/PhD from a listed Korean university or institute', False)],
            'You must belong to one of these groups before points count.')
        + '<div class="field"><label for="age">Age on the application date</label><input id="age" inputmode="decimal" value="29"></div>'
        + sel('edu', 'Highest degree (diploma, not a completion certificate)', [
            ('none', 'No degree', False), ('assoc', 'Associate degree (2–3 year college)', False),
            ('ba', 'Bachelor’s', True), ('ma', 'Master’s', False), ('phd', 'PhD', False)])
        + chk('stem', 'Degree is in science/engineering (STEM), or you hold 2+ degrees')
        + sel('kor', 'Korean: TOPIK level or KIIP stage', [
            ('0', 'None', False), ('1', 'TOPIK 1 / KIIP stage 1', False), ('2', 'TOPIK 2 / KIIP stage 2', False),
            ('3', 'TOPIK 3 / KIIP stage 3', True), ('4', 'TOPIK 4 / KIIP stage 4', False), ('5', 'TOPIK 5–6 / KIIP stage 5', False)])
        + '<div class="field"><label for="inc">Annual taxable income in Korea (KRW)</label><input id="inc" inputmode="decimal" value="42,000,000"><small class="hint">From your tax office income certificate (소득금액증명), latest year.</small></div>'
        + '<p class="kicker" style="margin:6px 0 0">Bonus points (max 40)</p>'
        + chk('rec1', 'Recommended as a talent from a Korean War participating country (+20)')
        + chk('rec2', 'Recommended by the head of a central government agency (+20)')
        + chk('kiip', 'Completed KIIP stage 5 (+10)')
        + sel('uni', 'Degree from a top university', [
            ('0', 'None', True), ('30', 'PhD – QS top 500 or THE top 200 (+30)', False),
            ('20', 'Master’s – QS top 500 or THE top 200 (+20)', False), ('15', 'Bachelor’s – QS top 500 or THE top 200 (+15)', False),
            ('10', 'PhD – listed as “domestic” in the notice (+10)', False), ('7', 'Master’s – “domestic” (+7)', False),
            ('5', 'Bachelor’s – “domestic” (+5)', False)], 'Ranking in any of the 5 years before you apply.')
        + sel('vol', 'Volunteer work in Korea', [
            ('0', 'None or under 1 year', True), ('1', '1–2 years, 6+ times and 50+ hours (+1)', False),
            ('5', '2–3 years, 12+ times and 100+ hours (+5)', False), ('7', '3+ years, 18+ times and 150+ hours (+7)', False)])
        + '<p class="kicker" style="margin:6px 0 0">Deductions (max −70)</p>'
        + sel('imm', 'Immigration-law fines (paid in the last 3 years)', [
            ('0', 'None', True), ('10', '₩500,000 to under ₩1 million (−10)', False),
            ('20', '₩1 million to under ₩3 million (−20)', False),
            ('30', '₩3 million or more, or a departure order/deportation in the last 5 years (−30)', False),
            ('x', '3+ violations in 3 years totalling ₩5 million or more (not eligible)', False)])
        + sel('crim', 'Criminal record (Korea or abroad)', [
            ('0', 'None', True), ('20', 'Fine under ₩2 million (−20)', False), ('30', 'Fine ₩2 million to under ₩3 million (−30)', False),
            ('40', 'Fine ₩3 million+ more than 3 years ago, or prison-level sentence more than 5 years ago (−40)', False),
            ('x', 'Fine ₩3 million+ in the last 3 years, or prison-level sentence in the last 5 years (not eligible)', False)])
        + '</div>')

JS = r'''<script>
(function(){
const $=id=>document.getElementById(id);
const n=id=>{const v=parseFloat(String($(id).value).replace(/[,\s₩]/g,''));return isFinite(v)?v:0};
const f=x=>Math.round(x).toLocaleString('en-US');
const MINW=10320*209*12, GNI15=52570000*1.5;
const EDU={none:[0,0],assoc:[15,10],ba:[17,15],ma:[20,17],phd:[25,20]}, KOR=[0,3,5,10,15,20];
const BANDS=[[1e8,60],[9e7,58],[8e7,56],[7e7,53],[6e7,50],[5e7,45],[4e7,40],[3e7,30]];
function agep(a){if(a<18)return 0;for(const [h,p] of [[24,23],[29,25],[34,23],[39,20],[44,12],[50,8]])if(a<=h)return p;return 3}
function incp(w){if(w<MINW)return 0;for(const [l,p] of BANDS)if(w>=l)return p;return 10}
function run(){
 const a=n('age'),w=n('inc'),e=EDU[$('edu').value][$('stem').checked?0:1],k=KOR[+$('kor').value],ap=agep(a),ip=incp(w);
 const base=ap+e+k+ip;
 const braw=($('rec1').checked?20:0)+($('rec2').checked?20:0)+($('kiip').checked?10:0)+(+$('uni').value)+(+$('vol').value);
 const b=Math.min(40,braw), im=$('imm').value, cr=$('crim').value, out=im==='x'||cr==='x';
 const draw=(im==='x'?0:+im)+(cr==='x'?0:+cr), d=Math.min(70,draw), t=base+b-d, ok=!out&&t>=80;
 const tips=[];
 if(k<20)tips.push('Next Korean level: +'+(KOR[KOR.indexOf(k)+1]-k)+' points');
 const nb=[...BANDS].reverse().find(x=>x[0]>w);
 if(w>=MINW&&nb&&nb[1]>ip)tips.push('Income of ₩'+f(nb[0])+' or more: +'+(nb[1]-ip)+' points');
 if(w<MINW)tips.push('Income below the 2026 minimum wage for a year (₩'+f(MINW)+') scores 0');
 if(!$('kiip').checked&&k>=15)tips.push('Completing KIIP stage 5 adds a +10 bonus');
 let warn='';
 if($('trk').value==='2'&&w<GNI15)warn='<p class="note"><b>High-tech track:</b> your income must be at least 1.5 × GNI per capita – about ₩'+f(GNI15)+' using the Bank of Korea’s ₩52.57 million for 2025. Immigration may use a slightly different figure.</p>';
 if(a<18)warn+='<p class="note">Age points start at 18.</p>';
 const rows=[['Age ('+a+')',ap+' / 25'],['Education',e+' / 25'],['Korean (TOPIK / KIIP)',k+' / 20'],['Income (₩'+f(w)+')',ip+' / 60'],['Basic items',base+' / 130'],['Bonus'+(braw>40?' (capped at 40)':''),'+'+b],['Deductions',d?'−'+d:'0']];
 $('out').innerHTML='<p class="kicker">Your F-2-7 score</p><p class="big">'+(out?'Not eligible':t+' points')+'</p><p class="bigsub">'+(out?'A disqualifying record applies, whatever your score.':ok?'Meets the 80-point minimum (max 170).':'You need '+(80-t)+' more points to reach 80.')+'</p>'+
 '<table>'+rows.map(r=>'<tr><td>'+r[0]+'</td><td class="n">'+r[1]+'</td></tr>').join('')+'<tr class="t"><td>Total</td><td class="n">'+t+' / 170</td></tr></table>'+warn+
 (tips.length&&!out?'<p class="note"><b>Ways to add points:</b> '+tips.join(' · ')+'</p>':'')+
 '<p class="note">Estimate based on Ministry of Justice notice No. 2025-408. Immigration checks your documents and makes the final decision.</p>';
}
const fm=$('form');fm.addEventListener('input',run);fm.addEventListener('change',run);
$('inc').addEventListener('blur',()=>{$('inc').value=f(n('inc'))});
run();
})();
</script>'''

# ---------- article ----------
T2 = lambda h: h.replace('class="tbl"', 'class="tbl t2"', 1)
T2CSS = ('<style>.field select{max-width:100%;min-width:0}@media(max-width:640px){.help .t2{display:table;width:100%}.help .t2 thead{display:table-header-group}'
         '.help .t2 tbody{display:table-row-group}.help .t2 tr{display:table-row;border:0}.help .t2 td{display:table-cell;border-bottom:1px solid var(--line,#E3E7EE);padding:6px 4px;text-align:left}'
         '.help .t2 td:not(:first-child),.help .t2 th:not(:first-child){text-align:right;white-space:nowrap}.help .t2 td::before{content:none}}</style>')
age_t = T2(table(['Age on the application date', 'Points'], [['18–24', '23'], ['25–29', '25 (maximum)'], ['30–34', '23'], ['35–39', '20'], ['40–44', '12'], ['45–50', '8'], ['51 and over', '3']]))
edu_t = T2(table(['Degree', 'STEM or 2+ degrees', 'Other fields'], [['PhD', '25', '20'], ['Master’s', '20', '17'], ['Bachelor’s', '17', '15'], ['Associate', '15', '10']]))
kor_t = T2(table(['TOPIK level or KIIP stage', 'Points'], [['TOPIK 5–6 or KIIP stage 5', '20'], ['TOPIK 4 or KIIP stage 4', '15'], ['TOPIK 3 or KIIP stage 3', '10'], ['TOPIK 2 or KIIP stage 2', '5'], ['TOPIK 1 or KIIP stage 1', '3']]))
inc_t = T2(table(['Annual income (KRW)', 'Points'], [['₩100 million or more', '60'], ['₩90M – under ₩100M', '58'], ['₩80M – under ₩90M', '56'], ['₩70M – under ₩80M', '53'], ['₩60M – under ₩70M', '50'], ['₩50M – under ₩60M', '45'], ['₩40M – under ₩50M', '40'], ['₩30M – under ₩40M', '30'], ['Minimum wage – under ₩30M', '10'], ['Below minimum wage, no income papers, or unemployed', '0']]))
bon_t = T2(table(['Bonus item', 'Points'], [['Recommended as a Korean War participating country talent', '20'], ['Recommended by a central government agency head', '20'], ['Completed KIIP stage 5', '10'], ['Top-university degree (QS top 500 or THE top 200): PhD / master’s / bachelor’s', '30 / 20 / 15'], ['Degree listed as “domestic” (국내) in the notice: PhD / master’s / bachelor’s', '10 / 7 / 5'], ['Volunteer work: 3+ years / 2–3 years / 1–2 years', '7 / 5 / 1']]))
ded_t = T2(table(['Record', 'Deduction'], [['Immigration fine ₩3M+, or departure order / deportation (last 5 years)', '−30'], ['Immigration fine ₩1M – under ₩3M (last 3 years)', '−20'], ['Immigration fine ₩500,000 – under ₩1M (last 3 years)', '−10'], ['Criminal fine ₩3M+ (more than 3 years ago) or heavier', '−40'], ['Criminal fine ₩2M – under ₩3M', '−30'], ['Criminal fine under ₩2M', '−20']]))

FAQ = [
    ('How many points do you need for the F-2-7 visa?', 'At least 80 points out of a possible 170. The basic items (age, education, Korean and income) give up to 130, bonus items up to 40, and deductions can take away up to 70.'),
    ('How do I get 80 points for F-2-7?', 'A typical passing mix is age 25–29 (25), a master’s in engineering (20), TOPIK 4 (15) and ₩40–50 million income (40) = 100 points. Without much income or Korean it is hard: a 33-year-old business graduate with TOPIK 2 and ₩34 million scores 73.'),
    ('How many points is TOPIK worth for F-2-7?', 'TOPIK 1 = 3, TOPIK 2 = 5, TOPIK 3 = 10, TOPIK 4 = 15 and TOPIK 5 or 6 = 20 points. KIIP stages 1–5 score the same. Completing KIIP stage 5 also gives a separate +10 bonus.'),
    ('How much income do I need for F-2-7?', 'There is no single minimum in the points table, but income gives up to 60 points: ₩30 million earns 30, ₩40 million 40, ₩50 million 45 and ₩100 million or more 60. Income below the yearly minimum wage scores 0. Only the high-tech industry group needs at least 1.5 × GNI per capita (about ₩78.9 million on the Bank of Korea’s 2025 figure).'),
    ('Can I apply for F-2-7 on an E-7 visa?', 'Yes, if you have lived in Korea legally for 3 years in a row on E-1 to E-7 or D-5 to D-9 status and meet the extension requirements. E-6-2 and E-7-2 to E-7-4 holders are excluded from this group.'),
    ('Does a criminal record or immigration fine stop me getting F-2-7?', 'Small records cost points: an immigration fine of ₩1–3 million is −20 and a criminal fine under ₩2 million is −20. A criminal fine of ₩3 million or more in the last 3 years, a prison-level sentence in the last 5 years, or 3+ immigration violations totalling ₩5 million in 3 years makes you ineligible.'),
    ('When did the current F-2-7 points table start?', 'The Ministry of Justice notice No. 2025-408 took effect on 24 October 2025. Applications filed before that date were judged under the old notice. It was still the current version when we checked on 23 November 2026.'),
]
faq_h = '<h2 id="faq" style="margin-top:22px">F-2-7 visa FAQ</h2>' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in FAQ)

ART = (TBL_CSS + T2CSS +
'<p class="hl-ans" style="background:#F3F8FF;border:1px solid #D6E6FD;border-radius:12px;padding:12px 14px;margin:0 0 14px;line-height:1.6">'
'<b>Quick answer (2026):</b> You need <b>80 points out of 170</b> for Korea’s F-2-7 residence visa. Age gives up to 25, education 25, Korean (TOPIK/KIIP) 20 and income 60; bonuses add up to 40. '
'A 29-year-old with a STEM master’s, TOPIK 4 and ₩42 million income scores <b>100 points</b>.</p>'
'<h2 id="figures">F-2-7 points table (current Ministry of Justice notice)</h2>'
'<p>The F-2-7 is Korea’s points-based long-term residence visa. Each item gives points, and the total must be <b>80 or more</b>. These are the official numbers from notice No. 2025-408, in force since 24 October 2025.</p>'
'<h3>1. Age (up to 25 points)</h3>' + age_t +
'<h3>2. Education (up to 25 points)</h3><p>Only a degree certificate counts – a “completion” certificate (수료) does not. “STEM” means science and engineering. If you hold two or more degrees, you get the STEM column whatever the subject.</p>' + edu_t +
'<h3>3. Korean language (up to 20 points)</h3><p><b>TOPIK</b> is the official Korean test. <b>KIIP</b> (사회통합프로그램) is the government’s free integration course; you can check your stage on socinet.go.kr.</p>' + kor_t +
'<h3>4. Annual income (up to 60 points)</h3><p>This is your <b>taxable income</b> for the latest year, shown on the tax office’s income certificate (소득금액증명). For 2026 the minimum wage is ₩10,320 an hour – about ₩25.88 million a year at 209 hours a month.</p>' + inc_t +
'<h3>5. Bonus points (up to 40 in total)</h3>' + bon_t +
'<p class="note">“Top university” means the school was in the QS World University Rankings top 500 or the THE top 200 in any of the 5 years before you apply. The notice lists a second, smaller column called “domestic” (국내) without defining it further – ask immigration whether your degree qualifies.</p>'
'<h3>6. Deductions (up to −70)</h3>' + ded_t +
'<h2 id="ex" style="margin-top:22px">Worked examples</h2><p>Each score is age + education + Korean + income, then bonus and deductions. All examples are worked out with this calculator.</p>'
'<div id="examples">' + table(['Person', 'F-2-7 score', 'Result'], [[r[0], r[3], 'Passes' if r[4] == 'Passes' else 'Below 80'] for r in ex_rows]) + '</div>'
'<h3>How each score adds up</h3>' + table(['Person', 'Age + degree + Korean + income', 'Bonus / deduction', 'Total', 'Result'], ex_rows) +
'<ul><li><b>The marketer</b> starts at 73 – 7 short. Passing TOPIK 4 instead of TOPIK 2 adds 10 points and takes the score to 83.</li>'
'<li><b>The researcher</b> passes with no Korean at all, because a STEM PhD (25) and ₩95 million income (58) carry the score.</li>'
'<li><b>The developer</b> earns only ₩31 million, but a bachelor’s from a QS top-500 university adds a 15-point bonus: 82 + 15 = 97.</li>'
'<li><b>The teacher</b> loses 20 points for a ₩1.5 million immigration fine but still passes with 82.</li></ul>'
'<h2 id="how" style="margin-top:22px">How the F-2-7 points system works</h2>'
'<p><b>Step 1 – be in an eligible group.</b> Points only matter if you fit one of five groups:</p><ul>'
'<li><b>Professionals:</b> 3 years in a row in Korea on E-1 to E-7 or D-5 to D-9 status (not E-6-2 or E-7-2 to E-7-4), meeting the extension rules.</li>'
'<li><b>Listed-company staff:</b> working (or hired) at a KOSPI/KOSDAQ company as a manager or professional.</li>'
'<li><b>High-tech industry workers:</b> in a government-listed advanced-technology field, earning at least 1.5 × the previous year’s GNI per capita.</li>'
'<li><b>Korean graduates:</b> a Korean master’s or PhD and a professional job within 5 years of graduating.</li>'
'<li><b>Potential talent:</b> a STEM master’s or PhD from one of the specialised universities or institutes listed in the notice.</li></ul>'
'<p><b>Step 2 – add up your points.</b> The four basic items can give 130 points. Bonuses are capped at 40, so the highest possible total is 170. You need 80.</p>'
'<p><b>Step 3 – check you are not disqualified.</b> Some records rule you out completely, whatever your score: a criminal fine of ₩3 million or more in the last 3 years, a prison-level sentence in the last 5 years, 3 or more immigration violations in 3 years totalling ₩5 million or more, or false documents.</p>'
'<h2 id="tips" style="margin-top:22px">Tips to raise your score – and common mistakes</h2><ul>'
'<li><b>Korean is usually the quickest win.</b> Going from TOPIK 2 to TOPIK 4 adds 10 points; TOPIK 5 adds 15.</li>'
'<li><b>Watch the income lines.</b> ₩29.9 million scores 10, but ₩30 million scores 30 – a 20-point jump. ₩39.9 million → ₩40 million is another +10.</li>'
'<li><b>KIIP counts twice:</b> stage 5 gives 20 in the Korean item and completing it adds a 10-point bonus.</li>'
'<li><b>Age moves your score.</b> Turning 30 costs 2 points and turning 40 costs 8, so it can pay to apply before a birthday.</li>'
'<li><b>Mistake:</b> using gross salary from a contract. Immigration looks at taxable income on the official income certificate.</li>'
'<li><b>Mistake:</b> counting a completion certificate or volunteer work of under 1 year – neither gets points.</li></ul>'
+ faq_h +
'<p class="note">Sources (checked 23 November 2026): <a href="https://www.law.go.kr/LSW/admRulInfoP.do?admRulSeq=2100000266296" rel="nofollow">Ministry of Justice notice No. 2025-408 – age, education and income criteria for F-2 (points table, attachment 2), law.go.kr</a>; '
'<a href="https://www.bok.or.kr/portal/bbs/B0000501/view.do?nttId=10098382&amp;menuNo=201264" rel="nofollow">Bank of Korea – 2025 national accounts (GNI per capita ₩52.57 million)</a>; '
'Ministry of Employment and Labor – 2026 minimum wage ₩10,320 an hour. Examples use this page’s own formula. '
'How long each F-2-7 permit lasts and the rules for family members (F-2-71) are not covered here – ask the Immigration Contact Center (1345).</p>')

TOC = [('form', 'Calculator'), ('figures', 'F-2-7 points table'), ('ex', 'Worked examples'), ('how', 'How the points system works'), ('tips', 'Tips & common mistakes'), ('faq', 'FAQ')]
TOP = ('<!--hl:deep--><div class="hl-by"><span>By <b>Hong Life Calculators</b></span><span>Checked <b>23 November 2026</b></span>'
       '<span>Source <b>Ministry of Justice notice No. 2025-408</b></span></div>'
       '<details class="card hl-toc" open><summary>On this page</summary><ol>' + ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in TOC) + '</ol></details>')

# ---------- assemble from template ----------
src = os.path.join(ORIG, 'en/korea-severance-pay-calculator.html')
s = open(src, encoding='utf-8').read()
s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
s = re.sub(r'<link rel="canonical" href="[^"]*"><link rel="alternate" hreflang="en" href="[^"]*">',
           f'<link rel="canonical" href="{URL}"><link rel="alternate" hreflang="en" href="{URL}">', s, count=1)
for p, v in (('og:title', TITLE), ('og:description', DESC), ('og:url', URL), ('og:image:alt', 'Korea F-2-7 Visa Points Calculator')):
    s = re.sub(r'(<meta property="' + p + r'" content=")[^"]*', lambda m: m.group(1) + v, s, count=1)
# no page-specific share image exists yet: drop the severance image tags
s = re.sub(r'<meta property="og:image[^>]*>', '', s)
s = re.sub(r'<!--hl:img-->.*?<!--/hl:img-->', '', s, flags=re.S)
s = re.sub(r'<meta name="twitter:image" content="[^"]*">', '', s)
s = s.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary">')
s = re.sub(r'(?s)<script type="application/ld\+json">.*?</script>', '', s)
ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": "Korea F-2-7 Visa Points Calculator", "url": URL,
       "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
       "dateModified": "2026-11-23", "inLanguage": "en"},
      {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
          {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld) + TOP_CSS + '</head>', 1)
s = re.sub(r'<header class="top">.*?</header>',
           '<header class="top"><h1>Korea <b>F-2-7 Visa Points</b> Calculator</h1><p class="sub">Check whether you reach the 80 points needed for Korea’s points-based residence visa – using the current Ministry of Justice table.</p></header>', s, count=1, flags=re.S)
s = s.replace('<a href="korea-severance-pay-calculator.html" aria-current="page">Korea severance</a>',
              '<a href="korea-severance-pay-calculator.html">Korea severance</a><a href="korea-f-2-7-visa-points-calculator.html" aria-current="page">F-2-7 points</a>', 1)
s = re.sub(r'<section class="panel" data-calc="krsev">.*?</section>',
           TOP + '<section class="panel">' + FORM + '<div class="card res" id="out" aria-live="polite"></div></section>', s, count=1, flags=re.S)
s = re.sub(r'<section class="card help">.*?</section>', lambda m: '<section class="card help">' + ART + '</section>', s, count=1, flags=re.S)
s = s.replace('<script src="../g.js"></script>', '<script src="../g.js"></script>\n' + JS, 1)
s = s.replace('</body>', '<script src="/assets/hl-views.js?v=3" defer data-target="#examples" data-lang="en"></script></body>', 1)
assert 'data-calc' not in s and 'id="figures"' in s and 'Korea F-2-7' in s
out = os.path.join(OUT, 'en', SLUG)
open(out, 'w', encoding='utf-8').write(s)
print(out)
