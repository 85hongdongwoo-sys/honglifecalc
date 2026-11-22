"""2026-11-22: 사용자 요청으로 번역 페이지 2개를 검색에 노출 (noindex 제거) + 영어판과 hreflang 서로 연결.
- /zh/travel-budget-calculator.html  <-> /en/travel-budget-calculator.html (중국어 购物花费 검색이 영어판으로 가던 문제)
- /pl/iq/iq-70-co-oznacza.html       <-> /en/iq/iq-70.html ('ile to 70 iq' 검색이 영어판으로 가던 문제)
Run: HL_ORIG=/tmp/hl_orig python3 build/pages/unnoindex_20261122.py"""
import os, re
ORIG = os.environ.get('HL_ORIG', '/tmp/hl_orig')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'overlay')
B = 'https://honglifecalc.com'
PAIRS = [('en/travel-budget-calculator.html', 'zh/travel-budget-calculator.html', 'zh-Hans'),
         ('en/iq/iq-70.html', 'pl/iq/iq-70-co-oznacza.html', 'pl')]


def rd(p):
    ov = os.path.join(OUT, p)
    return open(ov if os.path.exists(ov) else os.path.join(ORIG, p), encoding='utf-8').read()


def wr(p, s):
    f = os.path.join(OUT, p); os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(s); print('wrote', p)


def add_alt(s, lang, url):
    tag = f'<link rel="alternate" hreflang="{lang}" href="{url}">'
    if tag in s:
        return s
    m = re.search(r'<link rel="alternate" hreflang="x-default"[^>]*>', s)
    return s[:m.start()] + tag + s[m.start():] if m else s.replace('</head>', tag + '</head>', 1)


for en, tr, lang in PAIRS:
    e, t = rd(en), rd(tr)
    t = re.sub(r'<meta name="robots" content="noindex,\s*follow">\s*', '', t, count=1)
    assert 'noindex' not in t, tr
    for code, u in (('en', en), (lang, tr)):
        e = add_alt(e, code, f'{B}/{u}')
        t = add_alt(t, code, f'{B}/{u}')
    wr(en, e); wr(tr, t)
