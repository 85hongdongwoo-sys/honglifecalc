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

# ---------------- 독일 (de) — 2026-11-28 ----------------
T['de'] = {
  'f_head': 'Ihre Behandlung', 'first': 'Datum der ersten Spritze', 'dose': 'Aktuelle Wochendosis', 'since': 'Seit wann diese Dosis',
  'last': 'Datum der letzten Spritze', 'unit': 'Gewichtseinheit', 'w0': 'Gewicht zu Beginn', 'w1': 'Gewicht heute', 'ht': 'Größe (cm, für den BMI)',
  'prod': 'Ihr Präparat', 'p_kwik': 'KwikPen (4 Dosen pro Pen)', 'p_pen': 'Einzeldosis-Fertigpen (ältere Packung)',
  'lab_mg': 'Etikett: mg', 'lab_ml': 'Etikett: ml', 'conc_hint': '', 'r_over': '',
  'r_step': 'Dosisstufe', 'of6': 'von 6', 'r_weeks': 'Wochen auf dieser Dosis', 'r_next': 'Frühester Termin für die nächste Stufe laut Fachinformation',
  'r_max': 'Sie sind auf der Höchstdosis (15 mg).', 'r_fast': 'Diese Dosis wurde schneller erreicht, als die Fachinformation erlaubt (mindestens 4 Wochen pro Stufe). Bitte mit der verordnenden Ärztin bzw. dem Arzt klären.',
  'r_ok': 'Ihre Dosisstufe passt zum Schema der Fachinformation.', 'r_due': 'Nächste Spritze fällig', 'r_late': 'Tage nach Fälligkeit',
  'r_take': 'Vergessene Dosis: Es sind höchstens 4 Tage (96 Stunden) vergangen – spritzen Sie so bald wie möglich.',
  'r_skip': 'Vergessene Dosis: Mehr als 4 Tage vergangen – auslassen und am gewohnten Wochentag weitermachen',
  'r_you': 'Sie sind in Behandlung seit', 'r_lost': 'Abgenommen', 'r_pct': 'Veränderung seit Beginn', 'r_bmi': 'BMI heute',
  'r_trial': 'Durchschnitt in der Studie SURMOUNT-1 nach 72 Wochen auf dieser Dosis',
  'r_vol': 'Volumen', 'r_units': 'Einheiten', 'units': 'Einheiten',
  'r_pen': 'Nichts abzumessen: Der Pen gibt die volle Dosis ab. Ziehen Sie kein Arzneimittel mit einer Spritze aus einem Pen.',
  'r_kwik': 'Der KwikPen gibt pro Anwendung fest 0,6 ml ab. Keine andere Menge einstellen und keine zusätzlichen Dosen entnehmen – Restflüssigkeit wird mit dem Pen entsorgt.',
  'sched': 'Ihre nächsten 6 Spritztermine', 'chart': 'Ihre Gewichtsveränderung im Vergleich zur Studie (72 Wochen)',
  'you': 'Sie', 'placebo': 'Placebo', 'fill': 'Bitte Daten und Dosis eintragen', 'na': '—',
  'warn': '<b>Wichtig:</b> Dieser Rechner gleicht Ihre Angaben mit der Fachinformation ab – er legt keine Dosis fest. Ändern Sie Ihre Dosis nie eigenmächtig. Mounjaro ist verschreibungspflichtig.',
  'wk': 'Wochen', 'days': 'Tage', 'kg': 'kg', 'lb': 'lb',
  'r_cost': 'Apothekenpreis für Ihre Stärke', 'r_pen1': 'pro KwikPen (4 Wochen)', 'r_year': 'Etwa ein Jahr (13 Pens)',
  'cost_note': 'Preise einer Versandapotheke, Stand November 2026. Zur Gewichtsreduktion zahlen gesetzliche Krankenkassen in der Regel nicht (§ 34 SGB V); bei Typ-2-Diabetes ist Mounjaro erstattungsfähig.',
  'r_bmi0': 'BMI zu Beginn', 'lab_ok': 'Laut EU-Zulassung kommt eine Behandlung zur Gewichtsreduktion ab BMI 30 in Frage, oder ab 27 mit einer gewichtsbedingten Begleiterkrankung.',
}
PAGES['de'] = dict(
  tpl=sys.argv[1].replace('/en/health/tdee-calculator.html','/de/zinseszins-rechner.html'), lang='de', t='de',
  path='/de/mounjaro-dosis-rechner.html', hub='/de/', products=['kwik', 'pen'], ht='175',
  title='Mounjaro Dosis-Rechner – Dosierungsschema, vergessene Dosis, Abnehmen & Kosten (Tirzepatid)',
  desc='Mounjaro (Tirzepatid) KwikPen: Dosisstufe prüfen (2,5 mg für 4 Wochen, dann alle 4 Wochen +2,5 mg bis 15 mg), Spritztermine planen, vergessene Dosis, Gewichtsabnahme mit SURMOUNT-1 vergleichen und Apothekenpreise von 206,80 € bis 490,01 € pro Pen.',
  h1='Mounjaro <b>Dosis-Rechner</b> (Tirzepatid: Schema, Abnehmen &amp; Kosten)',
  kicker='🇩🇪 Gesundheit', lead='Für Menschen, denen Mounjaro bereits verordnet wurde. Ergebnisse aktualisieren sich beim Tippen.',
  brand='Hong Life Rechner', hubname='Rechner für Deutschland',
  foot='Nur zur Information – keine Diagnose und keine ärztliche Beratung. Halten Sie sich immer an die Dosis, die Ihre Ärztin, Ihr Arzt oder Ihre Apotheke vorgibt.',
  foot_links='<a href="/">Rechner nach Ländern</a> · <a href="/privacy.html">Datenschutz</a> · <a href="/report-error.html">Fehler melden</a>',
  reviewed='Zuletzt geprüft: November 2026',
  xdata={'price': {'2.5': 206.80, '5': 277.60, '7.5': 383.80, '10': 383.80, '12.5': 490.01, '15': 490.01}},
  extra_js=r"""
 { const ht=v('ht'),w0=v('w0'),u=$('u').value; if(isFinite(ht)&&ht>0&&isFinite(w0)){ const kg0=u==='lb'?w0*0.45359237:w0; o+=kv([[T.r_bmi0,nf(kg0/Math.pow(ht/100,2))]])+'<p class="mj-info">'+T.lab_ok+'</p>'; }
   const pr=X.price[String(dose)]; if(pr){ o+='<div class="mj-sec">'+T.r_cost+'</div>'+kv([[T.r_cost,pr.toLocaleString('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2})+' € '+T.r_pen1],[T.r_year,nf(pr*13,0)+' €']])+'<p class="mj-info">'+T.cost_note+'</p>'; } }
""",
)

