"""검색어(자동완성) 기반 제목·H1·설명 적용 — 배포 때 실행. 데이터: build/kw/titles.json (build/kw/choose.py가 만듦).
Usage: python3 build/patch_kw.py _site"""
import html, json, os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
TP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kw', 'titles.json')
if not os.path.isfile(TP):
    print('no titles.json yet'); sys.exit(0)
T = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kw', 'titles.json'), encoding='utf-8'))
E = lambda s: html.escape(s, quote=True)
n = 0
for u, d in T.items():
    p = os.path.join(root, u.lstrip('/') + ('index.html' if u.endswith('/') else ''))
    if not os.path.isfile(p):
        continue
    s = open(p, encoding='utf-8').read()
    m = re.search(r'<title>(.*?)</title>', s, re.S)
    if not m:
        continue
    oldfull = m.group(1)
    new = d['title']
    s = s.replace('<title>%s</title>' % oldfull, '<title>%s</title>' % E(new), 1)
    for prop in ('og:title', 'twitter:title'):
        s = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*' % prop, lambda mm: mm.group(1) + E(new), s, count=1)
    oldcore = html.unescape(re.split(r' – Free Calculator| \| ', oldfull)[0])
    s = s.replace('"name": "%s"' % oldcore.replace('"', '\\"'), '"name": "%s"' % new.replace('"', '\\"'))
    prim = d['primary']
    # H1: 검색어 그대로(계산기 단어는 강조)
    h1 = E(new.split(' – ')[0])
    h1 = re.sub(r'(?i)\b(calculator)\b', r'<b>\1</b>', h1, count=1)
    s = re.sub(r'<h1>.*?</h1>', '<h1>%s</h1>' % h1, s, count=1, flags=re.S)
    md = re.search(r'<meta name="description" content="([^"]*)"', s)
    if md and prim.lower() not in html.unescape(md.group(1)).lower():
        nd = new.split(' – ')[0] + ': ' + html.unescape(md.group(1))
        s = s.replace(md.group(0), '<meta name="description" content="%s"' % E(nd[:300]), 1)
        s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda mm: mm.group(1) + E(nd[:300]), s, count=1)
    open(p, 'w', encoding='utf-8').write(s); n += 1
print('kw titles applied:', n)
