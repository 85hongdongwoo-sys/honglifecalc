import sys,re,json,os; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import table, add_top, ORIG, OUT, TBL_CSS
P='/ar/bmi-calculator.html'
s=open(os.path.join(ORIG,P.lstrip('/')),encoding='utf-8').read()

TITLE='حاسبة مؤشر كتلة الجسم BMI 2026 — الوزن المثالي لطولك بالكيلوغرام'
DESC='احسب مؤشر كتلة الجسم من الوزن والطول، واعرف فئتك حسب منظمة الصحة العالمية والوزن الصحي لطولك، مع أمثلة وجدول للأطوال ومحيط الخصر.'

# --- calculator: WHO adult classes (obesity class I/II/III); healthy range 18.5–24.9 ---
old_run=s[s.index('  run(v){'):s.index('function build(id){')]
new_run='''  run(v){
    const kg=v.unit==='i'?v.w*0.453592:v.w,m=v.unit==='i'?v.h*0.0254:v.h/100;
    const bmi=m?kg/(m*m):0;
    const cut=v.asia?[18.5,23,25,30]:[18.5,25,30,35,40];
    const lab=v.asia?['نقص الوزن','وزن طبيعي','زيادة الوزن','سمنة','سمنة شديدة']:['نقص الوزن','وزن طبيعي','زيادة الوزن (ما قبل السمنة)','سمنة من الدرجة الأولى','سمنة من الدرجة الثانية','سمنة من الدرجة الثالثة'];
    let i=0;while(i<cut.length&&bmi>=cut[i])i++;
    const lo=18.5*m*m,hi=(v.asia?22.9:24.9)*m*m,toW=x=>v.unit==='i'?fmt(x/0.453592,1)+' رطل':fmt(x,1)+' كغ';
    const diff=kg<lo?'تحتاج إلى زيادة نحو '+toW(lo-kg)+' لتصل إلى الوزن الطبيعي':kg>hi?'الوزن الطبيعي لطولك أقل بنحو '+toW(kg-hi):'وزنك ضمن النطاق الطبيعي لطولك';
    return{k:'مؤشر كتلة الجسم (BMI)',big:fmt(bmi,1),sub:lab[i],rows:[['الوزن الطبيعي لطولك','',toW(lo)+' – '+toW(hi)],
      ...cut.map((c,j)=>[lab[j+1],'','≥ '+fmt(c,1)])],
      note:'<b>'+diff+'.</b> للبالغين من عمر 20 عامًا فأكثر. مؤشر كتلة الجسم أداة فحص أولي وليس تشخيصًا، ولا يميّز بين العضلات والدهون، ولا يُستخدم للأطفال أو أثناء الحمل.'};
  }
};
'''
s=s.replace(old_run,new_run,1)

def bmi(h,w): return w/(h/100)**2
def cls(b):
    for c,l in [(18.5,'نقص الوزن'),(25,'وزن طبيعي'),(30,'زيادة الوزن'),(35,'سمنة من الدرجة الأولى'),(40,'سمنة من الدرجة الثانية')]:
        if b<c: return l
    return 'سمنة من الدرجة الثالثة'
f1=lambda x:f"{x:.1f}"
ex=[]
for h,w in [(160,55),(165,80),(175,95),(180,120)]:
    b=bmi(h,w);m=h/100
    ex.append([f"{h} سم",f"{w} كغ",f1(b),cls(b),f"{f1(18.5*m*m)} – {f1(24.9*m*m)} كغ"])
hw=[[f"{h} سم",f1(18.5*(h/100)**2),f1(24.9*(h/100)**2),f1(29.9*(h/100)**2)] for h in range(150,195,5)]
print(ex)

