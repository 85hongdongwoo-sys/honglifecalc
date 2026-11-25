import sys,re,json,os; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import table, add_top, ORIG, OUT, TBL_CSS
P='/ru/bmi-calculator.html'
s=open(os.path.join(ORIG,P.lstrip('/')),encoding='utf-8').read()

TITLE='Калькулятор ИМТ 2026 – индекс массы тела и норма веса по росту'
DESC='Рассчитайте индекс массы тела по весу и росту, узнайте категорию по классификации ВОЗ и нормальный вес для своего роста. Примеры и таблица по росту.'

# --- calculator: WHO adult classes incl. obesity I/II/III; healthy range 18.5–24.9 ---
old_run=s[s.index('  run(v){'):s.index('function build(id){')]
new_run='''  run(v){
    const kg=v.unit==='i'?v.w*0.453592:v.w,m=v.unit==='i'?v.h*0.0254:v.h/100;
    const bmi=m?kg/(m*m):0;
    const cut=v.asia?[18.5,23,25,30]:[18.5,25,30,35,40];
    const lab=v.asia?['Недостаточный вес','Нормальный вес','Избыточный вес','Ожирение','Тяжёлое ожирение']:['Недостаточный вес','Нормальный вес','Избыточный вес (предожирение)','Ожирение I степени','Ожирение II степени','Ожирение III степени'];
    let i=0;while(i<cut.length&&bmi>=cut[i])i++;
    const lo=18.5*m*m,hi=(v.asia?22.9:24.9)*m*m,toW=x=>v.unit==='i'?fmt(x/0.453592,1)+' фунт.':fmt(x,1)+' кг';
    const diff=!m||!kg?'Введите вес и рост':kg<lo?'До нормального веса не хватает около '+toW(lo-kg):kg>hi?'Нормальный вес для вашего роста меньше примерно на '+toW(kg-hi):'Ваш вес в пределах нормы для вашего роста';
    return {k:'ИМТ',big:fmt(bmi,1),sub:m&&kg?lab[i]:'',rows:[['Нормальный вес при вашем росте','',toW(lo)+' – '+toW(hi)],
      ...cut.map((c,j)=>[lab[j+1],'','≥ '+fmt(c,1)])],
      note:'<b>'+diff+'.</b> Для взрослых от 20 лет. ИМТ – инструмент для скрининга, а не диагноз: он не отличает мышцы от жира и не подходит детям и беременным.'};
  }
};
'''
s=s.replace(old_run,new_run,1)

def bmi(h,w): return w/(h/100)**2
def cls(b):
    for c,l in [(18.5,'недостаточный вес'),(25,'нормальный вес'),(30,'избыточный вес'),(35,'ожирение I степени'),(40,'ожирение II степени')]:
        if b<c: return l
    return 'ожирение III степени'
f1=lambda x:f"{x:.1f}".replace('.',',')
ex=[]
for h,w in [(160,55),(165,80),(175,95),(180,120)]:
    b=bmi(h,w);m=h/100
    ex.append([f"{h} см",f"{w} кг",f1(b),cls(b),f"{f1(18.5*m*m)} – {f1(24.9*m*m)} кг"])
hw=[[f"{h} см",f1(18.5*(h/100)**2),f1(24.9*(h/100)**2),f1(29.9*(h/100)**2)] for h in range(150,195,5)]
print(ex)
print(f1(70/1.7**2), f1(100/1.7**2), f1(18.5*1.7**2), f1(24.9*1.7**2), f1(18.5*1.6**2), f1(24.9*1.6**2), f1(18.5*1.8**2), f1(24.9*1.8**2))

