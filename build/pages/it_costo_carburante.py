import sys, math; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/it/calcolo-costo-carburante.html'
CHK='25 novembre 2026'
# Latest MIMIT national average self-service prices (€/l) and their date; leave None unless verified today.
MIMIT=None   # e.g. {'data':'24 novembre 2026','benzina':1.951,'gasolio':2.204}

form='''<form class="card" id="form" onsubmit="return false"><h2>I tuoi dati</h2><label class="f"><span>Distanza (km)</span><input id="dist" inputmode="decimal" value="500"><small>Solo andata. Scegli sotto se fai anche il ritorno.</small></label><label class="f"><span>Viaggio</span><select id="rt"><option value="1">Solo andata</option><option value="2">Andata e ritorno</option></select></label><label class="f"><span>Consumo (L/100 km)</span><input id="cons" inputmode="decimal" value="6,5"><small>Se conosci i km con un litro: 100 ÷ km/l. Esempio: 16 km/l = 6,25 L/100 km.</small></label><label class="f"><span>Prezzo al litro (€)</span><input id="fp" inputmode="decimal" value="1,95"><small>Un prezzo di esempio: usa quello del distributore dove fai il pieno.</small></label><label class="f"><span>Persone che dividono</span><input id="ppl" inputmode="decimal" value="2"></label></form>'''

calc='''function calc(){const k=num('dist')*(Number(($('rt')||{}).value)||1),l=num('cons'),p=num('fp'),n=Math.max(1,Math.round(num('ppl')));
 if(k<=0||l<=0)return big(O.cost,'–','Inserisci distanza e consumo');
 const v=k*l/100,c=v*p;
 return big(O.cost,mf2(c),O.pp+' ('+n+'): '+mf2(c/n))+kv([['Chilometri totali',nn(k,0)+' km'],[O.vol,nn(v,1)+' '+O.lit],['Costo ogni 100 km',mf2(l*p)],['Costo al km',mf(l*p/100,3)],['Km con un litro',nn(100/l,1)+' km']])+'<p class="note">Solo carburante: pedaggi, parcheggio e usura dell\\'auto non sono inclusi.</p>'}'''

def cost(km,cons,price): v=km*cons/100; return v, v*price
eur=lambda x:(f"{x:,.2f} €").replace(',','X').replace('.',',').replace('X','.')
rows=[]
for lab,km,cons,pr in [('Milano → Roma (solo andata)',575,6.5,1.95),('Milano → Roma, andata e ritorno',1150,6.5,1.95),('Pendolare 40 km al giorno × 20 giorni',800,5.5,1.95),('Auto diesel, Bologna → Napoli',570,5.0,2.20)]:
    v,c=cost(km,cons,pr); rows.append([lab,f"{km:,}".replace(',','.')+' km',f"{cons:.1f}".replace('.',',')+' L/100 km',eur(pr),f"{v:.1f}".replace('.',',')+' l',eur(c)])
print(rows)

fig=[]
if MIMIT:
    fig+= [['Prezzo medio nazionale self – benzina',eur(MIMIT['benzina'])+' al litro','Media MIMIT del '+MIMIT['data']+'.'],
           ['Prezzo medio nazionale self – gasolio',eur(MIMIT['gasolio'])+' al litro','Media MIMIT del '+MIMIT['data']+'.']]

FAQ=[
("Come si calcola il costo del carburante di un viaggio?","Litri = km × consumo ÷ 100. Costo = litri × prezzo al litro. Esempio: 575 km a 6,5 L/100 km servono 37,4 litri; a 1,95 €/l spendi circa 72,88 €."),
("Quanto costa andare da Milano a Roma in auto?","Solo di carburante, circa 73 € all'andata con un'auto che consuma 6,5 L/100 km e benzina a 1,95 €/l (575 km). Andata e ritorno circa 146 €. I pedaggi autostradali sono a parte."),
("Come passo da km/l a L/100 km?","Fai 100 diviso i km con un litro. 20 km/l = 5 L/100 km; 15 km/l = 6,7 L/100 km; 12 km/l = 8,3 L/100 km."),
("Quanto spendo al mese per andare al lavoro?","Con 40 km al giorno per 20 giorni fai 800 km. A 5,5 L/100 km servono 44 litri: a 1,95 €/l sono 85,80 € al mese."),
("Come divido le spese di benzina tra amici?","Calcola il costo totale e dividilo per il numero di persone. 145,76 € per andata e ritorno Milano–Roma in 3 persone fanno 48,59 € a testa."),
("Che prezzo al litro devo inserire?","Quello che paghi al distributore dove fai il pieno. Gli esempi in questa pagina usano 1,95 €/l per la benzina e 2,20 €/l per il gasolio, ma sono solo esempi arrotondati, non prezzi ufficiali."),
]

