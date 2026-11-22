import sys, json, subprocess, re; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
D='/home/claude/honglifecalc/build/pages/'
P='/es/calculadora-finiquito.html'
ENG=open(D+'mx_fin_engine.js').read(); REN=open(D+'hl_render_local.js').read()
def run(**v):
    js=("const m={exports:{}};new Function('module',"+json.dumps(ENG+'})();')+")(m);"
        "process.stdout.write(JSON.stringify(m.exports.run("+json.dumps(v)+")._n))")
    return json.loads(subprocess.check_output(['node','-e',js]))
def M(x): return '$'+f'{x:,.2f}'
UMA=117.31
base=dict(s=15000,ini='2021-06-01',fin='2026-11-22',pend=10,vacT=0,zona='gen')
r1=run(**base,tipo='ren',v20='no'); r2=run(**base,tipo='desp',v20='no'); r3=run(**base,tipo='desp',v20='si')
r4=run(s=12000,ini='2026-03-01',fin='2026-11-22',pend=0,vacT=0,tipo='ren',v20='no',zona='gen')
r5=run(s=25000,ini='2010-02-15',fin='2026-11-22',pend=0,vacT=5,tipo='ren',v20='no',zona='gen')
r6=run(s=25000,ini='2010-02-15',fin='2026-11-22',pend=0,vacT=5,tipo='desp',v20='no',zona='gen')
ex=[
 ['Renuncia, $15,000/mes, 01/06/2021 → 22/11/2026, 10 días pendientes',M(r1['pend']+r1['ag']),M(r1['vac']+r1['prima']),'—',M(r1['total'])],
 ['Despido injustificado, mismo caso (3 meses + prima de antigüedad)',M(r2['pend']+r2['ag']),M(r2['vac']+r2['prima']),M(r2['m3']+r2['pa']),M(r2['total'])],
 ['Mismo despido con 20 días por año (art. 50)',M(r3['pend']+r3['ag']),M(r3['vac']+r3['prima']),M(r3['m3']+r3['d20']+r3['pa']),M(r3['total'])],
 ['Renuncia, $12,000/mes, menos de 1 año (01/03 → 22/11/2026)',M(r4['ag']),M(r4['vac']+r4['prima']),'—',M(r4['total'])],
 ['Renuncia con 16 años, $25,000/mes, 5 días de vacaciones tomados',M(r5['ag']),M(r5['vac']+r5['prima']),M(r5['pa'])+' (prima de antigüedad, tope)',M(r5['total'])],
 ['Despido con 16 años, $25,000/mes',M(r6['ag']),M(r6['vac']+r6['prima']),M(r6['m3']+r6['pa']),M(r6['total'])]]
