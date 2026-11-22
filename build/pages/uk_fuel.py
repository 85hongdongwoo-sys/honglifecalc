import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html

form='''<form class="card" id="form" onsubmit="return false"><h2>Your trip</h2><style>.money::before{content:"£"}</style>
<label class="f"><span>Distance</span><input id="dist" inputmode="decimal" value="300"></label>
<label class="f"><span>Distance unit</span><select id="du"><option value="mi" selected>miles</option><option value="km">kilometres</option></select></label>
<label class="f"><span>Return journey?</span><select id="rt"><option value="1" selected>One way</option><option value="2">Return (distance × 2)</option></select></label>
<label class="f"><span>Fuel economy</span><input id="cons" inputmode="decimal" value="45"></label>
<label class="f"><span>Economy unit</span><select id="cu"><option value="mpg" selected>mpg (UK gallons)</option><option value="l">litres per 100 km</option></select><small>Use your car's real-world average from the trip computer; the official WLTP figure is usually optimistic.</small></label>
<label class="f"><span>Fuel price per litre</span><div class="money"><input id="fp" inputmode="decimal" value="1.74"></div><small>Default £1.74 = HMRC pump price basis for its December 2026 advisory fuel rates (petrol). Enter the price on the pump, in pounds (174.9p = 1.749).</small></label>
<label class="f"><span>People sharing the cost</span><input id="ppl" inputmode="decimal" value="2"></label></form>'''

calc='''function calc(){const G=4.54609,M=1.609344,d=num('dist')*(+$('rt').value||1),km=$('du').value==='mi'?d*M:d,c=num('cons'),l100=$('cu').value==='mpg'?(c>0?100*G/M/c:0):c,L=km*l100/100,cost=L*num('fp'),mi=km/M,mpg=l100>0?100*G/M/l100:0;
 return big('Fuel cost',mf2(cost),'Per person: '+mf2(cost/Math.max(1,num('ppl'))))+kv([['Fuel needed',nn(L,1)+' litres ('+nn(L/G,1)+' UK gallons)'],['Distance driven',nn(mi,0)+' miles / '+nn(km,0)+' km'],['Cost per mile',mi>0?nn(cost/mi*100,1)+'p':'–'],['Cost per km',km>0?nn(cost/km*100,1)+'p':'–'],['Economy',nn(mpg,1)+' mpg = '+nn(l100,2)+' L/100 km']])}'''

FAQ=[
("How do I work out the fuel cost of a trip in the UK?","Divide the miles by your mpg to get UK gallons, multiply by 4.546 to get litres, then multiply by the price per litre. 300 miles at 45 mpg uses 6.67 gallons = 30.3 litres; at £1.74 a litre that costs £52.73."),
("How much does it cost to drive 100 miles?","At 45 mpg and £1.74 a litre, 100 miles uses 10.1 litres and costs about £17.58 (17.6p a mile). At 30 mpg it is £26.37, at 60 mpg £13.18. Change the price box to today's pump price for your own figure."),
("How do I convert mpg to litres per 100 km?","Divide 282.48 by the mpg figure (UK gallons). 45 mpg = 6.28 L/100 km, 50 mpg = 5.65 L/100 km. The same formula works the other way: 282.48 ÷ 7 L/100 km = 40.4 mpg."),
("Why is my mpg different from the figure on the car's brochure?","Official figures come from the WLTP laboratory test. Real driving with motorway speeds above 70 mph, cold starts, short trips, roof boxes, under-inflated tyres and air-con usually gives a lower mpg, so use your trip computer or a brim-to-brim measurement."),
("Is a US mpg the same as a UK mpg?","No. A UK (imperial) gallon is 4.54609 litres and a US gallon is 3.785 litres, so a car doing 40 US mpg does about 48 UK mpg. Check which one a review or website quotes before using it here."),
("How do I split fuel costs fairly for a lift share?","Work out the fuel cost of the whole journey and divide by the number of people in the car, including the driver. A 300-mile trip costing £52.73 split four ways is £13.18 each. Lift-share contributions that only cover running costs are not treated as making a profit.")]
FAQ[5]=("How do I split fuel costs fairly for a lift share?","Work out the fuel cost of the whole journey and divide by the number of people in the car, including the driver. A 300-mile trip costing £52.73 split four ways is £13.18 each. Set the 'People sharing the cost' box to do this automatically.")