art='''<h2 id="figures">Quale prezzo usare</h2>
<p>I prezzi della benzina e del gasolio cambiano spesso e sono diversi da un distributore all'altro. Nel calcolatore usa il prezzo che paghi davvero alla pompa.</p>
<h2 id="ex">Esempi di costo del viaggio</h2>
<div id="examples">'''+table(['Viaggio','Distanza','Consumo','Prezzo al litro','Litri','Costo'],rows)+'''</div>
<ul><li><b>Milano → Roma:</b> 575 km a 6,5 L/100 km sono 37,4 litri. A 1,95 €/l spendi <b>72,88 €</b> solo andata.</li>
<li><b>Andata e ritorno:</b> il doppio, <b>145,76 €</b>. In 3 persone sono 48,59 € a testa.</li>
<li><b>Pendolare:</b> 800 km al mese a 5,5 L/100 km costano <b>85,80 €</b>.</li>
<li><b>Diesel:</b> 570 km a 5 L/100 km con gasolio a 2,20 €/l costano <b>62,70 €</b>.</li></ul>
<p class="note">I prezzi negli esempi (1,95 €/l benzina, 2,20 €/l gasolio) sono esempi arrotondati, non prezzi ufficiali. Gli esempi usano la formula di questo calcolatore.</p>
<h2 id="how">Come funziona il calcolo</h2>
<p>Prima un esempio. Vai da Milano a Roma: 575 km. La tua auto consuma 6,5 litri ogni 100 km. Ti servono 575 × 6,5 ÷ 100 = <b>37,4 litri</b>. Con la benzina a 1,95 € al litro spendi 37,4 × 1,95 = <b>72,88 €</b>.</p>
<ul><li><b>Consumo (L/100 km)</b>: quanti litri usa l'auto per fare 100 km. Più è basso, meglio è.</li>
<li><b>Litri necessari</b> = chilometri × consumo ÷ 100.</li>
<li><b>Costo</b> = litri × prezzo al litro.</li>
<li><b>Costo ogni 100 km</b> = consumo × prezzo. A 6,5 L/100 km e 1,95 €/l sono circa 12,7 €.</li></ul>
<h2 id="tips">Consigli per spendere meno</h2>
<ul><li><b>Confronta i distributori.</b> Il prezzo cambia da un impianto all'altro. Il self costa di solito meno del servito.</li>
<li><b>Usa il consumo reale.</b> Il dato del libretto è spesso più basso. In autostrada a 130 km/h l'auto consuma di più.</li>
<li><b>Gomme gonfie e guida fluida.</b> Pressione corretta e meno frenate fanno risparmiare carburante.</li>
<li><b>Non dimenticare i pedaggi.</b> Questo calcolatore conta solo il carburante.</li></ul>
<h2 id="faq" style="margin-top:22px">Domande frequenti</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Gli esempi usano la formula di questo calcolatore e prezzi di esempio, non prezzi ufficiali. Informazioni generali.</p>'''

out=build(P,'Calcolo costo carburante 2026 – quanto costa il viaggio in auto',
 'Calcola quanto spendi di benzina o gasolio per un viaggio: litri, costo andata e ritorno e quota a persona. Esempi come Milano–Roma e il pendolarismo.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Di','Hong Life Calculators'),('Aggiornato il',CHK),('Calcolo','formula del calcolatore')],
 [('form','Calcolatore'),('figures','Quale prezzo usare'),('ex','Esempi'),('how','Come funziona'),('tips','Consigli'),('faq','Domande frequenti')],'In questa pagina',('#examples','it'))
print(out)
