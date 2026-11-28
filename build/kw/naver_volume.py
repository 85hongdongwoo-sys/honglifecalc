"""네이버 검색광고 키워드 도구로 한국어 페이지 주제어의 월간 검색수 조사.
필요 비밀값(GitHub Secrets): NAVER_AD_CUSTOMER_ID, NAVER_AD_ACCESS_LICENSE, NAVER_AD_SECRET_KEY
(searchad.naver.com → 도구 → API 사용 관리에서 무료 발급)
결과: out/naver_kw.json — 검색어별 PC·모바일 월 검색수, 2,000~5,000 구간 목록과 가장 맞는 우리 페이지.
사용: python3 build/kw/naver_volume.py _site out"""
import base64, hashlib, hmac, html, json, os, re, sys, time, urllib.parse, urllib.request
root, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
CID, KEY, SEC = (os.environ.get(k, '') for k in ('NAVER_AD_CUSTOMER_ID', 'NAVER_AD_ACCESS_LICENSE', 'NAVER_AD_SECRET_KEY'))
if not (CID and KEY and SEC):
    print('비밀값이 없어요: NAVER_AD_CUSTOMER_ID / NAVER_AD_ACCESS_LICENSE / NAVER_AD_SECRET_KEY'); sys.exit(1)
def call(hints):
    ts = str(int(time.time() * 1000)); path = '/keywordstool'
    sig = base64.b64encode(hmac.new(SEC.encode(), f'{ts}.GET.{path}'.encode(), hashlib.sha256).digest()).decode()
    q = urllib.parse.urlencode({'hintKeywords': ','.join(hints), 'showDetail': '1'})
    req = urllib.request.Request(f'https://api.searchad.naver.com{path}?{q}', headers={
        'X-Timestamp': ts, 'X-API-KEY': KEY, 'X-Customer': CID, 'X-Signature': sig})
    for t in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30)).get('keywordList', [])
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(5 * (t + 1)); continue
            print('HTTP', e.code, hints, e.read()[:200]); return []
        except Exception as e:
            print('ERR', e); time.sleep(3)
    return []
def num(v):
    return 5 if isinstance(v, str) else int(v or 0)   # "< 10" → 5
pages = {}
for d, _, fs in os.walk(os.path.join(root, 'ko')):
    for f in fs:
        if not f.endswith('.html'): continue
        fp = os.path.join(d, f); s = open(fp, encoding='utf-8', errors='ignore').read(8000)
        t = re.search(r'<title>(.*?)</title>', s, re.S)
        if not t or 'http-equiv="refresh"' in s.lower(): continue
        rel = '/' + os.path.relpath(fp, root).replace(os.sep, '/')
        pages[rel] = html.unescape(t.group(1)).strip()
def seed(title):
    t = re.split(r'\s*[|·:\-–—(]\s*', title)[0]
    t = re.sub(r'\s*(계산기|계산|조회|확인|표)$', '', t).strip()
    t = re.sub(r'\s+', '', t)  # 키워드 도구는 띄어쓰기 없는 형태로 받음
    return t[:20] if len(t) >= 2 else None
seeds = sorted({x for x in (seed(t) for t in pages.values()) if x})
print('pages', len(pages), 'seeds', len(seeds))
vol = {}
for i in range(0, len(seeds), 5):
    for k in call(seeds[i:i + 5]):
        kw = k.get('relKeyword'); 
        if not kw: continue
        pc, mo = num(k.get('monthlyPcQcCnt')), num(k.get('monthlyMobileQcCnt'))
        vol[kw] = {'pc': pc, 'mo': mo, 'total': pc + mo, 'comp': k.get('compIdx')}
    time.sleep(0.25)
    if i % 200 == 0: print(i, '/', len(seeds), 'keywords', len(vol))
def toks(s): return set(re.findall(r'[가-힣]{2,}|[a-z0-9]{2,}', s.lower()))
ptok = {p: toks(t + ' ' + p) for p, t in pages.items()}
def best_page(kw):
    kt = toks(kw)
    if not kt: return None, 0
    sc = sorted(((len(kt & pt) / len(kt), p) for p, pt in ptok.items()), reverse=True)[:1]
    return (sc[0][1], round(sc[0][0], 2)) if sc and sc[0][0] > 0 else (None, 0)
band = []
for kw, v in vol.items():
    if 2000 <= v['total'] <= 5000:
        p, sc = best_page(kw)
        band.append({'kw': kw, **v, 'page': p, 'match': sc, 'q': bool(re.search(r'방법|얼마|언제|몇|기준|조건|계산법|하는법|뜻|차이|자격|신청|대상|금액|나이', kw))})
band.sort(key=lambda x: -x['total'])
json.dump({'built': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'n_keywords': len(vol), 'band_2000_5000': band,
           'all': vol}, open(os.path.join(out, 'naver_kw.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('keywords', len(vol), 'in 2000~5000', len(band))
