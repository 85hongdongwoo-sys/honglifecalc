"""한국어 '우주' 페이지 링크 — 배포 때 patch_newpages.py 다음에 실행.
1) 첫 화면 '과학·공학' 타일을 눌렀을 때 나오는 목록(sublink) 맨 앞에 넣기
2) /ko/science/ 목록 맨 앞에 넣기"""
import os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
PAGES = [('/ko/science/moon-distance.html', '달까지 거리 실시간', '달까지 거리 실시간 (지금 달과 나의 거리·보름달·ISS)')]
hub = os.path.join(root, 'ko', 'index.html')
if os.path.isfile(hub):
    h = open(hub, encoding='utf-8').read()
    for url, short, _ in PAGES:
        if f'data-group="sci" href="{url}"' not in h:
            h = re.sub(r'(<a class="sublink" data-group="sci" href="/ko/science/" hidden>[^<]*</a>)',
                       lambda m: m.group(1) + f'\n<a class="sublink" data-group="sci" href="{url}" hidden>{short}</a>', h, count=1)
    open(hub, 'w', encoding='utf-8').write(h)
sci = os.path.join(root, 'ko', 'science', 'index.html')
if os.path.isfile(sci):
    s = open(sci, encoding='utf-8').read()
    for url, _, long in PAGES:
        rel = url.rsplit('/', 1)[1]
        if f'href="{rel}"' not in s:
            s = s.replace('<h3>역학</h3>', f'<h3>우주·천문</h3><ul><li><a href="{rel}">{long}</a></li></ul><h3>역학</h3>', 1)
    open(sci, 'w', encoding='utf-8').write(s)
print('ko space links done')
