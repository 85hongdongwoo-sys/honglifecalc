import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html

form='''<form class="card" id="form" onsubmit="return false"><h2>Your appliance</h2><style>.money::before{content:"£"}</style>
<label class="f"><span>Power (watts)</span><input id="w" inputmode="decimal" value="1,000"><small>On the rating plate or in the manual. 1 kW = 1,000 W.</small></label>
<label class="f"><span>Hours of use per day</span><input id="h" inputmode="decimal" value="3"></label>
<label class="f"><span>Plus minutes per day</span><input id="mn" inputmode="decimal" value="0"><small>Handy for kettles, showers and hair dryers (10 minutes = 0.17 hours).</small></label>
<label class="f"><span>Electricity price per kWh (£)</span><div class="money"><input id="kp" inputmode="decimal" value="0.2632"></div><small>Default 26.32p = Ofgem price cap GB average, Direct Debit, 1 Oct–31 Dec 2026. Use the rate on your bill, in pounds (26.32p = 0.2632).</small></label>
<label class="f"><span>Days</span><input id="d" inputmode="decimal" value="30"></label></form>'''

calc='''function calc(){const kw=num('w')/1000,hd=num('h')+num('mn')/60,d=Math.max(1,num('d')),p=num('kp'),k=kw*hd*d,m=k*p;
 return big('Cost for '+nn(d,0)+' days',mf2(m),nn(k,1)+' kWh')+kv([['Per day',mf2(m/d)+' ('+nn(kw*hd,2)+' kWh)'],['Per hour of use',nn(kw*p*100,1)+'p'],['Per year at this use',mf(m*365/d)],['Hours a day used',nn(hd,2)]])+'<p class="note">Running cost only – your daily standing charge is paid whether or not the appliance is on.</p>'}'''

ex=[('Kettle (3,000 W)','10 min a day','0.5','13.2p','£3.95','£48.03'),
    ('Electric shower (9,500 W)','10 min a day','1.58','41.7p','£12.50','£152'),
    ('Portable heater (2,000 W)','4 h a day at full power','8','£2.11','£63.17','£769'),
    ('Tumble dryer (2,500 W)','1 h a day','2.5','65.8p','£19.74','£240'),
    ('Electric oven (2,000 W)','1 h a day','2','52.6p','£15.79','£192'),
    ('Desktop PC (300 W)','4 h a day','1.2','31.6p','£9.48','£115'),
    ('TV (100 W)','5 h a day','0.5','13.2p','£3.95','£48.03'),
    ('Laptop (50 W)','8 h a day','0.4','10.5p','£3.16','£38.43'),
    ('LED bulb (8 W)','5 h a day','0.04','1.1p','£0.32','£3.84')]

FAQ=[
("How do I calculate the cost of running an appliance?","Multiply the power in kilowatts by the hours used to get kWh, then multiply by your unit rate. A 2,000 W heater for 3 hours uses 2 × 3 = 6 kWh; at the October–December 2026 price cap rate of 26.32p per kWh that is £1.58."),
("How much does it cost to run a 1,000 W appliance for an hour?","1,000 W for one hour uses exactly 1 kWh, so it costs your unit rate – 26.32p at the Oct–Dec 2026 price cap average. Three hours a day for 30 days is 90 kWh, or £23.69."),
("How much does it cost to boil a kettle?","A 3,000 W kettle that takes about 2 minutes to boil uses 0.1 kWh, so about 2.6p at 26.32p per kWh. Boiling only the water you need cuts the time and the cost."),
("Does the calculator include the standing charge?","No. The standing charge is a fixed amount per day on your bill that you pay regardless of use, so it does not change when you switch an appliance on or off. Under the October–December 2026 price cap the average electricity standing charge is 54.83p a day – about £200 a year. This calculator shows the extra cost of using the appliance."),
("How do I find my electricity unit rate?","It is printed on your bill or in your supplier's app as pence per kWh, often with a separate day and night rate on Economy 7. If you are on a standard variable tariff, Ofgem's price cap sets the maximum average unit rate each quarter: 26.32p per kWh (GB average, Direct Debit) from 1 October to 31 December 2026."),
("Why does my fridge cost less than its wattage suggests?","Fridges and freezers cycle on and off, so they rarely draw full power for 24 hours. Use the annual kWh figure on the energy label instead: 250 kWh a year at 26.32p per kWh is £65.80 a year.")]

