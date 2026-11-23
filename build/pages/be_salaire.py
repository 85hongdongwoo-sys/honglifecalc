import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top

form='''<form class="card" id="form" onsubmit="return false"><h2>Vos données</h2><label class="f"><span>Salaire brut mensuel (€)</span><input id="m" inputmode="decimal" value="4 000"><small>Employé (contrat d’employé), temps plein ou partiel. Sans pécule de vacances ni 13e mois.</small></label><label class="f"><span>Taxe communale (%)</span><input id="c" inputmode="decimal" value="7"><small>Le taux de votre commune figure sur votre avertissement-extrait de rôle. 7 % est un exemple.</small></label><label class="f"><span>Enfants à charge</span><input id="k" inputmode="decimal" value="0"></label></form>'''

calc='''function calc(){const T=[[16720,.25],[29510,.40],[51070,.45],[Infinity,.50]],EK=[0,2130,5130,11440,18510];
 const m=num('m'),on=m*.1307,ai=12*(m-on),fp=Math.min(ai*.3,6070),ni=ai-fp,k=Math.max(0,Math.round(num('k'))),qe=11550+(k<=4?EK[k]:18510+(k-4)*7070),tax=Math.max(0,prog(ni,T)-prog(qe,T)),com=tax*num('c')/100,net=ai-tax-com;
 return big('Net mensuel estimé',mf(net/12),'revenus 2026 · hors pécule de vacances et 13e mois')+kv([['ONSS travailleur (13,07 %) / mois',mf(on),'neg'],['Brut annuel après ONSS',mf(ai)],['Frais professionnels forfaitaires (an)',mf(fp)],['Revenu imposable (an)',mf(ni)],['Quotité exemptée (avec enfants)',mf(qe)],['Impôt fédéral (an)',mf(tax),'neg'],['Taxe communale (an)',mf(com),'neg'],['Net annuel',mf(net)]])+'<p class="note">Estimation de l’impôt final pour un employé isolé. Non inclus : bonus à l’emploi (bas salaires), cotisation spéciale de sécurité sociale, réductions d’impôt personnelles. Le précompte retenu chaque mois peut être un peu différent.</p>'}'''

def prog(x,B):
    t=0;lo=0
    for hi,r in B:
        if x>lo: t+=(min(x,hi)-lo)*r
        lo=hi
    return max(0,t)
T=[(16720,.25),(29510,.40),(51070,.45),(float('inf'),.50)]
EK=[0,2130,5130,11440,18510]
def be(m,c=7,k=0):
    on=m*.1307;ai=12*(m-on);fp=min(ai*.3,6070);ni=ai-fp;qe=11550+(EK[k] if k<=4 else 18510+(k-4)*7070)
    tax=max(0,prog(ni,T)-prog(qe,T));com=tax*c/100;net=ai-tax-com
    return on,ai,fp,ni,qe,tax,com,net
def e(x,d=0):
    s=f"{x:,.{d}f}".replace(',',' ').replace('.',',')
    return s+' €'
R={}
rows=[]
for m,k in [(2500,0),(3000,0),(4000,0),(5000,0),(4000,2)]:
    on,ai,fp,ni,qe,tax,com,net=be(m,7,k); R[(m,k)]=(on,ai,fp,ni,qe,tax,com,net)
    rows.append([e(m)+(' · 2 enfants' if k else ' · isolé'),e(on,2),e(tax),e(com),f'<b>{e(net/12)}</b>'])

n25=e(R[(2500,0)][7]/12); n30=e(R[(3000,0)][7]/12); n40=e(R[(4000,0)][7]/12); n50=e(R[(5000,0)][7]/12); n40k=e(R[(4000,2)][7]/12)
on4,ai4,fp4,ni4,qe4,tax4,com4,net4=R[(4000,0)]
tax0=be(4000,0,0)[7]

