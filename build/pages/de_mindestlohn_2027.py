"""DE: Mindestlohn 2027 — 14,60 € ab 1.1.2027 (2026: 13,90 €), Minijob-Grenze 633 € (2026: 603 €), source: Bundesregierung.
Own design: Stempelkarte (time card) + history stamps. Shell: /de/stundenlohn-rechner.html. Writes overlay/de/mindestlohn-2027.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table

PATH = '/de/mindestlohn-2027.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Mindestlohn 2027: 14,60 € – Brutto pro Monat & Minijob 633 €'
H1 = 'Mindestlohn 2027: 14,60 Euro'
DESC = ('Mindestlohn 2027: 14,60 € brutto pro Stunde ab 1. Januar 2027 (2026: 13,90 €). Monatslohn bei 10 bis 40 Stunden pro Woche, '
        'Minijob-Grenze 633 €, Rechner für deine Stunden und alle Erhöhungen seit 2015.')
DATE_DE = '25. November 2026'


def eur(x):
    return f'{x:,.2f}'.replace(',', '§').replace('.', ',').replace('§', '.') + ' €'


ROWS = [(h, 14.60 * h * 13 / 3, 13.90 * h * 13 / 3) for h in (10, 20, 30, 35, 38.5, 40)]
HIST = [('1.1.2015', 8.50), ('1.1.2017', 8.84), ('1.1.2019', 9.19), ('1.1.2020', 9.35), ('1.1.2021', 9.50), ('1.7.2021', 9.60), ('1.1.2022', 9.82),
        ('1.7.2022', 10.45), ('1.10.2022', 12.00), ('1.1.2024', 12.41), ('1.1.2025', 12.82), ('1.1.2026', 13.90), ('1.1.2027', 14.60)]

CSS = '''<style id="ml-css">
section.app.ml{display:block!important;grid-template-columns:none!important;min-width:0;max-width:100%}
.ml-ans{font-size:17px;line-height:1.6;margin:4px 2px 14px}
.ml-grid{display:grid;grid-template-columns:minmax(0,320px) minmax(0,1fr);gap:16px;align-items:start}
.ml-card{background-color:#F7F3E8;border:1px solid #D8CFB6;border-radius:6px;padding:14px 14px 10px;font-family:"Courier New",Consolas,monospace;color:#2A2418;position:relative;min-width:0}
.ml-card:before{content:"";position:absolute;left:50%;top:-9px;width:46px;height:18px;margin-left:-23px;border-radius:0 0 10px 10px;background-color:#fff;border:1px solid #D8CFB6;border-top:0}
.ml-card h2{font-size:15px;letter-spacing:.12em;text-align:center;margin:6px 0 2px}.ml-card .s{font-size:11.5px;text-align:center;color:#7A6E55;margin:0 0 10px}
.ml-big{text-align:center;border:2px solid #B91C1C;color:#B91C1C;border-radius:8px;padding:8px 4px;margin:6px 6px 12px;transform:rotate(-2deg);font-weight:900}
.ml-big b{display:block;font-size:38px;line-height:1.05}.ml-big span{font-size:12px;letter-spacing:.08em}
.ml-row{display:grid;grid-template-columns:4.2em minmax(0,1fr) minmax(0,1fr);gap:6px;border-top:1px dashed #CBBF9F;padding:6px 0;font-size:13.5px;align-items:center}
.ml-row.h{font-weight:700;font-size:11.5px;color:#7A6E55;border-top:0}
.ml-row em{font-style:normal;text-align:right}.ml-row b{text-align:right}
.ml-calc{background-color:#fff;border:1px solid #E5E7EB;border-radius:16px;padding:14px;min-width:0}
.ml-calc h2{font-size:18px;margin:0 0 10px}
.ml-seg{display:flex;gap:6px;margin-bottom:10px}.ml-seg label{flex:1;text-align:center;border:1px solid #D1D5DB;border-radius:999px;padding:7px 4px;font-size:14px;cursor:pointer;position:relative;overflow:hidden}
.ml-seg input{position:absolute;opacity:0;width:1px;height:1px;left:0;top:0}.ml-seg label:has(input:checked){background-color:#111827;color:#fff;border-color:#111827}
.ml-in{display:block;font-size:13px;font-weight:700}.ml-in input{display:block;width:100%;box-sizing:border-box;font:inherit;font-size:18px;padding:10px;border:1px solid #D1D5DB;border-radius:10px;margin-top:4px}
.ml-out{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:12px}
.ml-out div{border-radius:12px;padding:10px;min-width:0}.ml-out .a{background-color:#F3F4F6}.ml-out .b{background-color:#FEF2F2;border:1px solid #FECACA}
.ml-out small{display:block;font-size:12px;color:#6B7280}.ml-out b{display:block;font-size:20px;overflow-wrap:anywhere}
.ml-note{font-size:13.5px;margin-top:10px;padding:10px 12px;border-radius:12px;background-color:#FFFBEB;border:1px solid #FDE68A}
.ml-stamps{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.ml-stamps div{border:2px solid #94A3B8;border-radius:10px;padding:6px 9px;text-align:center;font-size:11.5px;color:#475569;transform:rotate(var(--r));min-width:72px}
.ml-stamps div b{display:block;font-size:15px;color:#0F172A}.ml-stamps div.now{border-color:#B91C1C;color:#B91C1C}.ml-stamps div.now b{color:#B91C1C}
@media(max-width:760px){.ml-grid{grid-template-columns:minmax(0,1fr)}}
@media(max-width:420px){.ml-out{grid-template-columns:1fr}}
</style>'''

rows = ''.join(f'<div class="ml-row"><span>{str(h).replace(".", ",")} h</span><em>{eur(o)}</em><b>{eur(n)}</b></div>' for h, n, o in ROWS)
stamps = ''.join(f'<div class="{"now" if d == "1.1.2027" else ""}" style="--r:{(-3, 2, -1, 3, -2, 1)[i % 6]}deg">{d}<b>{eur(v)}</b></div>' for i, (d, v) in enumerate(HIST))
APP = f'''<section class="app ml" id="calc"><p class="ml-ans">Der <b>Mindestlohn 2027</b> beträgt <b>14,60 € brutto pro Stunde</b> ab dem 1. Januar 2027 – 70 Cent bzw. <b>5,0 % mehr</b> als 2026 (13,90 €). Bei 40 Stunden pro Woche sind das <b>{eur(14.6 * 40 * 13 / 3)} brutto im Monat</b>. Die Minijob-Grenze steigt auf <b>633 €</b>.</p>
<div class="ml-grid"><div class="ml-card"><h2>STEMPELKARTE</h2><p class="s">MINDESTLOHN · DEUTSCHLAND</p><div class="ml-big"><b>14,60 €</b><span>PRO STUNDE · AB 1.1.2027</span></div>
<div class="ml-row h"><span>Std./Woche</span><em>2026</em><b>2027</b></div>{rows}<p class="s" style="margin-top:8px">Monat = Stundenlohn × Wochenstunden × 13 ÷ 3</p></div>
<div class="ml-calc"><h2>Deine Stunden</h2><div class="ml-seg"><label><input type="radio" name="per" value="w" checked>pro Woche</label><label><input type="radio" name="per" value="m">pro Monat</label></div>
<label class="ml-in">Arbeitsstunden<input id="hrs" inputmode="decimal" value="40"></label>
<div class="ml-out"><div class="a"><small>2026 · 13,90 €</small><b id="o26">–</b><small id="y26"></small></div><div class="b"><small>2027 · 14,60 €</small><b id="o27">–</b><small id="y27"></small></div></div>
<div class="ml-note" id="mj"></div>
<p style="font-size:13px;color:#6B7280;margin:10px 0 0">Netto hängt von Steuerklasse, Kirchensteuer und Krankenkasse ab: <a href="/de/brutto-netto-rechner.html">Brutto-Netto-Rechner</a>.</p></div></div>
<h2 style="font-size:18px;margin:18px 0 4px">Alle Erhöhungen seit 2015</h2><div class="ml-stamps">{stamps}</div></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const N=s=>{const x=parseFloat(String(s).replace(',','.').replace(/[^0-9.]/g,''));return isFinite(x)?x:0};
const E=x=>x.toLocaleString('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2})+' €';
function go(){const h=N($('hrs').value),w=(document.querySelector('input[name=per]:checked')||{}).value==='w';const m=w?h*13/3:h;
 $('o26').textContent=E(13.90*m)+' / Monat';$('o27').textContent=E(14.60*m)+' / Monat';
 $('y26').textContent=E(13.90*m*12)+' im Jahr';$('y27').textContent=E(14.60*m*12)+' im Jahr · +'+E(0.70*m*12);
 const mj=14.60*m;$('mj').innerHTML=mj<=633?'✅ Mit '+E(mj)+' im Monat bleibst du 2027 unter der <b>Minijob-Grenze von 633 €</b> (höchstens '+(633/14.60).toLocaleString('de-DE',{maximumFractionDigits:1})+' Stunden im Monat).':(mj<=2000?'ℹ️ '+E(mj)+' im Monat liegt 2027 im <b>Übergangsbereich (Midijob) von 633,01 € bis 2.000 €</b>: geringere Sozialabgaben für dich.':'ℹ️ Über 2.000 € im Monat: normale Sozialversicherungsbeiträge.')}
$('hrs').addEventListener('input',go);document.querySelectorAll('input[name=per]').forEach(r=>r.addEventListener('change',()=>{const v=N($('hrs').value);$('hrs').value=(r.value==='m'?(v*13/3):(v*3/13)).toLocaleString('de-DE',{maximumFractionDigits:1});go()}));go();
})();
</script>'''

FAQ = [
    ('Wie hoch ist der Mindestlohn 2027?', 'Ab dem 1. Januar 2027 beträgt der gesetzliche Mindestlohn 14,60 Euro brutto pro Stunde. Seit dem 1. Januar 2026 sind es 13,90 Euro.'),
    ('Wie viel ist der Mindestlohn 2027 im Monat bei 40 Stunden?', f'14,60 € × 40 Stunden × 13 ÷ 3 = {eur(14.6 * 40 * 13 / 3)} brutto im Monat ({eur(14.6 * 40 * 52)} im Jahr).'),
    ('Wie hoch ist die Minijob-Grenze 2027?', 'Die Verdienstgrenze für Minijobs steigt 2027 auf 633 Euro im Monat (2026: 603 Euro). Sie ist an den Mindestlohn gekoppelt: 10 Wochenstunden × Mindestlohn × 13 ÷ 3, aufgerundet.'),
    ('Wie viele Stunden darf ich 2027 im Minijob arbeiten?', 'Mit Mindestlohn höchstens etwa 43,3 Stunden im Monat (633 € ÷ 14,60 €).'),
    ('Wie viel ist der Mindestlohn 2027 netto?', 'Das hängt von Steuerklasse, Kirchensteuer, Kinderlosenzuschlag und Krankenkasse ab. Rechne deinen Monatslohn mit dem <a href="/de/brutto-netto-rechner.html">Brutto-Netto-Rechner</a> aus.'),
]
ART = ('<h2 id="faq">Häufige Fragen</h2>' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in FAQ)
       + '<h3 id="tabelle">Mindestlohn 2026 und 2027 im Monat</h3>'
       + table(['Wochenstunden', '2026 (13,90 €)', '2027 (14,60 €)', 'Plus pro Monat'], [[str(h).replace('.', ','), eur(o), eur(n), eur(n - o)] for h, n, o in ROWS])
       + f'<p class="note">Quelle (geprüft am {DATE_DE}): <a href="https://www.bundesregierung.de/breg-de/aktuelles/mindestlohn-steigt-2391010" rel="nofollow">Bundesregierung: Mindestlohn jetzt bei 13,90 Euro (2027: 14,60 Euro, Minijob 633 Euro)</a>. Keine Rechtsberatung.</p>')


def main():
    s = open(os.path.join(ORIG, 'de/stundenlohn-rechner.html'), encoding='utf-8').read()
    old = 'https://honglifecalc.com/de/stundenlohn-rechner.html'
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + H1, s, count=1)
    s = s.replace(old, URL); assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": H1, "url": URL, "description": DESC, "inLanguage": "de-DE"},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": "Deutschland", "item": "https://honglifecalc.com/de/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld) + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', f'<header class="hero"><div class="in"><span class="year">🇩🇪 Ab 1. Januar 2027</span><h1>{H1}</h1><p>Monatslohn, Minijob-Grenze und dein eigener Stundenplan.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: APP, s, count=1, flags=re.S)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'id="o27"' in s and 'id="faq"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
