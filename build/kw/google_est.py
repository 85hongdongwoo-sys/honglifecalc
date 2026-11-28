"""한국어 검색어 인기도 추정 (구글 자동완성 기반) — 네이버 검색량 자료가 없을 때 대신 쓴다.
1) 한국어 페이지 주제어마다 '주제어 + 얼마/계산/조건/기준/언제/방법/신청/2027' 자동완성으로 실제 검색어 후보를 모은다.
2) 후보마다 앞글자를 몇 자만 쳐도 자동완성 1~10위에 뜨는지(이분 탐색) 잰다. 짧게 쳐도 뜨면 많이 찾는 검색어.
3) 점수 = 1 - (뜨기 시작한 글자 수 / 전체 글자 수) + 순위 보정 → 구간으로 월 검색수를 '추정'한다.
   (상위 15%: 5,000+, 15~45%: 2,000~5,000, 그 아래: 2,000 미만 — 네이버 자료가 생기면 보정)
사용: python3 build/kw/google_est.py _site out [최대후보수]"""
import html, json, os, re, sys, time, urllib.parse, urllib.request
root, out = sys.argv[1], sys.argv[2]
MAXC = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
os.makedirs(out, exist_ok=True)
CACHE = {}
def sugg(q):
    if q in CACHE: return CACHE[q]
    u = 'https://suggestqueries.google.com/complete/search?client=firefox&hl=ko&gl=kr&q=' + urllib.parse.quote(q)
    for t in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15)
            res = [' '.join(x.split()) for x in json.loads(r.read().decode('utf-8', 'ignore'))[1]]
            CACHE[q] = res; time.sleep(0.12); return res
        except Exception:
            time.sleep(2 + 3 * t)
    CACHE[q] = []; return []
pages = {}
for d, _, fs in os.walk(os.path.join(root, 'ko')):
    for f in fs:
        if not f.endswith('.html'): continue
        fp = os.path.join(d, f); s = open(fp, encoding='utf-8', errors='ignore').read(8000)
        t = re.search(r'<title>(.*?)</title>', s, re.S)
        if not t or 'http-equiv="refresh"' in s.lower(): continue
        pages['/' + os.path.relpath(fp, root).replace(os.sep, '/')] = html.unescape(t.group(1)).strip()
def seed(title):
    t = re.split(r'\s*[|·:–—(]\s*', title)[0]
    t = re.sub(r'\s*(계산기|계산|조회|확인)$', '', t).strip()
    return t if 2 <= len(t) <= 18 else None
seeds = {}
for p, t in pages.items():
    s = seed(t)
    if s: seeds.setdefault(s, p)
print('pages', len(pages), 'seeds', len(seeds))
SUF = ['', ' 얼마', ' 계산', ' 조건', ' 기준', ' 언제', ' 방법', ' 신청', ' 2027']
cand = {}
for i, (s, p) in enumerate(seeds.items()):
    for suf in SUF:
        for k in sugg(s + suf):
            if k not in cand: cand[k] = p
    if i % 100 == 0: print('seed', i, len(cand))
    if len(cand) >= MAXC: break
print('candidates', len(cand))
def first_hit(kw):
    """kw 가 자동완성 10위 안에 뜨는 가장 짧은 앞부분 길이와 그때 순위"""
    lo, hi, best = 1, len(kw), (len(kw), 10)
    while lo <= hi:
        m = (lo + hi) // 2
        r = sugg(kw[:m])
        if kw in r: best = (m, r.index(kw)); hi = m - 1
        else: lo = m + 1
    return best
rows = []
for n, (kw, p) in enumerate(cand.items()):
    L, rank = first_hit(kw)
    sc = round(1 - L / max(1, len(kw)) + (10 - rank) / 100, 3)
    rows.append({'kw': kw, 'page': p, 'prefix': L, 'rank': rank, 'score': sc,
                 'q': bool(re.search(r'얼마|언제|몇|기준|조건|방법|하는법|뜻|차이|자격|신청|대상|금액|나이|계산법', kw))})
    if n % 300 == 0: print('scored', n, '/', len(cand))
rows.sort(key=lambda r: -r['score'])
N = len(rows)
for i, r in enumerate(rows):
    r['est'] = '5000+' if i < 0.15 * N else '2000-5000' if i < 0.45 * N else '<2000'
band = [r for r in rows if r['est'] == '2000-5000']
json.dump({'built': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'method': '구글 자동완성 앞글자 깊이로 추정',
           'n': N, 'band_2000_5000': band, 'all': rows}, open(os.path.join(out, 'kw_est.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('done', N, 'band', len(band))
