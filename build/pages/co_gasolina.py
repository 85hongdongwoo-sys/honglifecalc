import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/co/calculadora-gasto-gasolina.html'

GAL=3.785411784          # US gallon in litres (exact definition)
PRICE=16000              # example price per gallon used in examples (not an official quote)
OFFICIAL=None            # e.g. ('gasolina corriente, Bogotá, noviembre de 2026', 16xxx, 'url') once verified

form='''<form class="card" id="form" onsubmit="return false"><h2>Tus datos</h2><label class="f"><span>Distancia (km)</span><input id="dist" inputmode="decimal" value="500"><small>Solo ida. Marca «ida y vuelta» abajo para duplicarla.</small></label><label class="f"><span>Unidad de rendimiento</span><select id="cu"><option value="kmg" selected>Kilómetros por galón (km/gal)</option><option value="l100">Litros por cada 100 km (L/100 km)</option></select></label><label class="f"><span>Rendimiento del vehículo</span><input id="cons" inputmode="decimal" value="40"><small>Ejemplo: un carro pequeño hace unos 40–50 km por galón en carretera. Mira el dato de tu vehículo.</small></label><label class="f"><span>Precio por galón ($)</span><input id="fp" inputmode="decimal" value="16.000"><small>El precio cambia por ciudad y mes. Usa el de tu estación.</small></label><label class="f"><span>Peajes del viaje ($, opcional)</span><input id="toll" inputmode="decimal" value="0"></label><label class="f"><span>Personas que comparten</span><input id="ppl" inputmode="decimal" value="2"></label><label class="chk"><input type="checkbox" id="rt"> Ida y vuelta</label></form>'''

calc='''function calc(){const GAL=3.785411784,d=Math.max(0,num('dist'))*($('rt').checked?2:1),cv=Math.max(0,num('cons')),u=$('cu').value,p=Math.max(0,num('fp')),toll=Math.max(0,num('toll')),n=Math.max(1,Math.round(num('ppl')));
 if(!d||!cv)return big('Costo de la gasolina',mf2(0),'Introduce la distancia y el rendimiento');
 const g=u==='kmg'?d/cv:d*cv/100/GAL,c=g*p,t=c+toll;
 return big('Costo de la gasolina',mf2(c),O.pp+': '+mf2(t/n))+kv([[O.vol,nn(g,2)+' galones ('+nn(g*GAL,1)+' litros)'],['Distancia total',nn(d,0)+' km'],['Costo por kilómetro',mf2(c/d)],['Peajes',mf2(toll)],['Total con peajes',mf2(t),'t'],[O.pp+' ('+n+')',mf2(t/n)]])+'<p class="note">1 galón = 3,785 litros. El rendimiento real baja con tráfico, aire acondicionado, carga y subidas.</p>'}'''

def gals(d,cv,u='kmg'): return d/cv if u=='kmg' else d*cv/100/GAL
cop=lambda x:'$'+f"{round(x):,}".replace(',','.')
rows=[]
for d,cv,lab in [(100,40,'Viaje corto'),(300,40,'Fin de semana'),(500,45,'Viaje largo'),(500,30,'Camioneta, viaje largo')]:
    g=gals(d,cv);c=g*PRICE
    rows.append([lab,f"{d} km",f"{cv} km/gal",f"{g:.1f}".replace('.',','),cop(c),cop(c/2)])
print(rows)
dflt=gals(500,40)*PRICE; print(dflt)
l100=gals(500,7,'l100'); print(l100, l100*PRICE)
rt=gals(1000,40)*PRICE; print(rt)

fig=[['1 galón (EE. UU.)','3,785 litros','En Colombia la gasolina se vende por galón.'],
     ['Rendimiento en km/gal → L/100 km','L/100 km = 378,5 ÷ km/gal','Ejemplo: 40 km/gal ≈ 9,5 L/100 km.'],
     ['Litros → galones','galones = litros ÷ 3,785','Ejemplo: 40 litros ≈ 10,6 galones.']]
if OFFICIAL:
    fig.insert(0,['Precio de referencia: '+OFFICIAL[0],cop(OFFICIAL[1])+' por galón','Precio regulado por el Gobierno. Cambia según la ciudad.'])

