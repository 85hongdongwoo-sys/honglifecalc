"""대만 페이지: 勞退 월제출 등급표(PG)에 빠져 있던 1~24등급(1,500~28,590)을 채운다 — 배포 때 실행 (2026-11-28).
원본은 PG=HG.slice(...)로 29,500부터만 있어 그보다 낮은 임금이 29,500으로 올려 계산됐다.
근거: 勞工保險局 勞工退休金月提繳工資分級表 2026 (https://www.bli.gov.tw/Files/25709, 62등급 1,500~150,000), 2026-11-28 확인.
Usage: python3 build/patch_tw_pg.py _site"""
import os, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
OLD = 'PG=HG.slice(0,HG.indexOf(150000)+1)'
NEW = ('PG=[1500,3000,4500,6000,7500,8700,9900,11100,12540,13500,15840,16500,17280,17880,19047,20008,'
       '21009,22000,23100,24000,25250,26400,27600,28590].concat(HG.slice(0,HG.indexOf(150000)+1))')
n = 0
for dp, dn, fn in os.walk(os.path.join(root, 'tw')):
    for f in fn:
        if f.endswith('.html'):
            p = os.path.join(dp, f)
            s = open(p, encoding='utf-8').read()
            if OLD in s and NEW not in s:
                open(p, 'w', encoding='utf-8').write(s.replace(OLD, NEW)); n += 1
print('tw PG grades fixed', n)