# ---------------- 스페인어 (es: 스페인, es-MX: 멕시코) — 2026-11-28 ----------------
T['es'] = {
  'f_head': 'Tu tratamiento', 'first': 'Fecha de tu primera inyección', 'dose': 'Dosis semanal actual', 'since': 'Fecha en que empezaste esta dosis',
  'last': 'Fecha de tu última inyección', 'unit': 'Unidad de peso', 'w0': 'Peso al empezar', 'w1': 'Peso hoy', 'ht': 'Estatura (cm, para el IMC)',
  'prod': 'Tu presentación', 'p_kwik': 'Pluma KwikPen (4 dosis por pluma)', 'p_pen': 'Pluma de dosis única', 'p_vial': 'Vial / frasco (con jeringa)',
  'lab_mg': 'Etiqueta del vial: mg', 'lab_ml': 'Etiqueta del vial: ml', 'conc_hint': 'Copia los dos números de la etiqueta, por ejemplo «2,5 mg/0,5 ml».',
  'r_over': 'Es más líquido del que contiene el vial: revisa la etiqueta y la dosis que te recetaron.',
  'r_step': 'Escalón de dosis', 'of6': 'de 6', 'r_weeks': 'Semanas con esta dosis', 'r_next': 'Fecha más temprana para subir según la ficha técnica',
  'r_max': 'Estás en la dosis máxima (15 mg).', 'r_fast': 'Llegaste a esta dosis más rápido de lo que indica la ficha técnica (mínimo 4 semanas por escalón). Consúltalo con tu médico.',
  'r_ok': 'Tu escalón de dosis coincide con la pauta de la ficha técnica.', 'r_due': 'Próxima inyección', 'r_late': 'días de retraso',
  'r_take': 'Dosis olvidada: han pasado 4 días (96 horas) o menos – inyéctala en cuanto puedas.',
  'r_skip': 'Dosis olvidada: han pasado más de 4 días – sáltala y ponte la siguiente en tu día habitual',
  'r_you': 'Llevas en tratamiento', 'r_lost': 'Peso perdido', 'r_pct': 'Cambio desde el inicio', 'r_bmi': 'IMC hoy',
  'r_trial': 'Media del ensayo SURMOUNT-1 a las 72 semanas con esta dosis',
  'r_vol': 'Volumen a inyectar', 'r_units': 'En una jeringa de insulina U-100', 'units': 'unidades',
  'r_pen': 'No hace falta medir: la pluma administra la dosis completa. No extraigas medicamento de una pluma con jeringa.',
  'r_kwik': 'La KwikPen administra siempre 0,6 ml por dosis. No intentes marcar otra cantidad ni sacar dosis extra; el líquido sobrante se desecha con la pluma.',
  'sched': 'Tus próximas 6 inyecciones', 'chart': 'Tu cambio de peso frente a las medias del ensayo (72 semanas)',
  'you': 'Tú', 'placebo': 'Placebo', 'fill': 'Completa las fechas y la dosis', 'na': '—',
  'warn': '<b>Importante:</b> esta herramienta compara tus datos con la ficha técnica; no decide tu dosis. Nunca cambies la dosis por tu cuenta. Mounjaro es un medicamento con receta.',
  'wk': 'semanas', 'days': 'días', 'kg': 'kg', 'lb': 'lb',
  'r_cost': 'Precio aproximado en farmacia', 'r_pen1': 'por pluma (4 semanas)', 'r_year': 'Aproximadamente un año (13 plumas)',
  'cost_note': 'Precios orientativos publicados por la OCU (julio de 2025). Para adelgazar no está financiado por la sanidad pública; confirma el precio en tu farmacia.',
  'r_bmi0': 'IMC al empezar', 'lab_ok': 'Según la autorización europea, el tratamiento para controlar el peso se plantea a partir de IMC 30, o 27 con una enfermedad relacionada con el peso.',
  'mx_note': 'En México hay pluma KwikPen y viales de dosis única (0.5 ml). Si usas vial, la calculadora convierte tu dosis a mililitros y unidades de jeringa. Compra solo en farmacias establecidas y con receta.',
}
PAGES['es'] = dict(
  tpl=sys.argv[1].replace('/en/health/tdee-calculator.html','/es/pregnancy-due-date-calculator.html'), lang='es', t='es',
  path='/es/calculadora-dosis-mounjaro.html', hub='/es/', products=['kwik'], ht='168',
  title='Calculadora de dosis de Mounjaro – Pauta, dosis olvidada, pérdida de peso y precio en España (tirzepatida)',
  desc='Mounjaro (tirzepatida) KwikPen: comprueba tu escalón de dosis (2,5 mg 4 semanas, luego +2,5 mg cada 4 semanas hasta 15 mg), planifica tus inyecciones, qué hacer si olvidas una dosis, tu pérdida de peso frente al ensayo SURMOUNT-1 y el precio por pluma en España.',
  h1='Calculadora de <b>dosis de Mounjaro</b> (pauta, peso y precio)',
  kicker='🇪🇸 Salud', lead='Para personas a las que ya les han recetado Mounjaro. Los resultados se actualizan al escribir.',
  brand='Hong Life Calculators', hubname='Calculadoras de España',
  foot='Solo informativo: no es un diagnóstico ni consejo médico. Sigue siempre la dosis que te indiquen tu médico y tu farmacéutico.',
  foot_links='<a href="/">Calculadoras por país</a> · <a href="/privacy.html">Privacidad</a> · <a href="/report-error.html">Informar de un error</a>',
  reviewed='Última revisión: noviembre de 2026',
  xdata={'price': {'2.5': 207.91, '5': 271.35, '7.5': 358.71, '10': 358.71, '12.5': 446.07, '15': 446.07}},
  extra_js=r"""
 { const ht=v('ht'),w0=v('w0'),u=$('u').value; if(isFinite(ht)&&ht>0&&isFinite(w0)){ const kg0=u==='lb'?w0*0.45359237:w0; o+=kv([[T.r_bmi0,nf(kg0/Math.pow(ht/100,2))]])+'<p class="mj-info">'+T.lab_ok+'</p>'; }
   const pr=X.price[String(dose)]; if(pr){ o+='<div class="mj-sec">'+T.r_cost+'</div>'+kv([[T.r_cost,pr.toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2})+' € '+T.r_pen1],[T.r_year,nf(pr*13,0)+' €']])+'<p class="mj-info">'+T.cost_note+'</p>'; } }
""",
)
PAGES['mx'] = dict(
  tpl=sys.argv[1].replace('/en/health/tdee-calculator.html','/mx/calculadora-isr.html'), lang='es-MX', t='es',
  path='/mx/calculadora-dosis-mounjaro.html', hub='/mx/', products=['kwik', 'vial'], ht='165',
  title='Calculadora de dosis de Mounjaro México – Pauta, dosis olvidada, vial a ml y unidades, y pérdida de peso',
  desc='Mounjaro (tirzepatida) en México: revisa tu escalón de dosis (2.5 mg 4 semanas y luego +2.5 mg cada 4 semanas hasta 15 mg), calendario de inyecciones, dosis olvidada, conversión del vial de mg a ml y unidades de jeringa, y tu pérdida de peso frente al estudio SURMOUNT-1.',
  h1='Calculadora de <b>dosis de Mounjaro</b> México (pluma y vial)',
  kicker='🇲🇽 Salud', lead='Para personas a las que ya les recetaron Mounjaro. Los resultados se actualizan al escribir.',
  brand='Hong Life Calculators', hubname='Calculadoras México',
  foot='Solo informativo: no es un diagnóstico ni consejo médico. Sigue siempre la dosis que te indiquen tu médico y tu farmacéutico.',
  foot_links='<a href="/">Calculadoras por país</a> · <a href="/privacy.html">Privacidad</a> · <a href="/report-error.html">Informar de un error</a>',
  reviewed='Última revisión: noviembre de 2026',
  extra_js=r"""
 { const ht=v('ht'),w0=v('w0'),u=$('u').value; if(isFinite(ht)&&ht>0&&isFinite(w0)){ const kg0=u==='lb'?w0*0.45359237:w0; o+=kv([[T.r_bmi0,nf(kg0/Math.pow(ht/100,2))]]); }
   o+='<p class="mj-info">'+T.mx_note+'</p>'; }
""",
)

