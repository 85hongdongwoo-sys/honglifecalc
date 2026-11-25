import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/es/root-exponent-calculator.html'

form='''<form class="card" id="form" onsubmit="return false"><div class="pr" style="border:0;margin:0;padding:0"><h3>√ Simplificada</h3><div class="row2"><span>√</span><input id="sq" inputmode="decimal" value="72" aria-label="Número dentro de la raíz cuadrada"></div><small class="f">Ejemplo: 72 → 6√2</small></div><div class="pr"><h3>ⁿ√ Raíz n-ésima</h3><div class="row2"><input id="rn" inputmode="decimal" value="3" aria-label="Índice (n)" style="max-width:80px"><span>√</span><input id="rx" inputmode="decimal" value="27" aria-label="Número"></div><small class="f">Primero el índice (3 = raíz cúbica), luego el número.</small></div><div class="pr"><h3>xⁿ Potencia</h3><div class="row2"><input id="pb" inputmode="decimal" value="2" aria-label="Base"><span>^</span><input id="pe" value="10" aria-label="Exponente"></div><small class="f">El exponente admite fracciones: escribe 2/3 para 8^(2/3).</small></div><div class="pr"><h3>log<sub>b</sub>(x) Logaritmo</h3><div class="row2"><span>log</span><input id="lb" value="2" aria-label="Base" style="max-width:80px"><span>(</span><input id="lx" inputmode="decimal" value="8" aria-label="Número"><span>)</span></div><small class="f">Base 10 = logaritmo decimal; escribe e para el neperiano (ln).</small></div></form>'''

calc='''function calc(){const rows=[];
  const x=P($('sq').value);
  if(isFinite(x)){if(x<0)rows.push(['√'+F(x),'— (no real)']);else if(Number.isInteger(x)&&x<=1e12){const [o,r]=sqs(x);rows.push(['√'+F(x),(r==1?F(o):(o==1?'√'+r:F(o)+'√'+r))+(r==1?'':' ≈ '+F(Math.sqrt(x))),'t'])}else rows.push(['√'+F(x),F(Math.sqrt(x)),'t'])}
  const n=P($('rn').value),rx=P($('rx').value);
  if(isFinite(n)&&n!=0&&isFinite(rx)){let v=rx<0?(Number.isInteger(n)&&n%2!=0?-Math.pow(-rx,1/n):NaN):Math.pow(rx,1/n);rows.push(['<sup>'+F(n)+'</sup>√'+F(rx),isFinite(v)?F(v):'— (no real)','t'])}
  const b=P($('pb').value),pe=ex($('pe').value);
  if(isFinite(b)&&isFinite(pe)){let v=Math.pow(b,pe);const m=/^\\s*(-?\\d+)\\s*\\/\\s*(\\d+)\\s*$/.exec($('pe').value);if(b<0&&m&&+m[2]%2==1)v=Math.sign(Math.pow(-1,+m[1]))*Math.pow(-b,pe);rows.push([F(b)+'^'+$('pe').value.trim(),isFinite(v)?F(v):'— (no real)','t'])}
  const lb=$('lb').value.trim().toLowerCase()=='e'?Math.E:ex($('lb').value),lx=ex($('lx').value);
  if(isFinite(lb)&&isFinite(lx)&&lb>0&&lb!=1&&lx>0)rows.push(['log'+($('lb').value.trim().toLowerCase()=='e'?'e':F(lb))+'('+F(lx)+')',F(Math.log(lx)/Math.log(lb)),'t']);
  const r0=rows.length?String(rows[0][1]):'—';return big(L.res,r0.startsWith('—')?'—':r0,r0.startsWith('— ')?'No es un número real':'')+kv(rows)}'''

R=lambda *a:list(a)
ex_sq=[R('√12','√(4 × 3)','2√3','3,4641'),R('√18','√(9 × 2)','3√2','4,2426'),R('√48','√(16 × 3)','4√3','6,9282'),
       R('√50','√(25 × 2)','5√2','7,0711'),R('√72','√(36 × 2)','6√2','8,4853'),R('√200','√(100 × 2)','10√2','14,1421')]
ex_mix=[R('Raíz cúbica','∛64','4 × 4 × 4 = 64','4'),R('Raíz cuarta','⁴√81','3 × 3 × 3 × 3 = 81','3'),
        R('Exponente fraccionario','8^(2/3)','(∛8)² = 2² ','4'),R('Exponente fraccionario','16^(3/4)','(⁴√16)³ = 2³','8'),
        R('Exponente negativo','2^(−3)','1 ÷ 2³ = 1 ÷ 8','0,125'),R('Logaritmo','log₂(1024)','2^10 = 1024','10'),
        R('Logaritmo','log₃(81)','3^4 = 81','4'),R('Logaritmo decimal','log₁₀(1000)','10³ = 1000','3')]

