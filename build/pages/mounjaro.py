"""마운자로(티르제파타이드) 용량·일정·체중 감소 계산기 — 나라·언어별 페이지 생성 (2026-11-28).
영어판을 먼저 만들고, 나라별 판은 L(언어 사전)과 C(나라 정보)를 더해 같은 계산기로 만든다.
틀: 같은 사이트의 TDEE 계산기 페이지 머리말(스타일·광고·분석 태그)을 그대로 쓰고 본문만 새로 쓴다.
사용: python3 build/pages/mounjaro.py <tdee 원본 html> <나라코드...>   → overlay/... 에 저장
수치 출처: FDA 허가 문서(Mounjaro/Zepbound), SURMOUNT-1(N Engl J Med 2022;387:205-216)."""
import html, json, os, re, sys

TPL = {'en': sys.argv[1]}
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

PAGES = {
  'en': dict(
    lang='en', path='/en/health/mounjaro-dose-calculator.html', hub='/en/health/',
    title='Mounjaro Dose Calculator – Tirzepatide Dosing Schedule, Missed Dose & Weight Loss Tracker',
    desc='Check your Mounjaro or Zepbound (tirzepatide) dose step against the label schedule (2.5 mg start, +2.5 mg every 4 weeks, max 15 mg), plan injection dates, handle a missed dose, convert mg to mL and syringe units, and compare your weight loss with the SURMOUNT-1 trial.',
    h1='Mounjaro <b>Dose Calculator</b> (tirzepatide schedule &amp; weight loss)',
    kicker='💪 Health & fitness', lead='For people already prescribed Mounjaro or Zepbound. Results update as you type.',
    brand='Hong Life Calculators', hubname='Health & fitness',
    foot='For information only — not a diagnosis or medical advice. Always follow the dose your prescriber and pharmacist give you.',
  ),
}

# 화면 문구 (언어별)
T = {
 'en': {
  'f_head': 'Your treatment', 'first': 'Date of your first injection', 'dose': 'Current weekly dose', 'since': 'Date you started this dose',
  'last': 'Date of your last injection', 'unit': 'Weight unit', 'w0': 'Weight when you started', 'w1': 'Weight today', 'ht': 'Height (cm, optional – for BMI)',
  'prod': 'Your product', 'p_pen': 'Single-dose pen (fixed dose)', 'p_kwik': 'KwikPen (4 fixed doses per pen)', 'p_vial': 'Vial (draw with a syringe)',
  'lab_mg': 'Vial label: total mg', 'lab_ml': 'Vial label: total mL', 'conc_hint': 'Copy both numbers from your vial label, e.g. “5 mg/0.5 mL” (single-dose vial) or “20 mg/2.4 mL” (four-dose vial).',
  'r_over': 'This is more liquid than the vial holds – check the label numbers and your prescribed dose.',
  'r_step': 'Dose step', 'of6': 'of 6', 'r_weeks': 'Weeks on this dose', 'r_next': 'Earliest date the label allows a step up',
  'r_max': 'You are on the maximum dose (15 mg).', 'r_fast': 'This dose was reached faster than the label’s minimum of 4 weeks per step. Please check with your prescriber.',
  'r_ok': 'Your dose step matches the label schedule.', 'r_due': 'Next injection due', 'r_late': 'days since the dose was due',
  'r_take': 'Missed dose: you are within 4 days (96 hours) – take it as soon as you can.',
  'r_skip': 'Missed dose: more than 4 days have passed – skip it and take your next dose on the usual day',
  'r_you': 'You have been on treatment for', 'r_lost': 'Weight lost', 'r_pct': 'Change from start', 'r_bmi': 'BMI now', 'r_trial': 'SURMOUNT-1 average at 72 weeks on this dose',
  'r_vol': 'Volume to inject', 'r_units': 'On a U-100 insulin syringe', 'units': 'units',
  'r_pen': 'No measuring needed: your pen delivers the full dose. Do not draw medicine out of a pen with a syringe.',
  'r_kwik': 'The KwikPen is set to one fixed dose of 0.6 mL. Do not try to dial a different amount or draw extra doses from it.',
  'sched': 'Your next 6 injection days', 'chart': 'Your weight change vs. clinical trial averages (72 weeks)',
  'you': 'You', 'placebo': 'Placebo', 'fill': 'Fill in the dates and doses', 'na': '—',
  'warn': '<b>Important:</b> this tool checks your numbers against the official label; it does not decide your dose. Never change your dose, skip steps or use a product that wasn’t prescribed for you. Tirzepatide is a prescription medicine.',
  'wk': 'weeks', 'days': 'days', 'kg': 'kg', 'lb': 'lb',
 },
}

