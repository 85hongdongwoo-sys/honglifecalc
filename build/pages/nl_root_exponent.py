import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/nl/root-exponent-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><div class="pr" style="border:0;margin:0;padding:0"><h3>√ Vereenvoudigd</h3><div class="row2"><span>√</span><input id="sq" inputmode="decimal" value="72" aria-label="Getal onder het wortelteken"></div><small class="f">Voorbeeld: 72 → 6√2</small></div><div class="pr"><h3>ⁿ√ n-de machtswortel</h3><div class="row2"><input id="rn" inputmode="decimal" value="3" aria-label="Wortelexponent (n)" style="max-width:80px"><span>√</span><input id="rx" inputmode="decimal" value="27" aria-label="Getal"></div><small class="f">Eerst de wortelexponent (3 = derdemachtswortel), dan het getal.</small></div><div class="pr"><h3>xⁿ Macht</h3><div class="row2"><input id="pb" inputmode="decimal" value="2" aria-label="Grondtal"><span>^</span><input id="pe" value="10" aria-label="Exponent"></div><small class="f">De exponent mag een breuk zijn: typ 2/3 voor 8^(2/3).</small></div><div class="pr"><h3>log<sub>b</sub>(x) Logaritme</h3><div class="row2"><span>log</span><input id="lb" value="2" aria-label="Grondtal" style="max-width:80px"><span>(</span><input id="lx" inputmode="decimal" value="8" aria-label="Getal"><span>)</span></div><small class="f">Grondtal 10 = gewone logaritme; typ e voor de natuurlijke logaritme (ln).</small></div></form>'''

calc='''function calc(){const rows=[];
  const x=P($('sq').value);
  if(isFinite(x)){if(x<0)rows.push(['√'+F(x),'— (niet reëel)']);else if(Number.isInteger(x)&&x<=1e12){const [o,r]=sqs(x);rows.push(['√'+F(x),(r==1?F(o):(o==1?'√'+r:F(o)+'√'+r))+(r==1?'':' ≈ '+F(Math.sqrt(x))),'t'])}else rows.push(['√'+F(x),F(Math.sqrt(x)),'t'])}
  const n=P($('rn').value),rx=P($('rx').value);
  if(isFinite(n)&&n!=0&&isFinite(rx)){let v=rx<0?(Number.isInteger(n)&&n%2!=0?-Math.pow(-rx,1/n):NaN):Math.pow(rx,1/n);rows.push(['<sup>'+F(n)+'</sup>√'+F(rx),isFinite(v)?F(v):'— (niet reëel)','t'])}
  const b=P($('pb').value),pe=ex($('pe').value);
  if(isFinite(b)&&isFinite(pe)){let v=Math.pow(b,pe);const m=/^\\s*(-?\\d+)\\s*\\/\\s*(\\d+)\\s*$/.exec($('pe').value);if(b<0&&m&&+m[2]%2==1)v=Math.sign(Math.pow(-1,+m[1]))*Math.pow(-b,pe);rows.push([F(b)+'^'+$('pe').value.trim(),isFinite(v)?F(v):'— (niet reëel)','t'])}
  const lb=$('lb').value.trim().toLowerCase()=='e'?Math.E:ex($('lb').value),lx=ex($('lx').value);
  if(isFinite(lb)&&isFinite(lx)&&lb>0&&lb!=1&&lx>0)rows.push(['log'+($('lb').value.trim().toLowerCase()=='e'?'e':F(lb))+'('+F(lx)+')',F(Math.log(lx)/Math.log(lb)),'t']);
  const r0=rows.length?String(rows[0][1]):'—';return big(L.res,r0.startsWith('—')?'—':r0,r0.startsWith('— ')?'Geen reëel getal':'')+kv(rows)}'''

R=lambda *a:list(a)
ex_sq=[R('√12','√(4 × 3)','2√3','3,4641'),R('√18','√(9 × 2)','3√2','4,2426'),R('√48','√(16 × 3)','4√3','6,9282'),
       R('√50','√(25 × 2)','5√2','7,0711'),R('√72','√(36 × 2)','6√2','8,4853'),R('√200','√(100 × 2)','10√2','14,1421')]
ex_mix=[R('Derdemachtswortel','∛64','4 × 4 × 4 = 64','4'),R('Vierdemachtswortel','⁴√81','3 × 3 × 3 × 3 = 81','3'),
        R('Gebroken exponent','8^(2/3)','(∛8)² = 2²','4'),R('Gebroken exponent','16^(3/4)','(⁴√16)³ = 2³','8'),
        R('Negatieve exponent','2^(−3)','1 ÷ 2³ = 1 ÷ 8','0,125'),R('Logaritme','²log(1024)','2^10 = 1024','10'),
        R('Logaritme','³log(81)','3^4 = 81','4'),R('Gewone logaritme','log(1000)','10³ = 1000','3')]

FAQ=[
("Hoe vereenvoudig je een wortel?","Zoek het grootste kwadraat dat in het getal past en haal het buiten de wortel. Voorbeeld: 72 = 36 × 2 en √36 = 6, dus √72 = 6√2 (≈ 8,4853)."),
("Wat is de wortel van 2?","√2 ≈ 1,4142. De decimalen houden nooit op en herhalen zich niet: √2 is een irrationaal getal. Daarom laat je √72 als exacte uitkomst staan als 6√2."),
("Wat betekent een gebroken exponent zoals 8^(2/3)?","Het getal onder de breukstreep is de wortel, het getal erboven de macht. 8^(2/3) = (∛8)² = 2² = 4. Typ in de rekenmachine 2/3 bij de exponent."),
("Wat doet een negatieve exponent?","Je neemt het omgekeerde: 2^(−3) = 1 ÷ 2³ = 1 ÷ 8 = 0,125. Een negatieve exponent maakt de uitkomst dus niet negatief."),
("Bestaat de wortel uit een negatief getal?","Niet binnen de reële getallen, want elk getal keer zichzelf is positief. De derdemachtswortel bestaat wel: ∛(−8) = −2, want (−2)³ = −8."),
("Wat is een logaritme, simpel uitgelegd?","Het is de vraag: tot welke macht moet ik het grondtal verheffen? ²log(8) = 3, want 2³ = 8. En log(1000) = 3, want 10³ = 1000."),
("Wat is een getal tot de macht 0?","Altijd 1 (behalve 0^0). Bijvoorbeeld 5^0 = 1. Dat komt van delen: 2³ ÷ 2³ = 2^(3−3) = 2^0 = 1."),
]

art='''<h2 id="ex">Voorbeelden: wortels vereenvoudigen</h2>
<div id="examples">'''+table(['Wortel','Splits in','Vereenvoudigd','Decimaal'],ex_sq)+'''</div>
<p class="note">Afgerond op 4 decimalen. Alle uitkomsten komen uit deze rekenmachine.</p>
<h2 id="meer">Meer voorbeelden: wortels, machten en logaritmen</h2>
'''+table(['Soort','Som','Waarom','Uitkomst'],ex_mix)+'''
<h2 id="stappen">Stap voor stap</h2>
<ul><li><b>√72.</b> 72 = 36 × 2. Omdat √36 = 6, krijg je <b>6√2</b>. Als decimaal: 6 × 1,4142 ≈ 8,4853.</li>
<li><b>∛27.</b> Welk getal drie keer met zichzelf vermenigvuldigd geeft 27? 3 × 3 × 3 = 27. Uitkomst: <b>3</b>.</li>
<li><b>8^(2/3).</b> Eerst de derdemachtswortel van 8: dat is 2. Dan kwadrateren: 2² = <b>4</b>.</li>
<li><b>²log(8).</b> Hoe vaak vermenigvuldig je 2 om bij 8 te komen? 2 × 2 × 2 = 8, dus 3 keer. Uitkomst: <b>3</b>.</li></ul>
<h2 id="uitleg">Zo werkt het (eenvoudig uitgelegd)</h2>
<ul><li><b>Macht</b> = een getal een aantal keer met zichzelf vermenigvuldigen. 2^10 = 2 × 2 × … × 2 (10 keer) = 1024. Het grote getal heet het <b>grondtal</b>, het kleine getal erboven de <b>exponent</b>.</li>
<li><b>Wortel</b> = het omgekeerde van een macht. √9 = 3, want 3² = 9. Het kleine getal bij de wortel heet de <b>wortelexponent</b>: 2 is de vierkantswortel (die schrijf je niet), 3 de derdemachtswortel.</li>
<li><b>Kwadraat</b> = een getal keer zichzelf: 4, 9, 16, 25, 36, 49, 64, 81, 100 …</li>
<li><b>Vereenvoudigen</b> = het grootste kwadraat buiten de wortel halen: √(a² × b) = a√b.</li>
<li><b>Gebroken exponent</b>: x^(m/n) = (ⁿ√x)^m. De noemer is de wortelexponent.</li>
<li><b>Logaritme</b>: <sup>b</sup>log(x) = y betekent b^y = x. De rekenmachine rekent log(x) ÷ log(b), zo werkt elk grondtal.</li></ul>
<h2 id="fouten">Veelgemaakte fouten</h2>
<ul><li><b>√(a + b) is niet √a + √b.</b> √(9 + 16) = √25 = 5, maar √9 + √16 = 3 + 4 = 7.</li>
<li><b>Niet het grootste kwadraat nemen.</b> √72 = 2√18 klopt, maar is niet af: in 18 zit nog een 9. Het eindantwoord is 6√2.</li>
<li><b>−3² en (−3)² door elkaar halen.</b> −3² = −9, maar (−3)² = 9. Zet het minteken in het grondtal.</li>
<li><b>Komma of punt?</b> Beide werken: 2,5 en 2.5 geven hetzelfde.</li></ul>
<h2 id="faq" style="margin-top:22px">Veelgestelde vragen</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Gecontroleerd op 25 november 2026. De voorbeelden zijn berekend met de formule van deze rekenmachine en met de hand nagerekend. Alleen uitkomsten in de reële getallen (geen complexe getallen).</p>'''

out=build(P,'Wortel- en machtrekenmachine – wortel vereenvoudigen, macht, log',
 'Vereenvoudig wortels (√72 = 6√2), bereken derdemachtswortels, machten met een gebroken of negatieve exponent en logaritmen. Met stap-voor-stap voorbeelden.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Door','Hong Life Calculators'),('Gecontroleerd','25 november 2026'),('Methode','formule van deze rekenmachine')],
 [('form','Rekenmachine'),('ex','Wortels vereenvoudigen'),('meer','Machten en logaritmen'),('stappen','Stap voor stap'),('uitleg','Zo werkt het'),('fouten','Veelgemaakte fouten'),('faq','Veelgestelde vragen')],'Op deze pagina',('#examples','nl'))
print(out)