FAQ=[
("Как рассчитать индекс массы тела?","Разделите вес в килограммах на рост в метрах, возведённый в квадрат. Пример: вес 70 кг, рост 1,70 м. 1,70 × 1,70 = 2,89. 70 ÷ 2,89 = 24,2. Это нормальный вес."),
("Какой ИМТ считается нормальным?","Для взрослых – от 18,5 до 24,9 по классификации ВОЗ. От 25 до 29,9 – избыточный вес (предожирение), 30 и больше – ожирение."),
("Какой нормальный вес при росте 170 см?","Примерно от 53,5 до 72,0 кг – это ИМТ от 18,5 до 24,9. При росте 160 см норма – от 47,4 до 63,7 кг, при росте 180 см – от 59,9 до 80,7 кг."),
("Точен ли ИМТ для спортсменов?","Не всегда. ИМТ не отличает мышцы от жира. У человека с большой мышечной массой ИМТ может быть «избыточным», хотя жира мало. Здесь помогает измерение талии."),
("Подходит ли ИМТ для детей и беременных?","Нет. Для детей и подростков от 5 до 19 лет ВОЗ оценивает ИМТ по возрасту и полу по специальным таблицам роста. Во время беременности взрослые пороги не используют."),
("Какая окружность талии считается нормальной?","По данным ВОЗ риск для здоровья повышен у мужчин с талией от 94 см и у женщин от 80 см. Сильно повышен – от 102 см у мужчин и от 88 см у женщин."),
("Зачем нужны азиатские пороги ИМТ?","У жителей Азии риск болезней растёт уже при более низком ИМТ. Поэтому для Азиатско-Тихоокеанского региона ВОЗ предлагала считать избыточным вес от 23, а ожирением – от 25. Включите эту галочку, если она к вам относится."),
]

art='''<h2 id="figures">Классификация ИМТ для взрослых (ВОЗ)</h2>
'''+table(['ИМТ','Категория'],[['меньше 18,5','Недостаточный вес'],['18,5 – 24,9','Нормальный вес'],['25,0 – 29,9','Избыточный вес (предожирение)'],['30,0 – 34,9','Ожирение I степени'],['35,0 – 39,9','Ожирение II степени'],['40 и больше','Ожирение III степени']])+'''
<p class="note">ВОЗ считает избыточным вес при ИМТ 25 и больше, а ожирением – при ИМТ 30 и больше (для взрослых).</p>
<h3>Окружность талии</h3>
'''+table(['','Риск повышен','Риск сильно повышен'],[['Мужчины','от 94 см','от 102 см'],['Женщины','от 80 см','от 88 см']])+'''
<p class="note">Пороги ВОЗ. Жир на животе опаснее для здоровья, поэтому талию стоит мерить вместе с ИМТ.</p>
<p class="note">В мире в 2024 году избыточный вес был у 45% взрослых (2,6 млрд человек), из них ожирение – у 940 млн (16%), по данным ВОЗ.</p>
<h2 id="ex">Примеры расчёта</h2>
'''+table(['Рост','Вес','ИМТ','Категория','Нормальный вес при этом росте'],ex)+'''
<h3>Нормальный вес по росту</h3>
<div id="ru-w">'''+table(['Рост','Минимум нормы, кг','Максимум нормы, кг','Граница ожирения, кг'],hw)+'''</div>
<p class="note">Посчитано формулой этой страницы: минимум = 18,5 × рост², максимум = 24,9 × рост², граница ожирения = 29,9 × рост² (рост в метрах).</p>
<h2 id="how">Как считать: простыми словами</h2>
<p>Пример: вес 100 кг, рост 170 см.</p>
<ul><li>Переводим рост в метры: 170 см = 1,70 м.</li>
<li>Умножаем рост сам на себя: 1,70 × 1,70 = 2,89.</li>
<li>Делим вес на это число: 100 ÷ 2,89 = <b>34,6</b>. Это ожирение I степени.</li></ul>
<p><b>Индекс массы тела</b> (ИМТ) – число, которое связывает вес и рост. Формула: вес (кг) ÷ рост² (м). Для американских единиц калькулятор сам переводит фунты в килограммы, а дюймы – в метры.</p>
<h3>Чего ИМТ не показывает</h3>
<ul><li><b>Не отличает мышцы от жира.</b> Спортсмен может получить «избыточный вес».</li>
<li><b>Не для детей и подростков.</b> Для них есть нормы по возрасту и полу.</li>
<li><b>Не для беременных.</b></li>
<li><b>Не показывает, где жир.</b> Жир на животе опаснее, поэтому мерьте и талию.</li></ul>
<h2 id="tips">Советы и частые ошибки</h2>
<ul><li><b>Рост вводите в сантиметрах</b> (170, а не 1,70), если выбраны метрические единицы.</li>
<li><b>Взвешивайтесь утром</b> и в лёгкой одежде – так результат стабильнее.</li>
<li><b>Не делайте выводов по одному числу.</b> Если ИМТ 30 и больше или талия в зоне риска, обсудите это с врачом.</li>
<li><b>Худеть лучше медленно.</b> Даже небольшое снижение веса полезно для здоровья.</li></ul>
<h2 id="faq" style="margin-top:22px">Частые вопросы</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Источники (проверено 25 ноября 2026 г.): <a href="https://www.who.int/ru/news-room/fact-sheets/detail/obesity-and-overweight" rel="nofollow">ВОЗ – Ожирение и избыточный вес</a>; <a href="https://www.who.int/europe/news-room/fact-sheets/item/nutrition---maintaining-a-healthy-lifestyle" rel="nofollow">ВОЗ (Европа) – классификация ИМТ</a>; <a href="https://www.who.int/publications/i/item/9789241501491" rel="nofollow">ВОЗ – окружность талии и соотношение талии и бёдер (2008)</a>; <a href="https://iris.who.int/handle/10665/206936" rel="nofollow">ВОЗ, Азиатско-Тихоокеанский регион – пороги ИМТ (2000)</a>. Расчёты сделаны формулой этого калькулятора. Это справочная информация, а не медицинская консультация.</p>'''

