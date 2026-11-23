import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/fr/calcul-consommation-electrique.html'
B,HP,HC=0.2001,0.2142,0.1589  # Tarif Bleu TTC au 1er août 2026 (6 kVA)

def r2(x): return f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X',' ')
def n(x,d=1):
    s=f'{x:,.{d}f}'.replace(',','X').replace('.',',').replace('X',' ')
    return s.rstrip('0').rstrip(',') if ',' in s else s
def eur(x): return (r2(x) if abs(x)<100 else f'{round(x):,}'.replace(',',' '))+' €'

def ex(name,uso,w,h,mn):
    kd=w/1000*(h+mn/60);k=kd*30;m=k*B
    return [name,uso,n(kd,2)+' kWh',n(k,1)+' kWh',r2(m)+' €',eur(m*365/30)],(k,m)

E=[ex('Radiateur électrique 2 000 W','4 h par jour à pleine puissance',2000,4,0),
   ex('Ballon d’eau chaude 2 000 W','3 h de chauffe par jour',2000,3,0),
   ex('Four électrique 2 500 W','30 min par jour',2500,0,30),
   ex('Plaque de cuisson 1 500 W','40 min par jour',1500,0,40),
   ex('Ordinateur fixe 200 W','4 h par jour',200,4,0),
   ex('Box internet 10 W','24 h sur 24',10,24,0),
   ex('Sèche-cheveux 1 800 W','10 min par jour',1800,0,10)]
rows=[e[0] for e in E]
kR,mR=E[0][1]; kE,mE=E[1][1]

form='''<form class="card" id="form" onsubmit="return false"><h2>Votre appareil</h2>
<label class="f"><span>Puissance (W)</span><input id="w" inputmode="decimal" value="2 000"><small>Sur la plaque signalétique ou la notice. 1 kW = 1 000 W.</small></label>
<label class="f"><span>Heures par jour</span><input id="h" inputmode="decimal" value="4"></label>
<label class="f"><span>Plus minutes par jour</span><input id="mn" inputmode="decimal" value="0"><small>Pratique pour le four, le sèche-cheveux ou la bouilloire (30 min = 0,5 h).</small></label>
<label class="f"><span>Prix du kWh (€)</span><input id="kp" inputmode="decimal" value="0,2001"><small>Par défaut : Tarif Bleu EDF option Base, TTC, depuis le 1er août 2026. Mettez le prix de votre facture.</small></label>
<label class="f"><span>Jours</span><input id="d" inputmode="decimal" value="30"></label></form>'''

calc='''function calc(){const pv=id=>{const v=String($(id).value).trim();return /^0[.,]\\d+$/.test(v)?parseFloat(v.replace(',','.')):num(id)};const kw=num('w')/1000,hd=num('h')+num('mn')/60,d=Math.max(1,num('d')),p=pv('kp'),k=kw*hd*d,m=k*p;
 return big('Coût sur '+nn(d,0)+' jours',mf2(m),nn(k,1)+' kWh')+kv([['Par jour',mf2(m/d)+' ('+nn(kw*hd,2)+' kWh)'],['Par heure d’utilisation',mf2(kw*p)],['Par mois (30 jours)',mf2(m*30/d)],[O.y,mf(m*365/d)],['Durée par jour',nn(hd,2)+' h'],['Même conso en heures creuses (0,1589 €)',mf2(k*0.1589)]])+'<p class="note">Coût de l’énergie seulement : l’abonnement est payé même si l’appareil est éteint.</p>'}'''