FAQ=[
("¿Cómo calculo la gasolina que gasta mi carro en un viaje?","Divide los kilómetros entre el rendimiento en km por galón. Luego multiplica por el precio del galón. Ejemplo: 500 km ÷ 40 km/gal = 12,5 galones. Con el galón a $16.000, son $200.000."),
("¿Cuántos galones necesito para 100 km?","Depende del carro. A 40 km por galón necesitas 2,5 galones. A 30 km por galón necesitas unos 3,3 galones."),
("¿Cómo paso de L/100 km a km por galón?","Divide 378,5 entre los litros por 100 km. Ejemplo: 7 L/100 km ≈ 54 km por galón. Y al revés: 378,5 ÷ 40 km/gal ≈ 9,5 L/100 km."),
("¿Cuánto cuesta un viaje de ida y vuelta?","Duplica la distancia. 500 km de ida y vuelta son 1.000 km. A 40 km/gal y $16.000 el galón, son $400.000 de gasolina, sin peajes."),
("¿Cómo divido la gasolina entre los pasajeros?","Suma gasolina y peajes, y divide entre el número de personas. Ejemplo: $200.000 de gasolina y $60.000 de peajes entre 4 personas = $65.000 cada una."),
("¿Por qué mi carro gasta más de lo que dice la ficha?","El dato de fábrica se mide en condiciones ideales. El tráfico, el aire acondicionado, la carga, la velocidad alta y las subidas aumentan el consumo."),
]

art='''<h2 id="figures">Datos útiles para calcular</h2>
'''+table(['Dato','Valor','Para qué sirve'],fig)+'''
<p class="note">Según el Ministerio de Minas y Energía (comunicado del 30 de octubre de 2026), en noviembre de 2026 los precios de referencia de la gasolina motor corriente y el ACPM se mantienen estables a nivel nacional, y el Gobierno evaluará si sigue así en diciembre. El precio exacto cambia por ciudad: escribe el que pagas en tu estación.</p>
<h2 id="ex">Ejemplos de gasto de gasolina</h2>
<div id="examples">'''+table(['Viaje','Distancia','Rendimiento','Galones','Costo de gasolina','Por persona (2)'],rows)+'''</div>
<ul><li><b>500 km a 40 km/gal</b> gastan 12,5 galones. Con el galón a $16.000 son <b>$200.000</b>, o $100.000 por persona si viajan dos.</li>
<li><b>Ida y vuelta</b> (1.000 km) cuesta el doble: <b>$400.000</b>.</li>
<li><b>Con dato en L/100 km:</b> 500 km a 7 L/100 km son 35 litros, unos 9,2 galones. A $16.000 el galón: '''+cop(l100*PRICE)+'''.</li></ul>
<p class="note">Los ejemplos usan un precio de ejemplo de $16.000 por galón, no un precio oficial. Calculados con la fórmula de esta calculadora.</p>
<h2 id="how">Cómo se calcula, fácil</h2>
<p>Ejemplo: viaje de 300 km, carro que hace 40 km por galón, galón a $16.000.</p>
<ul><li>Galones: 300 ÷ 40 = <b>7,5 galones</b>.</li>
<li>Costo: 7,5 × $16.000 = <b>$120.000</b>.</li>
<li>Entre 3 personas: $40.000 cada una.</li></ul>
<p>El <b>rendimiento</b> dice cuántos kilómetros recorre el carro con un galón. Si tu dato está en <b>L/100 km</b> (litros por cada 100 km), elige esa unidad: la calculadora pasa los litros a galones.</p>
<h2 id="tips">Consejos y errores comunes</h2>
<ul><li><b>Usa tu rendimiento real.</b> Llena el tanque, anota los kilómetros y vuelve a llenar: km recorridos ÷ galones cargados.</li>
<li><b>No olvides los peajes.</b> En viajes largos pueden sumar mucho.</li>
<li><b>En ciudad se gasta más</b> que en carretera por el pare y arranque.</li>
<li><b>Revisa la presión de las llantas.</b> Llantas bajas aumentan el consumo.</li></ul>
<h2 id="faq" style="margin-top:22px">Preguntas frecuentes</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Fuentes (revisado el 25 de noviembre de 2026): <a href="https://minenergia.gov.co/es/sala-de-prensa/noticias-index/en-noviembre-el-gobierno-nacional-mantiene-estables-los-precios-de-la-gasolina-y-el-acpm/" rel="nofollow">Ministerio de Minas y Energía – En noviembre el Gobierno nacional mantiene estables los precios de la gasolina y el ACPM</a>. 1 galón estadounidense = 3,785411784 litros (definición exacta). Los cálculos usan la fórmula de esta calculadora.</p>'''

out=build(P,'Calculadora de gasto de gasolina Colombia – costo del viaje por galón',
 'Calcula cuánta gasolina gasta tu carro en un viaje y cuánto cuesta: galones, precio por galón, peajes, ida y vuelta y costo por persona.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('Por','Hong Life Calculators'),('Revisado','25 de noviembre de 2026'),('Fuentes','Ministerio de Minas y Energía')],
 [('form','Calculadora'),('figures','Datos útiles'),('ex','Ejemplos'),('how','Cómo se calcula'),('tips','Consejos'),('faq','Preguntas frecuentes')],'En esta página',('#examples','es'))
print(out)
