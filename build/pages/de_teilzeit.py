import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
import math
from enrich_lib import build, table, add_top
P='/de/teilzeit-rechner.html'

# Form: same input ids as the original; Steuerklasse V removed (no honest approximation possible here).
form='''<form class="card" id="form" onsubmit="return false"><h2>Ihre Angaben</h2><label class="f"><span>Vollzeit-Brutto pro Monat</span><input id="b" inputmode="decimal" value="4.000"></label><label class="f"><span>Vollzeit-Wochenstunden</span><input id="v" inputmode="decimal" value="40"></label><label class="f"><span>Teilzeit-Wochenstunden</span><input id="t" inputmode="decimal" value="30"></label><label class="f"><span>Steuerklasse</span><select id="kl"><option value="1" selected>I</option><option value="2">II (alleinerziehend, 1 Kind)</option><option value="3">III</option><option value="4">IV</option></select><small>Gerechnet ohne Kirchensteuer, mit dem durchschnittlichen Zusatzbeitrag 2026 (2,9 %). Klasse I, III und IV: kinderlos ab 23 Jahren. Steuerklasse V ist nicht enthalten.</small></label></form>'''

# calc(): uses T (DE2026), TX (DETax), num, $, big, kv, eur2, pc from the page/de.js scope.
calc='''function calc(){const v=num('v'),t=num('t'),kl=$('kl').value,bm=num('b');
 if(bm<=0||v<=0||t<=0)return big('Teilzeit netto pro Monat','—','Bitte Brutto und Wochenstunden eingeben');
 const G=603,OG=2000,F=0.6619;
 const nz=(b)=>{const m=b/12;let fA=1,fG=1;if(m>G&&m<=OG){fA=OG/(OG-G)*(m-G)/m;fG=(F*G+(OG/(OG-G)-G/(OG-G)*F)*(m-G))/m}
  const rvB=Math.min(b,T.bbgRV)*fA,kvB=Math.min(b,T.bbgKV)*fA,kvG=Math.min(b,T.bbgKV)*fG,rv=rvB*T.rv/2,av=rvB*T.av/2,kvAN=kvB*(T.kv/2+T.zusatz/2),pvAN=kvB*T.pv/2+(kl==='2'?0:kvG*T.pvKinderlos);
  const kvpv=kvB*(T.kvErm/2+T.zusatz/2)+pvAN,vsp=rv+Math.max(kvpv,Math.min(1900,kvpv+av));let zve=b-T.wkp-T.sap-vsp;if(kl==='2')zve-=T.alleinerz;
  const lst=kl==='3'?TX.estSplit(Math.max(0,zve)):TX.est(zve),so=TX.soli(lst,kl==='3'),sv=rv+av+kvAN+pvAN;return {n:b-lst-so-sv,lst:lst+so,sv}};
 const q=t/v,bv=bm*12,bt=bv*q,mt=bt/12,V=nz(bv),nv=V.n/12;
 const hv=v*52/12,ht=t*52/12;
 if(mt<=G){const rvAN=mt<175?T.rv*175-.15*mt:mt*.036,n=mt-rvAN;return big('Minijob: netto pro Monat',eur2(n),'Brutto '+eur2(mt)+' · bis 603 € gilt die Minijob-Regel')+kv([['Vollzeit netto',eur2(nv)],['Ihr Rentenbeitrag',eur2(-rvAN),'neg'],['Netto mit Befreiung von der Rentenversicherung',eur2(mt)],['Netto pro Stunde (Vollzeit → Minijob)',eur2(nv/hv)+' → '+eur2(n/ht)]])+'<p class="note">Im Minijob zahlen Sie keine Kranken-, Pflege- und Arbeitslosenversicherung. Rentenversicherung: Ihr Anteil ist 3,6 % (unter 175 € Lohn mehr, wegen des Mindestbeitrags). Sie können sich davon befreien lassen. Die Steuer (2 % pauschal) zahlt meist der Arbeitgeber.</p>'}
 const R=nz(bt),nt=R.n/12;
 return big('Teilzeit netto pro Monat',eur2(nt),'Brutto '+eur2(mt)+(mt<=OG?' · Übergangsbereich (Midijob)':''))+kv([['Lohnsteuer + Soli',eur2(-R.lst/12),'neg'],['Sozialbeiträge',eur2(-R.sv/12),'neg'],['Vollzeit netto',eur2(nv)],['Weniger Brutto',eur2(mt-bm),'neg'],['Weniger Netto',eur2(nt-nv),'neg'],['Anteil vom Vollzeit-Netto',pc(nt/nv,0),'t'],['Anteil der Stunden',pc(q,0)],['Netto pro Stunde (Vollzeit → Teilzeit)',eur2(nv/hv)+' → '+eur2(nt/ht)]])+'<p class="note">Lohnsteuer 2026 nach § 32a EStG, Sozialbeiträge mit den Werten 2026, ohne Kirchensteuer. Zwischen 603,01 € und 2.000 € Brutto im Monat sind Ihre Sozialbeiträge geringer (Übergangsbereich). Das Ergebnis ist eine Schätzung; maßgeblich ist Ihre Lohnabrechnung.</p>'}'''