FAQ=[
("Combien de net pour 4 000 € brut en Belgique ?",f"Environ <b>{n40}</b> net par mois pour un employé isolé sans enfant, avec une taxe communale de 7 % (revenus 2026). On retire d’abord {e(on4,2)} d’ONSS, puis l’impôt ({e(tax4)} par an) et la taxe communale ({e(com4)} par an). Avec 2 enfants à charge, le net monte à environ {n40k}."),
("Combien fait 3 000 € brut en net ?",f"Environ <b>{n30}</b> net par mois pour un employé isolé sans enfant (taxe communale 7 %). Pour 2 500 € brut, c’est environ {n25} ; pour 5 000 € brut, environ {n50}."),
("Combien de net pour 2 500 € brut ?",f"Environ <b>{n25}</b> par mois pour un isolé sans enfant. Attention : à ce niveau de salaire, le bonus à l’emploi peut réduire vos cotisations et votre impôt. Il n’est pas inclus ici, donc votre vrai net peut être un peu plus élevé."),
("Quel est le taux de l’ONSS sur le salaire ?","La cotisation personnelle du travailleur est de <b>13,07 %</b> du salaire brut (pension 7,50 %, soins de santé 3,55 %, indemnités 1,15 %, chômage 0,87 %). Pour un employé, elle se calcule sur 100 % du brut. Pour un ouvrier, elle se calcule sur le brut majoré de 8 % (108 %), car son pécule de vacances est payé par une caisse à part."),
("Qu’est-ce que la taxe communale ?",f"C’est un impôt local, calculé en pourcentage de votre impôt fédéral. Chaque commune choisit son taux. Exemple : avec un impôt fédéral de {e(tax4)} et 7 % de taxe communale, vous payez {e(com4)} de plus par an. Le taux de votre commune est indiqué sur votre avertissement-extrait de rôle."),
("Quelle est la quotité exemptée d’impôt pour les revenus 2026 ?","La réforme de l’impôt des personnes physiques adoptée en juillet 2026 fait passer le montant de base de 4 785 € à 4 945 €. Après indexation, cela donne environ <b>11 550 €</b> pour les revenus 2026 (exercice d’imposition 2027), contre 11 180 € sans la réforme. Avec un enfant à charge, on ajoute 2 130 € ; avec deux, 5 130 €."),
]

def faq_block(faq):
    return '<h2 id="faq" style="margin-top:22px">Questions fréquentes</h2>'+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faq)

