"""People pages data job: resolves each registry entry (build/people/people.json) to Wikidata and stores the public facts
the pages use → out/people-data/people.json. Runs daily in .github/workflows/people-data.yml (runners can reach Wikidata).
Facts only: birth/death date + precision, birthplace, height, occupations, teams (P54), positions held (P39), awards (P166),
work period start (P2031), companies founded (inverse P112). No images, no private life."""
import json, os, sys, time, urllib.parse, urllib.request

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
REG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'people.json'), encoding='utf-8'))
UA = {'User-Agent': 'honglifecalc.com people pages (data job; contact via honglifecalc.com)', 'Accept': 'application/json'}


def get(url, data=None):
    for a in range(5):
        try:
            req = urllib.request.Request(url, data=data, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            print('retry', a, e); time.sleep(4 * (a + 1))
    raise SystemExit('unreachable ' + url[:120])


def sparql(q):
    return get('https://query.wikidata.org/sparql?format=json&query=' + urllib.parse.quote(q))['results']['bindings']


def tval(node):
    """(YYYY-MM-DD, precision) from a time value node"""
    if not node: return None
    return node['value'][:10]


out = []
for p in REG['people']:
    j = get('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=info|labels|descriptions|sitelinks&sites='
            + p['wiki'] + '&titles=' + urllib.parse.quote(p['title']) + '&languages=' + p['lang'] + '|en')
    ents = [e for e in j.get('entities', {}).values() if 'missing' not in e]
    if not ents:
        print('NOT FOUND', p['title']); continue
    e = ents[0]; q = e['id']; L = p['lang']
    lab = (e['labels'].get(L) or e['labels'].get('en') or {}).get('value', p['title'])
    desc = (e.get('descriptions', {}).get(L) or {}).get('value', '')
    sl = len(e.get('sitelinks', {}))
    lang = f'"{L},en"'
    base = sparql(f'''SELECT ?b ?bp ?d ?dp ?placeLabel ?h ?hu ?ws WHERE {{
      wd:{q} p:P569/psv:P569 [wikibase:timeValue ?b; wikibase:timePrecision ?bp].
      OPTIONAL{{ wd:{q} p:P570/psv:P570 [wikibase:timeValue ?d; wikibase:timePrecision ?dp] }}
      OPTIONAL{{ wd:{q} wdt:P19 ?place }}
      OPTIONAL{{ wd:{q} p:P2048/psv:P2048 [wikibase:quantityAmount ?h; wikibase:quantityUnit ?hu] }}
      OPTIONAL{{ wd:{q} wdt:P2031 ?ws }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language {lang}. }} }}''')
    if not base:
        print('NO BIRTH', lab); continue
    b0 = base[0]
    births = {x['b']['value'][:10] for x in base}
    if len(births) > 1 or int(b0['bp']['value']) < 11:
        print('SKIP unclear birth', lab, births); continue
    cm = None
    for x in base:
        if 'h' in x:
            v = float(x['h']['value']); u = x['hu']['value']
            if u.endswith('Q11573'): v *= 100
            if u.endswith('Q174728'): pass
            if 140 <= v <= 230: cm = round(v)
    occ = [x['oLabel']['value'] for x in sparql(f'SELECT ?oLabel WHERE {{ wd:{q} wdt:P106 ?o. SERVICE wikibase:label {{ bd:serviceParam wikibase:language {lang}. }} }}')]
    teams = [{'n': x['tLabel']['value'], 's': tval(x.get('s')), 'e': tval(x.get('e'))} for x in sparql(
        f'SELECT ?tLabel ?s ?e WHERE {{ wd:{q} p:P54 ?st. ?st ps:P54 ?t. OPTIONAL{{?st pq:P580 ?s}} OPTIONAL{{?st pq:P582 ?e}} SERVICE wikibase:label {{ bd:serviceParam wikibase:language {lang}. }} }}')]
    pos = [{'n': x['pLabel']['value'], 's': tval(x.get('s')), 'e': tval(x.get('e'))} for x in sparql(
        f'SELECT ?pLabel ?s ?e WHERE {{ wd:{q} p:P39 ?st. ?st ps:P39 ?p. OPTIONAL{{?st pq:P580 ?s}} OPTIONAL{{?st pq:P582 ?e}} SERVICE wikibase:label {{ bd:serviceParam wikibase:language {lang}. }} }}')]
    awards = [{'n': x['aLabel']['value'], 'd': tval(x.get('d'))} for x in sparql(
        f'SELECT ?aLabel ?d WHERE {{ wd:{q} p:P166 ?st. ?st ps:P166 ?a. OPTIONAL{{?st pq:P585 ?d}} SERVICE wikibase:label {{ bd:serviceParam wikibase:language {lang}. }} }}')]
    founded = [{'n': x['cLabel']['value'], 'd': tval(x.get('d'))} for x in sparql(
        f'SELECT ?cLabel ?d WHERE {{ ?c wdt:P112 wd:{q}. OPTIONAL{{?c wdt:P571 ?d}} SERVICE wikibase:label {{ bd:serviceParam wikibase:language {lang}. }} }} LIMIT 20')]
    rec = dict(p, qid=q, label=lab, desc=desc, sitelinks=sl, birth=b0['b']['value'][:10],
               death=(b0['d']['value'][:10] if 'd' in b0 else None), place=b0.get('placeLabel', {}).get('value', ''),
               cm=cm, work_start=tval(b0.get('ws')), occ=sorted(set(occ)), teams=teams, positions=pos, awards=awards, founded=founded)
    out.append(rec); print('ok', q, lab, rec['birth'], cm, len(teams), len(pos), len(awards), len(founded))
    time.sleep(1)

os.makedirs(os.path.join(OUT, 'people-data'), exist_ok=True)
json.dump({'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'source': 'Wikidata (CC0)', 'people': out},
          open(os.path.join(OUT, 'people-data', 'people.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
assert out, 'no people'
print('done', len(out))