# ---------------- 프랑스 (fr) · 일본 (ja) · 한국 (ko) — 2026-11-28 ----------------
T['fr'] = {
  'f_head': 'Votre traitement', 'first': 'Date de la première injection', 'dose': 'Dose hebdomadaire actuelle', 'since': 'Date de début de cette dose',
  'last': 'Date de la dernière injection', 'unit': 'Unité de poids', 'w0': 'Poids au départ', 'w1': 'Poids aujourd’hui', 'ht': 'Taille (cm, pour l’IMC)',
  'prod': 'Votre stylo', 'p_kwik': 'Stylo KwikPen (4 doses par stylo)', 'p_pen': 'Stylo unidose',
  'lab_mg': '', 'lab_ml': '', 'conc_hint': '', 'r_over': '',
  'r_step': 'Palier de dose', 'of6': 'sur 6', 'r_weeks': 'Semaines à cette dose', 'r_next': 'Date la plus proche pour passer au palier suivant (RCP)',
  'r_max': 'Vous êtes à la dose maximale (15 mg).', 'r_fast': 'Cette dose a été atteinte plus vite que ne le prévoit le RCP (au moins 4 semaines par palier). Parlez-en à votre médecin.',
  'r_ok': 'Votre palier correspond au schéma du RCP.', 'r_due': 'Prochaine injection', 'r_late': 'jours de retard',
  'r_take': 'Dose oubliée : 4 jours (96 heures) ou moins – faites l’injection dès que possible.',
  'r_skip': 'Dose oubliée : plus de 4 jours – ne la faites pas et reprenez le jour habituel',
  'r_you': 'Vous êtes traité(e) depuis', 'r_lost': 'Poids perdu', 'r_pct': 'Évolution depuis le début', 'r_bmi': 'IMC aujourd’hui',
  'r_trial': 'Moyenne de l’étude SURMOUNT-1 à 72 semaines à cette dose', 'r_vol': '', 'r_units': '', 'units': '',
  'r_pen': 'Rien à mesurer : le stylo délivre la dose complète. Ne prélevez jamais de médicament dans un stylo avec une seringue.',
  'r_kwik': 'Le KwikPen délivre toujours 0,6 ml par dose. Ne réglez pas une autre quantité et ne prélevez pas de dose supplémentaire ; le reste de solution est jeté avec le stylo.',
  'sched': 'Vos 6 prochaines injections', 'chart': 'Votre évolution de poids comparée à l’étude (72 semaines)',
  'you': 'Vous', 'placebo': 'Placebo', 'fill': 'Indiquez les dates et la dose', 'na': '—',
  'warn': '<b>Important :</b> cet outil compare vos données au RCP ; il ne décide pas de votre dose. Ne modifiez jamais votre dose seul(e). Mounjaro est un médicament sur ordonnance.',
  'wk': 'semaines', 'days': 'jours', 'kg': 'kg', 'lb': 'lb',
  'r_cost': 'Prix public de votre dosage', 'r_pen1': 'par stylo (4 semaines)', 'r_year': 'Environ un an (13 stylos)',
  'cost_note': 'Prix publics indiqués par VIDAL (2026). Remboursement à 65 % seulement si les conditions sont remplies ; sinon, le prix est entièrement à votre charge.',
  'r_bmi0': 'IMC au départ', 'rb_h': 'Conditions de remboursement (contrôle du poids)', 'rb_cm': 'J’ai au moins une comorbidité reconnue (diabète de type 2, hypertension, apnée du sommeil, maladie cardiovasculaire…)',
  'rb_fail': 'Une prise en charge nutritionnelle bien conduite pendant 6 mois a fait perdre moins de 5 % du poids',
  'rb_yes': 'Vous semblez remplir les critères de remboursement à 65 % (IMC ≥ 40, ou ≥ 35 avec une comorbidité, après échec de la prise en charge nutritionnelle). La première prescription doit venir d’un spécialiste de l’obésité.',
  'rb_no': 'Vous ne semblez pas remplir les critères de remboursement pour le contrôle du poids ; le traitement peut être prescrit mais reste à votre charge.',
}
PAGES['fr'] = dict(
  tpl=sys.argv[1].replace('/en/health/tdee-calculator.html','/fr/bmi-calculator.html'), lang='fr', t='fr',
  path='/fr/calcul-dose-mounjaro.html', hub='/fr/', products=['kwik'], ht='168',
  title='Calcul dose Mounjaro – Paliers, dose oubliée, perte de poids, prix et remboursement (tirzépatide)',
  desc='Mounjaro (tirzépatide) KwikPen : vérifiez votre palier (2,5 mg pendant 4 semaines puis +2,5 mg toutes les 4 semaines jusqu’à 15 mg), vos dates d’injection, la conduite en cas d’oubli, votre perte de poids face à SURMOUNT-1, le prix (176,10 € à 433,80 €) et les conditions de remboursement à 65 %.',
  h1='Calcul de <b>dose Mounjaro</b> (paliers, poids, prix &amp; remboursement)',
  kicker='🇫🇷 Santé', lead='Pour les personnes à qui Mounjaro a déjà été prescrit. Les résultats se mettent à jour en direct.',
  brand='Hong Life Calculators', hubname='Calculateurs France',
  foot='À titre informatif uniquement – ni diagnostic ni avis médical. Suivez toujours la dose indiquée par votre médecin et votre pharmacien.',
  foot_links='<a href="/">Calculateurs par pays</a> · <a href="/privacy.html">Confidentialité</a> · <a href="/report-error.html">Signaler une erreur</a>',
  reviewed='Dernière vérification : novembre 2026',
  xdata={'price': {'2.5': 176.10, '5': 237.68, '7.5': 335.95, '10': 335.95, '12.5': 433.80, '15': 433.80}},
  extra_js=r"""
 { const ht=v('ht'),w0=v('w0'),u=$('u').value; if(isFinite(ht)&&ht>0&&isFinite(w0)){ const kg0=u==='lb'?w0*0.45359237:w0,b0=kg0/Math.pow(ht/100,2),cm=$('rbcm').checked,fl=$('rbfail').checked;
   o+='<div class="mj-sec">'+T.rb_h+'</div>'+kv([[T.r_bmi0,nf(b0)]]); o+=((b0>=40||(b0>=35&&cm))&&fl)?'<p class="mj-ok">'+T.rb_yes+'</p>':'<p class="mj-info">'+T.rb_no+'</p>'; }
   const pr=X.price[String(dose)]; if(pr){ o+='<div class="mj-sec">'+T.r_cost+'</div>'+kv([[T.r_cost,pr.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2})+' € '+T.r_pen1],[T.r_year,nf(pr*13,0)+' €']])+'<p class="mj-info">'+T.cost_note+'</p>'; } }
""",
)
PAGES['fr']['extra_form'] = '<div class="mj-sec">' + T['fr']['rb_h'] + '</div><label class="chk"><input type="checkbox" id="rbcm"> ' + T['fr']['rb_cm'] + '</label><label class="chk"><input type="checkbox" id="rbfail"> ' + T['fr']['rb_fail'] + '</label>'

