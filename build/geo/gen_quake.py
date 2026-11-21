# 나라별 실시간 지진 지도 페이지 (USGS) — 배포 때 최근 큰 지진 표·나라별 횟수를 본문에 넣는다.
# 사용: python3 build/geo/gen_quake.py _site
import json, math, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pagekit import B, E, build_page, faq_ld, app_ld, faq_html, register

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
UA = {'User-Agent': 'Mozilla/5.0 (honglifecalc.com earthquake map)'}
FEED = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/'


week = json.load(open(os.path.join(SITE, 'geo', 'quake_week.json')))['features']
now = time.time() * 1000
Q = [[round(f['geometry']['coordinates'][1], 3), round(f['geometry']['coordinates'][0], 3), round(f['geometry']['coordinates'][2] or 0, 1),
      f['properties']['mag'], f['properties']['time'], f['properties']['place'] or '', f['properties']['tsunami'] or 0, f['properties']['url'], f['properties'].get('felt') or 0]
     for f in week if f['properties'].get('mag') is not None]
Q.sort(key=lambda q: -q[4])
SNAP = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())

# cc: (언어, 중심, 줌, bbox[s,w,n,e] 또는 None, 나라 이름, 공식 기관(이름, 주소))
C = {
 'us': ('en', [39, -98], 3, [18, -180, 72, -65], 'the United States', ('USGS', 'https://earthquake.usgs.gov/')),
 'ca': ('en', [56, -100], 3, [41, -141, 84, -52], 'Canada', ('Natural Resources Canada – Earthquakes Canada', 'https://earthquakescanada.nrcan.gc.ca/')),
 'nz': ('en', [-41, 174], 5, [-48, 165, -34, 179.9], 'New Zealand', ('GeoNet', 'https://www.geonet.org.nz/')),
 'ph': ('en', [12, 122], 5, [4, 116, 21, 127], 'the Philippines', ('PHIVOLCS', 'https://www.phivolcs.dost.gov.ph/')),
 'in': ('en', [22, 80], 4, [6, 68, 36, 98], 'India', ('National Center for Seismology', 'https://seismo.gov.in/')),
 'en': ('en', [20, 0], 2, None, 'the world', ('USGS', 'https://earthquake.usgs.gov/')),
 'jp': ('ja', [37, 138], 4, [24, 122, 46, 154], '日本', ('気象庁', 'https://www.jma.go.jp/bosai/map.html#contents=earthquake_map')),
 'tr': ('tr', [39, 35], 5, [35, 25, 43, 45], 'Türkiye', ('AFAD', 'https://deprem.afad.gov.tr/')),
 'id': ('id', [-2, 118], 4, [-11, 94, 6, 141], 'Indonesia', ('BMKG', 'https://www.bmkg.go.id/')),
 'mx': ('es', [23, -102], 4, [14, -118, 33, -86], 'México', ('Servicio Sismológico Nacional', 'http://www.ssn.unam.mx/')),
 'cl': ('es', [-35, -71], 4, [-56, -76, -17, -66], 'Chile', ('Centro Sismológico Nacional', 'https://www.sismologia.cl/')),
 'co': ('es', [4, -74], 5, [-5, -80, 13, -66], 'Colombia', ('Servicio Geológico Colombiano', 'https://www.sgc.gov.co/sismos')),
 'es': ('es', [40, -4], 5, [27, -19, 44, 5], 'España', ('Instituto Geográfico Nacional', 'https://www.ign.es/web/ign/portal/sis-catalogo-terremotos')),
 'it': ('it', [42, 12.5], 5, [36, 6, 47, 19], 'Italia', ('INGV', 'https://terremoti.ingv.it/')),
 'zh': ('zh', [34, 105], 3, [18, 73, 54, 135], '中国', ('中国地震台网', 'https://news.ceic.ac.cn/')),
}