FAQ=[
("Combien consomme un radiateur électrique ?","Un radiateur de 2 000 W allumé 4 heures à pleine puissance consomme 8 kWh par jour, soit 240 kWh en 30 jours. Au Tarif Bleu Base (0,2001 € TTC le kWh), cela fait "+r2(mR)+" € par mois. Avec un thermostat, il se coupe souvent, donc la vraie consommation est plus basse."),
("Quel est le prix du kWh en 2026 ?","Au Tarif Bleu d’EDF (tarif réglementé), depuis le 1er août 2026 : 0,2001 € TTC le kWh en option Base (3 et 6 kVA). En option Heures creuses : 0,2142 € en heures pleines et 0,1589 € en heures creuses. Les offres de marché ont leurs propres prix."),
("Comment convertir des kWh en euros ?","Multipliez les kWh par le prix du kWh. 100 kWh au Tarif Bleu Base coûtent 100 × 0,2001 = 20,01 €. Pour passer des watts aux kWh : watts ÷ 1 000 × heures."),
("Combien coûte un ballon d’eau chaude par mois ?","Un ballon de 2 000 W qui chauffe 3 heures par jour consomme 6 kWh par jour, 180 kWh par mois : "+r2(mE)+" € au prix Base, ou "+r2(kE*HC)+" € s’il chauffe en heures creuses à 0,1589 €."),
("Combien coûte l’abonnement 6 kVA ?","Au Tarif Bleu depuis le 1er août 2026 : 15,86 € TTC par mois en option Base comme en Heures creuses. Il se paie en plus de la consommation, quoi que vous allumiez."),
("Quand le prix de l’électricité change-t-il ?","Le Tarif Bleu a augmenté en moyenne de 2,5 % TTC le 1er août 2026. Selon Service-Public.fr, des changements de structure pourront s’appliquer à partir de février 2027. Au 23 novembre 2026, aucun nouveau prix n’était publié.")]

