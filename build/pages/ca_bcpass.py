"""Canada (BC): mountain-pass trip planner — fuel cost, winter-tire date check, summit elevation chart and live DriveBC highway cameras.
Camera list taken from DriveBC's public webcam API on 24 Nov 2026 (images: www.drivebc.ca/images/{id}.jpg; BC government open data).
Winter tire rules: gov.bc.ca winter driving pages (checked 24 Nov 2026)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from livecam_kit import make, table

# id, name, elevation (m) — one camera per location, ordered along the route
ROUTES = {
 'coq': ('Coquihalla (Hwy 5) – Hope to Kamloops', 200, [(666, 'Portia', 635), (675, 'Box Canyon', 849), (2, 'Great Bear Snowshed', 980), (676, 'Zopkios', 1208), (685, 'Coquihalla Summit', 1230), (161, 'Coquihalla Lakes', 1193), (657, 'Mine Creek', 1084), (58, 'Larson Hill', 1025), (287, 'Comstock', 990), (56, 'Helmer Lake', 1385), (1056, 'Hwy 5 at Hwy 97D', 1330), (61, 'Walloper', 1300)]),
 'rog': ('Rogers Pass (Hwy 1) – Revelstoke to Golden', 148, [(11, 'Revelstoke', 450), (486, 'Albert Canyon', 658), (1161, 'Jack McDonald Snowshed', 910), (101, 'Rogers Pass', 1335), (487, 'Quartz Creek', 1080), (385, 'Donald Bridge', 780), (901, 'Golden', 803), (214, 'Kicking Horse Canyon', 1131)]),
 's2s': ('Sea-to-Sky (Hwy 99) – Vancouver to Whistler', 120, [(21, 'Taylor Way (West Vancouver)', 14), (766, 'Lions Bay', 66), (180, 'Furry Creek', 107), (521, 'Britannia', 13), (1062, 'Valley Drive (Squamish)', 13), (665, 'Alice Lake', 144), (690, 'Culliton', 313), (691, 'Daisy Lake', 369), (178, 'Function Junction', 600), (528, 'Whistler Village Gate', 674)]),
 'duf': ('Duffey Lake Road (Hwy 99) – Pemberton to Lillooet', 100, [(599, 'Pemberton', 209), (182, 'Duffey Lake Road', 1279), (206, 'Lillooet–Fountain Valley', 340)]),
 'h3w': ('Hope–Princeton (Hwy 3, Allison Pass)', 133, [(383, 'Hwy 3/5 Junction', 258), (467, 'Hope Slide', 734), (1112, 'Allison Pass', 1343), (1065, 'Similkameen Falls', 988), (1155, 'Sunday Summit', 1289), (452, 'Princeton', 700)]),
 'h3e': ('Salmo–Creston (Hwy 3, Kootenay Pass)', 84, [(158, 'Salmo', 671), (5, 'Kootenay Pass', 1781), (1151, 'Creston', 586)]),
 'c97': ('Okanagan Connector (Hwy 97C) – Merritt to West Kelowna', 108, [(370, 'Aspen Grove', 1071), (868, 'Pothole Lake', 1045), (194, 'Elkhart', 1621), (251, 'Pennask Summit', 1717), (497, 'Brenda Mine', 1271)]),
 'mal': ('Malahat Drive (Hwy 1) – Victoria to Mill Bay', 40, [(974, 'Goldstream', 13), (927, 'Tunnel Hill', 133), (424, 'Malahat Summit', 341), (8, 'Malahat Drive', 327), (664, 'Bamberton', 149), (396, 'Mill Bay', 28)]),
}
OPTS = ''.join(f'<option value="{k}"{" selected" if k == "coq" else ""}>{v[0]}</option>' for k, v in ROUTES.items())
RJS = json.dumps({k: {'n': v[0], 'km': v[1], 'c': v[2]} for k, v in ROUTES.items()}, ensure_ascii=False)

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Your mountain drive</h2>
<label class="f"><span>Route</span><select id="rt">{OPTS}</select></label>
<div class="lc-row"><label class="f"><span>Distance one way (km)</span><input id="km" inputmode="decimal" value="200"><small>Filled in with an approximate distance for the route – change it to your own trip.</small></label>
<label class="f"><span>Trips</span><select id="rtp"><option value="1">One way</option><option value="2" selected>Return</option></select></label></div>
<div class="lc-row"><label class="f"><span>Fuel consumption (L/100 km)</span><input id="lk" inputmode="decimal" value="9"><small>Climbing passes uses more fuel than city driving.</small></label>
<label class="f"><span>Gas price ($/L)</span><input id="gp" inputmode="decimal" value="1.75"><small>Example – enter the price at your station.</small></label></div>
<label class="f"><span>Travel date</span><input id="dt" type="date"></label>
</form><section class="card" id="out" aria-live="polite"></section>
<section class="card" id="cams"><h2 id="cameras">Live DriveBC highway cameras on this route</h2><div id="camgrid"></div></section>'''

JS = r'''
const R=''' + RJS + r''';
const cad=x=>new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD'}).format(x);
let lastRt=null;
function today(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
if(!$('dt').value)$('dt').value=today();
function winter(ds){const d=new Date(ds+'T12:00:00');if(isNaN(d))return null;const m=d.getMonth()+1;return m>=10||m<=4}
function calc(){
  const k=$('rt').value,r=R[k];
  if(k!==lastRt){if(lastRt!==null)$('km').value=r.km;lastRt=k;cams()}
  const km=Math.max(0,num('km'))*+$('rtp').value,lk=Math.max(0,num('lk')),gp=Math.max(0,num('gp')),L=km*lk/100;
  const top=r.c.reduce((a,c)=>c[2]>a[2]?c:a,r.c[0]),w=winter($('dt').value);
  let h='<div class="big"><span>Fuel for this drive</span><b>'+cad(L*gp)+'</b><em>'+km.toFixed(0)+' km · '+L.toFixed(1)+' litres · highest camera point '+top[1]+' at '+top[2].toLocaleString('en-CA')+' m</em></div>';
  h+='<p><b>Winter tires or chains:</b> '+(w===null?'—':w?'required on signed routes on your travel date (October 1 – April 30; some lower routes end March 31).':'not required on your travel date (the rule runs October 1 – April 30).')+'<br><b>Legal winter tire:</b> mountain/snowflake or M+S symbol and at least 3.5 mm of tread.</p>';
  const items=r.c.map(c=>[c[1],c[2]]);
  h+='<h3 class="lc-h">Elevation along the route (camera sites, metres)</h3>'+sw(tbl(['Camera site','Elevation'],r.c.map(c=>[c[1],c[2].toLocaleString('en-CA')+' m'])),bars(items,v=>v.toLocaleString('en-CA')+' m'),['Table','Chart']);
  h+='<p class="lc-src">Higher sites are where snow and ice are most likely. Distances are approximate route lengths – type in your own.</p>';
  $('out').innerHTML=h}
function cams(){const r=R[$('rt').value],t=Math.floor(Date.now()/300000);
  $('camgrid').innerHTML='<span class="lc-live"><i></i>Live · images update every few minutes</span><div class="lc-grid">'+r.c.map(c=>'<figure class="lc-cam"><img loading="lazy" src="https://www.drivebc.ca/images/'+c[0]+'.jpg?t='+t+'" alt="Live highway camera: '+c[1]+'" width="800" height="468"><span class="lc-t">'+c[2].toLocaleString('en-CA')+' m</span><figcaption><b>'+c[1]+'</b>DriveBC camera '+c[0]+'</figcaption></figure>').join('')+'</div><p class="lc-src">Camera images: DriveBC, Province of British Columbia. Always check <a href="https://www.drivebc.ca/" rel="noopener" target="_blank">DriveBC</a> for closures and advisories before you go.</p>'}
$('form').addEventListener('input',calc);$('form').addEventListener('change',calc);calc();
setInterval(()=>{if(!document.hidden)cams()},300000);
'''

FAQ = [
 ("When do I need winter tires in BC?",
  "Drivers must obey winter tire and chain signs throughout the province from October 1 to April 30. For some highways that are not through mountain passes or high-snowfall areas, the requirement ends March 31. Signs at the start of each section tell you whether it applies."),
 ("What counts as a winter tire in BC?",
  "A tire with the three-peaked mountain/snowflake symbol or the M+S (mud and snow) symbol, with at least 3.5 mm of tread. You need at least two matching winter tires on the main drive axle, even on a 4×4. Mountain/snowflake tires (including all-weather tires) grip better on snow and ice."),
 ("How much fuel does the Coquihalla take?",
  "With the default numbers – about 200 km from Hope to Kamloops each way, 400 km return at 9 L/100 km – the trip uses 36 litres, which is $63.00 at $1.75 a litre. Long climbs to the 1,230 m summit push consumption up, so a heavily loaded car or SUV can use more."),
 ("Where do the camera pictures come from?",
  "From DriveBC, the Province of British Columbia’s road information service, which runs more than 1,000 highway cameras. This page shows the cameras along the route you choose, using the camera list published by DriveBC."),
 ("Is the Coquihalla a toll road?",
  "No. Tolls on the Coquihalla Highway were removed in 2008, and none of the routes on this page charge a toll."),
]

ART = '''<p><b>Short answer:</b> winter tires or chains are required on signed BC highways from October 1 to April 30, and a legal winter tire needs the mountain/snowflake or M+S symbol and 3.5 mm of tread. This planner adds your fuel cost, checks your travel date against those rules, charts how high the road climbs and shows live DriveBC cameras along the pass.</p>
<h2 id="how">How it works</h2>
<ul><li><b>Fuel</b> = distance × trips × L/100 km ÷ 100 × price per litre</li>
<li><b>Winter tire check</b> = is your travel date between October 1 and April 30?</li>
<li><b>Elevation chart</b> = the height of each DriveBC camera site on the route, so you can see where the summit is.</li></ul>
<h3 id="routes">Routes covered</h3>
''' + table(['Route', 'Approx. distance', 'Highest camera site'], [
    [v[0], f'{v[1]} km', max(v[2], key=lambda c: c[2])[1] + f' ({max(v[2], key=lambda c: c[2])[2]:,} m)'] for v in ROUTES.values()]) + '''
<p class="note">Distances are approximate and only used as a starting value; elevations come from DriveBC’s camera list.</p>
<h3 id="examples">Worked examples (return trip, 9 L/100 km, $1.75/L)</h3>
''' + table(['Route', 'Return distance', 'Fuel', 'Cost'], [
    ['Coquihalla, Hope–Kamloops', '400 km', '36.0 L', '$63.00'],
    ['Rogers Pass, Revelstoke–Golden', '296 km', '26.6 L', '$46.62'],
    ['Sea-to-Sky, Vancouver–Whistler', '240 km', '21.6 L', '$37.80']]) + '''
<h3 id="tips">Winter mountain driving tips</h3>
<ul><li>Check the cameras at the summit, not just at the start – the weather can be completely different 1,000 m higher.</li>
<li>Carry chains for extreme conditions, plus warm clothes, water and a charged phone.</li>
<li>Fill up before the pass: stations are far apart on routes like the Coquihalla and Kootenay Pass.</li></ul>
<h2 id="faq" style="margin-top:22px">FAQ</h2>''' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in FAQ) + '''
<p class="note">Sources (checked November 24, 2026): <a href="https://www2.gov.bc.ca/gov/content/transportation/driving-and-cycling/traveller-information/seasonal/winter-driving" rel="nofollow">Province of BC – Winter driving</a>; <a href="https://www2.gov.bc.ca/gov/content/transportation/driving-and-cycling/traveller-information/seasonal/winter-driving/about-winter-tires" rel="nofollow">Province of BC – Passenger vehicle tire and chain requirements</a>; <a href="https://www.drivebc.ca/" rel="nofollow">DriveBC highway cameras</a>. Related: <a href="/ca/cra-mileage-rate-calculator.html">CRA mileage rate calculator</a>.</p>'''

make('ca', 'bc-mountain-pass-trip-cameras.html', 'cra-mileage-rate-calculator.html',
     'BC Mountain Pass Trip Planner – Coquihalla, Rogers Pass & Sea-to-Sky Live Cameras, Fuel & Winter Tires',
     'Plan a drive over the Coquihalla, Rogers Pass, Sea-to-Sky or Kootenay Pass: fuel cost, winter tire date check, summit elevation and live DriveBC highway cameras.',
     'BC Mountain Pass Trip Planner & Live Cameras', '🇨🇦 British Columbia · live DriveBC cameras',
     'Fuel cost, winter-tire rules for your travel date, how high the road climbs – and live highway cameras along the pass.',
     FORM, JS, ART, FAQ, [('form', 'Calculator'), ('cameras', 'Live cameras'), ('how', 'How it works'), ('routes', 'Routes'), ('examples', 'Examples'), ('faq', 'FAQ')],
     'November 24, 2026', 'DriveBC · Province of BC', 'en-CA', 'CAD', 'All calculators', 'cra-mileage-rate-calculator.html', 'BC Mountain Pass Trip Planner & Live Cameras')
