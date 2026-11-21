import re, json, urllib.request, io, csv
UA={'User-Agent':'Mozilla/5.0 (honglifecalc.com EV map)'}
def get(u, n=None):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120)
    return r.read(n) if n else r.read()
# DE
h=get('https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/DownloadundKontakt.html').decode('utf-8','replace')
links=sorted(set(re.findall(r'href="([^"]*Ladesaeulenregister[^"]*)"',h)))
print('DE links',links)
csvl=[l for l in links if 'csv' in l.lower()]
if csvl:
    u=csvl[0] if csvl[0].startswith('http') else 'https://www.bundesnetzagentur.de/'+csvl[0].lstrip('/')
    b=get(u, 6000)
    for enc in ('utf-8','cp1252'):
        try: print(b.decode(enc)[:3000]); break
        except Exception: pass
# FR
for api in ['https://transport.data.gouv.fr/api/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques',
            'https://www.data.gouv.fr/api/1/datasets/base-nationale-des-irve-infrastructures-de-recharge-pour-vehicules-electriques/']:
    try:
        d=json.loads(get(api))
        res=d.get('resources',[])
        print('FR',api,len(res))
        for r in res[:12]: print('  ',r.get('title'),r.get('format'),r.get('url') or r.get('original_url'),r.get('filesize'))
    except Exception as e: print('FR ERR',api,e)
