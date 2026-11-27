import sys, math; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/de/abiturnote-rechner.html'
CHK='27. November 2026'

form='''<form class="card" id="form" onsubmit="return false"><h2>Ihre Punkte</h2><div class="two"><label class="f"><span>Block I (max. 600)</span><input id="b1" inputmode="decimal" value="430"><small>Punkte aus den Kursen der Qualifikationsphase. Mind. 200.</small></label><label class="f"><span>Block II (max. 300)</span><input id="b2" inputmode="decimal" value="210"><small>Punkte aus den Abiturprüfungen. Mind. 100.</small></label></div></form>'''

calc='''function calc(){const b1=num('b1'),b2=num('b2'),p=b1+b2;if(p<=0)return big('Abiturnote','—','Punkte eingeben');
 if(b1>600||b2>300)return big('Abiturnote','—','Block I hat höchstens 600, Block II höchstens 300 Punkte');
 const nt=x=>{let n=Math.floor((17/3-x/180)*10+1e-9)/10;return n<1?1:n},f=x=>x.toFixed(1).replace('.',',');
 const miss=[];if(b1<200)miss.push('Block I unter 200');if(b2<100)miss.push('Block II unter 100');if(p<300)miss.push('Gesamt unter 300');
 if(miss.length)return big('Abiturnote','nicht bestanden',p+' Punkte · '+miss.join(', '))+kv([['Block I',b1+' / 600'],['Block II',b2+' / 300'],['Gesamt',p+' / 900','t']]);
 const n=nt(p);let up='–';if(n>1){let q=p;while(nt(q)>=n&&q<900)q++;up=(q-p)+' Punkte mehr für '+f(nt(q))}
 return big('Abiturnote',f(n),p+' von 900 Punkten')+kv([['Block I',b1+' / 600'],['Block II',b2+' / 300'],['Gesamt',p+' / 900','t'],['Nächste bessere Note',up,'pos'],['Für 1,0 nötig','823 Punkte']])+'<p class="note">Note = 17/3 − Punkte/180, auf eine Stelle nach dem Komma abgeschnitten (nicht gerundet).</p>'}'''

def note(p):
    n=math.floor((17/3-p/180)*10+1e-9)/10; return max(1.0,n)
rng={}
for p in range(300,901): rng.setdefault(note(p),[]).append(p)
f=lambda x:f"{x:.1f}".replace('.',',')
tab=[[f(g),f"{min(v)}–{max(v)}" if min(v)!=max(v) else str(v[0])] for g,v in sorted(rng.items())]
half=(len(tab)+1)//2
tab2=[a+(tab[i+half] if i+half<len(tab) else ['','']) for i,a in enumerate(tab[:half])]

def nextup(p):
    n=note(p);q=p
    while note(q)>=n and q<900: q+=1
    return q-p, note(q)
ex=[]
for b1,b2 in [(430,210),(540,250),(330,140),(600,300),(380,90)]:
    p=b1+b2; ok=b1>=200 and b2>=100 and p>=300
    if ok:
        d,g=nextup(p); ex.append([str(b1),str(b2),str(p),f(note(p)),(f"{d} Punkte für {f(g)}" if note(p)>1 else '–')])
    else:
        ex.append([str(b1),str(b2),str(p),'nicht bestanden','Block II unter 100'])
print(ex)

FAQ=[
("Wie viele Punkte brauche ich für einen Schnitt von 2,0?","Mindestens 643 Punkte von 900. Mit 642 Punkten steht im Zeugnis eine 2,1. Für eine 1,5 brauchen Sie 733 Punkte, für eine 3,0 genau 463."),
("Ab wie vielen Punkten habe ich eine 1,0?","Ab 823 Punkten. Alles zwischen 823 und 900 Punkten ergibt die Note 1,0. Besser als 1,0 geht nicht."),
("Wird die Abiturnote gerundet?","Nein. Die Note wird nach der Formel 17/3 − Punkte/180 berechnet und nach der ersten Stelle hinter dem Komma abgeschnitten. 640 Punkte ergeben 2,111…, also eine 2,1 – nicht 2,0."),
("Wie viele Punkte brauche ich zum Bestehen?","Mindestens 300 Punkte insgesamt. Zur Prüfung zugelassen wird, wer in Block I mindestens 200 Punkte hat, und in Block II müssen es mindestens 100 Punkte sein. Mit genau 300 Punkten ist die Note 4,0."),
("Was ist Block I und was ist Block II?","Block I sind die Punkte aus Ihren Kursen in der Qualifikationsphase, höchstens 600. Block II sind die Punkte aus den Abiturprüfungen, höchstens 300. Beide zusammen ergeben die Gesamtpunktzahl von höchstens 900."),
("Gilt die Formel in allen Bundesländern?","Ja. Die Umrechnung von Punkten in die Note steht in der Vereinbarung der Kultusministerkonferenz und gilt bundesweit. Wie Block I genau zusammengesetzt wird – welche Kurse zählen und wie oft – regelt Ihr Bundesland."),
("Wie viele Punkte fehlen mir zur nächsten besseren Note?","Die Notenstufen liegen meist 18 Punkte auseinander. Mit 640 Punkten haben Sie eine 2,1. Schon 3 Punkte mehr, also 643, ergeben eine 2,0. Der Rechner zeigt Ihnen den Abstand direkt an."),
]

