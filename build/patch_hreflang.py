"""Adds a hreflang cluster linking the global hub (/) and every country hub (/us/, /uk/, ...).
Runs in the deploy workflow after the site bundle is unpacked into _site/."""
import os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
B = 'https://honglifecalc.com/'
REG = {'arg': 'AR', 'uk': 'GB'}
LANG_DIRS = {'ko', 'en', 'zh', 'hi', 'ar', 'fr', 'pt', 'ru', 'es', 'id'}
hubs = []
for d in sorted(os.listdir(root)):
    p = os.path.join(root, d, 'index.html')
    if d in LANG_DIRS or not (len(d) in (2, 3) and os.path.isfile(p)):
        continue
    m = re.search(r'<html[^>]*\blang="([^"]+)"', open(p, encoding='utf-8').read(1500))
    if not m:
        continue
    hubs.append((d, m.group(1).split('-')[0] + '-' + REG.get(d, d.upper())))
tags = ''.join(f'<link rel="alternate" hreflang="{t}" href="{B}{d}/">' for d, t in hubs)
tags += f'<link rel="alternate" hreflang="x-default" href="{B}">'
n = 0
for d in [''] + [h[0] for h in hubs]:
    p = os.path.join(root, d, 'index.html')
    s = open(p, encoding='utf-8').read()
    if 'data-hubset' in s:
        continue
    # 2026-11-28: 원본에 미리 박혀 있던 엉킨 언어 연결(영어→/en/iq/, 독일어→/at/ 등, x-default 중복)을 지우고 나라 허브 묶음만 남긴다
    s = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\s*', '', s)
    s2 = s.replace('</head>', f'<meta name="hl-hubs" data-hubset="1">{tags}</head>', 1)
    if s2 != s:
        open(p, 'w', encoding='utf-8').write(s2); n += 1
print('hreflang hubs:', len(hubs), 'pages patched:', n)
