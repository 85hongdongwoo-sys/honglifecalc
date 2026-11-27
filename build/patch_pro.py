"""해외(한국어 외) 페이지에 신뢰감 테마(/assets/hl-pro.css)를 붙이고, 구조화 데이터의 발행처 이름을 영문으로 통일한다 — 배포 때 실행.
이유(2026-11-27 분석): 돈·세금 검색자는 '공식 자료처럼 정돈된' 사이트를 고른다. 풀밭 배경·강아지 장식은 한국어 페이지에만 남긴다.
Usage: python3 build/patch_pro.py _site"""
import os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else '_site'
TAG = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
       '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">'
       '<link rel="stylesheet" href="/assets/hl-pro.css?v=2" id="hl-pro">')
MOTION = '<script src="/assets/hl-motion.js?v=1" defer></script>'  # 메인(첫 화면)만
SKIP_TOP = {'assets', 'ko', 'embed'}
LANG = re.compile(r'<html[^>]*\blang="([^"]*)"', re.I)
n = 0
for dp, dn, fn in os.walk(root):
    rel = os.path.relpath(dp, root)
    if rel != '.' and rel.split(os.sep)[0] in SKIP_TOP:
        continue
    for f in fn:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dp, f)
        s = open(p, encoding='utf-8').read()
        m = LANG.search(s[:600])
        if not m or m.group(1).lower().startswith('ko') or 'id="hl-pro"' in s or '</head>' not in s:
            continue
        s = s.replace('</head>', TAG + '</head>', 1)
        if rel == '.' and f == 'index.html':
            s = s.replace('</body>', MOTION + '</body>', 1)
        s = s.replace('"name": "Hong Life (홍라이프)"', '"name": "Hong Life Calculators"').replace('"name":"Hong Life (홍라이프)"', '"name":"Hong Life Calculators"')
        open(p, 'w', encoding='utf-8').write(s); n += 1
print('pro theme pages:', n)
