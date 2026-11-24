"""Argentina daily data pages — built at deploy from data-ar (BCRA API v4), numbers written into the HTML.
Pages: /arg/uva-hoy.html, /arg/icl-hoy.html, /arg/inflacion-2026.html (acumulada), /arg/inflacion-<mes>-<año>.html (one per month).
Each page has its own design. Adds sitemap entries and links on /arg/index.html.
Usage: python3 build/ar/gen_ar_pages.py _site"""
import datetime as dt, html, json, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
B = 'https://honglifecalc.com'
D = json.load(open(os.path.join(SITE, 'arg-data', 'bcra.json')))
SHELL = open(os.path.join(SITE, 'arg', 'calculadora-vacaciones.html'), encoding='utf-8').read()
E = lambda s: html.escape(str(s), quote=True)
TODAY = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).date()
T = TODAY.isoformat()
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
DIA = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']


def n(x, d=2):
    s = f'{x:,.{d}f}'
    return s.replace(',', '§').replace('.', ',').replace('§', '.')


def fd(s):
    y, m, d = s.split('-'); return f'{d}/{m}/{y}'


def flong(s):
    x = dt.date.fromisoformat(s); return f'{DIA[x.weekday()]} {x.day} de {MES[x.month - 1]} de {x.year}'


def at(series, day):
    v = None
    for f, x in series:
        if f <= day: v = (f, x)
        else: break
    return v


def spark(pts, w=640, h=150, color='#F59E0B', fill='rgba(245,158,11,.14)', pad=8):
    ys = [p[1] for p in pts]; lo, hi = min(ys), max(ys); rng = (hi - lo) or 1
    xy = [(pad + i * (w - 2 * pad) / max(1, len(pts) - 1), h - pad - (p[1] - lo) / rng * (h - 2 * pad)) for i, p in enumerate(pts)]
    path = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in xy)
    area = path + f' L{xy[-1][0]:.1f},{h - pad} L{xy[0][0]:.1f},{h - pad} Z'
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" aria-label="Evolución" style="width:100%;height:{h}px;display:block">'
            f'<path d="{area}" fill="{fill}"/><path d="{path}" fill="none" stroke="{color}" stroke-width="2.5" vector-effect="non-scaling-stroke"/>'
            f'<circle cx="{xy[-1][0]:.1f}" cy="{xy[-1][1]:.1f}" r="4" fill="{color}"/></svg>')


def page(path, title, desc, h1, kicker, lead, css, body, faq, sources, crumb='Argentina'):
    url = B + path
    s = SHELL
    s = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(title), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + E(h1), s, count=1)
    s = s.replace(B + '/arg/calculadora-vacaciones.html', url)
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": h1, "url": url, "description": desc, "inLanguage": "es-AR",
           "dateModified": T},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": B + "/"},
              {"@type": "ListItem", "position": 2, "name": crumb, "item": B + "/arg/"},
              {"@type": "ListItem", "position": 3, "name": h1, "item": url}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in faq]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld) + css + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', f'<header class="hero"><div class="in"><span class="year">{kicker}</span><h1>{h1}</h1><p>{lead}</p></div></header>', s, count=1, flags=re.S)
    faqh = '<h2 id="faq">Preguntas frecuentes</h2>' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in faq)
    note = f'<p class="note">Fuentes (actualizado {fd(T)}): ' + '; '.join(f'<a href="{u}" rel="nofollow">{t}</a>' for t, u in sources) + '.</p>'
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: body, s, count=1, flags=re.S)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + faqh + note + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", '', s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    p = os.path.join(SITE, path.lstrip('/'))
    open(p, 'w', encoding='utf-8').write(s)
    return path


made = []

