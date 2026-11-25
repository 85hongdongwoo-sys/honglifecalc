import sys, math; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/nz/fuel-cost-calculator.html'
CHK='25 November 2026'
# Latest MBIE weekly average retail prices (NZ$/L) and week; leave None unless verified today.
MBIE=None   # e.g. {'week':'week ending 20 November 2026','p91':2.80,'diesel':2.40}
# NZTA light-vehicle RUC rate (NZ$ per 1,000 km); leave None unless verified today.
RUC=76

form='''<form class="card" id="form" onsubmit="return false"><h2>Your numbers</h2><label class="f"><span>Distance (km)</span><input id="dist" inputmode="decimal" value="500"><small>One way. Choose return below if you are coming back.</small></label><label class="f"><span>Trip</span><select id="rt"><option value="1">One way</option><option value="2">Return</option></select></label><label class="f"><span>Fuel consumption (L/100 km)</span><input id="cons" inputmode="decimal" value="7"><small>Use your car's real figure if you know it.</small></label><label class="f"><span>Fuel price per litre ($)</span><input id="fp" inputmode="decimal" value="2.6"><small>An example price – use what you pay at the pump.</small></label><label class="f"><span>People sharing the cost</span><input id="ppl" inputmode="decimal" value="2"></label><label class="f"><span>Road user charges ($ per 1,000 km, diesel cars and EVs)</span><input id="ruc" inputmode="decimal" value="0"><small>Petrol cars: leave at 0 (fuel tax is in the pump price). Diesel cars and EVs pay RUC instead – enter the rate on your RUC licence.</small></label></form>'''

calc='''function calc(){const k=num('dist')*(Number(($('rt')||{}).value)||1),l=num('cons'),p=num('fp'),n=Math.max(1,Math.round(num('ppl'))),r=num('ruc');
 if(k<=0||(l<=0&&r<=0))return big(O.cost,'–','Enter a distance and fuel consumption');
 const v=k*l/100,f=v*p,ru=k*r/1000,c=f+ru;
 const rows=[['Total distance',nn(k,0)+' km'],[O.vol,nn(v,1)+' '+O.lit],['Fuel',mf2(f)]];
 if(r>0)rows.push(['Road user charges',mf2(ru)]);
 rows.push(['Cost per 100 km',mf2(c/k*100)],['Cost per km',mf(c/k,3)]);
 return big(r>0?'Trip cost (fuel + RUC)':O.cost,mf2(c),O.pp+' ('+n+'): '+mf2(c/n))+kv(rows)+'<p class="note">Fuel and RUC only. Parking, ferries and wear and tear are not included.</p>'}'''

def trip(km,cons,price,ruc=0):
    v=km*cons/100; return v, v*price+km*ruc/1000
d=lambda x:f"${x:,.2f}"
rows=[]
for lab,km,cons,pr in [('Auckland → Wellington (one way)',640,7.0,2.60),('Auckland → Wellington, return',1280,7.0,2.60),('Christchurch → Queenstown (one way)',480,6.0,2.60),('Commute 30 km a day × 20 days',600,8.0,2.60)]:
    v,c=trip(km,cons,pr); rows.append([lab,f"{km:,} km",f"{cons:.1f} L/100 km",d(pr),f"{v:.1f} L",d(c)])
print(rows)

fig=[]
if MBIE:
    fig+=[['Average 91 petrol price',d(MBIE['p91'])+' a litre','MBIE weekly fuel price monitoring, '+MBIE['week']+'.'],
          ['Average diesel price',d(MBIE['diesel'])+' a litre','MBIE weekly fuel price monitoring, '+MBIE['week']+'. Diesel is cheaper at the pump because diesel vehicles pay RUC separately.']]
if RUC:
    fig+=[['Road user charges – standard rate, light vehicles (RUC type 1)',d(RUC)+' per 1,000 km (GST inclusive)','For powered vehicles with 2 axles up to 3,500 kg, such as diesel cars and EVs. This is the standard rate: NZTA also lists a temporary RUC reduction, so check the NZTA page for the rate that applies to you.'],
          ['Road user charges – plug-in petrol hybrids (RUC type 12)','$38 per 1,000 km (GST inclusive)','Standard rate for plug-in petrol hybrids of 1,001–3,500 kg.']]
else:
    fig+=[['Road user charges (RUC)','Diesel vehicles and EVs','They pay RUC per 1,000 km instead of fuel tax in the pump price. Check the current rate on the NZTA website.']]

