# 나라별 정부 공식 전기차 충전소 자료를 받아 0.5도 격자 타일 JSON으로 만든다 → out/ev/<cc>/
#  de: Bundesnetzagentur Ladesäulenregister (CC BY 4.0)
#  fr: data.gouv.fr Base nationale des IRVE (Licence Ouverte 2.0)
# 사용: python3 build/ev/fetch_ev.py out de fr
import csv, io, json, math, os, re, sys, time, urllib.request, collections

UA = {'User-Agent': 'Mozilla/5.0 (honglifecalc.com EV charger map)'}
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
WHICH = sys.argv[2:] or ['de', 'fr']
# plug bits: 1 Type2(AC) 2 CCS 4 CHAdeMO 8 Schuko/E-F/domestic 16 Tesla/NACS 32 Type1/J1772


def get(u):
    for i in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=600).read()
        except Exception as e:
            print('retry', u, e); time.sleep(10)
    raise SystemExit('download failed ' + u)


def fnum(s):
    try:
        return float(str(s).strip().replace(',', '.'))
    except Exception:
        return None


def write(cc, stations, meta):
    ops = collections.Counter(s['op'] for s in stations)
    oplist = [o for o, _ in ops.most_common()]
    oi = {o: i for i, o in enumerate(oplist)}
    tiles = collections.defaultdict(list)
    for s in stations:
        k = f'{math.floor(s["lat"] * 2)}_{math.floor(s["lon"] * 2)}'
        tiles[k].append([round(s['lat'], 5), round(s['lon'], 5), s['kw'], s['n'], oi[s['op']], s['addr'], s['plug'], s.get('tel', ''), s.get('pay', '')])
    d = os.path.join(OUT, 'ev', cc, 't')
    os.makedirs(d, exist_ok=True)
    for k, v in tiles.items():
        json.dump(v, open(os.path.join(d, k + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    meta.update({'stations': len(stations), 'points': sum(s['n'] for s in stations), 'fast': sum(1 for s in stations if s['kw'] >= 50),
                 'tiles': sorted(tiles), 'ops': oplist, 'built': time.strftime('%Y-%m-%d')})
    json.dump(meta, open(os.path.join(OUT, 'ev', cc, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(cc, 'stations', len(stations), 'tiles', len(tiles))


def de():
    page = get('https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/DownloadundKontakt.html').decode('utf-8', 'replace')
    url = [u for u in re.findall(r'href="([^"]*Ladesaeulenregister[^"]*\.csv[^"]*)"', page)][0]
    if not url.startswith('http'):
        url = 'https://www.bundesnetzagentur.de/' + url.lstrip('/')
    raw = get(url)
    try:
        txt = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        txt = raw.decode('cp1252')
    stand = re.search(r'Letzte Aktualisierung vom:\s*([\d.]+)', txt)
    lines = txt.splitlines()
    hi = next(i for i, l in enumerate(lines) if l.startswith('Ladeeinrichtungs-ID'))
    rd = csv.DictReader(io.StringIO('\n'.join(lines[hi:])), delimiter=';')
    res = []
    for r in rd:
        if (r.get('Status') or '').strip() not in ('In Betrieb', ''):
            continue
        lat, lon = fnum(r.get('Breitengrad')), fnum(r.get('Längengrad'))
        if not lat or not lon or not (47 <= lat <= 55.2 and 5.5 <= lon <= 15.5):
            continue
        plugs = ' '.join(r.get(f'Steckertypen{i}', '') or '' for i in range(1, 7))
        bits = (1 if 'Typ 2' in plugs else 0) | (2 if 'CCS' in plugs or 'Combo' in plugs else 0) | (4 if 'CHAdeMO' in plugs else 0) | (8 if 'Schuko' in plugs or 'CEE' in plugs else 0) | (16 if 'Tesla' in plugs else 0)
        kw = fnum(r.get('Nennleistung Ladeeinrichtung [kW]')) or 0
        addr = ' '.join(x for x in [(r.get('Straße') or '').strip(), (r.get('Hausnummer') or '').strip()] if x)
        addr = f'{addr}, {(r.get("Postleitzahl") or "").strip()} {(r.get("Ort") or "").strip()}'.strip(', ')
        res.append({'lat': lat, 'lon': lon, 'kw': round(kw), 'n': int(fnum(r.get('Anzahl Ladepunkte')) or 1), 'op': (r.get('Betreiber') or '').strip()[:60],
                    'addr': addr[:90], 'plug': bits, 'pay': (r.get('Bezahlsysteme') or '').replace(';', ', ')[:80]})
    write('de', res, {'src': 'Bundesnetzagentur – Ladesäulenregister', 'src_url': 'https://www.bundesnetzagentur.de/ladesaeulenkarte',
                      'license': 'CC BY 4.0', 'stand': stand.group(1) if stand else ''})


def fr():
    d = json.loads(get('https://www.data.gouv.fr/api/1/datasets/base-nationale-des-irve-infrastructures-de-recharge-pour-vehicules-electriques/'))
    res_ = [r for r in d['resources'] if (r.get('format') or '').lower() == 'csv' and 'onsolidation' in (r.get('title') or '') and 'ocumentation' not in (r.get('title') or '')]
    url = res_[0]['url']
    stand = re.search(r'(\d{8})', url)
    txt = get(url).decode('utf-8-sig', 'replace')
    rd = csv.DictReader(io.StringIO(txt))
    st = {}
    for r in rd:
        sid = (r.get('id_station_itinerance') or r.get('id_station_local') or '').strip() or (r.get('coordonneesXY') or '')
        lat, lon = fnum(r.get('consolidated_latitude')), fnum(r.get('consolidated_longitude'))
        if lat is None or lon is None:
            m = re.findall(r'-?\d+\.\d+', r.get('coordonneesXY') or '')
            if len(m) >= 2:
                lon, lat = float(m[0]), float(m[1])
        if lat is None or lon is None or not (41 <= lat <= 51.5 and -5.5 <= lon <= 10):
            continue  # 본토·코르시카만
        kw = fnum(r.get('puissance_nominale')) or 0
        if kw > 1000:
            kw = kw / 1000  # 일부 W 단위 입력
        yes = lambda k: (r.get(k) or '').strip().lower() in ('true', '1', 'vrai', 'oui')
        bits = (1 if yes('prise_type_2') else 0) | (2 if yes('prise_type_combo_ccs') else 0) | (4 if yes('prise_type_chademo') else 0) | (8 if yes('prise_type_ef') else 0)
        s = st.get(sid)
        if not s:
            op = (r.get('nom_operateur') or r.get('nom_enseigne') or '').strip()[:60]
            s = st[sid] = {'lat': lat, 'lon': lon, 'kw': 0, 'n': 0, 'op': op, 'addr': (r.get('adresse_station') or '').strip()[:90], 'plug': 0,
                           'tel': (r.get('telephone_operateur') or '').strip()[:20],
                           'pay': ('gratuit' if yes('gratuit') else (r.get('tarification') or '').strip()[:80])}
        s['n'] += 1
        s['kw'] = max(s['kw'], round(kw))
        s['plug'] |= bits
    write('fr', list(st.values()), {'src': 'data.gouv.fr – Base nationale des IRVE', 'src_url': 'https://www.data.gouv.fr/fr/datasets/base-nationale-des-irve-infrastructures-de-recharge-pour-vehicules-electriques/',
                                     'license': 'Licence Ouverte 2.0', 'stand': stand.group(1) if stand else ''})


for cc in WHICH:
    try:
        globals()[cc]()
    except SystemExit:
        raise
    except Exception as e:
        print('ERR', cc, e)
