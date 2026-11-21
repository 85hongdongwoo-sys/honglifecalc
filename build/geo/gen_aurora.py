# 나라별 오로라 예보 지도 (NOAA SWPC OVATION + Kp 3일 예보) — 배포 때 Kp 예보 표를 본문에 넣는다.
# 사용: python3 build/geo/gen_aurora.py _site
import json, os, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pagekit import B, E, build_page, faq_ld, app_ld, faq_html, register

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
G = os.path.join(SITE, 'geo')
OV = json.load(open(os.path.join(G, 'ovation.json')))
KP = json.load(open(os.path.join(G, 'kp_forecast.json')))
# Kp 예보: [[time_tag, kp, observed|estimated|predicted, scale], ...] (첫 줄 머리글)
if KP and isinstance(KP[0], dict):
    rows = [[r.get('time_tag', ''), r.get('kp'), r.get('observed', ''), r.get('noaa_scale')] for r in KP if r.get('kp') is not None]
else:
    rows = [r for r in KP[1:] if r and r[1] not in (None, '')] if KP and isinstance(KP[0], list) and KP[0][0] == 'time_tag' else []
rows = [[r[0], round(float(r[1]), 2), r[2], r[3]] for r in rows]
_now = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
kp_now = next((r for r in reversed(rows) if r[2] in ('observed', 'estimated') and r[0] <= _now), None)
days = collections.OrderedDict()
for r in rows:
    if r[2] == 'predicted':
        d = r[0][:10]
        days[d] = max(days.get(d, 0), float(r[1]))
DAYS = list(days.items())[:3]
OBS = OV.get('Observation Time', '')[:16].replace('T', ' ')
FC = OV.get('Forecast Time', '')[:16].replace('T', ' ')
# 지도용: 확률 3 이상 칸만 (경도, 위도, 값)
GRID = [[c[0], c[1], c[2]] for c in OV.get('coordinates', []) if c[2] >= 3]
def _bk(v): return 3 if v >= 50 else 2 if v >= 30 else 1 if v >= 10 else 0
RUNS, _by = [], collections.defaultdict(list)
for lo, la, v in GRID:
    _by[la].append((lo if lo <= 180 else lo - 360, v))
for la, cs in _by.items():
    cs.sort(); cur = None
    for lo, v in cs:
        b = _bk(v)
        if cur and cur[3] == b and lo == cur[2] + 1:
            cur[2] = lo
        else:
            if cur: RUNS.append(cur)
            cur = [la, lo, lo, b]
    if cur: RUNS.append(cur)
json.dump({'obs': OBS, 'fc': FC, 'g': GRID, 'r': RUNS}, open(os.path.join(G, 'aurora_grid.json'), 'w'), separators=(',', ':'))

