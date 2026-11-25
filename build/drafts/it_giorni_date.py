import sys; sys.path.insert(0,'/home/claude/honglifecalc/build'); sys.path.insert(0,'/tmp/claude-0/-home-claude/22ae3873-7b3e-5235-a76f-08bef551a9af/scratchpad')
from enrich_lib import build, table, add_top
from it_hol import count, easter
P='/it/calcolo-giorni-tra-date.html'
CHK='25 novembre 2026'

form='''<form class="card" id="form" onsubmit="return false"><h2>I tuoi dati</h2><div class="two"><label class="f"><span>Data di inizio</span><input id="d1" type="date" value="2026-11-25"></label><label class="f"><span>Data di fine</span><input id="d2" type="date" value="2026-12-25"></label></div><label class="f"><span>Giorno finale</span><select id="fine"><option value="0">Escluso (come la differenza tra le date)</option><option value="1">Incluso (conta anche l’ultimo giorno)</option></select></label><label class="f"><span>Festività nei giorni lavorativi</span><select id="fe"><option value="1">Escludi le festività nazionali</option><option value="0">Non escluderle</option></select><small>Feste nazionali italiane, compreso il 4 ottobre dal 2026. Il santo patrono locale non è escluso.</small></label></form>'''

calc='''function calc(){const a=new Date($('d1').value),b=new Date($('d2').value);if(isNaN(a)||isNaN(b))return big(O.d,'—','Inserisci due date');
 const inc=$('fine')&&$('fine').value==='1',exf=!$('fe')||$('fe').value==='1';
 const eas=y=>{const A=y%19,B=Math.floor(y/100),C=y%100,D=Math.floor(B/4),E=B%4,F=Math.floor((B+8)/25),G=Math.floor((B-F+1)/3),H=(19*A+B-D-G+15)%30,I=Math.floor(C/4),K=C%4,L=(32+2*E+2*I-H-K)%7,M=Math.floor((A+11*H+22*L)/451),mo=Math.floor((H+L-7*M+114)/31),da=(H+L-7*M+114)%31+1;return Date.UTC(y,mo-1,da)};
 const HC={},hol=y=>{if(HC[y])return HC[y];const s=new Set(['1-1','1-6','4-25','5-1','6-2','8-15','11-1','12-8','12-25','12-26']);if(y>=2026)s.add('10-4');const p=new Date(eas(y)+864e5);s.add((p.getUTCMonth()+1)+'-'+p.getUTCDate());return HC[y]=s};
 let d=Math.round((b-a)/864e5);const s=d>=0?a:b,n=Math.abs(d)+(inc?1:0);let wd=0,fh=0;
 for(let k=0;k<n;k++){const x=new Date(s.getTime()+k*864e5),w=x.getUTCDay();if(WD.includes(w)){wd++;if(hol(x.getUTCFullYear()).has((x.getUTCMonth()+1)+'-'+x.getUTCDate()))fh++}}
 if(inc)d=d>=0?d+1:d-1;const ad=Math.abs(d);
 const rows=[[O.wd+(exf?' senza festività':''),nn(exf?wd-fh:wd,0)]];if(exf)rows.push(['Festività nazionali in giorni feriali',nn(fh,0)]);
 rows.push(['Weekend e altri giorni',nn(n-wd,0)],[O.m,nn(d/30.4375,1)],[O.y,nn(d/365.25,2)]);
 return big(O.d,nn(d,0),(d<0?'la data di fine viene prima · ':'')+nn(Math.trunc(ad/7),0)+' '+(Math.trunc(ad/7)===1?'settimana':O.w)+' e '+nn(ad%7,0)+' '+(ad%7===1?'giorno':O.dd))+kv(rows)+'<p class="note">'+(inc?'Il primo e l’ultimo giorno sono entrambi contati.':'Il giorno di inizio è contato, quello di fine no.')+' Giorni lavorativi = da lunedì a venerdì.</p>'}'''

def it(n): return f"{n:,}".replace(',','.')
ex=[]
for a,b,i,lab in [('2026-11-25','2026-12-25',False,'Dal 25 novembre a Natale'),('2026-11-06','2026-12-25',False,'Dal 6 novembre a Natale'),('2026-12-01','2026-12-31',True,'Dicembre 2026, tutti i giorni'),('2026-01-01','2026-12-31',True,'Tutto il 2026'),('2026-11-25','2027-06-01',False,'Dal 25/11/2026 al 1/6/2027')]:
    d,wd,wdh=count(a,b,i)
    ex.append([lab,'incluso' if i else 'escluso',it(d),it(wd),it(wdh)])
print(ex)

fest=[['1 gennaio','Capodanno','giovedì'],['6 gennaio','Epifania','martedì'],['6 aprile','Lunedì dell’Angelo (Pasquetta)','lunedì'],['25 aprile','Festa della Liberazione','sabato'],['1 maggio','Festa del Lavoro','venerdì'],['2 giugno','Festa della Repubblica','martedì'],['15 agosto','Assunzione (Ferragosto)','sabato'],['4 ottobre','San Francesco d’Assisi (dal 2026)','domenica'],['1 novembre','Ognissanti','domenica'],['8 dicembre','Immacolata Concezione','martedì'],['25 dicembre','Natale','venerdì'],['26 dicembre','Santo Stefano','sabato']]
import datetime as D
wk=['lunedì','martedì','mercoledì','giovedì','venerdì','sabato','domenica']
for r in fest:
    g,m={'gennaio':1,'aprile':4,'maggio':5,'giugno':6,'agosto':8,'ottobre':10,'novembre':11,'dicembre':12}[r[0].split()[1]],0
    dd=D.date(2026,g,int(r[0].split()[0])); assert wk[dd.weekday()]==r[2], (r,wk[dd.weekday()])