# ---------------- 영국 (en-GB) — 2026-11-28 ----------------
T['en-GB'] = dict(T['en'])
T['en-GB'].update({
  'p_kwik': 'KwikPen (4 doses per pen)', 'p_pen': 'Single-dose pen (older packs)',
  'warn': '<b>Important:</b> this tool checks your numbers against the UK licence (MHRA/SmPC); it does not decide your dose. Never change your dose, skip steps or use a pen that wasn’t prescribed for you. Mounjaro is a prescription-only medicine in the UK.',
  'nhs_h': 'NHS eligibility check (England)', 'cm_htn': 'High blood pressure (hypertension)', 'cm_lip': 'High cholesterol / blood fats (dyslipidaemia)',
  'cm_osa': 'Obstructive sleep apnoea', 'cm_cvd': 'Heart or circulation disease (ASCVD)', 'cm_t2d': 'Type 2 diabetes',
  'eth': 'South Asian, Chinese, other Asian, Middle Eastern, Black African or African-Caribbean background (thresholds 2.5 lower)',
  'r_nhs': 'NHS priority cohorts (NHS England interim guidance)', 'r_bmi0': 'BMI when you started', 'r_cm': 'Qualifying conditions ticked',
  'nhs_y2': 'You appear to fit the 2026/27 priority group (BMI from 35 with at least 4 qualifying conditions, or the 2025/26 group). Ask your GP practice about NHS tirzepatide and the required wraparound support.',
  'nhs_y3': 'Not in the 2026/27 groups yet, but you would fit the planned 2027/28 group (BMI from 40 with at least 3 qualifying conditions). Your GP can tell you when local services open.',
  'nhs_no': 'You don’t appear to fit the NHS priority groups for 2025–28. The UK licence still allows a private prescription from BMI 30, or 27 with a weight-related condition, after a clinical assessment.',
  'r_cost': 'NHS list price for your strength', 'r_pen': 'per KwikPen (4 weeks)', 'r_year': 'About a year (13 pens) at list price',
  'cost_note': 'List prices from September 2025. Private pharmacies set their own prices; NHS patients in England pay the standard prescription charge unless exempt.',
})
PAGES['uk'] = dict(
  tpl=sys.argv[1].replace('/en/health/tdee-calculator.html','/uk/income-tax-calculator.html'), lang='en-GB', t='en-GB', path='/uk/mounjaro-dose-calculator.html', hub='/uk/', products=['kwik', 'pen'],
  title='Mounjaro Dose Calculator UK – KwikPen Schedule, Missed Dose, NHS Eligibility & Cost',
  desc='UK Mounjaro (tirzepatide) KwikPen calculator: check your dose step (2.5 mg for 4 weeks, then up 2.5 mg every 4 weeks to 15 mg), plan injection days, handle a missed dose, check NHS England eligibility (BMI and conditions) and see the £133–£330 list price per pen.',
  h1='Mounjaro <b>Dose Calculator</b> UK (KwikPen, NHS &amp; cost)',
  kicker='🇬🇧 UK health', lead='For people in the UK already prescribed Mounjaro. Results update as you type.',
  brand='Hong Life Calculators', hubname='UK calculators',
  foot='For information only — not a diagnosis or medical advice. Always follow the dose your prescriber and pharmacist give you.',
  xdata={'price': {'2.5': 133, '5': 180, '7.5': 255, '10': 255, '12.5': 330, '15': 330}},
  extra_form=None,
)
PAGES['uk']['extra_form'] = ('<div class="mj-sec">{h}</div>'.format(h=T['en-GB']['nhs_h']) + ''.join(
  f'<label class="chk"><input type="checkbox" class="cm" id="cm_{k}"> {T["en-GB"]["cm_"+k]}</label>' for k in ('htn', 'lip', 'osa', 'cvd', 't2d')) +
  f'<label class="chk"><input type="checkbox" id="eth"> {T["en-GB"]["eth"]}</label>')
PAGES['uk']['extra_js'] = r"""
 { const ht=v('ht'),w0=v('w0'),u=$('u').value; if(isFinite(ht)&&ht>0&&isFinite(w0)){ const kg0=u==='lb'?w0*0.45359237:w0, b0=kg0/Math.pow(ht/100,2), n=document.querySelectorAll('.cm:checked').length, adj=$('eth').checked?2.5:0;
   o+='<div class="mj-sec">'+T.r_nhs+'</div>'+kv([[T.r_bmi0,nf(b0)],[T.r_cm,n]]);
   if(b0>=35-adj&&n>=4)o+='<p class="mj-ok">'+T.nhs_y2+'</p>';else if(b0>=40-adj&&n>=3)o+='<p class="mj-info">'+T.nhs_y3+'</p>';else o+='<p class="mj-info">'+T.nhs_no+'</p>'; }
   const pr=X.price[String(dose)]; if(pr){ o+='<div class="mj-sec">'+T.r_cost+'</div>'+kv([[T.r_cost,'£'+nf(pr,0)+' '+T.r_pen],[T.r_year,'£'+nf(pr*13,0)]])+'<p class="mj-info">'+T.cost_note+'</p>'; } }
"""

