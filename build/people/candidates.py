"""Candidate list for "Famosos en números / Famous people in numbers": the people a country actually reads about most.
Sums Wikimedia's per-country daily top articles over the last 365 days (official pageviews API), keeps living adults
on Wikidata, drops people known for crimes, maps occupations to a category, ranks by views.
Usage: python3 build/people/candidates.py US enwiki en out   → out/people-data/candidates-US.json"""
import datetime as dt, json, os, re, sys, time, urllib.parse, urllib.request

CC, WIKI, LANG, OUT = (sys.argv[1:5] + ['US', 'enwiki', 'en', 'out'][len(sys.argv[1:5]):])
PROJECT = {'enwiki': 'en.wikipedia', 'eswiki': 'es.wikipedia', 'ptwiki': 'pt.wikipedia', 'dewiki': 'de.wikipedia', 'viwiki': 'vi.wikipedia'}[WIKI]
UA = {'User-Agent': 'honglifecalc.com people pages (candidate job)', 'Accept': 'application/json'}


def get(url):
    for a in range(7):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception as e:
            if '404' in str(e): return {}
            w = 30 * (a + 1) if '429' in str(e) else 3 * (a + 1); print('retry', e, w); time.sleep(w)
    return {}


# 1) a year of daily top articles for the country
views = {}
today = dt.date.today()
for k in range(2, 367):
    day = today - dt.timedelta(days=k)
    j = get(f'https://wikimedia.org/api/rest_v1/metrics/pageviews/top-per-country/{CC}/all-access/{day.year}/{day.month:02d}/{day.day:02d}')
    for it in j.get('items', []):
        for a in it.get('articles', []):
            if a.get('project') != PROJECT or ':' in a['article'] or a['article'] in ('Main_Page',): continue
            views[a['article']] = views.get(a['article'], 0) + a.get('views_ceil', 0)
    time.sleep(0.15)
print('articles', len(views))
top = sorted(views.items(), key=lambda x: -x[1])[:9000]

# 2) Wikidata facts for each title (50 per call)
OCC = [  # (category, occupation QIDs) — first match wins, in this order
    ('politico', {'Q82955'}),
    ('futbolista', {'Q937857'}),
    ('atleta', {'Q3665646', 'Q19204627', 'Q10871364', 'Q11774891', 'Q10833314', 'Q13156709', 'Q11303721', 'Q378622', 'Q11607585', 'Q11338576',
                'Q13474373', 'Q11513337', 'Q10843402', 'Q2066131', 'Q13381376', 'Q15117302'}),
    ('cantante', {'Q177220', 'Q639669', 'Q36834', 'Q2252262', 'Q753110', 'Q488205', 'Q130857', 'Q183945', 'Q855091'}),
    ('actor', {'Q33999', 'Q10800557', 'Q10798782', 'Q2405480', 'Q245068', 'Q2526255', 'Q3282637'}),
    ('empresario', {'Q131524', 'Q43845', 'Q484876', 'Q557880'}),
    ('creador', {'Q17125263', 'Q57414145', 'Q947873', 'Q2906862', 'Q1930187'}),
    ('otro', {'Q36180', 'Q901', 'Q1622272', 'Q1028181', 'Q5322166'}),
]
BAD = re.compile(r'murder|killer|criminal|convicted|shooter|assassin|terrorist|victim|kidnap|fraudster|rapist|cult leader|asesin|crimin|homicid', re.I)
out = []
for i in range(0, len(top), 50):
    chunk = top[i:i + 50]
    titles = '|'.join(t.replace('_', ' ') for t, _ in chunk)
    j = get('https://www.wikidata.org/w/api.php?format=json&action=wbgetentities&props=claims|descriptions|sitelinks&languages=en&sitefilter='
            + WIKI + '&sites=' + WIKI + '&titles=' + urllib.parse.quote(titles))
    byt = {}
    for e in j.get('entities', {}).values():
        if 'missing' in e: continue
        sl = e.get('sitelinks', {}).get(WIKI, {}).get('title')
        if sl: byt[sl.replace(' ', '_')] = e
    for t, v in chunk:
        e = byt.get(t)
        if not e: continue
        C = e.get('claims', {})
        ids = lambda p: {c['mainsnak'].get('datavalue', {}).get('value', {}).get('id') for c in C.get(p, [])}
        if 'Q5' not in ids('P31') or C.get('P570') or C.get('P1399'): continue
        desc = e.get('descriptions', {}).get('en', {}).get('value', '')
        if BAD.search(desc): continue
        b = C.get('P569', [{}])[0].get('mainsnak', {}).get('datavalue', {}).get('value', {})
        if not b or b.get('precision', 0) < 11: continue
        by = int(b['time'][1:5])
        if today.year - by < 19: continue  # adults only
        occ = ids('P106'); cat = next((c for c, s in OCC if occ & s), None)
        if cat == 'politico' and not C.get('P39'): cat = next((c for c, s in OCC[1:] if occ & s), None)
        if not cat: continue
        out.append({'wiki': WIKI, 'title': t.replace('_', ' '), 'lang': LANG, 'cat': cat, 'qid': e['id'], 'views': v})
    time.sleep(1)
print('candidates', len(out))
os.makedirs(os.path.join(OUT, 'people-data'), exist_ok=True)
json.dump({'built': today.isoformat(), 'country': CC, 'wiki': WIKI, 'people': out},
          open(os.path.join(OUT, 'people-data', f'candidates-{CC}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
