"""US: Turkey thawing & roasting time calculator – USDA FSIS "Let's Talk Turkey" tables (refrigerator thaw 24 h per 4–5 lb,
cold water 30 min per lb, roasting timetable at 325 °F unstuffed/stuffed, 165 °F, 20 min rest, 1–2 days in fridge after thawing).
Template: /us/electricity-cost-calculator.html. Writes overlay/us/turkey-cooking-time-calculator.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/us/turkey-cooking-time-calculator.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Turkey Cooking Time Calculator – Thaw & Roast Schedule (USDA, 325 °F)'
H1 = 'Turkey Thawing & Cooking Time Calculator'
DESC = ('Enter your turkey weight and dinner time: get the USDA roasting time at 325 °F (stuffed or unstuffed), how many days to thaw in the '
        'fridge or hours in cold water, and a timeline that tells you exactly when to start.')
DATE_EN = 'November 25, 2026'

CSS = '''<style id="tk-css">
.app>#form,.app>#out{min-width:0;max-width:100%}@media(max-width:860px){section.app{grid-template-columns:minmax(0,1fr)!important}}
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.tk-row{display:grid;grid-template-columns:1fr 1fr;gap:10px}.tk-row .f{min-width:0}
.tk-seg{display:flex;gap:6px;flex-wrap:wrap}.tk-seg label{flex:1 1 120px;display:flex;align-items:center;gap:6px;border:1px solid #C9D3E3;border-radius:10px;padding:8px 10px;font-size:14px;cursor:pointer;background:#fff;min-width:0}
.tk-seg input{width:18px;height:18px;margin:0;flex:none}
.tk-hero{display:grid;grid-template-columns:120px minmax(0,1fr);gap:14px;align-items:center;background-color:#FFF7ED;border:1px solid #FED7AA;border-radius:16px;padding:12px}
.tk-oven svg{width:120px;height:120px;display:block}
.tk-glow{animation:tkg 1.8s ease-in-out infinite}@keyframes tkg{50%{opacity:.45}}
.tk-merc{transform-origin:bottom;transform-box:fill-box;animation:tkm 2.4s ease-out both}@keyframes tkm{from{transform:scaleY(.08)}to{transform:scaleY(1)}}
.tk-big small{display:block;font-size:12.5px;color:#7C2D12}.tk-big b{display:block;font-size:30px;line-height:1.1;color:#9A3412;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.tk-big span{display:block;font-size:13.5px;color:#3a3a3c;margin-top:4px}
.tk-tl{list-style:none;margin:14px 0 0;padding:0;position:relative}
.tk-tl:before{content:"";position:absolute;left:15px;top:6px;bottom:6px;width:3px;border-radius:3px;background-color:#FED7AA}
.tk-tl li{position:relative;padding:0 0 12px 42px;min-width:0;opacity:0;animation:tki .4s ease forwards}
@keyframes tki{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}
.tk-tl li i{position:absolute;left:2px;top:0;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:16px;background-color:#fff;border:2px solid #FDBA74}
.tk-tl b{display:block;font-size:15px;color:#12305C;overflow-wrap:anywhere}.tk-tl span{display:block;font-size:13px;color:#5B6B82;overflow-wrap:anywhere}
.tk-sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0}
.tk-sum div{background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:12px;padding:9px 11px;min-width:0}
.tk-sum b{display:block;font-size:17px;color:#12305C;overflow-wrap:anywhere}.tk-sum span{font-size:12px;color:#5B6B82}
.tk-warn{background-color:#FEF2F2;border:1px solid #FECACA;border-radius:12px;padding:10px 12px;font-size:14px;color:#7F1D1D;margin:8px 0}
.tk-ok{background-color:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;padding:10px 12px;font-size:14px;color:#1E3A8A;margin:8px 0}
.tk-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
@media(max-width:600px){.tk-row,.tk-sum{grid-template-columns:1fr}.tk-hero{grid-template-columns:86px minmax(0,1fr);gap:10px}.tk-oven svg{width:86px;height:86px}.tk-big b{font-size:24px}}
@media(prefers-reduced-motion:reduce){.tk-glow,.tk-merc,.tk-tl li{animation:none;opacity:1}}
</style>'''

FORM = '''<form class="card" id="form" onsubmit="return false"><h2>Your turkey</h2>
<div class="tk-row"><label class="f"><span>Weight</span><input id="w" inputmode="decimal" value="16"></label>
<label class="f"><span>Unit</span><select id="u"><option value="lb">pounds (lb)</option><option value="kg">kilograms (kg)</option></select></label></div>
<div class="f"><span>Stuffing inside the bird?</span><div class="tk-seg"><label><input type="radio" name="st" value="0" checked>Unstuffed</label><label><input type="radio" name="st" value="1">Stuffed</label></div></div>
<div class="f"><span>Turkey is now</span><div class="tk-seg"><label><input type="radio" name="th" value="fridge" checked>Frozen – thaw in fridge</label><label><input type="radio" name="th" value="water">Frozen – cold water</label><label><input type="radio" name="th" value="fresh">Fresh / thawed</label></div></div>
<label class="f"><span>Dinner time</span><input id="dt" type="datetime-local" value="2026-12-25T17:00"><small>We count back from here: 20 minutes rest, roasting time, thawing.</small></label>
</form><section class="card" id="out" aria-live="polite"><p>Calculating …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=v=>{const n=parseFloat(String(v).replace(',','.').replace(/[^0-9.]/g,''));return isFinite(n)?n:0};
// USDA FSIS roasting timetable, 325 °F (hours): [maxLb, min, max]
const UN=[[8,1.5,3.25],[12,2.75,3],[14,3,3.75],[18,3.75,4.25],[20,4.25,4.5],[24,4.5,5]];
const STF=[[6,null,null],[8,2.5,3.5],[12,3,3.5],[14,3.5,4],[18,4,4.25],[20,4.25,4.75],[24,4.75,5.25]];
const rad=n=>(document.querySelector('input[name="'+n+'"]:checked')||{}).value;
const hm=h=>{const m=Math.round(h*60);return Math.floor(m/60)+' h'+(m%60?' '+(m%60)+' min':'')};
const df=new Intl.DateTimeFormat('en-US',{weekday:'short',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
const dd=new Intl.DateTimeFormat('en-US',{weekday:'short',month:'short',day:'numeric'});
function draw(){const kg=$('u').value==='kg',w=num($('w').value),lb=kg?w*2.20462:w,stuffed=rad('st')==='1',th=rad('th');
 const dinner=new Date($('dt').value);
 if(!lb||isNaN(dinner)){$('out').innerHTML='<p>Enter the weight and dinner time.</p>';return}
 const T=stuffed?STF:UN,row=T.find(r=>lb<=r[0]+1e-9);
 if(lb<4||!row){$('out').innerHTML='<div class="tk-warn">The USDA roasting table covers turkeys from 4 to 24 pounds (about 1.8 to 10.9 kg). For '+(kg?w+' kg':w+' lb')+', follow the label or the USDA Meat and Poultry Hotline (1-888-674-6854), and always check 165 °F with a food thermometer.</div>';return}
 if(row[1]==null){$('out').innerHTML='<div class="tk-warn">USDA lists stuffed turkey breasts of 4 to 6 pounds as "not usually applicable". Roast it unstuffed and cook the stuffing in a separate dish.</div>';return}
 const rest=20/60,roastStart=new Date(dinner-((row[2]+rest)*3600000)),check=new Date(dinner-((row[2]-row[1]+rest)*3600000)),ovenOut=new Date(dinner-rest*3600000);
 let thawH=0,thawStart=null,thawTxt='';
 if(th==='fridge'){thawH=Math.ceil(lb/4)*24;thawStart=new Date(roastStart-thawH*3600000);thawStart.setHours(8,0,0,0);thawTxt='Move the frozen turkey to the fridge (40 °F or below) – about '+Math.ceil(lb/4)+' day'+(Math.ceil(lb/4)>1?'s':'')+' (24 h per 4–5 lb)'}
 if(th==='water'){thawH=lb*0.5;thawStart=new Date(roastStart-Math.ceil(thawH*2)/2*3600000-1800000);thawTxt='Cold-water thaw in the wrapper, breast down, changing the water every 30 min – about '+hm(lb*0.5)+'. Cook right after thawing.'}
 const now=new Date(),late=thawStart&&thawStart<now;
 const pct=Math.min(1,lb/24);
 let h='<div class="tk-hero"><div class="tk-oven"><svg viewBox="0 0 120 120" aria-hidden="true"><rect x="8" y="14" width="104" height="96" rx="12" fill="#334155"/><rect x="8" y="14" width="104" height="18" rx="9" fill="#475569"/><circle cx="26" cy="23" r="4" fill="#F8FAFC"/><circle cx="40" cy="23" r="4" fill="#F8FAFC"/><rect class="tk-glow" x="18" y="40" width="84" height="60" rx="8" fill="#F97316" opacity=".85"/><ellipse cx="60" cy="80" rx="'+(16+14*pct).toFixed(1)+'" ry="'+(10+8*pct).toFixed(1)+'" fill="#B45309"/><ellipse cx="'+(52-6*pct).toFixed(1)+'" cy="'+(74-4*pct).toFixed(1)+'" rx="7" ry="4" fill="#D97706" opacity=".8"/><rect x="96" y="44" width="8" height="52" rx="4" fill="#fff"/><rect class="tk-merc" x="98" y="52" width="4" height="42" rx="2" fill="#DC2626"/><text x="100" y="40" font-size="8" fill="#fff" text-anchor="middle">165°</text></svg></div>'
 +'<div class="tk-big"><small>Roast at 325 °F ('+(stuffed?'stuffed':'unstuffed')+', '+(kg?w+' kg = '+lb.toFixed(1)+' lb':lb+' lb')+')</small><b>'+hm(row[1])+' – '+hm(row[2])+'</b><span>USDA range for '+(T[T.indexOf(row)-1]?T[T.indexOf(row)-1][0]:4)+'–'+row[0]+' lb. Done at 165 °F in the thickest part of the breast, the innermost wing and the innermost thigh'+(stuffed?', and 165 °F in the center of the stuffing':'')+'.</span></div></div>';
 if(late)h+='<div class="tk-warn">⚠️ To thaw in time you should have started on <b>'+df.format(thawStart)+'</b>. '+(th==='fridge'?'Switch to the cold-water method or move dinner later.':'Move dinner later.')+'</div>';
 else if(th==='fridge')h+='<div class="tk-ok">A thawed turkey keeps 1–2 days in the fridge, so starting a day early is fine.</div>';
 const ev=[];
 if(thawStart)ev.push(['🧊',df.format(thawStart),thawTxt]);
 ev.push(['🔥',df.format(roastStart),'Turkey into a 325 °F oven ('+hm(row[2])+' before it must come out)']);
 ev.push(['🌡️',df.format(check),'Start checking with a food thermometer (earliest USDA time, '+hm(row[1])+')']);
 ev.push(['⏸️',df.format(ovenOut),'Out of the oven at 165 °F – rest 20 minutes before carving']);
 ev.push(['🍽️',df.format(dinner),'Dinner']);
 h+='<ol class="tk-tl">'+ev.map((e,i)=>'<li style="animation-delay:'+(i*0.12)+'s"><i>'+e[0]+'</i><b>'+e[1]+'</b><span>'+e[2]+'</span></li>').join('')+'</ol>';
 h+='<div class="tk-sum"><div><span>Fridge thaw</span><b>'+Math.ceil(lb/5)+'–'+Math.ceil(lb/4)+' days</b><span>24 h per 4–5 lb</span></div><div><span>Cold-water thaw</span><b>'+hm(lb*0.5)+'</b><span>30 min per lb</span></div><div><span>Oven + rest</span><b>'+hm(row[2]+rest)+'</b><span>longest time + 20 min</span></div></div>';
 h+='<p class="tk-src">Times: USDA Food Safety and Inspection Service, "Let’s Talk Turkey" (thawing guide and roasting timetable at 325 °F). Times are approximate – the food thermometer decides.</p>';
 $('out').innerHTML=h}
['w','dt'].forEach(i=>$(i).addEventListener('input',draw));$('u').addEventListener('change',()=>{const v=num($('w').value);if(v)$('w').value=$('u').value==='kg'?(v/2.20462).toFixed(1):(v*2.20462).toFixed(1);draw()});
document.querySelectorAll('#form input[type=radio]').forEach(r=>r.addEventListener('change',draw));draw();
})();
</script>'''

FAQ = [
 ("How long does it take to cook a turkey?",
  "At 325 °F, USDA times for an unstuffed turkey are 2¾–3 hours for 8–12 lb, 3–3¾ hours for 12–14 lb, 3¾–4¼ hours for 14–18 lb, 4¼–4½ hours for 18–20 lb and 4½–5 hours for 20–24 lb. A stuffed turkey takes about 15–45 minutes longer."),
 ("How long does it take to thaw a turkey in the fridge?",
  "USDA: about 24 hours for every 4 to 5 pounds in a refrigerator at 40 °F or below – 1–3 days for 4–12 lb, 3–4 days for 12–16 lb, 4–5 days for 16–20 lb and 5–6 days for 20–24 lb. A thawed turkey can stay in the fridge 1–2 days."),
 ("Can I thaw a turkey in cold water?",
  "Yes. Keep it in its wrapper, submerge it in cold tap water and change the water every 30 minutes. Allow about 30 minutes per pound (6–8 hours for 12–16 lb) and cook it immediately after thawing. Do not refreeze."),
 ("What temperature is a turkey done?",
  "165 °F, measured with a food thermometer in the thickest part of the breast, the innermost part of the wing and the innermost part of the thigh. If stuffed, the center of the stuffing must also reach 165 °F. Let it stand 20 minutes before carving."),
 ("Can I cook a turkey from frozen?",
  "Yes, USDA says a turkey can be cooked from frozen, but it takes at least 50 percent longer than a thawed one. This calculator plans for a thawed turkey."),
]

ART = '''<p><b>In short:</b> enter the weight, whether it is stuffed, whether it is still frozen, and when you want to eat. You get the <b>USDA roasting time at 325 °F</b>, the <b>thawing time</b> and a <b>timeline</b>: when to put it in the fridge, when it goes in the oven, when to start checking the thermometer and when to take it out.</p>
<h2 id="how">How it works</h2>
<ul><li><b>Roasting time</b> from the USDA timetable for 325 °F (unstuffed or stuffed)</li>
<li><b>Oven start</b> = dinner − 20 minutes rest − the longest time in the range</li>
<li><b>Fridge thaw</b> = 24 hours per 4 lb (the safe end of USDA's 4–5 lb), started in the morning</li>
<li><b>Cold-water thaw</b> = 30 minutes per pound</li></ul>
<h3 id="tables">USDA roasting timetable (325 °F)</h3>
''' + table(['Weight', 'Unstuffed', 'Stuffed'], [
    ['4 to 6 lb (breast)', '1½ to 3¼ hours (4–8 lb)', 'Not usually applicable'],
    ['6 to 8 lb (breast)', '1½ to 3¼ hours (4–8 lb)', '2½ to 3½ hours'],
    ['8 to 12 lb', '2¾ to 3 hours', '3 to 3½ hours'],
    ['12 to 14 lb', '3 to 3¾ hours', '3½ to 4 hours'],
    ['14 to 18 lb', '3¾ to 4¼ hours', '4 to 4¼ hours'],
    ['18 to 20 lb', '4¼ to 4½ hours', '4¼ to 4¾ hours'],
    ['20 to 24 lb', '4½ to 5 hours', '4¾ to 5¼ hours'],
]) + '''
<h3 id="thaw">USDA thawing times</h3>
''' + table(['Weight', 'In the refrigerator', 'In cold water'], [
    ['4 to 12 lb', '1 to 3 days', '2 to 6 hours'],
    ['12 to 16 lb', '3 to 4 days', '6 to 8 hours'],
    ['16 to 20 lb', '4 to 5 days', '8 to 10 hours'],
    ['20 to 24 lb', '5 to 6 days', '10 to 12 hours'],
]) + '''
''' + faq_html(FAQ, heading='FAQ').replace('<h2 style="margin-top:22px">FAQ</h2>', '<h2 id="faq" style="margin-top:22px">FAQ</h2>') + f'''
<p class="note">Source (checked {DATE_EN}): <a href="https://www.fsis.usda.gov/es/node/3307" rel="nofollow">USDA Food Safety and Inspection Service: Let's Talk Turkey – A Consumer Guide to Safely Roasting a Turkey</a>. See also: <a href="/us/white-christmas-chance.html">White Christmas chance by city</a> · <a href="/us/santa-speed-calculator.html">How fast does Santa fly?</a></p>'''

TOC = [('form', 'Calculator'), ('how', 'How it works'), ('tables', 'Roasting table'), ('thaw', 'Thawing table'), ('faq', 'FAQ')]
HERO = ('🦃 USDA food safety tables', 'Weight + dinner time = when to thaw, when to roast, when to carve.')
BY = 'USDA FSIS'
CHECK = ('id="dt"', 'id="tables"', 'id="thaw"')


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
