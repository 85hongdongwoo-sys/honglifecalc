import sys,re; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html, ORIG
def setdef(path,vals):
    s=open(ORIG+path,encoding='utf-8').read()
    f=re.search(r'<form class="card" id="form".*?</form>',s,re.S).group(0)
    for k,v in vals.items(): f=re.sub(r'(<input id="%s"[^>]*value=")[^"]*'%k,lambda m:m.group(1)+v,f)
    return f
# ---------- Spain fuel ----------
FAQ_ES=[
("¿Cómo se calcula el gasto de gasolina de un viaje?","Litros = kilómetros × consumo (L/100 km) ÷ 100, y coste = litros × precio por litro. Por ejemplo, 500 km con un coche que gasta 6 L/100 km son 30 litros; a 1,79 €/L cuestan 53,70 €."),
("¿Cuánto cuesta la gasolina en España ahora?","Según el Boletín Petrolero de la UE con precios del 12 de octubre de 2026, la media nacional era de 1,790 €/L para la gasolina 95 y 1,889 €/L para el diésel, impuestos incluidos. Los precios cambian cada semana; consulta el Geoportal de gasolineras del Ministerio para tu zona."),
("¿Qué es la rebaja del impuesto de hidrocarburos de 2026?","El Real Decreto-ley 25/2026, vigente desde el 1 de octubre, rebaja el impuesto sobre hidrocarburos hasta diciembre. En noviembre se mantiene la rebaja de 20 céntimos por litro (unos 24,2 céntimos con IVA) para gasolina y diésel, salvo en Canarias, Ceuta y Melilla."),
("¿Cuánto cuesta un viaje Madrid–Barcelona en coche?","Son unos 620 km por autovía. Con 6 L/100 km se gastan unos 37 litros: unos 66,60 € a 1,79 €/L (sin contar peajes)."),
("¿Cómo repartir la gasolina entre los pasajeros?","Divide el coste total entre las personas que comparten el viaje. Si añades peajes y aparcamiento, súmalos antes de repartir.")]
art_es='''<h2>Cómo calcular el gasto de combustible</h2>
<p><b>Litros = distancia (km) × consumo (L/100 km) ÷ 100.</b> <b>Coste = litros × precio por litro.</b> La calculadora aplica estas dos fórmulas y divide el resultado entre las personas que comparten el viaje.</p>
<h3>Ejemplos (precios medios de octubre de 2026)</h3>
'''+table(['Viaje','Consumo','Precio','Litros','Coste'],[['100 km','6 L/100 km','1,79 €/L (gasolina 95)','6','10,74 €'],['500 km','6 L/100 km','1,79 €/L','30','53,70 €'],['500 km','7 L/100 km','1,79 €/L','35','62,65 €'],['500 km','5 L/100 km','1,889 €/L (diésel)','25','47,23 €'],['600 km','8 L/100 km','1,889 €/L','48','90,67 €'],['1.000 km','7 L/100 km','1,79 €/L','70','125,30 €']])+'''
<h3>Precio medio del combustible en España</h3>
'''+table(['Combustible','Media nacional (12/10/2026)','Impuesto especial por litro (sin IVA) con la rebaja'],[['Gasolina 95','1,790 €/L','27,27 céntimos (antes 47,27)'],['Diésel','1,889 €/L','17,90 céntimos (antes 37,90)']])+'''
<p class="note">Boletín Petrolero de la UE (Comisión Europea), precios con impuestos. La rebaja del Real Decreto-ley 25/2026 rige de octubre a diciembre de 2026; el importe de diciembre depende del IPC. Comprueba el precio de tu gasolinera en el Geoportal del Ministerio para la Transición Ecológica.</p>
<h3>Cómo gastar menos</h3>
<ul><li>Conducir a 110 km/h en lugar de 130 km/h reduce notablemente el consumo en autovía.</li><li>Lleva la presión de los neumáticos que indica el fabricante y quita la baca o el cofre si no los usas.</li><li>Compara precios: entre gasolineras de la misma zona puede haber diferencias apreciables.</li><li>El consumo homologado (WLTP) suele ser algo menor que el real; usa el dato del ordenador de a bordo si lo tienes.</li></ul>
'''+faq_html(FAQ_ES,'Preguntas frecuentes')+'''
<p class="note">Fuentes (consultadas el 20/11/2026): Comisión Europea, Weekly Oil Bulletin (precios del 12/10/2026); Real Decreto-ley 25/2026 y resolución del Congreso publicada en el BOE el 20/10/2026, según <a href="https://selectra.es/energia/noticias/carburantes-2026-noviembre-rebaja-impuesto-litro" rel="nofollow">Selectra</a>. Los peajes no están incluidos. Cálculo orientativo.</p>'''
print(build('/es/calculadora-gasto-gasolina.html','Calculadora de gasto de gasolina 2026 – Coste del viaje y por persona',
 'Calcula cuánto cuesta la gasolina o el diésel de un viaje según kilómetros, consumo y precio por litro, y repártelo entre pasajeros. Precios medios de 2026 y rebaja del impuesto.',art_es,FAQ_ES,form=setdef('/es/calculadora-gasto-gasolina.html',{'fp':'1,79'})))
