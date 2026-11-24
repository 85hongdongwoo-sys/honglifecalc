"""Argentina: BCRA Estadísticas API v4 → out/arg-data/bcra.json (UVA, ICL, CER, inflación mensual e interanual, tasa 30 días).
Runs daily in .github/workflows/ar-data.yml. Exits 1 (and publishes nothing) if UVA or ICL can't be read."""
import json, os, sys, time, urllib.request, datetime as dt

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
API = 'https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/'
today = dt.date.today()
S = {  # id: (key, days back)
    31: ('uva', 420), 40: ('icl', 420), 30: ('cer', 420),
    27: ('ipc_m', 365 * 10), 28: ('ipc_a', 400), 12: ('tasa30', 120), 4: ('usd_min', 60),
}


def get(i, desde):
    out, off = [], 0
    while True:
        url = f'{API}{i}?desde={desde}&limit=3000&offset={off}'
        for a in range(4):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'honglifecalc.com data job', 'Accept': 'application/json'})
                j = json.load(urllib.request.urlopen(req, timeout=40))
                break
            except Exception as e:
                print('retry', i, e); time.sleep(5 * (a + 1))
        else:
            raise SystemExit(f'BCRA {i} unreachable')
        d = (j.get('results') or [{}])[0].get('detalle') or []
        out += d
        off += 3000
        if off >= (j.get('metadata', {}).get('resultset', {}).get('count') or 0) or not d:
            break
    return sorted([[x['fecha'], float(x['valor'])] for x in out])


data = {'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'source': 'BCRA API de Estadísticas v4'}
for i, (k, back) in S.items():
    try:
        data[k] = get(i, (today - dt.timedelta(days=back)).isoformat())
        print(k, len(data[k]), data[k][-1] if data[k] else None)
    except SystemExit as e:
        if k in ('uva', 'icl'):
            raise
        print('skip', k, e); data[k] = []
assert data['uva'] and data['icl'], 'empty UVA/ICL'
os.makedirs(os.path.join(OUT, 'arg-data'), exist_ok=True)
json.dump(data, open(os.path.join(OUT, 'arg-data', 'bcra.json'), 'w'), separators=(',', ':'))
print('ok')
