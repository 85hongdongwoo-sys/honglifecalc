# 나라별 '충전소 지도 + 충전비 계산기' 페이지를 그 나라 기존 계산기 페이지 틀(머리·바닥글)로 만든다 → overlay/<cc>/<slug>.html
# 사용: python3 build/ev/gen_ev_pages.py <풀어둔 사이트 폴더>
import json, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
B = 'https://honglifecalc.com'

P = {
 'de': dict(tpl='de/spritkosten-rechner.html', slug='ladesaeulen-karte.html', locale='de-DE', cur='EUR', center=[52.52, 13.405], hub_after='/de/spritkosten-rechner.html',
   label='Ladesäulen-Karte & Ladekosten-Rechner',
   title='Ladesäulen in der Nähe – Karte mit Ladekosten-Rechner (Bundesnetzagentur-Daten)',
   desc='Öffentliche Ladesäulen in Ihrer Nähe auf der Karte: Ladeleistung (kW), Stecker (CCS, Typ 2, CHAdeMO), Betreiber und Route. Dazu Ladekosten und Ladedauer in Euro berechnen – mit den offiziellen Daten des Ladesäulenregisters der Bundesnetzagentur.',
   h1='<b>Ladesäulen</b> in der Nähe', sub='Nächste Ladesäule finden, Ladedauer und Kosten für Ihr Auto sehen, mit einem Tipp losnavigieren.',
   loc='📍 Meinen Standort verwenden', fast='⚡ Nächster Schnelllader', all='Alle', plugAll='Alle Stecker',
   calcH='Ladekosten & Ladedauer berechnen', f=['Akkukapazität (kWh)', 'Ladestand von (%)', 'Laden bis (%)', 'Ladeleistung der Säule (kW)', 'Max. Ladeleistung des Autos (kW)', 'Ladeverluste (%)', 'Strompreis (€/kWh)', 'Verbrauch E-Auto (kWh/100 km)', 'Vergleich Verbrenner (l/100 km)', 'Spritpreis (€/l)'],
   v=['60', '20', '80', '50', '100', '10', '0,38', '17', '6,5', '1,75'], priceNote='Beispielwerte – tragen Sie den Preis Ihres Ladetarifs ein.',
   t=dict(domestic='Schuko', energy='Strom aus dem Netz', inBattery='Davon im Akku', time='Ladedauer (ca.)', power='Wirksame Leistung', range='Reichweite dazu (ca.)', per100='Kosten pro 100 km',
          fuelSame='Sprit für dieselbe Strecke', save='Ersparnis gegenüber Verbrenner', more='Mehrkosten gegenüber Verbrenner', cost='Ladekosten', check='Bitte Akkukapazität, Ladestand und Leistung prüfen.',
          calcNote='Dauer vereinfacht: Oberhalb von ca. 80 % laden Schnelllader deutlich langsamer.', points='Ladepunkte', route='Route', call='Anrufen', useKw='Leistung im Rechner nutzen',
          zoomIn='Zum Anzeigen der Ladesäulen bitte näher heranzoomen.', inView='{n} Ladesäulen im Kartenausschnitt', nearest='die nächsten zuerst', none='Keine Ladesäule im Ausschnitt – Karte verschieben oder Filter ändern.',
          stat='{s} Standorte mit {p} Ladepunkten, davon {f} Schnelllader (ab 50 kW). Quelle:', loadErr='Daten konnten nicht geladen werden.', noGeo='Standort nicht verfügbar', locating='Standort wird gesucht…', locDone='📍 Standort gefunden', you='Ihr Standort', free='kostenlos', noFast='Kein Schnelllader in der Nähe gefunden'),
   faq=[('Woher stammen die Ladesäulen-Daten?', 'Aus dem Ladesäulenregister der Bundesnetzagentur. Betreiber öffentlich zugänglicher Ladepunkte müssen diese dort anzeigen. Die Daten stehen unter der Lizenz CC BY 4.0 und werden hier wöchentlich aktualisiert. Nicht jede Ladesäule ist erfasst, weil nur abgeschlossene Anzeigen veröffentlicht werden.'),
        ('Wie berechne ich die Ladekosten?', 'Ladekosten = Akkukapazität × (Ziel-Ladestand − Start-Ladestand) ÷ (1 − Ladeverluste) × Strompreis. Beispiel: 60 kWh von 20 % auf 80 % sind 36 kWh im Akku, mit 10 % Verlust rund 40 kWh aus dem Netz.'),
        ('Wird mein Standort gespeichert?', 'Nein. Ihr Standort wird nur in Ihrem Browser verwendet, um die nächsten Ladesäulen zu sortieren, und nicht an unseren Server gesendet.')],
   src_line='Ladesäulen: Bundesnetzagentur, Ladesäulenregister (CC BY 4.0). Karte: © OpenStreetMap-Mitwirkende.'),
 'fr': dict(tpl='fr/calcul-cout-carburant.html', slug='carte-bornes-recharge.html', locale='fr-FR', cur='EUR', center=[48.8566, 2.3522], hub_after='/fr/calcul-cout-carburant.html',
   label='Carte des bornes de recharge & coût de recharge',
   title='Bornes de recharge près de moi – carte et calcul du coût de recharge (données IRVE officielles)',
   desc='Les bornes de recharge publiques autour de vous sur une carte : puissance (kW), prises (Type 2, CCS, CHAdeMO), opérateur, téléphone et itinéraire. Calculez aussi le coût et la durée de recharge en euros, avec la base nationale officielle des IRVE (data.gouv.fr).',
   h1='<b>Bornes de recharge</b> près de moi', sub='Trouvez la borne la plus proche, voyez la durée et le coût pour votre voiture, lancez l’itinéraire en un geste.',
   loc='📍 Utiliser ma position', fast='⚡ Borne rapide la plus proche', all='Toutes', plugAll='Toutes les prises',
   calcH='Calculer le coût et la durée de recharge', f=['Capacité de la batterie (kWh)', 'Charge de départ (%)', 'Charger jusqu’à (%)', 'Puissance de la borne (kW)', 'Puissance max. du véhicule (kW)', 'Pertes de recharge (%)', 'Prix de l’électricité (€/kWh)', 'Consommation VE (kWh/100 km)', 'Comparaison thermique (L/100 km)', 'Prix du carburant (€/L)'],
   v=['60', '20', '80', '50', '100', '10', '0,25', '17', '7', '1,75'], priceNote='Valeurs d’exemple – saisissez le prix de votre offre ou de la borne.',
   t=dict(domestic='Prise E/F', energy='Électricité soutirée', inBattery='Dont dans la batterie', time='Durée (env.)', power='Puissance effective', range='Autonomie ajoutée (env.)', per100='Coût aux 100 km',
          fuelSame='Carburant pour la même distance', save='Économie vs thermique', more='Surcoût vs thermique', cost='Coût de recharge', check='Vérifiez la capacité, la charge et la puissance.',
          calcNote='Durée simplifiée : au-delà d’environ 80 %, la recharge rapide ralentit nettement.', points='points de charge', route='Itinéraire', call='Appeler', useKw='Utiliser cette puissance',
          zoomIn='Zoomez pour afficher les bornes.', inView='{n} stations dans la zone affichée', nearest='les plus proches d’abord', none='Aucune borne dans la zone – déplacez la carte ou changez les filtres.',
          stat='{s} stations, {p} points de charge, dont {f} rapides (50 kW et plus). Source :', loadErr='Impossible de charger les données.', noGeo='Position indisponible', locating='Recherche de la position…', locDone='📍 Position trouvée', you='Votre position', free='gratuit', noFast='Aucune borne rapide trouvée à proximité'),
   faq=[('D’où viennent les données des bornes ?', 'De la base nationale des IRVE consolidée par data.gouv.fr à partir des déclarations des aménageurs, sous Licence Ouverte 2.0. Elle est mise à jour ici chaque semaine. Certaines bornes peuvent manquer ou être incomplètes.'),
        ('Comment calculer le coût d’une recharge ?', 'Coût = capacité × (charge visée − charge de départ) ÷ (1 − pertes) × prix du kWh. Exemple : 60 kWh de 20 % à 80 % font 36 kWh dans la batterie, soit environ 40 kWh soutirés avec 10 % de pertes.'),
        ('Ma position est-elle enregistrée ?', 'Non. Votre position sert uniquement dans votre navigateur à trier les bornes les plus proches ; elle n’est pas envoyée à notre serveur.')],
   src_line='Bornes : base nationale des IRVE, data.gouv.fr (Licence Ouverte 2.0). Carte : © contributeurs OpenStreetMap.'),
}

