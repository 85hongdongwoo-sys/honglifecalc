/* page-local engine for /es/calculadora-finiquito.html (México, LFT) — replaces the shared g.js finiquito spec */
(function(){
const LOC='es-MX';
const fmt=(n,d=0)=>(isFinite(n)?n:0).toLocaleString(LOC,{minimumFractionDigits:d,maximumFractionDigits:d});
const money=(n,d)=>(n<0?'-':'')+'$'+fmt(Math.abs(n),d??2);
const $=id=>document.getElementById(id);
const T=o=>(o&&typeof o==='object'&&!Array.isArray(o))?o.es:o;
const SM={gen:315.04, fr:440.87};
function vacDays(y){ if(y<1) return 12; if(y<=5) return 12+2*(Math.ceil(y)-1); return 20+2*Math.ceil((Math.ceil(y)-5)/5); }
function run(v){
  const a=new Date(v.ini+'T00:00'), b=new Date(v.fin+'T00:00'); const days=Math.round((b-a)/864e5)+1; if(!(days>0)) return {k:'',big:'—',sub:'',rows:[]};
  const yrs=days/365, sd=v.s/30, pend=sd*v.pend;
  const yStart=new Date(b.getFullYear(),0,1), dY=Math.round((b-Math.max(yStart,a))/864e5)+1;
  const ag=sd*15*dY/365;
  const anniv=new Date(b.getFullYear(),a.getMonth(),a.getDate()); if(anniv>b) anniv.setFullYear(b.getFullYear()-1);
  const sinceAnniv=Math.max(0,Math.round((b-Math.max(anniv,a))/864e5)), vd=vacDays(Math.max(yrs,0.01)), vac=Math.max(0, sd*(vd*sinceAnniv/365 - v.vacT)), prima=vac*0.25;
  let rows=[['Sueldo pendiente',v.pend+' días',money(pend)],['Aguinaldo proporcional',`15 días × ${dY}/365`,money(ag)],['Vacaciones proporcionales',`${vd} días/año × ${sinceAnniv}/365 − tomados`,money(vac)],['Prima vacacional','25% de las vacaciones',money(prima)]];
  let total=pend+ag+vac+prima, m3=0,d20=0,pa=0;
  const sdTope=Math.min(sd,2*SM[v.zona]);
  if(v.tipo==='desp'){ m3=sd*90; pa=sdTope*12*yrs; rows.push(['Indemnización 3 meses','90 días de salario (art. 48 y 50)',money(m3)]);
    if(v.v20==='si'){ d20=sd*20*yrs; rows.push(['20 días por año','art. 50: sin reinstalación (art. 49) o rescisión del trabajador (art. 52)',money(d20)]); }
    rows.push(['Prima de antigüedad','12 días por año, tope 2 salarios mínimos (art. 162)',money(pa)]); total+=m3+d20+pa; }
  else if(yrs>=15){ pa=sdTope*12*yrs; rows.push(['Prima de antigüedad','renuncia con 15 años o más (art. 162)',money(pa)]); total+=pa; }
  rows.push(['__t',v.tipo==='desp'?'Total liquidación (bruto)':'Total finiquito (bruto)',money(total)]);
  return {k:v.tipo==='desp'?'Liquidación estimada':'Finiquito estimado', big:money(total), sub:`Antigüedad ${fmt(yrs,2)} años · salario diario ${money(sd)}`, rows,
    note:'Cálculo con la LFT vigente (vacaciones dignas: 12 días el primer año). Montos brutos antes de ISR, con salario diario = sueldo mensual ÷ 30; las indemnizaciones se calculan legalmente con salario integrado, que suele ser algo mayor. Si te despidieron, la PROFEDET asesora gratis.',
    _n:{yrs,sd,pend,ag,vd,sinceAnniv,vac,prima,m3,d20,pa,total}};
}
const spec={f:[ ['s',{es:'Sueldo mensual bruto ($)'},'money',{es:15000}],
      ['ini',{es:'Fecha de ingreso'},'date','2021-06-01'],['fin',{es:'Fecha de salida'},'date','today'],
      ['pend',{es:'Días de sueldo pendientes de pago'},'num',{es:10}],
      ['vacT',{es:'Días de vacaciones ya tomados este año'},'num',{es:0}],
      ['tipo',{es:'Motivo de salida'},'select',[['ren',{es:'Renuncia voluntaria (finiquito)'}],['desp',{es:'Despido injustificado (liquidación)'}]]],
      ['v20',{es:'¿Incluir 20 días por año? (solo despido)'},'select',[['no',{es:'No — indemnización de 3 meses (art. 48)'}],['si',{es:'Sí — sin reinstalación o rescisión (art. 49, 50, 52)'}]]],
      ['zona',{es:'Zona'},'select',[['gen',{es:'Resto del país'}],['fr',{es:'Zona libre de la frontera norte'}]]] ], run};
if(typeof module!=='undefined'){ module.exports={run}; return; }
