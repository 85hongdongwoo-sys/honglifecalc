"""Singapore: drive-to-JB trip cost (tolls, Malaysia road charge, petrol saving) + live Causeway / Second Link cameras.
Data: data.gov.sg traffic-images (LTA, Singapore Open Data Licence); data.gov.my fuelprice (CC BY 4.0); ECB reference rates (/fx/latest.json).
Tolls checked on OneMotoring 24 Nov 2026; RM20 road charge per entry (JPJ VEP rules, reported by FMT 30 Jun 2025)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from livecam_kit import make, table

FORM = '''<form class="card" id="form" onsubmit="return false"><h2>Your trip to Johor Bahru</h2>
<label class="f"><span>Crossing</span><select id="rt"><option value="w" selected>Woodlands Causeway</option><option value="t">Tuas Second Link</option></select></label>
<div class="lc-row"><label class="f"><span>Total driving distance, return (km)</span><input id="km" inputmode="decimal" value="60"><small>Home → checkpoint → JB and back.</small></label>
<label class="f"><span>Fuel consumption (L/100 km)</span><input id="lk" inputmode="decimal" value="7"></label></div>
<div class="lc-row"><label class="f"><span>Singapore pump price (S$/litre)</span><input id="sgp" inputmode="decimal" value="2.80"><small>Example only – type in the price you paid last.</small></label>
<label class="f"><span>Petrol you buy in JB (litres)</span><input id="buy" inputmode="decimal" value="30"><small>You must leave Singapore with at least ¾ of a tank.</small></label></div>
<div class="lc-row"><label class="f"><span>JB petrol grade</span><select id="gr"><option value="ron97" selected>RON97</option><option value="ron95">RON95 (unsubsidised price)</option></select></label>
<label class="f"><span>Malaysian tolls, return (RM)</span><input id="myt" inputmode="decimal" value="0"><small>Bridge / expressway tolls from your Touch ’n Go history.</small></label></div>
<label class="f"><span>Other spending in JB you want to compare (S$, optional)</span><input id="oth" inputmode="decimal" value="0"></label>
</form><section class="card" id="out" aria-live="polite"><p>Loading today’s Malaysian fuel price and exchange rate…</p></section>
<section class="card" id="cams"><h2 id="cameras">Live checkpoint cameras</h2>
<p style="margin:0 0 6px">LTA cameras at the Woodlands Causeway and the Tuas Second Link. New pictures arrive every few minutes – check the queue before you go.</p>
<div id="camgrid"><p>Loading cameras…</p></div></section>'''

JS = r'''
const S=(x,d)=>'S$'+new Intl.NumberFormat('en-SG',{minimumFractionDigits:d==null?2:d,maximumFractionDigits:d==null?2:d}).format(x);
const RM=x=>'RM'+new Intl.NumberFormat('en-SG',{minimumFractionDigits:2,maximumFractionDigits:2}).format(x);
const TOLL={w:{out:0.80,in:0},t:{out:2.10,in:2.10}},RC=20;
let FUEL=null,FX=null;
function calc(){
  const rt=$('rt').value,km=Math.max(0,num('km')),lk=Math.max(0,num('lk')),sgp=Math.max(0,num('sgp')),buy=Math.max(0,num('buy')),myt=Math.max(0,num('myt'));
  let h='';
  if(!FUEL||!FX){$('out').innerHTML='<p class="lc-err">Today’s Malaysian fuel price or exchange rate could not be loaded. Please try again shortly.</p>';return}
  const myPrice=FUEL[$('gr').value],rate=FX.MYR/FX.SGD; // RM per S$1
  const tollSG=TOLL[rt].out+TOLL[rt].in,rcS=RC/rate,mytS=myt/rate,driveS=km*lk/100*sgp;
  const jbFuelS=buy*myPrice/rate,sgFuelS=buy*sgp,save=sgFuelS-jbFuelS;
  const cost=tollSG+rcS+mytS+driveS,net=save-cost;
  h+='<span class="lc-live"><i></i>Malaysia fuel price week of '+FUEL.date+' · S$1 = '+rate.toFixed(4)+' RM ('+FX.date+')</span>';
  h+='<div class="big"><span>'+(net>=0?'You come out ahead on petrol by':'The trip costs more than it saves on petrol by')+'</span><b>'+S(Math.abs(net))+'</b><em>Petrol saving '+S(save)+' − trip costs '+S(cost)+'</em></div>';
  const rows=[['Singapore tolls (exit + re-entry)',S(tollSG),''],['Malaysia road charge (per entry)',S(rcS),RM(RC)],['Malaysian tolls',S(mytS),RM(myt)],['Petrol used for the drive ('+(km*lk/100).toFixed(1)+' L at Singapore price)',S(driveS),''],
   ['<b>Trip costs</b>','<b>'+S(cost)+'</b>',''],[buy+' L in JB ('+RM(myPrice)+'/L)',S(jbFuelS),RM(buy*myPrice)],['Same petrol in Singapore',S(sgFuelS),''],['<b>Petrol saving</b>','<b>'+S(save)+'</b>','']];
  const items=[['Trip costs',cost],['Petrol in JB',jbFuelS],['Same petrol in SG',sgFuelS]];
  h+='<h3 class="lc-h">Breakdown</h3>'+sw(tbl(['Item','S$','RM'],rows),bars(items,v=>S(v,0)),['Table','Chart']);
  const oth=Math.max(0,num('oth'));if(oth>0)h+='<p>Including your other JB spending of '+S(oth)+', the whole day out costs about '+S(cost+jbFuelS+oth)+'.</p>';
  if(net<0&&save>0)h+='<p>You would need to buy about <b>'+Math.ceil(cost/((sgp-myPrice/rate)||1))+' litres</b> in JB for the petrol saving to cover the trip.</p>';
  h+='<p class="lc-src">Singapore tolls: OneMotoring. Malaysian fuel price: Ministry of Finance via data.gov.my (CC BY 4.0). Exchange rate: European Central Bank reference rates (cross rate). Malaysian toll amounts are not included unless you enter them.</p>';
  $('out').innerHTML=h}
Promise.all([fetch('https://api.data.gov.my/data-catalogue?id=fuelprice&sort=-date&limit=4').then(r=>r.json()),fetch('/fx/latest.json').then(r=>r.json())]).then(([f,x])=>{
  const lv=f.find(r=>r.series_type==='level');FUEL={ron95:lv.ron95,ron97:lv.ron97,date:lv.date};FX={MYR:x.rates.MYR,SGD:x.rates.SGD,date:x.date};calc()}).catch(()=>calc());
$('form').addEventListener('input',calc);$('form').addEventListener('change',calc);
// ---- live LTA cameras ----
const NAMES={'2701':'Woodlands Causeway (towards Johor)','2702':'Woodlands Checkpoint','2704':'Near Woodlands Checkpoint','4703':'Tuas Second Link','4713':'Tuas Checkpoint','4712':'Near Tuas Checkpoint'};
const ORDER=['2701','2702','2704','4703','4713','4712'];
const tf=new Intl.DateTimeFormat('en-SG',{timeZone:'Asia/Singapore',hour:'2-digit',minute:'2-digit',day:'numeric',month:'short'});
function cams(){fetch('https://api.data.gov.sg/v1/transport/traffic-images').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}).then(j=>{
  const L=(j.items[0].cameras||[]).filter(c=>NAMES[c.camera_id]).sort((a,b)=>ORDER.indexOf(a.camera_id)-ORDER.indexOf(b.camera_id));
  const rt=$('rt').value;L.sort((a,b)=>((b.camera_id[0]==='2')===(rt==='w'))-((a.camera_id[0]==='2')===(rt==='w')));
  $('camgrid').innerHTML='<span class="lc-live"><i></i>Live · refreshed every 2 minutes</span><div class="lc-grid">'+L.map(c=>'<figure class="lc-cam"><img loading="lazy" src="'+c.image+'" alt="Live traffic camera: '+NAMES[c.camera_id]+'" width="320" height="240"><span class="lc-t">'+tf.format(new Date(c.timestamp))+'</span><figcaption><b>'+NAMES[c.camera_id]+'</b>LTA camera '+c.camera_id+'</figcaption></figure>').join('')+'</div><p class="lc-src">Traffic images: Land Transport Authority via data.gov.sg, Singapore Open Data Licence.</p>'})
 .catch(e=>{$('camgrid').innerHTML='<p class="lc-err">Camera pictures could not be loaded right now ('+e.message+').</p>'})}
cams();setInterval(()=>{if(!document.hidden)cams()},120000);$('rt').addEventListener('change',cams);
'''

FAQ = [
 ("How much is the toll to drive from Singapore to JB?",
  "On the Singapore side a car pays S$0.80 when leaving through Woodlands Checkpoint and nothing when coming back in. Through Tuas Checkpoint a car pays S$2.10 to leave and S$2.10 to come back. You pay with a NETS CashCard, Motoring Card or CEPAS card at the immigration booth, even if the barrier is already up. Malaysia charges its own tolls on top."),
 ("What is the RM20 road charge?",
  "Foreign-registered cars entering Malaysia through the Johor Causeway or the Second Link must have an activated VEP (Vehicle Entry Permit) RFID tag and pay a RM20 road charge for each entry. The RFID sticker itself costs RM10 once."),
 ("Do I really need ¾ of a tank to leave Singapore?",
  "Yes. LTA requires the fuel tank of every vehicle leaving Singapore by road to be at least three-quarters full, including hybrids. So you cannot drive across on an empty tank – the petrol you can save is limited to what you top up in JB."),
 ("Which Malaysian fuel price does the calculator use?",
  "It reads the weekly prices published by Malaysia’s Ministry of Finance on data.gov.my. RON97 is the default. The RON95 option uses the unsubsidised RON95 price, not the BUDI95 subsidised price (RM1.99), which is only for eligible Malaysians."),
 ("Is driving to JB just for petrol worth it?",
  "Only if you buy enough. With the default numbers (Woodlands, 60 km return, 7 L/100 km, S$2.80 in Singapore) the drive itself burns about 4.2 litres and the tolls and road charge add a few dollars, so you need to top up a decent amount in JB for the cheaper petrol to cover the trip. The calculator shows the break-even litres."),
]

ART = '''<p><b>Short answer:</b> a car crossing at Woodlands pays S$0.80 in Singapore tolls (out only); at Tuas it pays S$2.10 each way. Malaysia adds a RM20 road charge per entry plus its own tolls. This page adds those to the petrol you burn, compares it with the cheaper petrol you can buy in JB, and shows live LTA checkpoint cameras.</p>
<h2 id="how">How it works</h2>
<ul><li><b>Trip costs</b> = Singapore tolls + RM20 road charge + Malaysian tolls (converted to S$) + petrol for the drive at the Singapore price</li>
<li><b>Petrol saving</b> = litres bought in JB × (Singapore price − JB price in S$)</li>
<li><b>Result</b> = petrol saving − trip costs</li></ul>
<p>The Malaysian price is read live from data.gov.my and converted with the latest European Central Bank reference rates (MYR and SGD cross rate).</p>
<h3 id="tolls">Singapore checkpoint tolls for cars (OneMotoring, checked 24 November 2026)</h3>
''' + table(['Checkpoint', 'Leaving Singapore', 'Re-entering Singapore'], [['Woodlands', 'S$0.80', '—'], ['Tuas', 'S$2.10', 'S$2.10']]) + '''
<h3 id="rules">Rules to remember</h3>
<ul><li><b>¾ tank rule:</b> your tank must be at least three-quarters full when you leave Singapore.</li>
<li><b>Malaysia VEP:</b> foreign cars need an activated VEP RFID tag; driving in without one can bring an immediate RM300 fine. A RM20 road charge applies to each entry.</li>
<li><b>Pay your tolls:</b> insert your stored-value card at the booth even if the barrier is lifted – not paying can lead to fines of up to S$1,000.</li></ul>
<h3 id="examples">Worked example</h3>
<p>Woodlands, 60 km return at 7 L/100 km uses 4.2 litres. At S$2.80 that is S$11.76. Add S$0.80 Singapore toll and RM20 road charge (about S$6.27 at RM3.19 per S$1) and the trip costs about S$18.83 before Malaysian tolls. Buying 30 litres of RON97 at RM4.00 costs RM120 (about S$37.60) instead of S$84.00 in Singapore – a saving of about S$46.40, so you come out about S$27.58 ahead.</p>
<p class="note">The example uses RM3.19 per S$1 and RON97 at RM4.00 (week of 19 November 2026). The live calculator uses this week’s figures.</p>
<h2 id="faq" style="margin-top:22px">FAQ</h2>''' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in FAQ) + '''
<p class="note">Sources (checked 24 November 2026): <a href="https://onemotoring.lta.gov.sg/content/onemotoring/home/driving/entering_and_exiting_singapore/vehicles-registered-in-singapore.html" rel="nofollow">OneMotoring – vehicles registered in Singapore (tolls, ¾ tank rule)</a>; <a href="https://www.freemalaysiatoday.com/category/nation/2025/06/30/full-vep-enforcement-at-johor-border-begins-tomorrow" rel="nofollow">FMT – VEP enforcement and RM20 road charge</a>; <a href="https://data.gov.sg/datasets/d_6cdb6b405b25aaaacbaf7689bcc6fae0/view" rel="nofollow">data.gov.sg – traffic images (LTA)</a>; <a href="https://data.gov.my/data-catalogue/fuelprice" rel="nofollow">data.gov.my – fuel prices</a>; ECB euro reference rates. Related: <a href="/sg/fuel-cost-calculator.html">Fuel cost calculator</a>.</p>'''

make('sg', 'jb-trip-cost-causeway-cameras.html', 'fuel-cost-calculator.html',
     'Drive to JB Cost Calculator 2026 – Tolls, RM20 Road Charge, Petrol & Live Causeway Cameras',
     'Is driving to JB worth it? Add Woodlands or Tuas tolls, the RM20 road charge and petrol, compare with this week’s Malaysian fuel price, and see live checkpoint cameras.',
     'Drive to JB: Trip Cost & Live Checkpoint Cameras', '🇸🇬 Live cameras · this week’s Malaysian fuel price',
     'Work out whether a JB trip pays off on petrol, and check the Causeway and Second Link queues on live LTA cameras before you leave.',
     FORM, JS, ART, FAQ, [('form', 'Calculator'), ('cameras', 'Live cameras'), ('how', 'How it works'), ('tolls', 'Tolls'), ('rules', 'Rules'), ('faq', 'FAQ')],
     '24 November 2026', 'LTA · data.gov.my · ECB', 'en-SG', 'SGD', 'All calculators', 'fuel-cost-calculator.html', 'Drive to JB: Trip Cost & Live Checkpoint Cameras')
