import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/au/atar-selection-rank-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Your ATAR</h2><label class="f"><span>ATAR</span><input id="a" inputmode="decimal" value="85.40"><small>Between 30.00 and 99.95.</small></label><div class="two"><label class="f"><span>Subject / HSC bonus points</span><input id="s" inputmode="decimal" value="2"></label><label class="f"><span>Equity / regional / other</span><input id="e" inputmode="decimal" value="0"></label></div><label class="f"><span>Maximum adjustment for this university (points)</span><input id="mx" inputmode="decimal" value="5"><small>An example. Each university sets its own maximum; check the course page on UAC, VTAC or the university site.</small></label></form>'''

calc='''function calc(){const F=x=>(Math.round(x*100)/100).toFixed(2);const a=num('a'),s=Math.max(0,num('s')),e=Math.max(0,num('e')),mx=Math.max(0,num('mx'));
 if(a<=0)return big('Selection rank','—','Enter your ATAR');
 if(a>99.95)return big('Selection rank','—','An ATAR cannot be higher than 99.95');
 const want=s+e,adj=Math.min(want,mx),raw=a+adj,r=Math.min(99.95,raw);
 const rows=[['Your ATAR',F(a)],['Adjustment points you entered',F(want)],['Adjustment points used',F(adj),'pos']];
 if(want>mx)rows.push(['Points over the university maximum',F(want-mx),'neg']);
 if(raw>99.95)rows.push(['Points lost at the 99.95 limit',F(raw-99.95),'neg']);
 return big('Selection rank',F(r),'ATAR '+F(a)+' + '+F(adj)+' adjustment')+kv(rows)+'<p class="note">Your ATAR itself never changes. Adjustment points only raise your selection rank for the courses where they apply, and this calculator caps the result at 99.95.</p>'}'''

def sel(a,s,e,mx):
    adj=min(s+e,mx); return adj, min(99.95,a+adj)
ex=[(85.40,2,0,5,'HSC student with subject bonus'),(78.00,3,2,5,'Regional student'),(92.50,5,5,5,'Two schemes, university cap 5'),(98.50,3,0,5,'High ATAR near the top')]
rows=[]
for a,s,e,mx,lab in ex:
    adj,r=sel(a,s,e,mx)
    rows.append([lab,f"{a:.2f}",f"{s+e:g}",f"{mx:g}",f"{adj:g}",f"{r:.2f}"])
print(rows)

fig=[['ATAR range','0.00 to 99.95, in steps of 0.05','It is a rank, not a mark out of 100.'],
     ['What the ATAR shows','Your position compared with all students in your age group','An ATAR of 80.00 means you did better than about 80% of your age group.'],
     ['Low ATARs (NSW, UAC)','Below 30 is shown as “less than 30”','You still get a result; the exact number isn\'t shown.'],
     ['Selection rank','ATAR + adjustment factors','Used by universities to decide offers. Each course can use different adjustments.'],
     ['Adjustment factors','Set by each university','For example: subject bonuses, living or studying in a regional area, or educational disadvantage (Educational Access Schemes).'],
     ['Lowest selection rank','The lowest rank that got an offer last time','A guide to how competitive a course is, not a fixed cut-off.']]

FAQ=[
("What is the difference between ATAR and selection rank?","Your ATAR is one number for everything. Your selection rank is your ATAR plus any adjustment points for one course. Example: ATAR 85.40 + 2 subject bonus points = selection rank 87.40 for courses that give that bonus."),
("Do bonus points change my ATAR?","No. Your ATAR stays the same. Bonus points (adjustment factors) only raise your selection rank for the courses and universities that offer them."),
("How many bonus points can I get?","It depends on the university and the scheme. Each university sets its own rules and its own maximum. If you qualify for 10 points but the university's limit is 5, only 5 count. Check the course page on UAC, VTAC or the university website."),
("Can my selection rank be higher than 99.95?","This calculator stops at 99.95, the highest possible ATAR. Example: ATAR 98.50 + 3 points would be 101.50, but the calculator shows 99.95. Some admission centres handle this differently, so check your centre's rules if you are near the top."),
("What does an ATAR of 80 mean?","It means you did better than about 80% of your age group – all students of your age, not only those who finished Year 12. It is not a percentage mark."),
("What is a lowest selection rank?","It is the lowest selection rank (ATAR plus adjustments) that received an offer for a course last time. If yours is a little lower, you may still get in, because the number changes each round."),
]

art='''<h2 id="figures">Key facts about ATAR and selection ranks</h2>
'''+table(['Item','Rule','What it means'],fig)+'''
<h2 id="ex">Selection rank examples</h2>
<div id="examples">'''+table(['Student','ATAR','Points earned','University max','Points used','Selection rank'],rows)+'''</div>
<ul><li><b>ATAR 85.40 with 2 bonus points</b> gives a selection rank of <b>87.40</b>.</li>
<li><b>A regional student with ATAR 78.00</b> earns 3 + 2 = 5 points. The university allows 5, so the rank is <b>83.00</b>.</li>
<li><b>ATAR 92.50 with 10 points</b> from two schemes only gets 5 if the university's maximum is 5. Rank: <b>97.50</b>.</li>
<li><b>ATAR 98.50 + 3 points</b> would be 101.50, but the result stops at <b>99.95</b>.</li></ul>
<p class="note">The maximum of 5 points is an example only. Use the real limit for your course.</p>
<h2 id="how">How it works</h2>
<p>Example first. Your ATAR is 85.40. You did well in a subject the course likes, so the university gives you 2 bonus points. Your selection rank for that course is 85.40 + 2 = <b>87.40</b>. For another course with no bonus, your selection rank is still 85.40.</p>
<ul><li><b>ATAR</b> (Australian Tertiary Admission Rank) = your rank compared with your age group, from 0.00 to 99.95.</li>
<li><b>Adjustment factors</b> = extra points a university adds for certain reasons, such as subject results, where you live or hardship.</li>
<li><b>Selection rank</b> = ATAR + adjustment points, but no more than the university allows.</li></ul>
<p>The calculator adds your points, cuts them to the university's maximum, adds them to your ATAR and stops at 99.95.</p>
<h2 id="tips">Tips and common mistakes</h2>
<ul><li><b>Check each course.</b> The same scheme can give different points at different universities.</li>
<li><b>Apply for schemes on time.</b> Educational Access Schemes usually need a separate application through UAC, VTAC or your state's admission centre.</li>
<li><b>Don't add points twice.</b> Many universities cap the total from all schemes together.</li>
<li><b>Lowest selection ranks are a guide.</b> They change every round, so list your dream course first and safer options after.</li></ul>
<h2 id="faq" style="margin-top:22px">ATAR and selection rank FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked 25 November 2026): <a href="https://uac.edu.au/future-applicants/admission-criteria/year-12-qualifications" rel="nofollow">UAC – Year 12 qualifications and the ATAR</a>; <a href="https://uac.edu.au/future-applicants/admission-criteria/university-selection-rank-adjustments" rel="nofollow">UAC – selection rank adjustments</a>; <a href="https://uac.edu.au/current-applicants/educational-access-schemes" rel="nofollow">UAC – Educational Access Schemes</a>. Examples use this calculator's own formula. General information only – each university sets its own rules.</p>'''

out=build(P,'ATAR Selection Rank Calculator 2026 – Add Bonus Points',
 'Add bonus points (adjustment factors) to your ATAR to see your selection rank for a course. Worked examples, university limits and the 99.95 cap explained.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked','25 November 2026'),('Sources','UAC')],
 [('form','Calculator'),('figures','Key facts'),('ex','Examples'),('how','How it works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