TRIAL = {5: 15.0, 10: 19.5, 15: 20.9}   # SURMOUNT-1, 72주 평균 체중 변화율(%) — 2.5·7.5·12.5mg는 유지 용량으로 시험되지 않음
PLACEBO = 3.1


def head(tpl, P):
    s = open(tpl, encoding='utf-8').read()
    h = s[:s.index('</head>')]
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', '', h, flags=re.S)
    h = re.sub(r'<title>.*?</title>', '<title>' + html.escape(P['title']) + '</title>', h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + html.escape(P['desc']) + '">', h)
    url = 'https://honglifecalc.com' + P['path']
    h = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + url + '">', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + html.escape(P['title']) + '">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + html.escape(P['desc']) + '">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="' + url + '">', h)
    h = re.sub(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="' + html.escape(P['title']) + '">', h)
    h = re.sub(r'<!--hl:alt-->.*?<!--/hl:alt-->', '<!--hl:alt-->' + ''.join(
        f'<link rel="alternate" hreflang="{q["lang"]}" href="https://honglifecalc.com{q["path"]}">' for q in PAGES.values()) +
        f'<link rel="alternate" hreflang="x-default" href="https://honglifecalc.com{PAGES["en"]["path"]}"><!--/hl:alt-->', h, flags=re.S)
    if '<!--hl:alt-->' not in h:
        h += '<!--hl:alt--><!--/hl:alt-->'
        h = re.sub(r'<!--hl:alt-->.*?<!--/hl:alt-->', '<!--hl:alt-->' + ''.join(
            f'<link rel="alternate" hreflang="{q["lang"]}" href="https://honglifecalc.com{q["path"]}">' for q in PAGES.values()) +
            f'<link rel="alternate" hreflang="x-default" href="https://honglifecalc.com{PAGES["en"]["path"]}"><!--/hl:alt-->', h, flags=re.S)
    ld = {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': re.sub('<[^>]+>', '', P['h1']).replace('&amp;', '&'),
          'url': url, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any', 'inLanguage': P['lang'],
          'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
          'publisher': {'@type': 'Organization', 'name': 'Hong Life Calculators', 'url': 'https://honglifecalc.com/'}}
    css = '''<style id="mj-css">.mj-row{display:grid;grid-template-columns:1fr 1fr;gap:0 12px}@media(max-width:560px){.mj-row{grid-template-columns:1fr}}
.mj-sec{font-size:13px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:#7c3aed;margin:16px 0 4px}
.mj-ok,.mj-bad,.mj-info{border-radius:12px;padding:10px 12px;margin:10px 0;font-size:14.5px;line-height:1.5}
.mj-ok{background:#ecfdf3;border:1px solid #b7ebc9;color:#14532d}.mj-bad{background:#fff4ed;border:1px solid #fbd0b4;color:#7c2d12}.mj-info{background:#f4f0fe;border:1px solid #ddd0fb;color:#3b1a7a}
.mj-days{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 2px;padding:0;list-style:none}.mj-days li{background:#f4f0fe;border-radius:999px;padding:5px 10px;font-size:13.5px;font-weight:600;color:#3b1a7a}
.mj-bars{margin:8px 0 0}.mj-bar{display:grid;grid-template-columns:92px 1fr 54px;align-items:center;gap:8px;margin:6px 0;font-size:13.5px}.mj-bar i{display:block;height:14px;border-radius:7px;background:#c4b5fd}.mj-bar.me i{background:#7c3aed}.mj-bar b{text-align:right;font-variant-numeric:tabular-nums}
.mj-warn{margin:14px 0 0;font-size:14px;line-height:1.55;background:#fffbeb;border:1px solid #f3dfa2;border-radius:12px;padding:12px 14px}</style>'''
    return h + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>' + css + '</head>', s


def body(P, t, src):
    dsel = ''.join(f'<option value="{d}"{" selected" if d == 5 else ""}>{d} mg</option>' for d in (2.5, 5, 7.5, 10, 12.5, 15))
    form = f'''<form class="card" id="form" onsubmit="return false"><h2>{t['f_head']}</h2>
<div class="mj-row"><label class="f"><span>{t['first']}</span><input type="date" id="d0"></label>
<label class="f"><span>{t['dose']}</span><select id="dose">{dsel}</select></label>
<label class="f"><span>{t['since']}</span><input type="date" id="ds"></label>
<label class="f"><span>{t['last']}</span><input type="date" id="dl"></label></div>
<div class="mj-row"><label class="f"><span>{t['unit']}</span><select id="u"><option value="kg">{t['kg']}</option><option value="lb">{t['lb']}</option></select></label>
<label class="f"><span>{t['ht']}</span><input id="ht" inputmode="decimal" value="{P.get('ht','170')}"></label>
<label class="f"><span>{t['w0']}</span><input id="w0" inputmode="decimal" value="100"></label>
<label class="f"><span>{t['w1']}</span><input id="w1" inputmode="decimal" value="92"></label></div>
<label class="f"><span>{t['prod']}</span><select id="pr">{''.join(f'<option value="{k}">{t["p_"+k]}</option>' for k in P.get('products',['pen','kwik','vial']))}</select></label>
<div id="concw"><div class="mj-row"><label class="f"><span>{t['lab_mg']}</span><input id="lmg" inputmode="decimal" value="5"></label><label class="f"><span>{t['lab_ml']}</span><input id="lml" inputmode="decimal" value="0.5"></label></div><p class="f"><small>{t['conc_hint']}</small></p></div>
{P.get('extra_form','')}<p class="mj-warn">{t['warn']}</p></form>'''
    return f'''<body>
<div class="brand"><div class="in"><a class="logo" href="{P['hub']}"><img class="hl-mark" src="/assets/brand/symbol-small.svg" width="28" height="28" alt="">{P['brand']}</a><span class="flag">💪</span></div></div>
<header class="hero"><div class="in"><span class="year">{P['kicker']}</span><h1>{P['h1']}</h1><p>{P['lead']}</p></div></header>
<main class="wrap">
<section class="app">{form}<section class="card" id="out" aria-live="polite"></section></section>
</main>
<footer><a href="{P['hub']}">{P['hubname']}</a> · {P.get('foot_links','<a href="/">Calculators by country</a> · <a href="/privacy.html">Privacy</a> · <a href="/report-error.html">Report an error</a>')}<br>{P['foot']}<div class="hl-trust" style="margin-top:6px;font-size:13px">{P.get('reviewed','Last reviewed: November 2026 · <a href="/about.html">About</a> · <a href="/editorial-policy.html">Editorial policy</a>')}</div></footer>
<script>
(function(){{'use strict';
const T={json.dumps(t, ensure_ascii=False)},X={json.dumps(P.get('xdata',{}), ensure_ascii=False)},TR={json.dumps(TRIAL)},PL={PLACEBO},LANG='{P['lang']}';
const $=id=>document.getElementById(id),v=id=>{{const x=parseFloat(String($(id).value).replace(',','.'));return isFinite(x)?x:NaN}};
const D=s=>{{if(!s)return null;const d=new Date(s+'T00:00:00');return isNaN(d)?null:d}},DAY=864e5,today=new Date(new Date().toDateString());
const fmt=d=>d.toLocaleDateString(LANG,{{year:'numeric',month:'short',day:'numeric',weekday:'short'}}),add=(d,n)=>new Date(d.getTime()+n*DAY);
const nf=(x,k)=>Number(x).toLocaleString(LANG,{{maximumFractionDigits:k==null?1:k}});
const big=(l,val,s)=>'<div class="big"><span>'+l+'</span><b>'+val+'</b>'+(s?'<em>'+s+'</em>':'')+'</div>';
const kv=r=>'<div class="kv">'+r.map(x=>'<div>'+x[0]+'</div><div>'+x[1]+'</div>').join('')+'</div>';
function iso(d){{return d.toISOString().slice(0,10)}}
// 기본값: 첫 투여 10주 전, 현재 용량 시작 2주 전, 마지막 투여 3일 전
if(!$('d0').value)$('d0').value=iso(add(today,-70));if(!$('ds').value)$('ds').value=iso(add(today,-14));if(!$('dl').value)$('dl').value=iso(add(today,-3));
function run(){{
 if($('concw'))$('concw').style.display=$('pr').value==='vial'?'':'none';
 const d0=D($('d0').value),ds=D($('ds').value),dl=D($('dl').value),dose=v('dose');let o='';
 if(!d0||!ds||!dl||!isFinite(dose)){{$('out').innerHTML=big(T.fill,T.na);return}}
 const step=Math.round(dose/2.5),wk=Math.floor((today-ds)/DAY/7),tot=(today-d0)/DAY/7,need=(step-1)*4;
 o+=big(T.r_step,step+' '+T.of6,dose+' mg');
 const nxt=add(ds,28);
 o+=kv([[T.r_weeks,nf(Math.max(0,wk),0)+' '+T.wk],[T.r_next,dose>=15?'—':fmt(nxt)]]);
 if(dose>=15)o+='<p class="mj-info">'+T.r_max+'</p>';
 if(tot+0.01<need&&dose>2.5)o+='<p class="mj-bad">'+T.r_fast+'</p>';else o+='<p class="mj-ok">'+T.r_ok+'</p>';
 // 다음 투여·놓친 용량
 const due=add(dl,7),late=Math.round((today-due)/DAY);
 if(late<=0)o+=kv([[T.r_due,fmt(due)]]);else if(late<=4)o+=kv([[T.r_due,fmt(due)+' ('+late+' '+T.r_late+')']])+'<p class="mj-bad">'+T.r_take+'</p>';
 else o+=kv([[T.r_due,fmt(due)+' ('+late+' '+T.r_late+')']])+'<p class="mj-bad">'+T.r_skip+' ('+fmt(add(due,7*Math.ceil(late/7)))+').</p>';
 const days=[];if(late>0&&late<=4)days.push('<li>'+fmt(today)+' *</li>');let k=late>0?Math.ceil(late/7):0;if(late>0&&late%7===0)k=late/7;let n0=add(due,7*Math.max(k,0));if(n0<today)n0=add(n0,7);while(days.length<6){{days.push('<li>'+fmt(n0)+'</li>');n0=add(n0,7)}}
 o+='<div class="mj-sec">'+T.sched+'</div><ul class="mj-days">'+days.join('')+'</ul>';
 // 체중
 const u=$('u').value,w0=v('w0'),w1=v('w1'),ht=v('ht');
 if(isFinite(w0)&&isFinite(w1)&&w0>0){{const lost=w0-w1,pct=-lost/w0*100;
  o+='<div class="mj-sec">'+T.chart+'</div>'+kv([[T.r_lost,nf(lost)+' '+T[u]],[T.r_pct,(pct<0?'−':'+')+nf(Math.abs(pct))+'%']]);
  const kg=u==='lb'?w1*0.45359237:w1;if(isFinite(ht)&&ht>0)o+=kv([[T.r_bmi,nf(kg/Math.pow(ht/100,2))]]);
  const rows=[[T.you,Math.max(0,-pct),1],['5 mg',TR[5]],['10 mg',TR[10]],['15 mg',TR[15]],[T.placebo,PL]],mx=Math.max(25,...rows.map(r=>r[1]));
  o+='<div class="mj-bars">'+rows.map(r=>'<div class="mj-bar'+(r[2]?' me':'')+'"><span>'+r[0]+'</span><i style="width:'+(r[1]/mx*100).toFixed(1)+'%"></i><b>−'+nf(r[1])+'%</b></div>').join('')+'</div>';
  const tk=dose>=12.5?15:dose>=7.5?10:5;o+='<p class="mj-info">'+T.r_trial+' ('+tk+' mg): −'+TR[tk]+'%. '+T.r_you+': '+nf(tot,0)+' '+T.wk+'.</p>';}}
 // 단위 변환
 const pr=$('pr').value;
 if(pr==='vial'){{const lm=v('lmg'),ll=v('lml');if(isFinite(lm)&&isFinite(ll)&&lm>0&&ll>0){{const ml=dose/(lm/ll);o+='<div class="mj-sec">'+T.r_vol+'</div>'+kv([[T.r_vol,nf(ml,3)+' mL'],[T.r_units,nf(ml*100,1)+' '+T.units]]);if(ml>ll+1e-9)o+='<p class="mj-bad">'+T.r_over+'</p>';}}}}
 else o+='<p class="mj-info">'+(pr==='kwik'?T.r_kwik:T.r_pen)+'</p>';
 {P.get('extra_js','')}
 $('out').innerHTML=o;
}}
$('form').addEventListener('input',run);$('form').addEventListener('change',run);run();
}})();
</script>
<script src="/assets/share.js" defer></script>
</body>
</html>'''


for code in sys.argv[2:]:
    P = PAGES[code]; t = T[P.get('t', P['lang'])]
    h, src = head(P.get('tpl', TPL['en']), P)
    h = re.sub(r'<html lang="[^"]*"', f'<html lang="{P["lang"]}"', h, count=1)
    out = os.path.join(ROOT, 'overlay', P['path'].lstrip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(h + '\n' + body(P, t, src))
    print('wrote', out)
