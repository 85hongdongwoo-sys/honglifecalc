"""하루치 다시 올리기: build/kw/release.json 순서대로, 아직 noindex_list에 있는 페이지 N개를 목록에서 빼고 lastmod를 오늘로.
Usage: python3 build/kw/release_next.py 100"""
import datetime, json, os, sys
if not os.path.isfile('build/kw/release.json'):
    print('release.json not ready yet'); sys.exit(0)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
R = json.load(open('build/kw/release.json', encoding='utf-8'))
L = open('build/noindex_list.txt', encoding='utf-8').read().split('\n')
cur = {x.strip() for x in L}
todo = [u for u in R if u in cur][:N]
if not todo:
    print('nothing left'); sys.exit(0)
ts = set(todo)
open('build/noindex_list.txt', 'w', encoding='utf-8').write('\n'.join(x for x in L if x.strip() not in ts))
SX = 'build/sitemap_exclude.txt'   # 사이트맵 제외 목록에서도 빼야 구글이 사이트맵으로 찾음
if os.path.isfile(SX):
    X = open(SX, encoding='utf-8').read().split('\n')
    open(SX, 'w', encoding='utf-8').write('\n'.join(x for x in X if x.strip() not in ts))
lm = json.load(open('build/lastmod.json', encoding='utf-8'))
today = datetime.date.today().isoformat()
for u in todo: lm[u] = today
json.dump(lm, open('build/lastmod.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open('build/kw/released.log', 'a', encoding='utf-8').write(''.join('%s %s\n' % (today, u) for u in todo))
print('released', len(todo), 'left', sum(1 for u in R if u in cur) - len(todo))
