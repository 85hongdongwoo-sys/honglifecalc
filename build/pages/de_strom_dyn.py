"""DE: Dynamischer Stromtarif-Rechner – Börsenstrompreis (Day-Ahead, Viertelstunde) live von SMARD.de
(Bundesnetzagentur, CC BY 4.0). Vorlage: /de/stromkosten-rechner.html. Schreibt overlay/de/dynamischer-stromtarif-rechner.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/de/dynamischer-stromtarif-rechner.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Dynamischer Stromtarif Rechner 2026 – Börsenstrompreis & günstigste Uhrzeit'
H1 = 'Dynamischer Stromtarif-Rechner'
DESC = ('Wann ist Strom am günstigsten? Börsenstrompreise (Day-Ahead, je Viertelstunde) direkt von SMARD.de, '
        'günstigste Startzeit für Waschmaschine, Geschirrspüler oder E-Auto und Ersparnis gegenüber Ihrem Festpreis.')
DATE_DE = '24. November 2026'

CSS = '''<style id="dy-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.dy-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.dy-row .f{min-width:0}
.dy-live{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;color:#1f7a3a;background:#EAF6EE;border:1px solid #CBE8D4;border-radius:999px;padding:2px 10px;margin:0 0 10px;max-width:100%;flex-wrap:wrap}
.dy-live i{width:8px;height:8px;border-radius:50%;background:#1f9d4a;animation:dyp 1.6s infinite}@keyframes dyp{50%{opacity:.3}}
.dy-sw{display:inline-flex;background:#ececf0;border-radius:9px;padding:2px;margin:4px 0 8px}
.dy-sw button{border:0;background:transparent;font:inherit;font-size:13px;padding:6px 14px;border-radius:7px;color:#3a3a3c;cursor:pointer;min-height:32px}
.dy-sw button[aria-pressed="true"]{background:#fff;color:#1d1d1f;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.dy-h{font-size:16px;margin:18px 0 4px;color:#12305C}
.dy-leg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:#6e6e73;margin:2px 0 6px}
.dy-leg i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.dy-plot{position:relative;height:210px;margin:14px 6px 40px 46px}
.dy-gl{position:absolute;left:0;right:0;border-top:1px solid #ececf0;height:0}.dy-gl.z{border-top-color:#8e8e93}
.dy-gl span{position:absolute;right:100%;top:-8px;padding-right:7px;font-size:11px;color:#8e8e93;white-space:nowrap;font-variant-numeric:tabular-nums}
.dy-bars{position:absolute;inset:0;display:flex;gap:1px}
.dy-b{flex:1 1 0;min-width:0;height:100%;position:relative}
.dy-b span,.dy-c span{position:absolute;left:0;right:0;display:block}
.dy-b small{position:absolute;top:100%;left:0;margin-top:6px;font-size:10.5px;color:#6e6e73;white-space:nowrap;transform:translateX(-50%)}
.dy-b small:before{content:"";position:absolute;left:50%;top:-6px;height:4px;border-left:1px solid #c7c7cc}
.dy-grp{position:absolute;inset:0;display:flex}
.dy-g{flex:1 1 0;min-width:0;display:flex;flex-direction:column;position:relative}
.dy-cols{flex:1;display:flex;justify-content:center;gap:4px;padding:0 3px}
.dy-c{flex:0 1 24px;height:100%;position:relative;min-width:6px}
.dy-c span{border-radius:3px}
.dy-x{position:absolute;top:100%;left:-4px;right:-4px;padding-top:6px;text-align:center;font-size:11.5px;line-height:1.25;color:#3a3a3c;word-break:keep-all}
.dy-x small{display:block;color:#8e8e93;font-size:10.5px}
.dy-grpw .dy-plot{margin-bottom:50px}
.dy-err{background:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.dy-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
figure.dy-fig{margin:14px 0 6px;padding:12px 12px 4px;border:1px solid #ececf0;border-radius:12px;background:#fbfbfd}
figure.dy-fig figcaption{font-size:13px;color:#5B6B82;margin-top:4px;line-height:1.5}
@media(max-width:480px){.dy-row{grid-template-columns:1fr}.dy-plot{margin-left:40px}.dy-x{font-size:10.5px}.dy-cols{gap:2px;padding:0 2px}}
</style>'''

DEV = [('wm', 'Waschmaschine (60 °C)', 1.0, 2), ('gs', 'Geschirrspüler (Eco)', 0.9, 3), ('tr', 'Wäschetrockner', 2.5, 2),
       ('ea', 'E-Auto (30 kWh, Wallbox 11 kW)', 30, 3), ('ea7', 'E-Auto (20 kWh, 3,7 kW)', 20, 6), ('own', 'Eigene Angaben', 1.5, 2)]
dev_opts = ''.join(f'<option value="{k}" data-kwh="{kwh}" data-h="{h}">{n}</option>' for k, n, kwh, h in DEV)

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Ihr Gerät und Ihr Tarif</h2>
<label class="f"><span>Gerät</span><select id="dev">{dev_opts}</select><small>Wählen Sie ein Beispiel oder tragen Sie unten eigene Werte ein.</small></label>
<div class="dy-row"><label class="f"><span>Verbrauch pro Durchgang (kWh)</span><input id="kwh" inputmode="decimal" value="1,0"></label>
<label class="f"><span>Laufzeit (Stunden)</span><input id="dur" inputmode="decimal" value="2"></label></div>
<div class="dy-row"><label class="f"><span>Durchgänge pro Woche</span><input id="runs" inputmode="decimal" value="4"></label>
<label class="f"><span>Ihr Festpreis (ct/kWh, brutto)</span><input id="fix" inputmode="decimal" value="35"><small>Arbeitspreis von Ihrer Stromrechnung.</small></label></div>
<label class="f"><span>Aufschläge im dynamischen Tarif (ct/kWh, netto)</span><input id="add" inputmode="decimal" value="20"><small>Netzentgelt, Stromsteuer, Abgaben, Umlagen und Marge des Anbieters – steht im Preisblatt. Darauf kommen 19 % Mehrwertsteuer.</small></label>
</form><section class="card" id="out" aria-live="polite"><p>Börsenstrompreise werden geladen …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=id=>{let s=String($(id).value).trim().replace(/\s/g,'');if(/,/.test(s))s=s.replace(/\./g,'').replace(',','.');const v=parseFloat(s);return isFinite(v)?v:0};
const nn=(x,d)=>new Intl.NumberFormat('de-DE',{maximumFractionDigits:d==null?1:d,minimumFractionDigits:d==null?0:d}).format(x);
const TZ='Europe/Berlin';
const hf=new Intl.DateTimeFormat('de-DE',{timeZone:TZ,hour:'2-digit',minute:'2-digit',hour12:false});
const hof=new Intl.DateTimeFormat('en-GB',{timeZone:TZ,hour:'2-digit',hourCycle:'h23'});
const dk=new Intl.DateTimeFormat('en-CA',{timeZone:TZ,year:'numeric',month:'2-digit',day:'2-digit'});
const dl=new Intl.DateTimeFormat('de-DE',{timeZone:TZ,weekday:'short',day:'2-digit',month:'2-digit',year:'numeric'});
const API='https://www.smard.de/app/chart_data/4169/DE-LU/';
const BLUE='#3B82F6',ORANGE='#F59E0B',PALE='#BFD5FB',RED='#EF4444';
const VAT=1.19;
let data=null,view={a:'chart',b:'chart'},busy=0;
function nice(m){if(m<=0)return 1;const p=Math.pow(10,Math.floor(Math.log10(m))),f=m/p;for(const s of [1,1.2,1.5,2,2.5,3,4,5,6,8,10])if(f<=s+1e-9)return s*p;return 10*p}
function scale(vals){let lo=Math.min(0,...vals),hi=Math.max(0,...vals);if(hi===lo)hi=lo+1;const st=nice((hi-lo)/4);lo=Math.floor(lo/st-1e-9)*st;hi=Math.ceil(hi/st-1e-9)*st;if(hi<=lo)hi=lo+st;return{lo,hi,st}}
function grid(S,unit){let g='';for(let v=S.lo;v<=S.hi+S.st/2;v+=S.st){const y=(v-S.lo)/(S.hi-S.lo)*100;g+='<div class="dy-gl'+(Math.abs(v)<S.st/1e6?' z':'')+'" style="bottom:'+y.toFixed(2)+'%"><span>'+nn(Math.abs(v)<1e-9?0:v,S.st<1?1:0)+unit+'</span></div>'}return g}
function bar(S,v,c,r){const z=(0-S.lo)/(S.hi-S.lo)*100,y=(Math.min(v,0)-S.lo)/(S.hi-S.lo)*100,h=Math.max(.5,Math.abs(v)/(S.hi-S.lo)*100);return '<span style="bottom:'+y.toFixed(2)+'%;height:'+h.toFixed(2)+'%;background:'+c+';border-radius:'+(v>=0?r+' '+r+' 0 0':'0 0 '+r+' '+r)+'"></span>'}
function sw(k,a,b){return '<div class="dy-sw" role="group"><button type="button" data-k="'+k+'" data-v="chart" aria-pressed="'+(view[k]==='chart')+'">Diagramm</button><button type="button" data-k="'+k+'" data-v="table" aria-pressed="'+(view[k]==='table')+'">Tabelle</button></div><div data-p="'+k+'-chart"'+(view[k]==='chart'?'':' hidden')+'>'+a+'</div><div data-p="'+k+'-table"'+(view[k]==='table'?'':' hidden')+'>'+b+'</div>'}
function tbl(h,r){return '<div class="scroll" style="overflow-x:auto;max-height:420px"><table class="tbl"><thead><tr>'+h.map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>'+r.map(x=>'<tr>'+x.map(y=>'<td>'+y+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'}
async function load(){
  const idx=await fetch(API+'index_quarterhour.json').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json()});
  const ts=idx.timestamps.slice(-2);
  const parts=await Promise.all(ts.map(t=>fetch(API+'4169_DE-LU_quarterhour_'+t+'.json').then(r=>r.json())));
  const pts=[];parts.forEach(p=>p.series.forEach(x=>{if(x[1]!=null)pts.push({t:x[0],p:x[1]/10})}));
  pts.sort((a,b)=>a.t-b.t);
  if(pts.length<24)throw new Error('keine Daten');
  const days={};pts.forEach(x=>{const k=dk.format(new Date(x.t));(days[k]=days[k]||[]).push(x)});
  const keys=Object.keys(days).sort();let last=keys[keys.length-1];
  if(days[last].length<88&&keys.length>1)last=keys[keys.length-2];
  return{pts,days,keys,last};
}
function avg(a,i,n){let s=0;for(let k=0;k<n;k++)s+=a[i+k].p;return s/n}
function render(D){
  const kwh=Math.max(0,num('kwh')),dur=Math.max(.25,num('dur')),runs=Math.max(0,num('runs')),fix=Math.max(0,num('fix')),add=num('add');
  const day=D.days[D.last],n=Math.min(day.length,Math.max(1,Math.round(dur*4)));
  const endp=ct=>(ct+add)*VAT;
  let bi=0,wi=0,bv=1e9,wv=-1e9;for(let i=0;i+n<=day.length;i++){const v=avg(day,i,n);if(v<bv){bv=v;bi=i}if(v>wv){wv=v;wi=i}}
  const dAvg=day.reduce((s,x)=>s+x.p,0)/day.length;
  const eur=ct=>kwh*endp(ct)/100;
  const cB=eur(bv),cW=eur(wv),cA=eur(dAvg),cF=kwh*fix/100;
  const yr=(cF-cB)*runs*52,yrA=(cA-cB)*runs*52;
  const tEnd=new Date(day[bi].t+n*900000);
  let h='<span class="dy-live"><i></i>Börsenstrompreis DE-LU · '+dl.format(new Date(day[0].t))+' · SMARD.de</span>';
  h+='<div class="big"><span>Günstigste Startzeit an diesem Tag</span><b>'+hf.format(new Date(day[bi].t))+' Uhr</b><em>'+nn(dur,2).replace(/,00$/,'')+' h Laufzeit bis '+hf.format(tEnd)+' · Ø '+nn(bv,1)+' ct/kWh an der Börse · '+nn(cB,2)+' € pro Durchgang</em></div>';
  const rows=[['Günstigster Start ('+hf.format(new Date(day[bi].t))+')',nn(cB,2)+' €'],
    ['Teuerster Start ('+hf.format(new Date(day[wi].t))+')',nn(cW,2)+' €'],
    ['Zum Tagesdurchschnitt',nn(cA,2)+' €'],
    ['Mit Ihrem Festpreis ('+nn(fix,1)+' ct)',nn(cF,2)+' €'],
    ['Ersparnis pro Jahr ggü. Festpreis*','<b>'+(yr>=0?'':'−')+nn(Math.abs(yr),0)+' €</b>'],
    ['Ersparnis pro Jahr durch Verschieben*',nn(yrA,0)+' €']];
  h+='<div class="kv">'+rows.map(r=>'<div>'+r[0]+'</div><div>'+r[1]+'</div>').join('')+'</div>';
  h+='<p class="dy-src">* Hochrechnung: '+nn(runs,1)+' Durchgänge pro Woche, 52 Wochen, jeder Tag wie der gezeigte. Endpreis = (Börsenpreis + '+nn(add,1)+' ct) × 1,19.</p>';
  // Diagramm A: Börsenpreis des Tages
  const narrow=$('out').clientWidth<560;
  const S0=day.map((x,i)=>({t:x.t,p:x.p,i0:i})),step=narrow?4:1;
  const S=narrow?S0.reduce((a,x,i)=>{if(i%4===0)a.push({t:x.t,p:x.p,i0:i,c:1});else{const y=a[a.length-1];y.p=(y.p*y.c+x.p)/(y.c+1);y.c++}return a},[]):S0;
  const SA=scale(S.map(x=>x.p));
  let bars='';S.forEach((x,i)=>{const inB=x.i0+step>bi&&x.i0<bi+n,c=inB?BLUE:x.p<0?RED:PALE;const H=+hof.format(new Date(x.t))%24,m=new Date(x.t).getUTCMinutes();
    const lab=(m===0&&H%(narrow?6:3)===0&&i>0)?'<small>'+String(H).padStart(2,'0')+':00</small>':'';
    bars+='<div class="dy-b" title="'+hf.format(new Date(x.t))+' Uhr: '+nn(x.p,2)+' ct/kWh">'+bar(SA,x.p,c,'2px')+lab+'</div>'});
  const negs=S0.some(x=>x.p<0);
  const chartA='<div class="dy-leg"><span><i style="background:'+BLUE+'"></i>Günstigstes Zeitfenster</span><span><i style="background:'+PALE+'"></i>Börsenpreis (ct/kWh, netto)</span>'+(negs?'<span><i style="background:'+RED+'"></i>Negativer Preis</span>':'')+'</div><div class="dy-plot">'+grid(SA,'')+'<div class="dy-bars">'+bars+'</div></div>';
  const hourly=[];for(let i=0;i<day.length;i+=4){const q=day.slice(i,i+4),p=q.reduce((s,x)=>s+x.p,0)/q.length;hourly.push([hf.format(new Date(day[i].t))+' Uhr',nn(p,2),nn(endp(p),1),nn(Math.min(...q.map(x=>x.p)),2)+' / '+nn(Math.max(...q.map(x=>x.p)),2)])}
  h+='<h3 class="dy-h">Börsenstrompreis am '+dl.format(new Date(day[0].t))+'</h3>'+sw('a',chartA,tbl(['Stunde','Börse Ø ct/kWh','Endpreis ct/kWh (brutto)','Viertelstunden min / max'],hourly));
  // Diagramm B: Tageszeiten – gezeigter Tag vs. 7-Tage-Durchschnitt
  const SL=[[0,6,'Nacht','0–6 Uhr'],[6,10,'Morgen','6–10 Uhr'],[10,16,'Mittag','10–16 Uhr'],[16,20,'Abend','16–20 Uhr'],[20,24,'Spät','20–24 Uhr']];
  const ki=D.keys.indexOf(D.last),wk=D.keys.slice(Math.max(0,ki-6),ki+1);
  const sl=(arr,a,b)=>{const v=arr.filter(x=>{const H=+hof.format(new Date(x.t))%24;return H>=a&&H<b});return v.length?v.reduce((s,x)=>s+x.p,0)/v.length:0};
  const A1=SL.map(s=>sl(day,s[0],s[1])),A7=SL.map(s=>sl([].concat(...wk.map(k=>D.days[k])),s[0],s[1]));
  const SB=scale(A1.concat(A7));let g='';
  SL.forEach((s,i)=>{g+='<div class="dy-g"><div class="dy-cols"><div class="dy-c" title="'+s[2]+', dieser Tag: '+nn(A1[i],2)+' ct">'+bar(SB,A1[i],ORANGE,'4px')+'</div><div class="dy-c" title="'+s[2]+', Ø '+wk.length+' Tage: '+nn(A7[i],2)+' ct">'+bar(SB,A7[i],BLUE,'4px')+'</div></div><div class="dy-x">'+s[2]+'<small>'+s[3]+'</small></div></div>'});
  const chartB='<div class="dy-leg"><span><i style="background:'+ORANGE+'"></i>Gezeigter Tag</span><span><i style="background:'+BLUE+'"></i>Ø letzte '+wk.length+' Tage</span></div><div class="dy-grpw"><div class="dy-plot">'+grid(SB,'')+'<div class="dy-grp">'+g+'</div></div></div>';
  h+='<h3 class="dy-h">Wann ist Strom meist günstig? (ct/kWh)</h3>'+sw('b',chartB,tbl(['Tageszeit','Gezeigter Tag','Ø '+wk.length+' Tage'],SL.map((s,i)=>[s[2]+' ('+s[3]+')',nn(A1[i],2),nn(A7[i],2)])));
  h+='<p class="dy-src">Daten: Bundesnetzagentur | <a href="https://www.smard.de/" rel="noopener" target="_blank">SMARD.de</a>, Großhandelspreis Day-Ahead Deutschland/Luxemburg, Lizenz CC BY 4.0. Stand der Daten: '+hf.format(new Date(D.pts[D.pts.length-1].t))+' Uhr, '+dl.format(new Date(D.pts[D.pts.length-1].t))+'. SMARD veröffentlicht mit etwas Verzögerung; maßgeblich sind die Preise Ihres Anbieters.</p>';
  return h;
}
function draw(){if(data)$('out').innerHTML=render(data)}
async function run(){const id=++busy;try{data=await load();if(id===busy)draw()}catch(e){if(id===busy)$('out').innerHTML='<p class="dy-err">Die Börsenstrompreise konnten gerade nicht geladen werden ('+e.message+'). Bitte in einer Minute erneut versuchen.</p>'}}
$('dev').addEventListener('change',()=>{const o=$('dev').selectedOptions[0];if(o.value!=='own'){$('kwh').value=String(o.dataset.kwh).replace('.',',');$('dur').value=String(o.dataset.h).replace('.',',')}draw()});
$('out').addEventListener('click',e=>{const b=e.target.closest('.dy-sw button');if(!b)return;view[b.dataset.k]=b.dataset.v;
  b.parentNode.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  ['chart','table'].forEach(v=>{const p=$('out').querySelector('[data-p="'+b.dataset.k+'-'+v+'"]');if(p)p.hidden=v!==b.dataset.v})});
['kwh','dur','runs','fix','add'].forEach(id=>$(id).addEventListener('input',draw));
let rw=0;addEventListener('resize',()=>{clearTimeout(rw);rw=setTimeout(draw,200)});
run();setInterval(()=>{if(!document.hidden)run()},30*60000);
})();
</script>'''


def static_fig():
    """Feste Beispielgrafik (indexierbar): Börsenpreis vs. Endpreis zu drei Uhrzeiten."""
    groups = [('03:00 Uhr', 'Nacht, viel Wind', 8.0), ('13:00 Uhr', 'Mittag, viel Sonne', -1.0), ('19:00 Uhr', 'Abendspitze', 18.0)]
    add = 20.0
    vals = [(b, (b + add) * 1.19) for _, _, b in groups]
    lo, hi, st = -10, 50, 10
    def bar(v, c):
        y = (min(v, 0) - lo) / (hi - lo) * 100
        hh = max(.5, abs(v) / (hi - lo) * 100)
        r = '4px 4px 0 0' if v >= 0 else '0 0 4px 4px'
        return f'<span style="bottom:{y:.2f}%;height:{hh:.2f}%;background:{c};border-radius:{r}"></span>'
    grid = ''.join(f'<div class="dy-gl{" z" if v == 0 else ""}" style="bottom:{(v - lo) / (hi - lo) * 100:.2f}%"><span>{v}</span></div>'
                   for v in range(lo, hi + 1, st))
    g = ''
    for (name, sub, _), (b, e) in zip(groups, vals):
        bs, es = f'{b:.1f}'.replace('.', ','), f'{e:.1f}'.replace('.', ',')
        g += (f'<div class="dy-g"><div class="dy-cols"><div class="dy-c" title="{name}: Börse {bs} ct">{bar(b, "#F59E0B")}</div>'
              f'<div class="dy-c" title="{name}: Endpreis {es} ct">{bar(e, "#3B82F6")}</div></div>'
              f'<div class="dy-x">{name}<small>{sub}</small></div></div>')
    rows = [[n, f'{b:.1f} ct'.replace('.', ','), f'{e:.1f} ct'.replace('.', ',')] for (n, _, _), (b, e) in zip(groups, vals)]
    return ('<figure class="dy-fig" role="group" aria-label="Beispiel: Börsenpreis und Endpreis zu drei Uhrzeiten">'
            '<div class="dy-leg"><span><i style="background:#F59E0B"></i>Börsenpreis (netto)</span><span><i style="background:#3B82F6"></i>Endpreis inkl. 20 ct Aufschläge und 19 % MwSt.</span></div>'
            f'<div class="dy-grpw"><div class="dy-plot">{grid}<div class="dy-grp">{g}</div></div></div>'
            '<figcaption>Beispielrechnung (keine echten Marktdaten): Auch bei einem negativen Börsenpreis bleibt der Endpreis positiv, '
            'weil Netzentgelt, Steuern und Abgaben weiter anfallen.</figcaption></figure>'
            + table(['Uhrzeit', 'Börsenpreis', 'Endpreis brutto'], rows))


FAQ = [
 ("Was ist ein dynamischer Stromtarif?",
  "Bei einem dynamischen Stromtarif folgt der Arbeitspreis dem Börsenstrompreis am Day-Ahead-Markt. Der Preis ändert sich deshalb im Laufe des Tages – nachts und bei viel Wind oder Sonne ist Strom oft günstig, in den Abendstunden meist teurer. Zum Börsenpreis kommen Netzentgelt, Steuern, Abgaben, Umlagen und die Marge des Anbieters hinzu."),
 ("Muss jeder Stromanbieter einen dynamischen Tarif anbieten?",
  "Ja. Nach § 41a Energiewirtschaftsgesetz (EnWG) müssen seit dem 1. Januar 2025 alle Stromlieferanten einen dynamischen Tarif anbieten – für Kundinnen und Kunden, die ein intelligentes Messsystem (Smart Meter) haben."),
 ("Warum gibt es Preise für jede Viertelstunde?",
  "Seit dem 1. Oktober 2025 wird der Day-Ahead-Markt in Europa in 15-Minuten-Schritten statt in Stunden gehandelt. Pro Tag gibt es daher 96 Preise. Der Rechner nutzt diese Viertelstundenpreise; in der Tabelle sind sie zusätzlich zu Stunden zusammengefasst."),
 ("Was bedeutet ein negativer Strompreis?",
  "Wenn sehr viel Wind- und Solarstrom ins Netz kommt und wenig verbraucht wird, kann der Börsenpreis unter null fallen. Ihr Endpreis wird dadurch niedriger, bleibt aber in der Regel positiv, weil Netzentgelt, Stromsteuer und weitere Bestandteile unabhängig vom Börsenpreis anfallen."),
 ("Lohnt sich ein dynamischer Tarif für mich?",
  "Das hängt davon ab, wie viel Verbrauch Sie zeitlich verschieben können. Mit E-Auto, Wärmepumpe oder Batteriespeicher ist das Potenzial größer als mit Waschmaschine und Geschirrspüler allein. Beachten Sie auch die Kosten für das intelligente Messsystem und dass Preisspitzen – etwa in kalten, windstillen Wochen – auf Ihrer Rechnung ankommen."),
 ("Woher stammen die Daten?",
  "Die Preise kommen von SMARD.de, der Strommarktdaten-Plattform der Bundesnetzagentur (Großhandelspreis Day-Ahead für die Preiszone Deutschland/Luxemburg). Die Daten stehen unter der Lizenz CC BY 4.0 und werden mit etwas Verzögerung veröffentlicht. Maßgeblich für Ihre Abrechnung sind die Preise Ihres Anbieters."),
]

ART = '''<h2 id="how">So rechnet der Rechner</h2>
<p>Der Rechner lädt die aktuellen <b>Börsenstrompreise je Viertelstunde</b> von SMARD.de und sucht für Ihr Gerät das zusammenhängende Zeitfenster mit dem <b>niedrigsten Durchschnittspreis</b>. Daraus ergeben sich die Kosten pro Durchgang und eine Hochrechnung für ein Jahr.</p>
<ul><li><b>Endpreis je kWh</b> = (Börsenpreis + Aufschläge) × 1,19 (Mehrwertsteuer)</li>
<li><b>Kosten pro Durchgang</b> = Verbrauch in kWh × Ø Endpreis im Zeitfenster</li>
<li><b>Ersparnis pro Jahr</b> = (Kosten mit Festpreis − Kosten zur günstigsten Zeit) × Durchgänge pro Woche × 52</li></ul>
<h3 id="bild">Grafik: Woraus besteht der Preis?</h3>
<p>Der Börsenpreis ist nur ein Teil Ihres Strompreises. Die Grafik zeigt an drei Beispiel-Uhrzeiten, wie aus dem Börsenpreis der Endpreis wird.</p>
''' + static_fig() + '''
<h3>Rechenbeispiel</h3>
<p>Eine Waschmaschine braucht 1 kWh pro Waschgang. Kostet der Strom im günstigsten Zeitfenster an der Börse im Schnitt 6 ct/kWh, zahlen Sie bei 20 ct Aufschlägen (6 + 20) × 1,19 = 30,9 ct, also rund 0,31 € pro Waschgang. Mit einem Festpreis von 35 ct sind es 0,35 €. Bei 4 Waschgängen pro Woche spart das etwa 8,50 € im Jahr – mit einem E-Auto und 30 kWh pro Ladung ist die Ersparnis entsprechend dreißigmal so groß.</p>
<h3 id="bestandteile">Bestandteile des Strompreises</h3>
''' + table(['Bestandteil', 'Ändert sich mit der Uhrzeit?'],
            [['Börsenpreis (Day-Ahead)', 'Ja, jede Viertelstunde'], ['Netzentgelt', 'Meist nein (manche Netzbetreiber bieten zeitvariable Netzentgelte nach § 14a EnWG an)'],
             ['Stromsteuer, Konzessionsabgabe, Umlagen', 'Nein'], ['Marge / Grundgebühr des Anbieters', 'Nein'], ['Mehrwertsteuer (19 %)', 'Nein, aber auf den gesamten Preis']]) + '''
<h3>Tipps für günstigen Strom</h3>
<ul><li><b>Startzeitvorwahl nutzen:</b> Waschmaschine und Geschirrspüler mit „Ende in …“ so einstellen, dass sie im günstigen Fenster laufen.</li>
<li><b>E-Auto laden, wenn es billig ist:</b> Viele Wallboxen und Fahrzeug-Apps können automatisch zu günstigen Viertelstunden laden.</li>
<li><b>Mittags bei Sonne:</b> An sonnigen Tagen ist Strom um die Mittagszeit oft am günstigsten, im Winter eher nachts.</li>
<li><b>Abendspitze meiden:</b> Zwischen etwa 17 und 20 Uhr sind die Preise häufig am höchsten.</li></ul>
<h3>Häufige Fehler</h3>
<ul><li>Den Börsenpreis mit dem Endpreis verwechseln – Aufschläge und Mehrwertsteuer kommen immer dazu.</li>
<li>Die Kosten für das intelligente Messsystem nicht einrechnen.</li>
<li>Annehmen, jeder Tag sei so günstig wie ein windiger Sonntag.</li></ul>
''' + faq_html(FAQ, heading='Häufige Fragen').replace('<h2 style="margin-top:22px">Häufige Fragen</h2>', '<h2 id="faq" style="margin-top:22px">Häufige Fragen</h2>') + f'''
<p class="note">Quellen (Stand {DATE_DE}): <a href="https://www.smard.de/" rel="nofollow">SMARD.de – Bundesnetzagentur (CC BY 4.0)</a>; <a href="https://www.smard.de/en/15-minute-wholesale-prices-available-218078" rel="nofollow">SMARD: 15-Minuten-Großhandelspreise seit 1. Oktober 2025</a>; <a href="https://www.gesetze-im-internet.de/enwg_2005/__41a.html" rel="nofollow">§ 41a EnWG</a>. Verwandt: <a href="/de/stromkosten-rechner.html">Stromkosten-Rechner</a>.</p>'''

TOC = [('form', 'Rechner'), ('how', 'So wird gerechnet'), ('bild', 'Grafik: Preisbestandteile'), ('bestandteile', 'Bestandteile'), ('faq', 'Häufige Fragen')]


def main():
    s = open(os.path.join(ORIG, 'de/stromkosten-rechner.html'), encoding='utf-8').read()
    old = 'https://honglifecalc.com/de/stromkosten-rechner.html'
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + H1, s, count=1)
    s = s.replace(old, URL)
    assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": H1, "url": URL, "description": DESC,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "de-DE",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": "Alle Rechner", "item": "https://honglifecalc.com/de/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇩🇪 Live-Daten · SMARD.de</span>'
               f'<h1>{H1}</h1><p>Wann ist Strom am günstigsten? Börsenpreise je Viertelstunde, die beste Startzeit für Ihr Gerät und Ihre Ersparnis.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>Von <b>Hong Life Rechner</b></span><span>Geprüft <b>{DATE_DE}</b></span>'
           '<span>Daten <b>Bundesnetzagentur | SMARD.de</b></span></div><details class="card hl-toc" open><summary>Inhalt</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'smard.de/app/chart_data' in s and 'id="dev"' in s and 'id="bild"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
