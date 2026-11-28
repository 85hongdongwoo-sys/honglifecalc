/* hl-motion: 메인 페이지 애플식 스크롤 모션 (2026-11-28)
   - 첫 화면: 큰 제목이 단어별로 떠오름, 스크롤하면 살짝 작아지며 흐려짐
   - 스크롤 이야기: 오른쪽 그림이 고정된 채 3단계(입력 → 결과 → 그래프 2개)로 바뀜
   - 아래 목록: 화면에 들어올 때 부드럽게 올라옴
   숫자는 페이지에 실제로 있는 계산기 링크 수를 세어서 씀(지어낸 숫자 없음). 움직임 줄이기 설정이면 정지 화면. */
(function () {
  if (window.__hlMotion) return; window.__hlMotion = 1;
  var D = document, W = window;
  var KO = /^ko/i.test(D.documentElement.lang || '');
  var main = D.querySelector('main.hlu') || D.querySelector('main') || D.querySelector('body > div.wrap');
  if (!main) return;
  var RM = W.matchMedia && W.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var nCalc = KO ? (function () { var s = {}; [].forEach.call(main.querySelectorAll('a[href$=".html"]'), function (a) { s[a.getAttribute('href')] = 1; }); return Object.keys(s).length; })() : D.querySelectorAll('main .hlu-p a[href$=".html"]').length;
  var L = KO ? {
    eyebrow: '● 무료 · 가입 없음 · 휴대폰에서도', words: [['필요한', 0], ['모든', 0], ['계산,', 0], ['한\u00a0곳에서.', 1]],
    sub: '세금·월급·대출·연금 계산기를 공식 기준으로 만들고, 계산 과정을 한 줄씩 보여 드려요.',
    sCalc: '이 페이지의 계산기', sYear: '발표된 2027년 기준 반영',
    s1: ['1단계', '숫자를 넣으세요.', '연봉·가격·이율을 넣으면 바로 계산돼요. 넣은 숫자는 내 휴대폰·컴퓨터 안에서만 쓰여요.'],
    s2: ['2단계', '답부터 보여 드려요.', '궁금한 숫자를 맨 위에, 계산 과정은 그 아래에 한 줄씩 보여 드려요.'],
    s3: ['3단계', '그래프 두 개로 한눈에.', '나눠 볼 수 있는 결과는 그래프 두 개로 보여 드려요. 도넛·막대·기둥 중에서 골라 보세요.'],
    f1: '연봉', f2: '기준 연도', cur: '', unit: '원', typ: '50,000,000', cap: '한 달 실수령액', to: 3520000, note: '예시예요 — 실제 금액은 입력에 따라 달라요.', aria: '소개', loc: 'ko-KR'
  } : {
    eyebrow: '● Free · No sign-up · Works on your phone', words: [['Every', 0], ['number', 0], ['you', 0], ['need,', 0], ['in', 1], ['every', 1], ['country.', 1]],
    sub: 'Tax, salary, mortgage and benefit calculators built on each country’s official rules — with the working shown, so you can check every step.',
    sCalc: 'calculators on this page', sYear: 'tax figures where published',
    s1: ['Step 1', 'Type your numbers.', 'Salary, price, rate — results update as you type, right in your browser.'],
    s2: ['Step 2', 'See the answer first.', 'The number you came for sits at the top, with each line of the calculation underneath.'],
    s3: ['Step 3', 'Read it in two charts.', 'Results with a breakdown come with two graphs — pick donut, bars or columns for each.'],
    f1: 'Annual salary', f2: 'Tax year', cur: '$', unit: '', typ: '85,000', cap: 'Take-home pay a month', to: 5240, note: 'Example only — your numbers will differ.', aria: 'Introduction', loc: 'en-US'
  };
  var nCountry = (function () { var s = {}; [].forEach.call(D.querySelectorAll('a[href]'), function (a) { var m = (a.getAttribute('href') || '').match(/^\/([a-z]{2,3})\/(?:index\.html)?$/); if (m) s[m[1]] = 1; }); return Object.keys(s).length; })();
  function fmt(n) { return n.toLocaleString(L.loc); }

  var css = '' +
    '.hm{position:relative;margin:0 0 28px;word-break:keep-all}' +
    '.hm-hero{min-height:min(78vh,720px);display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:48px 8px 24px;will-change:transform,opacity}' +
    '.hm-eyebrow{display:inline-flex;gap:8px;align-items:center;padding:6px 14px;border-radius:999px;background:#EEF2FF;color:#4F46E5;font:600 13px/1 Inter,system-ui,sans-serif;letter-spacing:.01em;margin-bottom:22px}' +
    '.hm-h{font:800 clamp(40px,8.4vw,92px)/1.02 Inter,system-ui,sans-serif;letter-spacing:-.045em;color:#0F172A;margin:0;max-width:14ch}' +
    '.hm-h .w{display:inline-block;opacity:0;transform:translateY(.45em);filter:blur(8px);transition:opacity .9s cubic-bezier(.2,.8,.2,1),transform .9s cubic-bezier(.2,.8,.2,1),filter .9s}' +
    '.hm-h .g{background:linear-gradient(90deg,#4F46E5,#7C3AED 45%,#DB2777);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent}' +
    '.hm.in .hm-h .w{opacity:1;transform:none;filter:none}' +
    '.hm-sub{max-width:560px;margin:22px auto 0;font:400 clamp(17px,2.1vw,21px)/1.55 Inter,system-ui,sans-serif;color:#475569;opacity:0;transform:translateY(14px);transition:all .9s .5s cubic-bezier(.2,.8,.2,1)}' +
    '.hm.in .hm-sub{opacity:1;transform:none}' +
    '.hm-stats{display:flex;gap:28px;justify-content:center;flex-wrap:wrap;margin-top:30px;opacity:0;transition:opacity .9s .8s}.hm.in .hm-stats{opacity:1}' +
    '.hm-stats b{display:block;font:800 clamp(28px,4vw,40px)/1 Inter,system-ui,sans-serif;letter-spacing:-.03em;color:#0F172A;font-variant-numeric:tabular-nums}.hm-stats span{font:500 13px/1.4 Inter,system-ui,sans-serif;color:#64748B}' +
    '.hm-cue{margin-top:34px;width:26px;height:42px;border:2px solid #CBD5E1;border-radius:14px;position:relative}.hm-cue:after{content:"";position:absolute;left:50%;top:8px;width:4px;height:8px;margin-left:-2px;border-radius:2px;background:#94A3B8;animation:hmcue 1.6s infinite}' +
    '@keyframes hmcue{0%{opacity:0;transform:translateY(0)}30%{opacity:1}100%{opacity:0;transform:translateY(14px)}}' +
    /* 스크롤 이야기 */
    '.hm-story{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:start;margin:10px 0 40px}' +
    '.hm-steps{display:flex;flex-direction:column}.hm-step{min-height:72vh;display:flex;flex-direction:column;justify-content:center;opacity:.25;transition:opacity .5s}.hm-step.on{opacity:1}' +
    '.hm-step small{font:700 13px/1 Inter,system-ui,sans-serif;color:#4F46E5;letter-spacing:.08em;text-transform:uppercase}' +
    '.hm-step h3{font:800 clamp(28px,3.6vw,44px)/1.08 Inter,system-ui,sans-serif;letter-spacing:-.035em;color:#0F172A;margin:12px 0 12px}' +
    '.hm-step p{font:400 17px/1.6 Inter,system-ui,sans-serif;color:#475569;margin:0;max-width:30ch}' +
    '.hm-stage{position:sticky;top:calc(50vh - 190px);height:380px;border-radius:28px;background:linear-gradient(160deg,#0F172A,#1E1B4B 60%,#312E81);box-shadow:0 30px 80px -30px rgba(49,46,129,.6);overflow:hidden}' +
    '.hm-stage:before{content:"";position:absolute;inset:-40%;background:radial-gradient(closest-side,rgba(124,58,237,.35),transparent 70%);transform:translate(var(--hx,0),var(--hy,0));transition:transform .2s}' +
    '.hm-scene{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;opacity:0;transform:scale(.94) translateY(16px);transition:opacity .6s cubic-bezier(.2,.8,.2,1),transform .6s cubic-bezier(.2,.8,.2,1)}' +
    '.hm-scene.on{opacity:1;transform:none}' +
    '.hm-card{width:min(78%,320px);background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:20px;padding:20px;-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);color:#E2E8F0;font:500 14px/1.4 Inter,system-ui,sans-serif}' +
    '.hm-field{margin:0 0 12px}.hm-field i{display:block;font-style:normal;font-size:12px;color:#A5B4FC;margin-bottom:6px}.hm-field b{display:block;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.1);font:700 18px/1 Inter,system-ui,sans-serif;color:#fff;font-variant-numeric:tabular-nums}' +
    '.hm-field b:after{content:"";display:inline-block;width:2px;height:18px;margin-left:3px;vertical-align:-3px;background:#A5B4FC;animation:hmblink 1s steps(1) infinite}@keyframes hmblink{50%{opacity:0}}' +
    '.hm-big{white-space:nowrap;font:800 clamp(34px,6vw,64px)/1 Inter,system-ui,sans-serif;letter-spacing:-.04em;color:#fff;font-variant-numeric:tabular-nums}.hm-cap{color:#A5B4FC;font:600 13px/1 Inter,system-ui,sans-serif;margin-bottom:10px;letter-spacing:.04em;text-transform:uppercase}' +
    '.hm-two{display:grid;grid-template-columns:1fr 1fr;gap:14px;width:min(86%,380px)}.hm-two>div{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:16px;display:flex;align-items:center;justify-content:center}' +
    '.hm-two svg{width:100%;height:auto}.hm-ring{transition:stroke-dashoffset 1.4s cubic-bezier(.2,.8,.2,1)}.hm-bar{transform-origin:0 50%;transform:scaleX(0);transition:transform 1.1s cubic-bezier(.2,.8,.2,1)}' +
    '.hm-scene.on .hm-bar{transform:none}' +
    /* 목록 나타나기 */
    '.hm-rv{opacity:0;transform:translateY(28px);transition:opacity .8s cubic-bezier(.2,.8,.2,1),transform .8s cubic-bezier(.2,.8,.2,1)}.hm-rv.on{opacity:1;transform:none}' +
    '.hm-mini{display:none}@media(max-width:760px){.hm-story{grid-template-columns:1fr;gap:0}.hm-stage{display:none}.hm-step{min-height:0;padding:28px 0;opacity:.35}.hm-step p{max-width:none}.hm-mini{display:block;position:relative;height:240px;margin-top:18px;border-radius:22px;background:linear-gradient(160deg,#0F172A,#1E1B4B 60%,#312E81);overflow:hidden;box-shadow:0 20px 50px -24px rgba(49,46,129,.6)}.hm-card{padding:16px}.hm-two{gap:10px}}' +
    '@media (prefers-reduced-motion:reduce){.hm *,.hm-rv{transition:none!important;animation:none!important;opacity:1!important;transform:none!important;filter:none!important}}';
  var st = D.createElement('style'); st.textContent = css; D.head.appendChild(st);

  var WS = L.words;
  var h = WS.map(function (w, i) { return '<span class="w' + (w[1] ? ' g' : '') + '" style="transition-delay:' + (i * 80) + 'ms">' + w[0] + '</span>'; }).join(' ');
  var stats = '';
  if (nCalc > 0) stats += '<div><b data-to="' + nCalc + '">0</b><span>' + L.sCalc + '</span></div>';
  stats += '<div><b>2027</b><span>' + L.sYear + '</span></div>';

  var sec = D.createElement('section'); sec.className = 'hm'; sec.setAttribute('aria-label', L.aria);
  sec.innerHTML =
    '<div class="hm-hero"><div class="hm-eyebrow">' + L.eyebrow + '</div>' +
    '<h2 class="hm-h">' + h + '</h2>' +
    '<p class="hm-sub">' + L.sub + '</p>' +
    '<div class="hm-stats">' + stats + '</div><div class="hm-cue" aria-hidden="true"></div></div>' +
    '<div class="hm-story">' +
    '<div class="hm-steps">' +
    '<div class="hm-step" data-s="0"><small>' + L.s1[0] + '</small><h3>' + L.s1[1] + '</h3><p>' + L.s1[2] + '</p></div>' +
    '<div class="hm-step" data-s="1"><small>' + L.s2[0] + '</small><h3>' + L.s2[1] + '</h3><p>' + L.s2[2] + '</p></div>' +
    '<div class="hm-step" data-s="2"><small>' + L.s3[0] + '</small><h3>' + L.s3[1] + '</h3><p>' + L.s3[2] + '</p></div>' +
    '</div>' +
    '<div class="hm-stage" aria-hidden="true">' +
    '<div class="hm-scene" data-s="0"><div class="hm-card"><div class="hm-field"><i>' + L.f1 + '</i><b class="hm-type" data-v="' + L.typ + '">' + L.cur + '</b></div><div class="hm-field"><i>' + L.f2 + '</i><b>2027</b></div></div></div>' +
    '<div class="hm-scene" data-s="1"><div class="hm-card" style="text-align:left"><div class="hm-cap">' + L.cap + '</div><div class="hm-big" data-to="' + L.to + '" data-pre="' + L.cur + '" data-suf="' + L.unit + '">' + L.cur + '0' + L.unit + '</div><div style="margin-top:12px;color:#CBD5E1;font-size:13px">' + L.note + '</div></div></div>' +
    '<div class="hm-scene" data-s="2"><div class="hm-two"><div><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="44" fill="none" stroke="rgba(255,255,255,.12)" stroke-width="18"/>' +
    '<circle class="hm-ring" cx="60" cy="60" r="44" fill="none" stroke="#818CF8" stroke-width="18" stroke-dasharray="276.5" stroke-dashoffset="276.5" data-off="88" transform="rotate(-90 60 60)"/>' +
    '<circle class="hm-ring" cx="60" cy="60" r="44" fill="none" stroke="#F472B6" stroke-width="18" stroke-dasharray="276.5" stroke-dashoffset="276.5" data-off="230" transform="rotate(-90 60 60)" style="transition-delay:.25s"/></svg></div>' +
    '<div><svg viewBox="0 0 120 120"><rect class="hm-bar" x="8" y="22" width="104" height="18" rx="6" fill="#818CF8"/><rect class="hm-bar" x="8" y="51" width="70" height="18" rx="6" fill="#A78BFA" style="transition-delay:.15s"/><rect class="hm-bar" x="8" y="80" width="40" height="18" rx="6" fill="#F472B6" style="transition-delay:.3s"/></svg></div></div></div>' +
    '</div></div>';
  main.insertBefore(sec, main.firstChild);

  function count(el, dur) {
    var to = +el.getAttribute('data-to'), pre = el.getAttribute('data-pre') || '', suf = el.getAttribute('data-suf') || '', t0 = null;
    if (RM) { el.textContent = pre + fmt(to) + suf; return; }
    function f(t) { if (!t0) t0 = t; var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3); el.textContent = pre + fmt(Math.round(to * e)) + suf; if (p < 1) requestAnimationFrame(f); }
    requestAnimationFrame(f);
  }
  function type(el) {
    var v = el.getAttribute('data-v'), i = 0, c = L.cur, u = L.unit; el.textContent = c;
    if (RM) { el.textContent = c + v + u; return; }
    (function n() { if (i <= v.length) { el.textContent = c + v.slice(0, i) + (i === v.length ? u : ''); i++; setTimeout(n, 90); } })();
  }
  requestAnimationFrame(function () { setTimeout(function () { sec.classList.add('in'); [].forEach.call(sec.querySelectorAll('.hm-stats b[data-to]'), function (b) { count(b, 1400); }); }, 60); });

  var steps = [].slice.call(sec.querySelectorAll('.hm-step')), scenes = [].slice.call(sec.querySelectorAll('.hm-scene')), cur = -1;
  function setScene(k) {
    if (k === cur) return; cur = k;
    steps.forEach(function (s, i) { s.classList.toggle('on', i === k); });
    scenes.forEach(function (s, i) { s.classList.toggle('on', i === k); });
    var sc = scenes[k];
    if (k === 0) type(sc.querySelector('.hm-type'));
    if (k === 1) count(sc.querySelector('.hm-big'), 1200);
    [].forEach.call(sec.querySelectorAll('.hm-ring'), function (r) { r.style.strokeDashoffset = k === 2 ? r.getAttribute('data-off') : 276.5; });
  }
  var MOB = W.innerWidth <= 760;
  if (MOB) {   /* 휴대폰: 고정 그림 대신 단계마다 그림을 바로 아래에 둠 */
    steps.forEach(function (st, i) { var m = D.createElement('div'); m.className = 'hm-mini'; m.setAttribute('aria-hidden', 'true'); m.appendChild(scenes[i]); st.appendChild(m); });
  }
  setScene(0);
  var hero = sec.querySelector('.hm-hero'), stage = sec.querySelector('.hm-stage'), ticking = false;
  function onScroll() {
    ticking = false;
    var vh = W.innerHeight, y = W.scrollY || W.pageYOffset;
    if (!RM) { var p = Math.min(1, y / (vh * 0.8)); hero.style.transform = 'scale(' + (1 - p * 0.08) + ')'; hero.style.opacity = String(1 - p * 0.85); }
    var mid = W.innerWidth <= 760 ? vh * 0.62 : vh * 0.5, best = 0, bd = 1e9;
    steps.forEach(function (s, i) { var r = (s.querySelector('h3') || s).getBoundingClientRect(), d = Math.abs(r.top + r.height / 2 - mid); if (d < bd) { bd = d; best = i; } });
    setScene(best);
  }
  W.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
  if (!RM && stage) stage.addEventListener('pointermove', function (e) { var r = stage.getBoundingClientRect(); stage.style.setProperty('--hx', ((e.clientX - r.left) / r.width - .5) * 30 + '%'); stage.style.setProperty('--hy', ((e.clientY - r.top) / r.height - .5) * 30 + '%'); });

  /* 아래 목록이 화면에 들어올 때 올라오기 */
  if ('IntersectionObserver' in W && !RM) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('on'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    [].forEach.call(D.querySelectorAll('main .hlu-top, main .hl-home, main .hlu-tabs, main .hlu-p, body > div.wrap > section, body > div.wrap > div'), function (el) { if (el === sec || sec.contains(el)) return; el.classList.add('hm-rv'); io.observe(el); });
  }
})();
