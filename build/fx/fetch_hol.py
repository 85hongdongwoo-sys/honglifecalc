# 나라별 공휴일 (Nager.Date 공개 API, 올해·내년) → out/hol/<CC>-<YEAR>.json
import json, os, sys, time, urllib.request
OUT = os.path.join(sys.argv[1] if len(sys.argv) > 1 else 'out', 'hol')
os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (honglifecalc.com holiday calendar)'}
def get(u): return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read())
CC = ['US', 'GB', 'CA', 'AU', 'IE', 'NZ', 'ZA', 'SG', 'PH', 'DE', 'AT', 'CH', 'FR', 'BE', 'ES', 'MX', 'IT', 'NL', 'BR', 'PL', 'SE', 'NO', 'DK',
      'TR', 'ID', 'JP', 'CN', 'HK', 'CL', 'CO', 'AR', 'NG', 'EG', 'PT', 'IN', 'MY', 'VN', 'RU']
avail = {c['countryCode'] for c in get('https://date.nager.at/api/v3/AvailableCountries')}
y = int(time.strftime('%Y'))
done = []
for cc in CC:
    if cc not in avail:
        continue
    for yr in (y, y + 1):
        try:
            d = get(f'https://date.nager.at/api/v3/PublicHolidays/{yr}/{cc}')
            if d:
                json.dump(d, open(os.path.join(OUT, f'{cc}-{yr}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
                done.append(f'{cc}-{yr}')
        except Exception as e:
            print('ERR', cc, yr, e)
        time.sleep(0.3)
print('holidays:', len(done), ' '.join(done))
