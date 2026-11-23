import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top

form='''<form class="card" id="form" onsubmit="return false"><h2>Vos données</h2><label class="f"><span>Heures par semaine</span><input id="h" inputmode="decimal" value="35"><small>Au-delà de 35 h : +25 % pour les 8 premières heures supplémentaires, +50 % ensuite (sauf accord collectif différent).</small></label><label class="f"><span>Lieu de travail</span><select id="z"><option value="m">France (hors Mayotte)</option><option value="y">Mayotte</option></select></label></form>'''

calc='''function calc(){const may=($('z')&&$('z').value==='y'),s=may?9.56:12.31,h=num('h'),hm=52/12,base=Math.min(h,35)*hm*s,hs=Math.max(0,Math.min(h,43)-35)*hm*s*1.25+Math.max(0,h-43)*hm*s*1.5,b=base+hs;
 const rows=[['Dont heures supplémentaires majorées',eur2(hs)],['Taux horaire brut',eur2(s)],['Heures payées par mois',(Math.min(h,35)*hm).toLocaleString('fr-FR',{maximumFractionDigits:2})+' h'+(h>35?' + '+((h-35)*hm).toLocaleString('fr-FR',{maximumFractionDigits:2})+' h sup.':'')],['Brut annuel',eur(b*12,0)]];
 if(!may)rows.splice(1,0,['Net estimé (≈ 79,2 % du brut, comme le net officiel à 35 h)',eur2(b*.7916)]);
 return big('SMIC mensuel brut',eur2(b),h.toLocaleString('fr-FR')+' h par semaine · depuis le 1er juin 2026')+kv(rows)+(may?'<p class="note">Service-public.fr ne publie pas de SMIC net pour Mayotte : seul le brut est affiché.</p>':'<p class="note">Net indicatif : il dépend de votre mutuelle, de votre convention collective et du traitement des heures supplémentaires.</p>')}'''

hm=52/12
def smic(h,s=12.31):
    base=min(h,35)*hm*s; hs=max(0,min(h,43)-35)*hm*s*1.25+max(0,h-43)*hm*s*1.5; b=base+hs
    return base,hs,b,b*.7916
def e(x,d=2):
    return f"{x:,.{d}f}".replace(',',' ').replace('.',',')+' €'
rows=[]
for h,lab in [(35,'Temps plein 35 h'),(39,'39 h (4 h sup. à +25 %)'),(24,'Temps partiel 24 h'),(20,'Mi-temps 20 h')]:
    base,hs,b,n=smic(h); rows.append([lab,e(b),e(n),e(b*12,0)])
b39=smic(39); b24=smic(24); b20=smic(20)

FAQ=[
("Quel est le montant du SMIC en 2026 ?","Depuis le <b>1er juin 2026</b>, le SMIC horaire brut est de <b>12,31 €</b>. Pour 35 heures par semaine, cela fait <b>1 867,02 € brut</b> par mois, soit environ <b>1 477,93 € net</b> selon service-public.fr. Avant cette date (depuis le 1er janvier 2026), il était de 12,02 € de l’heure, soit 1 823,03 € brut."),
("Combien fait le SMIC net par mois en 2026 ?","Pour un temps plein de 35 heures, l’administration indique <b>1 477,93 € net</b> par mois (9,74 € net de l’heure) depuis le 1er juin 2026. De janvier à mai 2026, c’était 1 443,11 € net. Le montant exact dépend de votre mutuelle et de votre convention collective."),
("Combien fait le SMIC pour 39 heures ?",f"À 39 heures, les 4 heures en plus sont des heures supplémentaires payées 25 % de plus. Cela donne environ <b>{e(b39[2])} brut</b> par mois ({e(b39[1])} d’heures supplémentaires), soit environ {e(b39[3])} net avec le même taux que le net officiel à 35 h."),
("Pourquoi le SMIC a-t-il augmenté le 1er juin 2026 ?","Quand les prix à la consommation montent d’au moins 2 % depuis la dernière fixation du SMIC, la loi impose une hausse automatique du même pourcentage. Le SMIC a donc augmenté de <b>2,41 %</b> au 1er juin 2026 (arrêté du 22 mai 2026)."),
("Le SMIC va-t-il augmenter le 1er janvier 2027 ?","Le SMIC est revalorisé chaque année au 1er janvier. Le montant pour 2027 n’a pas encore été publié officiellement au 23 novembre 2026 : il sera fixé par décret en fin d’année. Ce calculateur sera mis à jour dès sa publication."),
("Quel est le SMIC à Mayotte et le minimum garanti ?","À Mayotte, le SMIC horaire brut est de <b>9,56 €</b> depuis le 1er juin 2026, soit 1 449,93 € brut par mois pour 35 h. Le <b>minimum garanti</b> (une valeur de référence utilisée par exemple pour les avantages en nature repas) est de <b>4,35 €</b> depuis le 1er juin 2026, contre 4,25 € au 1er janvier."),
]
def faq_block(faq):
    return '<h2 id="faq" style="margin-top:22px">Questions fréquentes sur le SMIC</h2>'+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faq)

