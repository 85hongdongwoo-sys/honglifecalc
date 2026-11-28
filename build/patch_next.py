"""계산 결과(#out) 바로 아래에 '같은 주제 다음 계산' 2~3개를 칩으로 연결.
같은 폴더에서 주소(슬러그) 단어가 많이 겹치는 페이지를 고르고, 없으면 바로 옆 페이지.
사이트맵(색인 허용)에 있는 페이지만 대상. 배포 때 patch_related 다음에 실행."""
import collections, html, os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
B = 'https://honglifecalc.com'
N = 3
STOP = {'calculator', 'calculators', 'converter', 'calc', 'calculadora', 'calculo', 'calcul', 'rechner',
        'calcolatore', 'kalkulator', 'kalkulaator', 'html', 'of', 'the', 'to', 'and', 'for', 'de', 'la', 'el',
        'du', 'des', 'der', 'die', 'и', 'online', 'free', 'my', 'a', 'in', 'per', 'vs', 'y', 'e', 'da', 'do'}
HEAD = {'en': 'Next, work out', 'ko': '이어서 계산해 보기', 'es': 'Calcula también', 'pt': 'Calcule também',
        'de': 'Als Nächstes berechnen', 'fr': 'Calculez aussi', 'it': 'Calcola anche', 'nl': 'Reken ook uit',
        'ja': '続けて計算', 'zh': '接着算一算', 'pl': 'Oblicz też', 'tr': 'Bunu da hesaplayın',
        'sv': 'Räkna också ut', 'da': 'Beregn også', 'nb': 'Regn også ut', 'no': 'Regn også ut',
        'id': 'Hitung juga', 'ms': 'Kira juga', 'vi': 'Tính tiếp', 'ru': 'Посчитайте также', 'ar': 'احسب أيضًا',
        'hi': 'यह भी गणना करें', 'th': 'คำนวณต่อ'}
CSS = ('<style id="hl-next-css">.hl-next{margin:12px 0 4px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;'
       'max-width:100%}.hl-next>span{font-size:13px;font-weight:700;opacity:.75;margin-right:2px}'
       '.hl-next a{display:inline-block;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'
       'padding:7px 12px;border-radius:999px;border:1px solid currentColor;font-size:14px;font-weight:600;'
       'text-decoration:none;line-height:1.3;opacity:.92}.hl-next a:hover{opacity:1;text-decoration:underline}'
       '.hl-next a:after{content:" →"}html[dir=rtl] .hl-next a:after{content:" ←"}'
       '@media print{.hl-next{display:none}}html.hl-embed .hl-next{display:none!important}</style>')

def path_of(u):
    return u[len(B):] if u.startswith(B) else u

def file_of(p):
    return os.path.join(root, p.lstrip('/') + ('index.html' if p.endswith('/') else ''))

def natkey(p):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', p)]

GEN = {'calculator', 'converter', 'free', 'online', 'calculate', 'calculates', 'your', 'with', 'from', 'this', 'that',
       'how', 'what', 'and', 'the', 'for', 'use', 'enter', 'get', 'see', 'into', 'are', 'you', 'can', 'its', 'per'}
def toks(p):
    s = open(file_of(p), encoding='utf-8', errors='ignore').read(12000)
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', s)
    txt = html.unescape((t.group(1) if t else '') + ' ' + (d.group(1) if d else '') + ' ' + p.rsplit('/', 1)[-1].replace('-', ' '))
    w = {x for x in re.findall(r'\w{3,}', txt.lower()) if not x.isdigit()}
    return w - GEN - STOP

sm = open(os.path.join(root, 'sitemap.xml'), encoding='utf-8').read()
pages = [path_of(u.strip()) for u in re.findall(r'<loc>([^<]+)</loc>', sm)]
pages = [p for p in pages if p.endswith('.html') and not p.endswith('/index.html') and p.count('/') >= 2 and os.path.isfile(file_of(p))]
groups = collections.defaultdict(list)
for p in pages:
    groups[p.rsplit('/', 1)[0]].append(p)
titles = {}
def title(p):
    if p not in titles:
        s = open(file_of(p), encoding='utf-8', errors='ignore').read(8000)
        m = re.search(r'<title>(.*?)</title>', s, re.S)
        t = html.unescape(m.group(1)).strip() if m else p.rsplit('/', 1)[-1]
        t = re.split(r'\s+[|–—]\s+|\s+\(|\s*[:：]\s+', t)[0].strip()
        titles[p] = t[:48].rstrip() + ('…' if len(t) > 48 else '')
    return titles[p]

done = 0
for folder, mem in groups.items():
    mem.sort(key=natkey)
    n = len(mem)
    if n < 2:
        continue
    T = {p: toks(p) for p in mem}
    for i, p in enumerate(mem):
        f = file_of(p)
        s = open(f, encoding='utf-8').read()
        if 'class="hl-next"' in s:
            continue
        a = s.find('id="out"')
        if a < 0:
            continue
        b = s.find('</section>', a)
        if b < 0:
            continue
        b += len('</section>')
        dist = lambda j: min((j - i) % n, (i - j) % n)
        cands = sorted((q for q in range(n) if q != i), key=lambda j: (-len(T[p] & T[mem[j]]) / (len(T[p] | T[mem[j]]) or 1), dist(j)))
        picks = [mem[j] for j in cands[:N]]
        lang = (re.search(r'<html[^>]*\blang="([^"]+)"', s[:2000]) or [None, 'en'])[1].split('-')[0].lower()
        links = ''.join(f'<a href="{html.escape(q.rsplit("/", 1)[-1])}">{html.escape(title(q))}</a>' for q in picks)
        block = f'<nav class="hl-next" aria-label="{html.escape(HEAD.get(lang, HEAD["en"]))}"><span>{HEAD.get(lang, HEAD["en"])}</span>{links}</nav>'
        s2 = s[:b] + block + s[b:]
        if 'hl-next-css' not in s2:
            s2 = s2.replace('</head>', CSS + '</head>', 1)
        open(f, 'w', encoding='utf-8').write(s2)
        done += 1
print('next-step links:', done)
