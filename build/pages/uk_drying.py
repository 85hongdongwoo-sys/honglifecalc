"""UK: Will my washing dry outside? – hourly drying forecast from MET Norway Locationforecast (CC BY 4.0, called from the browser,
CORS ok) + postcodes.io (Open Government Licence) for postcode → lat/lon. Drying power = Penman (1948) wind function × vapour
pressure deficit. Template: /uk/electricity-cost-calculator.html. Writes overlay/uk/washing-drying-forecast.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/uk/washing-drying-forecast.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Will My Washing Dry Outside Today? Drying Forecast by Postcode (2026)'
H1 = 'Washing Line Drying Forecast'
DESC = ('Enter your postcode to see, hour by hour for the next two days, how well washing will dry outside – from temperature, humidity, '
        'wind and rain – the best time to hang it out, and how much you save by skipping the tumble dryer.')
DATE_EN = '24 November 2026'

CSS = '''<style id="wd-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.wd-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.wd-row .f{min-width:0}
.wd-loc{display:flex;gap:8px;flex-wrap:wrap}.wd-loc input{flex:1 1 140px;min-width:0}
.wd-loc button{border:1px solid #C9D3E3;background:#fff;border-radius:10px;padding:8px 12px;font:inherit;font-size:14px;cursor:pointer;min-height:40px}
.wd-live{display:inline-flex;align-items:baseline;gap:6px;font-size:12.5px;font-weight:700;color:#1f4f8a;background:#EAF1FB;border:1px solid #CFDDF3;border-radius:999px;padding:2px 10px;margin:0 0 10px;max-width:100%;flex-wrap:wrap}
.wd-hero{display:grid;grid-template-columns:120px minmax(0,1fr);gap:14px;align-items:center;background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:16px;padding:12px;margin-bottom:12px}
.wd-line{position:relative;height:110px}
.wd-line svg{width:100%;height:110px;display:block}
.wd-shirt{transform-origin:60px 34px;animation:wdsway 2.4s ease-in-out infinite}
.wd-shirt.calm{animation-duration:6s}.wd-shirt.wet{animation:none}
@keyframes wdsway{0%,100%{transform:rotate(-6deg)}50%{transform:rotate(6deg)}}
.wd-verdict b{display:block;font-size:22px;color:#12305C;line-height:1.25}.wd-verdict span{display:block;font-size:13.5px;color:#3a3a3c;margin-top:4px}
.app>#form,.app>#out{min-width:0;max-width:100%}@media(max-width:860px){section.app{grid-template-columns:minmax(0,1fr)!important}}#out{overflow:hidden}.wd-strip{max-width:100%;display:flex;gap:2px;overflow-x:auto;padding:4px 2px 2px;scrollbar-width:thin}
.wd-h{flex:0 0 30px;text-align:center;font-size:10.5px;color:#5B6B82}
.wd-h i{display:block;height:46px;border-radius:6px;margin-bottom:3px;position:relative}
.wd-h i em{position:absolute;left:0;right:0;bottom:3px;font-style:normal;font-size:13px}
.wd-h.best i{outline:2.5px solid #12305C;outline-offset:1px}
.wd-h.day b{display:block;color:#12305C;font-size:10.5px;white-space:nowrap}
.wd-leg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:#5B6B82;margin:6px 0}
.wd-leg i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.wd-sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0}
.wd-sum div{background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:12px;padding:9px 11px;min-width:0}
.wd-sum b{display:block;font-size:19px;color:#12305C;overflow-wrap:anywhere}.wd-sum span{font-size:12px;color:#5B6B82}
.wd-err{background-color:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.wd-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
@media(max-width:600px){.wd-row,.wd-sum{grid-template-columns:1fr}.wd-hero{grid-template-columns:90px minmax(0,1fr)}}
@media(prefers-reduced-motion:reduce){.wd-shirt{animation:none}}
</style>'''

FORM = '''<form class="card" id="form" onsubmit="return false"><h2>Where and what</h2>
<label class="f"><span>Postcode (full or first part)</span><div class="wd-loc"><input id="pc" value="M1" autocomplete="postal-code"><button type="button" id="go">Check</button><button type="button" id="me">📍 Use my location</button></div>
<small>Your location is only used to look up the forecast and is not stored.</small></label>
<div class="wd-row"><label class="f"><span>Tumble dryer energy per load (kWh)</span><input id="kwh" inputmode="decimal" value="2.5"><small>On the energy label or in the manual. Heat-pump dryers use far less than vented or condenser ones.</small></label>
<label class="f"><span>Electricity unit rate (p/kWh)</span><input id="ppk" inputmode="decimal" value="26.32"><small>Ofgem price cap average, Direct Debit, 1 Oct – 31 Dec 2026. Use the rate on your bill.</small></label></div>
<label class="f"><span>Loads a week</span><input id="loads" inputmode="decimal" value="4"></label>
</form><section class="card" id="out" aria-live="polite"><p>Loading the forecast …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=id=>{const v=parseFloat(String($(id).value).replace(/[,\s£p]/g,''));return isFinite(v)?v:0};
const TZ='Europe/London';
const hh=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,hour:'2-digit',hourCycle:'h23'});
const dd=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,weekday:'short'});
const tf=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,weekday:'short',hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
const MET='https://api.met.no/weatherapi/locationforecast/2.0/compact';
let pos=null,place='',fc=null,busy=0;
// Penman (1948) aerodynamic evaporation: Ea = 0.26 (1 + 0.54 u2) (es - ea), mm/day, e in hPa, u2 = wind at 2 m (m/s)
function es(T){return 6.108*Math.exp(17.27*T/(T+237.3))}
function power(T,RH,u10){const u2=u10*4.87/Math.log(67.8*10-5.42);return Math.max(0,0.26*(1+0.54*u2)*es(T)*(1-RH/100))}
function cls(p,rain){if(rain>0)return['wet','#94A3B8','☔','Raining'];if(p>=3)return['great','#16A34A','🌬️','Great'];if(p>=1.5)return['good','#84CC16','🙂','Good'];if(p>=0.5)return['slow','#FACC15','🐌','Slow'];return['poor','#F97316','💧','Poor']}
async function geo(q){q=q.trim().replace(/\s+/g,'');const full=q.length>4;const r=await fetch('https://api.postcodes.io/'+(full?'postcodes/':'outcodes/')+encodeURIComponent(q));const j=await r.json();if(!r.ok||!j.result)throw new Error('postcode not found');const x=j.result;return{lat:x.latitude,lon:x.longitude,label:full?x.postcode:x.outcode+(x.admin_district&&x.admin_district[0]?' · '+x.admin_district[0]:'')}}
async function load(){const r=await fetch(MET+'?lat='+pos.lat.toFixed(4)+'&lon='+pos.lon.toFixed(4));if(!r.ok)throw new Error('forecast '+r.status);return r.json()}
function shirt(c){const col=c==='wet'?'#94A3B8':'#3B82F6';return '<svg viewBox="0 0 120 110" aria-hidden="true"><line x1="4" y1="22" x2="116" y2="22" stroke="#6B7280" stroke-width="2"/><g class="wd-shirt'+(c==='wet'?' wet':c==='poor'||c==='slow'?' calm':'')+'"><rect x="54" y="18" width="4" height="10" fill="#9CA3AF"/><rect x="62" y="18" width="4" height="10" fill="#9CA3AF"/><path d="M38 34 L50 28 Q60 36 70 28 L82 34 L90 50 L80 55 L78 48 L78 92 L42 92 L42 48 L40 55 L30 50 Z" fill="'+col+'"/>'+(c==='wet'?'<circle cx="52" cy="98" r="2.5" fill="#60A5FA"/><circle cx="66" cy="102" r="2.5" fill="#60A5FA"/>':'')+'</g></svg>'}
function draw(){if(!fc)return;const kwh=Math.max(0,num('kwh')),ppk=Math.max(0,num('ppk')),loads=Math.max(0,num('loads'));
 const now=Date.now()-3600000;const H=fc.properties.timeseries.filter(x=>x.data.next_1_hours&&new Date(x.time).getTime()>=now).slice(0,48).map(x=>{const d=x.data.instant.details,n=x.data.next_1_hours;const rain=(n.details&&n.details.precipitation_amount)||0;const p=power(d.air_temperature,d.relative_humidity,d.wind_speed);return{t:new Date(x.time),T:d.air_temperature,RH:d.relative_humidity,u:d.wind_speed,rain,p,c:cls(p,rain)}});
 if(!H.length){$('out').innerHTML='<p class="wd-err">No hourly forecast available.</p>';return}
 const day=x=>{const h=+hh.format(x.t);return h>=8&&h<=17};
 let bi=-1,bs=-1;for(let i=0;i+4<=H.length;i++){const w=H.slice(i,i+4);if(!w.every(day)||w.some(x=>x.rain>0))continue;const s=w.reduce((a,x)=>a+x.p,0);if(s>bs){bs=s;bi=i}}
 const best=bi>=0?H.slice(bi,bi+4):null,avgP=best?bs/4:0,bc=best?cls(avgP,0):['wet','','☔',''];
 let verdict,sub;if(!best){verdict='Not a drying day – keep it indoors';sub='Every daytime window in the next 48 hours has rain or no daylight.'}
 else{verdict=(bc[0]==='great'?'Yes – great drying ':bc[0]==='good'?'Yes – good drying ':bc[0]==='slow'?'Slow drying ':'Poor drying ')+tf.format(best[0].t)+'–'+hh.format(new Date(best[3].t.getTime()+3600000))+':00';
  sub='Average '+nn1(best.reduce((a,x)=>a+x.T,0)/4)+' °C, humidity '+Math.round(best.reduce((a,x)=>a+x.RH,0)/4)+' %, wind '+nn1(best.reduce((a,x)=>a+x.u,0)/4)+' m/s, no rain forecast.'}
 const dryHours=H.filter(x=>day(x)&&x.rain===0&&x.p>=1.5).length,save=kwh*ppk/100;
 let h='<span class="wd-live">📍 '+esc(place)+' · MET Norway forecast · updated '+tf.format(new Date(fc.properties.meta.updated_at))+'</span>';
 h+='<div class="wd-hero"><div class="wd-line">'+shirt(best?bc[0]:'wet')+'</div><div class="wd-verdict"><b>'+verdict+'</b><span>'+sub+'</span></div></div>';
 h+='<div class="wd-strip" role="img" aria-label="Drying power hour by hour">'+H.map((x,i)=>{const lab=+hh.format(x.t),first=i===0||lab===0;return '<div class="wd-h'+(best&&i>=bi&&i<bi+4?' best':'')+(first?' day':'')+'" title="'+tf.format(x.t)+': '+x.c[3]+' · '+nn1(x.T)+' °C · '+Math.round(x.RH)+' % · '+nn1(x.u)+' m/s'+(x.rain?' · '+x.rain+' mm':'')+'"><i style="background:'+x.c[1]+';opacity:'+(day(x)?1:.45)+'"><em>'+x.c[2]+'</em></i>'+(first?'<b>'+dd.format(x.t)+'</b>':'')+String(lab).padStart(2,'0')+'</div>'}).join('')+'</div>';
 h+='<div class="wd-leg"><span><i style="background:#16A34A"></i>Great</span><span><i style="background:#84CC16"></i>Good</span><span><i style="background:#FACC15"></i>Slow</span><span><i style="background:#F97316"></i>Poor</span><span><i style="background:#94A3B8"></i>Rain</span><span>Faded = before 8:00 or after 18:00 · outline = best 4 hours</span></div>';
 h+='<div class="wd-sum"><div><span>Good daylight drying hours (next 48 h)</span><b>'+dryHours+' h</b></div><div><span>Saved per load by not using the dryer</span><b>£'+save.toFixed(2)+'</b><span>'+kwh+' kWh × '+ppk+'p</span></div><div><span>Saved a year if half your loads go outside</span><b>£'+(save*loads/2*52).toFixed(0)+'</b><span>'+loads+' loads a week</span></div></div>';
 h+='<p class="wd-src">Weather: MET Norway Locationforecast (CC BY 4.0). Postcodes: postcodes.io (Open Government Licence). Drying power uses the Penman wind function × vapour pressure deficit; the Great/Good/Slow/Poor bands are Hong Life\'s rule of thumb, not an official forecast.</p>';
 $('out').innerHTML=h}
function nn1(x){return (Math.round(x*10)/10).toFixed(1)}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
async function run(){const id=++busy;$('out').innerHTML='<p>Loading the forecast …</p>';try{if(!pos){const g=await geo($('pc').value);pos={lat:g.lat,lon:g.lon};place=g.label}fc=await load();if(id===busy)draw()}catch(e){if(id===busy)$('out').innerHTML='<p class="wd-err">Could not load the forecast ('+esc(e.message)+'). Check the postcode and try again.</p>'}}
$('go').addEventListener('click',()=>{pos=null;run()});
$('pc').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();pos=null;run()}});
$('me').addEventListener('click',()=>{if(!navigator.geolocation)return;navigator.geolocation.getCurrentPosition(p=>{pos={lat:p.coords.latitude,lon:p.coords.longitude};place='Your location';run()},()=>{$('out').innerHTML='<p class="wd-err">Location not allowed – type a postcode instead.</p>'},{timeout:10000,maximumAge:600000})});
['kwh','ppk','loads'].forEach(id=>$(id).addEventListener('input',draw));
run();
})();
</script>'''

FAQ = [
 ("Will washing dry outside in winter?",
  "Often, yes. Cold air holds little moisture, so on a dry, breezy winter day the air can still be fairly 'thirsty'. What stops drying is high humidity, still air and rain – the hourly strip shows exactly that."),
 ("What does 'drying power' mean?",
  "It is the evaporation the air could drive from a wet surface: the gap between how much moisture the air could hold and how much it holds (vapour pressure deficit), multiplied by the Penman wind function. Higher is faster. We turn it into Great, Good, Slow and Poor bands."),
 ("Why only between 8:00 and 18:00?",
  "The best window is chosen from daytime hours, when most people can hang washing out and bring it in. Night hours are still shown, faded."),
 ("How much does a tumble dryer cost per load?",
  "Energy per load × your unit rate. At the Ofgem price cap average of 26.32p/kWh (1 Oct – 31 Dec 2026), a 2.5 kWh load costs about 66p; a 5 kWh vented dryer load about £1.32."),
 ("Where does the forecast come from?",
  "From the Norwegian Meteorological Institute (MET Norway), which publishes free forecasts for the whole world under CC BY 4.0. Postcodes are turned into a location with postcodes.io."),
]

ART = '''<p><b>In short:</b> type your postcode and the page shows the next 48 hours as coloured blocks – <b>green dries fast, yellow slowly, grey means rain</b> – picks the best four daytime hours to hang washing out, and works out what you save by not using the tumble dryer.</p>
<h2 id="how">How it works</h2>
<ul><li><b>Vapour pressure deficit</b> = saturation vapour pressure at the air temperature × (1 − relative humidity)</li>
<li><b>Drying power</b> = 0.26 × (1 + 0.54 × wind at 2 m) × vapour pressure deficit (Penman, 1948) – in mm of water per day from an open wet surface</li>
<li><b>Bands</b>: rain → Rain; 3 or more → Great; 1.5–3 → Good; 0.5–1.5 → Slow; below 0.5 → Poor</li>
<li><b>Saving per load</b> = dryer kWh per load × unit rate</li></ul>
<h3 id="examples">Examples</h3>
''' + table(['Weather', 'Drying power', 'Band'], [
    ['12 °C, 60 % humidity, wind 5 m/s', '0.26 × (1 + 0.54 × 3.7) × 5.6 hPa ≈ 4.4', 'Great'],
    ['8 °C, 80 % humidity, wind 3 m/s', '0.26 × (1 + 0.54 × 2.2) × 2.1 hPa ≈ 1.2', 'Slow'],
    ['6 °C, 95 % humidity, wind 1 m/s', '0.26 × (1 + 0.54 × 0.7) × 0.5 hPa ≈ 0.2', 'Poor'],
    ['Any temperature, rain forecast', '—', 'Rain'],
]) + '''
<h3 id="cost">What a dryer load costs</h3>
''' + table(['Dryer energy per load', 'At 26.32p/kWh', '4 loads a week for a year'], [
    ['1.5 kWh (heat-pump example)', '39p', '£82'],
    ['2.5 kWh', '66p', '£137'],
    ['4.5 kWh (vented example)', '£1.18', '£246'],
]) + '''
<h3>Tips</h3>
<ul><li>Shake items out and leave space between them so air can move through.</li>
<li>Wind matters more than sunshine: a grey, breezy day can beat a still, sunny one.</li>
<li>Bring washing in before dusk, when humidity rises again.</li></ul>
''' + faq_html(FAQ, heading='FAQ').replace('<h2 style="margin-top:22px">FAQ</h2>', '<h2 id="faq" style="margin-top:22px">FAQ</h2>') + f'''
<p class="note">Sources (checked {DATE_EN}): <a href="https://api.met.no/" rel="nofollow">MET Norway Weather API – Locationforecast (CC BY 4.0)</a>; <a href="https://postcodes.io/" rel="nofollow">postcodes.io (Open Government Licence)</a>; <a href="https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026" rel="nofollow">Ofgem: price cap 1 Oct – 31 Dec 2026</a>; Penman, H.L. (1948) Natural evaporation from open water, bare soil and grass. See also: <a href="/uk/electricity-cost-calculator.html">Electricity cost calculator</a>.</p>'''

TOC = [('form', 'Calculator'), ('how', 'How it works'), ('examples', 'Examples'), ('cost', 'Dryer cost'), ('faq', 'FAQ')]


def main():
    s = open(os.path.join(ORIG, 'uk/electricity-cost-calculator.html'), encoding='utf-8').read()
    old = 'https://honglifecalc.com/uk/electricity-cost-calculator.html'
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + H1, s, count=1)
    s = s.replace(old, URL)
    assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": H1, "url": URL, "description": DESC,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "en-GB",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": "UK calculators", "item": "https://honglifecalc.com/uk/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇬🇧 Live forecast · MET Norway</span>'
               f'<h1>{H1}</h1><p>Will your washing dry outside today? Hour-by-hour drying power for your postcode and the best time to hang it out.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>By <b>Hong Life Calculators</b></span><span>Checked <b>{DATE_EN}</b></span>'
           '<span>Data <b>MET Norway (CC BY 4.0)</b></span></div><details class="card hl-toc" open><summary>On this page</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'locationforecast/2.0/compact' in s and 'id="pc"' in s and 'id="cost"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