# ───────────── UVA hoy (LED board) ─────────────
uva = D['uva']; u0 = at(uva, T)
fut = [x for x in uva if x[0] > T][:7]
u30 = at(uva, (TODAY - dt.timedelta(days=30)).isoformat()); u365 = at(uva, (TODAY - dt.timedelta(days=365)).isoformat())
v30 = (u0[1] / u30[1] - 1) * 100 if u30 else None; v365 = (u0[1] / u365[1] - 1) * 100 if u365 else None
CSS_U = '''<style id="uv-css">
section.uv{display:block;min-width:0;max-width:100%}
.uv-board{background-color:#0E1726;border-radius:20px;padding:18px 16px;color:#FDE68A;box-shadow:inset 0 0 0 2px #1E293B,0 10px 30px rgba(14,23,38,.25)}
.uv-board small{display:block;color:#94A3B8;font-size:12.5px;letter-spacing:.06em;text-transform:uppercase}
.uv-led{font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;font-size:46px;font-weight:800;line-height:1.1;margin:6px 0 4px;color:#FCD34D;text-shadow:0 0 12px rgba(252,211,77,.55);overflow-wrap:anywhere}
.uv-led span{color:#FDE68A;opacity:.6;font-size:.6em;margin-right:6px}
.uv-sub{font-size:14px;color:#CBD5E1}
.uv-days{display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:6px;margin-top:14px}
.uv-days div{background-color:#16233A;border:1px solid #243552;border-radius:10px;padding:7px 8px;min-width:0}
.uv-days b{display:block;font-family:Consolas,monospace;color:#FDE68A;font-size:14px}.uv-days i{font-style:normal;font-size:11.5px;color:#94A3B8}
.uv-ans{font-size:16.5px;line-height:1.6;margin:14px 2px}
.uv-card{background-color:#fff;border:1px solid #E5E7EB;border-radius:16px;padding:14px;margin:12px 0;min-width:0}
.uv-card h2{font-size:18px;margin:0 0 10px}
.uv-kpi{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.uv-kpi div{background-color:#FFFBEB;border:1px solid #FDE68A;border-radius:12px;padding:9px 10px;min-width:0}.uv-kpi small{display:block;font-size:11.5px;color:#92400E}.uv-kpi b{font-size:18px;color:#78350F;overflow-wrap:anywhere}
.uv-conv{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:8px;align-items:end}
.uv-conv label{display:block;font-size:13px;font-weight:700;min-width:0}.uv-conv input{width:100%;box-sizing:border-box;font:inherit;font-size:17px;padding:10px;border:1px solid #D1D5DB;border-radius:10px;min-width:0;margin-top:4px}
.uv-conv span{font-size:22px;padding-bottom:8px;color:#9CA3AF}
.uv-tb{width:100%;border-collapse:collapse;font-size:14px}.uv-tb td,.uv-tb th{padding:6px 4px;border-bottom:1px solid #F1F5F9;text-align:right}.uv-tb td:first-child,.uv-tb th:first-child{text-align:left}
@media(max-width:560px){.uv-led{font-size:36px}.uv-kpi{grid-template-columns:1fr 1fr}.uv-kpi div:last-child{grid-column:1/-1}.uv-conv{grid-template-columns:1fr}.uv-conv span{display:none}}
</style>'''
days_html = ''.join(f'<div><i>{fd(f)[:5]} · {DIA[dt.date.fromisoformat(f).weekday()][:3]}</i><b>{n(v)}</b></div>' for f, v in fut)
last30 = [x for x in uva if (TODAY - dt.timedelta(days=90)).isoformat() <= x[0] <= T]
tbl = ''.join(f'<tr><td>{fd(f)}</td><td>$ {n(v)}</td></tr>' for f, v in reversed([x for x in uva if x[0] <= T][-15:]))
body_u = (f'<section class="app uv" id="calc"><div class="uv-board"><small>Valor UVA hoy · {fd(u0[0])}</small>'
          f'<div class="uv-led"><span>$</span>{n(u0[1])}</div><div class="uv-sub">Unidad de Valor Adquisitivo · BCRA (base 31/3/2016 = 14,05)</div>'
          + (f'<div class="uv-days">{days_html}</div>' if fut else '') + '</div>'
          f'<p class="uv-ans">El valor de la <b>UVA hoy</b>, {flong(u0[0])}, es <b>$ {n(u0[1])}</b> según el Banco Central.'
          + (f' Mañana será <b>$ {n(fut[0][1])}</b>.' if fut else '') + (f' En los últimos 30 días subió <b>{n(v30, 1)} %</b>' if v30 is not None else '')
          + (f' y en un año <b>{n(v365, 1)} %</b>.' if v365 is not None else '.') + '</p>'
          f'<div class="uv-card"><h2>Convertir UVA ↔ pesos (valor de hoy)</h2><div class="uv-conv"><label>UVA<input id="ua" inputmode="decimal" value="100"></label><span>⇄</span><label>Pesos ($)<input id="up" inputmode="decimal"></label></div>'
          f'<p style="font-size:13px;color:#6B7280;margin:8px 0 0">Ej.: una cuota de crédito hipotecario UVA de 300 UVA hoy son $ {n(300 * u0[1], 0)}.</p></div>'
          f'<div class="uv-card"><h2>Últimos 90 días</h2>{spark(last30)}<div class="uv-kpi" style="margin-top:10px"><div><small>Hoy</small><b>$ {n(u0[1])}</b></div>'
          f'<div><small>Hace 30 días</small><b>{"+" + n(v30, 1) + " %" if v30 is not None else "—"}</b></div><div><small>Hace 1 año</small><b>{"+" + n(v365, 1) + " %" if v365 is not None else "—"}</b></div></div></div>'
          f'<div class="uv-card"><h2>Valores de los últimos 15 días</h2><table class="uv-tb"><thead><tr><th>Fecha</th><th>UVA</th></tr></thead><tbody>{tbl}</tbody></table></div>'
          f'<p style="font-size:14px">Ver también: <a href="/arg/icl-hoy.html">ICL hoy</a> · <a href="/arg/inflacion-2026.html">Inflación 2026</a> · <a href="/arg/calculadora-alquileres.html">Calculadora de alquileres</a></p>'
          f'<script>(function(){{var V={u0[1]},a=document.getElementById("ua"),p=document.getElementById("up");var N=function(s){{var x=parseFloat(String(s).replace(/\\./g,"").replace(",",".").replace(/[^0-9.]/g,""));return isFinite(x)?x:0}};var F=function(x,d){{return x.toLocaleString("es-AR",{{minimumFractionDigits:d,maximumFractionDigits:d}})}};'
          f'a.addEventListener("input",function(){{p.value=F(N(a.value)*V,2)}});p.addEventListener("input",function(){{a.value=F(N(p.value)/V,4)}});p.value=F(100*V,2)}})();</script></section>')