FAQ=[
("¿Cómo se simplifica una raíz cuadrada?","Busca el cuadrado perfecto más grande que divide al número y sácalo fuera de la raíz. Ejemplo: 72 = 36 × 2, y √36 = 6, así que √72 = 6√2 (≈ 8,4853)."),
("¿Cuánto es la raíz cuadrada de 2?","√2 ≈ 1,4142. No tiene decimales que se repitan ni terminen: es un número irracional. Por eso √72 se deja como 6√2 cuando se pide el resultado exacto."),
("¿Qué significa un exponente fraccionario como 8^(2/3)?","El número de abajo de la fracción es la raíz y el de arriba es la potencia. 8^(2/3) = (∛8)² = 2² = 4. En la calculadora escribe 2/3 en el exponente."),
("¿Qué pasa con un exponente negativo?","Da la vuelta al número: 2^(−3) = 1 ÷ 2³ = 1 ÷ 8 = 0,125. Un exponente negativo nunca hace el resultado negativo."),
("¿Existe la raíz cuadrada de un número negativo?","No en los números reales, porque cualquier número multiplicado por sí mismo da positivo. Sí existe la raíz cúbica de un negativo: ∛(−8) = −2, porque (−2)³ = −8."),
("¿Qué es un logaritmo, explicado fácil?","Es la pregunta «¿a qué número tengo que elevar la base?». log₂(8) = 3 porque 2³ = 8. log₁₀(1000) = 3 porque 10³ = 1000."),
("¿Cuánto es cualquier número elevado a 0?","Es 1 (por ejemplo 5^0 = 1 y 2^0 = 1). Viene de dividir un número entre sí mismo: 2³ ÷ 2³ = 2^(3−3) = 2^0 = 1."),
]

art='''<h2 id="ex">Ejemplos de raíces cuadradas simplificadas</h2>
<div id="examples">'''+table(['Raíz','Se separa en','Forma simplificada','Valor decimal'],ex_sq)+'''</div>
<p class="note">Valores redondeados a 4 decimales. Todos los resultados salen de esta misma calculadora.</p>
<h2 id="mas">Más ejemplos: raíces, potencias y logaritmos</h2>
'''+table(['Tipo','Operación','Por qué','Resultado'],ex_mix)+'''
<h2 id="pasos">Ejemplos paso a paso</h2>
<ul><li><b>√72.</b> 72 = 36 × 2. Como √36 = 6, queda <b>6√2</b>. En decimal: 6 × 1,4142 ≈ 8,4853.</li>
<li><b>∛27.</b> Buscamos un número que, multiplicado tres veces, dé 27: 3 × 3 × 3 = 27. Resultado: <b>3</b>.</li>
<li><b>8^(2/3).</b> Primero la raíz cúbica de 8, que es 2. Luego al cuadrado: 2² = <b>4</b>.</li>
<li><b>log₂(8).</b> ¿Cuántas veces multiplico 2 para llegar a 8? 2 × 2 × 2 = 8, o sea 3 veces. Resultado: <b>3</b>.</li></ul>
<h2 id="como">Cómo funciona (explicado fácil)</h2>
<ul><li><b>Potencia</b> = multiplicar un número por sí mismo varias veces. 2^10 = 2 × 2 × … × 2 (10 veces) = 1024. El número de abajo es la <b>base</b> y el pequeño de arriba es el <b>exponente</b>.</li>
<li><b>Raíz</b> = la operación contraria a la potencia. √9 = 3 porque 3² = 9. El número pequeño de la raíz se llama <b>índice</b>: 2 es raíz cuadrada (no se escribe), 3 es raíz cúbica.</li>
<li><b>Cuadrado perfecto</b> = número que es otro número al cuadrado: 4, 9, 16, 25, 36, 49, 64, 81, 100…</li>
<li><b>Simplificar</b> = sacar fuera de la raíz el cuadrado perfecto más grande: √(a² × b) = a√b.</li>
<li><b>Exponente fraccionario</b>: x^(m/n) = (ⁿ√x)^m. El denominador es el índice de la raíz.</li>
<li><b>Logaritmo</b>: log<sub>b</sub>(x) = y significa b^y = x. La calculadora usa log(x) ÷ log(b), así sirve con cualquier base.</li></ul>
<h2 id="errores">Errores frecuentes</h2>
<ul><li><b>√(a + b) no es √a + √b.</b> √(9 + 16) = √25 = 5, pero √9 + √16 = 3 + 4 = 7.</li>
<li><b>Sacar un cuadrado que no es el mayor.</b> √72 = 2√18 es correcto, pero no está simplificado: 18 todavía tiene un 9 dentro. La forma final es 6√2.</li>
<li><b>Confundir −3² con (−3)².</b> −3² = −9, pero (−3)² = 9. En la calculadora, pon el signo dentro de la base.</li>
<li><b>Escribir la coma decimal.</b> Puedes usar coma o punto: 2,5 y 2.5 dan lo mismo.</li></ul>
<h2 id="faq" style="margin-top:22px">Preguntas frecuentes</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Revisado el 25 de noviembre de 2026. Los ejemplos se calcularon con la fórmula de esta calculadora y se comprobaron multiplicando a mano. Solo da resultados en los números reales (sin números complejos).</p>'''

out=build(P,'Calculadora de raíces, potencias y logaritmos – Simplificar √',
 'Simplifica raíces cuadradas (√72 = 6√2), calcula raíces cúbicas, potencias con exponente fraccionario o negativo y logaritmos. Con ejemplos paso a paso.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Por','Hong Life Calculators'),('Revisado','25 de noviembre de 2026'),('Método','fórmula de la propia calculadora')],
 [('form','Calculadora'),('ex','Raíces simplificadas'),('mas','Potencias y logaritmos'),('pasos','Paso a paso'),('como','Cómo funciona'),('errores','Errores frecuentes'),('faq','Preguntas frecuentes')],'En esta página',('#examples','es'))
print(out)