art='''<h2>How to work out the running cost</h2>
<p>Your bill charges for <b>kilowatt-hours (kWh)</b> – one kWh is 1,000 watts used for one hour.</p>
<ul><li><b>kWh</b> = watts ÷ 1,000 × hours of use</li><li><b>Cost</b> = kWh × unit rate (£ per kWh)</li><li><b>Cost per hour</b> = kW × unit rate – a 2 kW heater at 26.32p/kWh costs 52.6p an hour</li></ul>
<p>Enter your own unit rate from your bill: the price varies by supplier, tariff, region and payment method, and on standard variable tariffs it changes every quarter with Ofgem's energy price cap (which rose by 4% from 1 October 2026).</p>
<h3>Current official figures: Ofgem price cap, 1 October – 31 December 2026</h3>
'''+table(['GB average, Direct Debit','Unit rate','Standing charge'],[['Electricity','26.32p per kWh','54.83p per day (≈ £200 a year)'],['Electricity, 1 Jul–30 Sep 2026 (previous cap)','26.11p per kWh','57.19p per day'],['Gas','7.97p per kWh','29.68p per day']])+'''
<p class="note">Typical dual-fuel bill £1,723 a year, up 4% on the previous quarter. Electricity cap rates carry no VAT from 1 October 2026 to 31 March 2027; gas rates include 5% VAT. Rates vary by region and payment method. The cap for 1 January – 31 March 2027 is due to be announced by 25 November 2026.</p>
<h3>Running costs of common appliances (at 26.32p per kWh)</h3>
'''+table(['Appliance','Use','kWh a day','Cost a day','30 days','A year'],[list(r) for r in ex])+'''
<p class="note">Wattages are typical rating-plate figures; check your own appliance. Heaters, ovens and dryers with thermostats cycle on and off, so real use is often lower than full power × hours. 26.32p is the GB average Direct Debit cap rate for October–December 2026.</p>
<h3>Cost per hour at different unit rates</h3>
'''+table(['Power','20p/kWh','26.32p/kWh (cap Oct–Dec 2026)','30p/kWh'],[[f"{w:,} W",f"{w/1000*20:.1f}p",f"{w/1000*26.32:.1f}p",f"{w/1000*30:.1f}p"] for w in [10,100,500,1000,2000,3000,9500]])+'''
<h3>Tips to cut appliance running costs</h3>
<ul><li><b>Target the high-wattage, long-use items</b> first: electric heaters, tumble dryers and electric showers dominate most bills; LED bulbs and phone chargers barely register.</li><li><b>Shorten heating times</b> rather than lowering power settings – a 2 kW heater for one hour less a day saves 2 kWh a day.</li><li><b>Use the energy label</b> (annual kWh) for fridges, freezers and washing machines instead of the wattage.</li><li><b>Time-of-use tariffs</b> such as Economy 7 make night-time use cheaper – enter the night rate to see the saving.</li><li><b>Measure it</b> with a plug-in energy monitor if you are unsure how much an appliance really uses.</li></ul>
<h3>Common mistakes</h3>
<ul><li>Typing the unit rate in pence (26.32) instead of pounds (0.2632).</li><li>Using watts as kWh – a 1,000 W appliance only uses 1 kWh if it runs for a full hour.</li><li>Assuming a thermostat-controlled appliance runs at full power the whole time.</li><li>Adding the standing charge to each appliance – it is a fixed daily charge for the whole home.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 22 Nov 2026): <a href="https://www.ofgem.gov.uk/press-release/energy-price-cap-will-rise-4-october-2026" rel="nofollow">Ofgem – Energy price cap will rise by 4% from October 2026</a>; <a href="https://www.ofgem.gov.uk/your-energy-supply/your-energy-bill/energy-price-cap-unit-rates-and-standing-charges" rel="nofollow">Ofgem – Energy price cap unit rates and standing charges</a>; <a href="https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026" rel="nofollow">Ofgem – Changes to energy price cap between 1 October and 31 December 2026</a>. Appliance examples use the calculator's own formula at 26.32p/kWh.</p>'''

print(build('/uk/electricity-cost-calculator.html','Electricity Cost Calculator UK 2026 – Appliance Running Cost per Hour, Day & Year',
 'Work out what an appliance costs to run per hour, day, month and year from its watts and your unit rate (p/kWh), with UK examples for kettles, heaters, dryers and showers.',art,FAQ,form=form,calc=calc))
