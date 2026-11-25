import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/fr/calcul-objectif-epargne.html'
CHK='25 novembre 2026'
LA=2.0  # taux d'exemple
LAs=f"{LA:g}".replace('.',',')

form=f'''<form class="card" id="form" onsubmit="return false"><h2>Vos données</h2><label class="f"><span>Objectif d’épargne (€)</span><input id="T" inputmode="decimal" value="18 000"></label><label class="f"><span>Déjà épargné (€)</span><input id="C" inputmode="decimal" value="1 800"></label><label class="f"><span>Durée (années)</span><input id="y" inputmode="decimal" value="3"><small>Pour 18 mois, tapez 1,5.</small></label><label class="f"><span>Taux de rémunération (% par an)</span><input id="r" inputmode="decimal" value="{LAs}"><small>Exemple – utilisez le taux de votre placement. Mettez 0 si votre compte ne rapporte rien.</small></label></form>'''

calc='''function calc(){const T=num('T'),C=num('C'),i=num('r')/1200,n=Math.round(num('y')*12);
 const nt='<p class="note">Versement à la fin de chaque mois, intérêts ajoutés chaque mois à taux constant, sans impôt.</p>';
 if(n<1)return big(O.need,'–','Indiquez une durée d’au moins 1 mois (0,1 an)');
 const g=Math.pow(1+i,n),grow=C*g;
 if(grow>=T)return big('Objectif déjà atteint',mf(0,0),'avec votre épargne actuelle')+kv([['Votre épargne actuelle devient',mf(grow,0)],['Intérêts gagnés',mf(grow-C,0),'pos'],['Mois',String(n)]])+nt;
 const need=i?(T-grow)*i/(g-1):(T-C)/n,dep=need*n;
 return big(O.need,mf(need,need<100?2:0),O.per)+kv([['Soit par semaine (environ)',mf(need*12/52,2)],[O.tot,mf(dep,0)],['Déjà épargné',mf(C,0)],[O.int,mf(Math.max(0,T-C-dep),0),'pos'],['Mois',String(n)]])+nt}'''

def need(T,C,y,r):
    i=r/1200;n=round(y*12);g=(1+i)**n
    if C*g>=T: return 0
    return (T-C*g)*i/(g-1) if i else (T-C)/n
e=lambda x:f"{x:,.0f} €".replace(',',' ')
rows=[]
for T,y,lab in [(3000,1,'3 000 € (vacances)'),(5000,1,'5 000 €'),(10000,2,'10 000 €'),(20000,5,'20 000 € (apport immobilier)')]:
    a=[need(T,0,y,r) for r in (0,LA,3)]
    rows.append([lab,f"{y} an{'s' if y>1 else ''}",e(a[0]),e(a[1]),e(a[2]),e(T-a[1]*y*12)])
d=need(18000,1800,3,LA)
print(rows, round(d,2))
D=e(d)


FAQ=[
("Combien épargner par mois pour atteindre mon objectif ?","Divisez ce qu’il vous manque par le nombre de mois. Pour 10 000 € en 2 ans en partant de zéro : 10 000 € ÷ 24 = 417 € par mois sans intérêts. Avec un placement à "+LAs+" % par an, il faut "+e(need(10000,0,2,LA))+" par mois."),
("Combien faut-il de temps pour économiser 10 000 € ?","À 300 € par mois, il faut un peu moins de 3 ans (34 mois sans intérêts). À 500 € par mois, il faut 20 mois. Des intérêts raccourcissent un peu ce délai."),
("Combien épargner pour un apport immobilier de 20 000 € ?","En 5 ans, il faut 333 € par mois sans intérêts, ou "+e(need(20000,0,5,LA))+" par mois à "+LAs+" %. Les intérêts apportent alors environ "+e(20000-need(20000,0,5,LA)*60)+"."),
("Les intérêts changent-ils beaucoup le résultat ?","Sur une courte durée, peu. Pour 5 000 € en 1 an, on passe de 417 € à "+e(need(5000,0,1,LA))+" par mois à "+LAs+" %. Sur 5 ans ou plus, l’écart grandit, car les intérêts produisent eux-mêmes des intérêts."),
("Que faire si j’ai déjà une partie de la somme ?","Indiquez-la dans « Déjà épargné ». Elle rapporte aussi des intérêts, donc il vous faut moins chaque mois. Avec 1 800 € déjà épargnés, 18 000 € en 3 ans demandent "+D+" par mois à "+LAs+" %."),
("Combien épargner par semaine ?","Multipliez le montant mensuel par 12, puis divisez par 52. 417 € par mois font environ 96 € par semaine. Le calculateur affiche aussi ce montant."),
]

