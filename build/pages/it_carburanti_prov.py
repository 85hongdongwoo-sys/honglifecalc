"""IT: Prezzo carburante oggi nella tua provincia – medie self/servito e distributori più economici (MIMIT Osservaprezzi, IODL 2.0),
costo del pieno e del pendolarismo. Dati: .github/workflows/it-fuel-data.yml → grenen data-it → raw.githubusercontent.com.
Modello: /it/calcolo-costo-carburante.html. Scrive overlay/it/prezzo-carburante-provincia.html."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/it/prezzo-carburante-provincia.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Prezzo benzina e gasolio oggi per provincia 2026 – distributori più economici e costo del pieno'
H1 = 'Prezzo carburante oggi nella tua provincia'
DESC = ('Prezzi medi di benzina, gasolio, GPL e metano (self e servito) in ogni provincia dai dati ufficiali MIMIT, i distributori più '
        'economici vicino a te, il costo del pieno e quanto spendi al mese per andare al lavoro.')
DATE_IT = '24 novembre 2026'
SRC = 'https://raw.githubusercontent.com/85hongdongwoo-sys/honglifecalc/data-it/it/carburanti.json'

PROV = {'AG': 'Agrigento', 'AL': 'Alessandria', 'AN': 'Ancona', 'AO': 'Aosta', 'AP': 'Ascoli Piceno', 'AQ': "L'Aquila", 'AR': 'Arezzo',
        'AT': 'Asti', 'AV': 'Avellino', 'BA': 'Bari', 'BG': 'Bergamo', 'BI': 'Biella', 'BL': 'Belluno', 'BN': 'Benevento', 'BO': 'Bologna',
        'BR': 'Brindisi', 'BS': 'Brescia', 'BT': 'Barletta-Andria-Trani', 'BZ': 'Bolzano', 'CA': 'Cagliari', 'CB': 'Campobasso',
        'CE': 'Caserta', 'CH': 'Chieti', 'CL': 'Caltanissetta', 'CN': 'Cuneo', 'CO': 'Como', 'CR': 'Cremona', 'CS': 'Cosenza',
        'CT': 'Catania', 'CZ': 'Catanzaro', 'EN': 'Enna', 'FC': 'Forlì-Cesena', 'FE': 'Ferrara', 'FG': 'Foggia', 'FI': 'Firenze',
        'FM': 'Fermo', 'FR': 'Frosinone', 'GE': 'Genova', 'GO': 'Gorizia', 'GR': 'Grosseto', 'IM': 'Imperia', 'IS': 'Isernia',
        'KR': 'Crotone', 'LC': 'Lecco', 'LE': 'Lecce', 'LI': 'Livorno', 'LO': 'Lodi', 'LT': 'Latina', 'LU': 'Lucca', 'MB': 'Monza e Brianza',
        'MC': 'Macerata', 'ME': 'Messina', 'MI': 'Milano', 'MN': 'Mantova', 'MO': 'Modena', 'MS': 'Massa-Carrara', 'MT': 'Matera',
        'NA': 'Napoli', 'NO': 'Novara', 'NU': 'Nuoro', 'OR': 'Oristano', 'PA': 'Palermo', 'PC': 'Piacenza', 'PD': 'Padova',
        'PE': 'Pescara', 'PG': 'Perugia', 'PI': 'Pisa', 'PN': 'Pordenone', 'PO': 'Prato', 'PR': 'Parma', 'PT': 'Pistoia',
        'PU': 'Pesaro e Urbino', 'PV': 'Pavia', 'PZ': 'Potenza', 'RA': 'Ravenna', 'RC': 'Reggio Calabria', 'RE': 'Reggio Emilia',
        'RG': 'Ragusa', 'RI': 'Rieti', 'RM': 'Roma', 'RN': 'Rimini', 'RO': 'Rovigo', 'SA': 'Salerno', 'SI': 'Siena', 'SO': 'Sondrio',
        'SP': 'La Spezia', 'SR': 'Siracusa', 'SS': 'Sassari', 'SU': 'Sud Sardegna', 'SV': 'Savona', 'TA': 'Taranto', 'TE': 'Teramo',
        'TN': 'Trento', 'TO': 'Torino', 'TP': 'Trapani', 'TR': 'Terni', 'TS': 'Trieste', 'TV': 'Treviso', 'UD': 'Udine', 'VA': 'Varese',
        'VB': 'Verbano-Cusio-Ossola', 'VC': 'Vercelli', 'VE': 'Venezia', 'VI': 'Vicenza', 'VR': 'Verona', 'VT': 'Viterbo', 'VV': 'Vibo Valentia'}

CSS = '''<style id="ic-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.ic-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.ic-row .f{min-width:0}
.app>#form,.app>#out{min-width:0;max-width:100%}@media(max-width:860px){section.app{grid-template-columns:minmax(0,1fr)!important}}
.ic-seg{display:inline-flex;background:#ececf0;border-radius:10px;padding:3px;gap:2px;flex-wrap:wrap;max-width:100%}
.ic-seg button{border:0;background:transparent;font:inherit;font-size:14px;padding:7px 12px;border-radius:8px;color:#3a3a3c;cursor:pointer;min-height:36px}
.ic-seg button[aria-pressed="true"]{background:#fff;color:#1d1d1f;font-weight:700;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.ic-live{display:inline-flex;align-items:baseline;gap:6px;font-size:12.5px;font-weight:700;color:#1f4f8a;background:#EAF1FB;border:1px solid #CFDDF3;border-radius:999px;padding:2px 10px;margin:0 0 10px;max-width:100%;flex-wrap:wrap}
.ic-pump{display:grid;grid-template-columns:96px minmax(0,1fr);gap:14px;align-items:center;background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:16px;padding:12px;margin-bottom:12px}
.ic-pump svg{width:96px;height:120px;display:block}
.ic-fill{transform-origin:bottom;animation:icfill 1.4s ease both}@keyframes icfill{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.ic-big small{display:block;font-size:12.5px;color:#5B6B82}.ic-big b{display:block;font-size:30px;color:#12305C;line-height:1.1;font-variant-numeric:tabular-nums}
.ic-big span{display:block;font-size:13px;color:#3a3a3c;margin-top:4px}
.ic-sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:6px 0 12px}
.ic-sum div{background-color:#F5F8FC;border:1px solid #E3EAF4;border-radius:12px;padding:9px 11px;min-width:0}
.ic-sum b{display:block;font-size:18px;color:#12305C;overflow-wrap:anywhere}.ic-sum span{font-size:12px;color:#5B6B82}
.ic-h{font-size:16px;margin:18px 0 4px;color:#12305C}
.ic-plot{position:relative;height:200px;margin:12px 4px 54px 44px}
.ic-gl{position:absolute;left:0;right:0;border-top:1px solid #ececf0;height:0}.ic-gl span{position:absolute;right:100%;top:-8px;padding-right:6px;font-size:11px;color:#8e8e93;white-space:nowrap}
.ic-bars{position:absolute;inset:0;display:flex;gap:4px}
.ic-b{flex:1 1 0;min-width:0;position:relative}
.ic-b span{position:absolute;left:10%;right:10%;bottom:0;border-radius:4px 4px 0 0;display:block;transform-origin:bottom;animation:icfill .8s ease both}
.ic-b small{position:absolute;top:100%;left:-4px;right:-4px;margin-top:5px;font-size:10.5px;text-align:center;color:#3a3a3c;font-weight:600}
.ic-b em{position:absolute;left:-6px;right:-6px;font-style:normal;font-size:10px;text-align:center;color:#1d1d1f;font-variant-numeric:tabular-nums}
.ic-b.me span{background:#F59E0B!important}.ic-b.me small{color:#B45309}
.ic-tb{width:100%;border-collapse:collapse;font-size:14px}.ic-tb th,.ic-tb td{padding:7px 6px;border-bottom:1px solid #ececf0;text-align:left;vertical-align:top}
.ic-tb td.n,.ic-tb th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}.ic-tb small{display:block;color:#6e6e73;font-size:12px}
.ic-err{background-color:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.ic-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
@media(max-width:600px){.ic-row,.ic-sum{grid-template-columns:1fr}.ic-b em{display:none}
 .ic-tb thead{display:none}.ic-tb tr{display:block;border-bottom:1px solid #ececf0;padding:6px 0}.ic-tb td{display:flex;justify-content:space-between;gap:10px;border:0;padding:3px 4px}
 .ic-tb td:before{content:attr(data-l);color:#6e6e73;font-size:12.5px}.ic-tb td>span{text-align:right;min-width:0;overflow-wrap:anywhere}}
@media(prefers-reduced-motion:reduce){.ic-fill,.ic-b span{animation:none}}
</style>'''

prov_opts = ''.join(f'<option value="{k}"{" selected" if k == "RM" else ""}>{v} ({k})</option>' for k, v in sorted(PROV.items(), key=lambda x: x[1]))

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Provincia e carburante</h2>
<label class="f"><span>Provincia</span><select id="prov">{prov_opts}</select></label>
<div class="f"><span>Carburante</span><div class="ic-seg" id="fuel"><button type="button" data-f="benzina" aria-pressed="true">Benzina</button><button type="button" data-f="gasolio" aria-pressed="false">Gasolio</button><button type="button" data-f="gpl" aria-pressed="false">GPL</button><button type="button" data-f="metano" aria-pressed="false">Metano</button></div></div>
<div class="ic-row"><label class="f"><span>Capacità serbatoio (litri; metano: kg)</span><input id="tank" inputmode="decimal" value="45"></label>
<label class="f"><span>Consumo (km per litro)</span><input id="kml" inputmode="decimal" value="15"><small>Metano: km per kg.</small></label></div>
<div class="ic-row"><label class="f"><span>Km casa–lavoro (solo andata)</span><input id="km" inputmode="decimal" value="20"></label>
<label class="f"><span>Giorni di lavoro al mese</span><input id="gg" inputmode="decimal" value="21"></label></div>
</form><section class="card" id="out" aria-live="polite"><p>Carico i prezzi ufficiali …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=id=>{let s=String($(id).value).trim().replace(/\s/g,'');if(/,/.test(s))s=s.replace(/\./g,'').replace(',','.');const v=parseFloat(s);return isFinite(v)?v:0};
const eur=(x,d)=>new Intl.NumberFormat('it-IT',{style:'currency',currency:'EUR',minimumFractionDigits:d==null?2:d,maximumFractionDigits:d==null?2:d}).format(x);
const n3=x=>new Intl.NumberFormat('it-IT',{minimumFractionDigits:3,maximumFractionDigits:3}).format(x);
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const SRC='__SRC__';const NAMES=__NAMES__;
const UNIT={benzina:'L',gasolio:'L',gpl:'L',metano:'kg'};
let D=null,fuel='benzina',me=null;
function km(a,b,c,d){const R=6371,r=Math.PI/180,x=Math.sin((c-a)*r/2)**2+Math.cos(a*r)*Math.cos(c*r)*Math.sin((d-b)*r/2)**2;return 2*R*Math.asin(Math.sqrt(x))}
function pump(level){const h=Math.max(.08,Math.min(1,level))*72;return '<svg viewBox="0 0 96 120" aria-hidden="true"><rect x="10" y="10" width="54" height="100" rx="8" fill="#12305C"/><rect x="18" y="20" width="38" height="22" rx="3" fill="#E0F2FE"/><rect x="18" y="'+(102-h).toFixed(1)+'" width="38" height="'+h.toFixed(1)+'" rx="3" fill="#F59E0B" class="ic-fill"/><rect x="18" y="50" width="38" height="52" rx="3" fill="none" stroke="#93C5FD"/><path d="M64 34 h12 a8 8 0 0 1 8 8 v46 a6 6 0 0 1 -12 0 v-20" fill="none" stroke="#12305C" stroke-width="5" stroke-linecap="round"/><rect x="4" y="108" width="66" height="8" rx="3" fill="#64748B"/></svg>'}
function draw(){if(!D)return;const p=$('prov').value,P=D.prov[p],F=P&&P[fuel];
 if(!F||!F.s){$('out').innerHTML='<p class="ic-live">⛽ '+esc(NAMES[p]||p)+'</p><p class="ic-err">Nessun prezzo self per questo carburante in questa provincia oggi.</p>';return}
 const tank=Math.max(0,num('tank')),kml=Math.max(.1,num('kml')),kmd=Math.max(0,num('km')),gg=Math.max(0,num('gg'));
 const avg=F.s[0],low=F.s[1],nat=D.nat[fuel]?D.nat[fuel][0]:avg,serv=F.v?F.v[0]:null,u=UNIT[fuel];
 const all=Object.keys(D.prov).filter(k=>D.prov[k][fuel]&&D.prov[k][fuel].s).map(k=>[k,D.prov[k][fuel].s[0]]).sort((a,b)=>a[1]-b[1]);
 const rank=all.findIndex(x=>x[0]===p)+1,mo=kmd*2*gg/kml*avg;
 let h='<span class="ic-live">⛽ '+esc(NAMES[p]||p)+' · '+F.s[2]+' distributori self · dati MIMIT '+esc(D.estrazione.replace(/^Estrazione del\s*/i,''))+'</span>';
 h+='<div class="ic-pump">'+pump(1-(rank-1)/Math.max(1,all.length-1))+'<div class="ic-big"><small>Prezzo medio self '+fuel+'</small><b>'+n3(avg)+' €/'+u+'</b><span>'+(avg<=nat?'🟢 ':'🔴 ')+n3(Math.abs(avg-nat))+' € '+(avg<=nat?'sotto':'sopra')+' la media italiana ('+n3(nat)+') · '+rank+'ª più economica su '+all.length+'</span></div></div>';
 h+='<div class="ic-sum"><div><span>Pieno da '+tank+' '+u+' al prezzo medio</span><b>'+eur(tank*avg)+'</b><span>al più economico: '+eur(tank*low)+'</span></div>'
  +'<div><span>Casa–lavoro al mese</span><b>'+eur(mo)+'</b><span>'+(kmd*2*gg).toLocaleString('it-IT')+' km · '+(kmd*2*gg/kml).toLocaleString('it-IT',{maximumFractionDigits:0})+' '+u+'</span></div>'
  +'<div><span>Self invece del servito</span><b>'+(serv?eur((serv-avg)*tank)+' / pieno':'–')+'</b><span>'+(serv?'servito medio '+n3(serv)+' €':'nessun dato servito')+'</span></div></div>';
 // grafico: 6 più economiche, la tua, 6 più care
 const pick=[...all.slice(0,6),...(rank>6&&rank<=all.length-6?[all[rank-1]]:[]),...all.slice(-6)];
 const lo=Math.floor(Math.min(...pick.map(x=>x[1]))*20-1)/20,hi=Math.ceil(Math.max(...pick.map(x=>x[1]))*20)/20,sp=hi-lo||.05;
 let g='<div class="ic-plot">';for(let v=lo;v<=hi+1e-9;v+=.05)g+='<div class="ic-gl" style="bottom:'+((v-lo)/sp*100).toFixed(1)+'%"><span>'+v.toFixed(2).replace('.',',')+'</span></div>';
 g+='<div class="ic-bars">'+pick.map((x,i)=>{const hh=Math.max(2,(x[1]-lo)/sp*100);return '<div class="ic-b'+(x[0]===p?' me':'')+'" title="'+esc(NAMES[x[0]]||x[0])+': '+n3(x[1])+'"><span style="height:'+hh.toFixed(1)+'%;background:'+(i<6?'#22A06B':'#EF4444')+';animation-delay:'+(i*40)+'ms"></span><em style="bottom:calc('+hh.toFixed(1)+'% + 2px)">'+x[1].toFixed(3).replace('.',',')+'</em><small>'+x[0]+'</small></div>'}).join('')+'</div></div>';
 h+='<h3 class="ic-h">Le province più economiche e più care ('+fuel+' self, €/'+u+')</h3>'+g;
 let list=F.top.map(t=>({p:t[0],n:t[1],b:t[2],ad:t[3],c:t[4],d:me?km(me.lat,me.lon,t[5],t[6]):null}));
 h+='<h3 class="ic-h">Distributori più economici in provincia (self)</h3>'+(me?'':'<p style="margin:0 0 6px"><button type="button" id="near" class="ic-seg" style="padding:7px 12px;border:0;border-radius:9px;cursor:pointer;font:inherit">📍 Mostra la distanza da me</button></p>');
 h+='<table class="ic-tb"><thead><tr><th>Distributore</th><th class="n">€/'+u+'</th>'+(me?'<th class="n">Distanza</th>':'')+'<th class="n">Pieno</th></tr></thead><tbody>'+list.map(s=>'<tr><td data-l="Distributore"><span>'+esc(s.b||s.n)+'<small>'+esc(s.ad)+' – '+esc(s.c)+'</small></span></td><td class="n" data-l="Prezzo"><span>'+n3(s.p)+'</span></td>'+(me?'<td class="n" data-l="Distanza"><span>'+s.d.toFixed(1).replace('.',',')+' km</span></td>':'')+'<td class="n" data-l="Pieno"><span>'+eur(s.p*tank)+'</span></td></tr>').join('')+'</tbody></table>';
 h+='<p class="ic-src">Fonte: Ministero delle Imprese e del Made in Italy – Osservaprezzi carburanti (IODL 2.0), prezzi comunicati dai gestori e praticati alle ore 8. Medie calcolate da Hong Life su tutti i distributori della provincia.</p>';
 $('out').innerHTML=h}
async function run(){try{const r=await fetch(SRC,{cache:'no-cache'});if(!r.ok)throw new Error('HTTP '+r.status);D=await r.json();draw()}catch(e){$('out').innerHTML='<p class="ic-err">Impossibile caricare i prezzi ('+esc(e.message)+'). Riprova tra poco.</p>'}}
$('fuel').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;fuel=b.dataset.f;[...$('fuel').children].forEach(x=>x.setAttribute('aria-pressed',x===b));draw()});
$('prov').addEventListener('change',draw);['tank','kml','km','gg'].forEach(id=>$(id).addEventListener('input',draw));
$('out').addEventListener('click',e=>{if(!e.target.closest('#near'))return;navigator.geolocation&&navigator.geolocation.getCurrentPosition(p=>{me={lat:p.coords.latitude,lon:p.coords.longitude};draw()},()=>{},{timeout:10000})});
run();
})();
</script>'''.replace('__SRC__', SRC).replace('__NAMES__', json.dumps(PROV, ensure_ascii=False))

FAQ = [
 ("Da dove vengono i prezzi?",
  "Dall’Osservatorio prezzi carburanti del Ministero delle Imprese e del Made in Italy (MIMIT). I gestori sono obbligati a comunicare i prezzi praticati; il Ministero pubblica ogni giorno i prezzi in vigore alle ore 8 come dati aperti (IODL 2.0)."),
 ("Perché il prezzo al distributore può essere diverso?",
  "I dati sono quelli praticati alle 8 del mattino e comunicati dal gestore: durante la giornata il prezzo può cambiare. Controlla sempre il cartello prima di fare rifornimento."),
 ("Quanto si risparmia con il self?",
  "Dipende dalla provincia: il riquadro «Self invece del servito» confronta la media self con la media servito nella stessa provincia e moltiplica per il tuo serbatoio."),
 ("Come calcolo il costo mensile casa–lavoro?",
  "Km andata × 2 × giorni lavorativi ÷ km per litro × prezzo medio self della provincia."),
 ("Ogni quanto si aggiornano i dati?",
  "Una volta al giorno: la pagina mostra la data dell’estrazione MIMIT usata."),
]

ART = '''<p><b>In breve:</b> scegli provincia e carburante. Vedi subito il <b>prezzo medio self di oggi</b>, quanto è sopra o sotto la media italiana, il costo del pieno, la spesa mensile per andare al lavoro e i <b>15 distributori più economici</b> della provincia.</p>
<h2 id="come">Come funziona il calcolo</h2>
<ul><li><b>Prezzo medio</b> = media dei prezzi self comunicati da tutti i distributori della provincia (ore 8)</li>
<li><b>Pieno</b> = capacità serbatoio × prezzo</li>
<li><b>Casa–lavoro al mese</b> = km andata × 2 × giorni ÷ km per litro × prezzo medio</li>
<li><b>Risparmio self</b> = (media servito − media self) × capacità serbatoio</li></ul>
<h3 id="esempi">Esempi</h3>
''' + table(['Situazione', 'Calcolo', 'Risultato'], [
    ['Pieno 45 L a 1,800 €/L', '45 × 1,800', '81,00 €'],
    ['Pieno 45 L a 1,760 €/L', '45 × 1,760', '79,20 € (1,80 € in meno)'],
    ['20 km andata, 21 giorni, 15 km/L, 1,800 €/L', '20 × 2 × 21 ÷ 15 × 1,800', '100,80 € al mese'],
    ['Servito 0,15 €/L più caro, serbatoio 45 L', '0,15 × 45', '6,75 € in più a pieno'],
]) + '''
<h3>Consigli</h3>
<ul><li>Il self costa quasi sempre meno del servito: la differenza può superare i 15 centesimi al litro.</li>
<li>In autostrada i prezzi sono di solito più alti: fai il pieno prima di partire.</li>
<li>Una differenza di pochi centesimi non vale una lunga deviazione: il carburante per arrivarci costa anche lui.</li></ul>
''' + faq_html(FAQ, heading='Domande frequenti').replace('<h2 style="margin-top:22px">Domande frequenti</h2>', '<h2 id="faq" style="margin-top:22px">Domande frequenti</h2>') + f'''
<p class="note">Fonti (verificate il {DATE_IT}): <a href="https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti" rel="nofollow">MIMIT – Carburanti: prezzi praticati e anagrafica degli impianti (IODL 2.0)</a>; <a href="https://carburanti.mise.gov.it/" rel="nofollow">Osservaprezzi carburanti</a>. Vedi anche: <a href="/it/calcolo-costo-carburante.html">Calcolo del costo del carburante</a>.</p>'''

TOC = [('form', 'Calcolatore'), ('come', 'Come funziona'), ('esempi', 'Esempi'), ('faq', 'Domande frequenti')]


def main():
    s = open(os.path.join(ORIG, 'it/calcolo-costo-carburante.html'), encoding='utf-8').read()
    old = 'https://honglifecalc.com/it/calcolo-costo-carburante.html'
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + H1, s, count=1)
    s = s.replace(old, URL)
    assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": H1, "url": URL, "description": DESC,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "it-IT",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": "Tutti i calcolatori", "item": "https://honglifecalc.com/it/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇮🇹 Prezzi ufficiali MIMIT · aggiornati ogni giorno</span>'
               f'<h1>{H1}</h1><p>Benzina, gasolio, GPL e metano: media self e servito, distributori più economici e costo del pieno.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>A cura di <b>Hong Life Calcolatori</b></span><span>Verificato il <b>{DATE_IT}</b></span>'
           '<span>Dati <b>MIMIT (IODL 2.0)</b></span></div><details class="card hl-toc" open><summary>Indice</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'data-it/it/carburanti.json' in s and 'id="prov"' in s and 'id="esempi"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