# ---- Python re-implementation of the same formula (for the examples) ----
RV,AV,KV,KVE,ZUS,PV,PVK=.186,.026,.146,.14,.029,.036,.006
BBGRV,BBGKV,WKP,SAP,AE=101400,69750,1230,36,4260
def est(z):
    z=math.floor(max(0,z))
    if z<=12348: t=0
    elif z<=17799: y=(z-12348)/1e4; t=(914.51*y+1400)*y
    elif z<=69878: y=(z-17799)/1e4; t=(173.10*y+2397)*y+1034.87
    elif z<=277825: t=.42*z-11135.63
    else: t=.45*z-19470.38
    return math.floor(t)
def soli(l,j):
    fg=40700 if j else 20350
    return 0 if l<=fg else min(l*.055,(l-fg)*.119)
def nz(b,kl):
    m=b/12;fA=fG=1
    if 603<m<=2000:
        fA=2000/1397*(m-603)/m; fG=(.6619*603+(2000/1397-603/1397*.6619)*(m-603))/m
    rvB=min(b,BBGRV)*fA;kvB=min(b,BBGKV)*fA;kvG=min(b,BBGKV)*fG
    rv=rvB*RV/2;av=rvB*AV/2;kvAN=kvB*(KV/2+ZUS/2);pvAN=kvB*PV/2+(0 if kl=='2' else kvG*PVK)
    kvpv=kvB*(KVE/2+ZUS/2)+pvAN;vsp=rv+max(kvpv,min(1900,kvpv+av));zve=b-WKP-SAP-vsp
    if kl=='2': zve-=AE
    l=2*est(max(0,zve)/2) if kl=='3' else est(zve)
    return b-l-soli(l,kl=='3')-(rv+av+kvAN+pvAN)
def ex(bm,v,t,kl):
    bt=bm*12*t/v; mt=bt/12
    nv=nz(bm*12,kl)/12
    if mt<=603: nt=mt-(RV*175-.15*mt if mt<175 else mt*.036)
    else: nt=nz(bt,kl)/12
    return mt,nt,nv,nt/nv

e=lambda x:f"{x:,.0f}".replace(',','.')+' €'
e2=lambda x:f"{x:,.2f}".replace(',','X').replace('.',',').replace('X','.')+' €'
pct=lambda x:f"{x*100:.0f} %"
cases=[(4000,40,32,'1','4.000 €, 40 → 32 Std. (Klasse I)'),(4000,40,30,'1','4.000 €, 40 → 30 Std. (Klasse I)'),
       (4000,40,20,'1','4.000 €, 40 → 20 Std. (Klasse I)'),(3000,40,20,'1','3.000 €, 40 → 20 Std. (Klasse I)'),
       (5000,40,30,'3','5.000 €, 40 → 30 Std. (Klasse III)')]
R={}
rows=[]
for b,v,t,kl,lab in cases:
    mt,nt,nv,s=ex(b,v,t,kl); R[(b,v,t,kl)]=(mt,nt,nv,s)
    rows.append([lab,e(mt),e(nt),e(nv),pct(s)])
for r in rows: print(r)
mj=ex(2400,40,10,'1'); print('minijob',mj)
A=R[(4000,40,30,'1')]; B=R[(4000,40,20,'1')]; C=R[(3000,40,20,'1')]; D=R[(4000,40,32,'1')]
hv=A[2]/(40*52/12); ht=A[1]/(30*52/12)
print('hourly',hv,ht)

