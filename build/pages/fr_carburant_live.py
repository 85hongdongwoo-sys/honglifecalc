"""FR : Carburant le moins cher autour de moi – prix en temps réel (flux instantané v2, data.economie.gouv.fr, Licence Ouverte)
+ géocodage Géoplateforme IGN (data.geopf.fr, Licence Ouverte). Modèle : /fr/calcul-cout-carburant.html.
Écrit overlay/fr/carburant-moins-cher-autour-de-moi.html. Les deux API répondent en CORS depuis honglifecalc.com (testé le 24/11/2026)."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/fr/carburant-moins-cher-autour-de-moi.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = 'Carburant le moins cher autour de moi 2026 – prix en direct et coût du plein'
H1 = 'Carburant le moins cher autour de moi'
DESC = ('Prix officiels des stations-service en temps réel autour de votre commune : gazole, E10, SP98, SP95, E85, GPLc. '
        'Coût du plein, détour compris, et économie par rapport à la moyenne.')
DATE_FR = '24 novembre 2026'

CSS = '''<style id="fc-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.fc-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.fc-row .f{min-width:0}
.fc-loc{display:flex;gap:8px;align-items:stretch;flex-wrap:wrap}.fc-loc input{flex:1 1 160px;min-width:0}
.fc-loc button{border:1px solid #C9D3E3;background:#fff;border-radius:10px;padding:8px 12px;font:inherit;font-size:14px;cursor:pointer;min-height:40px;max-width:100%}
.fc-live{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;color:#1f4f8a;background:#EAF1FB;border:1px solid #CFDDF3;border-radius:999px;padding:2px 10px;margin:0 0 10px;max-width:100%;flex-wrap:wrap}
.fc-sw{display:inline-flex;background:#ececf0;border-radius:9px;padding:2px;margin:4px 0 8px}
.fc-sw button{border:0;background:transparent;font:inherit;font-size:13px;padding:6px 14px;border-radius:7px;color:#3a3a3c;cursor:pointer;min-height:32px}
.fc-sw button[aria-pressed="true"]{background:#fff;color:#1d1d1f;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.fc-sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:6px 0 12px}
.fc-sum div{background:#F5F8FC;border:1px solid #E3EAF4;border-radius:10px;padding:8px 10px;min-width:0}
.fc-sum b{display:block;font-size:18px;color:#12305C;overflow-wrap:anywhere}.fc-sum span{font-size:12px;color:#5B6B82}
.fc-tb{width:100%;border-collapse:collapse;font-size:14px}.fc-tb th,.fc-tb td{padding:7px 6px;border-bottom:1px solid #ececf0;text-align:left;vertical-align:top}
.fc-tb td.n,.fc-tb th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.fc-tb tr.best td{background:#EEF7F0}.fc-tb small{display:block;color:#6e6e73;font-size:12px}
.fc-plot{position:relative;height:200px;margin:14px 6px 64px 44px}
.fc-gl{position:absolute;left:0;right:0;border-top:1px solid #ececf0;height:0}
.fc-gl span{position:absolute;right:100%;top:-8px;padding-right:7px;font-size:11px;color:#8e8e93;white-space:nowrap}
.fc-bars{position:absolute;inset:0;display:flex;gap:6px}
.fc-b{flex:1 1 0;min-width:0;height:100%;position:relative}
.fc-b span{position:absolute;left:12%;right:12%;bottom:0;border-radius:4px 4px 0 0;display:block}
.fc-b em{position:absolute;left:-2px;right:-2px;font-style:normal;font-size:11px;text-align:center;color:#1d1d1f;font-variant-numeric:tabular-nums}
.fc-b small{position:absolute;top:100%;left:-3px;right:-3px;margin-top:6px;font-size:10.5px;line-height:1.2;color:#3a3a3c;text-align:center;word-break:break-word;max-height:3.6em;overflow:hidden}
.fc-err{background:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.fc-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
@media(max-width:560px){.fc-b em{font-size:9.5px}.fc-b:nth-child(even) em{display:none}.fc-row{grid-template-columns:1fr}.fc-sum{grid-template-columns:1fr}
 .fc-tb thead{display:none}.fc-tb tr{display:block;border-bottom:1px solid #ececf0;padding:6px 0}.fc-tb td{display:flex;justify-content:space-between;gap:10px;border:0;padding:3px 4px}
 .fc-tb td:before{content:attr(data-l);color:#6e6e73;font-size:12.5px;flex:0 0 auto}.fc-tb td.n{white-space:normal}.fc-tb td>span{text-align:right;min-width:0;overflow-wrap:anywhere}}
</style>'''

FUELS = [('gazole', 'Gazole (B7)'), ('e10', 'SP95-E10'), ('sp98', 'SP98'), ('sp95', 'SP95'), ('e85', 'E85 (superéthanol)'), ('gplc', 'GPLc')]
fuel_opts = ''.join(f'<option value="{k}">{n}</option>' for k, n in FUELS)

FORM = f'''<form class="card" id="form" onsubmit="return false"><h2>Où et quoi ?</h2>
<label class="f"><span>Commune, code postal ou adresse</span><div class="fc-loc"><input id="q" value="Lyon 69003" autocomplete="postal-code"><button type="button" id="go">Chercher</button><button type="button" id="me">📍 Ma position</button></div>
<small>Votre position sert seulement à chercher les stations proches ; elle n’est pas enregistrée.</small></label>
<div class="fc-row"><label class="f"><span>Carburant</span><select id="fuel">{fuel_opts}</select></label>
<label class="f"><span>Rayon de recherche</span><select id="rad"><option value="3">3 km</option><option value="5" selected>5 km</option><option value="10">10 km</option><option value="20">20 km</option></select></label></div>
<div class="fc-row"><label class="f"><span>Litres à mettre</span><input id="lit" inputmode="decimal" value="40"><small>Un plein de citadine ≈ 40 L, de familiale ≈ 55 L.</small></label>
<label class="f"><span>Consommation (L/100 km)</span><input id="cons" inputmode="decimal" value="6,5"><small>Sert à compter le carburant du détour (aller-retour).</small></label></div>
</form><section class="card" id="out" aria-live="polite"><p>Recherche des stations …</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=id=>{let s=String($(id).value).trim().replace(/\s/g,'').replace(',','.');const v=parseFloat(s);return isFinite(v)?v:0};
const eur=(x,d)=>new Intl.NumberFormat('fr-FR',{style:'currency',currency:'EUR',minimumFractionDigits:d==null?2:d,maximumFractionDigits:d==null?2:d}).format(x);
const nb=(x,d)=>new Intl.NumberFormat('fr-FR',{maximumFractionDigits:d,minimumFractionDigits:d}).format(x);
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const cap=s=>String(s||'').toLowerCase().replace(/(^|[\s\-'’])([a-zà-ÿ])/g,(m,a,b)=>a+b.toUpperCase());
const API='https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records';
const GEO='https://data.geopf.fr/geocodage/search';
const NAMES={gazole:'Gazole',e10:'SP95-E10',sp98:'SP98',sp95:'SP95',e85:'E85',gplc:'GPLc'};
let pos=null,place='',rows=[],view='table',busy=0;
function km(a,b,c,d){const R=6371,r=Math.PI/180,x=Math.sin((c-a)*r/2)**2+Math.cos(a*r)*Math.cos(c*r)*Math.sin((d-b)*r/2)**2;return 2*R*Math.asin(Math.sqrt(x))}
const dfmt=new Intl.DateTimeFormat('fr-FR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit',timeZone:'Europe/Paris'});
async function geocode(q){const r=await fetch(GEO+'?limit=1&q='+encodeURIComponent(q));if(!r.ok)throw new Error('géocodage '+r.status);const j=await r.json();const f=j.features&&j.features[0];if(!f)throw new Error('adresse introuvable');return{lat:f.geometry.coordinates[1],lon:f.geometry.coordinates[0],label:f.properties.label}}
async function stations(){const f=$('fuel').value,R=+$('rad').value;
 const where="within_distance(geom, geom'POINT("+pos.lon+" "+pos.lat+")', "+R+"km) AND "+f+"_prix is not null";
 const u=API+'?limit=100&select='+encodeURIComponent('id,adresse,ville,cp,geom,'+f+'_prix,'+f+'_maj')+'&where='+encodeURIComponent(where)+'&order_by='+f+'_prix';
 const r=await fetch(u);if(!r.ok)throw new Error('prix '+r.status);const j=await r.json();
 return (j.results||[]).filter(x=>x.geom&&x[f+'_prix']>0).map(x=>({id:x.id,adr:cap(x.adresse),ville:cap(x.ville),cp:x.cp,p:+x[f+'_prix'],maj:x[f+'_maj'],d:km(pos.lat,pos.lon,x.geom.lat,x.geom.lon)}))}
async function run(){const id=++busy;$('out').innerHTML='<p>Recherche des stations …</p>';
 try{if(!pos){const g=await geocode($('q').value);pos={lat:g.lat,lon:g.lon};place=g.label}
  const r=await stations();if(id!==busy)return;rows=r;draw()}
 catch(e){if(id===busy)$('out').innerHTML='<p class="fc-err">Les prix n’ont pas pu être chargés ('+esc(e.message)+'). Vérifiez l’adresse ou réessayez dans une minute.</p>'}}
function draw(){const f=$('fuel').value,L=num('lit'),C=num('cons');
 if(!rows.length){$('out').innerHTML='<p class="fc-live">📍 '+esc(place)+'</p><p class="fc-err">Aucune station ne vend du '+NAMES[f]+' dans ce rayon. Agrandissez le rayon ou choisissez un autre carburant.</p>';return}
 const list=rows.map(s=>{const det=2*s.d*C/100*s.p;return Object.assign({},s,{plein:L*s.p,det:det,tot:L*s.p+det})});
 const avg=list.reduce((a,s)=>a+s.p,0)/list.length,maxp=Math.max(...list.map(s=>s.p));
 const best=list.slice().sort((a,b)=>a.tot-b.tot)[0],cheap=list[0];
 const sav=L*avg-best.tot,savMax=L*maxp-best.tot;
 let h='<p class="fc-live">📍 '+esc(place)+' · '+list.length+' stations · '+NAMES[f]+'</p>';
 h+='<div class="fc-sum"><div><span>Meilleur choix (détour compris)</span><b>'+eur(best.tot)+'</b><span>'+esc(best.adr)+', '+esc(best.ville)+' · '+nb(best.d,1)+' km</span></div>'
  +'<div><span>Prix le plus bas</span><b>'+nb(cheap.p,3)+' €/L</b><span>moyenne du secteur '+nb(avg,3)+' €/L</span></div>'
  +'<div><span>Économie sur '+nb(L,0)+' L</span><b>'+eur(Math.max(0,sav))+'</b><span>vs prix moyen · '+eur(Math.max(0,savMax))+' vs la plus chère</span></div></div>';
 const top=list.slice().sort((a,b)=>a.tot-b.tot).slice(0,15);
 let t='<table class="fc-tb"><thead><tr><th>Station</th><th class="n">Prix</th><th class="n">Distance</th><th class="n">Plein</th><th class="n">Détour</th><th class="n">Total</th></tr></thead><tbody>';
 top.forEach((s,i)=>{t+='<tr'+(i===0?' class="best"':'')+'><td data-l="Station"><span>'+esc(s.adr)+'<small>'+esc(s.cp)+' '+esc(s.ville)+(s.maj?' · maj '+dfmt.format(new Date(s.maj)):'')+'</small></span></td><td class="n" data-l="Prix"><span>'+nb(s.p,3)+' €/L</span></td><td class="n" data-l="Distance"><span>'+nb(s.d,1)+' km</span></td><td class="n" data-l="Plein"><span>'+eur(s.plein)+'</span></td><td class="n" data-l="Détour (A/R)"><span>'+eur(s.det)+'</span></td><td class="n" data-l="Total"><span><b>'+eur(s.tot)+'</b></span></td></tr>'});
 t+='</tbody></table>';
 const ch=list.slice(0,10),lo=Math.floor(Math.min(...ch.map(s=>s.p))*20-1)/20,hi=Math.ceil(Math.max(...ch.map(s=>s.p))*20)/20+0.0001,span=hi-lo;
 let g='<div class="fc-plot">';for(let v=lo;v<=hi;v+=0.05){g+='<div class="fc-gl" style="bottom:'+((v-lo)/span*100).toFixed(2)+'%"><span>'+nb(v,2)+'</span></div>'}
 g+='<div class="fc-bars">'+ch.map((s,i)=>{const hh=Math.max(2,(s.p-lo)/span*100);return '<div class="fc-b"><span style="height:'+hh.toFixed(1)+'%;background:'+(i===0?'#22A06B':'#3B82F6')+'"></span><em style="bottom:calc('+hh.toFixed(1)+'% + 2px)">'+nb(s.p,3)+'</em><small>'+esc(s.ville)+'<br>'+nb(s.d,1)+' km</small></div>'}).join('')+'</div></div>';
 h+='<div class="fc-sw" role="group"><button type="button" data-v="table" aria-pressed="'+(view==='table')+'">Tableau</button><button type="button" data-v="chart" aria-pressed="'+(view==='chart')+'">Graphique (10 moins chères, €/L)</button></div>'
  +'<div'+(view==='table'?'':' hidden')+'>'+t+'</div><div'+(view==='chart'?'':' hidden')+'>'+g+'</div>';
 h+='<p class="fc-src">Prix déclarés par les stations au ministère de l’Économie (flux instantané, mis à jour toutes les 10 minutes environ) · <a href="https://www.prix-carburants.gouv.fr/" rel="nofollow">prix-carburants.gouv.fr</a> · Licence Ouverte. Le détour compte l’aller-retour en ligne droite : la distance réelle par la route est un peu plus longue.</p>';
 $('out').innerHTML=h}
$('out').addEventListener('click',e=>{const b=e.target.closest('.fc-sw button');if(!b)return;view=b.dataset.v;draw()});
$('go').addEventListener('click',()=>{pos=null;run()});
$('q').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();pos=null;run()}});
$('me').addEventListener('click',()=>{if(!navigator.geolocation){$('out').innerHTML='<p class="fc-err">La géolocalisation n’est pas disponible sur cet appareil.</p>';return}
 navigator.geolocation.getCurrentPosition(p=>{pos={lat:p.coords.latitude,lon:p.coords.longitude};place='Ma position';run()},()=>{$('out').innerHTML='<p class="fc-err">Position refusée. Saisissez plutôt une commune ou un code postal.</p>'},{timeout:10000,maximumAge:600000})});
['fuel','rad'].forEach(id=>$(id).addEventListener('change',run));
['lit','cons'].forEach(id=>$(id).addEventListener('input',()=>{if(rows.length)draw()}));
run();
})();
</script>'''

FAQ = [
 ("D’où viennent les prix ?",
  "Les stations-service sont obligées de déclarer leurs prix de vente à l’administration à chaque changement. Le ministère de l’Économie les publie sur prix-carburants.gouv.fr et en données ouvertes (flux instantané). Ce calculateur lit ce flux officiel directement."),
 ("Les prix sont-ils à jour ?",
  "Le flux instantané est actualisé en continu (environ toutes les 10 minutes). Chaque ligne du tableau affiche l’heure de la dernière mise à jour déclarée par la station ; un prix ancien peut ne plus être exact."),
 ("Faut-il faire un détour pour une station moins chère ?",
  "Seulement si l’économie sur le plein dépasse le carburant brûlé pour y aller et revenir. Le calculateur ajoute ce coût de détour (aller-retour × consommation × prix) et classe les stations sur le total."),
 ("Pourquoi certaines stations n’apparaissent pas ?",
  "Une station absente ne déclare pas le carburant choisi, est en rupture, ou se trouve hors du rayon. Essayez un rayon plus grand ou un autre carburant (par exemple SP95-E10 au lieu de SP95)."),
 ("Ma position est-elle enregistrée ?",
  "Non. La position ou l’adresse sert uniquement à interroger les services publics de géocodage et de prix depuis votre navigateur ; Hong Life ne l’enregistre pas."),
]

ART = '''<p><b>En bref :</b> saisissez une commune ou utilisez votre position, choisissez le carburant et le nombre de litres. Le calculateur charge les <b>prix officiels déclarés par les stations</b> autour de vous et classe les stations sur le <b>coût total du plein, détour compris</b>.</p>
<h2 id="how">Comment le calcul est fait</h2>
<ul><li><b>Coût du plein</b> = litres × prix au litre de la station</li>
<li><b>Coût du détour</b> = 2 × distance (km) × consommation (L/100 km) ÷ 100 × prix au litre</li>
<li><b>Total</b> = plein + détour — la station la moins chère « au total » est surlignée</li>
<li><b>Économie</b> = litres × prix moyen du secteur − total de la meilleure station</li></ul>
<h3 id="exemples">Exemples (40 L)</h3>
''' + table(['Situation', 'Calcul', 'Résultat'], [
    ['Station à 1,899 €/L, à 2 km, conso 6,5 L/100 km', '40 × 1,899 + 2 × 2 × 6,5 ÷ 100 × 1,899', '75,96 € + 0,49 € = 76,45 €'],
    ['Station à 1,959 €/L, à 0,5 km', '40 × 1,959 + 2 × 0,5 × 6,5 ÷ 100 × 1,959', '78,36 € + 0,13 € = 78,49 €'],
    ['Écart de 6 centimes par litre', '40 × 0,06', '2,40 € d’économie par plein'],
    ['Même écart, 2 pleins par mois', '2,40 € × 24', '57,60 € par an'],
]) + '''
<h3 id="carburants">Quel carburant choisir ?</h3>
''' + table(['Carburant', 'Pour quels véhicules'], [
    ['Gazole (B7)', 'Moteurs diesel'],
    ['SP95-E10', 'La plupart des voitures essence (vérifiez la compatibilité E10 dans le carnet ou la trappe à carburant)'],
    ['SP95 / SP98', 'Toutes les voitures essence ; le SP98 est plutôt réservé aux moteurs qui le demandent'],
    ['E85 (superéthanol)', 'Véhicules flex-fuel ou équipés d’un boîtier homologué ; consommation plus élevée'],
    ['GPLc', 'Véhicules équipés pour le GPL'],
]) + '''
<h3>Astuces</h3>
<ul><li>Les stations de grandes surfaces et les automates 24/24 affichent souvent les prix les plus bas.</li>
<li>Sur autoroute, les prix sont généralement plus élevés : faites le plein avant de partir.</li>
<li>Un écart de quelques centimes ne vaut pas un long détour : regardez la colonne « Total ».</li></ul>
''' + faq_html(FAQ, heading='Questions fréquentes').replace('<h2 style="margin-top:22px">Questions fréquentes</h2>', '<h2 id="faq" style="margin-top:22px">Questions fréquentes</h2>') + f'''
<p class="note">Sources (consultées le {DATE_FR}) : <a href="https://www.prix-carburants.gouv.fr/" rel="nofollow">prix-carburants.gouv.fr</a> ; <a href="https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/" rel="nofollow">data.economie.gouv.fr – Prix des carburants en France, flux instantané v2</a> (Licence Ouverte) ; géocodage <a href="https://geoservices.ign.fr/" rel="nofollow">Géoplateforme IGN</a>. Voir aussi : <a href="/fr/calcul-cout-carburant.html">Calcul du coût de carburant d’un trajet</a>.</p>'''

TOC = [('form', 'Calculateur'), ('how', 'Comment le calcul est fait'), ('exemples', 'Exemples'), ('carburants', 'Quel carburant'), ('faq', 'Questions fréquentes')]


def main():
    s = open(os.path.join(ORIG, 'fr/calcul-cout-carburant.html'), encoding='utf-8').read()
    old = 'https://honglifecalc.com/fr/calcul-cout-carburant.html'
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + H1, s, count=1)
    s = s.replace(old, URL)
    assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": H1, "url": URL, "description": DESC,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "fr-FR",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": "Tous les calculateurs", "item": "https://honglifecalc.com/fr/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇫🇷 Prix en direct · prix-carburants.gouv.fr</span>'
               f'<h1>{H1}</h1><p>Les stations les moins chères près de chez vous et le vrai coût du plein, détour compris.</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>Par <b>Hong Life Calculateurs</b></span><span>Vérifié le <b>{DATE_FR}</b></span>'
           '<span>Données <b>Ministère de l’Économie (Licence Ouverte)</b></span></div><details class="card hl-toc" open><summary>Sommaire</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'flux-instantane-v2' in s and 'id="fuel"' in s and 'id="exemples"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