art='''<h2 id="figures">Die Regeln der KMK (Stand November 2026)</h2>
'''+table(['Regel','Wert'],[
 ['Höchstpunktzahl','900 Punkte (Block I bis 600, Block II bis 300)'],
 ['Zum Bestehen nötig','mind. 300 Punkte gesamt und mind. 100 in Block II'],
 ['Zulassung zur Prüfung','mind. 200 Punkte in Block I'],
 ['Umrechnung','Note = 17/3 − Punkte ÷ 180, nach einer Nachkommastelle abgeschnitten'],
 ['Beste Note 1,0','ab 823 Punkten'],
 ['Note 4,0','genau 300 Punkte']])+'''
<h2 id="tabelle">Tabelle: Punkte in Abiturnote umrechnen</h2>
'''+table(['Note','Punkte','Note','Punkte'],tab2)+'''
<h2 id="ex">Beispiele</h2>
<div id="examples">'''+table(['Block I','Block II','Gesamt','Abiturnote','Zur nächsten Note'],ex)+'''</div>
<ul><li><b>430 + 210 = 640 Punkte</b> ergeben eine 2,1. Mit 3 Punkten mehr wäre es eine 2,0.</li>
<li><b>380 + 90</b>: Zusammen sind das 470 Punkte, aber Block II liegt unter 100. Das Abitur ist dann nicht bestanden.</li>
<li><b>600 + 300 = 900 Punkte</b> sind die volle Punktzahl. Die Note ist 1,0, wie schon ab 823 Punkten.</li></ul>
<h2 id="how">So wird die Abiturnote berechnet</h2>
<p>Erst ein Beispiel: Sie haben 640 Punkte. Rechnen Sie 17 ÷ 3 = 5,667. Dann 640 ÷ 180 = 3,556. Ziehen Sie ab: 5,667 − 3,556 = 2,111. Die zweite Stelle hinter dem Komma fällt weg. Ihre Note ist <b>2,1</b>.</p>
<ul><li><b>Qualifikationsphase</b> heißen die letzten zwei Schuljahre vor dem Abitur. Ihre Kurse dort ergeben Block I.</li>
<li><b>Abiturprüfungen</b> sind die Prüfungen am Ende, schriftlich oder mündlich. Sie ergeben Block II.</li>
<li><b>Abschneiden</b> heißt: Es wird nicht aufgerundet. Auch 2,19 bleibt eine 2,1.</li>
<li>Fast jede Notenstufe umfasst 18 Punkte. 18 Punkte mehr machen Ihre Note um 0,1 besser.</li></ul>
<h2 id="tips">Tipps</h2>
<ul><li><b>Für den Numerus clausus zählt jede Zehntelnote.</b> Prüfen Sie, wie viele Punkte Ihnen zur nächsten Stufe fehlen.</li>
<li><b>Knapp unter einer Grenze?</b> Schon wenige Punkte in den Prüfungen können die Note um 0,1 verbessern. Wie stark eine Prüfung zählt, sagt Ihnen Ihre Schule.</li>
<li><b>Block I genau prüfen.</b> Welche Kurse Sie einbringen müssen, ist von Land zu Land verschieden. Ihre Schule rechnet Block I für Sie aus.</li></ul>
<h2 id="faq" style="margin-top:22px">Häufige Fragen zur Abiturnote</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+f'''
<p class="note">Quelle (geprüft am {CHK}): <a href="https://www.kmk.org/fileadmin/Dateien/veroeffentlichungen_beschluesse/1972/1972_07_07-VB-gymnasiale-Oberstufe-Abiturpruefung.pdf" rel="nofollow">KMK – Vereinbarung zur Gestaltung der gymnasialen Oberstufe und der Abiturprüfung (i. d. F. vom 06.06.2024), Ziff. 9.5 und Anlage 4</a>. Tabelle und Beispiele mit der Formel dieses Rechners. Maßgeblich ist das Zeugnis Ihrer Schule.</p>'''

out=build(P,'Abiturnote berechnen 2026 – Punkte-Tabelle und Rechner (KMK)',
 'Abiturnote aus Block I und Block II berechnen: komplette Punkte-Tabelle von 1,0 bis 4,0, Bestehensregeln und wie viele Punkte zur nächsten Note fehlen.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Von','Hong Life Calculators'),('Geprüft',CHK),('Quelle','Kultusministerkonferenz (KMK)')],
 [('form','Rechner'),('figures','Regeln'),('tabelle','Punkte-Tabelle'),('ex','Beispiele'),('how','So wird gerechnet'),('faq','FAQ')],'Auf dieser Seite')
print(out)