art='''<h2 id="figures">Montants officiels du SMIC en 2026</h2>
'''+table(['Montant','Depuis le 1er janvier 2026','Depuis le 1er juin 2026'],[
 ['SMIC horaire brut','12,02 €','<b>12,31 €</b>'],
 ['SMIC horaire net (indicatif)','–','9,74 €'],
 ['SMIC mensuel brut (35 h)','1 823,03 €','<b>1 867,02 €</b>'],
 ['SMIC mensuel net (35 h, indicatif)','1 443,11 €','<b>1 477,93 €</b>'],
 ['SMIC annuel brut (35 h)','–','22 404,20 €'],
 ['Mayotte : horaire brut','9,33 €','9,56 €'],
 ['Mayotte : mensuel brut (35 h)','1 415,05 €','1 449,93 €'],
 ['Minimum garanti','4,25 €','4,35 €'],
])+'''
<p class="note">Hausse de 1,18 % au 1er janvier 2026, puis hausse automatique de 2,41 % au 1er juin 2026. Le « net » est donné par l’administration à titre indicatif : c’est le brut moins les cotisations salariales. Mineurs avec moins de 6 mois de pratique dans la branche : 11,08 € brut de l’heure à 17 ans, 9,85 € à 16 ans et moins.</p>

<h2 id="ex">Exemples : SMIC selon le nombre d’heures</h2>
<p>Calculés avec le SMIC de 12,31 € brut de l’heure (métropole). Un mois compte en moyenne 52 ÷ 12 = 4,33 semaines.</p>
<div id="examples">'''+table(['Durée par semaine','Brut / mois','Net estimé / mois','Brut / an'],rows)+f'''</div>
<ul><li>À <b>35 h</b> : 1 867,02 € brut, environ 1 477,93 € net. C’est le chiffre officiel.</li>
<li>À <b>39 h</b> : environ {e(b39[2])} brut, car les 4 heures en plus sont payées 125 %.</li>
<li>À <b>24 h</b> (temps partiel) : environ {e(b24[2])} brut et {e(b24[3])} net.</li></ul>

<h2 id="how">Comment le SMIC mensuel est calculé</h2>
<p>Exemple à 35 h : 35 heures × 52 semaines ÷ 12 mois = 151,67 heures par mois. Puis 151,67 × 12,31 € = <b>1 867,02 € brut</b>.</p>
<p>Avec des <b>heures supplémentaires</b> (les heures au-delà de 35 h par semaine), le Code du travail prévoit, sauf accord collectif différent :</p>
<ul><li><b>+25 %</b> pour chacune des 8 premières heures supplémentaires (de la 36e à la 43e heure) ;</li><li><b>+50 %</b> pour les heures suivantes.</li></ul>
<p>Pour 39 h : 4 h × 4,33 semaines × 12,31 € × 1,25 = {e(b39[1])} en plus par mois.</p>
<p>Le <b>net</b> est le brut moins les cotisations salariales (retraite, CSG, CRDS…). Ici, on applique le même rapport que le net officiel à 35 h : 1 477,93 ÷ 1 867,02 ≈ 79,2 %.</p>
<h3>Quand le SMIC change-t-il ?</h3>
<ul><li>Chaque <b>1er janvier</b>, selon l’inflation et l’évolution des salaires.</li><li>En cours d’année si les prix montent d’au moins <b>2 %</b> depuis la dernière hausse (c’est ce qui s’est passé le 1er juin 2026).</li><li>Le gouvernement peut aussi décider un « coup de pouce » à tout moment.</li></ul>

<h2 id="tips">Conseils et erreurs fréquentes</h2>
<ul>
<li><b>Ne confondez pas brut et net</b> : 12,31 € est le taux brut. Sur la fiche de paie, vous touchez environ 9,74 € net de l’heure.</li>
<li><b>Vérifiez votre fiche de paie de juin 2026</b> : le nouveau taux s’applique aux heures travaillées depuis le 1er juin.</li>
<li><b>Votre convention collective</b> peut prévoir un salaire minimum plus élevé que le SMIC : c’est le plus élevé qui s’applique.</li>
<li><b>Temps partiel</b> : le SMIC est un taux horaire. Il suffit de multiplier par vos heures réelles.</li>
<li><b>Heures supplémentaires</b> : elles se comptent par semaine, au-delà de 35 h, pas sur le mois.</li>
</ul>
'''+faq_block(FAQ)+'''
<p class="note">Sources (vérifiées le 23 novembre 2026) : <a href="https://www.service-public.gouv.fr/particuliers/vosdroits/F2300" rel="nofollow">Service-public.fr – Smic</a> ; <a href="https://www.service-public.gouv.fr/particuliers/actualites/A18916" rel="nofollow">Service-public.fr – hausse de 2,41 % au 1er juin 2026</a> ; <a href="https://www.service-public.gouv.fr/particuliers/actualites/A15811" rel="nofollow">Service-public.fr – Smic au 1er janvier 2026</a> ; <a href="https://legislation.lassuranceretraite.fr/Pdf/circulaire_cnav_2026_16_12062026.pdf" rel="nofollow">Circulaire Cnav 2026-16 (arrêté du 22 mai 2026, minimum garanti)</a> ; <a href="https://code.travail.gouv.fr/code-du-travail/l3121-36" rel="nofollow">Code du travail, art. L3121-36</a>. Exemples calculés avec la formule de ce calculateur.</p>'''

out=build('/fr/smic-2026.html','SMIC 2026 : 12,31 € brut de l’heure, 1 867,02 € brut et net par mois',
 'SMIC depuis le 1er juin 2026 : 12,31 € brut de l’heure, 1 867,02 € brut et 1 477,93 € net par mois (35 h). Calcul pour 39 h, temps partiel et Mayotte.',art,FAQ,form=form,calc=calc)
add_top(out,[('Par','Hong Life Calculators'),('Vérifié le','23 novembre 2026'),('Sources','Service-public.fr, Code du travail, Cnav')],
 [('form','Calculateur'),('figures','Montants 2026'),('ex','Exemples selon les heures'),('how','Comment c’est calculé'),('tips','Conseils et erreurs'),('faq','Questions fréquentes')],'Sur cette page')
print(out)
for r in rows: print(r)