FAQ_U = [("¿Qué es la UVA?", "La Unidad de Valor Adquisitivo es un índice que publica el Banco Central todos los días. Empezó el 31 de marzo de 2016 con un valor de $ 14,05 y se actualiza por el CER, que sigue a la inflación (IPC del INDEC)."),
         ("¿Por qué ya se conoce la UVA de los próximos días?", "Porque el BCRA calcula la UVA con el CER, que se conoce por adelantado: publica los valores hasta el día 6 del mes siguiente."),
         ("¿Cómo paso una cuota de crédito UVA a pesos?", f"Multiplicá las UVA de la cuota por el valor de la UVA del día de pago. Hoy: 300 UVA × $ {n(u0[1])} = $ {n(300 * u0[1], 0)}."),
         ("¿Cada cuánto se actualiza esta página?", "Todos los días por la mañana (hora de Buenos Aires) con los datos de la API de Estadísticas del BCRA.")]
made.append(page('/arg/uva-hoy.html', f'UVA hoy {fd(u0[0])}: $ {n(u0[1])} | Valor BCRA',
                 f'Valor de la UVA hoy {fd(u0[0])}: $ {n(u0[1])} (BCRA). Valores de los próximos días, conversor UVA a pesos, gráfico y tabla.',
                 'UVA hoy', '🇦🇷 BCRA · actualizado todos los días', 'Valor oficial de la Unidad de Valor Adquisitivo y conversor a pesos.', CSS_U, body_u, FAQ_U,
                 [('BCRA: API de Estadísticas (variable 31, UVA)', 'https://www.bcra.gob.ar/BCRAyVos/Catalogo_de_APIs_banco_central.asp'), ('BCRA: Principales variables', 'https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp')]))

