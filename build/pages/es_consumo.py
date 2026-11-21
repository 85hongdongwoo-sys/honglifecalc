import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
P='/es/calculadora-consumo-electrico.html'
def e(x,d=2): return f'{x:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
def row(name,w,h,p):
    k=w/1000*h*30;m=k*p
    return [name,f'{e(w,0)} W',e(h,1).rstrip('0').rstrip(','),f'{e(p)} €',f'{e(k,1)} kWh',f'{e(m)} €',f'{e(m*365/30)} €']
rows=[row('Bombilla LED',10,5,0.15),row('Televisor',100,4,0.15),row('Ordenador de sobremesa',200,6,0.15),row('Aparato de 1.000 W (valores por defecto)',1000,3,0.15),row('Radiador eléctrico',2000,4,0.15),row('Radiador eléctrico',2000,4,0.20),row('Aire acondicionado',1200,6,0.15)]
FAQ=[
("¿Cuánto cuesta un aparato de 1.000 W usado 3 horas al día?","Consume 1 kW × 3 h = 3 kWh al día, 90 kWh en 30 días. A 0,15 €/kWh son 13,50 € al mes y unos 164 € al año; a 0,20 €/kWh, 18,00 € al mes."),
("¿Cómo se calculan los kWh de un aparato?","kWh = potencia en vatios ÷ 1.000 × horas de uso. La potencia viene en la etiqueta o el manual del aparato. Un radiador de 2.000 W encendido 4 horas consume 8 kWh."),
("¿Qué precio del kWh pongo?","El de tu factura: divide el importe del término de energía entre los kWh consumidos. Si tienes la tarifa regulada (PVPC 2.0TD) el precio cambia cada hora: es más barato en el periodo valle (de 0 a 8 h entre semana y todo el fin de semana y festivos nacionales)."),
("¿Qué impuestos lleva la luz en 2026?","El impuesto especial sobre la electricidad (tipo ordinario 5,11269632 %, rebajado al 0,5 % en algunos meses de 2026) y el IVA (21 % general; en noviembre de 2026 se aplica el 10 % a contratos de hasta 10 kW). Estas rebajas dependen de decretos y del IPC, así que comprueba tu factura."),
("¿Cuál es el descuento del bono social eléctrico?","Hasta el 31 de diciembre de 2026, el 42,5 % para consumidores vulnerables y el 57,5 % para vulnerables severos (los porcentajes ordinarios son 35 % y 50 %)."),
("¿Cuánto gasta el frigorífico?","Según el IDAE, el frigorífico-congelador puede suponer hasta el 30 % del consumo de los electrodomésticos de una vivienda, y abrir la puerta mucho tiempo desperdicia un 7 % de su energía. Como funciona a ciclos, su consumo real se ve mejor en la etiqueta energética (kWh/año)."),
]
art='''<h2>Cómo se calcula el consumo eléctrico</h2>
<p><b>Energía (kWh) = potencia (W) ÷ 1.000 × horas al día × días.</b> <b>Coste = kWh × precio del kWh.</b> La calculadora muestra el coste del periodo elegido y lo extrapola a un año (coste del periodo × 365 ÷ días) y a un día.</p>
<p>Este cálculo sirve para aparatos que funcionan a potencia constante (bombillas, radiadores, hornos, ordenadores). Los que funcionan a ciclos —frigorífico, aire acondicionado con inverter, lavadora— no consumen su potencia máxima todo el rato: para ellos es mejor usar los kWh/año de la etiqueta energética.</p>
<h3>Ejemplos (30 días)</h3>
'''+table(['Aparato','Potencia','Horas/día','Precio kWh','Consumo','Coste 30 días','Coste al año'],rows)+'''
<p class="note">Calculado con la fórmula de esta página. Potencias y horas de ejemplo; los precios de 0,15 y 0,20 €/kWh son supuestos: usa el de tu factura.</p>
<h3>Tramos horarios de la tarifa 2.0TD (PVPC)</h3>
'''+table(['Periodo','Lunes a viernes laborables','Fines de semana y festivos nacionales'],[
['Punta (P1)','10–14 h y 18–22 h','—'],['Llano (P2)','8–10 h, 14–18 h y 22–24 h','—'],['Valle (P3)','0–8 h','Todas las horas']])+'''
<p class="note">Circular 3/2020 de la CNMC (península, Baleares y Canarias; Ceuta y Melilla tienen otro horario). Mover la lavadora o el lavavajillas al valle abarata el kWh si tienes PVPC o una tarifa con discriminación horaria.</p>
<h3>Impuestos y descuentos en 2026</h3>
'''+table(['Concepto','Valor','Nota'],[
['Impuesto especial sobre la electricidad','5,11269632 %','Tipo ordinario; rebajado al 0,5 % desde el 22 de marzo de 2026 y en otros meses según el IPC. En noviembre de 2026 rige el ordinario.'],
['IVA','21 %','10 % del 22/3 al 31/5/2026 y en noviembre de 2026 para contratos de hasta 10 kW y ciertos perceptores del bono social.'],
['Bono social (vulnerable)','42,5 %','Hasta el 31/12/2026 (ordinario 35 %)'],
['Bono social (vulnerable severo)','57,5 %','Hasta el 31/12/2026 (ordinario 50 %)'],
])+'''
<p class="note">Las rebajas de diciembre de 2026 dependen del IPC de octubre y no estaban confirmadas a 21/11/2026. El precio del kWh que introduces debería incluir lo que realmente pagas por energía; el término de potencia y el alquiler del contador se pagan aparte aunque no enciendas nada.</p>
<h3>Cómo gastar menos</h3>
<ul><li>Los aparatos que dan calor (radiadores, secadoras, hornos, termos) son los que más kWh consumen: cada hora de un radiador de 2.000 W son 2 kWh.</li>
<li>Usa la etiqueta energética al comprar: compara los kWh/año, no solo la letra.</li>
<li>No abras la puerta del frigorífico más de lo necesario (IDAE: un 7 % de su energía se pierde con aperturas prolongadas).</li>
<li>Apaga del todo (regleta con interruptor) los equipos que se quedan en espera.</li></ul>
'''+faq_html(FAQ,'Preguntas frecuentes')+'''
<p class="note">Fuentes (consultadas el 21/11/2026): <a href="https://www.boe.es/buscar/act.php?id=BOE-A-2020-1066" rel="nofollow">BOE — Circular 3/2020 de la CNMC (periodos horarios)</a>; <a href="https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/manual-iva-2026/capitulo-01-novedades-destacar-2026/tipos-impositivos.html" rel="nofollow">AEAT — Manual IVA 2026, tipos impositivos</a>; <a href="https://sede.agenciatributaria.gob.es/Sede/eu_es/todas-noticias/2026/septiembre/30/nuevas-medidas-marco-plan-integral-medio.html" rel="nofollow">AEAT — medidas del RDL 25/2026</a>; <a href="https://www.madrid.es/UnidadesDescentralizadas/Consumo/Promocionales/Nuevas%20medidas%20suministros%20energ%C3%A9ticos/ficheros/nuevas_medidas_energ%C3%ADa_nov26.pdf" rel="nofollow">Ayuntamiento de Madrid, Instituto Municipal de Consumo — medidas de noviembre de 2026</a>; <a href="https://www.miteco.gob.es/es/energia/pobreza-energetica/pe-001/preguntas-frecuentes-bono-social.html" rel="nofollow">MITECO — bono social</a>; <a href="https://www.idae.es/ahorra-energia/recomendaciones-para-el-ahorro-energetico-en-hogares" rel="nofollow">IDAE — ahorro en hogares</a>. Cálculo orientativo.</p>'''
print(build(P,'Calculadora de consumo eléctrico 2026 – Cuánto gasta un aparato en €',
 'Calcula los kWh y el coste en euros de cualquier aparato según su potencia, horas de uso y precio del kWh. Tramos 2.0TD, IVA e impuesto eléctrico de 2026 y ejemplos.',art,FAQ))