FAQ=[
("كيف أحسب مؤشر كتلة الجسم؟","اقسم وزنك بالكيلوغرام على مربع طولك بالمتر. مثال: وزن 70 كغ وطول 1.70 م: 1.70 × 1.70 = 2.89، ثم 70 ÷ 2.89 = 24.2. هذا وزن طبيعي."),
("ما هو مؤشر كتلة الجسم الطبيعي؟","من 18.5 إلى 24.9 للبالغين حسب تصنيف منظمة الصحة العالمية. من 25 إلى 29.9 زيادة في الوزن (ما قبل السمنة)، و30 فأكثر سمنة."),
("ما هو الوزن المثالي لطول 170 سم؟","الوزن الطبيعي لطول 170 سم يتراوح بين 53.5 و72.0 كغ تقريبًا، أي مؤشر كتلة جسم من 18.5 إلى 24.9. ولطول 160 سم بين 47.4 و63.7 كغ."),
("هل مؤشر كتلة الجسم دقيق للرياضيين؟","ليس دائمًا. فهو لا يميّز بين العضلات والدهون، لذلك قد يظهر الرياضي صاحب العضلات الكثيرة في فئة زيادة الوزن رغم أن نسبة الدهون لديه منخفضة. قياس محيط الخصر يساعد هنا."),
("هل يصلح مؤشر كتلة الجسم للأطفال والحوامل؟","لا تُستخدم فئات البالغين للأطفال. تقيس منظمة الصحة العالمية الأطفال من 5 إلى 19 عامًا بمؤشر كتلة الجسم حسب العمر مقارنةً بمرجع النمو. ولا يُنصح باستخدام حاسبة البالغين أثناء الحمل."),
("ما هو محيط الخصر الطبيعي؟","حسب وزارة الصحة السعودية: للرجال أقل من 94 سم طبيعي، ومن 94 إلى 101 سم خطر، و102 سم فأكثر خطر عالٍ. وللنساء أقل من 80 سم طبيعي، ومن 80 إلى 87 سم خطر، و88 سم فأكثر خطر عالٍ."),
("لماذا توجد حدود آسيوية أقل؟","بعض الشعوب، ومنها الآسيوية وشعوب الشرق الأوسط، ترتفع لديها المخاطر الصحية عند مؤشر كتلة جسم أقل، كما تذكر هيئة الصحة البريطانية (NHS). لذلك يتيح خيار الحدود الآسيوية في الحاسبة اعتبار 23 بداية زيادة الوزن و25 بداية السمنة."),
]

