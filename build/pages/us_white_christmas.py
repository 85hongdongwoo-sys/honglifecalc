"""US: White Christmas chance by city – NOAA NCEI GHCN-Daily snow depth on December 25, 1996–2025 (30 Christmases),
NOAA definition of a white Christmas: at least 1 inch of snow on the ground on Christmas morning.
Data pulled from the NCEI Access Data Service (daily-summaries, SNWD) on 2026-11-25 into build/data/white_christmas_noaa.json.
Template: /us/electricity-cost-calculator.html. Writes overlay/us/white-christmas-chance.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/us/white-christmas-chance.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'White Christmas Chance by City – 30 Years of NOAA Snow Data (2026)'
H1 = 'Will It Be a White Christmas? Chance by City'
DESC = ('How often is there snow on the ground on December 25 in your city? The last 30 Christmases (1996–2025) from NOAA '
        'station records for 50+ US cities, with a year-by-year snow strip and a ranking.')
DATE_EN = 'November 25, 2026'
Y0 = 1996

raw = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'white_christmas_noaa.json'), encoding='utf-8'))
D = {}
for city, (sid, name, arr) in raw.items():
    v = [x for x in arr if x is not None]
    if len(v) < 20:
        continue
    D[city] = {'id': sid, 'st': (lambda q: q[0].title().replace('Ohare', "O'Hare") + ', ' + q[1])(name[:-3].rsplit(', ', 1)), 'a': arr,
               'n': len(v), 'w': sum(1 for x in v if x >= 1)}
for c in D.values():
    c['p'] = round(100 * c['w'] / c['n'])
rank = sorted(D.items(), key=lambda kv: (-kv[1]['p'], kv[0]))
city_opts = ''.join(f'<option{" selected" if k == "Chicago, IL" else ""}>{k}</option>' for k in sorted(D))
JD = json.dumps({k: [v['a'], v['st'], v['id']] for k, v in D.items()}, separators=(',', ':'))

CSS = '''<style id="xc-css">
.app>#form,.app>#out{min-width:0;max-width:100%}@media(max-width:860px){section.app{grid-template-columns:minmax(0,1fr)!important}}
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.xc-top{display:grid;grid-template-columns:150px minmax(0,1fr);gap:16px;align-items:center;background-color:#0F2347;color:#fff;border-radius:18px;padding:14px;position:relative;overflow:hidden}
.xc-top canvas{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.xc-ring{position:relative;width:150px;height:150px}.xc-ring svg{width:150px;height:150px;display:block}
.xc-ring .arc{transition:stroke-dashoffset 1.2s ease}
.xc-ring b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column;font-size:34px;font-weight:900;color:#fff;font-variant-numeric:tabular-nums}
.xc-ring b small{font-size:11.5px;font-weight:600;opacity:.85;max-width:82%;text-align:center;line-height:1.15}
.xc-txt{position:relative;min-width:0}.xc-txt h3{margin:0 0 6px;font-size:20px;color:#fff;overflow-wrap:anywhere}.xc-txt p{margin:0 0 6px;font-size:14px;color:#DCE6F5}
.xc-txt .tag{display:inline-block;border-radius:999px;padding:3px 11px;font-size:12.5px;font-weight:800;background-color:#E0ECFF;color:#0F2347}
.xc-yrs{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:4px;margin:14px 0 6px}
.xc-y{border-radius:8px;text-align:center;padding:6px 0 4px;font-size:10.5px;line-height:1.25;background-color:#F1F5F9;color:#475569;min-width:0}
.xc-y i{display:block;font-style:normal;font-size:16px;line-height:1.1}
.xc-y.s{background-color:#DBEAFE;color:#1E3A8A;font-weight:700}.xc-y.x{background-color:#fff;border:1px dashed #CBD5E1;color:#94A3B8}
.xc-y{opacity:0;animation:xcin .35s ease forwards}@keyframes xcin{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
.xc-leg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:#5B6B82;margin:4px 0 10px}
.xc-sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0}
.xc-sum div{background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:12px;padding:9px 11px;min-width:0}
.xc-sum b{display:block;font-size:18px;color:#12305C;overflow-wrap:anywhere}.xc-sum span{font-size:12px;color:#5B6B82}
.xc-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
.xc-bars{display:flex;flex-direction:column;gap:4px;margin-top:8px}
.xc-b{display:grid;grid-template-columns:minmax(0,9.5em) minmax(0,1fr) 3.2em;gap:8px;align-items:center;font-size:13px}
.xc-b span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.xc-b i{display:block;height:12px;border-radius:999px;background-color:#93C5FD}
.xc-b.me span{font-weight:800}.xc-b.me i{background-color:#1D4ED8}
.xc-b em{font-style:normal;text-align:right;font-variant-numeric:tabular-nums}
@media(max-width:600px){.xc-top{grid-template-columns:110px minmax(0,1fr);gap:10px}.xc-ring,.xc-ring svg{width:110px;height:110px}.xc-ring b{font-size:26px}
.xc-yrs{grid-template-columns:repeat(6,minmax(0,1fr))}.xc-sum{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.xc-y{animation:none;opacity:1}.xc-ring .arc{transition:none}}
</style>'''

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Pick your city</h2>
<label class="f"><span>City</span><select id="city">{city_opts}</select>
<small>Each city uses one official NOAA weather station (mostly the main airport).</small></label>
<label class="f"><span>Snow depth threshold</span><select id="thr"><option value="1" selected>1 inch or more (NOAA white Christmas)</option><option value="3">3 inches or more</option><option value="6">6 inches or more</option></select></label>
</form><section class="card" id="out" aria-live="polite"><p>Loading …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const D=__DATA__,Y0=1996;
function stat(a,t){let n=0,w=0,mx=0,my=null,last=null;a.forEach((x,i)=>{if(x==null)return;n++;if(x>=t){w++;last=Y0+i}if(x>mx){mx=x;my=Y0+i}});return{n,w,p:n?Math.round(100*w/n):0,mx,my,last}}
function word(p){return p>=75?['Almost always white','#BFDBFE']:p>=50?['More often white than not','#DBEAFE']:p>=25?['About 1 in '+Math.max(2,Math.round(100/Math.max(p,1)))+' years','#E0ECFF']:p>0?['Rare','#E2E8F0']:['No white Christmas in 30 years','#E2E8F0']}
let snowRun=0;
function snow(c,p){const x=c.getContext('2d'),id=++snowRun,red=matchMedia('(prefers-reduced-motion: reduce)').matches;const r=c.getBoundingClientRect(),dp=devicePixelRatio||1;const w=r.width,h=r.height;c.width=w*dp;c.height=h*dp;x.setTransform(dp,0,0,dp,0,0);
 const F=Array.from({length:Math.round(6+p*0.9)},()=>({x:Math.random()*w,y:Math.random()*h,r:1+Math.random()*2.2,v:.3+Math.random()*.8,o:Math.random()*6}));
 (function fr(t){if(id!==snowRun)return;x.clearRect(0,0,w,h);x.fillStyle='rgba(255,255,255,.8)';F.forEach(f=>{if(!red){f.y+=f.v;f.x+=Math.sin(t/1500+f.o)*.3;if(f.y>h+3){f.y=-3;f.x=Math.random()*w}}x.beginPath();x.arc(f.x,f.y,f.r,0,6.283);x.fill()});if(!red)requestAnimationFrame(fr)})(0)}
function draw(){const k=$('city').value,t=+$('thr').value,[a,st,sid]=D[k],s=stat(a,t),wd=word(s.p);
 const C=2*Math.PI*62,off=C*(1-s.p/100);
 let h='<div class="xc-top"><canvas id="xcs"></canvas><div class="xc-ring"><svg viewBox="0 0 150 150" aria-hidden="true"><circle cx="75" cy="75" r="62" fill="none" stroke="rgba(255,255,255,.18)" stroke-width="13"/><circle class="arc" cx="75" cy="75" r="62" fill="none" stroke="#FFFFFF" stroke-width="13" stroke-linecap="round" transform="rotate(-90 75 75)" stroke-dasharray="'+C.toFixed(1)+'" stroke-dashoffset="'+C.toFixed(1)+'" id="arc"/></svg><b>'+s.p+'%<small>white Christmas</small></b></div>'
 +'<div class="xc-txt"><h3>'+esc(k)+'</h3><p>Snow on the ground ('+t+'+ in) on Dec 25 in <b>'+s.w+' of the last '+s.n+'</b> Christmases with a record.</p><span class="tag" style="background-color:'+wd[1]+'">'+wd[0]+'</span></div></div>';
 h+='<div class="xc-yrs" role="img" aria-label="Snow depth on December 25, 1996 to 2025">'+a.map((x,i)=>{const y=Y0+i,cl=x==null?'x':(x>=t?'s':'');return '<div class="xc-y '+cl+'" style="animation-delay:'+(i*0.03).toFixed(2)+'s" title="'+y+': '+(x==null?'no record':x+' in')+'"><i>'+(x==null?'·':(x>=t?'❄️':'🟫'))+'</i>\''+String(y).slice(2)+'<br>'+(x==null?'–':x+'"')+'</div>'}).join('')+'</div>';
 h+='<div class="xc-leg"><span>❄️ snow on the ground</span><span>🟫 no snow (or under '+t+' in)</span><span>· no record that year</span><span>Numbers = snow depth in inches</span></div>';
 h+='<div class="xc-sum"><div><span>Deepest Christmas snow</span><b>'+(s.mx?s.mx+' in':'none')+'</b><span>'+(s.my||'')+'</span></div><div><span>Last white Christmas</span><b>'+(s.last||'none since '+Y0)+'</b><span>'+t+'+ in on Dec 25</span></div><div><span>Odds in plain words</span><b>'+(s.p?'1 in '+(Math.round(10*100/s.p)/10):'—')+'</b><span>years</span></div></div>';
 const all=Object.keys(D).map(c=>[c,stat(D[c][0],t).p]).sort((x,y)=>y[1]-x[1]||x[0].localeCompare(y[0]));const me=all.findIndex(r=>r[0]===k);
 const lo=Math.max(0,Math.min(all.length-7,me-3));
 h+='<p style="margin:10px 0 2px;font-size:14px"><b>#'+(me+1)+' of '+all.length+'</b> cities on this page for a white Christmas:</p><div class="xc-bars">'+all.slice(lo,lo+7).map((r,i)=>'<div class="xc-b'+(r[0]===k?' me':'')+'"><span>'+(lo+i+1)+'. '+esc(r[0])+'</span><i style="width:'+Math.max(2,r[1])+'%"></i><em>'+r[1]+'%</em></div>').join('')+'</div>';
 h+='<p class="xc-src">Station: '+esc(st)+' ('+sid+'). Data: NOAA National Centers for Environmental Information, GHCN-Daily snow depth (SNWD) on December 25, 1996–2025, retrieved November 25, 2026. Past frequency, not a forecast for this year.</p>';
 $('out').innerHTML=h;requestAnimationFrame(()=>{const g=$('arc');if(g)g.style.strokeDashoffset=off.toFixed(1)});snow($('xcs'),s.p)}
$('city').addEventListener('change',draw);$('thr').addEventListener('change',draw);draw();
})();
</script>'''.replace('__DATA__', JD)

top10 = rank[:10]
low = [r for r in rank if r[1]['p'] <= 10]
FAQ = [
 ("What counts as a white Christmas?",
  "NOAA defines a white Christmas as at least 1 inch of snow on the ground on the morning of December 25. Snow that falls during the day but does not reach 1 inch on the ground does not count."),
 ("Where does this data come from?",
  "From NOAA's Global Historical Climatology Network – Daily (GHCN-Daily), the official daily record of US weather stations. For each city we read the snow depth reported for December 25 in each of the last 30 years (1996–2025) and counted the years with 1 inch or more. Years without a snow depth report are left out."),
 ("Why is my city's number different from NOAA's map?",
  "NOAA's white Christmas map uses the 1991–2020 climate normals and many more stations. This page uses the most recent 30 Christmases (1996–2025) at one main station per city, so numbers can differ by a few percentage points."),
 ("Can this tell me if it will snow this Christmas?",
  "No. It shows how often it happened in the past. For this year, check the National Weather Service forecast for your area about a week before Christmas (from around December 18)."),
 ("Which big cities almost always have a white Christmas?",
  "On this page: " + ', '.join(f"{k} ({v['p']}%)" for k, v in top10[:5]) + "."),
]

ART = f'''<p><b>In short:</b> pick a city to see how many of the last 30 Christmases had at least <b>1 inch of snow on the ground</b> – NOAA's definition of a white Christmas – with every year from 1996 to 2025 as a snowflake strip.</p>
<h2 id="how">How it works</h2>
<ul><li><b>Data:</b> NOAA NCEI GHCN-Daily snow depth (SNWD) on December 25 at one official station per city</li>
<li><b>Chance</b> = years with snow depth ≥ 1 inch ÷ years with a snow depth record (1996–2025)</li>
<li>Cities with fewer than 20 years of December 25 records were left out</li></ul>
<h3 id="top">Most likely white Christmas (1 inch or more)</h3>
''' + table(['City', 'Chance', 'White Christmases', 'Station'], [[k, f"{v['p']}%", f"{v['w']} of {v['n']}", v['id']] for k, v in top10]) + f'''
<h3 id="all">All {len(D)} cities</h3>
''' + table(['City', 'Chance', 'White Christmases'], [[k, f"{v['p']}%", f"{v['w']} of {v['n']}"] for k, v in rank]) + '''
''' + faq_html(FAQ, heading='FAQ').replace('<h2 style="margin-top:22px">FAQ</h2>', '<h2 id="faq" style="margin-top:22px">FAQ</h2>') + f'''
<p class="note">Sources (checked {DATE_EN}): <a href="https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily" rel="nofollow">NOAA NCEI: Global Historical Climatology Network – Daily</a>; <a href="https://www.ncei.noaa.gov/access/services/data/v1" rel="nofollow">NCEI Access Data Service</a>; <a href="https://www.climate.gov/news-features/featured-images/are-you-dreaming-white-christmas" rel="nofollow">NOAA Climate.gov: Are you dreaming of a white Christmas?</a> See also: <a href="/us/santa-speed-calculator.html">How fast does Santa fly?</a> · <a href="/us/wind-chill-frostbite-forecast.html">Wind chill &amp; frostbite forecast</a>.</p>'''

TOC = [('form', 'Calculator'), ('how', 'How it works'), ('top', 'Top 10'), ('all', 'All cities'), ('faq', 'FAQ')]


def main():
    s = open(os.path.join(ORIG, 'us/electricity-cost-calculator.html'), encoding='utf-8').read()
    old = 'https://honglifecalc.com/us/electricity-cost-calculator.html'
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + H1, s, count=1)
    s = s.replace(old, URL)
    assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": H1, "url": URL, "description": DESC,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "en-US",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": "US calculators", "item": "https://honglifecalc.com/us/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇺🇸 ❄️ NOAA station records · 1996–2025</span>'
               f'<h1>{H1}</h1><p>How often your city had snow on the ground on December 25 in the last 30 years.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>By <b>Hong Life Calculators</b></span><span>Checked <b>{DATE_EN}</b></span>'
           '<span>Data <b>NOAA NCEI</b></span></div><details class="card hl-toc" open><summary>On this page</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'xc-yrs' in s and 'id="city"' in s and 'id="all"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s), len(D), 'cities')


main()