C = {
 'us': ('en', 'N', [52, -105], 3, 'the United States'), 'ca': ('en', 'N', [58, -100], 3, 'Canada'), 'uk': ('en', 'N', [60, -3], 3, 'the UK'),
 'ie': ('en', 'N', [60, -8], 3, 'Ireland'), 'en': ('en', 'N', [62, 10], 2, 'the world'), 'nz': ('en', 'S', [-55, 170], 3, 'New Zealand'),
 'au': ('en', 'S', [-52, 145], 3, 'Australia'), 'no': ('nb', 'N', [68, 15], 3, 'Norge'), 'se': ('sv', 'N', [66, 17], 3, 'Sverige'),
 'dk': ('da', 'N', [62, 10], 3, 'Danmark'), 'de': ('de', 'N', [60, 10], 3, 'Deutschland'), 'pl': ('pl', 'N', [60, 19], 3, 'Polska'),
}
T = {
 'en': dict(slug='aurora-forecast.html',
            title='{A} Forecast Tonight – Aurora Map & Kp Index for {n}',
            desc='Will you see the {a} tonight? Live NOAA aurora map, the chance at your location, the Kp index forecast for the next 3 days and when it gets dark enough where you are.',
            h1='<b>{A}</b> forecast', sub='NOAA aurora map, chance at your location, Kp forecast and darkness – in one place.',
            loc='📍 Check my location', chance='Aurora chance overhead', near='Best within 500 km', dark='Dark enough now?', yes='Yes – it is dark', no='Not yet – too bright', darkFrom='Dark (sun below −12°) from {t1} to {t2}',
            noDark='No proper darkness in the next 24 hours here.', kpNow='Kp now', kpT='Kp index forecast (next 3 days)', kpMax='Max Kp', kpCols=['Day (UTC)', 'Max Kp', 'Outlook'],
            out={0: 'Quiet', 4: 'Active', 5: 'Storm (G1)', 6: 'Strong storm (G2)', 7: 'Severe storm (G3+)'},
            verdict={0: 'Low', 10: 'Possible', 30: 'Good', 50: 'Very good'},
            mapNote='Green to red = probability of aurora overhead from the NOAA OVATION model ({o}, forecast for {f} UTC). From farther away you may still see it low on the horizon.',
            src='Data: NOAA Space Weather Prediction Center (public domain).', kpTxt='Current Kp: {k} ({t} UTC).',
            faq=[('What Kp index do I need to see the {a}?', 'In far-north or far-south places a Kp of 2–3 can be enough. Mid-latitudes usually need Kp 5 or more (a geomagnetic storm), and Kp 7 or more for places much closer to the equator. Clear, dark skies matter just as much.'),
                 ('When is the best time to look?', 'When it is fully dark – usually between about 22:00 and 02:00 local time – away from city lights, looking toward the pole ({dir}). Check this page for the darkness window at your location.'),
                 ('Where does the forecast come from?', 'From the U.S. NOAA Space Weather Prediction Center: the OVATION model (about 30–90 minutes ahead) and the 3-day planetary Kp forecast. Your location is only used in your browser.')]),
 'nb': dict(slug='nordlys-varsel.html', title='Nordlysvarsel i kveld – nordlyskart og Kp-indeks for {n}',
            desc='Kan du se nordlyset i kveld? Live nordlyskart fra NOAA, sjansen der du er, Kp-varsel for de neste 3 dagene og når det blir mørkt nok.',
            h1='<b>Nordlys</b>varsel', sub='NOAA-nordlyskart, sjansen der du er, Kp-varsel og mørketid – samlet.',
            loc='📍 Sjekk min posisjon', chance='Sjanse for nordlys rett over deg', near='Beste innen 500 km', dark='Mørkt nok nå?', yes='Ja – det er mørkt', no='Ikke ennå – for lyst', darkFrom='Mørkt (sola under −12°) fra {t1} til {t2}',
            noDark='Ikke ordentlig mørkt de neste 24 timene her.', kpNow='Kp nå', kpT='Kp-varsel (neste 3 dager)', kpMax='Høyeste Kp', kpCols=['Dag (UTC)', 'Høyeste Kp', 'Utsikter'],
            out={0: 'Rolig', 4: 'Aktivt', 5: 'Storm (G1)', 6: 'Kraftig storm (G2)', 7: 'Svært kraftig storm (G3+)'},
            verdict={0: 'Lav', 10: 'Mulig', 30: 'God', 50: 'Svært god'},
            mapNote='Grønt til rødt = sannsynlighet for nordlys rett over deg fra NOAAs OVATION-modell ({o}, varsel for {f} UTC). Lenger unna kan du fortsatt se det lavt i nord.',
            src='Data: NOAA Space Weather Prediction Center.', kpTxt='Kp nå: {k} ({t} UTC).',
            faq=[('Hvilken Kp trenger jeg for å se nordlys?', 'I Nord-Norge holder ofte Kp 1–3. Sør i landet trengs gjerne Kp 4–5 eller mer. Klar og mørk himmel er like viktig.'),
                 ('Når er det best å se?', 'Når det er helt mørkt, ofte mellom kl. 22 og 02, langt fra bylys, med blikket mot nord. Se mørketiden for din posisjon på denne siden.'),
                 ('Hvor kommer varselet fra?', 'Fra NOAA Space Weather Prediction Center i USA: OVATION-modellen (30–90 minutter fram) og Kp-varselet for 3 dager. Posisjonen din brukes bare i nettleseren.')]),
 'sv': dict(slug='norrsken-prognos.html', title='Norrsken prognos i kväll – norrskenskarta och Kp-index för {n}',
            desc='Kan du se norrsken i kväll? Live norrskenskarta från NOAA, chansen där du är, Kp-prognos för tre dagar och när det blir tillräckligt mörkt.',
            h1='<b>Norrsken</b>sprognos', sub='NOAA-karta, chansen där du är, Kp-prognos och mörker – samlat.',
            loc='📍 Kolla min plats', chance='Chans för norrsken rakt ovanför', near='Bäst inom 500 km', dark='Mörkt nog nu?', yes='Ja – det är mörkt', no='Inte än – för ljust', darkFrom='Mörkt (solen under −12°) från {t1} till {t2}',
            noDark='Inget riktigt mörker de närmaste 24 timmarna här.', kpNow='Kp nu', kpT='Kp-prognos (tre dagar)', kpMax='Högsta Kp', kpCols=['Dag (UTC)', 'Högsta Kp', 'Utsikt'],
            out={0: 'Lugnt', 4: 'Aktivt', 5: 'Storm (G1)', 6: 'Kraftig storm (G2)', 7: 'Mycket kraftig storm (G3+)'},
            verdict={0: 'Låg', 10: 'Möjlig', 30: 'Bra', 50: 'Mycket bra'},
            mapNote='Grönt till rött = sannolikhet för norrsken rakt ovanför enligt NOAA:s OVATION-modell ({o}, prognos för {f} UTC). Längre bort kan det synas lågt i norr.',
            src='Data: NOAA Space Weather Prediction Center.', kpTxt='Kp nu: {k} ({t} UTC).',
            faq=[('Vilket Kp behövs för norrsken?', 'I Norrland räcker ofta Kp 2–3. I södra Sverige behövs vanligen Kp 5 eller mer. Klar och mörk himmel är lika viktigt.'),
                 ('När är det bäst att titta?', 'När det är helt mörkt, ofta mellan kl. 22 och 02, långt från stadsljus, mot norr. Se mörkerfönstret för din plats här.'),
                 ('Var kommer prognosen ifrån?', 'Från NOAA Space Weather Prediction Center i USA: OVATION-modellen (30–90 minuter framåt) och Kp-prognosen för tre dagar. Din plats används bara i webbläsaren.')]),
 'da': dict(slug='nordlys-prognose.html', title='Nordlys i aften – nordlyskort og Kp-indeks for {n}',
            desc='Kan du se nordlys i aften? Live nordlyskort fra NOAA, chancen hvor du er, Kp-prognose for tre dage og hvornår det bliver mørkt nok.',
            h1='<b>Nordlys</b>prognose', sub='NOAA-kort, chancen hvor du er, Kp-prognose og mørke – samlet.',
            loc='📍 Tjek min placering', chance='Chance for nordlys lige over dig', near='Bedst inden for 500 km', dark='Mørkt nok nu?', yes='Ja – det er mørkt', no='Ikke endnu – for lyst', darkFrom='Mørkt (solen under −12°) fra {t1} til {t2}',
            noDark='Intet rigtigt mørke de næste 24 timer her.', kpNow='Kp nu', kpT='Kp-prognose (tre dage)', kpMax='Højeste Kp', kpCols=['Dag (UTC)', 'Højeste Kp', 'Udsigt'],
            out={0: 'Roligt', 4: 'Aktivt', 5: 'Storm (G1)', 6: 'Kraftig storm (G2)', 7: 'Meget kraftig storm (G3+)'},
            verdict={0: 'Lav', 10: 'Mulig', 30: 'God', 50: 'Meget god'},
            mapNote='Grøn til rød = sandsynlighed for nordlys lige over dig ifølge NOAA’s OVATION-model ({o}, prognose for {f} UTC). Længere væk kan det stadig ses lavt mod nord.',
            src='Data: NOAA Space Weather Prediction Center.', kpTxt='Kp nu: {k} ({t} UTC).',
            faq=[('Hvilket Kp skal der til for nordlys i Danmark?', 'I Danmark kræver det som regel Kp 5 eller mere (en geomagnetisk storm), og en mørk, skyfri himmel med frit udsyn mod nord.'),
                 ('Hvornår er det bedst at kigge?', 'Når det er helt mørkt, ofte mellem kl. 22 og 02, væk fra bylys, mod nord. Se mørketiden for din placering her.'),
                 ('Hvor kommer prognosen fra?', 'Fra NOAA Space Weather Prediction Center i USA: OVATION-modellen (30–90 minutter frem) og Kp-prognosen for tre dage. Din placering bruges kun i browseren.')]),
 'de': dict(slug='polarlichter-vorhersage.html', title='Polarlichter heute – Vorhersage, Polarlicht-Karte und Kp-Index für {n}',
            desc='Polarlichter heute Nacht sichtbar? Live-Polarlichtkarte der NOAA, Chance an Ihrem Standort, Kp-Vorhersage für 3 Tage und wann es dunkel genug ist.',
            h1='<b>Polarlicht</b>-Vorhersage', sub='NOAA-Karte, Chance an Ihrem Standort, Kp-Vorhersage und Dunkelheit – auf einen Blick.',
            loc='📍 Meinen Standort prüfen', chance='Chance auf Polarlicht direkt über Ihnen', near='Beste Chance im Umkreis von 500 km', dark='Jetzt dunkel genug?', yes='Ja – es ist dunkel', no='Noch nicht – zu hell', darkFrom='Dunkel (Sonne unter −12°) von {t1} bis {t2}',
            noDark='In den nächsten 24 Stunden wird es hier nicht richtig dunkel.', kpNow='Kp aktuell', kpT='Kp-Vorhersage (3 Tage)', kpMax='Max. Kp', kpCols=['Tag (UTC)', 'Max. Kp', 'Aussicht'],
            out={0: 'Ruhig', 4: 'Aktiv', 5: 'Sturm (G1)', 6: 'Starker Sturm (G2)', 7: 'Schwerer Sturm (G3+)'},
            verdict={0: 'Gering', 10: 'Möglich', 30: 'Gut', 50: 'Sehr gut'},
            mapNote='Grün bis Rot = Wahrscheinlichkeit für Polarlicht direkt über Ihnen nach dem OVATION-Modell der NOAA ({o}, Vorhersage für {f} UTC). Aus größerer Entfernung ist es oft noch tief am Nordhorizont sichtbar.',
            src='Daten: NOAA Space Weather Prediction Center.', kpTxt='Kp aktuell: {k} ({t} UTC).',
            faq=[('Welcher Kp-Wert ist für Polarlichter in Deutschland nötig?', 'In Norddeutschland meist ab Kp 6, im Süden eher ab Kp 7 (starker geomagnetischer Sturm). Dazu braucht es einen dunklen, wolkenlosen Himmel mit freier Sicht nach Norden.'),
                 ('Wann sieht man Polarlichter am besten?', 'Wenn es ganz dunkel ist, meist zwischen 22 und 2 Uhr, fern von Stadtlicht, mit Blick nach Norden. Das Dunkelfenster für Ihren Standort steht auf dieser Seite.'),
                 ('Woher stammt die Vorhersage?', 'Vom NOAA Space Weather Prediction Center (USA): OVATION-Modell (30–90 Minuten im Voraus) und die 3-Tage-Kp-Vorhersage. Ihr Standort wird nur im Browser verwendet.')]),
 'pl': dict(slug='zorza-polarna-prognoza.html', title='Zorza polarna dziś – prognoza, mapa zorzy i indeks Kp dla Polski',
            desc='Czy zobaczysz dziś zorzę polarną? Mapa zorzy NOAA na żywo, szansa w Twojej lokalizacji, prognoza Kp na 3 dni i kiedy będzie wystarczająco ciemno.',
            h1='<b>Zorza polarna</b> – prognoza', sub='Mapa NOAA, szansa w Twojej lokalizacji, prognoza Kp i ciemność – w jednym miejscu.',
            loc='📍 Sprawdź moją lokalizację', chance='Szansa na zorzę nad Tobą', near='Najlepiej w promieniu 500 km', dark='Czy jest już ciemno?', yes='Tak – jest ciemno', no='Jeszcze nie – za jasno', darkFrom='Ciemno (słońce poniżej −12°) od {t1} do {t2}',
            noDark='W ciągu 24 godzin nie będzie tu prawdziwej ciemności.', kpNow='Kp teraz', kpT='Prognoza Kp (3 dni)', kpMax='Maks. Kp', kpCols=['Dzień (UTC)', 'Maks. Kp', 'Perspektywa'],
            out={0: 'Spokojnie', 4: 'Aktywnie', 5: 'Burza (G1)', 6: 'Silna burza (G2)', 7: 'Bardzo silna burza (G3+)'},
            verdict={0: 'Niska', 10: 'Możliwa', 30: 'Dobra', 50: 'Bardzo dobra'},
            mapNote='Od zielonego do czerwonego = prawdopodobieństwo zorzy nad głową wg modelu OVATION NOAA ({o}, prognoza na {f} UTC). Z większej odległości bywa widoczna nisko nad północnym horyzontem.',
            src='Dane: NOAA Space Weather Prediction Center.', kpTxt='Kp teraz: {k} ({t} UTC).',
            faq=[('Jaki Kp jest potrzebny, by zobaczyć zorzę w Polsce?', 'Na północy Polski zwykle od Kp 6, na południu raczej od Kp 7 (silna burza geomagnetyczna). Potrzebne jest też ciemne, bezchmurne niebo z widokiem na północ.'),
                 ('Kiedy najlepiej obserwować?', 'Gdy jest zupełnie ciemno, zwykle między 22:00 a 2:00, z dala od świateł miasta, patrząc na północ. Okno ciemności dla Twojej lokalizacji jest na tej stronie.'),
                 ('Skąd pochodzi prognoza?', 'Z NOAA Space Weather Prediction Center (USA): model OVATION (30–90 minut naprzód) i 3-dniowa prognoza Kp. Lokalizacja jest używana tylko w przeglądarce.')]),
}


