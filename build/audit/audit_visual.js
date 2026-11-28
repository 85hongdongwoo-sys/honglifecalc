// 표본 페이지를 휴대폰 크기로 열어: 가로 넘침, 잘린 글자, 디자인 밖 색, 그래프 상태, 오류 글자, 스크립트 오류
const {chromium}=require('playwright');const fs=require('fs');
const list=fs.readFileSync(process.argv[2],'utf8').trim().split('\n');const base=process.argv[3];const out=process.argv[4];
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
const res=[];let i=0;
for(const u of list){i++;const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e.message).slice(0,160)));
 try{await p.goto(base+u,{waitUntil:'domcontentloaded',timeout:25000});await p.waitForTimeout(1200);
  await p.evaluate(()=>{const f=document.querySelector('form#form, form.card, .card.form');const btn=f&&f.querySelector('button[type=submit],button.calc,button.primary');if(btn)btn.click();});
  await p.waitForTimeout(500);
  const r=await p.evaluate(()=>{
   const W=innerWidth;const o={};o.overflow=document.documentElement.scrollWidth>W+2?document.documentElement.scrollWidth:0;
   function hue(c){const m=c.match(/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?/);if(!m)return null;const r=+m[1],g=+m[2],b=+m[3];const a=m[4]===undefined?1:+m[4];if(a<.15)return null;const mx=Math.max(r,g,b),mn=Math.min(r,g,b);if(mx-mn<24)return null;let h;if(mx===r)h=((g-b)/(mx-mn))%6;else if(mx===g)h=(b-r)/(mx-mn)+2;else h=(r-g)/(mx-mn)+4;h*=60;if(h<0)h+=360;return h}
   function sel(e){let s=e.tagName.toLowerCase();if(e.id)s+='#'+e.id;if(typeof e.className==='string'&&e.className.trim())s+='.'+e.className.trim().split(/\s+/).slice(0,2).join('.');const pp=e.parentElement;return (pp&&pp!==document.body?(pp.tagName.toLowerCase()+(typeof pp.className==='string'&&pp.className.trim()?'.'+pp.className.trim().split(/\s+/)[0]:'')+'>'):'')+s}
   const warm={};const wide=[];const clip=[];
   for(const e of document.querySelectorAll('body *')){if(!e.getClientRects().length)continue;
    if(e.closest('svg,canvas,.hlv,.hlh-fortune,.kv .pos,.neg,.pos,img,video,iframe,[data-keep-color]'))continue;
    const cs=getComputedStyle(e);
    for(const pr of ['color','backgroundColor','borderTopColor']){const v=cs[pr];const h=hue(v);if(h===null)continue;
     if(pr==='borderTopColor'&&parseFloat(cs.borderTopWidth)===0)continue;
     if(pr==='color'&&!(e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())))continue;
     if((h>=20&&h<=60)||(h>=85&&h<=170)){const k=sel(e)+' '+pr+' '+v;warm[k]=(warm[k]||0)+1;}}
    const rc=e.getBoundingClientRect();if(rc.right>W+2&&cs.position!=='fixed'&&!e.closest('[style*="overflow"],.g-cards,table,pre,.hl-scroll,nav,.subtabs,.row'))wide.push(sel(e));
    if((cs.overflow==='hidden'||cs.overflowX==='hidden')&&cs.textOverflow!=='ellipsis'&&e.scrollWidth>e.clientWidth+3&&e.clientWidth>0&&e.textContent.trim().length&&e.children.length<3)clip.push(sel(e));}
   o.warm=Object.entries(warm).sort((a,b)=>b[1]-a[1]).slice(0,5);o.warmN=Object.keys(warm).length;o.wide=[...new Set(wide)].slice(0,5);o.clip=[...new Set(clip)].slice(0,5);
   const charts=[...document.querySelectorAll('.hlv')];o.charts=charts.length;o.chartEmpty=charts.filter(c=>{const s=c.querySelector('svg');return !s||!s.querySelector('path,rect,circle,line,polyline');}).length;
   const out=document.querySelector('#out,.res,.result');const tx=(out?out.innerText:'')+' '+charts.map(c=>c.innerText).join(' ');
   const m=tx.match(/NaN|undefined|Infinity|\[object/);o.badOut=m?tx.slice(Math.max(0,m.index-40),m.index+30).replace(/\s+/g,' '):'';
   o.outEmpty=out?!out.innerText.trim():null;
   return o});
  r.errs=errs.slice(0,3);r.u=u;res.push(r);
 }catch(e){res.push({u,load:String(e.message).slice(0,120)})}
 await p.close();if(i%50===0)console.log(i,'/',list.length);}
fs.writeFileSync(out,JSON.stringify(res));await b.close()})();