art='''<h2 id="figures" style="margin-top:4px">Prix officiels de l’électricité en 2026</h2>
'''+table(['Tarif Bleu résidentiel (6 kVA)','Prix TTC depuis le 1er août 2026','Prix hors taxes (CRE)'],[
['Option Base – prix du kWh','0,2001 €','13,61 c€'],
['Option Heures creuses – heures pleines','0,2142 €','14,79 c€'],
['Option Heures creuses – heures creuses','0,1589 €','10,18 c€'],
['Abonnement 6 kVA (Base ou HP/HC)','15,86 € par mois','143,28 € par an'],
['Accise sur l’électricité (≤ 36 kVA)','30,62 € par MWh (3,062 c€ par kWh)','depuis le 1er août 2026 (30,85 € avant)']])+'''
<p class="note">Le <b>Tarif Bleu</b> est le tarif réglementé de vente d’électricité (TRVE) : son prix est proposé par la Commission de régulation de l’énergie (CRE) et fixé par les pouvoirs publics. <b>TTC</b> veut dire toutes taxes comprises. <b>L’accise</b> est la taxe sur l’électricité, comptée par kWh. Hausse moyenne au 1er août 2026 : +2,5 % TTC. Le prix TTC du kWh = (prix HT + accise) × 1,20 de TVA : (13,61 + 3,062) × 1,2 ≈ 20,01 c€. Les prix sont ceux de la France métropolitaine continentale.</p>
<h2 id="ex">Exemples : combien consomme chaque appareil</h2>
<p>Un radiateur de 2 000 W allumé 4 heures consomme 8 kWh par jour. En 30 jours, c’est 240 kWh. À 0,2001 € le kWh, cela coûte '''+r2(mR)+''' € par mois. Voici d’autres appareils (30 jours, prix Tarif Bleu Base TTC) :</p>
<div id="examples">'''+table(['Appareil','Utilisation','kWh par jour','kWh sur 30 jours','Coût sur 30 jours','Coût par an'],rows)+'''</div>
<ul><li>Le radiateur coûte cher parce qu’il tire beaucoup de puissance pendant longtemps : 1 heure de moins par jour fait gagner 2 kWh, soit 0,40 € par jour.</li>
<li>Le ballon d’eau chaude chauffé en heures creuses revient à '''+r2(kE*HC)+''' € au lieu de '''+r2(mE)+''' € par mois.</li>
<li>La box internet ne consomme que 10 W, mais elle reste allumée tout le temps : '''+eur(E[5][1][1]*365/30)+''' par an.</li></ul>
<p class="note">Calculé avec la formule de cette page. Les puissances sont des exemples courants : vérifiez celles de vos appareils.</p>
<h2 id="how">Comment se calcule la consommation électrique</h2>
<p>Votre facture compte des <b>kWh</b> (kilowattheures). Un kWh, c’est un appareil de 1 000 W allumé pendant une heure.</p>
<ul><li><b>kWh par jour</b> = puissance (W) ÷ 1 000 × heures par jour</li>
<li><b>kWh sur la période</b> = kWh par jour × nombre de jours</li>
<li><b>Coût</b> = kWh × prix du kWh (€)</li></ul>
<p>Les minutes deviennent des heures : 30 minutes = 0,5 heure, 10 minutes ≈ 0,17 heure. Le coût par an = coût de la période × 365 ÷ jours.</p>
<h3>Quel prix du kWh choisir ?</h3>
<p>Prenez le prix TTC du kWh sur votre facture. En option Heures creuses, utilisez le prix des heures pleines pour un appareil utilisé en journée et celui des heures creuses pour un appareil programmé la nuit (souvent le ballon d’eau chaude). Avec une offre de marché, le prix est celui de votre contrat.</p>
<h3>Les appareils à thermostat</h3>
<p>Radiateurs, ballons, réfrigérateurs et fours s’allument et s’éteignent tout seuls. Ils ne tirent pas leur pleine puissance tout le temps. Le calcul donne donc un maximum. Pour un réfrigérateur, utilisez plutôt les kWh par an de l’étiquette énergie.</p>
<h2 id="tips">Conseils et erreurs fréquentes</h2>
<ul><li><b>Visez les appareils qui chauffent</b> : radiateurs, ballon, four, plaques et sèche-linge pèsent bien plus que les ampoules LED.</li>
<li><b>Programmez en heures creuses</b> si vous avez cette option : à 0,1589 € au lieu de 0,2142 €, le kWh coûte environ 26 % de moins.</li>
<li><b>Baissez le chauffage d’un cran</b> ou réduisez sa durée : chaque heure de moins d’un radiateur de 2 000 W économise 2 kWh.</li>
<li><b>Éteignez les veilles</b> avec une multiprise à interrupteur.</li></ul>
<h3>Erreurs fréquentes</h3>
<ul><li>Confondre W et kWh : 1 000 W ne font 1 kWh qu’après une heure entière.</li>
<li>Prendre le prix hors taxes : le prix TTC est environ 47 % plus élevé (0,2001 € contre 0,1361 €).</li>
<li>Ajouter l’abonnement au coût d’un appareil : il est fixe pour tout le logement.</li>
<li>Compter un radiateur à pleine puissance 24 h sur 24 alors que son thermostat le coupe.</li></ul>
<h2 id="faq" style="margin-top:22px">Questions fréquentes</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (vérifiées le 23 novembre 2026) : <a href="https://www.cre.fr/fileadmin/Documents/Deliberations/2026/260715_2026-147_TRVE.pdf" rel="nofollow">CRE – Délibération n° 2026-147 (TRVE au 1er août 2026)</a> ; <a href="https://www.cre.fr/fileadmin/Documents/Deliberations/2026/260715_2026-147_TRVE_Annexe_B.pdf" rel="nofollow">CRE – Annexe B, barèmes hors taxes</a> ; <a href="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054569470" rel="nofollow">Légifrance – Décision du 29 juillet 2026 (tarifs résidentiels)</a> ; <a href="https://www.service-public.gouv.fr/particuliers/actualites/A18776" rel="nofollow">Service-Public.fr – Tarifs de l’électricité au 1er août 2026</a> ; <a href="https://particulier.edf.fr/fr/accueil/guide-energie/electricite/prix-kwh-electricite.html" rel="nofollow">EDF – Prix TTC du Tarif Bleu</a>. Exemples calculés avec la formule de cette page.</p>'''

if __name__=='__main__':
    out=build(P,'Calcul consommation électrique 2026 – Coût d’un appareil en €',
     'Calculez les kWh et le coût en euros d’un radiateur, ballon ou four. Prix du kWh Tarif Bleu au 1er août 2026 : 0,2001 € TTC en Base. Exemples chiffrés.',art,FAQ,form=form,calc=calc)
    add_top(out,[('Par','Hong Life Calculators'),('Vérifié le','23 novembre 2026'),('Sources','CRE, Légifrance, Service-Public.fr, EDF')],
      [('form','Calculateur'),('figures','Prix officiels 2026'),('ex','Exemples par appareil'),('how','Comment se calcule la consommation'),('tips','Conseils et erreurs'),('faq','Questions fréquentes')],'Sur cette page')
    print(out)
    for r in rows: print(r)