CSS = ('<style id="ev-css">#ev-map{height:420px;border-radius:14px;border:1px solid #E3E7EE;margin:10px 0;z-index:0}'
       '.ev-tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.ev-tools button,.ev-tools select{font:inherit;font-size:14px;padding:9px 12px;border-radius:10px;border:1px solid #CBD3DF;background:#fff;cursor:pointer}'
       '.ev-tools #ev-loc{background:#12305C;color:#fff;border-color:#12305C;font-weight:700}.ev-tools button[aria-pressed=true]{background:#E7F0FF;border-color:#1971C2;color:#12305C;font-weight:700}'
       '.ev-stat,.ev-note,.ev-cnt{font-size:13px;color:#5B6B82;line-height:1.55;margin:6px 0}.ev-ol{list-style:none;margin:0;padding:0}'
       '.ev-ol li{display:flex;justify-content:space-between;gap:10px;padding:10px 4px;border-top:1px solid #E3E7EE;cursor:pointer}.ev-ol li>div{min-width:0}'
       '.ev-ol b{display:block;font-size:14.5px;color:#12305C;overflow-wrap:anywhere}.ev-ol small{display:block;font-size:12.5px;color:#5B6B82;overflow-wrap:anywhere}'
       '.ev-r{display:flex;flex-direction:column;align-items:flex-end;gap:4px;flex:none}.ev-r em{font-style:normal;font-size:12.5px;color:#12305C;font-weight:700}.ev-r a{font-size:13px;font-weight:700}'
       '.ev-kw{display:inline-block;color:#fff;font-weight:800;font-size:12px;padding:2px 7px;border-radius:999px;white-space:nowrap}'
       '.ev-pop{font-size:13px;line-height:1.5;max-width:240px}.ev-btns{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}.ev-btns a,.ev-btns button{font:inherit;font-size:12.5px;padding:5px 8px;border-radius:8px;border:1px solid #CBD3DF;background:#F7F8FB;color:#12305C;text-decoration:none;cursor:pointer}'
       '.ev-warn{color:#B42318}.ev-b{display:inline-block;font-size:11px;font-weight:800;padding:1px 6px;border-radius:6px;background:#E6F4EA;color:#1E6B34;margin-left:4px;vertical-align:1px}.ev-free{background:#FFF4E5;color:#9A4B00}'
       '.ev-est{color:#12305C!important;font-weight:700;margin-top:3px}.ev-ol .ev-btns{margin-top:6px}.ev-ol .ev-btns a{padding:7px 10px;font-weight:700}.ev-tools #ev-fast{background:#D9480F;color:#fff;border-color:#D9480F;font-weight:700}.ev-legend{display:flex;gap:10px;flex-wrap:wrap;font-size:12.5px;color:#5B6B82}.ev-legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;vertical-align:-1px}</style>')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def build(cc, c):
    tpl = open(os.path.join(SITE, c['tpl']), encoding='utf-8').read()
    url = f'{B}/{cc}/{c["slug"]}'
    h = tpl
    h = re.sub(r'<title>.*?</title>', f'<title>{esc(c["title"])}</title>', h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(c["desc"])}">', h, count=1)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h, count=1)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(c["title"])}">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(c["desc"])}">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', h)
    h = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{esc(c["label"])}">', h)
    h = re.sub(r'(?s)<script type="application/ld\+json">.*?</script>', '', h)
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c['faq']]}
    app = {"@context": "https://schema.org", "@type": "WebApplication", "name": c['label'], "url": url, "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any",
           "inLanguage": c['locale'], "offers": {"@type": "Offer", "price": "0", "priceCurrency": c['cur']}}
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (app, faq))
    head_add = ('<link rel="stylesheet" href="/assets/leaflet/leaflet.css">' + CSS + ld)
    h = h.replace('</head>', head_add + '</head>', 1)
    fields = ''.join(f'<label class="f"><span>{esc(lab)}</span><input id="ev-{k}" inputmode="decimal" value="{v}"></label>'
                     for lab, k, v in zip(c['f'], ['bat', 'from', 'to', 'ckw', 'car', 'loss', 'price', 'cons', 'fcons', 'fprice'], c['v']))
    t = c['t']
    body = (f'<header class="hero"><div class="in"><span class="year">{"🇩🇪" if cc == "de" else "🇫🇷"} 2026</span><h1>{c["h1"]}</h1><p>{esc(c["sub"])}</p></div></header>\n'
            '<main class="wrap">\n'
            f'<section class="card"><div class="ev-tools"><button type="button" id="ev-loc">{esc(c["loc"])}</button><button type="button" id="ev-fast">{esc(c["fast"])}</button>'
            f'<button type="button" data-minkw="0" aria-pressed="true">{esc(c["all"])}</button><button type="button" data-minkw="50" aria-pressed="false">≥ 50 kW</button><button type="button" data-minkw="150" aria-pressed="false">≥ 150 kW</button>'
            f'<select id="ev-plug" aria-label="{esc(c["plugAll"])}"><option value="0">{esc(c["plugAll"])}</option><option value="2">CCS</option><option value="1">Type 2</option><option value="4">CHAdeMO</option></select></div>'
            '<div id="ev-map" role="region" aria-label="map"></div>'
            '<div class="ev-legend"><span><i style="background:#1971C2"></i>&lt; 50 kW</span><span><i style="background:#D9480F"></i>50–149 kW</span><span><i style="background:#7C3AED"></i>≥ 150 kW</span></div>'
            '<p class="ev-stat" id="ev-stat">…</p><div id="ev-list"></div></section>\n'
            f'<section class="app" id="ev-calc"><form class="card" onsubmit="return false"><h2>{esc(c["calcH"])}</h2>{fields}<p class="ev-note">{esc(c["priceNote"])}</p></form>'
            '<section class="card" id="ev-out" aria-live="polite"></section></section>\n'
            '<article class="card help"><h2>FAQ</h2>' + ''.join(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>' for q, a in c['faq']) +
            f'<p class="note">{esc(c["src_line"])}</p></article>\n</main>\n')
    h = re.sub(r'(?s)<header class="hero">.*?(?=<footer>)', lambda m: body, h, count=1)
    cfg = {'cc': cc, 'locale': c['locale'], 'cur': c['cur'], 'center': c['center'], 't': t}
    tail = (f'<script>window.EVCFG={json.dumps(cfg, ensure_ascii=False)};</script>'
            '<script src="/assets/leaflet/leaflet.js"></script><script src="/assets/ev-map.js" defer></script>')
    # 원래 페이지 계산 스크립트(바닥글 뒤 마지막 인라인 스크립트) 제거
    i = h.index('</footer>') + len('</footer>')
    rest = re.sub(r'(?s)<script>\s*\(function\(\)\{\'use strict\';.*?</script>', '', h[i:], count=1)
    h = h[:i] + rest.replace('</body>', tail + '</body>', 1)
    out = os.path.join(REPO, 'overlay', cc, c['slug'])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(h)
    return {'url': f'/{cc}/{c["slug"]}', 'hub': f'/{cc}/index.html', 'after': c['hub_after'], 'label': c['label']}


pages = [build(cc, c) for cc, c in P.items()]
json.dump(pages, open(os.path.join(REPO, 'build', 'new_pages.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n'.join(p['url'] for p in pages))