def pick(d, v):
    k = max(x for x in d if v >= x)
    return d[k]


CSS = ('<style id="au-css">#au-map{height:420px;border-radius:14px;border:1px solid #E3E7EE;margin:10px 0;z-index:0;background:#0B1F3F}'
       '.au-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin-top:10px}.au-grid>div{border:1px solid #E3E7EE;border-radius:12px;padding:10px;background:#fff}'
       '.au-grid span{display:block;font-size:12.5px;color:#5B6B82}.au-grid b{display:block;font-size:22px;color:#12305C;margin-top:2px}.au-grid em{font-style:normal;font-size:12.5px;color:#12305C}'
       '#au-loc{font:inherit;font-weight:700;padding:10px 14px;border-radius:10px;border:0;background:#12305C;color:#fff;cursor:pointer}'
       '.au-note{font-size:13px;color:#5B6B82;line-height:1.55;margin:6px 0}.au-kp{width:100%;border-collapse:collapse;font-size:14px}.au-kp th,.au-kp td{padding:8px 6px;border-bottom:1px solid #E3E7EE;text-align:left}'
       '.au-bar{display:inline-block;height:10px;border-radius:5px;vertical-align:middle;margin-right:6px}.au-dark{margin-top:10px;font-size:14px;color:#12305C;font-weight:700;overflow-wrap:anywhere}</style>')


