import sys; sys.path.insert(0,'/home/claude/honglifecalc/build'); sys.path.insert(0,'/tmp/claude-0/-home-claude/22ae3873-7b3e-5235-a76f-08bef551a9af/scratchpad/f3')
from enrich_lib import build, table, add_top
from tz import ex
P='/de/teilzeit-rechner.html'

form='''<form class="card" id="form" onsubmit="return false"><h2>Ihre Angaben</h2><label class="f"><span>Vollzeit-Brutto pro Monat</span><input id="b" inputmode="decimal" value="4.000"></label><label class="f"><span>Vollzeit-Wochenstunden</span><input id="v" inputmode="decimal" value="40"></label><label class="f"><span>Teilzeit-Wochenstunden</span><input id="t" inputmode="decimal" value="30"></label><label class="f"><span>Steuerklasse</span><select id="kl"><option value="1" selected>I</option><option value="2">II (alleinerziehend)</option><option value="3">III</option><option value="4">IV</option></select><small>Gerechnet ohne Kinder, ohne Kirchensteuer, mit durchschnittlichem Zusatzbeitrag. Steuerklasse V ist nicht enthalten.</small></label></form>'''

calc='''function calc(){const v=num('v'),t=num('t'),kl=$('kl').value;
 if(v<=0||t<=0)return big('Teilzeit netto pro Monat','—','Bitte Wochenstunden eingeben');
 const G=603,OG=2000;
 const nz=(b)=>{const m=b/12;let f=1;if(m>G&&m<=OG)f=OG/(OG-G)*(m-G)/m;
  const rvB=Math.min(b,T.bbgRV)*f,kvB=Math.min(b,T.bbgKV)*f,rv=rvB*T.rv/2,av=rvB*T.av/2,kvAN=kvB*(T.kv/2+T.zusatz/2),pvAN=kvB*T.pv/2+kvB*T.pvKinderlos;
  const kvpv=kvB*(T.kvErm/2+T.zusatz/2)+pvAN,vsp=rv+Math.max(kvpv,Math.min(1900,kvpv+av));let zve=b-T.wkp-T.sap-vsp;if(kl==='2')zve-=T.alleinerz;
  const lst=kl==='3'?TX.estSplit(Math.max(0,zve)):TX.est(zve),so=TX.soli(lst,kl==='3');return b-lst-so-(rv+av+kvAN+pvAN)};
 const q=t/v,bv=num('b')*12,bt=bv*q,mt=bt/12,nv=nz(bv)/12;
 const hv=v*52/12,ht=t*52/12;
 if(mt<=G){const n=mt*(1-.036);return big('Minijob: netto pro Monat',eur2(n),'Brutto '+eur2(mt)+' · bis 603 € gilt die Minijob-Regel')+kv([['Vollzeit netto',eur2(nv)],['Eigenanteil Rentenversicherung (3,6 %)',eur2(-mt*.036),'neg'],['Ohne Rentenversicherung (Befreiung)',eur2(mt)]])+'<p class="note">Im Minijob zahlen Sie keine Kranken-, Pflege- und Arbeitslosenversicherung. Die Steuer zahlt meist der Arbeitgeber pauschal. Von der Rentenversicherung können Sie sich befreien lassen.</p>'}
 const nt=nz(bt)/12;
 return big('Teilzeit netto pro Monat',eur2(nt),'Brutto '+eur2(mt)+(mt<=OG?' · Übergangsbereich (Midijob)':''))+kv([['Vollzeit netto',eur2(nv)],['Weniger Brutto',eur2(mt-bv/12),'neg'],['Weniger Netto',eur2(nt-nv),'neg'],['Anteil vom Vollzeit-Netto',pc(nt/nv,0),'t'],['Anteil der Stunden',pc(q,0)],['Netto pro Stunde (Vollzeit → Teilzeit)',eur2(nv/hv)+' → '+eur2(nt/ht)]])+'<p class="note">Lohnsteuer 2026 nach §32a EStG, Sozialabgaben mit den Werten 2026, kinderlos ab 23 Jahren, ohne Kirchensteuer. Zwischen 603,01 € und 2.000 € Brutto im Monat sind Ihre Sozialbeiträge geringer (Übergangsbereich). Maßgeblich ist Ihre Lohnabrechnung.</p>'}'''

e=lambda x:f"{x:,.0f}".replace(',','.')+' €'
cases=[(4000,40,32,'1','4.000 €, 40 → 32 Std.'),(4000,40,30,'1','4.000 €, 40 → 30 Std.'),(4000,40,20,'1','4.000 €, 40 → 20 Std.'),(3000,40,20,'1','3.000 €, 40 → 20 Std.'),(5000,40,30,'3','5.000 €, 40 → 30 Std., Klasse III')]
rows=[]
for b,v,t,kl,lab in cases:
    bt,nt,nv,s=ex(b,v,t,kl)
    rows.append([lab,e(bt),e(nt),e(nv),f"{s*100:.0f} %".replace('.',',')])
