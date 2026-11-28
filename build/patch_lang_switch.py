"""언어 버튼: 방문자 언어 대신 '그 페이지 나라의 언어 | 영어(번역)'만 보이게 — 배포 때 실행 (2026-11-28 사용자 요청).
영어 페이지에는 언어 버튼을 띄우지 않는다. 원본 hl-extras-g.js 는 건드리지 않고 배포본(_site)만 고친다.
Usage: python3 build/patch_lang_switch.py _site"""
import os, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
p = os.path.join(root, 'assets', 'hl-extras-g.js')
s = open(p, encoding='utf-8').read()
old = "if(vis==='en'&&page==='en')return;\n  var loc=vis!=='en'?vis:page;"
new = "if(page==='en')return;\n  var loc=page;"
if new in s:
    print('lang switch: already'); sys.exit(0)
assert old in s, 'pattern not found'
s = s.replace(old, new, 1)
# 나라 허브(/br/ 등)의 '영어'는 영어 첫 화면(/)으로 — 다른 나라(/ae/) 허브로 가지 않게
o2 = "if(page==='en')enHref=here;else enHref=alt('en')||'/en/';"
n2 = "if(page==='en')enHref=here;else enHref=(D.querySelector('meta[name=hl-hubs]')?'/':alt('en'))||'/en/';"
assert o2 in s, 'pattern2 not found'
s = s.replace(o2, n2, 1)
open(p, 'w', encoding='utf-8').write(s)
print('lang switch: page language + English only')
