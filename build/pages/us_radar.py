"""US: bad-weather drive time & gas cost calculator with live NWS radar loops (public domain).
Speed-reduction ranges: FHWA Road Weather Management 'How Do Weather Events Affect Roads?' (checked 24 Nov 2026)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from livecam_kit import make, table

STATIONS = [('CONUS', 'Whole United States (lower 48)'), ('KOKX', 'New York City'), ('KBOX', 'Boston'), ('KDIX', 'Philadelphia'), ('KLWX', 'Washington, DC'),
            ('KRAX', 'Raleigh'), ('KFFC', 'Atlanta'), ('KAMX', 'Miami'), ('KTBW', 'Tampa'), ('KOHX', 'Nashville'),
            ('KLOT', 'Chicago'), ('KDTX', 'Detroit'), ('KCLE', 'Cleveland'), ('KIND', 'Indianapolis'), ('KMPX', 'Minneapolis'), ('KLSX', 'St. Louis'),
            ('KEAX', 'Kansas City'), ('KFWS', 'Dallas–Fort Worth'), ('KHGX', 'Houston'), ('KEWX', 'Austin / San Antonio'), ('KFTG', 'Denver'),
            ('KMTX', 'Salt Lake City'), ('KIWA', 'Phoenix'), ('KESX', 'Las Vegas'), ('KSOX', 'Los Angeles / Orange County'), ('KNKX', 'San Diego'),
            ('KMUX', 'San Francisco Bay Area'), ('KRTX', 'Portland'), ('KATX', 'Seattle')]
OPTS = ''.join(f'<option value="{k}">{n}{"" if k == "CONUS" else " (" + k + ")"}</option>' for k, n in STATIONS)

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Your drive</h2>
<div class="lc-row"><label class="f"><span>Trip distance (miles)</span><input id="mi" inputmode="decimal" value="250"></label>
<label class="f"><span>Normal average speed (mph)</span><input id="sp" inputmode="decimal" value="60"><small>Your usual average including towns, not the speed limit.</small></label></div>
<label class="f"><span>Expected road conditions</span><select id="wx"><option value="0">Dry</option><option value="15" selected>Rain / wet pavement (speeds 10–25% lower)</option><option value="35">Snow or slush (speeds 30–40% lower)</option><option value="c">Custom slowdown</option></select></label>
<label class="f" id="cwrap" hidden><span>Custom slowdown (%)</span><input id="cs" inputmode="decimal" value="20"></label>
<div class="lc-row"><label class="f"><span>Fuel economy (mpg)</span><input id="mpg" inputmode="decimal" value="30"></label>
<label class="f"><span>Gas price ($ per gallon)</span><input id="gp" inputmode="decimal" value="3.10"><small>Example – type in your local price.</small></label></div>
</form><section class="card" id="out" aria-live="polite"></section>
<section class="card" id="cams"><h2 id="radar">Live weather radar</h2>
<label class="f"><span>Radar for</span><select id="st">{OPTS}</select></label>
<div id="radbox"></div></section>'''

JS = r'''
const usd=(x,d)=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',minimumFractionDigits:d==null?2:d,maximumFractionDigits:d==null?2:d}).format(x);
const hm=h=>{const m=Math.round(h*60);return Math.floor(m/60)+' h '+String(m%60).padStart(2,'0')+' min'};
function calc(){
  $('cwrap').hidden=$('wx').value!=='c';
  const mi=Math.max(0,num('mi')),sp=Math.max(1,num('sp')),mpg=Math.max(1,num('mpg')),gp=Math.max(0,num('gp'));
  const red=Math.min(80,Math.max(0,$('wx').value==='c'?num('cs'):+$('wx').value));
  const t0=mi/sp,t1=mi/(sp*(1-red/100)),gal=mi/mpg,cost=gal*gp;
  let h='<div class="big"><span>Drive time in these conditions</span><b>'+hm(t1)+'</b><em>'+(t1>t0?'about '+Math.round((t1-t0)*60)+' min longer than in dry weather ('+hm(t0)+')':'same as a dry day')+' · gas about '+usd(cost)+'</em></div>';
  const items=[['Dry',t0*60],['Rain (−15%)',mi/(sp*.85)*60],['Snow (−35%)',mi/(sp*.65)*60]];
  if($('wx').value==='c')items.push(['Custom (−'+red+'%)',t1*60]);
  h+='<h3 class="lc-h">Drive time by road condition</h3>'+sw(tbl(['Condition','Average speed','Drive time'],items.map(x=>[x[0],(mi/(x[1]/60)).toFixed(0)+' mph',hm(x[1]/60)])),bars(items,v=>hm(v/60).replace(' min','m').replace(' h ','h ')),['Table','Chart']);
  h+='<p class="lc-src">Gas: '+mi+' miles ÷ '+mpg+' mpg = '+gal.toFixed(1)+' gallons × '+usd(gp)+'. Bad weather can also raise fuel use; this estimate does not add that.</p>';
  $('out').innerHTML=h}
function radar(){const st=$('st').value,t=Math.floor(Date.now()/300000);
  $('radbox').innerHTML='<span class="lc-live"><i></i>Live loop · refreshed every 5 minutes</span><figure class="lc-cam" style="max-width:620px"><img src="https://radar.weather.gov/ridge/standard/'+st+'_loop.gif?t='+t+'" alt="Live NWS radar loop: '+$('st').selectedOptions[0].text+'" style="aspect-ratio:auto;object-fit:contain"><figcaption><b>'+$('st').selectedOptions[0].text+'</b>Base reflectivity loop – greens are light rain, yellows and reds are heavy rain or storms.</figcaption></figure><p class="lc-src">Radar: National Weather Service (NOAA), public domain. Check <a href="https://www.weather.gov/" rel="noopener" target="_blank">weather.gov</a> for warnings before you leave.</p>'}
$('form').addEventListener('input',calc);$('form').addEventListener('change',calc);calc();
$('st').addEventListener('change',radar);radar();setInterval(()=>{if(!document.hidden)radar()},300000);
'''

FAQ = [
 ("How much longer does a drive take in the rain?",
  "Federal Highway Administration research summarised on its Road Weather Management site finds speeds on wet pavement are 10–25% lower on signalised arterial roads and 30–40% lower on snowy or slushy pavement. On freeways, average travel-time delay in adverse weather was measured at 14% in Washington, DC and 21% in Seattle. A 250-mile trip at a 60 mph average takes 4 h 10 min dry and about 4 h 54 min with a 15% slowdown."),
 ("Does bad weather change my gas cost?",
  "The calculator keeps the same mpg, so the gas cost is the same in every condition. In practice cold, wet and slow conditions often lower your mpg a little, so treat the gas figure as a minimum."),
 ("Where does the radar come from?",
  "The loops are the National Weather Service’s RIDGE radar images from its WSR-88D (NEXRAD) stations. US government weather data is in the public domain. The ‘Whole United States’ option shows the national mosaic."),
 ("How do I read the radar colors?",
  "The radar shows reflectivity: light greens are light rain, yellows and oranges are moderate to heavy rain, and reds or purples are very heavy rain, hail or strong storms. In winter, snow often shows as lighter blues and greens even when roads are bad."),
 ("What average speed should I enter?",
  "Use the average you really achieve door to door, not the speed limit. Mixed interstate driving with a few stops is often 55–65 mph; city and mountain routes are lower."),
]

ART = '''<p><b>Short answer:</b> FHWA research finds speeds 10–25% lower on wet pavement and 30–40% lower on snowy or slushy pavement (measured on signalised arterial roads; freeway delays of 14–21% were measured in rain). A 250-mile drive at 60 mph takes 4 h 10 min when dry, about 4 h 54 min in rain and about 6 h 25 min in snow. Check the live radar below before you leave.</p>
<h2 id="how">How it works</h2>
<ul><li><b>Dry drive time</b> = distance ÷ your normal average speed</li>
<li><b>Bad-weather drive time</b> = distance ÷ (normal speed × (1 − slowdown %))</li>
<li><b>Gas cost</b> = distance ÷ mpg × price per gallon</li></ul>
<h3 id="ranges">Speed reductions used (FHWA, checked 24 November 2026)</h3>
''' + table(['Road condition', 'Speed reduction (research range)', 'Default in calculator'], [
    ['Wet pavement', '10–25%', '15%'], ['Snowy or slushy pavement', '30–40%', '35%']]) + '''
<h3 id="examples">Worked examples (60 mph normal average)</h3>
''' + table(['Distance', 'Dry', 'Rain (−15%)', 'Snow (−35%)'], [
    ['100 miles', '1 h 40 min', '1 h 58 min', '2 h 34 min'],
    ['250 miles', '4 h 10 min', '4 h 54 min', '6 h 25 min'],
    ['500 miles', '8 h 20 min', '9 h 48 min', '12 h 49 min']]) + '''
<h3 id="tips">Tips</h3>
<ul><li>Leave earlier rather than driving faster to “make up” time.</li>
<li>Check the radar loop: if a band of storms is moving across your route, waiting an hour can be quicker than driving through it.</li>
<li>Fill up before long snowy stretches – stations can be far apart and you may sit in traffic.</li></ul>
<h2 id="faq" style="margin-top:22px">FAQ</h2>''' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in FAQ) + '''
<p class="note">Sources (checked 24 November 2026): <a href="https://ops.fhwa.dot.gov/weather/roadimpact.htm" rel="nofollow">FHWA – How Do Weather Events Affect Roads?</a>; <a href="https://radar.weather.gov/" rel="nofollow">National Weather Service radar</a>. Related: <a href="/us/fuel-cost-calculator.html">Fuel cost calculator</a>.</p>'''

make('us', 'bad-weather-drive-time-radar.html', 'fuel-cost-calculator.html',
     'Rain & Snow Drive Time Calculator – How Much Longer + Live Weather Radar',
     'How much longer will your drive take in rain or snow? Uses FHWA slowdown ranges, adds gas cost, and shows live NWS radar loops for 28 US metro areas.',
     'Bad-Weather Drive Time & Live Radar', '🇺🇸 Live NWS radar · FHWA research',
     'See how much longer your trip takes in rain or snow, what the gas costs, and what the radar looks like right now.',
     FORM, JS, ART, FAQ, [('form', 'Calculator'), ('radar', 'Live radar'), ('how', 'How it works'), ('ranges', 'Slowdown ranges'), ('examples', 'Examples'), ('faq', 'FAQ')],
     'November 24, 2026', 'NWS · FHWA', 'en-US', 'USD', 'All calculators', 'fuel-cost-calculator.html', 'Bad-Weather Drive Time & Live Radar')
