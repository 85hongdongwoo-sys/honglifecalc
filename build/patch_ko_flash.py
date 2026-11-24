"""한국어 허브(/ko/index.html) 첫 배너 시즌 교체 — 배포 때 실행.
수능(11월 19일)이 끝나서 1번 슬라이드를 크리스마스로 바꾼다. 링크는 홍라이프 도구의 크리스마스 D-day·선물 예산 페이지."""
import os, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
p = os.path.join(root, 'ko', 'index.html')
h = open(p, encoding='utf-8').read()
i = h.find('시험장 시간 그대로')
if i < 0:
    sys.exit(0)
a = h.rfind('<div class="fs', 0, i)
b = h.find('<div class="fs', i)
old = h[a:b]
head = old[:old.find('>') + 1]          # keep the slide wrapper (class on / aria-label)
mini = old[old.find('<div class="mini">'):]
new = (head + '<div><span class="k">🎄 시즌 · 크리스마스</span>'
       '<h2>12월 25일 금요일, 3일 연휴<br><em>크리스마스 D-day · 선물 예산</em></h2>'
       '<p>눈 내리는 카운트다운으로 남은 날을 세고, 가족·연인·친구 선물 예산을 사람별로 나눠 남은 돈까지 계산해요.</p>'
       '<a class="cta" href="https://honglife.co.kr/life/christmas.html">크리스마스 D-day 보기 →</a>'
       '<a class="cta2" href="https://honglife.co.kr/life/split-bill.html">연말 모임 N빵</a></div>'
       '<div class="vis" aria-hidden="true"><div class="orb"></div><div class="glass" style="background:linear-gradient(160deg,#9F1239,#BE123C)!important">'
       '<span class="ic">🎄</span><span class="lb">2026 크리스마스</span><span class="num" data-n="12월 25일">12월 25일</span>' + mini)
assert '<div class="mini">' in old and old.count('<div class="fs') == 1
h = h[:a] + new + h[b:]
open(p, 'w', encoding='utf-8').write(h)
print('ko flash: 수능 → 크리스마스')