# ───────────── ICL hoy (ruler + mini calculator) ─────────────
icl = D['icl']; i0 = at(icl, T)
CSS_I = '''<style id="ic-css">
section.ic{display:block;min-width:0;max-width:100%}
.ic-top{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;align-items:stretch}
.ic-val{background-color:#EEF6FF;border:2px solid #0B3A5B;border-radius:18px;padding:16px;min-width:0}
.ic-val small{display:block;font-size:13px;font-weight:700;color:#0B3A5B}.ic-val b{display:block;font-size:44px;line-height:1.05;color:#0B3A5B;font-variant-numeric:tabular-nums}
.ic-val span{font-size:13.5px;color:#24475F}
.ic-x{background-color:#0B3A5B;color:#fff;border-radius:18px;padding:16px;display:flex;flex-direction:column;justify-content:center;min-width:0}
.ic-x b{font-size:34px;line-height:1.1}.ic-x span{font-size:13.5px;color:#BFE3FA}
.ic-ruler{position:relative;margin:16px 0 6px;padding:22px 0 0}
.ic-ruler .bar{height:14px;border-radius:7px;background:linear-gradient(90deg,#BFE3FA,#0B3A5B)}
.ic-ruler .tk{position:absolute;top:0;transform:translateX(-50%);font-size:11px;color:#475569;white-space:nowrap}
.ic-ruler .tk:after{content:"";display:block;width:2px;height:22px;background-color:#0B3A5B;margin:2px auto 0}
.ic-ans{font-size:16.5px;line-height:1.6;margin:12px 2px}
.ic-calc{background-color:#fff;border:1px dashed #94A3B8;border-radius:16px;padding:14px;margin:12px 0}
.ic-calc h2{font-size:18px;margin:0 0 10px}.ic-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.ic-row label{font-size:13px;font-weight:700;min-width:0}.ic-row input{width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:10px;border:1px solid #CBD5E1;border-radius:10px;margin-top:4px;min-width:0}
.ic-out{margin-top:10px;font-size:16px;background-color:#F1F5F9;border-radius:12px;padding:10px 12px}
.ic-tb{width:100%;border-collapse:collapse;font-size:14px}.ic-tb td,.ic-tb th{padding:6px 4px;border-bottom:1px solid #E2E8F0;text-align:right}.ic-tb td:first-child,.ic-tb th:first-child{text-align:left}
@media(max-width:560px){.ic-top,.ic-row{grid-template-columns:1fr}.ic-val b{font-size:36px}}
</style>'''
base0 = 1.0  # 30/06/2020
mons = []
d = TODAY.replace(day=1)
for k in range(11, -1, -1):
    y, m = d.year, d.month - k
    while m <= 0: m += 12; y -= 1
    v = at(icl, f'{y}-{m:02d}-01')
    if v: mons.append((f'{y}-{m:02d}-01', v[1]))
lo, hi = mons[0][1], max(i0[1], mons[-1][1])
ticks = ''.join(f'<span class="tk" style="left:{(v - lo) / ((hi - lo) or 1) * 96 + 2:.1f}%">{MES[int(f[5:7]) - 1][:3]}</span>' for f, v in mons[::3])
y1 = at(icl, (TODAY - dt.timedelta(days=365)).isoformat())
mtbl = ''.join(f'<tr><td>1/{f[5:7]}/{f[:4]}</td><td>{n(v)}</td></tr>' for f, v in reversed(mons))
ICLJS = json.dumps([[f, v] for f, v in icl if f <= T], separators=(',', ':'))
body_i = (f'<section class="app ic" id="calc"><div class="ic-top"><div class="ic-val"><small>ICL hoy · {fd(i0[0])}</small><b>{n(i0[1])}</b><span>Índice para Contratos de Locación · BCRA</span></div>'
          f'<div class="ic-x"><b>× {n(i0[1] / base0, 1)}</b><span>veces desde el 30/06/2020 (base = 1)</span>'
          + (f'<span style="margin-top:6px">+{n((i0[1] / y1[1] - 1) * 100, 1)} % en 12 meses</span>' if y1 else '') + '</div></div>'
          f'<div class="ic-ruler" aria-hidden="true">{ticks}<div class="bar"></div></div>'
          f'<p class="ic-ans">El <b>ICL hoy</b>, {flong(i0[0])}, es <b>{n(i0[1])}</b>. Sirve para actualizar los alquileres de contratos firmados con la Ley 27.551 (julio 2020 – diciembre 2023): nuevo alquiler = alquiler × ICL de hoy ÷ ICL del inicio.</p>'
          f'<div class="ic-calc"><h2>Actualizar un alquiler con el ICL</h2><div class="ic-row"><label>Alquiler ($)<input id="im" inputmode="numeric" value="500.000"></label>'
          f'<label>Fecha de inicio o último ajuste<input id="idt" type="date" value="{(TODAY - dt.timedelta(days=365)).isoformat()}" min="{icl[0][0]}" max="{T}"></label></div><div class="ic-out" id="io"></div>'
          f'<p style="font-size:13px;color:#64748B;margin:8px 0 0">Para todo el contrato (ajustes cada 3, 4, 6 o 12 meses, o IPC) usá la <a href="/arg/calculadora-alquileres.html">calculadora de alquileres</a>.</p></div>'
          f'<div class="ic-calc" style="border-style:solid;border-color:#E2E8F0"><h2>ICL el día 1 de cada mes</h2><table class="ic-tb"><thead><tr><th>Fecha</th><th>ICL</th></tr></thead><tbody>{mtbl}</tbody></table></div>'
          f'<p style="font-size:14px">Ver también: <a href="/arg/uva-hoy.html">UVA hoy</a> · <a href="/arg/inflacion-2026.html">Inflación 2026</a></p>'
          '<script>(function(){var S=' + ICLJS + ',$=function(i){return document.getElementById(i)};function at(d){var v=null;for(var i=0;i<S.length;i++){if(S[i][0]<=d)v=S[i];else break}return v}'
          'var N=function(s){var x=parseFloat(String(s).replace(/\\./g,"").replace(",",".").replace(/[^0-9.]/g,""));return isFinite(x)?x:0};'
          'function go(){var m=N($("im").value),a=at($("idt").value),b=S[S.length-1];if(!m||!a){$("io").textContent="Elegí una fecha desde el "+S[0][0].split("-").reverse().join("/")+".";return}var f=b[1]/a[1];'
          '$("io").innerHTML="ICL "+a[0].split("-").reverse().join("/")+": <b>"+a[1].toLocaleString("es-AR")+"</b> → hoy: <b>"+b[1].toLocaleString("es-AR")+"</b><br>Aumento: <b>+"+((f-1)*100).toLocaleString("es-AR",{maximumFractionDigits:2})+" %</b> · Nuevo alquiler: <b>$ "+Math.round(m*f).toLocaleString("es-AR")+"</b>"}'
          '$("im").addEventListener("input",go);$("idt").addEventListener("input",go);go()})();</script></section>')
