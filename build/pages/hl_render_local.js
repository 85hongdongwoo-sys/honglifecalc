function build(spec){
  const form=$('form'), out=$('out'), q={};
  const today=new Date().toISOString().slice(0,10);
  form.innerHTML = spec.f.map(([key,label,type,a,b])=>{
    const L=T(label);
    if(type==='select'){ const def=T(b)||a[0][0]; return `<div class="field"><label for="f_${key}">${L}</label><select id="f_${key}">${a.map(([v,l])=>`<option value="${v}"${v===def?' selected':''}>${T(l)}</option>`).join('')}</select></div>`; }
    if(type==='check'){ return `<label class="check"><input type="checkbox" id="f_${key}"${T(a)?' checked':''}><span>${L}</span></label>`; }
    if(type==='date'){ return `<div class="field"><label for="f_${key}">${L}</label><input type="date" id="f_${key}" value="${a==='today'?today:a}"></div>`; }
    const dv=T(a); const shown= type==='money'? fmt(dv) : Number(dv).toLocaleString(LOC,{useGrouping:false,maximumFractionDigits:4}); return `<div class="field"><label for="f_${key}">${L}</label><input id="f_${key}" inputmode="decimal" value="${shown}"></div>`;
  }).join('');
  const read=()=>{ const v={}; spec.f.forEach(([key,,type])=>{ const el=$('f_'+key);
    if(type==='check') v[key]=el.checked; else if(type==='select'||type==='date') v[key]=el.value;
    else { const raw=String(el.value).replace(/\s/g,''); const s=raw.replace(/,/g,''); v[key]=parseFloat(s)||0; } }); return v; };
  const render=()=>{ const r=spec.run(read());
    out.innerHTML=`<p class="kicker">${r.k||''}</p><p class="big">${r.big}</p><p class="bigsub">${r.sub||''}</p>`+
      (r.rows&&r.rows.length?`<table>${r.rows.map(x=> x[0]==='__t'?`<tr class="t"><td>${x[1]}</td><td class="n">${x[2]}</td></tr>`:`<tr${String(x[2]).startsWith('−')?' class="m"':''}><td>${x[0]}${x[1]?`<span class="c">${x[1]}</span>`:''}</td><td class="n">${x[2]}</td></tr>`).join('')}</table>`:'')+
      (r.note?`<p class="note">${r.note}</p>`:''); };
  form.addEventListener('input',render); form.addEventListener('change',render);
  form.addEventListener('focusout',e=>{ const el=e.target; if(el.tagName!=='INPUT'||el.type!=='text'&&el.type!=='') return; const key=el.id.slice(2); const f=spec.f.find(x=>x[0]===key); if(f&&f[2]==='money'){ const v=read()[key]; el.value=fmt(v); } });
  render();
}
