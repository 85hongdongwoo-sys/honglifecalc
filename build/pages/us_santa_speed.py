"""US/EN fun science: How fast does Santa have to fly? Children 0–14 worldwide from the World Bank API (SP.POP.0014.TO, called live
from the browser, CORS ok; fallback = 2025 value 2,005,307,782), Earth land area 148.94 million km² (CIA World Factbook),
time zones UTC+14 to UTC−12 (26 h spread). Template: /us/electricity-cost-calculator.html. Writes overlay/us/santa-speed-calculator.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/us/santa-speed-calculator.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'How Fast Does Santa Fly? Santa Speed Calculator (Christmas 2026)'
H1 = 'How Fast Does Santa Have to Fly?'
DESC = ('Santa speed calculator: with the World Bank count of children on Earth, 26 hours of time zones and the land area of the planet, '
        'work out how fast the sleigh must go, how many homes per second and how long Santa can stay at each house.')
DATE_EN = 'November 25, 2026'

CSS = '''<style id="ss-css">
.app>#form,.app>#out{min-width:0;max-width:100%}@media(max-width:860px){section.app{grid-template-columns:minmax(0,1fr)!important}}
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.ss-row{display:grid;grid-template-columns:1fr 1fr;gap:10px}.ss-row .f{min-width:0}
.ss-sky{position:relative;height:170px;border-radius:18px;overflow:hidden;background-color:#0B1B3A;background-image:linear-gradient(180deg,#0B1B3A 0%,#1E2F63 100%)}
.ss-sky canvas{position:absolute;inset:0;width:100%;height:100%}
.ss-moon{position:absolute;right:18px;top:14px;width:38px;height:38px;border-radius:50%;background-color:#FEF3C7;box-shadow:0 0 24px rgba(254,243,199,.6)}
.ss-big{display:grid;grid-template-columns:minmax(0,1fr) 150px;gap:14px;align-items:center;margin:12px 0}
.ss-big small{display:block;font-size:12.5px;color:#5B6B82}.ss-big b{display:block;font-size:32px;line-height:1.1;color:#9F1239;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.ss-big span{display:block;font-size:14px;color:#3a3a3c;margin-top:4px}
.ss-g svg{width:150px;height:95px;display:block}.ss-g .nd{transition:transform 1.4s cubic-bezier(.2,.8,.2,1);transform-origin:75px 82px}
.ss-sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0}
.ss-sum div{background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:12px;padding:9px 11px;min-width:0}
.ss-sum b{display:block;font-size:17px;color:#12305C;overflow-wrap:anywhere}.ss-sum span{font-size:12px;color:#5B6B82}
.ss-cmp{display:flex;flex-direction:column;gap:6px;margin-top:8px}
.ss-c{display:grid;grid-template-columns:minmax(0,10em) minmax(0,1fr) minmax(0,6.5em);gap:8px;align-items:center;font-size:13px}
.ss-c span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ss-c i{display:block;height:12px;border-radius:999px;background-color:#CBD5E1;min-width:3px;transition:width 1.2s ease}
.ss-c.me i{background-color:#BE123C}.ss-c.me span{font-weight:800}.ss-c em{font-style:normal;text-align:right;font-variant-numeric:tabular-nums}
.ss-live{display:inline-flex;gap:6px;font-size:12.5px;font-weight:700;color:#1f4f8a;background-color:#EAF1FB;border:1px solid #CFDDF3;border-radius:999px;padding:2px 10px;margin:0 0 10px;max-width:100%;flex-wrap:wrap}
.ss-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
.ss-btn{border:1px solid #C9D3E3;background:#fff;border-radius:10px;padding:8px 12px;font:inherit;font-size:14px;cursor:pointer;min-height:40px;margin-top:8px}
@media(max-width:600px){.ss-row,.ss-sum{grid-template-columns:1fr}.ss-big{grid-template-columns:minmax(0,1fr) 110px}.ss-g svg{width:110px;height:70px}.ss-big b{font-size:26px}.ss-c{grid-template-columns:minmax(0,7.5em) minmax(0,1fr) minmax(0,6em)}}
</style>'''

FORM = '''<form class="card" id="form" onsubmit="return false"><h2>Santa's Christmas Eve</h2>
<label class="f"><span>Children on Earth (age 0–14)</span><input id="kids" inputmode="numeric" value="2,005,307,782"><small id="kidsrc">World Bank, 2025 estimate. Change it if you like.</small></label>
<div class="ss-row"><label class="f"><span>Share Santa visits (%)</span><input id="share" inputmode="decimal" value="100"><small>Lower it to count only children who celebrate Christmas – your choice.</small></label>
<label class="f"><span>Children per home</span><input id="per" inputmode="decimal" value="2"><small>Your guess. More children per home = fewer stops.</small></label></div>
<div class="ss-row"><label class="f"><span>Hours of night in each time zone</span><input id="night" inputmode="decimal" value="8"><small>e.g. 10 pm to 6 am = 8 hours</small></label>
<label class="f"><span>Units</span><select id="unit"><option value="mi">miles, mph</option><option value="km">km, km/h</option></select></label></div>
</form><section class="card" id="out" aria-live="polite"><p>Calculating …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=v=>{const n=parseFloat(String(v).replace(/[^0-9.]/g,''));return isFinite(n)?n:0};
const LAND=148940000,SPREAD=26,C=299792.458,SOUND=0.343; // km², h, km/s, km/s (20 °C)
const REF=[['Speed of sound',0.343],['Rifle bullet (about)',1],['Space Station',7.66],['Parker Solar Probe record',191.7],['Speed of light',C]];
function fmt(n,d){return n.toLocaleString('en-US',{maximumFractionDigits:d==null?0:d})}
function big(n){if(n>=1e9)return fmt(n/1e9,2)+' billion';if(n>=1e6)return fmt(n/1e6,1)+' million';return fmt(n)}
let fly=0,pct=0;
function sky(){const c=$('sky'),x=c.getContext('2d'),dp=devicePixelRatio||1,r=c.getBoundingClientRect(),w=r.width,h=r.height;c.width=w*dp;c.height=h*dp;x.setTransform(dp,0,0,dp,0,0);
 const S=Array.from({length:60},()=>[Math.random()*w,Math.random()*h*0.8,Math.random()*1.4+.3,Math.random()*6]),red=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const id=++fly;let t0=null;
 (function fr(t){if(id!==fly)return;if(t0==null)t0=t;x.clearRect(0,0,w,h);
  S.forEach(s=>{x.globalAlpha=.4+.6*Math.abs(Math.sin(t/900+s[3]));x.fillStyle='#fff';x.fillRect(s[0],s[1],s[2],s[2])});x.globalAlpha=1;
  // roofs
  x.fillStyle='#0A1430';for(let i=0;i<w;i+=46){const hh=26+((i*7)%22);x.fillRect(i,h-hh,40,hh);x.beginPath();x.moveTo(i-3,h-hh);x.lineTo(i+20,h-hh-14);x.lineTo(i+43,h-hh);x.fill();x.fillStyle='#FCD34D';x.fillRect(i+8,h-hh+8,7,7);x.fillStyle='#0A1430'}
  const per=Math.max(900,4200-pct*3000),p=red?0.55:(((t-t0)%per)/per),sx=-90+p*(w+180),sy=h*0.32+Math.sin(p*6.28)*10;
  // streak
  const g=x.createLinearGradient(sx-140,0,sx,0);g.addColorStop(0,'rgba(253,224,71,0)');g.addColorStop(1,'rgba(253,224,71,.9)');x.strokeStyle=g;x.lineWidth=3;x.beginPath();x.moveTo(sx-140,sy+8);x.lineTo(sx,sy+8);x.stroke();
  x.font='30px serif';x.fillText('🦌',sx+16,sy+12);x.fillText('🛷',sx-22,sy+18);
  if(!red)requestAnimationFrame(fr)})(performance.now())}
function draw(){const mi=$('unit').value==='mi',K=mi?0.621371:1,U=mi?'mi':'km',kids=num($('kids').value),share=Math.min(100,num($('share').value))/100,per=Math.max(0.1,num($('per').value)),night=Math.max(0,num($('night').value));
 const homes=kids*share/per,hrs=SPREAD+night,sec=hrs*3600;
 if(!homes||!sec){$('res').innerHTML='<p>Enter the number of children and hours.</p>';return}
 const gap=Math.sqrt(LAND/homes),dist=homes*gap,v=dist/sec; // km, km, km/s
 pct=Math.min(1,Math.log10(v/0.343+1)/4);
 const ang=-90+180*Math.min(1,Math.log10(v/0.343)/Math.log10(C/0.343));
 let h='<div class="ss-big"><div><small>Santa's average speed</small><b>'+fmt(v*K,0)+' '+U+'/s</b><span>'+fmt(v*3600*K)+' '+(mi?'mph':'km/h')+' · Mach '+fmt(v/SOUND)+' · '+fmt(v/C*100,2)+'% of the speed of light</span></div>'
 +'<div class="ss-g"><svg viewBox="0 0 150 95" aria-hidden="true"><path d="M12 82 A63 63 0 0 1 138 82" fill="none" stroke="#E2E8F0" stroke-width="12" stroke-linecap="round"/><path d="M12 82 A63 63 0 0 1 138 82" fill="none" stroke="#BE123C" stroke-width="12" stroke-linecap="round" stroke-dasharray="198" stroke-dashoffset="'+(198*(1-(ang+90)/180)).toFixed(1)+'"/><g class="nd" id="nd" style="transform:rotate(-90deg)"><line x1="75" y1="82" x2="75" y2="30" stroke="#0F172A" stroke-width="4" stroke-linecap="round"/></g><circle cx="75" cy="82" r="7" fill="#0F172A"/><text x="12" y="94" font-size="9" fill="#64748B">sound</text><text x="118" y="94" font-size="9" fill="#64748B">light</text></svg></div></div>';
 h+='<div class="ss-sum"><div><span>Homes to visit</span><b>'+big(homes)+'</b><span>'+fmt(kids*share)+' children ÷ '+per+' per home</span></div>'
 +'<div class="ss-sum-x"></div><div><span>Homes per second</span><b>'+fmt(homes/sec)+'</b><span>over '+fmt(hrs,1)+' hours of Christmas night</span></div>'
 +'<div><span>Time at each home</span><b>'+fmt(sec/homes*1e6,1)+' µs</b><span>microseconds – a blink takes ~100,000 µs</span></div></div>';
 h=h.replace('<div class="ss-sum-x"></div>','');
 h+='<div class="ss-sum"><div><span>Distance between homes</span><b>'+fmt(gap*1000*(mi?3.28084:1))+' '+(mi?'ft':'m')+'</b><span>homes spread evenly over all land</span></div><div><span>Total trip</span><b>'+big(dist*K)+' '+U+'</b><span>'+fmt(dist/384400)+' trips to the Moon</span></div><div><span>Time zones crossed</span><b>26 hours</b><span>from UTC+14 (Kiribati) to UTC−12</span></div></div>';
 const all=REF.concat([['🎅 Santa',v]]).sort((a,b)=>a[1]-b[1]),mx=Math.log10(C/0.2);
 h+='<p style="margin:12px 0 2px;font-size:14px"><b>Compared with fast things</b> (log scale):</p><div class="ss-cmp">'+all.map(r=>'<div class="ss-c'+(r[0].includes('Santa')?' me':'')+'"><span>'+r[0]+'</span><i style="width:'+Math.max(2,Math.log10(r[1]/0.2)/mx*100).toFixed(1)+'%"></i><em>'+(r[1]*K>=10?fmt(r[1]*K):fmt(r[1]*K,2))+' '+U+'/s</em></div>').join('')+'</div>';
 h+='<p class="ss-src">Model: homes spread evenly over Earth\'s land area (148.94 million km², CIA World Factbook); distance between homes = √(land ÷ homes); Santa visits every home once and flies across 26 hours of time zones plus your night length. A fun estimate, not physics advice for reindeer.</p>';
 $('res').innerHTML=h;requestAnimationFrame(()=>{const n=$('nd');if(n)n.style.transform='rotate('+ang.toFixed(1)+'deg)'})}
$('out').innerHTML='<span class="ss-live" id="live">🌍 Children count: World Bank</span><div class="ss-sky"><canvas id="sky"></canvas><div class="ss-moon"></div></div><div id="res"></div><button type="button" class="ss-btn" id="sh">🔗 Share this result</button>';
sky();addEventListener('resize',()=>sky());
['kids','share','per','night'].forEach(i=>$(i).addEventListener('input',draw));$('unit').addEventListener('change',draw);draw();
$('sh').onclick=()=>{const t='Santa has to fly about '+$('res').querySelector('.ss-big b').textContent+' to reach every home on Christmas Eve!';const u=location.href.split('#')[0];if(navigator.share)navigator.share({title:'How fast does Santa fly?',text:t,url:u}).catch(()=>{});else if(navigator.clipboard)navigator.clipboard.writeText(t+' '+u).then(()=>{$('sh').textContent='✅ Copied'})};
fetch('https://api.worldbank.org/v2/country/WLD/indicator/SP.POP.0014.TO?format=json&mrv=1').then(r=>r.json()).then(j=>{const x=j&&j[1]&&j[1][0];if(x&&x.value&&$('kids').value==='2,005,307,782'){$('kids').value=Math.round(x.value).toLocaleString('en-US');$('kidsrc').textContent='World Bank, '+x.date+' estimate (live). Change it if you like.';$('live').textContent='🌍 Children count: World Bank '+x.date+' (live)';draw()}}).catch(()=>{});
})();
</script>'''

FAQ = [
 ("How many children are there in the world?",
  "The World Bank estimates about 2.0 billion children aged 0–14 on Earth (2,005,307,782 for 2025, indicator SP.POP.0014.TO). The calculator loads the latest value live."),
 ("How long is Christmas night for Santa?",
  "Time zones on Earth span 26 hours, from UTC+14 (Line Islands, Kiribati) to UTC−12. If Santa starts when night begins in the first time zone and finishes when it ends in the last one, he gets 26 hours plus the length of one night – 34 hours with an 8-hour night."),
 ("How is the distance worked out?",
  "Homes are spread evenly over Earth's land area of 148.94 million km². The distance between neighbouring homes is the square root of (land area ÷ number of homes), and the whole trip is that distance times the number of homes."),
 ("So how fast is Santa?",
  "With every child aged 0–14, two children per home and an 8-hour night, about 1 billion homes in 34 hours: roughly 3,160 km (about 1,960 miles) per second – over 9,000 times the speed of sound, but only about 1% of the speed of light."),
 ("Is this real science?",
  "The numbers (children, land area, time zones, speeds of sound, the Space Station and light) are real; the even spread of homes and a non-stop flight are simplifications. It is a fun way to practise speed = distance ÷ time."),
]

ART = '''<p><b>In short:</b> Santa has about a billion homes to visit in roughly a day and a half. Enter how many children he visits, how many live in each home and how long the night is, and the calculator shows his <b>speed</b>, <b>homes per second</b> and <b>time at each house</b> – with a speedometer from the speed of sound to the speed of light.</p>
<h2 id="how">How it works</h2>
<ul><li><b>Homes</b> = children × share visited ÷ children per home</li>
<li><b>Time</b> = 26 hours of time zones + length of one night</li>
<li><b>Distance</b> = homes × √(148.94 million km² ÷ homes)</li>
<li><b>Speed</b> = distance ÷ time</li></ul>
<h3 id="examples">Examples (8-hour night, 34 hours in total)</h3>
''' + table(['Children visited', 'Per home', 'Homes', 'Speed'], [
    ['2.0 billion (all 0–14)', '2', '1.003 billion', 'about 3,160 km/s (≈ 1,960 mi/s)'],
    ['2.0 billion', '3', '668 million', 'about 2,580 km/s (≈ 1,600 mi/s)'],
    ['1.0 billion (half)', '2', '501 million', 'about 2,230 km/s (≈ 1,390 mi/s)'],
]) + '''
<h3 id="speeds">Reference speeds used</h3>
''' + table(['Thing', 'Speed'], [
    ['Speed of sound (air, 20 °C)', '343 m/s'],
    ['International Space Station', 'about 7.66 km/s (17,100 mph)'],
    ['Parker Solar Probe (record, Dec 2024)', 'about 191.7 km/s (430,000 mph)'],
    ['Speed of light', '299,792.458 km/s'],
]) + '''
''' + faq_html(FAQ, heading='FAQ').replace('<h2 style="margin-top:22px">FAQ</h2>', '<h2 id="faq" style="margin-top:22px">FAQ</h2>') + f'''
<p class="note">Sources (checked {DATE_EN}): <a href="https://data.worldbank.org/indicator/SP.POP.0014.TO" rel="nofollow">World Bank: Population ages 0–14, total</a>; <a href="https://www.cia.gov/the-world-factbook/countries/world/" rel="nofollow">CIA World Factbook: World (land area)</a>; <a href="https://www.nasa.gov/international-space-station/" rel="nofollow">NASA: International Space Station</a>; <a href="https://www.nasa.gov/mission/parker-solar-probe/" rel="nofollow">NASA: Parker Solar Probe</a>. See also: <a href="/us/white-christmas-chance.html">White Christmas chance by city</a>.</p>'''

TOC = [('form', 'Calculator'), ('how', 'How it works'), ('examples', 'Examples'), ('speeds', 'Speeds'), ('faq', 'FAQ')]
HERO = ('🎅 Fun science · World Bank data', 'How many homes, how many hours – and how fast the sleigh must go.')
BY = 'World Bank'
CHECK = ('id="kids"', 'id="speeds"')


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
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">' + HERO[0] + '</span>'
               f'<h1>{H1}</h1><p>{HERO[1]}</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>By <b>Hong Life Calculators</b></span><span>Checked <b>{DATE_EN}</b></span>'
           '<span>Data <b>' + BY + '</b></span></div><details class="card hl-toc" open><summary>On this page</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert all(c in s for c in CHECK) and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
