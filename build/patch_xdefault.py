"""나라 폴더 안 영어 쌍둥이 페이지(no·tr·se·dk·my): 기본(x-default)을 그 나라 언어 페이지로 — 배포 때 실행 (2026-11-28).
'그 나라에서 들어오면 그 나라 언어로, 영어는 번역으로'라는 사용자 요청에 맞춘다. 영어 페이지는 그대로 두고 번역판 역할만 한다.
Usage: python3 build/patch_xdefault.py _site"""
import os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
LOC = {'no': 'nb', 'tr': 'tr', 'se': 'sv', 'dk': 'da', 'my': 'ms'}
ALT = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">')
n = 0
for top, code in LOC.items():
    d = os.path.join(root, top)
    for dp, dn, fn in os.walk(d):
        for f in fn:
            if not f.endswith('.html'):
                continue
            p = os.path.join(dp, f)
            s = open(p, encoding='utf-8').read()
            alts = ALT.findall(s)
            loc = [h for l, h in alts if l.lower().split('-')[0] == code]
            if not loc:
                continue
            s2 = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]+">',
                        f'<link rel="alternate" hreflang="x-default" href="{loc[0]}">', s)
            if s2 != s:
                open(p, 'w', encoding='utf-8').write(s2); n += 1
print('x-default -> local language:', n)
