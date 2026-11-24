"""MIMIT Osservaprezzi carburanti (IODL 2.0) → out/it/carburanti.json
Prezzi praticati alle ore 8 del giorno + anagrafica impianti attivi. Per provincia: media/min self e servito per carburante,
e i 15 impianti più economici (self) per carburante principale."""
import csv, io, json, os, sys, time, urllib.request, statistics
out = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(os.path.join(out, 'it'), exist_ok=True)
U = 'https://www.mimit.gov.it/images/exportCSV/'
def get(name):
    for i in range(4):
        try:
            b = urllib.request.urlopen(urllib.request.Request(U + name, headers={'User-Agent': 'Mozilla/5.0 honglifecalc data job'}), timeout=120).read()
            return b.decode('utf-8', 'replace')
        except Exception as e:
            print('retry', name, e); time.sleep(20)
    sys.exit('fetch failed ' + name)
def rows(txt):
    lines = txt.splitlines()
    head = 0
    while head < len(lines) and not lines[head].lower().startswith('idimpianto'):
        head += 1
    first = lines[0] if lines else ''
    body = lines[head:]
    sep = '|' if body and body[0].count('|') > body[0].count(';') else ';'
    return first, list(csv.DictReader(io.StringIO('\n'.join(body)), delimiter=sep))
f1, prezzi = rows(get('prezzo_alle_8.csv'))
f2, anag = rows(get('anagrafica_impianti_attivi.csv'))
print(f1, len(prezzi), f2, len(anag)); print(list(prezzi[0].keys()), list(anag[0].keys()))
def k(d, *names):
    for n in names:
        for kk in d:
            if kk.strip().lower() == n.lower():
                return d[kk]
    return ''
A = {}
for a in anag:
    try:
        A[k(a, 'idImpianto')] = dict(n=k(a, 'Nome Impianto').strip(), b=k(a, 'Bandiera').strip(), ad=k(a, 'Indirizzo').strip(),
                                    c=k(a, 'Comune').strip().title(), p=k(a, 'Provincia').strip().upper(),
                                    lat=round(float(k(a, 'Latitudine')), 5), lon=round(float(k(a, 'Longitudine')), 5))
    except Exception:
        pass
FUEL = {'benzina': 'Benzina', 'gasolio': 'Gasolio', 'gpl': 'GPL', 'metano': 'Metano'}
def fuel_key(desc):
    d = desc.strip().lower()
    for key, name in FUEL.items():
        if d == name.lower():
            return key
    return None
by = {}
for r in prezzi:
    fk = fuel_key(k(r, 'descCarburante'))
    st = A.get(k(r, 'idImpianto'))
    if not fk or not st or not st['p']:
        continue
    try:
        pr = float(k(r, 'prezzo').replace(',', '.'))
    except ValueError:
        continue
    lim = (0.3, 4.0) if fk != 'metano' else (0.5, 5.0)
    if not lim[0] < pr < lim[1]:
        continue
    self_ = k(r, 'isSelf').strip() in ('1', 'true', 'True')
    by.setdefault(st['p'], {}).setdefault(fk, {'s': [], 'v': []})['s' if self_ else 'v'].append((pr, k(r, 'idImpianto')))
prov = {}
for p, fu in by.items():
    prov[p] = {}
    for fk, d in fu.items():
        e = {}
        for kind in ('s', 'v'):
            v = [x[0] for x in d[kind]]
            if v:
                e[kind] = [round(statistics.mean(v), 3), round(min(v), 3), len(v)]
        cheap = sorted(d['s'])[:15]
        e['top'] = [[x[0]] + [A[x[1]][q] for q in ('n', 'b', 'ad', 'c', 'lat', 'lon')] for x in cheap]
        prov[p][fk] = e
nat = {}
for fk in FUEL:
    v = [x[0] for p in by.values() for x in p.get(fk, {'s': []})['s']]
    if v:
        nat[fk] = [round(statistics.mean(v), 3), round(min(v), 3), len(v)]
if len(prov) < 90:
    sys.exit(f'too few provinces: {len(prov)}')
json.dump({'updated': int(time.time() * 1000), 'estrazione': f1.strip(), 'source': 'MIMIT – Osservaprezzi carburanti (IODL 2.0)',
           'nat': nat, 'prov': prov}, open(os.path.join(out, 'it', 'carburanti.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('provinces', len(prov), 'nat', nat, 'bytes', os.path.getsize(os.path.join(out, 'it', 'carburanti.json')))