T = {
 'en': dict(slug='earthquake-map.html', title='Earthquakes Near Me – Live Map of Recent Earthquakes in {n} Today', desc='Live earthquake map with USGS data, updated every minute: see recent quakes near you, distance from your location, magnitude, depth and tsunami flags. Includes the strongest earthquakes of the past 7 days in {n}.',
            h1='<b>Earthquakes</b> near me', sub='Live USGS data – distance from you, magnitude, depth and tsunami flags.',
            loc='📍 Use my location', near='Only within 500 km', m25='M2.5+', m45='M4.5+', sig='Significant', d1='24 h', d7='7 days', d30='30 days',
            list='Latest earthquakes', nearest='Nearest to you', strongest='Strongest', away='km from you', depth='Depth', tsu='Tsunami possible', felt='Did you feel it?', none='No earthquakes match these filters.',
            live='Live · updated {t}', legend=['< 1 hour', '< 24 hours', 'older'],
            weekT='Strongest earthquakes in the last 7 days (M4.5+)', cnt='{c} earthquakes of magnitude 4.5 or more were recorded in or near {n} in the last 7 days (USGS, as of {s}).', cnt0='No earthquake of magnitude 4.5 or more was recorded in or near {n} in the last 7 days (USGS, as of {s}).',
            th=['Time (UTC)', 'Place', 'Mag.', 'Depth'], src='Earthquake data: U.S. Geological Survey (USGS), public domain. For official warnings in {n} follow {a}.',
            faq=[('Where do these earthquake data come from?', 'From the U.S. Geological Survey (USGS) real-time feeds, which list earthquakes worldwide within minutes. Small local quakes may appear first on your national seismic agency’s website ({a}).'),
                 ('What does the magnitude mean?', 'Magnitude measures the energy released. Each whole number is about 32 times more energy: M5 is light to moderate, M6 can cause damage near the epicentre, M7 and above are major earthquakes.'),
                 ('Is my location stored?', 'No. Your location is only used in your browser to calculate distances and is never sent to our server.')]),
 'ja': dict(slug='jishin-map.html', title='地震情報マップ – 今日の地震・震源地をリアルタイム表示（{n}・世界）', desc='USGSのリアルタイムデータで最新の地震を地図に表示。現在地からの距離、マグニチュード、震源の深さ、津波の可能性をすぐ確認。過去7日間の大きな地震一覧も。',
            h1='<b>地震</b>情報マップ', sub='USGSリアルタイムデータ – 現在地からの距離・規模・深さ・津波の有無。',
            loc='📍 現在地を使う', near='500 km以内のみ', m25='M2.5以上', m45='M4.5以上', sig='重要な地震', d1='24時間', d7='7日間', d30='30日間',
            list='最新の地震', nearest='近い順', strongest='規模順', away='km（現在地から）', depth='深さ', tsu='津波の可能性', felt='揺れを報告', none='条件に合う地震はありません。',
            live='自動更新 · {t}', legend=['1時間以内', '24時間以内', 'それ以前'],
            weekT='過去7日間の大きな地震（M4.5以上）', cnt='過去7日間に{n}周辺でM4.5以上の地震が{c}回観測されました（USGS、{s}時点）。', cnt0='過去7日間に{n}周辺でM4.5以上の地震は観測されていません（USGS、{s}時点）。',
            th=['時刻（UTC）', '場所', '規模', '深さ'], src='地震データ：米国地質調査所（USGS）。日本の震度・津波情報は{a}の発表を確認してください。',
            faq=[('このデータはどこから？', '米国地質調査所（USGS）のリアルタイム情報で、世界の地震を数分以内に掲載します。震度や津波警報など日本の公式情報は{a}が発表します。'),
                 ('マグニチュードと震度の違いは？', 'マグニチュードは地震そのもののエネルギーの大きさ、震度は各地の揺れの強さです。マグニチュードが1大きくなるとエネルギーは約32倍になります。'),
                 ('現在地は保存されますか？', 'いいえ。現在地はブラウザ内で距離の計算にだけ使い、サーバーには送りません。')]),
 'tr': dict(slug='deprem-haritasi.html', title='Son Depremler Haritası – {n} ve Dünyada Canlı Deprem Listesi', desc='USGS verileriyle canlı deprem haritası: son depremler, konumunuza uzaklık, büyüklük, derinlik ve tsunami uyarısı. Son 7 günün en büyük depremleri listesi.',
            h1='<b>Son depremler</b> haritası', sub='Canlı USGS verisi – size uzaklık, büyüklük, derinlik ve tsunami uyarısı.',
            loc='📍 Konumumu kullan', near='Yalnızca 500 km içinde', m25='M2.5+', m45='M4.5+', sig='Önemli', d1='24 saat', d7='7 gün', d30='30 gün',
            list='Son depremler', nearest='Bana en yakın', strongest='En büyük', away='km uzakta', depth='Derinlik', tsu='Tsunami olasılığı', felt='Hissettiniz mi?', none='Bu filtrelere uyan deprem yok.',
            live='Canlı · güncelleme {t}', legend=['< 1 saat', '< 24 saat', 'daha eski'],
            weekT='Son 7 günün en büyük depremleri (M4.5+)', cnt='Son 7 günde {n} ve çevresinde 4,5 ve üzeri {c} deprem kaydedildi (USGS, {s} itibarıyla).', cnt0='Son 7 günde {n} ve çevresinde 4,5 ve üzeri deprem kaydedilmedi (USGS, {s} itibarıyla).',
            th=['Saat (UTC)', 'Yer', 'Büyüklük', 'Derinlik'], src='Deprem verisi: ABD Jeolojik Araştırmalar Kurumu (USGS). Türkiye için resmi bilgi: {a}.',
            faq=[('Bu veriler nereden geliyor?', 'ABD Jeolojik Araştırmalar Kurumu’nun (USGS) canlı akışından; dünyadaki depremler dakikalar içinde listelenir. Küçük yerel depremler önce {a} sitesinde görünebilir.'),
                 ('Büyüklük ne anlama gelir?', 'Büyüklük açığa çıkan enerjiyi ölçer. Her tam sayı yaklaşık 32 kat daha fazla enerji demektir: M5 hafif-orta, M6 merkez üssü yakınında hasar verebilir, M7 ve üzeri büyük depremdir.'),
                 ('Konumum kaydediliyor mu?', 'Hayır. Konumunuz yalnızca tarayıcınızda uzaklık hesaplamak için kullanılır, sunucumuza gönderilmez.')]),
 'id': dict(slug='peta-gempa.html', title='Peta Gempa Terkini – Gempa Hari Ini di {n} dan Dunia (Real-time)', desc='Peta gempa real-time dengan data USGS: gempa terbaru, jarak dari lokasi Anda, magnitudo, kedalaman, dan potensi tsunami. Daftar gempa terbesar 7 hari terakhir.',
            h1='<b>Peta gempa</b> terkini', sub='Data USGS real-time – jarak dari Anda, magnitudo, kedalaman, dan potensi tsunami.',
            loc='📍 Pakai lokasi saya', near='Hanya dalam 500 km', m25='M2,5+', m45='M4,5+', sig='Signifikan', d1='24 jam', d7='7 hari', d30='30 hari',
            list='Gempa terbaru', nearest='Terdekat', strongest='Terbesar', away='km dari Anda', depth='Kedalaman', tsu='Potensi tsunami', felt='Anda merasakan?', none='Tidak ada gempa yang sesuai filter.',
            live='Langsung · diperbarui {t}', legend=['< 1 jam', '< 24 jam', 'lebih lama'],
            weekT='Gempa terbesar 7 hari terakhir (M4,5+)', cnt='Dalam 7 hari terakhir tercatat {c} gempa bermagnitudo 4,5 atau lebih di dan sekitar {n} (USGS, per {s}).', cnt0='Dalam 7 hari terakhir tidak tercatat gempa bermagnitudo 4,5 atau lebih di sekitar {n} (USGS, per {s}).',
            th=['Waktu (UTC)', 'Lokasi', 'Mag.', 'Kedalaman'], src='Data gempa: Survei Geologi Amerika Serikat (USGS). Untuk peringatan resmi di Indonesia ikuti {a}.',
            faq=[('Dari mana data gempa ini?', 'Dari umpan real-time Survei Geologi Amerika Serikat (USGS) yang mencatat gempa di seluruh dunia dalam hitungan menit. Peringatan dini tsunami resmi di Indonesia dikeluarkan oleh {a}.'),
                 ('Apa arti magnitudo?', 'Magnitudo mengukur energi yang dilepaskan. Setiap naik satu angka energinya sekitar 32 kali lipat: M5 ringan–sedang, M6 dapat merusak dekat episentrum, M7 ke atas gempa besar.'),
                 ('Apakah lokasi saya disimpan?', 'Tidak. Lokasi Anda hanya dipakai di browser untuk menghitung jarak dan tidak dikirim ke server kami.')]),
 'es': dict(slug='mapa-sismos.html', title='Sismos Hoy – Mapa en Vivo de los Últimos Temblores en {n} y el Mundo', desc='Mapa de sismos en tiempo real con datos del USGS: últimos temblores, distancia desde tu ubicación, magnitud, profundidad y alerta de tsunami. Con los sismos más fuertes de los últimos 7 días.',
            h1='<b>Sismos</b> hoy', sub='Datos en vivo del USGS – distancia desde ti, magnitud, profundidad y posible tsunami.',
            loc='📍 Usar mi ubicación', near='Solo a menos de 500 km', m25='M2.5+', m45='M4.5+', sig='Relevantes', d1='24 h', d7='7 días', d30='30 días',
            list='Últimos sismos', nearest='Más cercanos', strongest='Más fuertes', away='km de ti', depth='Profundidad', tsu='Posible tsunami', felt='¿Lo sentiste?', none='No hay sismos con estos filtros.',
            live='En vivo · actualizado {t}', legend=['< 1 hora', '< 24 horas', 'anterior'],
            weekT='Sismos más fuertes de los últimos 7 días (M4.5+)', cnt='En los últimos 7 días se registraron {c} sismos de magnitud 4.5 o más en {n} y sus alrededores (USGS, a {s}).', cnt0='En los últimos 7 días no se registraron sismos de magnitud 4.5 o más en {n} ni sus alrededores (USGS, a {s}).',
            th=['Hora (UTC)', 'Lugar', 'Mag.', 'Prof.'], src='Datos sísmicos: Servicio Geológico de los Estados Unidos (USGS), dominio público. Información oficial en {n}: {a}.',
            faq=[('¿De dónde salen estos datos?', 'Del servicio en tiempo real del Servicio Geológico de los Estados Unidos (USGS), que publica los sismos del mundo en minutos. Los sismos locales pequeños pueden aparecer antes en {a}.'),
                 ('¿Qué significa la magnitud?', 'La magnitud mide la energía liberada. Cada punto entero equivale a unas 32 veces más energía: M5 es leve a moderado, M6 puede causar daños cerca del epicentro y M7 o más es un sismo mayor.'),
                 ('¿Se guarda mi ubicación?', 'No. Tu ubicación solo se usa en tu navegador para calcular distancias y no se envía a nuestro servidor.')]),
 'it': dict(slug='mappa-terremoti.html', title='Terremoti Oggi – Mappa in Tempo Reale degli Ultimi Terremoti in {n} e nel Mondo', desc='Mappa dei terremoti in tempo reale con dati USGS: ultime scosse, distanza dalla tua posizione, magnitudo, profondità e possibile tsunami. Con i terremoti più forti degli ultimi 7 giorni.',
            h1='<b>Terremoti</b> oggi', sub='Dati USGS in tempo reale – distanza da te, magnitudo, profondità e possibile tsunami.',
            loc='📍 Usa la mia posizione', near='Solo entro 500 km', m25='M2,5+', m45='M4,5+', sig='Significativi', d1='24 ore', d7='7 giorni', d30='30 giorni',
            list='Ultimi terremoti', nearest='Più vicini', strongest='Più forti', away='km da te', depth='Profondità', tsu='Possibile tsunami', felt='L’hai sentito?', none='Nessun terremoto con questi filtri.',
            live='In diretta · aggiornato {t}', legend=['< 1 ora', '< 24 ore', 'precedenti'],
            weekT='Terremoti più forti degli ultimi 7 giorni (M4,5+)', cnt='Negli ultimi 7 giorni sono stati registrati {c} terremoti di magnitudo 4,5 o superiore in {n} e dintorni (USGS, al {s}).', cnt0='Negli ultimi 7 giorni non sono stati registrati terremoti di magnitudo 4,5 o superiore in {n} e dintorni (USGS, al {s}).',
            th=['Ora (UTC)', 'Luogo', 'Mag.', 'Prof.'], src='Dati sismici: Servizio geologico degli Stati Uniti (USGS), pubblico dominio. Per le scosse in Italia la fonte ufficiale è {a}.',
            faq=[('Da dove vengono questi dati?', 'Dal servizio in tempo reale del Servizio geologico degli Stati Uniti (USGS), che pubblica i terremoti di tutto il mondo in pochi minuti. Le piccole scosse italiane compaiono prima su {a}.'),
                 ('Cosa indica la magnitudo?', 'La magnitudo misura l’energia liberata. Ogni punto in più vale circa 32 volte più energia: M5 è leggero-moderato, M6 può causare danni vicino all’epicentro, da M7 in su è un forte terremoto.'),
                 ('La mia posizione viene salvata?', 'No. La posizione è usata solo nel browser per calcolare le distanze e non viene inviata al nostro server.')]),
 'zh': dict(slug='dizhen-ditu.html', title='地震实时地图 – 今天{n}及全球最新地震', desc='用美国地质调查局（USGS）实时数据查看最新地震：离你的距离、震级、震源深度和海啸可能性，以及过去7天的强震列表。',
            h1='<b>地震</b>实时地图', sub='USGS实时数据 – 离你的距离、震级、深度和海啸提示。',
            loc='📍 使用我的位置', near='只看500公里内', m25='M2.5+', m45='M4.5+', sig='重要地震', d1='24小时', d7='7天', d30='30天',
            list='最新地震', nearest='离我最近', strongest='震级最大', away='公里（离你）', depth='深度', tsu='可能有海啸', felt='有震感？', none='没有符合条件的地震。',
            live='实时 · 更新于 {t}', legend=['1小时内', '24小时内', '更早'],
            weekT='过去7天的强震（M4.5以上）', cnt='过去7天，{n}及周边共记录到{c}次4.5级以上地震（USGS，截至{s}）。', cnt0='过去7天，{n}及周边未记录到4.5级以上地震（USGS，截至{s}）。',
            th=['时间（UTC）', '地点', '震级', '深度'], src='地震数据：美国地质调查局（USGS）。中国的正式地震信息请以{a}为准。',
            faq=[('这些数据从哪里来？', '来自美国地质调查局（USGS）的实时数据，几分钟内就会列出全球地震。中国境内的正式速报请以{a}为准。'),
                 ('震级代表什么？', '震级表示地震释放的能量，每增加1级能量约增加32倍：5级为轻到中等，6级可能在震中附近造成破坏，7级以上为大地震。'),
                 ('会保存我的位置吗？', '不会。位置只在你的浏览器里用来计算距离，不会发送到我们的服务器。')]),
}
DEC_COMMA = {'tr', 'id', 'it', 'es'}