assert easter(2026)==D.date(2026,4,5)

FAQ=[
("Quanti giorni mancano a Natale?","Dal 25 novembre al 25 dicembre 2026 ci sono 30 giorni. Di questi, 22 sono giorni da lunedì a venerdì e 21 sono lavorativi, perché l’8 dicembre (Immacolata) cade di martedì."),
("Quanti giorni lavorativi ci sono nel 2026?","Nel 2026 ci sono 261 giorni da lunedì a venerdì. Togliendo le 7 festività nazionali che cadono in un giorno feriale, restano 254 giorni lavorativi. Le ferie e il santo patrono vanno tolti a parte."),
("Il giorno finale va contato?","Dipende da cosa ti serve. Per la differenza tra due date (età, scadenze, “tra quanti giorni”) di solito non si conta. Per la durata di un periodo in cui contano tutti i giorni, come un soggiorno o un contratto dal 1 al 31 del mese, si conta. Scegli l’opzione nel calcolatore."),
("Il 4 ottobre è festivo?","Sì, dal 2026 il 4 ottobre, festa di San Francesco d’Assisi, è di nuovo festività nazionale. Nel 2026 cade di domenica; nel 2027 cade di lunedì, quindi toglie un giorno lavorativo."),
("Come si contano i giorni tra due date?","Si sottrae la data di inizio da quella di fine. Dal 6 novembre al 25 dicembre ci sono 24 giorni rimasti di novembre più 25 di dicembre: 49 giorni. Il calcolatore lo fa per te e tiene conto degli anni bisestili."),
("Quante settimane sono 100 giorni?","100 giorni sono 14 settimane e 2 giorni. Per passare dai giorni alle settimane dividi per 7: il quoziente sono le settimane, il resto sono i giorni."),
]

art='''<h2 id="figures">Festività nazionali 2026 (usate per i giorni lavorativi)</h2>
'''+table(['Data','Festività','Giorno della settimana 2026'],fest)+'''
<p class="note">Nel 2026 sette festività cadono da lunedì a venerdì. La Pasqua 2026 è domenica 5 aprile, quindi Pasquetta è lunedì 6 aprile. Il santo patrono della tua città non è compreso.</p>
<h2 id="ex">Esempi di calcolo</h2>
<div id="examples">'''+table(['Periodo','Giorno finale','Giorni','Lun–ven','Lavorativi (senza feste)'],ex)+'''</div>
<ul><li><b>Tutto il 2026</b> ha 365 giorni, 261 da lunedì a venerdì e 254 lavorativi.</li>
<li><b>Dicembre 2026</b> ha 23 giorni feriali, ma 2 sono festivi (8 e 25 dicembre). Restano 21 giorni lavorativi.</li>
<li>Tutti gli esempi sono calcolati con la stessa formula del calcolatore.</li></ul>
<h2 id="how">Come funziona il calcolo</h2>
<p>Prima un esempio. Dal 25 al 30 novembre sono 6 giorni, contando anche il 25. Dal 1 al 24 dicembre sono altri 24 giorni. Totale: <b>30 giorni</b>. Il 25 dicembre, giorno finale, non è contato.</p>
<ul><li><b>Giorni</b> = data di fine − data di inizio. Gli anni bisestili, con il 29 febbraio, sono già considerati.</li>
<li><b>Giorni lavorativi</b> = i giorni da lunedì a venerdì nel periodo. Se scegli di escludere le feste, il calcolatore toglie le festività nazionali che cadono in quei giorni.</li>
<li><b>Pasquetta</b> cambia ogni anno, perché dipende dalla data della Pasqua. Il calcolatore la calcola da solo.</li>
<li><b>Mesi e anni</b> sono approssimati: un mese medio vale 30,44 giorni e un anno 365,25 giorni.</li></ul>
<h2 id="tips">Consigli</h2>
<ul><li><b>Scadenze:</b> controlla sempre se il primo o l’ultimo giorno va contato. In caso di dubbio chiedi a chi ha fissato la scadenza.</li>
<li><b>Ferie:</b> per sapere quanti giorni di ferie servono, conta solo i giorni lavorativi del periodo.</li>
<li><b>Santo patrono:</b> se nella tua città è festa, togli un giorno a mano.</li></ul>
<h2 id="faq" style="margin-top:22px">Domande frequenti</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+f'''
<p class="note">Fonti (verificate il {CHK}): <a href="https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1949-05-27;260" rel="nofollow">Legge 27 maggio 1949, n. 260 – festività nazionali</a>; <a href="https://www.normattiva.it/eli/id/2025/10/10/25G00153/CONSOLIDATED/" rel="nofollow">Legge n. 151/2025 – festa nazionale di San Francesco d’Assisi (4 ottobre)</a>. Esempi calcolati con la formula di questo calcolatore.</p>'''

out=build(P,'Calcolo giorni tra due date 2026 – giorni lavorativi e festività',
 'Quanti giorni ci sono tra due date? Giorni, settimane e giorni lavorativi senza le festività nazionali 2026 (anche il 4 ottobre). Esempi e FAQ.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('A cura di','Hong Life Calculators'),('Verificato il','25 novembre 2026'),('Fonti','Normattiva')],
 [('form','Calcolatore'),('figures','Festività 2026'),('ex','Esempi'),('how','Come funziona'),('tips','Consigli'),('faq','FAQ')],'In questa pagina',('#examples','it'))
print(out)
