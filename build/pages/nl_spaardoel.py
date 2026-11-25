import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/nl/spaardoel-berekenen.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Uw gegevens</h2><label class="f"><span>Spaardoel (€)</span><input id="T" inputmode="decimal" value="18.000"></label><label class="f"><span>Al gespaard (€)</span><input id="C" inputmode="decimal" value="1.800"></label><label class="f"><span>Jaren</span><input id="y" inputmode="decimal" value="3"><small>Halve jaren mag: 18 maanden = 1,5.</small></label><label class="f"><span>Spaarrente (% per jaar)</span><input id="r" inputmode="decimal" value="2"><small>Een voorbeeldrente. Vul de rente van uw eigen spaarrekening in, of 0 voor geen rente.</small></label></form>'''

calc='''function calc(){const T=num('T'),C=num('C'),i=num('r')/1200,n=Math.round(num('y')*12);
 const nt='<p class="note">Aanname: u legt elke maand aan het eind van de maand in, de rente wordt maandelijks bijgeschreven en blijft gelijk. Belasting (box 3) is niet meegerekend.</p>';
 if(n<1)return big(O.need,'—','Vul minstens 1 maand in (0,08 jaar)');
 const g=Math.pow(1+i,n),grow=C*g;
 if(grow>=T)return big('U haalt uw doel al',mf(0,0),O.per)+kv([['Uw spaargeld groeit naar',mf(grow,0)],['Rente',mf(grow-C,0),'pos'],['Maanden',String(n)]])+nt;
 const need=i?(T-grow)*i/(g-1):(T-C)/n,dep=need*n;
 return big(O.need,mf(need),O.per)+kv([['Ongeveer per week',mf(need*12/52)],[O.tot,mf(dep,0)],['Al gespaard',mf(C,0)],[O.int,mf(Math.max(0,T-C-dep),0),'pos'],['Maanden',String(n)]])+nt}'''

def need(T,C,y,r):
    i=r/1200;n=round(y*12);g=(1+i)**n
    if C*g>=T: return 0
    return (T-C*g)*i/(g-1) if i else (T-C)/n
e=lambda x:'€ '+f"{x:,.0f}".replace(',','.')
rows=[]
for T,y,lab in [(5000,1,'€ 5.000 (vakantie, buffer)'),(10000,2,'€ 10.000'),(20000,3,'€ 20.000 (auto)'),(40000,5,'€ 40.000 (eigen geld bij een huis)')]:
    a=[need(T,0,y,r) for r in (0,1.5,2.5)]
    rows.append([lab,f"{y} jaar",e(a[0]),e(a[1]),e(a[2]),e(T-a[2]*y*12)])
d=need(18000,1800,3,2)
print(rows,round(d,2))

FAQ=[
("Hoeveel moet ik per maand sparen voor mijn doel?","Deel het bedrag dat nog ontbreekt door het aantal maanden. Rente maakt het iets minder. Voor € 10.000 in 2 jaar vanaf nul: € 10.000 ÷ 24 = € 417 per maand zonder rente, of € 407 per maand bij 2,5% rente."),
("Hoe lang duurt het om € 10.000 te sparen?","Met € 250 per maand duurt het 40 maanden zonder rente (3 jaar en 4 maanden). Met 2% rente zijn het 39 maanden. Met € 500 per maand bent u in 20 maanden klaar."),
("Hoeveel moet ik sparen voor een huis?","Wilt u € 40.000 eigen geld in 5 jaar, dan is dat € 667 per maand zonder rente, of € 627 per maand bij 2,5% rente. De rente levert dan ruim € 2.400 op."),
("Hoeveel rente krijg ik als ik elke maand spaar?","Dat hangt af van de rente en de tijd. Spaart u 3 jaar lang € 536 per maand bij 2,5% rente, dan levert de rente ongeveer € 720 op en heeft u € 20.000. Hoe langer u spaart, hoe meer rente op rente meetelt."),
("Is het beter om per week of per maand te sparen?","Voor het totaal maakt het weinig uit. € 100 per week is ongeveer € 433 per maand (€ 100 × 52 ÷ 12). De rekenhulp toont naast het maandbedrag ook een bedrag per week."),
("Wat als ik al genoeg gespaard heb?","Als uw huidige spaargeld met rente al boven uw doel uitkomt, toont de rekenhulp € 0 per maand en hoeveel uw geld groeit."),
]

art='''<p class="note">Spaarrentes van banken noemen we niet. Die veranderen vaak en verschillen per bank. Vul de rente van uw eigen rekening in.</p>
<h2 id="vb">Hoeveel per maand sparen? Voorbeelden</h2>
<div id="examples">'''+table(['Doel','Tijd','Per maand zonder rente','Per maand bij 1,5%','Per maand bij 2,5%','Rente bij 2,5%'],rows)+'''</div>
<ul><li>Voor <b>€ 5.000 in 1 jaar</b> spaart u ongeveer € 417 per maand. Met 2,5% rente is het € 412.</li>
<li>Voor <b>€ 20.000 in 3 jaar</b> is het € 556 per maand zonder rente, of € 536 bij 2,5%. De rente levert ongeveer € 720 op.</li>
<li>Voor <b>€ 40.000 in 5 jaar</b> is het € 627 per maand bij 2,5%. De rente levert dan ruim € 2.400 op.</li></ul>
<p class="note">Alle voorbeelden starten bij € 0 en zijn berekend met de formule van deze rekenhulp. 1,5% en 2,5% zijn voorbeeldrentes, geen bankaanbod.</p>
<h2 id="uitleg">Zo werkt de berekening</h2>
<p>Eerst een voorbeeld. U wilt € 18.000 in 3 jaar. U heeft al € 1.800 en krijgt 2% rente per jaar. Die € 1.800 groeit vanzelf naar ongeveer € 1.911. Er ontbreekt dan nog zo’n € 16.089. Spaart u <b>€ 434 per maand</b>, dan haalt u het doel, omdat de rente op uw inleg onderweg ongeveer € 576 toevoegt.</p>
<ul><li><b>Maandrente</b> = jaarrente ÷ 12. 2% per jaar is dus ongeveer 0,17% per maand.</li>
<li><b>Rente op rente</b> betekent dat u ook rente krijgt over eerder bijgeschreven rente. De rekenhulp schrijft elke maand rente bij.</li>
<li><b>Tekort</b> = doel − wat uw huidige spaargeld zelf wordt.</li>
<li><b>Bedrag per maand</b> = tekort × i ÷ ((1 + i)<sup>n</sup> − 1). Hier is i de maandrente en n het aantal maanden.</li></ul>
<p>Zonder rente is het gewoon (doel − al gespaard) ÷ aantal maanden.</p>
<h2 id="tips">Tips en veelgemaakte fouten</h2>
<ul><li><b>Spaar automatisch.</b> Zet een periodieke overboeking op de dag na uw salaris. Dan spaart u eerst en geeft u daarna uit.</li>
<li><b>Kijk naar de echte rente.</b> Een hoge rente geldt soms alleen tot een bepaald bedrag of zonder opnames. Vul de rente in die u echt krijgt.</li>
<li><b>Houd ook een buffer aan.</b> Dan hoeft u bij een onverwachte rekening niet uw spaardoel aan te spreken.</li>
<li><b>Let op belasting.</b> Heeft u veel vermogen, kijk dan op belastingdienst.nl naar de actuele regels voor box 3.</li></ul>
<h2 id="faq" style="margin-top:22px">Veelgestelde vragen over sparen</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Gecontroleerd op 25 november 2026. Voorbeelden met de formule van deze rekenhulp. Algemene informatie, geen financieel advies.</p>'''

out=build(P,'Spaardoel berekenen 2026 – hoeveel per maand sparen?',
 'Bereken hoeveel u per maand of per week moet sparen voor uw spaardoel, met rente. Met voorbeelden per doel, rente op rente en tips.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Door','Hong Life Calculators'),('Gecontroleerd','25 november 2026'),('Methode','formule van deze rekenhulp')],
 [('form','Rekenhulp'),('vb','Voorbeelden'),('uitleg','Zo werkt het'),('tips','Tips'),('faq','Veelgestelde vragen')],'Op deze pagina',('#examples','nl'))
print(out)
