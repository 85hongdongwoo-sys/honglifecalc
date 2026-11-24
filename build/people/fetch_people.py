"""People pages data job: resolves each registry entry (build/people/people.json) to Wikidata and stores the public facts
the pages use → out/people-data/people.json. Runs daily in .github/workflows/people-data.yml (runners can reach Wikidata).
Facts only: birth/death date + precision, birthplace, height, occupations, teams (P54), positions held (P39), awards (P166),
work period start (P2031), companies founded (inverse P112). No images, no private life."""
import json, os, sys, time, urllib.parse, urllib.request

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
REG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'people.json'), encoding='utf-8'))
UA = {'User-Agent': 'honglifecalc.com people pages (data job; contact via honglifecalc.com)', 'Accept': 'application/json'}


def get(url, data=None):
    for a in range(7):
        try:
            req = urllib.request.Request(url, data=data, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            wait = 30 * (a + 1) if '429' in str(e) else 4 * (a + 1)
            print('retry', a, e, 'wait', wait); time.sleep(wait)
    raise SystemExit('unreachable ' + url[:120])


def sparql(q):
    return get('https://query.wikidata.org/sparql?format=json&query=' + urllib.parse.quote(q))['results']['bindings']


def tval(node):
    """(YYYY-MM-DD, precision) from a time value node"""
    if not node: return None
    return node['value'][:10]


API = 'https://www.wikidata.org/w/api.php?format=json&'


def ents(ids, props='labels', langs='es|pt|en'):
    r = {}
    ids = [i for i in dict.fromkeys(ids) if i]
    for k in range(0, len(ids), 50):
        j = get(API + 'action=wbgetentities&props=' + props + '&languages=' + langs + '&ids=' + '|'.join(ids[k:k + 50]))
        r.update(j.get('entities', {}))
        time.sleep(0.5)
    return r


def tv(snak):
    """(YYYY-MM-DD, precision) of a time snak"""
    try:
        v = snak['datavalue']['value']; t = v['time'].lstrip('+')[:10]; pr = v['precision']
        if pr < 11: t = t[:4] if pr <= 9 else t[:7]   # keep the real precision: YYYY or YYYY-MM
        return t, pr
    except Exception:
        return None, 0


def qv(snak):
    try: return snak['datavalue']['value']['id']
    except Exception: return None


def qual(c, prop):
    q = c.get('qualifiers', {}).get(prop)
    return tv(q[0])[0] if q else None


out = []
for p in REG['people']:
    j = get(API + 'action=wbgetentities&props=labels|descriptions|claims|sitelinks&sites=' + p['wiki'] + '&titles='
            + urllib.parse.quote(p['title']) + '&languages=' + p['lang'] + '|en')
    found = [e for e in j.get('entities', {}).values() if 'missing' not in e]
    if not found:
        print('NOT FOUND', p['title']); continue
    e = found[0]; q = e['id']; L = p['lang']; C = e.get('claims', {})
    lab = (e['labels'].get(L) or e['labels'].get('en') or {}).get('value', p['title'])
    desc = (e.get('descriptions', {}).get(L) or {}).get('value', '')
    births = [tv(c['mainsnak']) for c in C.get('P569', []) if c.get('rank') != 'deprecated']
    births = [x for x in births if x[0]]
    if not births or len({x[0] for x in births}) > 1 or births[0][1] < 11:
        print('SKIP unclear birth', lab, births); continue
    death = [tv(c['mainsnak'])[0] for c in C.get('P570', [])]
    cm = None
    for c in C.get('P2048', []):
        try:
            v = c['mainsnak']['datavalue']['value']; amt = float(v['amount']); u = v['unit']
            if u.endswith('/Q11573'): amt *= 100
            if 140 <= amt <= 230: cm = round(amt)
        except Exception: pass
    refs = []
    place = qv(C['P19'][0]['mainsnak']) if C.get('P19') else None; refs.append(place)
    occ = [qv(c['mainsnak']) for c in C.get('P106', [])]; refs += occ
    teams = [(qv(c['mainsnak']), qual(c, 'P580'), qual(c, 'P582')) for c in C.get('P54', [])]
    pos = [(qv(c['mainsnak']), qual(c, 'P580'), qual(c, 'P582')) for c in C.get('P39', [])]
    aw = [(qv(c['mainsnak']), qual(c, 'P585')) for c in C.get('P166', [])]
    refs += [x[0] for x in teams + pos] + [x[0] for x in aw]
    ws = tv(C['P2031'][0]['mainsnak'])[0] if C.get('P2031') else None
    # companies founded: CirrusSearch haswbstatement (no query service)
    sr = get(API + 'action=query&list=search&srnamespace=0&srlimit=20&srsearch=' + urllib.parse.quote('haswbstatement:P112=' + q))
    comp = [x['title'] for x in sr.get('query', {}).get('search', [])]
    ce = ents(comp, 'labels|claims', L + '|en') if comp else {}
    refs = [r for r in refs if r]
    lb = ents(refs, 'labels', L + '|en')
    name = lambda i: ((lb.get(i, {}).get('labels', {}).get(L) or lb.get(i, {}).get('labels', {}).get('en') or {}).get('value')) if i else None
    founded = []
    for cid, ent in ce.items():
        inc = [tv(c['mainsnak'])[0] for c in ent.get('claims', {}).get('P571', [])]
        founded.append({'n': (ent.get('labels', {}).get(L) or ent.get('labels', {}).get('en') or {}).get('value', cid), 'd': inc[0] if inc else None})
    rec = dict(p, qid=q, label=lab, desc=desc, sitelinks=len(e.get('sitelinks', {})), birth=births[0][0],
               death=death[0] if death else None, place=name(place) or '', cm=cm, work_start=ws,
               occ=sorted({name(o) for o in occ if name(o)}),
               teams=[{'n': name(i), 's': s, 'e': en} for i, s, en in teams if name(i)],
               positions=[{'n': name(i), 's': s, 'e': en} for i, s, en in pos if name(i)],
               awards=[{'n': name(i), 'd': d} for i, d in aw if name(i)], founded=founded)
    out.append(rec); print('ok', q, lab, rec['birth'], cm, len(rec['teams']), len(rec['positions']), len(rec['awards']), len(founded))
    time.sleep(4)

os.makedirs(os.path.join(OUT, 'people-data'), exist_ok=True)
json.dump({'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'source': 'Wikidata (CC0)', 'people': out},
          open(os.path.join(OUT, 'people-data', 'people.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
assert out, 'no people'
print('done', len(out))