art='''<h2 id="figures">تصنيف مؤشر كتلة الجسم للبالغين (منظمة الصحة العالمية)</h2>
'''+table(['مؤشر كتلة الجسم','الفئة'],[['أقل من 18.5','نقص الوزن (نحافة)'],['18.5 – 24.9','وزن طبيعي'],['25.0 – 29.9','زيادة الوزن (ما قبل السمنة)'],['30.0 – 34.9','سمنة من الدرجة الأولى'],['35.0 – 39.9','سمنة من الدرجة الثانية'],['40 فأكثر','سمنة من الدرجة الثالثة (مفرطة)']])+'''
<p class="note">تعرّف منظمة الصحة العالمية زيادة الوزن بأنها مؤشر 25 أو أكثر، والسمنة بأنها 30 أو أكثر، للبالغين.</p>
<h3>محيط الخصر</h3>
'''+table(['','طبيعي','خطر','خطر عالٍ'],[['الرجال','أقل من 94 سم','94 – 101 سم','102 سم فأكثر'],['النساء','أقل من 80 سم','80 – 87 سم','88 سم فأكثر']])+'''
<p class="note">المصدر: وزارة الصحة السعودية. حدّ الخطر العالي (أكثر من 102 سم للرجال و88 سم للنساء) هو أيضًا حدّ منظمة الصحة العالمية.</p>
<h3>نسب السمنة بين البالغين في بعض الدول العربية</h3>
'''+table(['الدولة','نسبة السمنة (مؤشر 30 فأكثر)','المسح والسنة'],[['السعودية','23.1%','الهيئة العامة للإحصاء، 2024 (15 عامًا فأكثر)'],['الإمارات','27.8%','المسح الصحي الوطني 2017–2018 (18–69 عامًا)'],['مصر','35.7%','مسح STEPS لعام 2017 (15–69 عامًا)'],['الكويت','40.2%','مسح STEPS لعام 2014 (18–69 عامًا)'],['قطر','41.4%','مسح STEPS لعام 2012 (القطريون فقط)']])+'''
<p class="note">المسوح من سنوات وفئات عمرية مختلفة، لذلك لا تصلح للمقارنة المباشرة بين الدول. عالميًا في 2024: 45% من البالغين (2.6 مليار) يعانون من زيادة الوزن، منهم 940 مليونًا (16%) مصابون بالسمنة، حسب منظمة الصحة العالمية.</p>
<h2 id="ex">أمثلة محسوبة</h2>
'''+table(['الطول','الوزن','مؤشر كتلة الجسم','الفئة','الوزن الطبيعي لهذا الطول'],ex)+'''
<h3>الوزن الطبيعي حسب الطول</h3>
<div id="ar-w">'''+table(['الطول','أدنى وزن طبيعي (كغ)','أعلى وزن طبيعي (كغ)','حدّ زيادة الوزن (كغ)'],hw)+'''</div>
<p class="note">محسوبة بصيغة هذه الصفحة: أدنى وزن = 18.5 × الطول²، وأعلى وزن = 24.9 × الطول²، وحدّ زيادة الوزن = 29.9 × الطول² (الطول بالمتر).</p>
<h2 id="how">طريقة الحساب ببساطة</h2>
<p>نبدأ بمثال: وزنك 100 كغ وطولك 170 سم.</p>
<ul><li>حوّل الطول إلى متر: 170 سم = 1.70 م.</li>
<li>اضرب الطول في نفسه: 1.70 × 1.70 = 2.89.</li>
<li>اقسم الوزن على الناتج: 100 ÷ 2.89 = <b>34.6</b>. هذه سمنة من الدرجة الأولى.</li></ul>
<p><b>مؤشر كتلة الجسم</b> (BMI) رقم يربط وزنك بطولك. الصيغة: الوزن (كغ) ÷ الطول² (م). وللوحدات الأمريكية تحوّل الحاسبة الأرطال إلى كيلوغرامات والبوصات إلى أمتار.</p>
<h3>حدود المؤشر</h3>
<ul><li><b>لا يميّز بين العضلات والدهون.</b> قد يبدو صاحب العضلات «زائد الوزن».</li>
<li><b>لا يناسب الأطفال والمراهقين.</b> لهم مقاييس حسب العمر والجنس.</li>
<li><b>لا يُستخدم أثناء الحمل.</b></li>
<li><b>مكان الدهون مهم.</b> الدهون حول البطن أخطر، لذلك قِس محيط الخصر أيضًا.</li></ul>
<h2 id="tips">نصائح وأخطاء شائعة</h2>
<ul><li><b>أدخل الطول بالسنتيمتر</b> (170 لا 1.70) عند اختيار النظام المتري.</li>
<li><b>زن نفسك صباحًا</b> وبملابس خفيفة للحصول على رقم ثابت.</li>
<li><b>لا تعتمد على رقم واحد.</b> إذا كان مؤشرك 30 أو أكثر، أو محيط خصرك في منطقة الخطر، استشر طبيبًا.</li>
<li><b>التغيير البطيء أفضل.</b> خسارة جزء صغير من الوزن تفيد الصحة.</li></ul>
<h2 id="faq" style="margin-top:22px">أسئلة شائعة</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">المصادر (تم التحقق في 24 نوفمبر 2026): <a href="https://www.who.int/ar/news-room/fact-sheets/detail/obesity-and-overweight" rel="nofollow">منظمة الصحة العالمية — السمنة وزيادة الوزن</a>؛ <a href="https://www.who.int/europe/news-room/fact-sheets/item/nutrition---maintaining-a-healthy-lifestyle" rel="nofollow">منظمة الصحة العالمية (أوروبا) — تصنيف مؤشر كتلة الجسم</a>؛ <a href="https://moh.gov.sa/awarenessplateform/ChronicDisease/Pages/Obesity.aspx" rel="nofollow">وزارة الصحة السعودية — السمنة</a>؛ <a href="https://www.iarc.who.int/news-events/who-guidelines-on-waist-circumference-and-physical-activity-and-their-joint-association-with-cancer-risk/" rel="nofollow">الوكالة الدولية لبحوث السرطان (WHO) — محيط الخصر</a>؛ <a href="https://www.stats.gov.sa/documents/20117/1400941/Health+Determinants+Statistics+Publication+2024+AR.pdf/e5f18332-a904-78cc-5b84-16f27722d5f7?t=1734054150484" rel="nofollow">الهيئة العامة للإحصاء — إحصاءات محددات الصحة 2024</a>؛ <a href="https://cdn.who.int/media/docs/default-source/ncds/ncd-surveillance/data-reporting/united-arab-emirates/uae-national-health-survey-report-2017-2018.pdf?sfvrsn=86b8b1d9_1" rel="nofollow">المسح الصحي الوطني الإماراتي 2017–2018</a>؛ <a href="https://cdn.who.int/media/docs/default-source/ncds/ncd-surveillance/data-reporting/egpyt/steps/egypt-steps-survey-2017-fact-sheet.pdf?sfvrsn=33c64cb7_2&amp;download=true" rel="nofollow">مسح STEPS مصر 2017</a>؛ <a href="https://cdn.who.int/media/docs/default-source/ncds/ncd-surveillance/data-reporting/kuwait/steps/kuwait-2014-steps-report.pdf?sfvrsn=984898e7_3&amp;download=true" rel="nofollow">مسح STEPS الكويت 2014</a>؛ <a href="https://phs.moph.gov.qa/data/healthy-lifestyle/" rel="nofollow">وزارة الصحة العامة في قطر</a>؛ <a href="https://www.nhs.uk/health-assessment-tools/calculate-your-body-mass-index/calculate-bmi-for-adults" rel="nofollow">NHS — حاسبة BMI للبالغين</a>. المعلومات للتثقيف فقط وليست تشخيصًا طبيًا.</p>'''