FAQ=[
("How do I work out the fuel cost of a trip?","Litres = km × L/100 km ÷ 100. Cost = litres × price per litre. Example: 640 km at 7 L/100 km uses 44.8 litres. At $2.60 a litre that is $116.48."),
("How much does it cost to drive from Auckland to Wellington?","About $116 in fuel one way for a car using 7 L/100 km, at $2.60 a litre (640 km). A return trip is about $233. Split between 2 people, that is $116.48 each."),
("How do I convert km per litre to L/100 km?","Divide 100 by your km per litre. 20 km/L = 5 L/100 km. 14 km/L = 7.1 L/100 km. 10 km/L = 10 L/100 km."),
("Do I need to add road user charges?","Yes, if you drive a diesel car or an EV, because they pay road user charges. The standard light-vehicle rate (RUC type 1) is $76 per 1,000 km, so a 640 km trip adds $48.64. NZTA also lists a temporary reduction, so check the rate that applies to you. For a petrol car leave the box at 0."),
("How much do I spend on fuel commuting?","30 km a day for 20 days is 600 km. At 8 L/100 km that is 48 litres. At $2.60 a litre you pay $124.80 a month."),
("What fuel price should I use?","Use the price on the pump where you fill up. Prices differ by region, brand and station, and change often, so an average may not match what you pay."),
]

art='''<h2 id="figures">Road user charges for diesel cars and EVs</h2>
'''+table(['Item','Figure','What it means'],fig)+'''
<h2 id="ex">Trip cost examples</h2>
<div id="examples">'''+table(['Trip','Distance','Fuel use','Price a litre','Litres','Fuel cost'],rows)+'''</div>
<ul><li><b>Auckland → Wellington:</b> 640 km at 7 L/100 km uses 44.8 litres. At $2.60 a litre that is <b>$116.48</b> one way.</li>
<li><b>Return trip:</b> double it, <b>$232.96</b>. With 3 people sharing, $77.65 each.</li>
<li><b>Christchurch → Queenstown:</b> 480 km at 6 L/100 km costs <b>$74.88</b>.</li>
<li><b>Commuting:</b> 600 km a month at 8 L/100 km costs <b>$124.80</b>.</li></ul>
<p class="note">$2.60 a litre is an example price, not an official average. Distances are rounded road distances. Examples use this calculator's formula.</p>
<h2 id="how">How the calculator works</h2>
<p>Example first. You drive 640 km. Your car uses 7 litres every 100 km. You need 640 × 7 ÷ 100 = <b>44.8 litres</b>. At $2.60 a litre you pay 44.8 × 2.60 = <b>$116.48</b>.</p>
<ul><li><b>Fuel consumption (L/100 km)</b>: how many litres your car uses to drive 100 km. Lower is better.</li>
<li><b>Litres needed</b> = km × L/100 km ÷ 100.</li>
<li><b>Fuel cost</b> = litres × price per litre.</li>
<li><b>Road user charges (RUC)</b>: a charge per 1,000 km for diesel vehicles and EVs. The calculator adds km × rate ÷ 1,000.</li></ul>
<h2 id="tips">Tips to spend less</h2>
<ul><li><b>Compare stations.</b> Prices can differ a lot between towns and brands. Discount cards and apps can cut a few cents a litre.</li>
<li><b>Use your real fuel use.</b> Hills, towing and open-road speed raise fuel use.</li>
<li><b>Check tyre pressure.</b> Soft tyres and a roof box both increase fuel use.</li>
<li><b>Diesel or EV?</b> Remember RUC: at the standard $76 per 1,000 km it adds 7.6 cents a km.</li></ul>
<h2 id="faq" style="margin-top:22px">Fuel cost FAQ</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Sources (checked '''+CHK+'''): <a href="https://www.nzta.govt.nz/vehicles/road-user-charges/ruc-rates-and-transaction-fees" rel="nofollow">NZTA – RUC rates and transaction fees</a>. Examples use this calculator's own formula. General information.</p>'''

out=build(P,'Fuel Cost Calculator NZ 2026 – Trip Cost, Return Trip and RUC',
 'Work out the fuel cost of a trip in New Zealand: litres, one-way or return cost, cost per person and road user charges for diesel cars and EVs.',
 art,FAQ,form=form,calc=calc)
add_top(out,[('By','Hong Life Calculators'),('Checked',CHK),('Sources','NZTA')],
 [('form','Calculator'),('figures','Road user charges'),('ex','Examples'),('how','How it works'),('tips','Tips'),('faq','FAQ')],'On this page',('#examples','en'))
print(out)