def build(cc):
    lang, hemi, center, zoom, nm = C[cc]
    t = T[lang]
    A = ('Southern Lights' if hemi == 'S' else 'Northern Lights') if lang == 'en' else ''
    a = ('Southern Lights (Aurora Australis)' if hemi == 'S' else 'Northern Lights') if lang == 'en' else ''
    F = lambda s: s.replace('{n}', nm).replace('{A}', A).replace('{a}', a).replace('{o}', OBS).replace('{f}', FC).replace('{dir}', 'south' if hemi == 'S' else 'north')
    title, desc = F(t['title']), F(t['desc'])
    kptxt = F(t['kpTxt']).replace('{k}', str(kp_now[1]) if kp_now else '–').replace('{t}', kp_now[0][:16] if kp_now else '–')
    krows = ''.join(f'<tr><td>{d}</td><td><span class="au-bar" style="width:{max(6, v * 10):.0f}px;background:{"#2F9E44" if v < 4 else "#F08C00" if v < 5 else "#E03131"}"></span><b>{v:.2f}</b></td><td>{E(pick(t["out"], v))}</td></tr>' for d, v in DAYS)
    faq = [(F(q), F(x)) for q, x in t['faq']]
    url = f'{B}/{cc}/{t["slug"]}'
    body = (f'<header class="hero"><div class="in"><span class="year">NOAA · live</span><h1>{F(t["h1"])}</h1><p>{E(t["sub"])}</p></div></header>\n<main class="wrap">\n'
            f'<section class="card"><button type="button" id="au-loc">{E(t["loc"])}</button>'
            f'<div class="au-grid"><div><span>{E(t["chance"])}</span><b id="au-p">–</b><em id="au-v"></em></div><div><span>{E(t["near"])}</span><b id="au-n">–</b></div>'
            f'<div><span>{E(t["kpNow"])}</span><b>{kp_now[1] if kp_now else "–"}</b><em>{E(pick(t["out"], float(kp_now[1])) if kp_now else "")}</em></div><div><span>{E(t["dark"])}</span><b id="au-d">–</b></div></div>'
            '<p class="au-dark" id="au-dw"></p>'
            '<div id="au-map" role="region" aria-label="map"></div><div class="qk-leg" style="display:flex;gap:12px;flex-wrap:wrap;font-size:12.5px;color:#5B6B82"><span><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#2B8A3E;margin-right:4px"></i>3–9 %</span><span><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#94D82D;margin-right:4px"></i>10–29 %</span><span><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#F08C00;margin-right:4px"></i>30–49 %</span><span><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#E03131;margin-right:4px"></i>50 %+</span></div>'
            f'<p class="au-note">{E(F(t["mapNote"]))}</p></section>\n'
            f'<section class="card"><h2>{E(t["kpT"])}</h2><p>{E(kptxt)}</p><table class="au-kp"><thead><tr>' + ''.join(f'<th>{E(x)}</th>' for x in t['kpCols']) + f'</tr></thead><tbody>{krows}</tbody></table>'
            f'<p class="au-note">{E(t["src"])} <a href="https://www.swpc.noaa.gov/products/aurora-30-minute-forecast" target="_blank" rel="noopener">swpc.noaa.gov</a></p></section>\n'
            + faq_html(faq) + '\n</main>')
    cfg = {'center': center, 'zoom': zoom, 'hemi': hemi, 't': {k: t[k] for k in ('yes', 'no', 'darkFrom', 'noDark')}, 'verdict': t['verdict']}
    return build_page(SITE, cc, t['slug'], title, desc, body,
                      ld=[app_ld(title.split(' – ')[0], url, 'ReferenceApplication', {"dateModified": time.strftime('%Y-%m-%d')}), faq_ld(faq)],
                      head_extra='<link rel="stylesheet" href="/assets/leaflet/leaflet.css">' + CSS,
                      tail_extra=f'<script>window.AUCFG={json.dumps(cfg, ensure_ascii=False, separators=(",", ":"))};</script><script src="/assets/leaflet/leaflet.js"></script><script src="/assets/aurora.js" defer></script>',
                      marker='data-hl-aurora')


made = [build(cc) for cc in C]
register(SITE, made)
print('aurora pages:', sum(1 for m in made if m), 'grid', len(GRID), 'kp', kp_now, DAYS)