SUM='<b>إجابة سريعة:</b> مؤشر كتلة الجسم = الوزن (كغ) ÷ مربع الطول (م). المؤشر الطبيعي للبالغين من <b>18.5 إلى 24.9</b> حسب منظمة الصحة العالمية، و25 فأكثر زيادة في الوزن، و30 فأكثر سمنة. مثال: 70 كغ وطول 170 سم = <b>24.2</b> (وزن طبيعي)، والوزن الطبيعي لطول 170 سم بين 53.5 و72.0 كغ.'
box=f'<p class="hl-ans" style="background:#F3F8FF;border:1px solid #D6E6FD;border-radius:12px;padding:12px 14px;margin:0 0 14px;line-height:1.6">{SUM}</p>'
s=re.sub(r'<section class="card help">.*?</section>',lambda m:'<section class="card help">'+TBL_CSS.replace('nav.tabs{flex-wrap:wrap;overflow:visible;white-space:normal}','')+box+art+'</section>',s,count=1,flags=re.S)
s=re.sub(r'<title>.*?</title>',f'<title>{TITLE}</title>',s,count=1,flags=re.S)
s=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{DESC}">',s,count=1)
s=re.sub(r'(<meta property="og:title" content=")[^"]*',lambda m:m.group(1)+TITLE,s,count=1)
s=re.sub(r'(<meta property="og:description" content=")[^"]*',lambda m:m.group(1)+DESC,s,count=1)
ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub('<[^>]+>','',a)}} for q,a in FAQ]}
s=re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',lambda m:'<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False)+'</script>',s,count=1,flags=re.S)
s=s.replace('<section class="panel" data-calc="bmi">','<section class="app"></section><section class="panel" data-calc="bmi" id="form-wrap">',1)
out=os.path.join(OUT,P.lstrip('/'));os.makedirs(os.path.dirname(out),exist_ok=True);open(out,'w',encoding='utf-8').write(s)
add_top(out,[('إعداد','Hong Life Calculators'),('آخر تحقق','24 نوفمبر 2026'),('المصادر','منظمة الصحة العالمية، وزارة الصحة السعودية، الهيئة العامة للإحصاء')],
 [('form-wrap','الحاسبة'),('figures','تصنيف المؤشر ومحيط الخصر'),('ex','أمثلة محسوبة'),('how','طريقة الحساب'),('tips','نصائح وأخطاء شائعة'),('faq','أسئلة شائعة')],'محتويات الصفحة',('#ar-w','ar'))
t=open(out,encoding='utf-8').read()
t=t.replace('<section class="app"></section>','',1)
t=t.replace('</head>','<style>html[dir=rtl] .hl-toc ol{padding-left:0;padding-right:20px}</style></head>',1)
open(out,'w',encoding='utf-8').write(t)
print(out)
