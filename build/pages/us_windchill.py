"""US: Wind chill & frostbite time forecast – NWS api.weather.gov hourly forecast (public domain, called from the browser, CORS ok),
NWS wind chill formula (2001), frostbite-time bands from Environment and Climate Change Canada (same 2001 JAG/TI index).
Template: /us/electricity-cost-calculator.html. Writes overlay/us/wind-chill-frostbite-forecast.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/us/wind-chill-frostbite-forecast.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Wind Chill & Frostbite Time Calculator – 48-Hour Forecast for Your City (2026)'
H1 = 'Wind Chill & Frostbite Time Forecast'
DESC = ('How cold will it feel, and how fast can exposed skin freeze? Hour-by-hour wind chill for the next 48 hours from the '
        'National Weather Service, with frostbite times and a check for your walk, run or wait at the bus stop.')
DATE_EN = 'November 24, 2026'

CITIES = [('Anchorage, AK', 61.22, -149.90), ('Fairbanks, AK', 64.84, -147.72), ('Boston, MA', 42.36, -71.06), ('Burlington, VT', 44.48, -73.21),
          ('Buffalo, NY', 42.89, -78.88), ('Chicago, IL', 41.88, -87.63), ('Cleveland, OH', 41.50, -81.69), ('Denver, CO', 39.74, -104.99),
          ('Des Moines, IA', 41.59, -93.62), ('Detroit, MI', 42.33, -83.05), ('Duluth, MN', 46.79, -92.10), ('Fargo, ND', 46.88, -96.79),
          ('Bismarck, ND', 46.81, -100.78), ('Green Bay, WI', 44.51, -88.01), ('Indianapolis, IN', 39.77, -86.16), ('Milwaukee, WI', 43.04, -87.91),
          ('Minneapolis, MN', 44.98, -93.27), ('New York, NY', 40.71, -74.01), ('Omaha, NE', 41.26, -95.93), ('Philadelphia, PA', 39.95, -75.17),
          ('Pittsburgh, PA', 40.44, -80.00), ('Portland, ME', 43.66, -70.26), ('Rapid City, SD', 44.08, -103.23), ('Salt Lake City, UT', 40.76, -111.89),
          ('Sioux Falls, SD', 43.55, -96.73), ('Billings, MT', 45.78, -108.50), ('Helena, MT', 46.59, -112.04), ('Cheyenne, WY', 41.14, -104.82),
          ('Washington, DC', 38.91, -77.04), ('Kansas City, MO', 39.10, -94.58), ('St. Louis, MO', 38.63, -90.20), ('Seattle, WA', 47.61, -122.33),
          ('Spokane, WA', 47.66, -117.43), ('Boise, ID', 43.62, -116.20), ('Albany, NY', 42.65, -73.75), ('Madison, WI', 43.07, -89.40)]
city_opts = ''.join(f'<option value="{la},{lo}"{" selected" if n.startswith("Minneapolis") else ""}>{n}</option>' for n, la, lo in sorted(CITIES))

CSS = '''<style id="wc-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.wc-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.wc-row .f{min-width:0}
.app>#form,.app>#out{min-width:0;max-width:100%}@media(max-width:860px){section.app{grid-template-columns:minmax(0,1fr)!important}}
.wc-loc{display:flex;gap:8px;flex-wrap:wrap}.wc-loc select{flex:1 1 160px;min-width:0}
.wc-loc button{border:1px solid #C9D3E3;background:#fff;border-radius:10px;padding:8px 12px;font:inherit;font-size:14px;cursor:pointer;min-height:40px}
.wc-live{display:inline-flex;align-items:baseline;gap:6px;font-size:12.5px;font-weight:700;color:#1f4f8a;background:#EAF1FB;border:1px solid #CFDDF3;border-radius:999px;padding:2px 10px;margin:0 0 10px;max-width:100%;flex-wrap:wrap}
.wc-now{display:grid;grid-template-columns:70px minmax(0,1fr);gap:14px;align-items:center;background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:16px;padding:12px;margin-bottom:12px}
.wc-th svg{width:70px;height:150px;display:block}
.wc-merc{transform-origin:bottom;animation:wcm 1.2s ease both}@keyframes wcm{from{transform:scaleY(.05)}to{transform:scaleY(1)}}
.wc-big small{display:block;font-size:12.5px;color:#5B6B82}.wc-big b{display:block;font-size:34px;line-height:1.1;font-variant-numeric:tabular-nums}
.wc-big span{display:block;font-size:13.5px;color:#3a3a3c;margin-top:4px}
.wc-badge{display:inline-block;border-radius:999px;padding:2px 10px;font-size:12.5px;font-weight:800;color:#fff;margin-top:6px}
.wc-strip{display:flex;gap:2px;overflow-x:auto;padding:4px 2px 2px;max-width:100%;scrollbar-width:thin}
.wc-h{flex:0 0 32px;text-align:center;font-size:10.5px;color:#5B6B82}
.wc-h i{display:flex;align-items:flex-end;justify-content:center;height:56px;border-radius:6px;margin-bottom:3px;font-style:normal;font-size:10px;font-weight:700;color:#fff;padding-bottom:3px;box-sizing:border-box}
.wc-h b{display:block;color:#12305C;font-size:10.5px;white-space:nowrap}
.wc-leg{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12px;color:#5B6B82;margin:6px 0}
.wc-leg i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.wc-sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0}
.wc-sum div{background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:12px;padding:9px 11px;min-width:0}
.wc-sum b{display:block;font-size:18px;color:#12305C;overflow-wrap:anywhere}.wc-sum span{font-size:12px;color:#5B6B82}
.wc-warn{background-color:#FEF2F2;border:1px solid #FECACA;border-radius:12px;padding:10px 12px;font-size:14px;color:#7F1D1D;margin:8px 0}
.wc-ok{background-color:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:10px 12px;font-size:14px;color:#14532D;margin:8px 0}
.wc-err{background-color:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.wc-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
@media(max-width:600px){.wc-row,.wc-sum{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.wc-merc{animation:none}}
</style>'''

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Where and how long outside</h2>
<label class="f"><span>City</span><div class="wc-loc"><select id="city">{city_opts}</select><button type="button" id="me">📍 My location</button></div>
<small>Your location is only sent to the National Weather Service to get the forecast.</small></label>
<div class="wc-row"><label class="f"><span>Minutes outside</span><input id="mins" inputmode="numeric" value="20"><small>Walk, run, dog walk or waiting for the bus.</small></label>
<label class="f"><span>Units</span><select id="unit"><option value="F">°F, mph</option><option value="C">°C, km/h</option></select></label></div>
</form><section class="card" id="out" aria-live="polite"><p>Loading the NWS forecast …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let pos=null,place='',H=null,tz='America/Chicago',busy=0;
// NWS wind chill (2001): WC = 35.74 + 0.6215T − 35.75 V^0.16 + 0.4275 T V^0.16 (T °F ≤ 50, V mph > 3)
function wc(T,V){if(T>50||V<=3)return T;const v=Math.pow(V,0.16);return 35.74+0.6215*T-35.75*v+0.4275*T*v}
const toC=f=>(f-32)*5/9;
// ECCC risk bands (°C wind chill)
function band(wcF){const c=toC(wcF);if(c<=-55)return{k:6,n:'Extreme',t:'under 2 min',m:1,col:'#4C1D95'};if(c<=-48)return{k:5,n:'Severe',t:'2–5 min',m:2,col:'#7C3AED'};if(c<=-40)return{k:4,n:'Very high',t:'5–10 min',m:5,col:'#DC2626'};if(c<=-28)return{k:3,n:'High',t:'10–30 min',m:10,col:'#F97316'};if(c<=-10)return{k:2,n:'Moderate',t:'longer exposure',m:null,col:'#3B82F6'};if(c<0)return{k:1,n:'Low',t:'—',m:null,col:'#60A5FA'};return{k:0,n:'No wind chill risk',t:'—',m:null,col:'#94A3B8'}}
async function load(){const p=await fetch('https://api.weather.gov/points/'+pos.lat.toFixed(4)+','+pos.lon.toFixed(4)).then(r=>{if(!r.ok)throw new Error('location outside NWS coverage');return r.json()});
 tz=p.properties.timeZone||tz;const rel=p.properties.relativeLocation&&p.properties.relativeLocation.properties;if(!place&&rel)place=rel.city+', '+rel.state;
 const f=await fetch(p.properties.forecastHourly).then(r=>{if(!r.ok)throw new Error('forecast '+r.status);return r.json()});
 return f.properties.periods.slice(0,48).map(x=>{const ws=(String(x.windSpeed).match(/\d+/g)||['0']).map(Number);const T=x.temperatureUnit==='C'?x.temperature*9/5+32:x.temperature;return{t:new Date(x.startTime),T,V:Math.max(...ws),short:x.shortForecast}})}
function draw(){if(!H)return;const C=$('unit').value==='C',mins=Math.max(0,parseFloat($('mins').value)||0);
 const fmtT=f=>C?Math.round(toC(f))+'°C':Math.round(f)+'°F',fmtV=v=>C?Math.round(v*1.609)+' km/h':Math.round(v)+' mph';
 const hf=new Intl.DateTimeFormat('en-US',{timeZone:tz,hour:'numeric'}),df=new Intl.DateTimeFormat('en-US',{timeZone:tz,weekday:'short'}),hh=new Intl.DateTimeFormat('en-US',{timeZone:tz,hour:'numeric',hourCycle:'h23'});
 const rows=H.map(x=>{const w=wc(x.T,x.V);return Object.assign({},x,{w,b:band(w)})});
 const now=rows[0],worst=rows.reduce((a,x)=>x.w<a.w?x:a,rows[0]);
 const lvl=Math.max(0,Math.min(1,(toC(now.w)+60)/70));
 let h='<span class="wc-live">📍 '+esc(place)+' · National Weather Service hourly forecast</span>';
 h+='<div class="wc-now"><div class="wc-th"><svg viewBox="0 0 70 150" aria-hidden="true"><rect x="26" y="8" width="18" height="110" rx="9" fill="#fff" stroke="#94A3B8" stroke-width="2"/><rect class="wc-merc" x="31" y="'+(114-100*lvl).toFixed(1)+'" width="8" height="'+(100*lvl+4).toFixed(1)+'" rx="4" fill="'+now.b.col+'"/><circle cx="35" cy="128" r="16" fill="'+now.b.col+'" stroke="#94A3B8" stroke-width="2"/></svg></div>'
  +'<div class="wc-big"><small>Feels like now (wind chill)</small><b style="color:'+now.b.col+'">'+fmtT(now.w)+'</b><span>Air '+fmtT(now.T)+' · wind '+fmtV(now.V)+' · '+esc(now.short)+'</span><span class="wc-badge" style="background:'+now.b.col+'">'+now.b.n+(now.b.m?' · skin can freeze in '+now.b.t:'')+'</span></div></div>';
 const first=rows.find(x=>x.b.m!=null&&mins>=x.b.m);
 if(first)h+='<div class="wc-warn">⚠️ <b>'+mins+' minutes outside is too long</b> around '+df.format(first.t)+' '+hf.format(first.t)+': wind chill '+fmtT(first.w)+', exposed skin can freeze in '+first.b.t+'. Cover all skin or shorten the trip.</div>';
 else h+='<div class="wc-ok">✅ In the next 48 hours, exposed skin is not expected to freeze within '+mins+' minutes (wind chill risk bands of Environment and Climate Change Canada). Dress for the cold anyway.</div>';
 h+='<div class="wc-strip" role="img" aria-label="Wind chill hour by hour">'+rows.map((x,i)=>{const H24=+hh.format(x.t),d=i===0||H24===0;const ht=Math.max(18,Math.min(56,56*(1-(toC(x.w)+5)/-60)));return '<div class="wc-h" title="'+df.format(x.t)+' '+hf.format(x.t)+': feels '+fmtT(x.w)+' (air '+fmtT(x.T)+', wind '+fmtV(x.V)+') – '+x.b.n+'"><i style="background:'+x.b.col+';height:'+ht.toFixed(0)+'px;margin-top:'+(56-ht).toFixed(0)+'px">'+Math.round(C?toC(x.w):x.w)+'</i>'+(d?'<b>'+df.format(x.t)+'</b>':'')+hf.format(x.t).replace(' ','').toLowerCase()+'</div>'}).join('')+'</div>';
 h+='<div class="wc-leg"><span><i style="background:#94A3B8"></i>No risk</span><span><i style="background:#60A5FA"></i>Low</span><span><i style="background:#3B82F6"></i>Moderate</span><span><i style="background:#F97316"></i>High · 10–30 min</span><span><i style="background:#DC2626"></i>Very high · 5–10 min</span><span><i style="background:#7C3AED"></i>Severe · 2–5 min</span><span><i style="background:#4C1D95"></i>Extreme · &lt;2 min</span></div>';
 h+='<div class="wc-sum"><div><span>Coldest wind chill (48 h)</span><b>'+fmtT(worst.w)+'</b><span>'+df.format(worst.t)+' '+hf.format(worst.t)+'</span></div><div><span>Hours with frostbite risk</span><b>'+rows.filter(x=>x.b.m).length+' h</b><span>wind chill −28 °C (−18 °F) or colder</span></div><div><span>Warmest feel</span><b>'+fmtT(Math.max(...rows.map(x=>x.w)))+'</b></div></div>';
 h+='<p class="wc-src">Forecast: National Weather Service (api.weather.gov), public domain. Wind chill: NWS formula. Frostbite times: Environment and Climate Change Canada wind chill risk table; in winds over 50 km/h (31 mph) skin can freeze faster. Not medical advice.</p>';
 $('out').innerHTML=h}
async function run(){const id=++busy;$('out').innerHTML='<p>Loading the NWS forecast …</p>';try{if(!pos){const v=$('city').value.split(',');pos={lat:+v[0],lon:+v[1]};place=$('city').selectedOptions[0].text}H=await load();if(id===busy)draw()}catch(e){if(id===busy)$('out').innerHTML='<p class="wc-err">Could not load the forecast ('+esc(e.message)+'). Try again in a minute.</p>'}}
$('city').addEventListener('change',()=>{pos=null;run()});
$('me').addEventListener('click',()=>{navigator.geolocation&&navigator.geolocation.getCurrentPosition(p=>{pos={lat:p.coords.latitude,lon:p.coords.longitude};place='';run()},()=>{},{timeout:10000,maximumAge:600000})});
['mins','unit'].forEach(id=>$(id).addEventListener('input',draw));$('unit').addEventListener('change',draw);
run();
})();
</script>'''

FAQ = [
 ("How is wind chill calculated?",
  "With the formula the National Weather Service has used since 2001: Wind chill (°F) = 35.74 + 0.6215T − 35.75(V^0.16) + 0.4275T(V^0.16), where T is the air temperature in °F and V the wind speed in mph. It is only defined at 50 °F or colder and winds above 3 mph."),
 ("How fast can frostbite happen?",
  "Environment and Climate Change Canada, which uses the same wind chill index, lists: wind chill −28 to −39 °C (about −18 to −38 °F): exposed skin can freeze in 10–30 minutes; −40 to −47 °C: 5–10 minutes; −48 to −54 °C: 2–5 minutes; −55 °C or colder: under 2 minutes. In winds over 50 km/h it can be faster."),
 ("Example: 0 °F with a 15 mph wind?",
  "The NWS formula gives a wind chill of about −19 °F (−28 °C). The NWS says that at this wind chill exposed skin can freeze in 30 minutes."),
 ("Does wind chill affect cars or pipes?",
  "No. Wind chill describes heat loss from skin. Objects cannot cool below the actual air temperature; wind only helps them reach it faster."),
 ("Is this medical advice?",
  "No. It is a forecast-based guide. If you see signs of frostbite (numbness, white or grayish-yellow skin) or hypothermia (shivering, confusion), get warm and seek medical help."),
]

ART = '''<p><b>In short:</b> pick your city (or use your location). The page loads the <b>National Weather Service</b> hourly forecast, computes the <b>wind chill</b> for every hour of the next 48 and colours each hour by <b>how fast exposed skin can freeze</b>. Enter how long you will be outside and it warns you if that is too long.</p>
<h2 id="how">How it works</h2>
<ul><li><b>Wind chill</b> = 35.74 + 0.6215T − 35.75 V<sup>0.16</sup> + 0.4275 T V<sup>0.16</sup> (NWS, T in °F, V in mph)</li>
<li><b>Frostbite time</b> from the wind chill risk bands of Environment and Climate Change Canada</li>
<li><b>Warning</b> when your minutes outside reach the frostbite time of any forecast hour</li></ul>
<h3 id="examples">Worked examples (NWS formula)</h3>
''' + table(['Air temperature', 'Wind', 'Wind chill', 'Frostbite time'], [
    ['20 °F', '10 mph', 'about 9 °F (−13 °C)', 'no frostbite band'],
    ['0 °F', '15 mph', 'about −19 °F (−28 °C)', '10–30 minutes'],
    ['−10 °F', '20 mph', 'about −35 °F (−37 °C)', '10–30 minutes'],
    ['−20 °F', '25 mph', 'about −51 °F (−46 °C)', '5–10 minutes'],
]) + '''
<h3 id="bands">Wind chill risk bands</h3>
''' + table(['Wind chill', 'Risk', 'Exposed skin can freeze in'], [
    ['0 to −9 °C (32 to 16 °F)', 'Low', '—'],
    ['−10 to −27 °C (14 to −17 °F)', 'Moderate', 'long exposure without protection'],
    ['−28 to −39 °C (−18 to −38 °F)', 'High', '10–30 minutes'],
    ['−40 to −47 °C (−40 to −53 °F)', 'Very high', '5–10 minutes'],
    ['−48 to −54 °C (−54 to −65 °F)', 'Severe', '2–5 minutes'],
    ['−55 °C (−67 °F) or colder', 'Extreme', 'under 2 minutes'],
]) + '''
<h3>Staying safe</h3>
<ul><li>Cover the face, ears, nose and fingers first – they freeze fastest.</li>
<li>Dress in layers and keep dry; wet clothing loses heat quickly.</li>
<li>Plan shorter trips during the coldest hours shown in the strip.</li></ul>
''' + faq_html(FAQ, heading='FAQ').replace('<h2 style="margin-top:22px">FAQ</h2>', '<h2 id="faq" style="margin-top:22px">FAQ</h2>') + f'''
<p class="note">Sources (checked {DATE_EN}): <a href="https://www.weather.gov/documentation/services-web-api" rel="nofollow">National Weather Service API</a>; <a href="https://www.weather.gov/safety/cold-faqs" rel="nofollow">NWS: Cold weather FAQs (wind chill formula)</a>; <a href="https://www.canada.ca/en/services/environment/weather/severeweather/wind-chill-index.html" rel="nofollow">Environment and Climate Change Canada: Wind chill and the Wind Chill Index</a>. Not medical advice. See also: <a href="/us/electricity-cost-calculator.html">Electricity cost calculator</a>.</p>'''

TOC = [('form', 'Calculator'), ('how', 'How it works'), ('examples', 'Examples'), ('bands', 'Risk bands'), ('faq', 'FAQ')]


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
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇺🇸 Live · National Weather Service</span>'
               f'<h1>{H1}</h1><p>How cold will it feel, and how fast can exposed skin freeze? The next 48 hours for your city.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>By <b>Hong Life Calculators</b></span><span>Checked <b>{DATE_EN}</b></span>'
           '<span>Data <b>National Weather Service</b></span></div><details class="card hl-toc" open><summary>On this page</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'api.weather.gov/points' in s and 'id="city"' in s and 'id="bands"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