# ---------- Australia fuel ----------
FAQ_AU=[
("How do I work out the fuel cost of a trip?","Litres = distance (km) × consumption (L/100 km) ÷ 100, then multiply by the price per litre. A 500 km trip in a car using 7 L/100 km needs 35 litres; at $2.34 a litre that is $81.90."),
("What is the average petrol price in Australia now?","News reports on 9 November 2026 put the national average for unleaded 91 at about 234.3 cents a litre and diesel at about 278 cents (prices as at 7 November). Prices move every week and vary by city cycle — check your state's fuel price app before you fill up."),
("How much fuel does a car use per 100 km?","Small cars typically use about 5–7 L/100 km, medium SUVs 7–9 and large 4WDs and utes 9–12 or more. Use the combined figure on your car's fuel consumption label or the trip computer for a better estimate."),
("How much does Sydney to Melbourne cost in fuel?","It is about 880 km via the Hume. At 7 L/100 km you need about 62 litres — roughly $144 at $2.34 a litre."),
("How do I split fuel costs between passengers?","Divide the total by the number of people sharing. If you claim car expenses for work, the ATO's cents-per-kilometre method uses a set rate instead of actual fuel.")]
art_au='''<h2>How the fuel cost is calculated</h2>
<p><b>Fuel needed (L) = distance (km) × consumption (L/100 km) ÷ 100.</b> <b>Cost = litres × price per litre.</b> The calculator then divides the cost between the people sharing the trip.</p>
<h3>Trip examples</h3>
'''+table(['Trip','Consumption','Price','Litres','Fuel cost'],[['100 km','7 L/100 km','$2.34/L (ULP)','7','$16.38'],['500 km','7 L/100 km','$2.34/L','35','$81.90'],['900 km','8 L/100 km','$2.34/L','72','$168.48'],['500 km','9 L/100 km','$2.78/L (diesel)','45','$125.10'],['1,000 km','7 L/100 km','$2.34/L','70','$163.80']])+'''
<p class="note">Prices based on the national averages reported for 7 November 2026 (ULP about 234.3 c/L, diesel about 278 c/L). Use your local price for an accurate figure.</p>
<h3>Typical fuel consumption</h3>
'''+table(['Vehicle','Typical combined L/100 km'],[['Small hatch','5–7'],['Medium sedan','6–8'],['Medium SUV','7–9'],['Large SUV / 4WD','9–12'],['Ute (diesel)','8–11'],['Hybrid','4–5']])+'''
<p class="note">Indicative ranges; real-world use is usually higher than the label, especially towing, with roof loads or at 110 km/h.</p>
<h3>Ways to cut fuel costs</h3>
<ul><li>Buy at the low point of your city's price cycle — in the capital cities, unleaded prices rise and fall in regular cycles.</li><li>Keep tyres at the placard pressure and remove roof racks when not needed.</li><li>Drive smoothly and use cruise control on highways.</li><li>Compare stations with your state's fuel app (e.g. FuelCheck in NSW, FuelWatch in WA).</li></ul>
'''+faq_html(FAQ_AU)+'''
<p class="note">Sources (checked 20 Nov 2026): <a href="https://www.ibtimes.com.au/australian-fuel-prices-fall-wholesale-costs-1878124" rel="nofollow">IBTimes Australia, 9 November 2026</a> (national average ULP 234.3 c/L, diesel 278 c/L as at 7 November); ACCC petrol monitoring; Green Vehicle Guide (fuel consumption labels). Estimates only.</p>'''
print(build('/au/fuel-cost-calculator.html','Fuel Cost Calculator Australia 2026 – Trip Petrol Cost & Cost per Person',
 'Work out the petrol or diesel cost of a trip from distance, L/100 km and price per litre, and split it between passengers — with November 2026 average prices and typical consumption figures.',art_au,FAQ_AU,form=setdef('/au/fuel-cost-calculator.html',{'fp':'2.34'})))
