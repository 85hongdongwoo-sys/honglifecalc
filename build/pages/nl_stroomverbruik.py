import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/nl/stroomverbruik-berekenen.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Uw gegevens</h2><label class="f"><span>Vermogen (W)</span><input id="w" inputmode="decimal" value="1.000"><small>Staat op het typeplaatje of in de handleiding. 2 kW = 2.000 W.</small></label><label class="f"><span>Uren per dag</span><input id="h" inputmode="decimal" value="3"><small>10 minuten = 0,17 uur; 30 minuten = 0,5 uur.</small></label><label class="f"><span>Prijs per kWh (€)</span><input id="kp" inputmode="decimal" value="0,30"><small>Een voorbeeldprijs. Vul de kWh-prijs inclusief belastingen en btw uit uw eigen contract in.</small></label><label class="f"><span>Dagen</span><input id="d" inputmode="decimal" value="30"></label></form>'''

calc='''function calc(){const w=num('w'),h=Math.min(24,num('h')),d=num('d'),p=num('kp');
 if(d<=0||w<=0)return big(O.m,'—','Vul een vermogen en een aantal dagen in');
 const kd=w/1000*h,k=kd*d,m=k*p;
 return big(O.m,mf2(m),nn(k,1)+' kWh in '+nn(d,0)+' dagen')+kv([[O.day,mf2(kd*p)+' · '+nn(kd,2)+' kWh'],['Kosten per maand (30 dagen)',mf2(kd*30*p)],[O.y,mf(kd*365*p)],['Verbruik per jaar',nn(kd*365,0)+' kWh']])+'<p class="note">Berekend als vermogen × uren × dagen. Veel apparaten (koelkast, wasmachine) draaien niet steeds op vol vermogen; dan is het echte verbruik lager.</p>'}'''

def row(name,W,h,p=0.30):
    kd=W/1000*h; return [name,f"{W:,} W".replace(',','.'),str(h).replace('.',','),f"{kd*365:,.0f}".replace(',','.')+' kWh','€ '+f"{kd*365*p:,.2f}".replace(',','#').replace('.',',').replace('#','.')]
rows=[row('LED-lamp',8,5),row('Laptop',60,8),row('Televisie',100,4),row('Apparaat op stand-by',5,24),row('Waterkoker',2000,0.17),row('Elektrische kachel',2000,4)]
print(rows)

FAQ=[
("Hoe bereken ik het stroomverbruik van een apparaat?","Vermogen in watt ÷ 1.000 × aantal uren = kWh. Een apparaat van 1.000 W dat 3 uur aanstaat, gebruikt 1 × 3 = 3 kWh. Keer de prijs per kWh geeft de kosten: 3 × € 0,30 = € 0,90."),
("Wat kost een apparaat van 1.000 watt per uur?","Een uur op 1.000 W is precies 1 kWh. Bij € 0,30 per kWh kost dat € 0,30 per uur. Gebruikt u het 3 uur per dag, dan is dat € 27 per maand en € 328,50 per jaar."),
("Wat kost stand-by verbruik per jaar?","Een apparaat dat 5 W gebruikt en altijd aanstaat, verbruikt 5 × 24 × 365 ÷ 1.000 = 43,8 kWh per jaar. Bij € 0,30 per kWh is dat € 13,14. Tien van zulke apparaten kosten samen ruim € 130."),
("Wat is het verschil tussen watt en kWh?","Watt (W) is hoeveel stroom een apparaat op één moment vraagt. Kilowattuur (kWh) is hoeveel stroom het in totaal gebruikt: 1.000 W gedurende 1 uur = 1 kWh. Uw energierekening rekent in kWh."),
("Welke kWh-prijs moet ik invullen?","De prijs per kWh uit uw energiecontract, inclusief alle belastingen. Rekent u met een dynamisch contract, gebruik dan een gemiddelde prijs. De vaste leveringskosten en netbeheerkosten tellen niet mee per apparaat."),
("Kost een elektrische kachel veel stroom?","Ja. Een kachel van 2.000 W die 4 uur per dag brandt, gebruikt 8 kWh per dag. Bij € 0,30 per kWh is dat € 2,40 per dag, € 72 per maand."),
]

art='''<h2 id="vb">Voorbeelden: wat kost een apparaat per jaar?</h2>
<div id="examples">'''+table(['Apparaat','Vermogen (voorbeeld)','Uren per dag','Verbruik per jaar','Kosten per jaar bij € 0,30/kWh'],rows)+'''</div>
<p class="note">Vermogens en uren zijn voorbeelden; kijk op uw eigen apparaat. € 0,30 per kWh is een rekenvoorbeeld, geen officiële prijs. Berekend met de formule van deze rekenhulp.</p>
<ul><li>Een <b>laptop</b> die 8 uur per dag aanstaat, kost ongeveer € 53 per jaar.</li>
<li>Een <b>waterkoker</b> is sterk (2.000 W), maar staat kort aan: zo’n € 37 per jaar bij 10 minuten per dag.</li>
<li>Een <b>elektrische kachel</b> van 2.000 W, 4 uur per dag, kost € 2,40 per dag. Een heel jaar zou € 876 zijn.</li></ul>
<h2 id="uitleg">Zo werkt de berekening</h2>
<p>Voorbeeld: een apparaat van 1.000 W staat 3 uur per dag aan, 30 dagen lang. Dat is 1 kW × 3 uur = 3 kWh per dag, en 90 kWh in 30 dagen. Bij € 0,30 per kWh kost dat <b>€ 27,00</b>.</p>
<ul><li><b>Watt (W)</b> = hoeveel stroom een apparaat op één moment vraagt.</li>
<li><b>Kilowattuur (kWh)</b> = de hoeveelheid stroom die u in totaal gebruikt. 1 kWh = 1.000 W gedurende 1 uur.</li>
<li><b>kWh per dag</b> = vermogen ÷ 1.000 × uren per dag.</li>
<li><b>Kosten</b> = kWh × prijs per kWh.</li></ul>
<h2 id="tips">Tips om stroom te besparen</h2>
<ul><li><b>Zet apparaten echt uit.</b> Stand-by lijkt weinig, maar telt het hele jaar door.</li>
<li><b>Let op apparaten die warmte maken.</b> Kachels, drogers en ovens hebben een groot vermogen. Elk uur korter scheelt direct.</li>
<li><b>Meet het echte verbruik.</b> Een energiemeter in het stopcontact laat zien hoeveel kWh een apparaat echt gebruikt.</li>
<li><b>Dynamisch contract?</b> Gebruik grote apparaten op uren met een lage prijs.</li></ul>
<h2 id="faq" style="margin-top:22px">Veelgestelde vragen</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Gecontroleerd op 25 november 2026. € 0,30 per kWh is een rekenvoorbeeld, geen officiële prijs. Voorbeelden berekend met de formule van deze rekenhulp. Algemene informatie, geen advies.</p>'''

out=build(P,'Stroomverbruik berekenen – wat kost een apparaat per jaar?',
 'Bereken het stroomverbruik in kWh en de kosten per dag, maand en jaar van elk apparaat. Met voorbeelden voor kachel, laptop, tv en stand-by.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Door','Hong Life Calculators'),('Gecontroleerd','25 november 2026'),('Methode','vermogen × uren × prijs')],
 [('form','Rekenhulp'),('vb','Voorbeelden'),('uitleg','Zo werkt het'),('tips','Besparen'),('faq','Veelgestelde vragen')],'Op deze pagina',('#examples','nl'))
print(out)
