# USGS 최근 7일 M4.5+ 지진, NOAA 오로라(OVATION)·Kp 예보 → out/geo/
import json, os, sys, urllib.request
OUT = os.path.join(sys.argv[1] if len(sys.argv) > 1 else 'out', 'geo')
os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (honglifecalc.com maps)'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
for name, url in [('quake_week.json', 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson'),
                  ('ovation.json', 'https://services.swpc.noaa.gov/json/ovation_aurora_latest.json'),
                  ('kp_forecast.json', 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json')]:
    try:
        b = get(url); json.loads(b); open(os.path.join(OUT, name), 'wb').write(b); print(name, len(b))
    except Exception as e:
        print('ERR', name, e)