fig=[['Grundfreibetrag 2026','12.348 € im Jahr','Bis zu diesem zu versteuernden Einkommen zahlen Sie keine Einkommensteuer.'],
     ['Gesetzlicher Mindestlohn 2026','13,90 € pro Stunde','Gilt auch in Teilzeit für jede Stunde. Ab 2027: 14,60 €.'],
     ['Minijob-Grenze 2026','603 € im Monat','Keine Kranken-, Pflege- und Arbeitslosenversicherung. Rentenversicherung: Ihr Anteil 3,6 %, Befreiung auf Antrag möglich.'],
     ['Übergangsbereich (Midijob) 2026','603,01 € bis 2.000 € im Monat','Ihre Sozialbeiträge sind geringer als normal und steigen bis 2.000 € langsam auf den vollen Satz.'],
     ['Rentenversicherung / Arbeitslosenversicherung','18,6 % / 2,6 %','Sie zahlen die Hälfte: 9,3 % und 1,3 %.'],
     ['Krankenversicherung','14,6 % + Zusatzbeitrag (Durchschnitt 2026: 2,9 %)','Sie zahlen die Hälfte: 7,3 % + 1,45 %. Ihre Kasse kann einen anderen Zusatzbeitrag haben.'],
     ['Pflegeversicherung','3,6 % (kinderlos ab 23: + 0,6 %)','Ihr Anteil: 1,8 %, kinderlos 2,4 %. Ab dem 2. Kind unter 25 wird es weniger. In Sachsen ist Ihr Anteil 0,5 Punkte höher.'],
     ['Beitragsbemessungsgrenzen 2026','Rente/Arbeitslosigkeit 8.450 € · Kranken/Pflege 5.812,50 € im Monat','Über diesen Beträgen steigen die Beiträge nicht weiter.']]

law=[['Recht auf Teilzeit (§ 8 TzBfG)','Sie sind länger als 6 Monate im Betrieb, und der Arbeitgeber hat in der Regel mehr als 15 Beschäftigte (ohne Azubis).'],
     ['Antrag','Spätestens 3 Monate vor dem gewünschten Beginn, in Textform (zum Beispiel E-Mail). Nennen Sie auch, wie die Stunden verteilt sein sollen.'],
     ['Ablehnung','Nur aus betrieblichen Gründen, zum Beispiel wenn Ablauf, Organisation oder Sicherheit stark gestört würden oder es zu teuer wäre.'],
     ['Brückenteilzeit (§ 9a TzBfG)','Teilzeit für 1 bis 5 Jahre, danach zurück zur alten Stundenzahl. Gilt, wenn der Arbeitgeber mehr als 45 Beschäftigte hat.'],
     ['Gleiche Bezahlung (§ 4 TzBfG)','Sie bekommen mindestens den Lohn, der Ihrem Anteil an der Vollzeit entspricht.'],
     ['Urlaub (§ 3 BUrlG)','Mindestens 24 Werktage im Jahr. Werktage sind alle Tage außer Sonn- und Feiertagen, also 6 pro Woche – das sind 4 Wochen.']]