vac=[['1 año','12'],['2 años','14'],['3 años','16'],['4 años','18'],['5 años','20'],['6 a 10 años','22'],['11 a 15 años','24'],['16 a 20 años','26'],['21 a 25 años','28'],['26 a 30 años','30']]
FAQ=[
("¿Cómo se calcula el finiquito por renuncia en 2026?",f"Se suman el sueldo pendiente, el aguinaldo proporcional (15 días × días trabajados en el año ÷ 365), las vacaciones no gozadas y su prima vacacional (25%). Con un sueldo de $15,000 al mes, ingreso el 1 de junio de 2021 y salida el 22 de noviembre de 2026 con 10 días pendientes, el finiquito bruto es de unos {M(r1['total'])}."),
("¿Qué diferencia hay entre finiquito y liquidación?",f"El finiquito se paga siempre que termina la relación laboral. La liquidación (despido injustificado) suma además la indemnización de 3 meses de salario y la prima de antigüedad de 12 días por año; en el mismo ejemplo el total sube a {M(r2['total'])}."),
("¿Cuándo se pagan los 20 días por año?","La LFT los incluye en la indemnización del artículo 50 cuando el patrón no está obligado a reinstalar al trabajador (artículo 49) o se niega a hacerlo, y cuando el trabajador rescinde la relación por causa imputable al patrón (artículo 52). En un despido injustificado en que el trabajador demanda la indemnización (artículo 48) se pagan 3 meses de salario, no los 20 días."),
("¿Me corresponde prima de antigüedad si renuncio?",f"Sí, si tienes 15 años o más de servicio (artículo 162 LFT). Son 12 días por año, con un salario diario topado al doble del salario mínimo: $630.08 en 2026 ($881.74 en la zona libre de la frontera norte). Con 16.8 años y $25,000 al mes son unos {M(r5['pa'])}."),
("¿El finiquito paga ISR?",f"Parte está exenta (artículo 93 de la Ley del ISR): el aguinaldo hasta 30 UMA ({M(30*UMA)} en 2026), la prima vacacional hasta 15 UMA ({M(15*UMA)}) y las indemnizaciones y la prima de antigüedad hasta 90 UMA por año de servicio ({M(90*UMA)} por año). Lo que exceda paga ISR; el sueldo y las vacaciones pagadas pagan ISR normal."),
("¿Dónde pido asesoría gratis?","En la Procuraduría Federal de la Defensa del Trabajo (PROFEDET) o en el Centro Federal de Conciliación y Registro Laboral para la conciliación prejudicial, que es obligatoria antes de demandar. Para reclamar un despido tienes 2 meses (artículo 518 LFT).")]
art='''<h2>Cómo se calcula el finiquito y la liquidación en México (LFT 2026)</h2>
<p>El <b>finiquito</b> es lo que te deben al terminar la relación laboral por cualquier motivo: lo ya trabajado y las prestaciones proporcionales. La <b>liquidación</b> es el finiquito más la indemnización que corresponde cuando el despido es injustificado. La calculadora usa el salario diario = sueldo mensual ÷ 30.</p>
'''+table(['Concepto','Fórmula','Artículo LFT','Finiquito','Liquidación'],[
['Sueldo pendiente','salario diario × días no pagados','—','Sí','Sí'],
['Aguinaldo proporcional','salario diario × 15 × días trabajados en el año ÷ 365','87','Sí','Sí'],
['Vacaciones no gozadas','salario diario × días de vacaciones proporcionales desde el último aniversario','76, 79','Sí','Sí'],
['Prima vacacional','25% (mínimo) de las vacaciones','80','Sí','Sí'],
['Indemnización constitucional','90 días de salario','48, 50','—','Sí'],
['20 días por año','solo sin reinstalación o rescisión por el trabajador','49, 50, 52','—','Según el caso'],
['Prima de antigüedad','12 días por año, salario topado a 2 salarios mínimos','162, 485, 486','Con 15 años o más','Sí']])+'''
<h3>Cifras oficiales 2026</h3>
'''+table(['Dato','Valor 2026','Para qué sirve'],[
['Salario mínimo general (desde el 1 de enero)','$315.04 diarios','Tope de la prima de antigüedad: $630.08'],
['Salario mínimo, zona libre de la frontera norte','$440.87 diarios','Tope de la prima de antigüedad: $881.74'],
['UMA (desde el 1 de febrero de 2026)',f'{M(UMA)} diarios ($3,566.22 mensual, $42,794.64 anual)','Exenciones de ISR: aguinaldo 30 UMA, prima vacacional 15 UMA, indemnizaciones 90 UMA por año'],
['Aguinaldo mínimo','15 días de salario','Se paga antes del 20 de diciembre'],
['Prima vacacional mínima','25%','Sobre el salario de los días de vacaciones']])+'''
<h3>Días de vacaciones por antigüedad (reforma "vacaciones dignas")</h3>
'''+table(['Años de servicio','Días de vacaciones'],vac)+'''
<h3>Ejemplos calculados con esta calculadora</h3>
'''+table(['Caso','Sueldo pendiente + aguinaldo','Vacaciones + prima vacacional','Indemnizaciones','Total bruto'],ex)+'''
<p class="note">Montos brutos antes de ISR. En los ejemplos de 16 años el salario diario ($833.33) supera el doble del salario mínimo, por lo que la prima de antigüedad se calcula con $630.08.</p>
<h3>Consejos y errores comunes</h3>
<ul><li><b>Salario integrado.</b> Las indemnizaciones (3 meses, 20 días y prima de antigüedad) se calculan legalmente con salario integrado (artículos 84 y 89), que incluye la parte proporcional de aguinaldo, prima vacacional y otras prestaciones; por eso el monto real suele ser algo mayor que el de esta calculadora.</li>
<li><b>Salarios caídos.</b> Si demandas y ganas, además se pagan salarios caídos hasta por 12 meses; después corren intereses del 2% mensual (artículo 48).</li>
<li><b>No firmes en blanco.</b> Revisa que el recibo de finiquito desglose cada concepto antes de firmarlo; la renuncia debe ser voluntaria.</li>
<li><b>Plazos.</b> Para reclamar un despido tienes 2 meses (artículo 518); primero se acude a la conciliación ante el Centro Federal de Conciliación y Registro Laboral o el centro local.</li>
<li><b>Aguinaldo y vacaciones del año en curso.</b> Si ya te pagaron parte del aguinaldo o tomaste vacaciones, réstalo (la calculadora tiene un campo para los días ya tomados).</li></ul>
'''+faq_html(FAQ,'Preguntas frecuentes')+'''
<p class="note">Fuentes (consultadas el 22 de noviembre de 2026): <a href="https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf" rel="nofollow">Ley Federal del Trabajo</a> (arts. 48–52, 76, 80, 84, 87, 89, 162, 485–486, 518) y <a href="https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf" rel="nofollow">Ley del ISR</a> (art. 93), Cámara de Diputados; <a href="https://sidof.segob.gob.mx/notas/docFuente/5775534" rel="nofollow">Resolución de la CONASAMI (DOF) — salarios mínimos 2026</a>; <a href="https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/uma/uma2026.pdf" rel="nofollow">INEGI — UMA 2026</a>. Estimación informativa, no asesoría legal.</p>'''
html_engine='<script>\n'+ENG+REN+'build(spec);\n})();\n</script>'
out=build(P,'Calculadora de Finiquito y Liquidación 2026 (México, LFT)',
 'Calcula tu finiquito o liquidación 2026 según la LFT: sueldo pendiente, aguinaldo, vacaciones y prima vacacional, 3 meses, 20 días por año y prima de antigüedad.',art,FAQ)
s=open(out,encoding='utf-8').read()
s=re.sub(r'<section class="card help">.*?</section>\n','',s,count=1,flags=re.S)
s=s.replace('data-calc="finiquito"','data-calc-local="finiquito"',1)
s=s.replace('<script src="../g.js"></script>','<script src="../g.js"></script>'+html_engine,1)
assert 'data-calc-local' in s and 'vacDays' in s and s.count('card help')==1
open(out,'w',encoding='utf-8').write(s); print(out)