def num(x, lang, dp=1):
    s = f'{x:.{dp}f}'
    return s.replace('.', ',') if lang in DEC_COMMA else s


def inb(q, b):
    if not b:
        return True
    return b[0] <= q[0] <= b[2] and b[1] <= q[1] <= b[3]


CSS = ('<style id="qk-css">#qk-map{height:440px;border-radius:14px;border:1px solid #E3E7EE;margin:10px 0;z-index:0}'
       '.qk-tools{display:flex;flex-wrap:wrap;gap:6px;align-items:center}.qk-tools button{font:inherit;font-size:13.5px;padding:8px 11px;border-radius:10px;border:1px solid #CBD3DF;background:#fff;cursor:pointer}'
       '.qk-tools button[aria-pressed=true]{background:#E7F0FF;border-color:#1971C2;color:#12305C;font-weight:700}.qk-tools #qk-loc{background:#12305C;color:#fff;border-color:#12305C;font-weight:700}'
       '.qk-sep{width:100%;height:0}.qk-note{font-size:13px;color:#5B6B82;line-height:1.55;margin:6px 0}.qk-leg{display:flex;gap:12px;flex-wrap:wrap;font-size:12.5px;color:#5B6B82}.qk-leg i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;vertical-align:-1px}'
       '.qk-tabs{display:flex;gap:6px;margin:8px 0}.qk-tabs button{font:inherit;font-size:13.5px;padding:6px 10px;border-radius:999px;border:1px solid #CBD3DF;background:#fff;cursor:pointer}.qk-tabs button[aria-pressed=true]{background:#12305C;color:#fff;border-color:#12305C}'
       '.qk-ol{list-style:none;margin:0;padding:0}.qk-ol li{display:flex;gap:10px;align-items:flex-start;padding:10px 2px;border-top:1px solid #E3E7EE;cursor:pointer}'
       '.qk-m{flex:none;width:46px;height:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;color:#fff}'
       '.qk-ol li>div{min-width:0}.qk-ol b{display:block;font-size:14.5px;color:#12305C;overflow-wrap:anywhere}.qk-ol small{display:block;font-size:12.5px;color:#5B6B82}'
       '.qk-tsu{display:inline-block;background:#FDECEC;color:#B42318;font-size:11.5px;font-weight:800;border-radius:6px;padding:1px 6px;margin-left:4px}'
       '.qk-tbl{width:100%;border-collapse:collapse;font-size:13.5px}.qk-tbl th,.qk-tbl td{padding:7px 5px;border-bottom:1px solid #E3E7EE;text-align:left;vertical-align:top}.qk-tbl td:nth-child(3),.qk-tbl td:nth-child(4),.qk-tbl th:nth-child(3),.qk-tbl th:nth-child(4){text-align:right;white-space:nowrap}'
       '.qk-tbl td:first-child{white-space:nowrap;font-variant-numeric:tabular-nums}.qk-tbl td:nth-child(2){overflow-wrap:anywhere}.qk-tbl thead th{font-size:12px;color:#5B6B82}</style>')