FAQ=[
("Wie viel netto bleibt bei 30 statt 40 Stunden?",f"Bei 4.000 € Vollzeit-Brutto in Steuerklasse I sinkt das Brutto um 25 % auf 3.000 €. Netto bleiben rund {e(A[1])} statt {e(A[2])}. Das sind etwa {pct(A[3])} des Vollzeit-Nettos."),
("Warum sinkt das Netto weniger stark als das Brutto?",f"Weil die Lohnsteuer mit dem Einkommen steigt. Wer weniger verdient, zahlt einen kleineren Teil Steuer. Bei 20 statt 40 Stunden (4.000 € Vollzeit) bleiben deshalb rund {pct(B[3])} vom Netto, obwohl es nur 50 % vom Brutto sind."),
("Was ist der Übergangsbereich (Midijob)?",f"Verdienen Sie zwischen 603,01 € und 2.000 € im Monat, zahlen Sie weniger Sozialbeiträge als normal. Ihre Rente wird trotzdem nach dem vollen Lohn berechnet. Beispiel: 1.500 € Brutto ergeben in Klasse I rund {e(C[1])} netto."),
("Was bleibt bei einem Minijob netto?",f"Bis 603 € im Monat zahlen Sie keine Kranken-, Pflege- und Arbeitslosenversicherung. Nur 3,6 % gehen an die Rentenversicherung – davon können Sie sich befreien lassen. Bei 600 € bleiben so {e2(600*(1-.036))}, mit Befreiung 600 €."),
("Habe ich ein Recht auf Teilzeit?","Ja, wenn Sie länger als 6 Monate im Betrieb sind und der Arbeitgeber in der Regel mehr als 15 Beschäftigte hat. Stellen Sie den Antrag spätestens 3 Monate vor dem Beginn in Textform. Der Arbeitgeber darf nur aus betrieblichen Gründen ablehnen."),
("Kann ich später wieder Vollzeit arbeiten?","Mit der Brückenteilzeit ja: Sie vereinbaren 1 bis 5 Jahre Teilzeit und kehren danach zur alten Stundenzahl zurück. Das gilt bei Arbeitgebern mit mehr als 45 Beschäftigten."),
("Wie viel Urlaub habe ich in Teilzeit?","Das Gesetz gibt mindestens 24 Werktage. Bei 6 Werktagen pro Woche sind das 4 Wochen. In Teilzeit werden die Tage meist auf Ihre Arbeitstage umgerechnet, damit Sie auch 4 Wochen frei haben: bei 3 Arbeitstagen pro Woche 24 × 3 ÷ 6 = 12 Tage. Ihr Vertrag kann mehr geben."),
("Steigt mein Netto pro Stunde in Teilzeit?",f"Meist ja. Bei 4.000 € Vollzeit (40 Std.) und Teilzeit mit 30 Std. steigt das Netto pro Stunde von etwa {e2(hv)} auf {e2(ht)}, weil weniger Steuer anfällt."),
]