print(rows)

fig=[['Grundfreibetrag 2026','12.348 € im Jahr','Bis zu diesem zu versteuernden Einkommen zahlen Sie keine Einkommensteuer.'],
     ['Gesetzlicher Mindestlohn 2026','13,90 € pro Stunde','Gilt auch in Teilzeit für jede Stunde.'],
     ['Minijob-Grenze 2026','603 € im Monat','Bis dahin zahlen Sie keine Kranken-, Pflege- und Arbeitslosenversicherung; Rentenversicherung 3,6 %, Befreiung möglich.'],
     ['Übergangsbereich (Midijob)','603,01 € bis 2.000 € im Monat','Ihre Sozialbeiträge sind geringer als normal und steigen langsam bis 2.000 € an.'],
     ['Beitragssätze 2026 (Ihr Anteil)','Rente 9,3 % · Arbeitslosigkeit 1,3 % · Kranken 7,3 % + halber Zusatzbeitrag (Durchschnitt 2,9 %) · Pflege 1,8 % (+0,6 % kinderlos)','Diese Anteile zieht der Arbeitgeber vom Brutto ab.'],
     ['Beitragsbemessungsgrenzen 2026','Rente/Arbeitslosigkeit 8.450 € · Kranken/Pflege 5.812,50 € im Monat','Über diesen Beträgen steigen die Beiträge nicht weiter.']]

law=[['Recht auf Teilzeit (§ 8 TzBfG)','Arbeitsverhältnis länger als 6 Monate und mehr als 15 Beschäftigte beim Arbeitgeber.'],
     ['Antrag','Spätestens 3 Monate vor dem gewünschten Beginn, in Textform (zum Beispiel E-Mail).'],
     ['Brückenteilzeit (§ 9a TzBfG)','Teilzeit für 1 bis 5 Jahre mit Rückkehr zur alten Stundenzahl, wenn der Arbeitgeber mehr als 45 Beschäftigte hat.'],
     ['Gleiche Bezahlung (§ 4 TzBfG)','Teilzeitkräfte bekommen mindestens den anteiligen Lohn wie vergleichbare Vollzeitkräfte.']]

FAQ=[
("Wie viel netto bleibt bei 30 statt 40 Stunden?","Bei 4.000 € Vollzeit-Brutto in Steuerklasse I sinkt das Brutto um 25 % auf 3.000 €. Netto bleiben rund 2.054 € statt 2.606 €. Das sind etwa 79 % des Vollzeit-Nettos."),
("Warum sinkt das Netto weniger stark als das Brutto?","Weil die Lohnsteuer mit dem Einkommen steigt. Wer weniger verdient, zahlt einen kleineren Prozentsatz Steuer. Bei 20 statt 40 Stunden (4.000 € Vollzeit) bleiben deshalb rund 57 % des Nettos, obwohl es nur 50 % des Bruttos sind."),
("Was ist der Übergangsbereich (Midijob)?","Verdienen Sie zwischen 603,01 € und 2.000 € im Monat, zahlen Sie weniger Sozialbeiträge als normal. Der Arbeitgeber zahlt seinen vollen Anteil. Ein Beispiel: 1.500 € Brutto ergeben in Klasse I rund 1.207 € netto."),
("Habe ich ein Recht auf Teilzeit?","Ja, wenn Sie länger als 6 Monate im Betrieb sind und der Arbeitgeber mehr als 15 Beschäftigte hat. Stellen Sie den Antrag spätestens 3 Monate vor dem Beginn in Textform. Der Arbeitgeber darf nur aus betrieblichen Gründen ablehnen."),
("Kann ich später wieder Vollzeit arbeiten?","Mit der Brückenteilzeit geht das sicher: Sie vereinbaren 1 bis 5 Jahre Teilzeit und kehren danach zur alten Stundenzahl zurück. Das gilt bei Arbeitgebern mit mehr als 45 Beschäftigten."),
("Wie viel Urlaub habe ich in Teilzeit?","Das hängt von den Arbeitstagen ab, nicht von den Stunden. Rechnung: Urlaubstage × Ihre Arbeitstage ÷ 5. Bei 30 Tagen Urlaub und 3 Arbeitstagen pro Woche sind es 18 Tage – es bleiben trotzdem 6 freie Wochen."),
("Steigt mein Netto pro Stunde in Teilzeit?","Meist ja. Bei 4.000 € Vollzeit (40 Std.) und Teilzeit mit 30 Std. steigt das Netto pro Stunde von etwa 15,03 € auf 15,80 €, weil weniger Steuer anfällt."),
]

