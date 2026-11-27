"""검색될 만한 단어 찾기 — 대기 중(noindex) 페이지마다 구글 자동완성(미국/각 나라)을 모은다. GitHub Actions에서 실행.
입력: _site (배포 사이트), build/noindex_list.txt. 출력: kw-out/kw.json {url: {seed, lang, sugg:[...] }}
Usage: python3 build/kw/suggest.py _site kw-out [max_pages]"""
import html, json, os, re, sys, time, urllib.parse, urllib.request
site, out = sys.argv[1], sys.argv[2]; mx = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
os.makedirs(out, exist_ok=True)
GL = {'en': ('en', 'us'), 'us': ('en', 'us'), 'uk': ('en', 'gb'), 'ca': ('en', 'ca'), 'au': ('en', 'au'), 'in': ('en', 'in'), 'nz': ('en', 'nz'), 'ie': ('en', 'ie'),
      'sg': ('en', 'sg'), 'ph': ('en', 'ph'), 'za': ('en', 'za'), 'de': ('de', 'de'), 'at': ('de', 'at'), 'ch': ('de', 'ch'), 'fr': ('fr', 'fr'), 'be': ('fr', 'be'),
      'es': ('es', 'es'), 'mx': ('es', 'mx'), 'ar': ('es', 'ar'), 'co': ('es', 'co'), 'cl': ('es', 'cl'), 'it': ('it', 'it'), 'pt': ('pt', 'pt'), 'br': ('pt', 'br'),
      'nl': ('nl', 'nl'), 'pl': ('pl', 'pl'), 'jp': ('ja', 'jp'), 'tw': ('zh-TW', 'tw'), 'zh': ('zh-CN', 'cn'), 'ru': ('ru', 'ru'), 'tr': ('tr', 'tr'),
      'se': ('sv', 'se'), 'no': ('no', 'no'), 'dk': ('da', 'dk'), 'fi': ('fi', 'fi'), 'id': ('id', 'id'), 'vn': ('vi', 'vn'), 'th': ('th', 'th'), 'ko': ('ko', 'kr')}
def seed_of(title):
    t = html.unescape(title)
    t = re.split(r'\s[–—|-]\s|\(|:', t)[0]
    t = re.sub(r'\b20\d\d(?:[-/–]\d{2,4})?\b', '', t)
    t = re.sub(r'[?!.,]+', ' ', t)
    return ' '.join(t.lower().split())
def sugg(q, hl, gl):
    u = 'https://suggestqueries.google.com/complete/search?client=firefox&hl=%s&gl=%s&q=%s' % (hl, gl, urllib.parse.quote(q))
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15)
            return json.loads(r.read().decode('utf-8', 'ignore'))[1]
        except Exception as e:
            time.sleep(2)
    return None
TG = 'build/kw/targets.txt' if os.path.isfile('build/kw/targets.txt') else 'build/noindex_list.txt'
urls = [l.strip() for l in open(TG, encoding='utf-8') if l.startswith('/')][:mx]
res = {}
prev = os.path.join(out, 'kw.json')
for i, u in enumerate(urls):
    p = os.path.join(site, u.lstrip('/') + ('index.html' if u.endswith('/') else ''))
    if not os.path.isfile(p): continue
    s = open(p, encoding='utf-8', errors='ignore').read(6000)
    m = re.search(r'<title>(.*?)</title>', s, re.S)
    if not m: continue
    top = u.split('/')[1]; hl, gl = GL.get(top, ('en', 'us'))
    seed = seed_of(m.group(1))
    words = seed.split()
    short = ' '.join(w for w in words if w not in ('calculator', 'calculadora', 'rechner', 'calculateur', 'calcolatore', 'kalkulator', 'calculadora', 'calculator')) or seed
    a = sugg(seed, hl, gl) or []
    b = sugg(short, hl, gl) or [] if short != seed else []
    res[u] = {'seed': seed, 'short': short, 'hl': hl, 'gl': gl, 'title': html.unescape(m.group(1)).strip(), 'sugg': a, 'sugg_short': b}
    time.sleep(0.35)
    if i % 200 == 0:
        print(i, u, seed, a[:3], flush=True)
        json.dump(res, open(prev, 'w'), ensure_ascii=False)
json.dump(res, open(prev, 'w'), ensure_ascii=False)
print('pages', len(res), 'with suggestions', sum(1 for v in res.values() if v['sugg'] or v['sugg_short']))