art='''<h2 id="vb">Beispiele: Netto in Teilzeit 2026</h2>
<div id="examples">'''+table(['Fall','Brutto Teilzeit','Netto Teilzeit','Netto Vollzeit','Anteil vom Vollzeit-Netto'],rows)+f'''</div>
<p class="note">Pro Monat, kinderlos ab 23, ohne Kirchensteuer, durchschnittlicher Zusatzbeitrag 2,9 %. Berechnet mit der Formel dieses Rechners.</p>
<ul><li><b>32 statt 40 Stunden</b> (zum Beispiel 4-Tage-Woche): 20 % weniger Brutto, aber nur etwa {100-round(D[3]*100)} % weniger Netto.</li>
<li><b>20 statt 40 Stunden</b>: die Hälfte vom Brutto, aber rund {pct(B[3])} vom Netto.</li>
<li><b>3.000 € Vollzeit, 20 Stunden</b>: 1.500 € Brutto liegen im Übergangsbereich. Netto bleiben rund {e(C[1])}.</li></ul>
<h2 id="werte">Wichtige Werte 2026</h2>
'''+table(['Wert','Höhe','Was bedeutet das?'],fig)+f'''
<h2 id="rechnung">So rechnet der Rechner</h2>
<p>Ein Beispiel zuerst: Sie verdienen 4.000 € brutto bei 40 Stunden und wollen 30 Stunden arbeiten. Dann bekommen Sie 30 ÷ 40 = 75 % vom Brutto, also 3.000 €. Davon gehen Lohnsteuer und Sozialbeiträge ab. Netto bleiben rund <b>{e(A[1])}</b> statt {e(A[2])}.</p>
<ul><li><b>Teilzeit-Brutto</b> = Vollzeit-Brutto × Teilzeit-Stunden ÷ Vollzeit-Stunden.</li>
<li><b>Sozialbeiträge</b> = Ihr Anteil an Renten-, Arbeitslosen-, Kranken- und Pflegeversicherung, höchstens bis zur Beitragsbemessungsgrenze.</li>
<li><b>Lohnsteuer</b> = Steuer auf Ihren Lohn nach dem Tarif 2026. Vorher zieht der Rechner Pauschalen (1.230 € für Werbungskosten und eine kleine Pauschale für Sonderausgaben) und einen Teil der Sozialbeiträge ab.</li>
<li><b>Progression</b> = je mehr Sie verdienen, desto höher ist der Steuersatz. Deshalb verlieren Sie in Teilzeit weniger Netto als Brutto.</li>
<li><b>Übergangsbereich</b> = zwischen 603,01 € und 2.000 € rechnet der Rechner Ihre Beiträge nach der Formel der Rentenversicherung: 2.000 ÷ 1.397 × (Lohn − 603).</li></ul>
<h2 id="recht">Ihre Rechte bei Teilzeit</h2>
'''+table(['Regel','Was gilt'],law)+'''
<h2 id="tips">Tipps</h2>
<ul><li><b>Steuerklasse prüfen.</b> Verheiratete können die Steuerklassen wechseln. Das ändert das Netto im Monat, nicht die Steuer im ganzen Jahr.</li>
<li><b>An die Rente denken.</b> Weniger Brutto bedeutet weniger Rente später.</li>
<li><b>Mindestlohn prüfen.</b> Teilen Sie Ihr Teilzeit-Brutto durch Ihre Stunden im Monat. Es müssen 2026 mindestens 13,90 € pro Stunde sein.</li>
<li><b>Antrag früh stellen.</b> Mindestens 3 Monate vorher, schriftlich per E-Mail oder Brief, mit Wunsch-Stunden und Verteilung.</li>
<li><b>Grenzen beachten.</b> Knapp über 603 € oder 2.000 € ändern sich die Sozialbeiträge. Rechnen Sie beide Varianten durch.</li></ul>
<h2 id="faq" style="margin-top:22px">Häufige Fragen</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Quellen (geprüft am 28. November 2026): <a href="https://www.gesetze-im-internet.de/estg/__32a.html" rel="nofollow">§ 32a EStG</a>; <a href="https://www.gesetze-im-internet.de/estg/__39b.html" rel="nofollow">§ 39b EStG</a>; <a href="https://www.gesetze-im-internet.de/estg/__9a.html" rel="nofollow">§ 9a EStG</a>; <a href="https://www.gesetze-im-internet.de/estg/__24b.html" rel="nofollow">§ 24b EStG</a>; <a href="https://www.gesetze-im-internet.de/solzg_1995/BJNR097500993.html" rel="nofollow">SolzG</a>; <a href="https://www.gesetze-im-internet.de/tzbfg/BJNR196610000.html" rel="nofollow">Teilzeit- und Befristungsgesetz</a>; <a href="https://www.gesetze-im-internet.de/burlg/BJNR000020963.html" rel="nofollow">Bundesurlaubsgesetz</a>; <a href="https://www.bundesregierung.de/breg-de/aktuelles/beitragsbemessungsgrenzen-2386514" rel="nofollow">Bundesregierung – Rechengrößen 2026</a>; <a href="https://www.bundesregierung.de/breg-de/aktuelles/mindestlohn-steigt-2391010" rel="nofollow">Bundesregierung – Mindestlohn</a>; <a href="https://www.bundesgesundheitsministerium.de/beitraege.html" rel="nofollow">BMG – Beiträge</a>; <a href="https://www.bundesgesundheitsministerium.de/themen/pflege/online-ratgeber-pflege/die-pflegeversicherung/finanzierung" rel="nofollow">BMG – Pflegeversicherung</a>; <a href="https://www.deutsche-rentenversicherung.de/DRV/DE/Experten/Zahlen-und-Fakten/Werte-der-Rentenversicherung/werte-der-rentenversicherung_node.html" rel="nofollow">DRV – Werte</a>; <a href="https://www.deutsche-rentenversicherung.de/DRV/DE/Experten/Arbeitgeber-und-Steuerberater/summa-summarum/Lexikon/U/uebergangsbereich" rel="nofollow">DRV – Übergangsbereich</a>; <a href="https://www.minijob-zentrale.de/DE/die-minijobs/versicherungen/versicherungen_node.html" rel="nofollow">Minijob-Zentrale</a>. Beispiele mit der Formel dieses Rechners. Keine Steuer- oder Rechtsberatung.</p>'''

out=build(P,'Teilzeit-Rechner 2026 – Netto bei weniger Stunden berechnen',
 'Teilzeit-Rechner 2026: Brutto und Netto bei weniger Wochenstunden, mit Steuerklasse, Minijob und Midijob, Beispielen und Ihren Rechten nach dem TzBfG.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Von','Hong Life Calculators'),('Geprüft','28. November 2026'),('Quellen','EStG, TzBfG, BUrlG, Bundesregierung, BMG, DRV, Minijob-Zentrale')],
 [('form','Rechner'),('vb','Beispiele'),('werte','Werte 2026'),('rechnung','So wird gerechnet'),('recht','Ihre Rechte'),('tips','Tipps'),('faq','Häufige Fragen')],'Auf dieser Seite',('#examples','de'))
print(out)