T['ja'] = {
  'f_head': '治療の状況', 'first': '初回注射日', 'dose': '現在の週1回の用量', 'since': 'この用量を始めた日',
  'last': '前回の注射日', 'unit': '体重の単位', 'w0': '開始時の体重', 'w1': '今日の体重', 'ht': '身長（cm、BMI用）',
  'prod': '製剤', 'p_pen': 'アテオス（単回使用オートインジェクター）', 'p_kwik': 'クイックペン（4回分）',
  'lab_mg': '', 'lab_ml': '', 'conc_hint': '', 'r_over': '',
  'r_step': '用量の段階', 'of6': '/ 6', 'r_weeks': 'この用量での週数', 'r_next': '添付文書上、次に増量できる最も早い日',
  'r_max': '最大用量（15mg）です。', 'r_fast': '添付文書の「4週間以上の間隔」より早くこの用量に達しています。処方医に確認してください。',
  'r_ok': '用量の段階は添付文書の増量方法に合っています。', 'r_due': '次回の注射予定日', 'r_late': '日経過',
  'r_take': '打ち忘れ：4日（96時間）以内です。気づいた時点でできるだけ早く注射してください。',
  'r_skip': '打ち忘れ：4日を超えています。その回は打たず、次の予定日から再開してください',
  'r_you': '治療期間', 'r_lost': '減った体重', 'r_pct': '開始時からの変化', 'r_bmi': '現在のBMI',
  'r_trial': 'SURMOUNT-1試験（72週）のこの用量での平均', 'r_vol': '', 'r_units': '', 'units': '',
  'r_pen': '測る必要はありません。アテオスは1本で1回分を全量注射します。注射器で薬液を抜き取らないでください。',
  'r_kwik': 'クイックペンは1回0.6mLの固定量です。量を変えたり、追加の回数分を取り出したりしないでください。',
  'sched': '次の6回の注射日', 'chart': '体重変化と臨床試験の平均（72週）', 'you': 'あなた', 'placebo': 'プラセボ', 'fill': '日付と用量を入力してください', 'na': '—',
  'warn': '<b>大切なこと：</b>このツールは入力内容を添付文書と照らし合わせるだけで、用量を決めるものではありません。自己判断で用量を変えないでください。チルゼパチドは処方薬です。',
  'wk': '週', 'days': '日', 'kg': 'kg', 'lb': 'lb',
  'r_cost': '薬価（1キット＝1週分）', 'r_pen1': '/週', 'r_month': '4週分（10割）', 'r_3w': '4週分の自己負担（3割）',
  'cost_note': 'ゼップバウンドの薬価（2025年3月の収載時）。薬価は改定されることがあります。診察料・指導料などは含みません。',
  'r_bmi0': '開始時のBMI', 'ins_h': '保険適用の目安（ゼップバウンド・肥満症）', 'ins_dis': '高血圧・脂質異常症・2型糖尿病のいずれかがある',
  'ins_two': '肥満に関連する健康障害が2つ以上ある', 'ins_diet': '実施施設で6か月以上、食事療法・運動療法を行っても効果が不十分',
  'ins_yes': '最適使用推進ガイドラインの患者要件に当てはまる可能性があります（BMI35以上、またはBMI27以上で健康障害2つ以上）。要件を満たす施設・医師のもとで、最長72週間の投与となります。',
  'ins_no': '現時点では保険適用の要件に当てはまらない可能性があります。条件や対象施設は主治医に確認してください。',
}
PAGES['jp'] = dict(
  tpl=sys.argv[1].replace('/en/health/tdee-calculator.html','/jp/denkidai-keisan.html'), lang='ja', t='ja',
  path='/jp/zepbound-mounjaro-yoryo.html', hub='/jp/', products=['pen'], ht='165',
  title='ゼップバウンド・マンジャロ用量計算ツール｜増量スケジュール・打ち忘れ・体重変化・薬価と保険適用（チルゼパチド）',
  desc='ゼップバウンド（肥満症）・マンジャロ（2型糖尿病）の用量段階（2.5mgから4週間ごとに2.5mgずつ増量）、注射日、打ち忘れの対応、SURMOUNT-1との体重変化の比較、薬価（2.5mg 3,067円〜15mg 11,242円）と3割負担、保険適用の要件を確認できます。',
  h1='ゼップバウンド・<b>マンジャロ用量</b>計算（チルゼパチド）',
  kicker='🇯🇵 健康', lead='すでにチルゼパチドを処方されている方向けです。入力するとすぐ結果が変わります。',
  brand='Hong Life Calculators', hubname='日本の計算ツール',
  foot='情報提供のみを目的としており、診断や医学的助言ではありません。用量は必ず医師・薬剤師の指示に従ってください。',
  foot_links='<a href="/">国別の計算ツール</a> · <a href="/privacy.html">プライバシー</a> · <a href="/report-error.html">誤りを報告</a>',
  reviewed='最終確認：2026年11月',
  xdata={'price': {'2.5': 3067, '5': 5797, '7.5': 7721, '10': 8999, '12.5': 10180, '15': 11242}},
  extra_js=r"""
 { const ht=v('ht'),w0=v('w0'),u=$('u').value; if(isFinite(ht)&&ht>0&&isFinite(w0)){ const kg0=u==='lb'?w0*0.45359237:w0,b0=kg0/Math.pow(ht/100,2),dis=$('insdis').checked,two=$('instwo').checked,diet=$('insdiet').checked;
   o+='<div class="mj-sec">'+T.ins_h+'</div>'+kv([[T.r_bmi0,nf(b0)]]); o+=(dis&&diet&&(b0>=35||(b0>=27&&two)))?'<p class="mj-ok">'+T.ins_yes+'</p>':'<p class="mj-info">'+T.ins_no+'</p>'; }
   const pr=X.price[String(dose)]; if(pr){ o+='<div class="mj-sec">'+T.r_cost+'</div>'+kv([[T.r_cost,nf(pr,0)+'円'+T.r_pen1],[T.r_month,nf(pr*4,0)+'円'],[T.r_3w,nf(Math.round(pr*4*0.3),0)+'円']])+'<p class="mj-info">'+T.cost_note+'</p>'; } }
""",
)
PAGES['jp']['extra_form'] = '<div class="mj-sec">' + T['ja']['ins_h'] + '</div>' + ''.join(f'<label class="chk"><input type="checkbox" id="{i}"> {T["ja"][k]}</label>' for i, k in (('insdis', 'ins_dis'), ('instwo', 'ins_two'), ('insdiet', 'ins_diet')))

