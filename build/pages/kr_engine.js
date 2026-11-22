/* page-local engine for /en/korea-salary-calculator.html (replaces the shared g.js krsalary spec) */
(function(){
const LOC='en-US';
const fmt=(n,d=0)=>(isFinite(n)?n:0).toLocaleString(LOC,{minimumFractionDigits:d,maximumFractionDigits:d});
const krw=n=>'₩'+fmt(Math.round(n));
const pct=(n,d=2)=>fmt(n,d)+'%';
const $=id=>document.getElementById(id);
const T=o=>(o&&typeof o==='object'&&!Array.isArray(o))?o.en:o;
/* Earned income deduction, rates incl. 40/42/45% brackets, earned income tax credit with cap.
   Standard tax credit (130,000) only if the insurance-premium deduction is not claimed: the lower result is used. */
function krTax(g,pen,ins,deps){
  let d; if(g<=5e6)d=g*.7; else if(g<=15e6)d=3.5e6+(g-5e6)*.4; else if(g<=45e6)d=7.5e6+(g-15e6)*.15; else if(g<=1e8)d=12e6+(g-45e6)*.05; else d=14.75e6+(g-1e8)*.02;
  d=Math.min(d,2e7);
  const one=(insDed,std)=>{ const base=Math.max(0,g-d-1.5e6*(1+deps)-pen-insDed);
    const B=[[14e6,.06],[5e7,.15],[88e6,.24],[15e7,.35],[3e8,.38],[5e8,.40],[1e9,.42],[Infinity,.45]];
    let t=0,lo=0; for(const [hi,r] of B){ if(base>lo) t+=(Math.min(base,hi)-lo)*r; lo=hi; }
    let cr=t<=13e5?t*.55:715000+(t-13e5)*.3; let cap; if(g<=33e6)cap=74e4; else if(g<=7e7)cap=Math.max(66e4,74e4-(g-33e6)*.008); else if(g<=12e7)cap=Math.max(5e5,66e4-(g-7e7)*.5); else cap=Math.max(2e5,5e5-(g-12e7)*.5);
    cr=Math.min(cr,cap); return Math.max(0,t-cr-std); };
  return Math.min(one(ins,0),one(0,130000))*1.1;
}
const KR={2026:{pen:.0475,caps:[[6,6370000],[6,6590000]],h:.03595,care:.1314,careLbl:'13.14%'},
          2027:{pen:.05,caps:[[12,6590000]],h:.03595,care:.1390,careLbl:'13.90%'}};
const EMP=.009;
function run(v){
  const nt=Math.min(v.nt,200000)*12, taxable=Math.max(v.g-nt,0), mon=taxable/12, Y=KR[+v.yr]||KR[2027];
  const pen=Y.caps.reduce((s,[m,c])=>s+Math.min(mon,c)*Y.pen*m,0), h=taxable*Y.h, care=h*Y.care, emp=taxable*EMP;
  const tax=krTax(taxable,pen,h+care+emp,Math.max(0,Math.floor(v.deps))), net=v.g-pen-h-care-emp-tax;
  const flatTax=v.g*0.19*1.1, netFlat=v.g-pen-h-care-emp-flatTax;
  const capTxt=+v.yr===2026?'capped at ₩6.37M (Jan–Jun) / ₩6.59M (Jul–Dec) monthly income':'capped at ₩6.59M monthly income';
  const rows=[[`National Pension (${(Y.pen*100).toFixed(2)}%)`,capTxt,krw(-pen)],['Health insurance (3.595%)','',krw(-h)],[`Long-term care (${Y.careLbl} of health)`,'',krw(-care)],['Employment insurance (0.9%)','',krw(-emp)],['Income tax + local tax','progressive rates, standard deductions',krw(-tax)],['__t','Take-home per year',krw(net)]];
  if(v.flat) rows.push(['19% flat-rate option','20.9% incl. local tax on gross pay (no deductions)', krw(netFlat/12)+' /mo']);
  return {k:'Monthly take-home pay', big:krw(net/12), sub:`${krw(net)} per year · ${pct(v.g?net/v.g*100:0,1)} of gross`, rows:rows.map(r=>[r[0],r[1],String(r[2]).replace('₩-','−₩')]),
    note:`The flat 19% option is for foreign employees, for a limited period after they first start work in Korea. ${v.flat?(netFlat>net?'For your salary the flat rate gives more take-home pay.':'For your salary the normal progressive rates give more take-home pay.'):''} Monthly withholding follows the simplified tax table and is settled in the year-end tax settlement (Feb). Child tax credits and other credits are not included.`,
    _n:{pen,h,care,emp,tax,net,netFlat}};
}
const spec={f:[ ['g',{en:'Annual salary before tax (KRW)'},'money',{en:42000000}],
      ['nt',{en:'Non-taxable meal allowance (KRW / month)'},'money',{en:200000}],
      ['deps',{en:'Dependents (spouse, children)'},'num',{en:0}],
      ['yr',{en:'Tax year'},'select',[['2026',{en:'2026'}],['2027',{en:'2027'}]],{en:'2027'}],
      ['flat',{en:'Compare with 19% flat tax for foreigners'},'check',{en:true}] ], run};
if(typeof module!=='undefined'){ module.exports={run}; return; }