art='''<h2 id="vb">Beispiele: Netto in Teilzeit 2026</h2>
<div id="examples">'''+table(['Fall','Brutto Teilzeit','Netto Teilzeit','Netto Vollzeit','Anteil vom Vollzeit-Netto'],rows)+'''</div>
<p class="note">Pro Monat, kinderlos, ohne Kirchensteuer, durchschnittlicher Zusatzbeitrag 2,9 %. Berechnet mit der Formel dieses Rechners.</p>
<ul><li><b>32 statt 40 Stunden</b> (4-Tage-Woche): 20 % weniger Brutto, aber nur etwa 17 % weniger Netto.</li>
<li><b>20 statt 40 Stunden</b>: die Hälfte vom Brutto, aber rund 57 % vom Netto.</li>
<li><b>3.000 € Vollzeit, 20 Stunden</b>: 1.500 € Brutto liegen im Übergangsbereich. Netto bleiben rund 1.207 €.</li></ul>
<h2 id="werte">Wichtige Werte 2026</h2>
'''+table(['Wert','Höhe','Was bedeutet das?'],fig)+'''
<h2 id="rechnung">So rechnet der Rechner</h2>
<p>Ein Beispiel zuerst: Sie verdienen 4.000 € brutto bei 40 Stunden und wollen 30 Stunden arbeiten. Dann bekommen Sie 30 ÷ 40 = 75 % vom Brutto, also 3.000 €. Davon gehen Lohnsteuer und Sozialbeiträge ab. Netto bleiben rund <b>2.054 €</b> statt 2.606 €.</p>
<ul><li><b>Teilzeit-Brutto</b> = Vollzeit-Brutto × Teilzeit-Stunden ÷ Vollzeit-Stunden.</li>
<li><b>Sozialbeiträge</b> = Ihr Anteil an Renten-, Arbeitslosen-, Kranken- und Pflegeversicherung, bis zur Beitragsbemessungsgrenze.</li>
<li><b>Lohnsteuer</b> = Steuer auf das Einkommen nach dem Tarif 2026. Vorher werden Pauschalen und ein Teil der Sozialbeiträge abgezogen.</li>
<li><b>Progression</b> = je mehr Sie verdienen, desto höher ist der Steuersatz. Deshalb verlieren Sie in Teilzeit weniger Netto als Brutto.</li></ul>
<h2 id="recht">Ihre Rechte bei Teilzeit</h2>
'''+table(['Regel','Was gilt'],law)+'''
<h2 id="tips">Tipps</h2>
<ul><li><b>Steuerklasse prüfen.</b> Verheiratete können die Steuerklassen wechseln. Das ändert das monatliche Netto, nicht die Steuer im Jahr.</li>
<li><b>An die Rente denken.</b> Weniger Brutto bedeutet weniger Rentenpunkte.</li>
<li><b>Stunden gut verteilen.</b> Weniger Arbeitstage können mehr freie Tage bringen, bei gleichem Urlaub in Wochen.</li></ul>
<h2 id="faq" style="margin-top:22px">Häufige Fragen</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Quellen (geprüft am 25. November 2026): <a href="https://www.gesetze-im-internet.de/estg/__32a.html" rel="nofollow">§ 32a EStG</a>; <a href="https://www.gesetze-im-internet.de/tzbfg/" rel="nofollow">Teilzeit- und Befristungsgesetz</a>; <a href="https://www.bundesregierung.de/breg-de/aktuelles/beitragsbemessungsgrenzen-2386514" rel="nofollow">Bundesregierung – Sozialversicherungswerte 2026</a>; <a href="https://www.minijob-zentrale.de/" rel="nofollow">Minijob-Zentrale</a>; <a href="https://www.bmas.de/DE/Arbeit/Arbeitsrecht/Mindestlohn/mindestlohn.html" rel="nofollow">BMAS – Mindestlohn</a>. Beispiele mit der Formel dieses Rechners. Keine Steuer- oder Rechtsberatung.</p>'''

out=build(P,'Teilzeit-Rechner 2026 – Netto bei weniger Stunden berechnen',
 'Teilzeit-Rechner 2026: Brutto und Netto bei weniger Wochenstunden, mit Steuerklasse, Midijob-Übergangsbereich, Beispielen und Ihren Rechten nach dem TzBfG.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Von','Hong Life Calculators'),('Geprüft','25. November 2026'),('Quellen','EStG, TzBfG, Bundesregierung, Minijob-Zentrale')],
 [('form','Rechner'),('vb','Beispiele'),('werte','Werte 2026'),('rechnung','So wird gerechnet'),('recht','Ihre Rechte'),('tips','Tipps'),('faq','Häufige Fragen')],'Auf dieser Seite',('#examples','de'))
print(out)