FAQ_I = [("¿Qué es el ICL?", "El Índice para Contratos de Locación lo publica el BCRA todos los días desde el 1/7/2020 (base 30/6/2020 = 1). Se arma en partes iguales con la variación del CER (inflación) y del RIPTE (salarios)."),
         ("¿Cómo se calcula el aumento del alquiler con el ICL?", f"Se divide el ICL del día del ajuste por el ICL del inicio del contrato y se multiplica el alquiler. Ej.: 500.000 × {n(i0[1])} ÷ ICL de hace un año."),
         ("¿El ICL sigue vigente?", "El DNU 70/2023 derogó la Ley 27.551 desde el 29/12/2023. Los contratos firmados antes con ICL lo siguen usando hasta que terminen; en los nuevos, las partes eligen el índice."),
         ("¿Cada cuánto se actualiza esta página?", "Todos los días por la mañana con la API de Estadísticas del BCRA (variable 40).")]
made.append(page('/arg/icl-hoy.html', f'ICL hoy {fd(i0[0])}: {n(i0[1])} | Índice de alquileres BCRA',
                 f'ICL hoy {fd(i0[0])}: {n(i0[1])} (BCRA). Índice para Contratos de Locación, calculadora de aumento de alquiler y valores de cada mes.',
                 'ICL hoy', '🇦🇷 BCRA · actualizado todos los días', 'Índice para Contratos de Locación y aumento de tu alquiler.', CSS_I, body_i, FAQ_I,
                 [('BCRA: API de Estadísticas (variable 40, ICL)', 'https://www.bcra.gob.ar/BCRAyVos/Catalogo_de_APIs_banco_central.asp'), ('BCRA: Índice para Contratos de Locación', 'https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp')]))

