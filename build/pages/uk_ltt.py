import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
calc='''function calc(){const p=num('p'),h=$('h').checked,M=[[225000,0],[400000,.06],[750000,.075],[1500000,.10],[Infinity,.12]],H=[[180000,.05],[250000,.085],[400000,.10],[750000,.125],[1500000,.15],[Infinity,.17]];
 const run=B=>{let t=0,lo=0,rows=[];for(const [hi,r] of B){if(p>lo){const s=Math.min(p,hi)-lo,x=s*r;t+=x;rows.push([(hi===Infinity?'Over '+gbp(lo,0):gbp(lo===0?0:lo+1,0)+' – '+gbp(hi,0))+' at '+pc(r,Math.round(r*1000)%10?1:0),gbp(x,0)])}lo=hi}return {t,rows}};
 const m=run(M),x=run(H),r=h?x:m;
 return big(h?'Land Transaction Tax (higher rates)':'Land Transaction Tax (main rates)',gbp(r.t,0),'Effective rate '+pc(r.t/Math.max(p,1),2))+kv(r.rows.concat([['Total LTT',gbp(r.t,0),'t'],[h?'Main rates would be':'Higher rates would be',gbp(h?m.t:x.t,0)],['Difference',gbp(x.t-m.t,0)]]))+'<p class="note">Residential property in Wales. Higher rates apply to additional dwellings and to most purchases by companies. File the LTT return and pay within 30 days of the day after completion.</p>'}'''
FAQ=[
("How much LTT will I pay on a £300,000 house in Wales?","£4,500 at the main rates: nothing on the first £225,000 and 6% on the remaining £75,000. If it is an additional property, the higher rates give £19,950."),
("Is there first-time buyer relief from Land Transaction Tax?","No. Wales has no first-time buyer relief, but the 0% band on the main rates runs to £225,000, so homes up to that price pay no LTT whoever buys them."),
("What are the LTT higher rates in Wales?","Since 11 December 2024: 5% up to £180,000, 8.5% from £180,001 to £250,000, 10% to £400,000, 12.5% to £750,000, 15% to £1.5 million and 17% above. They apply to the whole price, so a £150,000 buy-to-let pays £7,500."),
("How much LTT on a £450,000 home in Wales?","£14,250 at the main rates (6% of £175,000 = £10,500 plus 7.5% of £50,000 = £3,750), an effective rate of 3.17%. At the higher rates it is £36,200."),
("When do I have to pay Land Transaction Tax?","The LTT return must be filed and the tax paid to the Welsh Revenue Authority within 30 days of the day after completion. A return is needed even when no tax is due. Your solicitor or conveyancer usually does this for you."),
("Is LTT the same as stamp duty?","No. Land Transaction Tax replaced Stamp Duty Land Tax in Wales on 1 April 2018 and has its own bands. Property in England and Northern Ireland pays SDLT and in Scotland LBTT.")]
art='''<h2>How Land Transaction Tax works</h2>
<p>LTT is charged in slices, like income tax: each rate applies only to the part of the price that falls inside its band. You pay the <b>main residential rates</b> when buying your only or main home and the <b>higher residential rates</b> when you will own more than one dwelling (for example a buy-to-let or second home), or when a company buys a home.</p>
<p><b>Formula:</b> LTT = Σ (part of price inside each band × that band's rate).</p>
<h3>Main residential rates (since 10 October 2022)</h3>
'''+table(['Price band','Rate','Tax on the full band'],[['Up to £225,000','0%','£0'],['£225,001 – £400,000','6%','£10,500'],['£400,001 – £750,000','7.5%','£26,250'],['£750,001 – £1,500,000','10%','£75,000'],['Over £1,500,000','12%','—']])+'''
<h3>Higher residential rates (since 11 December 2024)</h3>
'''+table(['Price band','Rate','Tax on the full band'],[['Up to £180,000','5%','£9,000'],['£180,001 – £250,000','8.5%','£5,950'],['£250,001 – £400,000','10%','£15,000'],['£400,001 – £750,000','12.5%','£43,750'],['£750,001 – £1,500,000','15%','£112,500'],['Over £1,500,000','17%','—']])+'''
<h3>Worked examples</h3>
'''+table(['Price','LTT – main rates','Effective','LTT – higher rates','Effective'],[['£150,000','£0','0%','£7,500','5.00%'],['£225,000','£0','0%','£12,825','5.70%'],['£250,000','£1,500','0.60%','£14,950','5.98%'],['£300,000','£4,500','1.50%','£19,950','6.65%'],['£450,000','£14,250','3.17%','£36,200','8.04%'],['£600,000','£25,500','4.25%','£54,950','9.16%'],['£800,000','£41,750','5.22%','£81,200','10.15%']])+'''
<p class="note">Example: £450,000 at main rates = 6% × £175,000 (£10,500) + 7.5% × £50,000 (£3,750) = £14,250. All figures from the calculator above.</p>
<h3>Practical points and common mistakes</h3>
<ul><li><b>Wales, not England:</b> use this only for property in Wales. Stamp Duty Land Tax bands and first-time buyer relief do not apply.</li>
<li><b>Higher rates for additional homes:</b> buying a second home or buy-to-let while you still own another dwelling usually triggers the higher rates on the whole price.</li>
<li><b>£40,000 threshold:</b> the higher rates apply to residential property bought for £40,000 or more when you already own a dwelling.</li><li><b>Replacing your main home:</b> if you buy a new main home before selling the old one, you pay the higher rates first and can claim a refund of the difference if you sell your previous main home within 3 years of buying the new one.</li>
<li><b>Deadline:</b> the return and payment are due within 30 days of the day after completion, even if no tax is payable; late filing and late payment attract penalties and interest.</li><li><b>Non-residential and mixed property</b> uses different bands: 0% to £225,000, 1% to £250,000, 5% to £1 million and 6% above (since 22 December 2020).</li>
<li><b>Budget for it:</b> LTT cannot be added to most mortgages, so plan it in cash alongside legal fees and surveys.</li></ul>
'''+faq_html(FAQ)+'''
<p class="note">Sources (checked 22 Nov 2026): <a href="https://www.gov.wales/land-transaction-tax-rates-and-bands" rel="nofollow">Welsh Revenue Authority – Land Transaction Tax rates and bands</a> (main and higher residential rates); <a href="https://www.gov.wales/land-transaction-tax-overview" rel="nofollow">LTT overview</a> (30-day return and payment, no first-time buyer relief); <a href="https://www.gov.wales/higher-rates-land-transaction-tax-overview" rel="nofollow">Higher rates overview</a> (£40,000 threshold); <a href="https://www.gov.wales/claim-refund-land-transaction-tax-higher-rates" rel="nofollow">Claim a refund of higher rates</a> (3-year window). Examples calculated with the calculator on this page. Not tax advice.</p>'''
print(build('/uk/ltt-calculator.html','LTT Calculator Wales 2026 – Land Transaction Tax & Higher Rates',
 'Work out Welsh Land Transaction Tax in 2026: 0% to £225,000 then 6%–12%, higher rates of 5%–17% for second homes and buy-to-lets, band-by-band breakdown and worked examples.',art,FAQ,calc=calc))
