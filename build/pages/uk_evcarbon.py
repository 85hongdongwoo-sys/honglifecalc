"""UK: best time to charge an EV — live grid carbon intensity (NESO Carbon Intensity API, CC BY 4.0).
New page built from the UK electricity-cost template. Writes overlay/uk/ev-charging-carbon-calculator.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/uk/ev-charging-carbon-calculator.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Best Time to Charge an EV (UK) – Live Grid Carbon Intensity Calculator'
H1 = 'Best Time to Charge Your EV'
DESC = ('Find the cleanest time to charge your electric car in the next 48 hours. Live half-hourly carbon intensity '
        'forecast for your GB region, CO₂ per charge and the fuel mix – updated every 30 minutes.')

REGIONS = [(18, 'Great Britain (national)'), (1, 'North Scotland'), (2, 'South Scotland'), (3, 'North West England'),
           (4, 'North East England'), (5, 'Yorkshire'), (6, 'North Wales & Merseyside'), (7, 'South Wales'),
           (8, 'West Midlands'), (9, 'East Midlands'), (10, 'East England'), (11, 'South West England'),
           (12, 'South England'), (13, 'London'), (14, 'South East England'), (15, 'England'), (16, 'Scotland'), (17, 'Wales')]
opts = ''.join(f'<option value="{i}"{" selected" if i == 18 else ""}>{n}</option>' for i, n in REGIONS)

CSS = '''<style id="ev-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.ev-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.ev-row .f{min-width:0}
.ev-live{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;color:#1f7a3a;background:#EAF6EE;border:1px solid #CBE8D4;border-radius:999px;padding:2px 10px;margin:0 0 10px}
.ev-live i{width:8px;height:8px;border-radius:50%;background:#1f9d4a;animation:evp 1.6s infinite}@keyframes evp{50%{opacity:.3}}
.ev-sw{display:inline-flex;background:#ececf0;border-radius:9px;padding:2px;margin:4px 0 8px}
.ev-sw button{border:0;background:transparent;font:inherit;font-size:13px;padding:6px 14px;border-radius:7px;color:#3a3a3c;cursor:pointer;min-height:32px}
.ev-sw button[aria-pressed="true"]{background:#fff;color:#1d1d1f;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.ev-h{font-size:16px;margin:18px 0 4px;color:#12305C}
.ev-leg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:#6e6e73;margin:2px 0 6px}
.ev-leg i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.ev-plot{position:relative;height:210px;margin:14px 6px 40px 46px}
.ev-gl{position:absolute;left:0;right:0;border-top:1px solid #ececf0;height:0}.ev-gl.z{border-top-color:#c7c7cc}
.ev-gl span{position:absolute;right:100%;top:-8px;padding-right:7px;font-size:11px;color:#8e8e93;white-space:nowrap;font-variant-numeric:tabular-nums}
.ev-bars{position:absolute;inset:0;display:flex;align-items:flex-end;gap:1px}
.ev-b{flex:1 1 0;min-width:0;height:100%;display:flex;align-items:flex-end;position:relative}
.ev-b span{display:block;width:100%;border-radius:2px 2px 0 0}
.ev-b small{position:absolute;top:100%;left:0;margin-top:6px;font-size:10.5px;color:#6e6e73;white-space:nowrap;transform:translateX(-50%)}
.ev-b small:before{content:"";position:absolute;left:50%;top:-6px;height:4px;border-left:1px solid #c7c7cc}
.ev-grp{position:absolute;inset:0;display:flex;align-items:stretch}
.ev-g{flex:1 1 0;min-width:0;display:flex;flex-direction:column;position:relative}
.ev-cols{flex:1;display:flex;align-items:flex-end;justify-content:center;gap:4px;padding:0 3px}
.ev-c{flex:0 1 22px;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;min-width:6px}
.ev-c span{display:block;width:100%;border-radius:4px 4px 0 0}
.ev-x{position:absolute;top:100%;left:-4px;right:-4px;padding-top:6px;text-align:center;font-size:11.5px;line-height:1.25;color:#3a3a3c;word-break:keep-all;overflow-wrap:normal}
.ev-mix .ev-plot{margin-bottom:48px}
.ev-err{background:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.ev-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
@media(max-width:480px){.ev-row{grid-template-columns:1fr}.ev-plot{margin-left:40px}.ev-x{font-size:10px}.ev-cols{gap:2px;padding:0 2px}}
</style>'''

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Your charge</h2>
<label class="f"><span>Your region</span><select id="rg">{opts}</select><small>Pick the area your electricity is delivered to (your distribution network region).</small></label>
<div class="ev-row"><label class="f"><span>Battery size (kWh)</span><input id="cap" inputmode="decimal" value="60"></label>
<label class="f"><span>Charger power (kW)</span><input id="kw" inputmode="decimal" value="7"><small>Most home wallboxes are 7 kW; a 3-pin plug is about 2.3 kW.</small></label></div>
<div class="ev-row"><label class="f"><span>Charge from (%)</span><input id="p0" inputmode="decimal" value="20"></label>
<label class="f"><span>Charge to (%)</span><input id="p1" inputmode="decimal" value="80"></label></div>
<div class="ev-row"><label class="f"><span>Car needed in</span><select id="by"><option value="8">8 hours</option><option value="12" selected>12 hours</option><option value="24">24 hours</option><option value="36">36 hours</option><option value="47">48 hours</option></select></label>
<label class="f"><span>Charging losses (%)</span><input id="loss" inputmode="decimal" value="10"><small>Extra electricity lost as heat while charging.</small></label></div>
</form><section class="card" id="out" aria-live="polite"><p>Loading the live forecast…</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=id=>{const v=parseFloat(String($(id).value).replace(/[^\d.\-]/g,''));return isFinite(v)?v:0};
const nn=(x,d)=>new Intl.NumberFormat('en-GB',{maximumFractionDigits:d==null?1:d,minimumFractionDigits:d==null?0:Math.min(d,1)}).format(x);
const TZ='Europe/London';
const tf=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,weekday:'short',hour:'2-digit',minute:'2-digit',hour12:false});
const hof=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,hour:'2-digit',hour12:false});
const hf=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,hour:'2-digit',minute:'2-digit',hour12:false});
const df=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,weekday:'short'});
const t=s=>tf.format(new Date(s)).replace(',','');
const API='https://api.carbonintensity.org.uk';
const FUEL={wind:'Wind',nuclear:'Nuclear',gas:'Gas',imports:'Imports',biomass:'Biomass',solar:'Solar',hydro:'Hydro',coal:'Coal',other:'Other'};
const FS={wind:'Wind',nuclear:'Nucl.',gas:'Gas',imports:'Imp.',biomass:'Bio.',solar:'Solar',hydro:'Hydro',coal:'Coal',other:'Other'};
const BLUE='#3B82F6',ORANGE='#F59E0B',PALE='#BFD5FB';
let cache={},view={a:'chart',b:'chart'},busy=0;
function nice(m){if(m<=0)return 1;const p=Math.pow(10,Math.floor(Math.log10(m))),f=m/p;for(const s of [1,1.2,1.5,2,2.5,3,4,5,6,8,10])if(f<=s+1e-9)return s*p;return 10*p}
function sw(k,html1,html2){return '<div class="ev-sw" role="group"><button type="button" data-k="'+k+'" data-v="chart" aria-pressed="'+(view[k]==='chart')+'">Chart</button><button type="button" data-k="'+k+'" data-v="table" aria-pressed="'+(view[k]==='table')+'">Table</button></div><div data-p="'+k+'-chart"'+(view[k]==='chart'?'':' hidden')+'>'+html1+'</div><div data-p="'+k+'-table"'+(view[k]==='table'?'':' hidden')+'>'+html2+'</div>'}
function grid(top,unit){let g='';for(let i=4;i>=0;i--)g+='<div class="ev-gl'+(i?'':' z')+'" style="bottom:'+i*25+'%"><span>'+nn(top*i/4,0)+unit+'</span></div>';return g}
function tbl(h,r){return '<div class="scroll" style="overflow-x:auto;max-height:420px"><table class="tbl"><thead><tr>'+h.map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>'+r.map(x=>'<tr>'+x.map(y=>'<td>'+y+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'}
async function load(rg){
  const k=rg+'|'+Math.floor(Date.now()/600000);
  if(cache[k])return cache[k];
  const from=new Date(Date.now()-30*60000).toISOString().slice(0,16)+'Z';
  const r=await fetch(API+'/regional/intensity/'+from+'/fw48h/regionid/'+rg);
  if(!r.ok)throw new Error('HTTP '+r.status);
  const j=await r.json();const d=(j.data&&j.data.data)||[];const now=Date.now();
  const s=d.filter(x=>new Date(x.to).getTime()>now).map(x=>({from:x.from,to:x.to,g:x.intensity.forecast,ix:x.intensity.index,mix:x.generationmix||[]}));
  if(s.length<4)throw new Error('no data');
  return cache[k]={name:j.data.shortname,s};
}
function avg(s,a,n){let w=0,g=0;for(let i=0;i<Math.ceil(n);i++){const f=Math.min(1,n-i);w+=f;g+=s[a+i].g*f}return g/w}
function mixAvg(s,a,n){const m={};let w=0;for(let i=0;i<Math.ceil(n);i++){const f=Math.min(1,n-i);w+=f;s[a+i].mix.forEach(x=>{m[x.fuel]=(m[x.fuel]||0)+x.perc*f})}for(const k in m)m[k]/=w;return m}
function render(D){
  const cap=Math.max(1,num('cap')),p0=Math.min(100,Math.max(0,num('p0'))),p1=Math.min(100,Math.max(0,num('p1'))),kw=Math.max(.5,num('kw')),loss=Math.min(50,Math.max(0,num('loss')));
  const by=+$('by').value,s=D.s;
  const kwhBat=cap*Math.max(0,p1-p0)/100,kwh=kwhBat/(1-loss/100),hrs=kwh/kw,n=hrs*2;
  const lim=Math.min(s.length,by*2);
  let h='<span class="ev-live"><i></i>Live forecast · '+D.name+' · updated '+hf.format(new Date())+'</span>';
  if(kwh<=0)return h+'<p>Set “charge to” above “charge from”.</p>';
  let best=0,worst=0,fits=Math.ceil(n)<=lim;
  if(fits){let bv=1e9,wv=-1;for(let a=0;a+Math.ceil(n)<=lim;a++){const v=avg(s,a,n);if(v<bv-1e-9){bv=v;best=a}if(v>wv){wv=v;worst=a}}}
  const nW=Math.min(n,s.length),gNow=avg(s,0,Math.min(nW,s.length)),gBest=fits?avg(s,best,n):gNow,gWorst=fits?avg(s,worst,n):gNow;
  const kg=g=>kwh*g/1000;
  const save=kg(gNow)-kg(gBest),pct=gNow>0?save/kg(gNow)*100:0;
  const endT=new Date(new Date(s[best].from).getTime()+hrs*3600000);
  h+='<div class="big"><span>'+(!fits?'Charging takes longer than your window – start now':best===0?'Start now – this is the cleanest time in your window':'Cleanest time to start charging')+'</span><b>'+t(s[best].from)+'</b><em>'+nn(hrs,1)+' h charge, done about '+hf.format(endT)+' · '+nn(gBest,0)+' gCO₂/kWh</em></div>';
  const rows=[['Grid electricity',nn(kwh,1)+' kWh'],
   ['Start now ('+t(s[0].from)+')',nn(kg(gNow),1)+' kg CO₂'],
   ['Cleanest start ('+t(s[best].from)+')',nn(kg(gBest),1)+' kg CO₂'],
   ['Dirtiest start'+(fits?' ('+t(s[worst].from)+')':''),nn(kg(gWorst),1)+' kg CO₂']];
  if(fits&&save>0.05)rows.push(['You save by waiting','<b>'+nn(save,1)+' kg ('+nn(pct,0)+'%)</b>']);
  h+='<div class="kv">'+rows.map(r=>'<div>'+r[0]+'</div><div>'+r[1]+'</div>').join('')+'</div>';
  // chart A: 48h forecast, vertical columns
  const narrow=$('out').clientWidth<560;
  const S0=s.slice(0,Math.min(s.length,96));
  // 좁은 화면은 1시간 단위로 묶어 막대를 굵게
  const S=narrow?S0.reduce((a,x,i)=>{if(i%2===0)a.push({from:x.from,g:x.g,ix:x.ix,i0:i,k:1});else{const y=a[a.length-1];y.g=(y.g+x.g)/2}return a},[]):S0.map((x,i)=>Object.assign({i0:i},x));
  const step=narrow?2:1,top=nice(Math.max.apply(null,S.map(x=>x.g))/4)*4||100;
  let bars='';S.forEach((x,i)=>{const j=x.i0,inB=fits&&j+step>best&&j<best+Math.ceil(n),out=j>=lim;const c=i===0?ORANGE:inB?BLUE:out?'#E5E7EB':PALE;
    const d=new Date(x.from),H=+hof.format(d)%24,prev=i?+hof.format(new Date(S[i-1].from))%24:-1,show=H!==prev&&(narrow?H%12===0:H%6===0),lab=show&&i>0?'<small>'+(H===0?df.format(d):String(H).padStart(2,'0')+':00')+'</small>':'';
    bars+='<div class="ev-b" title="'+t(x.from)+': '+nn(x.g,0)+' gCO₂/kWh ('+x.ix+')"><span style="height:'+Math.max(.6,x.g/top*100).toFixed(1)+'%;background:'+c+'"></span>'+lab+'</div>'});
  const legA='<div class="ev-leg"><span><i style="background:'+ORANGE+'"></i>Now</span>'+(fits?'<span><i style="background:'+BLUE+'"></i>Best charging window</span>':'')+'<span><i style="background:'+PALE+'"></i>Forecast (gCO₂/kWh)</span>'+(lim<S0.length?'<span><i style="background:#E5E7EB"></i>After your car is needed</span>':'')+'</div>';
  const chartA=legA+'<div class="ev-plot">'+grid(top,'')+'<div class="ev-bars">'+bars+'</div></div>';
  const hourly=[];for(let i=0;i<S0.length;i+=2){const a=S0[i],b=S0[i+1];hourly.push([t(a.from),nn(b?(a.g+b.g)/2:a.g,0),a.ix])}
  h+='<h3 class="ev-h">Carbon intensity, next '+Math.round(S0.length/2)+' hours</h3>'+sw('a',chartA,tbl(['Hour starting','gCO₂/kWh','Index'],hourly));
  // chart B: fuel mix now vs best window, grouped vertical columns
  const mN=mixAvg(s,0,Math.min(n,s.length)||1),mB=fits?mixAvg(s,best,n):mN;
  const fuels=Object.keys(FUEL).filter(f=>Math.max(mN[f]||0,mB[f]||0)>=1).sort((a,b)=>(mB[b]||0)+(mN[b]||0)-(mB[a]||0)-(mN[a]||0));
  const topB=nice(Math.max.apply(null,fuels.map(f=>Math.max(mN[f]||0,mB[f]||0)))/4)*4;
  let g='';fuels.forEach(f=>{g+='<div class="ev-g"><div class="ev-cols"><div class="ev-c" title="'+FUEL[f]+', now: '+nn(mN[f]||0,1)+'%"><span style="height:'+((mN[f]||0)/topB*100).toFixed(1)+'%;background:'+ORANGE+'"></span></div>'+
    (fits?'<div class="ev-c" title="'+FUEL[f]+', best window: '+nn(mB[f]||0,1)+'%"><span style="height:'+((mB[f]||0)/topB*100).toFixed(1)+'%;background:'+BLUE+'"></span></div>':'')+'</div><div class="ev-x">'+($('out').clientWidth<420?FS[f]:FUEL[f])+'</div></div>'});
  const chartB='<div class="ev-leg"><span><i style="background:'+ORANGE+'"></i>If you charge now</span>'+(fits?'<span><i style="background:'+BLUE+'"></i>Best window</span>':'')+'</div><div class="ev-mix"><div class="ev-plot">'+grid(topB,'%')+'<div class="ev-grp">'+g+'</div></div></div>';
  h+='<h3 class="ev-h">Where the electricity comes from (%)</h3>'+sw('b',chartB,tbl(['Source','Now','Best window'],fuels.map(f=>[FUEL[f],nn(mN[f]||0,1)+'%',fits?nn(mB[f]||0,1)+'%':'—'])));
  h+='<p class="ev-src">Forecast: <a href="https://carbonintensity.org.uk/" rel="noopener" target="_blank">Carbon Intensity API</a> by the National Energy System Operator (NESO), CC BY 4.0. Times are UK time. A forecast, not a guarantee – it is updated every half hour.</p>';
  return h;
}
async function run(){const id=++busy;const o=$('out');
  try{const D=await load($('rg').value);if(id!==busy)return;o.innerHTML=render(D)}
  catch(e){if(id!==busy)return;o.innerHTML='<p class="ev-err">The live forecast could not be loaded right now ('+e.message+'). Please try again in a minute.</p>'}}
$('out').addEventListener('click',e=>{const b=e.target.closest('.ev-sw button');if(!b)return;view[b.dataset.k]=b.dataset.v;
  b.parentNode.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  ['chart','table'].forEach(v=>{const p=$('out').querySelector('[data-p="'+b.dataset.k+'-'+v+'"]');if(p)p.hidden=v!==b.dataset.v})});
$('form').addEventListener('input',run);$('form').addEventListener('change',run);run();
setInterval(()=>{if(!document.hidden)run()},10*60000);
})();
</script>'''

FAQ = [
 ("When is the best time to charge an electric car in the UK?",
  "The cleanest time is whenever the grid’s carbon intensity is lowest, which changes every day with the wind, sunshine and demand. Overnight and windy periods are often low, and weekday early evenings (around 4pm–8pm) are often high, but not always. The calculator reads the live 48-hour forecast for your region and picks the start time with the lowest average for your charge."),
 ("What does gCO₂/kWh mean?",
  "Grams of carbon dioxide emitted for each kilowatt-hour of electricity used. Multiply it by the kWh your car draws to get the CO₂ of a charge: 40 kWh at 200 gCO₂/kWh is 8 kg of CO₂; the same charge at 50 gCO₂/kWh is 2 kg."),
 ("Where does the forecast come from?",
  "From the Carbon Intensity API run by the National Energy System Operator (NESO). It gives a half-hourly forecast up to 48 hours ahead for Great Britain and for 14 regional distribution areas, together with the expected fuel mix. The data is published under the Creative Commons Attribution 4.0 licence."),
 ("Why is my region different from the national figure?",
  "Each region’s figure reflects the generation feeding its local network. Scotland often has much lower intensity because of wind and hydro, while regions that rely more on gas power stations and imports are usually higher. Choose your own region for the most relevant answer."),
 ("Does charging at the cleanest time also save money?",
  "Often, but not always. Clean periods tend to be times of low demand or high wind, which are also when time-of-use tariffs are cheapest. Your bill depends on your own tariff, though, so check its off-peak hours as well. Use our electricity cost calculator to work out the price of a charge."),
 ("Will my home charger let me choose the time?",
  "Smart charge points sold in Great Britain since 30 June 2022 must have smart functionality and come with default charging hours outside peak times (8am–11am and 4pm–10pm on weekdays). You can change or remove these hours and set a schedule in the charger’s app – set it to the start time shown here."),
]

ART = '''<h2 id="how">How this calculator works</h2>
<p>Britain’s electricity comes from a changing mix of wind, nuclear, gas, solar, biomass, hydro and imports, so the CO₂ released for each unit you use – the <b>carbon intensity</b> – rises and falls through the day. This page reads the live half-hourly forecast for your region and finds the start time that gives your charge the <b>lowest average carbon intensity</b> before you need the car.</p>
<ul><li><b>Electricity drawn</b> = battery size × (charge to − charge from) ÷ (1 − charging losses)</li>
<li><b>Charging time</b> = electricity drawn ÷ charger power</li>
<li><b>CO₂ of the charge</b> = electricity drawn × average gCO₂/kWh over the charging time ÷ 1,000 (kg)</li></ul>
<p>Every possible half-hour start in your window is tested and the lowest-average block is shown in blue on the chart. The orange bar is the current half-hour, so you can compare “plug in now” with “wait”.</p>
<h3>Worked example</h3>
<p>A 60 kWh battery charged from 20% to 80% takes 36 kWh. With 10% charging losses the car draws 40 kWh from the grid – about 5.7 hours on a 7 kW wallbox.</p>
''' + table(['Average carbon intensity while charging', 'CO₂ for this 40 kWh charge'],
            [['250 gCO₂/kWh', '10.0 kg'], ['150 gCO₂/kWh', '6.0 kg'], ['50 gCO₂/kWh', '2.0 kg']]) + '''
<p class="note">Example figures only. The live result above uses the actual forecast for your region.</p>
<h3 id="regions">Regions covered</h3>
<p>The forecast is available for Great Britain as a whole, for England, Scotland and Wales, and for 14 regional distribution areas: North Scotland, South Scotland, North West England, North East England, Yorkshire, North Wales &amp; Merseyside, South Wales, West Midlands, East Midlands, East England, South West England, South England, London and South East England. Northern Ireland is a separate grid and is not covered.</p>
<h3>Tips for cleaner charging</h3>
<ul><li><b>Set a schedule, not a reminder.</b> Enter the start time in your charger or car app so it starts even if you are asleep.</li>
<li><b>Only charge what you need.</b> Stopping at 80% for daily driving shortens the charge and lets it fit into the cleanest hours.</li>
<li><b>Check again before you plug in.</b> The forecast is refreshed every half hour, and windy spells can arrive earlier or later than expected.</li>
<li><b>Lower power can be fine.</b> A slower charge spread over a long clean night can beat a fast charge at a dirtier time.</li></ul>
<h3>Common mistakes</h3>
<ul><li>Using the national figure when your own region is very different.</li>
<li>Forgetting charging losses – the grid supplies more than the battery stores.</li>
<li>Treating the forecast as exact. It is a forecast and can change.</li></ul>
''' + faq_html(FAQ).replace('<h2 style="margin-top:22px">FAQ</h2>', '<h2 id="faq" style="margin-top:22px">FAQ</h2>') + '''
<p class="note">Sources (checked 24 November 2026): <a href="https://carbonintensity.org.uk/" rel="nofollow">Carbon Intensity API – NESO</a>; <a href="https://carbon-intensity.github.io/api-definitions/" rel="nofollow">Carbon Intensity API definitions (CC BY 4.0)</a>; <a href="https://www.legislation.gov.uk/uksi/2021/1467/contents" rel="nofollow">The Electric Vehicles (Smart Charge Points) Regulations 2021</a>. Related: <a href="/uk/electricity-cost-calculator.html">Electricity cost calculator</a>.</p>'''

TOC = [('form', 'Calculator'), ('how', 'How it works'), ('regions', 'Regions'), ('faq', 'FAQ')]


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
              {"@type": "ListItem", "position": 2, "name": "All calculators", "item": "https://honglifecalc.com/uk/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇬🇧 Live data · updated every 30 min</span>'
               f'<h1>{H1}</h1><p>See when the grid in your region will be cleanest over the next 48 hours, and how much CO₂ your charge will cause.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = ('<!--hl:deep--><div class="hl-by"><span>By <b>Hong Life Calculators</b></span><span>Checked <b>24 November 2026</b></span>'
           '<span>Data <b>NESO Carbon Intensity API</b></span></div><details class="card hl-toc" open><summary>On this page</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = s.replace('<script src="/assets/hl-viz.js" defer></script>', '')  # no automatic ring chart on this page
    assert 'api.carbonintensity.org.uk' in s and 'id="rg"' in s and 'id="how"' in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