# ───────────── Inflación (receipt design) ─────────────
ipc = [(f[:7], v) for f, v in D['ipc_m']]
ipa = {f[:7]: v for f, v in D.get('ipc_a', [])}
IM = dict(ipc)
CSS_P = '''<style id="ip-css">
section.ip{display:block;min-width:0;max-width:100%}
.ip-wrap{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:16px;align-items:start}
.ip-ticket{background-color:#FFFEF8;border-radius:4px;padding:18px 16px 22px;font-family:"Courier New",Consolas,monospace;color:#1F2937;box-shadow:0 8px 24px rgba(0,0,0,.08);position:relative;min-width:0}
.ip-ticket:after{content:"";position:absolute;left:0;right:0;bottom:-10px;height:10px;background:radial-gradient(circle at 6px 0,transparent 6px,#FFFEF8 6.5px) 0 0/12px 10px repeat-x}
.ip-ticket h2{font-size:15px;text-align:center;margin:0 0 4px;letter-spacing:.08em}.ip-ticket .c{text-align:center;font-size:12px;color:#6B7280;margin:0 0 10px}
.ip-l{display:flex;justify-content:space-between;gap:8px;border-bottom:1px dashed #D1D5DB;padding:7px 0;font-size:14px}.ip-l b{font-size:15px;white-space:nowrap}
.ip-tot{display:flex;justify-content:space-between;gap:8px;font-size:22px;font-weight:800;padding:10px 0 2px}
.ip-bars{background-color:#fff;border:1px solid #E5E7EB;border-radius:16px;padding:12px;min-width:0}
.ip-bars h2{font-size:17px;margin:0 0 8px}
.ip-b{display:grid;grid-template-columns:4.2em minmax(0,1fr) 3.6em;gap:8px;align-items:center;font-size:13px;margin:4px 0}
.ip-b i{display:block;height:14px;border-radius:7px;background-color:#93C5FD}.ip-b.on i{background-color:#DC2626}.ip-b.on{font-weight:800}
.ip-b a{color:inherit}.ip-b em{font-style:normal;text-align:right}
.ip-ans{font-size:16.5px;line-height:1.6;margin:0 2px 12px}
.ip-calc{margin-top:12px;background-color:#F8FAFC;border:1px solid #E2E8F0;border-radius:14px;padding:12px}
.ip-calc input{font:inherit;font-size:16px;padding:9px;border:1px solid #CBD5E1;border-radius:10px;width:100%;box-sizing:border-box;margin-top:4px}
.ip-cal{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:6px;margin:10px 0}
.ip-cal a,.ip-cal span{display:block;border-radius:12px;padding:10px 4px;text-align:center;font-size:12.5px;text-decoration:none;color:#111827;min-width:0}
.ip-cal b{display:block;font-size:16px}
@media(max-width:760px){.ip-wrap{grid-template-columns:minmax(0,1fr)}.ip-cal{grid-template-columns:repeat(3,minmax(0,1fr))}}
</style>'''


def acum(year, upto):
    p = 1
    for m in range(1, upto + 1):
        k = f'{year}-{m:02d}'
        if k not in IM: return None
        p *= 1 + IM[k] / 100
    return (p - 1) * 100


def slug(k):
    return f'/arg/inflacion-{MES[int(k[5:]) - 1]}-{k[:4]}.html'