art=f'''<h2 id="ex">Combien épargner par mois : exemples</h2>
<div id="examples">'''+table(['Objectif','Durée','Par mois sans intérêts',f'Par mois à {LAs} %','Par mois à 3 %',f'Intérêts gagnés à {LAs} %'],rows)+f'''</div>
<ul><li>Pour <b>5 000 € en 1 an</b>, il faut environ 417 € par mois. À {LAs} %, c’est {e(need(5000,0,1,LA))}.</li>
<li>Pour <b>20 000 € en 5 ans</b>, comptez {e(need(20000,0,5,LA))} par mois à {LAs} %. Les intérêts font une partie du chemin.</li>
<li>Tous les exemples partent de 0 € et utilisent la formule de ce calculateur. {LAs} % et 3 % sont des exemples, pas des offres bancaires.</li></ul>
<h2 id="how">Comment fonctionne le calcul</h2>
<p>D’abord un exemple. Vous voulez 18 000 € dans 3 ans. Vous avez déjà 1 800 €, placés à {LAs} % par an. Ces 1 800 € grandissent seuls jusqu’à environ {e(1800*(1+LA/1200)**36)}. Il vous manque le reste. En versant <b>{D} par mois</b>, vous y arrivez, car vos versements rapportent aussi des intérêts.</p>
<ul><li><b>Taux mensuel</b> = taux annuel ÷ 12. Ainsi {LAs} % par an font environ {LA/12:.3f} % par mois.</li>
<li><b>Intérêts composés</b> : vous gagnez aussi des intérêts sur les intérêts déjà gagnés.</li>
<li><b>Ce qu’il manque</b> = objectif − ce que votre épargne actuelle va devenir.</li>
<li><b>Versement mensuel</b> = ce qu’il manque × i ÷ ((1 + i)<sup>n</sup> − 1), avec i le taux mensuel et n le nombre de mois.</li></ul>
<p>Sans intérêts, c’est simplement (objectif − déjà épargné) ÷ nombre de mois. Votre banque peut calculer les intérêts autrement : le résultat réel peut différer de quelques euros.</p>
<h2 id="tips">Conseils et erreurs fréquentes</h2>
<ul><li><b>Programmez un virement automatique</b> le jour de la paie. L’argent part avant que vous ne le dépensiez.</li>
<li><b>Vérifiez le vrai taux.</b> Certains taux promotionnels ne durent que quelques mois. Entrez le taux que vous aurez vraiment.</li>
<li><b>Gardez une épargne de précaution</b> à part, pour que les imprévus ne cassent pas votre objectif.</li>
<li><b>Revoyez votre plan chaque année.</b> Si le taux change, relancez le calcul.</li></ul>
<h2 id="faq" style="margin-top:22px">Questions fréquentes sur l’épargne</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+f'''
<p class="note">Mis à jour le {CHK}. Exemples calculés avec la formule de ce calculateur. Les taux utilisés sont des exemples. Information générale, pas un conseil financier.</p>'''

out=build(P,'Objectif d’épargne 2026 – Combien épargner par mois ?',
 'Calculez combien épargner chaque mois ou chaque semaine pour atteindre un objectif d’épargne, avec les intérêts. Exemples chiffrés et FAQ.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Par','Hong Life Calculators'),('Mis à jour le','25 novembre 2026'),('Méthode','intérêts composés mensuels')],
 [('form','Calculateur'),('ex','Exemples'),('how','Comment ça marche'),('tips','Conseils'),('faq','FAQ')],'Sur cette page',('#examples','fr'))
print(out)