T['ko'] = {
  'f_head': '나의 투약 정보', 'first': '첫 주사 날짜', 'dose': '현재 주 1회 용량', 'since': '이 용량을 시작한 날짜',
  'last': '마지막 주사 날짜', 'unit': '체중 단위', 'w0': '시작할 때 체중', 'w1': '오늘 체중', 'ht': '키(cm, 체질량지수 계산용)',
  'prod': '제품', 'p_pen': '프리필드펜(1회용, 1개 1회분)', 'p_kwik': '퀵펜(1개 4회분)',
  'lab_mg': '', 'lab_ml': '', 'conc_hint': '', 'r_over': '',
  'r_step': '용량 단계', 'of6': '/ 6단계', 'r_weeks': '이 용량으로 맞은 기간', 'r_next': '허가사항상 다음 단계로 올릴 수 있는 가장 빠른 날',
  'r_max': '최대 용량(15mg)이에요.', 'r_fast': '허가사항(한 단계에 최소 4주)보다 빨리 이 용량에 도달했어요. 처방한 의사와 꼭 확인하세요.',
  'r_ok': '지금 용량 단계는 허가된 증량 방법에 맞아요.', 'r_due': '다음 주사 예정일', 'r_late': '일 지남',
  'r_take': '놓친 주사: 4일(96시간) 이내예요. 생각난 즉시 맞으세요.',
  'r_skip': '놓친 주사: 4일이 지났어요. 이번 회차는 건너뛰고 원래 요일에 다음 주사를 맞으세요',
  'r_you': '투약 기간', 'r_lost': '감량한 체중', 'r_pct': '시작 대비 변화', 'r_bmi': '현재 체질량지수',
  'r_trial': '임상시험(SURMOUNT-1) 72주 평균, 이 용량 기준', 'r_vol': '', 'r_units': '', 'units': '',
  'r_pen': '양을 잴 필요가 없어요. 프리필드펜은 1개로 1회분을 모두 주사해요. 주사기로 약을 빼내지 마세요.',
  'r_kwik': '퀵펜은 1회 0.6mL로 고정돼 있어요. 양을 바꾸거나 남은 약으로 추가 회차를 만들지 마세요. 4회 후 남은 약은 펜과 함께 버려요.',
  'sched': '앞으로 6번의 주사 날짜', 'chart': '내 체중 변화와 임상시험 평균 비교(72주)', 'you': '나', 'placebo': '위약', 'fill': '날짜와 용량을 넣어 주세요', 'na': '—',
  'warn': '<b>꼭 읽어 주세요:</b> 이 도구는 입력한 내용을 허가사항과 비교해 줄 뿐, 용량을 정하지 않아요. 스스로 용량을 바꾸지 마세요. 마운자로는 전문의약품이에요.',
  'wk': '주', 'days': '일', 'kg': 'kg', 'lb': 'lb',
  'r_bmi0': '시작할 때 체질량지수', 'lab_ok': '허가사항상 체중 관리 목적은 체질량지수 30 이상, 또는 27 이상이면서 고혈압·이상지질혈증·2형 당뇨병·수면무호흡·심혈관질환 같은 동반질환이 있을 때예요.',
  'cost_note': '비만 치료 목적은 건강보험이 적용되지 않는 비급여라 병원·약국마다 가격이 달라요. 출시 당시(2025년 8월) 2.5mg 4주분이 약국에서 약 29만~35만 원 수준이었어요.',
}
PAGES['ko'] = dict(
  tpl=sys.argv[1].replace('/en/health/tdee-calculator.html','/ko/health/tdee-calculator.html'), lang='ko', t='ko',
  path='/ko/health/mounjaro-dose-calculator.html', hub='/ko/health/', products=['pen', 'kwik'], ht='165',
  title='마운자로 용량 계산기 – 증량 단계, 주사 놓쳤을 때, 체중 감소율, 비용 (터제파타이드)',
  desc='마운자로(터제파타이드) 용량 단계(2.5mg로 4주 시작, 4주 이상 간격으로 2.5mg씩 증량, 최대 15mg) 확인, 주사 일정, 주사를 놓쳤을 때(4일 기준), 임상시험과 체중 감소율 비교, 프리필드펜·퀵펜 사용 주의를 한 번에 확인하세요.',
  h1='마운자로 <b>용량 계산기</b>(증량 단계·체중 감소)',
  kicker='💪 건강', lead='이미 마운자로를 처방받은 분을 위한 도구예요. 입력하면 바로 결과가 바뀌어요.',
  brand='홍라이프 계산기', hubname='건강·운동 계산기',
  foot='참고용 정보이며 진단이나 의학적 조언이 아니에요. 용량은 반드시 처방한 의사와 약사의 안내를 따르세요.',
  foot_links='<a href="/ko/">전체 계산기</a> · <a href="/privacy.html">개인정보처리방침</a> · <a href="/ko/report-error.html">오류 신고</a>',
  reviewed='마지막 검토: 2026년 11월',
  extra_js=r"""
 { const ht=v('ht'),w0=v('w0'),u=$('u').value; if(isFinite(ht)&&ht>0&&isFinite(w0)){ const kg0=u==='lb'?w0*0.45359237:w0; o+=kv([[T.r_bmi0,nf(kg0/Math.pow(ht/100,2))]])+'<p class="mj-info">'+T.lab_ok+'</p>'; }
   o+='<p class="mj-info">'+T.cost_note+'</p>'; }
""",
)

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