last = ipc[-1][0]
months = [k for k, _ in ipc if k >= '2025-01']
for k in months:
    y, m = int(k[:4]), int(k[5:]); v = IM[k]; ac = acum(y, m); ia = ipa.get(k)
    prev = f'{y}-{m - 1:02d}' if m > 1 else f'{y - 1}-12'
    win = [x for x in ipc if x[0] <= k][-12:]; mx = max(x[1] for x in win) or 1
    bars = ''.join(f'<div class="ip-b{" on" if kk == k else ""}"><span>{MES[int(kk[5:]) - 1][:3]} {kk[2:4]}</span><i style="width:{max(3, vv / mx * 100):.0f}%"></i><em>{n(vv, 1)} %</em></div>' for kk, vv in win)
    nm = f'{MES[m - 1]} {y}'
    body = (f'<section class="app ip" id="calc"><p class="ip-ans">La <b>inflación de {nm}</b> fue <b>{n(v, 1)} %</b> según el IPC del INDEC'
            + (f' ({"más" if v > IM.get(prev, v) else "menos" if v < IM.get(prev, v) else "igual"} que el {n(IM[prev], 1)} % de {MES[int(prev[5:]) - 1]})' if prev in IM else '')
            + (f'. En los últimos 12 meses fue <b>{n(ia, 1)} %</b>' if ia is not None else '') + (f' y en lo que va de {y}, <b>{n(ac, 1)} %</b>.' if ac is not None else '.') + '</p>'
            f'<div class="ip-wrap"><div class="ip-ticket"><h2>TICKET IPC</h2><p class="c">INDEC · {nm.upper()}</p>'
            f'<div class="ip-l"><span>Inflación mensual</span><b>{n(v, 1)} %</b></div>'
            + (f'<div class="ip-l"><span>Interanual</span><b>{n(ia, 1)} %</b></div>' if ia is not None else '')
            + (f'<div class="ip-l"><span>Acumulada {y}</span><b>{n(ac, 1)} %</b></div>' if ac is not None else '')
            + (f'<div class="ip-l"><span>Mes anterior</span><b>{n(IM[prev], 1)} %</b></div>' if prev in IM else '')
            + f'<div class="ip-tot"><span>$ 100.000</span><span>→</span></div><div class="ip-l" style="border:0"><span>Hoy cuesta</span><b>$ {n(100000 * (1 + (ac or v) / 100), 0)}</b></div>'
            f'<p class="c" style="margin-top:8px">*lo que valía $ 100.000 en dic {y - 1 if ac is not None else ""}</p></div>'
            f'<div class="ip-bars"><h2>Inflación mes a mes</h2>{bars}'
            f'<div class="ip-calc"><label style="font-size:13px;font-weight:700">Monto a actualizar ($)<input id="pm" inputmode="numeric" value="100.000"></label><p id="po" style="margin:8px 0 0;font-size:15px"></p></div></div></div>'
            f'<p style="font-size:14px;margin-top:14px">Ver: <a href="/arg/inflacion-2026.html">inflación acumulada 2026</a> · <a href="/arg/calculadora-alquileres.html">aumento de alquiler por IPC</a> · <a href="/arg/uva-hoy.html">UVA hoy</a></p>'
            f'<script>(function(){{var f={(1 + v / 100):.6f},a={(1 + (ac or 0) / 100):.6f},i=document.getElementById("pm"),o=document.getElementById("po");var N=function(s){{var x=parseFloat(String(s).replace(/\\./g,"").replace(",",".").replace(/[^0-9.]/g,""));return isFinite(x)?x:0}};'
            f'function g(){{var m=N(i.value);o.innerHTML="Con la inflación de {nm}: <b>$ "+Math.round(m*f).toLocaleString("es-AR")+"</b>"+(a>1?"<br>Con la acumulada de {y}: <b>$ "+Math.round(m*a).toLocaleString("es-AR")+"</b>":"")}}i.addEventListener("input",g);g()}})();</script></section>')
    faq = [(f'¿Cuánto fue la inflación de {nm}?', f'{n(v, 1)} % mensual según el Índice de Precios al Consumidor (IPC) del INDEC.' + (f' La interanual fue {n(ia, 1)} %.' if ia is not None else '')),
           (f'¿Cuál es la inflación acumulada de {y} hasta {MES[m - 1]}?', (f'{n(ac, 1)} %: se multiplican las variaciones mensuales de enero a {MES[m - 1]} de {y}.' if ac is not None else 'Falta algún mes del año en los datos.')),
           ('¿Cómo uso el IPC para actualizar un alquiler?', 'Multiplicá (1 + IPC de cada mes del período) y restá 1. La <a href="/arg/calculadora-alquileres.html">calculadora de alquileres</a> lo hace con los datos oficiales.')]
    made.append(page(slug(k), f'Inflación {nm}: {n(v, 1)} % (IPC INDEC)', f'La inflación de {nm} fue {n(v, 1)} % (IPC INDEC).' + (f' Interanual {n(ia, 1)} %.' if ia is not None else '') + (f' Acumulada {y}: {n(ac, 1)} %.' if ac is not None else ''),
                     f'Inflación {nm}: {n(v, 1)} %', '🇦🇷 IPC · INDEC', f'Inflación mensual, interanual y acumulada de {nm}.', CSS_P, body, faq,
                     [('INDEC: Índice de precios al consumidor', 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31'), ('BCRA: API de Estadísticas (variables 27 y 28)', 'https://www.bcra.gob.ar/BCRAyVos/Catalogo_de_APIs_banco_central.asp')]))

# hub: inflación acumulada del año en curso
Y = int(last[:4]); lm = int(last[5:]); acY = acum(Y, lm)
cal = ''
for m in range(1, 13):
    k = f'{Y}-{m:02d}'
    if k in IM:
        v = IM[k]; a = min(1, v / 6)
        cal += f'<a href="{slug(k)}" style="background-color:rgba(220,38,38,{0.12 + 0.5 * a:.2f})">{MES[m - 1][:3]}<b>{n(v, 1)} %</b></a>'
    else:
        cal += f'<span style="background-color:#F3F4F6;color:#9CA3AF">{MES[m - 1][:3]}<b>—</b></span>'
rows = ''.join(f'<div class="ip-l"><span><a href="{slug(k)}">{MES[int(k[5:]) - 1].capitalize()}</a></span><b>{n(IM[k], 1)} % · acum. {n(acum(Y, int(k[5:])), 1)} %</b></div>' for k in [f'{Y}-{m:02d}' for m in range(1, lm + 1)])
body_h = (f'<section class="app ip" id="calc"><p class="ip-ans">La <b>inflación acumulada de {Y}</b> hasta {MES[lm - 1]} es <b>{n(acY, 1)} %</b> (IPC INDEC). La de {MES[lm - 1]} fue {n(IM[last], 1)} %'
          + (f' y la interanual {n(ipa[last], 1)} %' if last in ipa else '') + '.</p>'
          f'<div class="ip-cal">{cal}</div><div class="ip-wrap"><div class="ip-ticket"><h2>{Y}</h2><p class="c">INFLACIÓN MES A MES</p>{rows}<div class="ip-tot"><span>Acumulada</span><span>{n(acY, 1)} %</span></div></div>'
          f'<div class="ip-bars"><h2>Qué significa</h2><p style="font-size:15px">Lo que en diciembre de {Y - 1} costaba <b>$ 100.000</b>, en {MES[lm - 1]} de {Y} cuesta en promedio <b>$ {n(100000 * (1 + acY / 100), 0)}</b>.</p>'
          f'<p style="font-size:14px">Tocá un mes del calendario para ver el detalle. El INDEC publica cada mes a mediados del mes siguiente; esta página se actualiza sola.</p></div></div></section>')
FAQ_H = [(f'¿Cuál es la inflación acumulada de {Y}?', f'{n(acY, 1)} % de enero a {MES[lm - 1]} de {Y}, según el IPC del INDEC.'),
         ('¿Cómo se calcula la inflación acumulada?', 'Se multiplican (1 + variación mensual) de cada mes del año y se resta 1. No se suman los porcentajes.')]
made.append(page(f'/arg/inflacion-{Y}.html', f'Inflación acumulada {Y}: {n(acY, 1)} % (enero–{MES[lm - 1]}, INDEC)', f'Inflación acumulada {Y} en Argentina: {n(acY, 1)} % hasta {MES[lm - 1]}. Mes a mes, interanual y calendario del IPC del INDEC.',
                 f'Inflación acumulada {Y}', '🇦🇷 IPC · INDEC', f'Mes a mes y acumulada en {Y}.', CSS_P, body_h, FAQ_H,
                 [('INDEC: Índice de precios al consumidor', 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31')]))

# sitemap + hub links
sm = os.path.join(SITE, 'sitemap.xml')
if os.path.isfile(sm):
    s = open(sm, encoding='utf-8').read(); add = 0
    for p in made:
        if f'<loc>{B}{p}</loc>' not in s:
            s = s.replace('</urlset>', f'  <url><loc>{B}{p}</loc><lastmod>{T}</lastmod></url>\n</urlset>', 1); add += 1
        else:
            s = re.sub(r'(<loc>' + re.escape(B + p) + r'</loc><lastmod>)[^<]*', lambda m: m.group(1) + T, s)
    open(sm, 'w', encoding='utf-8').write(s)
hp = os.path.join(SITE, 'arg', 'index.html')
if os.path.isfile(hp):
    h = open(hp, encoding='utf-8').read()
    if 'id="ar-live"' not in h:
        box = ('<section class="card" id="ar-live" style="margin:14px 0"><h2>Datos de hoy (BCRA · INDEC)</h2><ul style="display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0;margin:0">'
               f'<li><a href="/arg/uva-hoy.html">UVA hoy: $ {n(u0[1])}</a></li><li><a href="/arg/icl-hoy.html">ICL hoy: {n(i0[1])}</a></li>'
               f'<li><a href="{slug(last)}">Inflación {MES[int(last[5:]) - 1]} {last[:4]}: {n(IM[last], 1)} %</a></li><li><a href="/arg/inflacion-{Y}.html">Inflación acumulada {Y}: {n(acY, 1)} %</a></li>'
               '<li><a href="/arg/calculadora-alquileres.html">Calculadora de alquileres ICL e IPC</a></li></ul></section>')
        h2 = re.sub(r'(<main[^>]*>)', lambda m: m.group(1) + box, h, count=1)
        if h2 != h: open(hp, 'w', encoding='utf-8').write(h2)
print('AR pages:', len(made), made[:4], '…')