SUM=None
try:
    SUM=json.load(open('/tmp/claude-0/-home-claude/22ae3873-7b3e-5235-a76f-08bef551a9af/scratchpad/summ_F5.json',encoding='utf-8')).get(P)
except Exception: pass
try:
    SUM=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','summaries.json'),encoding='utf-8')).get(P) or SUM
except Exception: pass
box=f'<p class="hl-ans" style="background:#F3F8FF;border:1px solid #D6E6FD;border-radius:12px;padding:12px 14px;margin:0 0 14px;line-height:1.6">{SUM}</p>' if SUM else ''
s=re.sub(r'<section class="card help">.*?</section>',lambda m:'<section class="card help">'+TBL_CSS.replace('nav.tabs{flex-wrap:wrap;overflow:visible;white-space:normal}','')+box+art+'</section>',s,count=1,flags=re.S)
s=re.sub(r'<title>.*?</title>',f'<title>{TITLE}</title>',s,count=1,flags=re.S)
s=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{DESC}">',s,count=1)
s=re.sub(r'(<meta property="og:title" content=")[^"]*',lambda m:m.group(1)+TITLE,s,count=1)
s=re.sub(r'(<meta property="og:description" content=")[^"]*',lambda m:m.group(1)+DESC,s,count=1)
ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub('<[^>]+>','',a)}} for q,a in FAQ]}
ldtag='<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False)+'</script>'
if re.search(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage"',s):
    s=re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',lambda m:ldtag,s,count=1,flags=re.S)
else:
    s=s.replace('</head>',ldtag+'</head>',1)
s=s.replace('<section class="panel" data-calc="bmi">','<section class="app"></section><section class="panel" data-calc="bmi" id="form-wrap">',1)
out=os.path.join(OUT,P.lstrip('/'));os.makedirs(os.path.dirname(out),exist_ok=True);open(out,'w',encoding='utf-8').write(s)
add_top(out,[('Автор','Hong Life Calculators'),('Проверено','25 ноября 2026 г.'),('Источники','ВОЗ')],
 [('form-wrap','Калькулятор'),('figures','Классификация ИМТ и талия'),('ex','Примеры'),('how','Как считать'),('tips','Советы'),('faq','Частые вопросы')],'Содержание',('#ru-w','ru'))
t=open(out,encoding='utf-8').read()
t=t.replace('<section class="app"></section>','',1)
open(out,'w',encoding='utf-8').write(t)
print(out)
