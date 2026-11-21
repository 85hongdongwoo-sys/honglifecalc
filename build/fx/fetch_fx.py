# 유럽중앙은행(ECB) 공식 기준환율 → out/fx/latest.json, out/fx/hist.json (최근 90일)
import json, os, re, sys, urllib.request
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
UA = {'User-Agent': 'Mozilla/5.0 (honglifecalc.com currency converter)'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode('utf-8')
def parse(x):
    days = []
    for d, body in re.findall(r"<Cube time=['\"](\d{4}-\d\d-\d\d)['\"]>(.*?)</Cube>\s*(?=<Cube time|</Cube>)", x, re.S):
        r = {c: float(v) for c, v in re.findall(r"currency=['\"]([A-Z]{3})['\"]\s+rate=['\"]([\d.]+)['\"]", body)}
        r['EUR'] = 1.0
        days.append((d, r))
    return sorted(days)
hist = parse(get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml'))
daily = parse(get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'))
if daily and (not hist or daily[-1][0] > hist[-1][0]): hist.append(daily[-1])
d, r = hist[-1]
os.makedirs(os.path.join(OUT, 'fx'), exist_ok=True)
json.dump({'date': d, 'base': 'EUR', 'rates': r, 'src': 'European Central Bank – euro foreign exchange reference rates',
           'src_url': 'https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html'},
          open(os.path.join(OUT, 'fx', 'latest.json'), 'w'), separators=(',', ':'))
curs = sorted(r)
json.dump({'dates': [x[0] for x in hist], 'rates': {c: [x[1].get(c) for x in hist] for c in curs}},
          open(os.path.join(OUT, 'fx', 'hist.json'), 'w'), separators=(',', ':'))
print('fx', d, len(r), 'currencies,', len(hist), 'days')