def build(cc):
    lang, center, zoom, bbox, nm, (agency, aurl) = C[cc]
    t = T[lang]
    F = lambda s: s.replace('{n}', nm).replace('{a}', agency).replace('{s}', SNAP)
    title, desc = F(t['title']), F(t['desc'])
    mine = [q for q in Q if inb(q, bbox)]
    cnt = F(t['cnt']).replace('{c}', str(len(mine))) if mine else F(t['cnt0'])
    top = sorted(mine if bbox and len(mine) >= 5 else Q, key=lambda q: -q[3])[:15]
    rows = ''.join(f'<tr><td>{time.strftime("%m-%d %H:%M", time.gmtime(q[4] / 1000))}</td><td>{E(q[5])}{"<span class=qk-tsu>tsunami</span>" if q[6] else ""}</td>'
                   f'<td><b>{num(q[3], lang)}</b></td><td>{num(q[2], lang, 0)} km</td></tr>' for q in top)
    faq = [(F(a), F(b)) for a, b in t['faq']]
    url = f'{B}/{cc}/{t["slug"]}'
    body = (f'<header class="hero"><div class="in"><span class="year">USGS · live</span><h1>{t["h1"]}</h1><p>{E(t["sub"])}</p></div></header>\n<main class="wrap">\n'
            '<section class="card"><div class="qk-tools">'
            f'<button type="button" id="qk-loc">{E(t["loc"])}</button><button type="button" id="qk-near" aria-pressed="false">{E(t["near"])}</button><span class="qk-sep"></span>'
            f'<button type="button" data-mag="2.5" aria-pressed="false">{E(t["m25"])}</button><button type="button" data-mag="4.5" aria-pressed="true">{E(t["m45"])}</button><button type="button" data-mag="significant" aria-pressed="false">{E(t["sig"])}</button><span class="qk-sep"></span>'
            f'<button type="button" data-per="day" aria-pressed="false">{E(t["d1"])}</button><button type="button" data-per="week" aria-pressed="true">{E(t["d7"])}</button><button type="button" data-per="month" aria-pressed="false">{E(t["d30"])}</button></div>'
            '<div id="qk-map" role="region" aria-label="map"></div>'
            f'<div class="qk-leg"><span><i style="background:#D7263D"></i>{E(t["legend"][0])}</span><span><i style="background:#F28C28"></i>{E(t["legend"][1])}</span><span><i style="background:#E9C46A"></i>{E(t["legend"][2])}</span></div>'
            f'<p class="qk-note" id="qk-live"></p>'
            f'<h2 style="margin-top:14px">{E(t["list"])}</h2><div class="qk-tabs"><button type="button" data-sort="time" aria-pressed="true">{E(t["list"])}</button><button type="button" data-sort="near" aria-pressed="false">{E(t["nearest"])}</button><button type="button" data-sort="mag" aria-pressed="false">{E(t["strongest"])}</button></div>'
            '<ol class="qk-ol" id="qk-list"></ol></section>\n'
            f'<section class="card"><h2>{E(t["weekT"])}</h2><p>{E(cnt)}</p><div style="overflow-x:auto"><table class="qk-tbl"><thead><tr>' + ''.join(f'<th>{E(x)}</th>' for x in t['th']) + f'</tr></thead><tbody>{rows}</tbody></table></div>'
            f'<p class="qk-note">{E(F(t["src"]))} <a href="{aurl}" target="_blank" rel="noopener">{E(agency)}</a></p></section>\n'
            + faq_html(faq) + '\n</main>')
    cfg = {'cc': cc, 'center': center, 'zoom': zoom, 'lang': lang, 't': {k: t[k] for k in ('away', 'depth', 'tsu', 'felt', 'none', 'live')}, 'snap': [q for q in Q]}
    return build_page(SITE, cc, t['slug'], title, desc, body,
                      ld=[app_ld(title.split(' – ')[0], url, 'ReferenceApplication', {"dateModified": time.strftime('%Y-%m-%d')}), faq_ld(faq)],
                      head_extra='<link rel="stylesheet" href="/assets/leaflet/leaflet.css">' + CSS,
                      tail_extra=f'<script>window.QKCFG={json.dumps(cfg, ensure_ascii=False, separators=(",", ":"))};</script><script src="/assets/leaflet/leaflet.js"></script><script src="/assets/quake.js" defer></script>',
                      marker='data-hl-quake')


made = [build(cc) for cc in C]
register(SITE, made)
print('quake pages:', sum(1 for m in made if m), 'snapshot', len(Q), SNAP)
