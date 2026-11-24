"""DK: Hvornår er strømmen billigst? – spotpris pr. kvarter fra Energi Data Service (Energinet, CC BY 4.0).
Data hentes hver 3. time af .github/workflows/el-data.yml → grenen data-el → raw.githubusercontent.com (CORS ok).
Skabelon: /dk/fuel-cost-calculator.html. Skriver overlay/dk/hvornaar-er-stroemmen-billigst.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/dk/hvornaar-er-stroemmen-billigst.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Hvornår er strømmen billigst i dag? Elpris time for time 2026 (DK1/DK2)'
H1 = 'Hvornår er strømmen billigst?'
DESC = ('Se dagens og morgendagens elpris pr. kvarter for Vest- og Østdanmark på et døgnur, find det billigste tidspunkt '
        'til vaskemaskine, opvasker og elbil, og hvad du sparer om året.')
DATE_DA = '24. november 2026'
SRC = 'https://raw.githubusercontent.com/85hongdongwoo-sys/honglifecalc/data-el/el/eds.json'

CSS = '''<style id="ek-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.ek-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.ek-row .f{min-width:0}
.ek-seg{display:inline-flex;background:#ececf0;border-radius:10px;padding:3px;gap:2px;flex-wrap:wrap;max-width:100%}
.ek-seg button{border:0;background:transparent;font:inherit;font-size:14px;padding:7px 14px;border-radius:8px;color:#3a3a3c;cursor:pointer;min-height:36px}
.ek-seg button[aria-pressed="true"]{background:#fff;color:#1d1d1f;font-weight:700;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.ek-live{display:inline-flex;align-items:baseline;gap:6px;font-size:12.5px;font-weight:700;color:#1f7a3a;background:#EAF6EE;border:1px solid #CBE8D4;border-radius:999px;padding:2px 10px;margin:0 0 10px;max-width:100%;flex-wrap:wrap}
.ek-live i{flex:0 0 8px;width:8px;height:8px;border-radius:50%;background:#1f9d4a;animation:ekp 1.6s infinite}@keyframes ekp{50%{opacity:.3}}
.ek-top{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:16px;align-items:center}
.ek-clock{position:relative;width:100%;max-width:300px;margin:0 auto}
.ek-clock svg{width:100%;height:auto;display:block}
.ek-clock .seg{transition:opacity .2s}.ek-clock .seg.dim{opacity:.35}
.ek-hand{transform-origin:150px 150px;transition:transform .6s ease}
.ek-mid{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;pointer-events:none}
.ek-mid small{font-size:12px;color:#6e6e73}.ek-mid b{font-size:30px;color:#12305C;line-height:1.1}.ek-mid em{font-style:normal;font-size:12.5px;color:#1f7a3a;font-weight:700}
.ek-cards{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.ek-cards div{background:#F5F8FC;border:1px solid #E3EAF4;border-radius:12px;padding:9px 11px;min-width:0}
.ek-cards b{display:block;font-size:18px;color:#12305C;overflow-wrap:anywhere}.ek-cards span{font-size:12px;color:#5B6B82}
.ek-cards .win{background:#EEF7F0;border-color:#CBE8D4}.ek-cards .win b{color:#17663A}
.ek-scale{display:flex;align-items:center;gap:8px;font-size:12px;color:#6e6e73;margin:8px 0 0}
.ek-scale i{flex:1;height:8px;border-radius:4px;background:linear-gradient(90deg,#16a34a,#84cc16,#facc15,#f97316,#dc2626)}
.ek-h{font-size:16px;margin:20px 0 4px;color:#12305C}
.ek-sw{display:inline-flex;background:#ececf0;border-radius:9px;padding:2px;margin:4px 0 8px}
.ek-sw button{border:0;background:transparent;font:inherit;font-size:13px;padding:6px 14px;border-radius:7px;color:#3a3a3c;cursor:pointer;min-height:32px}
.ek-sw button[aria-pressed="true"]{background:#fff;color:#1d1d1f;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.ek-plot{position:relative;height:210px;margin:14px 6px 34px 40px}
.ek-gl{position:absolute;left:0;right:0;border-top:1px solid #ececf0;height:0}.ek-gl.z{border-top-color:#8e8e93}
.ek-gl span{position:absolute;right:100%;top:-8px;padding-right:7px;font-size:11px;color:#8e8e93;white-space:nowrap}
.ek-bars{position:absolute;inset:0;display:flex;gap:2px;align-items:stretch}
.ek-b{flex:1 1 0;min-width:0;position:relative}
.ek-b span{position:absolute;left:0;right:0;border-radius:3px 3px 0 0;display:block;transform-origin:bottom;animation:ekg .7s ease both}
@keyframes ekg{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.ek-b.win span{outline:2px solid #12305C;outline-offset:0}
.ek-b small{position:absolute;top:100%;left:50%;transform:translateX(-50%);margin-top:5px;font-size:10.5px;color:#6e6e73;white-space:nowrap}
.ek-err{background:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.ek-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
@media(max-width:620px){.ek-top{grid-template-columns:1fr}.ek-row{grid-template-columns:1fr}.ek-plot{margin-left:34px}}
@media(prefers-reduced-motion:reduce){.ek-b span{animation:none}.ek-hand{transition:none}}
</style>'''

DEV = [('wm', 'Vaskemaskine (40 °C)', 0.8, 2), ('op', 'Opvaskemaskine (eco)', 0.9, 3), ('td', 'Tørretumbler', 2.0, 2),
       ('ev', 'Elbil – 30 kWh (11 kW ladeboks)', 30, 3), ('ev2', 'Elbil – 15 kWh (stikkontakt 3,7 kW)', 15, 4), ('own', 'Egne tal', 1.5, 2)]
dev_opts = ''.join(f'<option value="{k}" data-kwh="{kwh}" data-h="{h}">{n}</option>' for k, n, kwh, h in DEV)

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Dit apparat og din elpris</h2>
<div class="f"><span>Område</span><div class="ek-seg" id="area"><button type="button" data-a="DK1" aria-pressed="true">Vestdanmark (DK1)</button><button type="button" data-a="DK2" aria-pressed="false">Østdanmark (DK2)</button></div>
<small>Vest for Storebælt (Jylland, Fyn) = DK1 · Sjælland, Lolland-Falster og Bornholm = DK2.</small></div>
<label class="f"><span>Apparat</span><select id="dev">{dev_opts}</select></label>
<div class="ek-row"><label class="f"><span>Forbrug pr. gang (kWh)</span><input id="kwh" inputmode="decimal" value="0,8"></label>
<label class="f"><span>Varighed (timer)</span><input id="dur" inputmode="decimal" value="2"></label></div>
<div class="ek-row"><label class="f"><span>Gange om ugen</span><input id="runs" inputmode="decimal" value="4"></label>
<label class="f"><span>Tillæg (øre/kWh ekskl. moms)</span><input id="add" inputmode="decimal" value="50"><small>Nettarif, Energinets tariffer og elselskabets tillæg – står på din elregning. Elafgiften (0,8 øre) og 25 % moms lægges til automatisk.</small></label></div>
</form><section class="card" id="out" aria-live="polite"><p>Henter elpriser …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=id=>{let s=String($(id).value).trim().replace(/\s/g,'');if(/,/.test(s))s=s.replace(/\./g,'').replace(',','.');const v=parseFloat(s);return isFinite(v)?v:0};
const nn=(x,d)=>new Intl.NumberFormat('da-DK',{maximumFractionDigits:d==null?1:d,minimumFractionDigits:d==null?0:d}).format(x);
const kr=x=>new Intl.NumberFormat('da-DK',{style:'currency',currency:'DKK',minimumFractionDigits:2,maximumFractionDigits:2}).format(x);
const TZ='Europe/Copenhagen';
const hf=new Intl.DateTimeFormat('da-DK',{timeZone:TZ,hour:'2-digit',minute:'2-digit',hour12:false});
const hof=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,hour:'2-digit',hourCycle:'h23'});
const dkey=new Intl.DateTimeFormat('en-CA',{timeZone:TZ,year:'numeric',month:'2-digit',day:'2-digit'});
const dl=new Intl.DateTimeFormat('da-DK',{timeZone:TZ,weekday:'long',day:'numeric',month:'long'});
const SRC='__SRC__';
const ELAFGIFT=0.8,VAT=1.25;
let raw=null,area='DK1',day=null,view='chart',busy=0;
function col(t){t=Math.max(0,Math.min(1,t));const st=[[22,163,74],[132,204,22],[250,204,21],[249,115,22],[220,38,38]];const p=t*4,i=Math.min(3,Math.floor(p)),f=p-i,a=st[i],b=st[i+1];return 'rgb('+a.map((v,k)=>Math.round(v+(b[k]-v)*f)).join(',')+')'}
function days(){const pts=raw.areas[area].map(x=>({t:x[0],p:x[1]}));const D={};pts.forEach(x=>{const k=dkey.format(new Date(x.t));(D[k]=D[k]||[]).push(x)});return D}
async function load(){const r=await fetch(SRC,{cache:'no-cache'});if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}
function arc(cx,cy,r1,r2,a0,a1){const p=(r,a)=>[cx+r*Math.sin(a),cy-r*Math.cos(a)];const L=a1-a0>Math.PI?1:0;const [x1,y1]=p(r2,a0),[x2,y2]=p(r2,a1),[x3,y3]=p(r1,a1),[x4,y4]=p(r1,a0);return 'M'+x1.toFixed(2)+' '+y1.toFixed(2)+'A'+r2+' '+r2+' 0 '+L+' 1 '+x2.toFixed(2)+' '+y2.toFixed(2)+'L'+x3.toFixed(2)+' '+y3.toFixed(2)+'A'+r1+' '+r1+' 0 '+L+' 0 '+x4.toFixed(2)+' '+y4.toFixed(2)+'Z'}
function draw(){if(!raw)return;const D=days(),keys=Object.keys(D).sort(),today=dkey.format(new Date());
 const avail=keys.filter(k=>k>=today&&D[k].length>=80);if(!day||!avail.includes(day))day=avail[0]||keys[keys.length-1];
 const q=D[day];if(!q||!q.length){$('out').innerHTML='<p class="ek-err">Ingen priser for denne dag endnu.</p>';return}
 const kwh=Math.max(0,num('kwh')),dur=Math.max(.25,num('dur')),runs=Math.max(0,num('runs')),add=num('add');
 const endp=o=>(o+add+ELAFGIFT)*VAT;const n=Math.min(q.length,Math.max(1,Math.round(dur*4)));
 const now=Date.now();let start=0;if(day===today){start=q.findIndex(x=>x.t+900000>now);if(start<0)start=0}
 let bi=-1,bv=1e9,wv=-1e9,wi=0;for(let i=start;i+n<=q.length;i++){let s=0;for(let k=0;k<n;k++)s+=q[i+k].p;s/=n;if(s<bv){bv=s;bi=i}if(s>wv){wv=s;wi=i}}
 if(bi<0){bi=Math.max(0,q.length-n);bv=q.slice(bi).reduce((a,x)=>a+x.p,0)/n;wi=bi;wv=bv}
 const avg=q.reduce((a,x)=>a+x.p,0)/q.length;
 const cost=o=>kwh*endp(o)/100,cB=cost(bv),cW=cost(wv),cA=cost(avg),yr=(cA-cB)*runs*52;
 const hours=[];for(let h=0;h<24;h++){const v=q.filter(x=>+hof.format(new Date(x.t))%24===h);hours.push(v.length?v.reduce((a,x)=>a+x.p,0)/v.length:null)}
 const vals=hours.filter(v=>v!=null),lo=Math.min(...vals),hi=Math.max(...vals),norm=v=>hi>lo?(v-lo)/(hi-lo):.5;
 const sH=+hof.format(new Date(q[bi].t))%24,sM=new Date(q[bi].t).getUTCMinutes(),endT=new Date(q[bi].t+n*900000);
 // døgnur
 let svg='<svg viewBox="0 0 300 300" role="img" aria-label="Elpris time for time på et døgnur"><circle cx="150" cy="150" r="140" fill="#fff" stroke="#E3EAF4"/>';
 const wa0=(sH+sM/60)/24*2*Math.PI,wa1=wa0+n/96*2*Math.PI;
 hours.forEach((v,h)=>{if(v==null)return;const a0=h/24*2*Math.PI+.012,a1=(h+1)/24*2*Math.PI-.012;svg+='<path class="seg" d="'+arc(150,150,92,132,a0,a1)+'" fill="'+col(norm(v))+'"><title>'+String(h).padStart(2,'0')+':00 – '+nn(v,1)+' øre/kWh (spot)</title></path>'});
 svg+='<path d="'+arc(150,150,134,142,wa0,Math.min(wa1,wa0+2*Math.PI-.001))+'" fill="#12305C"/>';
 for(let h=0;h<24;h+=3){const a=h/24*2*Math.PI;svg+='<text x="'+(150+70*Math.sin(a)).toFixed(1)+'" y="'+(154-70*Math.cos(a)).toFixed(1)+'" font-size="11" text-anchor="middle" fill="#6e6e73">'+String(h).padStart(2,'0')+'</text>'}
 const na=day===today?((+hof.format(new Date())%24)+new Date().getMinutes()/60)/24*360:((sH+sM/60)/24*360);
 svg+='<g class="ek-hand" style="transform:rotate('+na.toFixed(1)+'deg)"><polygon points="150,60 144,71 156,71" fill="#12305C"/></g></svg>';
 let h='<span class="ek-live"><i></i>Spotpris '+area+' · '+dl.format(new Date(q[0].t))+' · Energinet</span>';
 if(avail.length>1)h+='<div class="ek-seg" id="days" style="margin:0 0 10px">'+avail.map(k=>'<button type="button" data-d="'+k+'" aria-pressed="'+(k===day)+'">'+(k===today?'I dag':dl.format(new Date(D[k][0].t)))+'</button>').join('')+'</div>';
 h+='<div class="ek-top"><div class="ek-clock">'+svg+'<div class="ek-mid"><small>Billigst at starte</small><b>'+hf.format(new Date(q[bi].t))+'</b><em>til '+hf.format(endT)+'</em></div></div>';
 h+='<div class="ek-cards"><div class="win"><span>Pr. gang på det billigste tidspunkt</span><b>'+kr(cB)+'</b><span>Ø '+nn(endp(bv),1)+' øre/kWh inkl. alt</span></div>'
  +'<div><span>På det dyreste tidspunkt ('+hf.format(new Date(q[wi].t))+')</span><b>'+kr(cW)+'</b></div>'
  +'<div><span>Til dagens gennemsnit</span><b>'+kr(cA)+'</b></div>'
  +'<div class="win"><span>Du sparer om året*</span><b>'+kr(Math.max(0,yr))+'</b><span>ved at flytte '+nn(runs,1)+' gange/uge</span></div></div></div>';
 h+='<div class="ek-scale"><span>Billig</span><i></i><span>Dyr</span><span>· spotpris '+nn(lo,0)+'–'+nn(hi,0)+' øre/kWh</span></div>';
 // søjler
 const lo2=Math.min(0,lo),st=Math.max(10,Math.ceil((hi-lo2)/4/10)*10),top=Math.ceil(hi/st)*st,bot=Math.floor(lo2/st)*st,span=top-bot||1;
 let g='<div class="ek-plot">';for(let v=bot;v<=top+1e-9;v+=st)g+='<div class="ek-gl'+(v===0?' z':'')+'" style="bottom:'+((v-bot)/span*100).toFixed(2)+'%"><span>'+nn(v,0)+'</span></div>';
 g+='<div class="ek-bars">'+hours.map((v,i)=>{if(v==null)return '<div class="ek-b"></div>';const inW=(i>=sH&&i<sH+Math.ceil(dur+sM/60));const y=(Math.min(v,0)-bot)/span*100,hh=Math.max(.6,Math.abs(v)/span*100);return '<div class="ek-b'+(inW?' win':'')+'" title="'+String(i).padStart(2,'0')+':00 · '+nn(v,1)+' øre"><span style="bottom:'+y.toFixed(2)+'%;height:'+hh.toFixed(2)+'%;background:'+col(norm(v))+';animation-delay:'+(i*25)+'ms"></span>'+(i%3===0?'<small>'+String(i).padStart(2,'0')+'</small>':'')+'</div>'}).join('')+'</div></div>';
 let t='<div style="overflow-x:auto;max-height:420px"><table class="tbl"><thead><tr><th>Time</th><th>Spotpris øre/kWh</th><th>Din pris øre/kWh (inkl. tillæg, afgift og moms)</th></tr></thead><tbody>';
 hours.forEach((v,i)=>{if(v!=null)t+='<tr><td>'+String(i).padStart(2,'0')+':00–'+String((i+1)%24).padStart(2,'0')+':00</td><td>'+nn(v,1)+'</td><td>'+nn(endp(v),1)+'</td></tr>'});t+='</tbody></table></div>';
 h+='<h3 class="ek-h">Spotpris time for time (øre/kWh ekskl. moms)</h3><div class="ek-sw" role="group"><button type="button" data-v="chart" aria-pressed="'+(view==='chart')+'">Søjler</button><button type="button" data-v="table" aria-pressed="'+(view==='table')+'">Tabel</button></div><div'+(view==='chart'?'':' hidden')+'>'+g+'</div><div'+(view==='table'?'':' hidden')+'>'+t+'</div>';
 h+='<p class="ek-src">* Hvis hver dag var som denne. Din pris = (spotpris + '+nn(add,1)+' øre tillæg + 0,8 øre elafgift) × 1,25. Kilde: Energi Data Service, Energinet (CC BY 4.0) – Day-ahead-priser pr. kvarter, opdateret '+hf.format(new Date(raw.updated))+'.</p>';
 $('out').innerHTML=h}
async function run(){const id=++busy;try{raw=await load();if(id===busy)draw()}catch(e){if(id===busy)$('out').innerHTML='<p class="ek-err">Elpriserne kunne ikke hentes lige nu ('+e.message+'). Prøv igen om lidt.</p>'}}
$('area').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;area=b.dataset.a;[...$('area').children].forEach(x=>x.setAttribute('aria-pressed',x===b));draw()});
$('dev').addEventListener('change',()=>{const o=$('dev').selectedOptions[0];if(o.value!=='own'){$('kwh').value=String(o.dataset.kwh).replace('.',',');$('dur').value=String(o.dataset.h).replace('.',',')}draw()});
$('out').addEventListener('click',e=>{const d=e.target.closest('#days button');if(d){day=d.dataset.d;draw();return}const b=e.target.closest('.ek-sw button');if(b){view=b.dataset.v;draw()}});
['kwh','dur','runs','add'].forEach(id=>$(id).addEventListener('input',draw));
run();setInterval(()=>{if(!document.hidden)run()},30*60000);
})();
</script>'''.replace('__SRC__', SRC)

FAQ = [
 ("Hvornår på dagen er strømmen billigst?",
  "Typisk om natten og midt på dagen, når det blæser eller solen skinner meget. Det dyreste tidspunkt er oftest kl. 17–21, hvor forbruget er højt og mange net-selskaber også har deres højeste tarif. Døgnuret viser den aktuelle dag med farver fra grøn (billig) til rød (dyr)."),
 ("Hvorfor er der en pris for hvert kvarter?",
  "Siden 1. oktober 2025 handles strøm i Norden i kvarter-perioder på day-ahead-markedet. Priserne for næste døgn offentliggøres omkring kl. 13 dagen før."),
 ("Hvad er forskellen på DK1 og DK2?",
  "Danmark er delt i to prisområder. DK1 er Vestdanmark (Jylland og Fyn), DK2 er Østdanmark (Sjælland, Lolland-Falster og Bornholm). Priserne er ofte ens, men kan afvige når forbindelserne er fyldt."),
 ("Hvor stor er elafgiften i 2026?",
  "Elafgiften er midlertidigt sat ned til 0,8 øre pr. kWh i 2026 og 2027 (Skattestyrelsen). Beregneren lægger den til automatisk, sammen med 25 % moms."),
 ("Hvad skal jeg skrive som tillæg?",
  "Læg nettarif, Energinets tariffer og dit elselskabs tillæg sammen fra din elregning (øre pr. kWh uden moms). Nettariffen er ofte højest kl. 17–21, så det billigste tidspunkt bliver typisk endnu bedre, end beregneren viser."),
 ("Hvor kommer priserne fra?",
  "Fra Energi Data Service, som drives af Energinet. Data er frie under CC BY 4.0. Hong Life henter dem hver tredje time."),
]

ART = '''<p><b>Kort sagt:</b> Vælg Vest- eller Østdanmark og dit apparat. Døgnuret farver hver time efter spotprisen – <b>grøn er billig, rød er dyr</b> – og den mørke bue viser det billigste tidspunkt at starte. Morgendagens priser kommer ved 13-tiden.</p>
<h2 id="how">Sådan regner beregneren</h2>
<ul><li><b>Din pris pr. kWh</b> = (spotpris + tillæg + elafgift 0,8 øre) × 1,25 (moms)</li>
<li><b>Billigste start</b> = det sammenhængende tidsrum med lavest gennemsnitlig spotpris (i dag tæller kun tidspunkter, der ikke er gået)</li>
<li><b>Pris pr. gang</b> = forbrug (kWh) × din gennemsnitlige pris i tidsrummet</li>
<li><b>Besparelse pr. år</b> = (pris til dagens gennemsnit − pris på billigste tidspunkt) × gange pr. uge × 52</li></ul>
<h3 id="eksempel">Regneeksempel</h3>
''' + table(['Situation', 'Beregning', 'Resultat'], [
    ['Vaskemaskine 0,8 kWh, spotpris 40 øre, tillæg 50 øre', '0,8 × (40 + 50 + 0,8) × 1,25 ÷ 100', '0,91 kr. pr. vask'],
    ['Samme vask ved spotpris 160 øre', '0,8 × (160 + 50 + 0,8) × 1,25 ÷ 100', '2,11 kr. pr. vask'],
    ['Forskel, 4 vaske om ugen', '(2,11 − 0,91) × 4 × 52', 'ca. 250 kr. om året'],
    ['Elbil 30 kWh, samme prisforskel 120 øre', '30 × 120 × 1,25 ÷ 100', '45 kr. pr. opladning'],
]) + '''
<h3 id="tips">Gode råd</h3>
<ul><li><b>Brug udskudt start:</b> De fleste vaskemaskiner og opvaskere kan sættes til at starte senere.</li>
<li><b>Lad elbilen om natten:</b> Mange ladebokse og biler kan styres efter timepris.</li>
<li><b>Undgå kl. 17–21:</b> Her er både spotpris og nettarif ofte højest.</li>
<li><b>Tjek morgendagen efter kl. 13:</b> Så kan du planlægge næste døgn.</li></ul>
''' + faq_html(FAQ, heading='Ofte stillede spørgsmål').replace('<h2 style="margin-top:22px">Ofte stillede spørgsmål</h2>', '<h2 id="faq" style="margin-top:22px">Ofte stillede spørgsmål</h2>') + f'''
<p class="note">Kilder (tjekket {DATE_DA}): <a href="https://www.energidataservice.dk/tso-electricity/DayAheadPrices" rel="nofollow">Energi Data Service – Day-ahead prices (Energinet, CC BY 4.0)</a>; <a href="https://skat.dk/erhverv/afgifter-paa-varer-og-ydelser-punktafgifter/nyhedsbrev-afgifter/midlertidig-nedsaettelse-af-elafgiften-i-2026-og-2027" rel="nofollow">Skattestyrelsen: midlertidig nedsættelse af elafgiften i 2026 og 2027</a>. Se også: <a href="/dk/beregn-elforbrug.html">Beregn elforbrug</a>.</p>'''

TOC = [('form', 'Beregner'), ('how', 'Sådan regnes der'), ('eksempel', 'Regneeksempel'), ('tips', 'Gode råd'), ('faq', 'Spørgsmål')]


def main():
    s = open(os.path.join(ORIG, 'dk/fuel-cost-calculator.html'), encoding='utf-8').read()
    old = 'https://honglifecalc.com/dk/fuel-cost-calculator.html'
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + H1, s, count=1)
    s = s.replace(old, URL)
    assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": H1, "url": URL, "description": DESC,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "da-DK",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "DKK"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": "Alle beregnere", "item": "https://honglifecalc.com/dk/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇩🇰 Live elpriser · Energinet</span>'
               f'<h1>{H1}</h1><p>Dagens elpris time for time på et døgnur – og det billigste tidspunkt til vask, opvask og elbil.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>Af <b>Hong Life-beregnere</b></span><span>Tjekket <b>{DATE_DA}</b></span>'
           '<span>Data <b>Energinet (CC BY 4.0)</b></span></div><details class="card hl-toc" open><summary>Indhold</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'data-el/el/eds.json' in s and 'id="area"' in s and 'id="eksempel"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