art='''<h2>How the fuel cost is calculated</h2>
<p>UK drivers usually think in <b>miles</b> and <b>miles per gallon</b>, while pumps charge per <b>litre</b>. The calculator converts everything to litres:</p>
<ul><li><b>Gallons used</b> = miles ÷ mpg</li><li><b>Litres used</b> = gallons × 4.54609 (one UK imperial gallon)</li><li><b>Fuel cost</b> = litres × price per litre</li><li><b>Cost per mile</b> = price per litre × 4.54609 ÷ mpg</li></ul>
<p>If you use metric units, litres = km × L/100 km ÷ 100. One mile is exactly 1.609344 km, so <b>L/100 km = 282.48 ÷ mpg</b>.</p>
<h3>mpg to litres per 100 km and cost per mile</h3>
'''+table(['UK mpg','L/100 km','Cost per mile at £1.74/L (petrol)','at £1.99/L (diesel)'],[[str(m),f"{282.48093633/m:.2f}",f"{174*4.54609/m:.1f}p",f"{199*4.54609/m:.1f}p"] for m in [30,35,40,45,50,55,60,70]])+'''
<p class="note">£1.74 and £1.99 are rounded from the pump prices HMRC used for its December 2026 advisory fuel rates (petrol 174.1p, diesel 199.2p a litre). Prices vary by forecourt; the government also publishes weekly UK average pump prices (DESNZ <i>Weekly road fuel prices</i>).</p>
<h3>Current official figures (UK, checked 22 Nov 2026)</h3>
'''+table(['Item','Figure','Source'],[['Fuel duty, petrol and diesel','52.95p per litre (temporary 5p cut extended to 31 December 2026), plus 20% VAT on the pump price','HM Treasury / HMRC fuel duty rates 2026 to 2027'],['Pump price basis for HMRC December 2026 rates','Petrol 174.1p, diesel 199.2p, LPG 97.0p per litre','HMRC advisory fuel rates'],['Electricity basis for advisory electricity rate','25.94p/kWh at home, 54.00p/kWh public charging','HMRC advisory fuel rates']])+'''
<h3>HMRC advisory fuel rates for company cars (pence per mile)</h3>
'''+table(['Engine size','Petrol 1 Sep–30 Nov 2026','Petrol from 1 Dec 2026','Diesel 1 Sep–30 Nov 2026','Diesel from 1 Dec 2026','LPG (both periods)'],[['Petrol 1400cc or less / diesel 1600cc or less','14p','16p','15p','16p','11p'],['Petrol 1401–2000cc / diesel 1601–2000cc','17p','19p','16p','18p','13p'],['Over 2000cc','27p','29p','22p','25p','20p']])+'''
<p class="note">Fully electric company cars: 7p a mile (home charging) or 15p (public charging) in both periods. Employers may keep using the previous rates for up to one month after a change. These rates are for reimbursing business fuel in company cars – they are not the rates for using your own car.</p>
<h3>Worked examples (petrol £1.74, diesel £1.99 a litre)</h3>
'''+table(['Trip','Economy','Fuel used','Fuel cost','Per person'],[
 ['100 miles','45 mpg petrol','10.1 L','£17.58','£8.79 (2 people)'],
 ['300 miles one way','45 mpg petrol','30.3 L','£52.73','£26.37 (2 people)'],
 ['300 miles one way','60 mpg diesel at £1.99','22.7 L','£45.23','£22.62 (2 people)'],
 ['300 miles one way','30 mpg petrol (large SUV)','45.5 L','£79.10','£19.78 (4 people)'],
 ['600 miles (300 there and back)','45 mpg petrol','60.6 L','£105.47','£26.37 (4 people)'],
 ['Commute: 20 miles a day, 5 days, 46 weeks','45 mpg petrol','464.7 L','£808.60 a year','about £67 a month']])+'''
<p class="note">All rows use the calculator's own formula. Every 5p change in the litre price moves the 300-mile, 45 mpg trip by £1.52. On 300 miles at 45 mpg the 52.95p duty alone is £16.05 before VAT.</p>
<h3>Ways to cut the fuel bill</h3>
<ul><li><b>Slow down on motorways:</b> fuel use rises quickly above about 60 mph because air resistance grows with the square of speed.</li><li><b>Check tyre pressures</b> against the figure on the door pillar or fuel flap, especially before a long, loaded trip.</li><li><b>Remove roof bars and boxes</b> when not in use and clear heavy items from the boot.</li><li><b>Drive smoothly:</b> anticipate traffic, change up early and avoid hard acceleration.</li><li><b>Compare forecourts:</b> motorway services are usually the most expensive place to fill up; supermarket sites often charge less.</li></ul>
<h3>Common mistakes</h3>
<ul><li>Using a <b>US mpg</b> figure from an American website – it understates UK mpg by about 17%.</li><li>Typing the price in pence (150) instead of pounds (1.50).</li><li>Forgetting the return leg – set <i>Return journey</i> to double the distance.</li><li>Using the brochure (WLTP) economy instead of your real-world average.</li></ul>
<h3>Business mileage</h3>
<p>If you drive your own car for work, your employer can repay you tax-free up to HMRC's approved mileage allowance payments – check the current rates on GOV.UK. For company cars, HMRC's <i>advisory fuel rates</i> above are updated quarterly (1 March, 1 June, 1 September and 1 December). Your real cost per mile from this calculator may be higher or lower than the advisory rate.</p>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 22 Nov 2026): <a href="https://www.gov.uk/government/publications/amended-fuel-duty-rates-for-2026-to-2027/amended-fuel-duty-rates-2026-to-2027" rel="nofollow">GOV.UK – Amended fuel duty rates 2026 to 2027</a> (52.95p/litre, 5p cut to 31 Dec 2026); conversion factors from the Weights and Measures Act 1985 (1 UK gallon = 4.54609 litres; 1 mile = 1.609344 km); <a href="https://www.gov.uk/government/statistics/weekly-road-fuel-prices" rel="nofollow">DESNZ – Weekly road fuel prices</a> for current UK average pump prices; <a href="https://www.gov.uk/guidance/advisory-fuel-rates" rel="nofollow">HMRC – Advisory fuel rates</a> (updated 18 Nov 2026: rates from 1 Dec 2026 and pump price basis). Enter your own pump price for an exact figure.</p>'''

print(build('/uk/fuel-cost-calculator.html','Fuel Cost Calculator UK 2026 – Trip Cost in Miles & mpg, Per Person',
 'Work out the fuel cost of a UK journey from miles and mpg (or km and L/100 km) and the pump price, with cost per mile, a return-trip option and a split per passenger.',art,FAQ,form=form,calc=calc))
