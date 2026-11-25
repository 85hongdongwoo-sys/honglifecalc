import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/de/zinseszins-rechner.html'
CHK='25. November 2026'

form='''<form class="card" id="form" onsubmit="return false"><h2>Ihre Angaben</h2><label class="f"><span>Startkapital (€)</span><input id="s" inputmode="decimal" value="5.000"></label><label class="f"><span>Monatliche Sparrate (€)</span><input id="m" inputmode="decimal" value="200"><small>Wird am Ende jedes Monats eingezahlt. 0 für eine Einmalanlage.</small></label><label class="f"><span>Zins p. a. (%)</span><input id="r" inputmode="decimal" value="5"><small>Beispielwert. Tragen Sie den Zins Ihres Angebots ein.</small></label><label class="f"><span>Jahre</span><input id="j" inputmode="decimal" value="20"><small>Halbe Jahre mit Komma, z. B. 2,5.</small></label></form>'''

calc='''function calc(){const r=num('r'),j=num('j'),n=Math.round(j*12),s=num('s'),m=num('m');
 if(n<1)return big('Endkapital','–','Bitte eine Laufzeit von mindestens 1 Monat eingeben');
 const i=Math.pow(1+r/100,1/12)-1;let b=s;
 for(let k=0;k<n;k++)b+=b*i+m;
 const e=s+m*n,zins=b-e;
 const rows=[['Ihre Einzahlungen',eur(e)],['Zinsertrag',eur(zins),'pos']];
 rows.push(['Anteil der Zinsen am Endkapital',b>0?pc(Math.max(0,b-e)/b,0):'–']);
 if(r>0)rows.push(['Verdopplung des Geldes (ohne Sparrate)','ca. '+(Math.log(2)/Math.log(1+r/100)).toLocaleString('de-DE',{maximumFractionDigits:1})+' Jahre']);
 return big('Endkapital',eur(b),'nach '+j.toLocaleString('de-DE')+' Jahren · Einzahlungen '+eur(e))+kv(rows)+'<p class="note">Zinseszins mit monatlicher Gutschrift zum konformen Zins: '+r.toLocaleString('de-DE')+' % im Jahr ergeben genau '+r.toLocaleString('de-DE')+' % effektiv. Sparrate jeweils am Monatsende.'+' Ohne Steuern und Kosten.'+'</p>'}'''

def zz(s,m,r,j,fb=None):
    i=(1+r/100)**(1/12)-1;b=s;tx=0;yi=0;n=round(j*12)
    for k in range(n):
        z=b*i;yi+=z;b+=z+m
        if fb is not None and ((k+1)%12==0 or k==n-1):
            t=max(0,yi-fb)*0.26375;b-=t;tx+=t;yi=0
    return b,s+m*n,tx
e=lambda x:f"{x:,.0f} €".replace(',','.')
ex=[]
for s,m,r,j,lab in [(0,100,5,10,'100 € im Monat, 10 Jahre'),(0,200,5,20,'200 € im Monat, 20 Jahre'),(5000,200,5,20,'5.000 € Start + 200 € im Monat, 20 Jahre'),(10000,0,4,10,'10.000 € einmalig, 10 Jahre'),(0,500,7,30,'500 € im Monat, 30 Jahre')]:
    b,ein,_=zz(s,m,r,j)
    ex.append([lab,f"{r} %".replace('.',','),e(ein),e(b),e(b-ein)])
print(ex)


FAQ=[
("Was werden 200 € im Monat in 20 Jahren?","Bei 5 % Zins im Jahr werden aus 200 € im Monat rund 81.161 €. Sie zahlen selbst 48.000 € ein. Die übrigen gut 33.000 € sind Zinsen und Zinseszinsen. Mit 5.000 € Startkapital sind es rund 94.427 €."),
("Wie lange dauert es, bis sich mein Geld verdoppelt?","Teilen Sie 72 durch den Zins. Bei 4 % sind das etwa 18 Jahre, bei 6 % etwa 12 Jahre. Genau gerechnet sind es bei 4 % 17,7 Jahre. Der Rechner zeigt den genauen Wert."),
("Was ist der Unterschied zwischen Zins und Zinseszins?","Zins bekommen Sie auf Ihr eingezahltes Geld. Zinseszins bekommen Sie zusätzlich auf die Zinsen, die schon gutgeschrieben wurden. Je länger Sie sparen, desto größer wird dieser Teil."),
("Was bringt eine Einmalanlage von 10.000 €?","Bei 4 % Zins im Jahr werden aus 10.000 € in 10 Jahren 14.802 €. Bei 6 % wären es 17.908 €. Ein höherer Zins macht über lange Zeit einen großen Unterschied."),
("Wie viel muss ich sparen, um in 20 Jahren 100.000 € zu haben?","Bei 5 % Zins brauchen Sie ohne Startkapital rund 246 € im Monat. Bei 3 % sind es rund 306 €. Probieren Sie im Rechner verschiedene Sparraten aus."),
("Rechnet der Rechner mit monatlicher oder jährlicher Verzinsung?","Mit monatlicher Gutschrift zum sogenannten konformen Zins. Das heißt: 5 % im Jahr bleiben genau 5 % effektiv, egal ob die Bank monatlich oder jährlich gutschreibt. Ein Einmalbetrag wächst daher genau wie bei jährlicher Verzinsung."),
]

