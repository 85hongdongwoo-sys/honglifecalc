"""Energi Data Service (Energinet, CC BY 4.0) – DayAheadPrices (kvarter) → out/el/eds.json
Bruges af /dk/hvornaar-er-stroemmen-billigst.html (hentes fra data-el-grenen via raw.githubusercontent.com)."""
import json, os, sys, time, urllib.request, urllib.parse
out = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(os.path.join(out, 'el'), exist_ok=True)
AREAS = ['DK1', 'DK2', 'NO2', 'SE3', 'SE4']
q = urllib.parse.urlencode({'start': 'now-P8D', 'end': 'now+P2D', 'limit': 20000, 'sort': 'TimeUTC asc',
                            'filter': json.dumps({'PriceArea': AREAS})})
url = 'https://api.energidataservice.dk/dataset/DayAheadPrices?' + q
for i in range(4):
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'honglifecalc.com data job'}), timeout=60))
        break
    except Exception as e:
        print('retry', e); time.sleep(20)
else:
    sys.exit('fetch failed')
res = {a: [] for a in AREAS}
for r in d['records']:
    if r.get('DayAheadPriceDKK') is None:
        continue
    t = r['TimeUTC']  # 'YYYY-MM-DDTHH:MM:SS' UTC
    import calendar
    ts = calendar.timegm(time.strptime(t, '%Y-%m-%dT%H:%M:%S')) * 1000
    res[r['PriceArea']].append([ts, round(r['DayAheadPriceDKK'] / 10, 3), round(r['DayAheadPriceEUR'] / 10, 3)])
n = sum(len(v) for v in res.values())
if n < 500:
    sys.exit(f'too few records: {n}')
json.dump({'updated': int(time.time() * 1000), 'unit': 'oere/kWh (DKK) and cent/kWh (EUR), excl. VAT',
           'source': 'Energi Data Service, Energinet (CC BY 4.0) – DayAheadPrices', 'areas': res},
          open(os.path.join(out, 'el', 'eds.json'), 'w'), separators=(',', ':'))
print({a: len(v) for a, v in res.items()})
