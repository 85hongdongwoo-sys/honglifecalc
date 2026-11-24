"""UK: London driving commute cost (fuel + Congestion Charge + ULEZ + parking) with live TfL JamCam traffic cameras.
Data: TfL Unified API /Place/Type/JamCam (TfL open data, 'Powered by TfL Open Data'). Charges checked on tfl.gov.uk 24 Nov 2026."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from livecam_kit import make, table

FORM = '''<form class="card" id="form" onsubmit="return false"><h2>Your London drive</h2>
<div class="lc-row"><label class="f"><span>One-way distance (miles)</span><input id="mi" inputmode="decimal" value="12"></label>
<label class="f"><span>Fuel economy (mpg)</span><input id="mpg" inputmode="decimal" value="45"><small>UK miles per gallon (4.546 litres).</small></label></div>
<div class="lc-row"><label class="f"><span>Fuel price (£ per litre)</span><input id="fp" inputmode="decimal" value="1.74"><small>Change it to the price at your usual pump.</small></label>
<label class="f"><span>Driving days per week</span><input id="dpw" inputmode="decimal" value="5"></label></div>
<label class="f"><span><input type="checkbox" id="cc" checked> I drive inside the Congestion Charge zone during charging hours</span><small>Mon–Fri 07:00–18:00, Sat–Sun and bank holidays 12:00–18:00.</small></label>
<div class="lc-row"><label class="f"><span>Congestion Charge per day (£)</span><input id="ccv" inputmode="decimal" value="18"><small>£18 paid on the day or in advance; £21 if paid later.</small></label>
<label class="f"><span>Does your car meet ULEZ standards?</span><select id="ulez"><option value="0" selected>Yes – no ULEZ charge</option><option value="12.5">No – pay £12.50 a day</option></select></label></div>
<div class="lc-row"><label class="f"><span>Parking per day (£)</span><input id="park" inputmode="decimal" value="0"></label>
<label class="f"><span>Weeks you drive per year</span><input id="wks" inputmode="decimal" value="46"><small>52 weeks minus holidays and days off.</small></label></div>
</form><section class="card" id="out" aria-live="polite"><p>Working out your cost…</p></section>
<section class="card" id="cams"><h2 id="cameras">Live London traffic cameras</h2>
<p style="margin:0 0 6px">Look at the roads on your route before you set off. Images refresh about every few minutes.</p>
<div class="lc-row"><label class="f"><span>Find a road or place</span><input id="q" placeholder="e.g. A40, Blackfriars, Elephant" autocomplete="off"></label>
<label class="f"><span>&nbsp;</span><button type="button" id="near" class="lc-btn">Cameras near me</button></label></div>
<div id="camgrid"><p>Loading cameras…</p></div></section>'''

JS = r'''
const nf=(x,d)=>new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP',minimumFractionDigits:d==null?2:d,maximumFractionDigits:d==null?2:d}).format(x);
const LPG=4.54609;
function calc(){
  const mi=Math.max(0,num('mi')),mpg=Math.max(1,num('mpg')),fp=Math.max(0,num('fp')),dpw=Math.min(7,Math.max(0,num('dpw'))),wks=Math.min(52,Math.max(0,num('wks')));
  const fuelDay=(mi*2/mpg)*LPG*fp;
  const ccDay=$('cc').checked?Math.max(0,num('ccv')):0,ulDay=+$('ulez').value,pkDay=Math.max(0,num('park'));
  const day=fuelDay+ccDay+ulDay+pkDay,days=dpw*wks;
  let h='<div class="big"><span>Your driving cost per day</span><b>'+nf(day)+'</b><em>'+nf(day*dpw)+' a week · '+nf(day*days/12,0)+' a month · '+nf(day*days,0)+' a year</em></div>';
  const items=[['Fuel',fuelDay*days],['Congestion Charge',ccDay*days],['ULEZ',ulDay*days],['Parking',pkDay*days]];
  const rows=items.map(x=>[x[0],nf(x[1]/days||0),nf(x[1],0)]);rows.push(['<b>Total</b>','<b>'+nf(day)+'</b>','<b>'+nf(day*days,0)+'</b>']);
  h+='<h3 class="lc-h">Where the money goes (per year)</h3>'+sw(tbl(['Cost','Per day','Per year'],rows),bars(items.filter(x=>x[1]>0),v=>nf(v,0)),['Table','Chart']);
  h+='<p class="lc-src">Fuel: '+nf(fuelDay)+' a day for '+(mi*2).toFixed(1)+' miles return ('+((mi*2/mpg)*LPG).toFixed(1)+' litres). A year = '+days.toFixed(0)+' driving days.</p>';
  $('out').innerHTML=h}
$('form').addEventListener('input',calc);$('form').addEventListener('change',calc);calc();
// ---- live JamCams ----
let CAMS=[],SHOW=[],pos=null;
const prop=(c,k)=>{const p=(c.additionalProperties||[]).find(x=>x.key===k);return p?p.value:''};
const dkm=(a,b,c,d)=>{const r=Math.PI/180,x=(d-b)*r*Math.cos((a+c)/2*r),y=(c-a)*r;return Math.sqrt(x*x+y*y)*6371};
function draw(){const g=$('camgrid');if(!SHOW.length){g.innerHTML='<p>No camera matches that search.</p>';return}
  const t=Date.now();g.innerHTML='<span class="lc-live"><i></i>Live · '+SHOW.length+' of '+CAMS.length+' cameras</span><div class="lc-grid">'+SHOW.map(c=>{
   const img=prop(c,'imageUrl'),vid=prop(c,'videoUrl'),dist=pos?' · '+(dkm(pos[0],pos[1],c.lat,c.lon)*0.621371).toFixed(1)+' mi away':'';
   return '<figure class="lc-cam"><img loading="lazy" src="'+img+'?t='+Math.floor(t/120000)+'" alt="Live traffic camera: '+c.commonName.replace(/"/g,'')+'" data-vid="'+vid+'" width="352" height="288"><span class="lc-t">Tap to play clip</span><figcaption><b>'+c.commonName+'</b>Looking '+(prop(c,'view')||'—')+dist+'</figcaption></figure>'}).join('')+'</div><p class="lc-src">Powered by TfL Open Data. Contains OS data © Crown copyright and database rights 2016 and Geomni UK Map data © and database rights 2019. Camera images are for information only.</p>'}
function pick(){const q=$('q').value.trim().toLowerCase();let L=CAMS;
  if(q)L=L.filter(c=>c.commonName.toLowerCase().includes(q));
  const ref=pos||[51.5155,-0.0922];L=L.slice().sort((a,b)=>dkm(ref[0],ref[1],a.lat,a.lon)-dkm(ref[0],ref[1],b.lat,b.lon));
  SHOW=L.slice(0,q?12:8);draw()}
$('camgrid').addEventListener('click',e=>{const im=e.target.closest('.lc-cam img');if(!im||!im.dataset.vid)return;
  const v=document.createElement('video');v.src=im.dataset.vid;v.muted=true;v.autoplay=true;v.loop=true;v.playsInline=true;v.controls=true;v.setAttribute('aria-label',im.alt);im.replaceWith(v);const t=v.parentNode.querySelector('.lc-t');if(t)t.remove()});
$('q').addEventListener('input',pick);
$('near').addEventListener('click',()=>{if(!navigator.geolocation){$('near').textContent='Location not available';return}
  navigator.geolocation.getCurrentPosition(p=>{pos=[p.coords.latitude,p.coords.longitude];pick()},()=>{$('near').textContent='Location blocked – search instead'})});
fetch('https://api.tfl.gov.uk/Place/Type/JamCam').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}).then(j=>{
  CAMS=j.filter(c=>prop(c,'available')==='true'&&prop(c,'imageUrl'));pick();
  setInterval(()=>{if(!document.hidden)draw()},120000)}).catch(e=>{$('camgrid').innerHTML='<p class="lc-err">The camera list could not be loaded right now ('+e.message+'). Please try again in a minute.</p>'});
'''

FAQ = [
 ("How much does it cost to drive into central London in 2026?",
  "The Congestion Charge is £18 a day if you pay on the day or in advance, or £21 if you pay by midnight on the third day after you travel. If your car does not meet the ULEZ emissions standards you also pay £12.50 a day. On top of that come fuel and parking. A 24-mile round trip in a 45 mpg car at £1.74 a litre uses about £4.22 of fuel, so a day in the zone costs about £22.22 for a ULEZ-compliant car before parking."),
 ("When do I have to pay the Congestion Charge?",
  "When you drive inside the zone between 07:00 and 18:00 Monday to Friday, or between 12:00 and 18:00 on Saturdays, Sundays and bank holidays. There is no charge between Christmas Day and the New Year’s Day bank holiday (inclusive)."),
 ("Is the ULEZ charge the same as the Congestion Charge?",
  "No. The ULEZ (Ultra Low Emission Zone) covers all London boroughs, runs 24 hours a day every day except Christmas Day, and only applies to vehicles that do not meet its emissions standards. The Congestion Charge covers the central zone during charging hours and applies to most vehicles. A non-compliant car driving in central London during charging hours pays both: £18 + £12.50 = £30.50 a day."),
 ("Where do the traffic camera pictures come from?",
  "From Transport for London’s JamCams – around 900 cameras on London roads. The page loads the camera list from the TfL open data API and shows the latest still image from each camera. Tap an image to play the short video clip TfL publishes for that camera."),
 ("How do I work out fuel cost from mpg?",
  "Divide the miles by the mpg to get gallons, multiply by 4.546 to get litres, then multiply by the price per litre. Example: 24 miles ÷ 45 mpg = 0.533 gallons × 4.546 = 2.42 litres × £1.74 = £4.22."),
]

ART = '''<p><b>Short answer:</b> in 2026 driving into central London costs £18 a day for the Congestion Charge (paid on the day or in advance), plus £12.50 a day if your car is not ULEZ-compliant, plus fuel and parking. This page adds them up for a day, a week, a month and a year, and shows live TfL traffic cameras so you can check the roads before you leave.</p>
<h2 id="how">How the cost is calculated</h2>
<ul><li><b>Fuel per day</b> = return miles ÷ mpg × 4.546 litres × price per litre</li>
<li><b>Daily charges</b> = Congestion Charge (if you drive in the zone in charging hours) + ULEZ charge (only for non-compliant cars) + parking</li>
<li><b>Per year</b> = cost per day × driving days per week × weeks you drive per year</li></ul>
<h3 id="charges">London road charges (checked 24 November 2026)</h3>
''' + table(['Charge', 'Amount', 'When it applies'], [
    ['Congestion Charge', '£18 a day (paid on the day or in advance) · £21 if paid by midnight of the third day after travel', '07:00–18:00 Mon–Fri, 12:00–18:00 Sat–Sun and bank holidays; none from Christmas Day to the New Year’s Day bank holiday'],
    ['ULEZ', '£12.50 a day', 'Only for vehicles that do not meet the ULEZ standards; 24 hours a day, every day except 25 December, across all London boroughs']]) + '''
<h3 id="examples">Worked examples (45 mpg, £1.74 a litre, 5 days a week, 46 weeks)</h3>
''' + table(['Trip', 'Per day', 'Per year'], [
    ['12 miles each way, in the zone, ULEZ-compliant, no parking', '£22.22', '£5,110'],
    ['12 miles each way, in the zone, not ULEZ-compliant', '£34.72', '£7,985'],
    ['12 miles each way, outside the zone, ULEZ-compliant', '£4.22', '£970'],
    ['5 miles each way, in the zone, £20 parking', '£39.76', '£9,144']]) + '''
<p class="note">Figures are rounded. The calculator above uses the exact numbers you enter.</p>
<h3 id="tips">Tips</h3>
<ul><li><b>Set up Auto Pay</b> with TfL so you never pay the £21 late price or get a penalty.</li>
<li><b>Check your car</b> with TfL’s vehicle checker before assuming it is ULEZ-compliant – most petrol cars from 2006 and diesel cars from late 2015 meet the standards, but always check.</li>
<li><b>Look at the cameras</b> before leaving: a jam on your usual road may make public transport the cheaper and faster choice that day.</li></ul>
<h2 id="faq" style="margin-top:22px">FAQ</h2>''' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in FAQ) + '''
<p class="note">Sources (checked 24 November 2026): <a href="https://tfl.gov.uk/modes/driving/congestion-charge" rel="nofollow">TfL – Congestion Charge</a>; <a href="https://tfl.gov.uk/modes/driving/ultra-low-emission-zone" rel="nofollow">TfL – Ultra Low Emission Zone</a>; <a href="https://api.tfl.gov.uk/" rel="nofollow">TfL Unified API (JamCams)</a> – Powered by TfL Open Data. Related: <a href="/uk/fuel-cost-calculator.html">Fuel cost calculator</a>.</p>'''

make('uk', 'london-driving-cost-traffic-cameras.html', 'fuel-cost-calculator.html',
     'London Driving Cost Calculator 2026 – Congestion Charge, ULEZ & Live Traffic Cameras',
     'Work out the daily, monthly and yearly cost of driving in London: fuel, £18 Congestion Charge, £12.50 ULEZ and parking – with live TfL JamCam traffic cameras.',
     'London Driving Cost & Live Traffic Cameras', '🇬🇧 2026 charges · live TfL cameras',
     'Add up fuel, the Congestion Charge, ULEZ and parking for your trip – then check the roads on live TfL traffic cameras.',
     FORM, JS, ART, FAQ, [('form', 'Calculator'), ('cameras', 'Live cameras'), ('how', 'How it works'), ('charges', '2026 charges'), ('examples', 'Examples'), ('faq', 'FAQ')],
     '24 November 2026', 'TfL open data', 'en-GB', 'GBP', 'All calculators', 'fuel-cost-calculator.html', 'London Driving Cost & Live Traffic Cameras')