art='''<h2 id="ex">Beispiele: So wächst Ihr Geld</h2>
<div id="examples">'''+table(['Sparplan','Zins p. a.','Eingezahlt','Endkapital','davon Zinsen'],ex)+'''</div>
<ul><li>Wer <b>30 Jahre lang 500 € im Monat</b> bei 7 % anlegt, zahlt 180.000 € ein. Am Ende sind es rund 584.726 € – mehr als zwei Drittel sind Zinsen.</li>
<li>Eine <b>Einmalanlage von 10.000 €</b> wächst bei 4 % in 10 Jahren auf 14.802 €.</li>
<li>Die Beispiele rechnen ohne Steuern und ohne Kosten. Bei Fonds und ETFs ist der Zins nicht fest. Dort sind 5 % oder 7 % nur Annahmen.</li></ul>
<h2 id="how">So funktioniert der Zinseszins</h2>
<p>Erst ein Beispiel: Sie legen 1.000 € zu 5 % an. Nach einem Jahr haben Sie 1.050 €. Im zweiten Jahr bekommen Sie 5 % auf 1.050 €, also 52,50 €. Nach zwei Jahren haben Sie 1.102,50 €. Die 2,50 € extra sind der Zinseszins.</p>
<ul><li><b>Startkapital</b> ist das Geld, das Sie am Anfang anlegen.</li>
<li><b>Sparrate</b> ist der Betrag, den Sie jeden Monat dazulegen.</li>
<li><b>Konformer Zins</b>: Der Rechner teilt den Jahreszins so auf die Monate auf, dass über ein Jahr genau der angegebene Zins herauskommt. Monatszins i = (1 + Jahreszins)<sup>1/12</sup> − 1.</li>
<li><b>Formel</b>: Endkapital = K₀ × (1 + i)<sup>n</sup> + Rate × ((1 + i)<sup>n</sup> − 1) ÷ i. Dabei ist n die Zahl der Monate.</li></ul>
<h2 id="tips">Tipps und häufige Fehler</h2>
<ul><li><b>Früh anfangen.</b> 200 € im Monat über 20 Jahre bringen bei 5 % rund 33.000 € Zinsen. Über 10 Jahre sind es nur etwa 6.900 €.</li>
<li><b>Steuern nicht vergessen.</b> Auf Zinsen können Steuern anfallen. Der Rechner zeigt Werte vor Steuern.</li>
<li><b>Lockzinsen prüfen.</b> Viele Tagesgeld-Angebote gelten nur ein paar Monate. Rechnen Sie mit dem Zins, der danach gilt.</li>
<li><b>Inflation bedenken.</b> Steigen die Preise schneller als Ihr Zins, kaufen Sie sich später trotzdem weniger.</li>
</ul>
<h2 id="faq" style="margin-top:22px">Häufige Fragen zum Zinseszins</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+f'''
<p class="note">Stand: {CHK}. Alle Beispiele sind mit der Formel dieses Rechners berechnet. Allgemeine Information, keine Anlageberatung.</p>'''

out=build(P,'Zinseszinsrechner 2026 – Sparplan mit Startkapital und monatlicher Rate',
 'Zinseszins berechnen: Endkapital mit Startkapital und monatlicher Sparrate, Zinsanteil und Verdopplungszeit. Beispiele, Formel und FAQ.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Von','Hong Life Calculators'),('Stand','25. November 2026'),('Grundlage','Finanzmathematik')],
 [('form','Rechner'),('ex','Beispiele'),('how','So funktioniert es'),('tips','Tipps'),('faq','FAQ')],'Auf dieser Seite',('#examples','de'))
print(out)
