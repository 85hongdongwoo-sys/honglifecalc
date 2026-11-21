"""모든 안쪽 페이지(한국어+해외)에 Apple HIG 느낌 스타일(/assets/hl-hig.css)을 붙인다 — 배포 때 실행. 허브(/ko/index.html)는 제외."""
import os, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
TAG = '<link rel="stylesheet" href="/assets/hl-hig.css?v=2" id="hl-hig">'
n = 0
SKIP_TOP = {'assets', 'ev', 'fx', 'geo', 'embed', 'games'}
for dp, dn, fn in os.walk(root):
    rel = os.path.relpath(dp, root)
    if rel == '.' or rel.split(os.sep)[0] in SKIP_TOP:
        continue
    for f in fn:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dp, f)
        if f == 'index.html':
            continue  # 허브(목록) 페이지는 제외
        s = open(p, encoding='utf-8').read()
        if 'id="hl-hig"' in s or '</head>' not in s:
            continue
        open(p, 'w', encoding='utf-8').write(s.replace('</head>', TAG + '</head>', 1)); n += 1
print('hig pages:', n)
