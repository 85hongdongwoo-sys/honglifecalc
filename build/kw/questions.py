"""사람들이 실제로 묻는 질문 모으기 — 주제마다 질문형 앞말(how much, is, can I …)을 붙여 구글 자동완성을 받는다. GitHub Actions에서 실행 (2026-11-28).
입력: build/kw/q_seeds.txt — 한 줄에 '페이지경로|주제어' (예: /uk/stamp-duty-calculator.html|stamp duty)
출력: q-out/q.json {페이지: {topic, lang, gl, qs:[질문...]}}
Usage: python3 build/kw/questions.py build/kw/q_seeds.txt q-out"""
import json, os, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
seeds, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
GL = {'us': ('en', 'us'), 'en': ('en', 'us'), 'uk': ('en', 'gb'), 'ca': ('en', 'ca'), 'au': ('en', 'au'), 'in': ('en', 'in'), 'ie': ('en', 'ie'), 'nz': ('en', 'nz'),
      'sg': ('en', 'sg'), 'ph': ('en', 'ph'), 'za': ('en', 'za'), 'ng': ('en', 'ng'), 'my': ('ms', 'my'),
      'de': ('de', 'de'), 'at': ('de', 'at'), 'ch': ('de', 'ch'), 'fr': ('fr', 'fr'), 'be': ('fr', 'be'), 'es': ('es', 'es'), 'mx': ('es', 'mx'), 'ar': ('es', 'ar'),
      'arg': ('es', 'ar'), 'co': ('es', 'co'), 'cl': ('es', 'cl'), 'it': ('it', 'it'), 'pt': ('pt', 'pt'), 'br': ('pt', 'br'), 'nl': ('nl', 'nl'), 'pl': ('pl', 'pl'),
      'jp': ('ja', 'jp'), 'tw': ('zh-TW', 'tw'), 'ru': ('ru', 'ru'), 'tr': ('tr', 'tr'), 'se': ('sv', 'se'), 'no': ('no', 'no'), 'dk': ('da', 'dk'),
      'id': ('id', 'id'), 'vn': ('vi', 'vn'), 'hi': ('hi', 'in'), 'ae': ('en', 'ae'), 'ko': ('ko', 'kr')}
PRE = {
    'en': ['how much {t}', 'how is {t}', 'how to {t}', 'is {t}', 'do i {t}', 'do you {t}', 'can i {t}', 'what is {t}', 'why {t}', 'when {t}', 'does {t}', '{t} on', '{t} if', '{t} for'],
    'es': ['cuánto {t}', 'cuanto {t}', 'cómo {t}', 'como calcular {t}', 'qué es {t}', 'cuándo {t}', 'por qué {t}', '{t} si', '{t} de', '{t} para'],
    'pt': ['quanto {t}', 'como {t}', 'o que é {t}', 'quando {t}', '{t} de', '{t} para'],
    'de': ['wie viel {t}', 'wie hoch {t}', 'wie {t}', 'was ist {t}', 'wann {t}', 'muss ich {t}', '{t} bei', '{t} für'],
    'fr': ['combien {t}', 'comment {t}', "qu'est-ce que {t}", 'quand {t}', '{t} pour', '{t} si'],
    'it': ['quanto {t}', 'come {t}', 'cosa è {t}', 'quando {t}', '{t} per'],
    'nl': ['hoeveel {t}', 'hoe {t}', 'wat is {t}', 'wanneer {t}', '{t} bij'],
    'pl': ['ile {t}', 'jak {t}', 'co to {t}', 'kiedy {t}', '{t} od'],
    'tr': ['{t} ne kadar', '{t} nasıl', '{t} kaç', '{t} nedir', '{t} ne zaman', '{t} hesaplama'],
    'ru': ['сколько {t}', 'как {t}', 'что такое {t}', 'когда {t}', '{t} при'],
    'ja': ['{t} いくら', '{t} 計算方法', '{t} とは', '{t} いつ', '{t} 何'],
    'vi': ['{t} bao nhiêu', 'cách tính {t}', '{t} là gì', '{t} khi nào'],
    'id': ['berapa {t}', 'cara {t}', 'apa itu {t}', 'kapan {t}'],
    'ms': ['berapa {t}', 'cara {t}', 'apa itu {t}', 'bila {t}'],
    'sv': ['hur mycket {t}', 'hur {t}', 'vad är {t}', 'när {t}'],
    'no': ['hvor mye {t}', 'hvordan {t}', 'hva er {t}', 'når {t}'],
    'da': ['hvor meget {t}', 'hvordan {t}', 'hvad er {t}', 'hvornår {t}'],
    'zh-TW': ['{t} 多少', '{t} 怎麼算', '{t} 是什麼'],
    'hi': ['{t} कितना', '{t} कैसे', '{t} क्या है'],
    'ko': ['{t} 얼마', '{t} 계산', '{t} 언제', '{t} 조건'],
}


def sugg(q, hl, gl):
    u = 'https://suggestqueries.google.com/complete/search?client=firefox&hl=%s&gl=%s&q=%s' % (hl, gl, urllib.parse.quote(q))
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15)
            return json.loads(r.read().decode('utf-8', 'ignore'))[1]
        except Exception:
            time.sleep(2)
    return []


res = {}
for line in open(seeds, encoding='utf-8'):
    if '|' not in line or line.startswith('#'):
        continue
    page, topic = [x.strip() for x in line.split('|', 1)]
    hl, gl = GL.get(page.split('/')[1], ('en', 'us'))
    lang = hl if hl in PRE else hl.split('-')[0]
    qs = []
    for p in PRE.get(lang, PRE['en']):
        for s in sugg(p.format(t=topic), hl, gl):
            s = ' '.join(s.split())
            if s not in qs:
                qs.append(s)
        time.sleep(0.4)
    res[page] = {'topic': topic, 'hl': hl, 'gl': gl, 'qs': qs}
    print(page, len(qs), flush=True)
json.dump(res, open(os.path.join(out, 'q.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