art='''<h2 id="figures">Chiffres officiels utilisés (revenus 2026, exercice d’imposition 2027)</h2>
'''+table(['Élément','Montant 2026','Ce que c’est'],[
 ['Cotisation ONSS du travailleur','13,07 % du brut','Part du salaire qui finance la sécurité sociale (pension, santé, chômage).'],
 ['Frais professionnels forfaitaires','30 % du revenu, max. 6 070 €','Somme que le fisc retire d’office de votre revenu, sans justificatif.'],
 ['Barème : tranche à 25 %','0 – 16 720 €','Taux sur la première partie du revenu imposable.'],
 ['Tranche à 40 %','16 720 – 29 510 €',''],
 ['Tranche à 45 %','29 510 – 51 070 €',''],
 ['Tranche à 50 %','au-delà de 51 070 €',''],
 ['Quotité exemptée de base','≈ 11 550 €','Partie du revenu sur laquelle vous ne payez pas d’impôt (montant de base légal 4 945 € après la réforme, indexé).'],
 ['Supplément 1 enfant','+ 2 130 €','S’ajoute à la quotité exemptée.'],
 ['2 enfants','+ 5 130 €',''],
 ['3 enfants','+ 11 440 €',''],
 ['4 enfants','+ 18 510 €',''],
 ['Par enfant en plus','+ 7 070 €',''],
])+'''
<p class="note">La réforme de l’impôt des personnes physiques (Chambre, juillet 2026) relève la quotité exemptée dès les revenus 2026 et gèle l’indexation des suppléments pour enfants. Les suppléments pour 1 et 2 enfants augmentent ; ceux pour 3 enfants et plus restent au niveau de l’an passé.</p>

<h2 id="ex">Exemples : de brut à net</h2>
<p>Employé isolé, temps plein, taxe communale 7 %. Montants calculés avec ce calculateur.</p>
<div id="examples">'''+table(['Brut mensuel','ONSS / mois','Impôt fédéral / an','Taxe communale / an','Net / mois'],rows)+f'''</div>
<ul><li>Pour <b>3 000 € brut</b>, il reste environ <b>{n30}</b> net par mois.</li>
<li>Pour <b>4 000 € brut</b>, environ <b>{n40}</b>. Avec deux enfants à charge, environ {n40k}.</li>
<li>Sans taxe communale (0 %), 4 000 € brut donne environ {e(tax0/12)} net : la commune pèse donc environ {e((tax0-net4)/12)} par mois.</li></ul>

<h2 id="how">Comment on passe du brut au net</h2>
<p>Prenons 4 000 € brut par mois, sans enfant, avec 7 % de taxe communale.</p>
<ol>
<li><b>ONSS</b> : 4 000 × 13,07 % = {e(on4,2)}. Il reste {e(4000-on4,2)} par mois, soit {e(ai4)} par an.</li>
<li><b>Frais professionnels forfaitaires</b> : 30 % de {e(ai4)}, mais plafonnés à {e(fp4)}. Le revenu imposable est donc {e(ni4)}.</li>
<li><b>Impôt selon le barème</b> : 25 % sur les premiers 16 720 €, 40 % jusqu’à 29 510 €, 45 % sur le reste. Ensuite on retire l’impôt sur la quotité exemptée (11 550 × 25 % = 2 887,50 €). Résultat : {e(tax4)} par an.</li>
<li><b>Taxe communale</b> : 7 % de {e(tax4)} = {e(com4)}.</li>
<li><b>Net</b> : {e(ai4)} − {e(tax4)} − {e(com4)} = {e(net4)} par an, soit <b>{n40}</b> par mois.</li>
</ol>
<p>En bref : <b>net = brut − ONSS − impôt fédéral − taxe communale</b>. L’impôt fédéral = barème(revenu imposable) − barème(quotité exemptée).</p>
<h3>Employé ou ouvrier ?</h3>
<p>Ce calculateur vise les <b>employés</b>. Pour un ouvrier, l’ONSS de 13,07 % se calcule sur 108 % du brut. Son net mensuel est donc un peu plus bas, mais son pécule de vacances est payé à part.</p>

<h2 id="tips">Conseils et erreurs fréquentes</h2>
<ul>
<li><b>Le net de la fiche de paie n’est pas exactement l’impôt final.</b> Chaque mois, l’employeur retient un <b>précompte professionnel</b> (une avance sur l’impôt). La différence est régularisée l’année suivante.</li>
<li><b>La cotisation spéciale de sécurité sociale</b> est aussi retenue sur la fiche de paie. Elle n’est pas incluse ici.</li>
<li><b>Bas salaires</b> : le bonus à l’emploi réduit l’ONSS et l’impôt. Il n’est pas inclus, donc pour un bas salaire le net réel est plus élevé que l’estimation.</li>
<li><b>Pécule de vacances et 13e mois</b> ne sont pas comptés : ce sont des montants en plus, taxés à part.</li>
<li><b>Vérifiez votre taxe communale</b> : elle change d’une commune à l’autre et s’applique sur l’impôt, pas sur le salaire.</li>
<li><b>Enfants à charge</b> : comptez seulement ceux qui sont fiscalement à votre charge au 1er janvier de l’année qui suit.</li>
</ul>
'''+faq_block(FAQ)+'''
<p class="note">Sources (consultées le 23 novembre 2026) : <a href="https://www.dekamer.be/FLWB/PDF/56/1243/56K1243009.pdf" rel="nofollow">Chambre des représentants – Projet de loi portant réforme de l’impôt des personnes physiques, DOC 56 1243/009</a> (texte adopté, <a href="https://www.dekamer.be/FLWB/PDF/56/1243/56K1243011.pdf" rel="nofollow">DOC 56 1243/011</a>) ; <a href="https://www.socialsecurity.be/employer/instructions/dmfa/fr/2024-2/instructions/socialsecuritycontributions/contributions.html" rel="nofollow">ONSS – Instructions DmfA, les cotisations</a> ; <a href="https://fin.belgium.be/fr/particuliers/declaration-impot/revenus/taux-imposition" rel="nofollow">SPF Finances – Taux d’imposition</a> (barème indexé et frais forfaitaires : page officielle non consultable lors de notre contrôle du 23/11/2026 ; montants à confirmer sur votre avertissement-extrait de rôle). Exemples calculés avec la formule de ce calculateur. Estimation indicative.</p>'''

out=build('/be/salaire-brut-net.html','Salaire brut net Belgique 2026 – calcul ONSS, impôt et taxe communale',
 'Calculez votre salaire net en Belgique (revenus 2026) : ONSS 13,07 %, barème 25–50 %, quotité exemptée réformée, enfants et taxe communale. Exemples 2 500 à 5 000 €.',art,FAQ,form=form,calc=calc)
add_top(out,[('Par','Hong Life Calculators'),('Vérifié le','23 novembre 2026'),('Sources','Chambre, ONSS, SPF Finances')],
 [('form','Calculateur'),('figures','Chiffres 2026'),('ex','Exemples brut-net'),('how','Comment ça marche'),('tips','Conseils et erreurs'),('faq','Questions fréquentes')],'Sur cette page')
print(out)
for k,v in R.items(): print(k,[round(x,2) for x in v])
