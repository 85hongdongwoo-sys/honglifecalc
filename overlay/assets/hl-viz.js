/* hl-viz: turns calculator result breakdowns into a donut infographic.
   Uses only numbers the calculator itself printed:
   1) stacked bars (.bar / .split with <i style="width:%">) + their .legend
   2) breakdown lists (.kv grid or table) where  first amount = sum of minus rows + last total row (checked to 0.5%) */
(function () {
  if (window.__hlViz) return; window.__hlViz = 1;
  var D = document, NS = 'http://www.w3.org/2000/svg';
  var PAL = ['#4F46E5', '#EC4899', '#0EA5E9', '#7C3AED', '#F59E0B', '#14B8A6', '#F43F5E', '#64748B', '#A855F7', '#22C55E'];  // 2026-11-28 첫 화면 색(남색·분홍·보라)에 맞춤
  var css = '.hlv{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:14px 18px;margin:16px 0 6px;padding:14px;border:1px solid #E1E5EC;border-radius:14px;background:#FAFBFD}' +
    '.hlv svg{flex:0 0 auto;width:136px;height:136px}.hlv circle{transition:stroke-dasharray .6s ease,stroke-dashoffset .6s ease}' +
    '.hlv .c1{font:800 22px/1 system-ui,sans-serif;fill:#12305C}.hlv .c2{font:600 10.5px/1 system-ui,sans-serif;fill:#5F6875}' +
    '.hlv ul{list-style:none;margin:0;padding:0;flex:1 1 220px;min-width:0;display:grid;gap:7px}' +
    '.hlv li{display:grid;grid-template-columns:12px 1fr auto;gap:8px;align-items:center;font-size:13.5px;line-height:1.35;color:#2F343B}' +
    '.hlv li i{width:12px;height:12px;border-radius:4px}.hlv li b{font-variant-numeric:tabular-nums;color:#12305C}' +
    '.hlv li span{overflow-wrap:anywhere;word-break:keep-all}@media(max-width:380px){.hlv{gap:12px;padding:12px}.hlv svg{width:112px;height:112px}.hlv li{font-size:12.5px}}' +
'.hlx{margin:16px 0 6px;padding:14px 16px;border:1px solid #E1E5EC;border-radius:14px;background:#FAFBFD}.hlx h4{margin:0 0 10px;font:700 13px/1.3 system-ui,sans-serif;color:#5F6875;letter-spacing:.02em;text-transform:uppercase}' +
    '.hlv.hlx-r li{font-size:13px}@media(max-width:430px){.hlv.hlx-r:not([data-hlv2]) svg,.hlv.hlx-s svg{width:108px;height:108px}}.hlx .br{display:grid;grid-template-columns:minmax(0,38%) 1fr;gap:10px;align-items:center;margin:7px 0;font-size:13.5px}.hlx .br span{overflow-wrap:anywhere;word-break:keep-all;color:#2F343B}' +
    '.hlx .br div{position:relative;height:22px;background:#EEF1F6;border-radius:7px;overflow:hidden}.hlx .br i{position:absolute;left:0;top:0;bottom:0;border-radius:7px;transition:width .6s ease}' +
    '.hlx .br b{position:absolute;right:8px;top:50%;transform:translateY(-50%);font:700 12px/1 system-ui,sans-serif;color:#12305C;font-variant-numeric:tabular-nums}' +
    '.hlx .gg{display:flex;flex-wrap:wrap;gap:14px;justify-content:space-around}.hlx .gg figure{margin:0;text-align:center;width:112px}.hlx .gg figcaption{font-size:12.5px;color:#2F343B;line-height:1.3;word-break:keep-all}' +
    '.hlx svg.ln{width:100%;height:auto;display:block}.hlx .lg{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:8px;font-size:12.5px;color:#2F343B}.hlx .lg i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}' +
'.hlv[data-hlv2]{display:block}.hlv2-g{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}@media(max-width:560px){.hlv2-g{grid-template-columns:1fr}}' +
    '.hlv2-p{background:#fff;border:1px solid #E5E8EE;border-radius:14px;padding:10px 12px 12px;min-width:0}.hlv2-t{display:flex;gap:4px;justify-content:flex-end;margin-bottom:6px}' +
    '.hlv2-t button{width:30px;height:28px;border:1px solid transparent;border-radius:8px;background:transparent;cursor:pointer;display:grid;place-items:center;padding:0;color:#94A3B8}.hlv2-t button svg{width:16px;height:16px;fill:currentColor}' +
    '.hlv2-t button:hover{background:#F1F5F9;color:#475569}.hlv2-t button[aria-selected=true]{background:#EEF2FF;border-color:#C7D2FE;color:#4F46E5}' +
    '.hlv2-c{display:flex;justify-content:center;align-items:center;min-height:150px}.hlv[data-hlv2] .hlv2-c svg{width:100%;height:auto;max-width:200px}.hlv[data-hlv2] .hlv2-c svg.k-bars,.hlv[data-hlv2] .hlv2-c svg.k-stack{max-width:100%}' +
    '.hlv2-c .bt{font:700 11px/1 system-ui,sans-serif;fill:#334155;font-variant-numeric:tabular-nums}.hlv2-c .st{font:700 10.5px/1 system-ui,sans-serif;fill:#fff}' +
    '.hlv2-c .gr{transform-origin:0 50%;animation:hlvg .7s cubic-bezier(.2,.8,.2,1) both}.hlv2-c .gc{transform-box:fill-box;transform-origin:50% 100%;animation:hlvc .7s cubic-bezier(.2,.8,.2,1) both}@keyframes hlvc{from{transform:scaleY(0)}}.hlv2-c .k-donut circle{animation:hlvf .6s ease both}@keyframes hlvg{from{transform:scaleX(0)}}@keyframes hlvf{from{opacity:0}}' +
    '@media (prefers-reduced-motion:reduce){.hlv2-c .gr,.hlv2-c .k-donut circle{animation:none}}' +
    '.hlv[data-hlv2] ul{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:7px 16px}' +
    '[dir=rtl] .hlv,[dir=rtl] .hlx{direction:rtl}';
  var T = (function (l) {
    var M = { ko: ['한눈에 비교', '비율', '변화 추이'], ja: ['ひと目で比較', '割合', '推移'], zh: ['一目了然', '比例', '变化趋势'],
      zht: ['一目了然', '比例', '變化趨勢'], de: ['Auf einen Blick', 'Anteile', 'Verlauf'], fr: ['En un coup d’œil', 'Proportions', 'Évolution'],
      es: ['De un vistazo', 'Proporciones', 'Evolución'], pt: ['Visão geral', 'Proporções', 'Evolução'], it: ['A colpo d’occhio', 'Proporzioni', 'Andamento'],
      nl: ['In één oogopslag', 'Verhoudingen', 'Verloop'], pl: ['W skrócie', 'Proporcje', 'Zmiany w czasie'], ru: ['Наглядно', 'Доли', 'Динамика'],
      vi: ['Tổng quan', 'Tỷ lệ', 'Diễn biến'], id: ['Sekilas', 'Proporsi', 'Perkembangan'], hi: ['एक नज़र में', 'अनुपात', 'समय के साथ'],
      ar: ['نظرة سريعة', 'النسب', 'التغير بمرور الوقت'] };
    l = String(l || '').toLowerCase(); var k = /^zh-(hant|tw|hk)/.test(l) ? 'zht' : l.split('-')[0];
    var v = M[k] || ['At a glance', 'Rates', 'Over time']; return { cmp: v[0], rate: v[1], trend: v[2] };
  })(D.documentElement.lang);
  var st = D.createElement('style'); st.textContent = css; (D.head || D.documentElement).appendChild(st);

  function pctTxt(p) { return (p >= 10 ? Math.round(p) : Math.round(p * 10) / 10) + '%'; }
  function stripNum(t) { return t.replace(/[\s ]*[-−+]?[\$€£¥₩₹₱₽₺₫₦R$]*\s?[\d][\d.,\s ']*\s?(%|[A-Za-z₩€£¥₹₽₺₫₦円원元₱zł]{0,4}\.?)?\s*$/, '').trim() || t; }

  /* 결과 그래프 2개 + 종류 선택(도넛·막대·띠·파이) — 2026-11-28 */
  var KINDS = [['donut', 'M12 3a9 9 0 1 0 9 9h-4a5 5 0 1 1-5-5z'], ['bars', 'M4 5h14v3H4zM4 10.5h9v3H4zM4 16h5v3H4z'], ['stack', 'M3 9h7v6H3zM10 9h6v6h-6zM16 9h5v6h-5z'], ['pie', 'M12 3v9l7.8 4.5A9 9 0 1 1 12 3z']];
  var KLAB = { donut: 'Donut', bars: 'Bars', stack: '100% bar', pie: 'Pie', rings: 'Rings', hbar: 'Bars', cols: 'Columns' };
  var CKINDS = [['rings', 'M12 2a10 10 0 1 0 10 10h-3a7 7 0 1 1-7-7zM12 7a5 5 0 1 0 5 5h-3a2 2 0 1 1-2-2z'], ['hbar', 'M4 5h14v3H4zM4 10.5h9v3H4zM4 16h5v3H4z'], ['cols', 'M4 20V10h4v10zM10 20V4h4v16zM16 20v-7h4v7z']];
  function drawRings(items) {
    var mx = Math.max.apply(null, items.map(function (x) { return x.v; }));
    var svg = svgEl('svg', { viewBox: '0 0 120 120', role: 'img', translate: 'no', 'class': 'k-donut' });
    var n = items.length, w = Math.max(5, Math.min(9, 40 / n)), gap = w + 2.2;
    items.forEach(function (x, k) {
      var R = 52 - w / 2 - k * gap, C = 2 * Math.PI * R, f = Math.max(0.012, x.v / mx) * 0.75;
      [['#EEF1F6', C * 0.75], [x.c, C * f]].forEach(function (a) { svg.appendChild(svgEl('circle', { cx: 60, cy: 60, r: R, fill: 'none', stroke: a[0], 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-dasharray': a[1] + ' ' + C, transform: 'rotate(-90 60 60)' })); });
    });
    return svg;
  }
  function drawHBar(items) {
    var mx = Math.max.apply(null, items.map(function (x) { return x.v; })), h = items.length * 26 + 4;
    var svg = svgEl('svg', { viewBox: '0 0 240 ' + h, role: 'img', translate: 'no', 'class': 'k-bars' });
    items.forEach(function (x, k) {
      var y = 4 + k * 26; svg.appendChild(svgEl('rect', { x: 0, y: y, width: 160, height: 18, rx: 6, fill: '#EEF1F6' }));
      svg.appendChild(svgEl('rect', { x: 0, y: y, width: Math.max(2, x.v / mx * 160), height: 18, rx: 6, fill: x.c, 'class': 'gr' }));
      var t = svgEl('text', { x: 166, y: y + 13, 'class': 'bt' }); t.textContent = x.t.length > 12 ? x.t.slice(0, 12) : x.t; svg.appendChild(t);
    });
    return svg;
  }
  function drawCols(items) {
    var mx = Math.max.apply(null, items.map(function (x) { return x.v; })), n = items.length, bw = Math.min(34, 200 / n - 8);
    var svg = svgEl('svg', { viewBox: '0 0 240 150', role: 'img', translate: 'no', 'class': 'k-stack' });
    svg.appendChild(svgEl('line', { x1: 0, x2: 240, y1: 130, y2: 130, stroke: '#E2E8F0' }));
    items.forEach(function (x, k) {
      var cx = (k + 0.5) * 240 / n, hh = Math.max(2, x.v / mx * 104);
      svg.appendChild(svgEl('rect', { x: cx - bw / 2, y: 130 - hh, width: bw, height: hh, rx: 5, fill: x.c, 'class': 'gc' }));
      var t = svgEl('text', { x: cx, y: 124 - hh, 'text-anchor': 'middle', 'class': 'bt' }); t.textContent = x.t.length > 10 ? x.t.slice(0, 10) : x.t; svg.appendChild(t);
    });
    return svg;
  }
  function drawC(kind, items) { return kind === 'hbar' ? drawHBar(items) : kind === 'cols' ? drawCols(items) : drawRings(items); }
  function svgEl(n, a) { var e = D.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function drawDonut(segs, tot, pie) {
    var svg = svgEl('svg', { viewBox: '0 0 120 120', role: 'img', translate: 'no', 'class': 'k-donut' });
    var R = pie ? 30 : 46, W = pie ? 60 : 20, C = 2 * Math.PI * R, off = 0;
    if (!pie) svg.appendChild(svgEl('circle', { cx: 60, cy: 60, r: R, fill: 'none', stroke: '#EEF1F6', 'stroke-width': W }));
    segs.forEach(function (s) {
      var len = C * s.v / tot;
      svg.appendChild(svgEl('circle', { cx: 60, cy: 60, r: R, fill: 'none', stroke: s.c, 'stroke-width': W, 'stroke-dasharray': Math.max(len - (segs.length > 1 && len > 2 ? (pie ? .6 : 1.2) : 0), 0) + ' ' + C, 'stroke-dashoffset': -off, transform: 'rotate(-90 60 60)' }));
      off += len;
    });
    if (!pie) {
      var main = segs[0], t1 = svgEl('text', { x: 60, y: 62, 'text-anchor': 'middle', 'class': 'c1' }); t1.textContent = pctTxt(main.v / tot * 100);
      var t2 = svgEl('text', { x: 60, y: 78, 'text-anchor': 'middle', 'class': 'c2' }); var sh = stripNum(main.l); t2.textContent = sh.length > 16 ? sh.slice(0, 15) + '…' : sh;
      svg.appendChild(t1); svg.appendChild(t2);
    }
    return svg;
  }
  function drawBars(segs, tot) {
    var n = segs.length, h = n * 26 + 4, mx = Math.max.apply(null, segs.map(function (s) { return s.v; }));
    var svg = svgEl('svg', { viewBox: '0 0 240 ' + h, role: 'img', translate: 'no', 'class': 'k-bars' });
    segs.forEach(function (s, k) {
      var y = 4 + k * 26, w = Math.max(2, s.v / mx * 178);
      svg.appendChild(svgEl('rect', { x: 0, y: y, width: 178, height: 18, rx: 6, fill: '#EEF1F6' }));
      svg.appendChild(svgEl('rect', { x: 0, y: y, width: w, height: 18, rx: 6, fill: s.c, 'class': 'gr' }));
      var t = svgEl('text', { x: 186, y: y + 13, 'class': 'bt' }); t.textContent = pctTxt(s.v / tot * 100); svg.appendChild(t);
    });
    return svg;
  }
  function drawStack(segs, tot) {
    var svg = svgEl('svg', { viewBox: '0 0 240 64', role: 'img', translate: 'no', 'class': 'k-stack' }), x = 0;
    segs.forEach(function (s) {
      var w = s.v / tot * 240;
      svg.appendChild(svgEl('rect', { x: x, y: 14, width: Math.max(w - (segs.length > 1 ? 1 : 0), 0.5), height: 28, fill: s.c, 'class': 'gr' }));
      if (w > 30) { var t = svgEl('text', { x: x + w / 2, y: 33, 'text-anchor': 'middle', 'class': 'st' }); t.textContent = pctTxt(s.v / tot * 100); svg.appendChild(t); }
      x += w;
    });
    return svg;
  }
  function draw(kind, segs, tot) { return kind === 'bars' ? drawBars(segs, tot) : kind === 'stack' ? drawStack(segs, tot) : drawDonut(segs, tot, kind === 'pie'); }
  function pref(i, v) { try { if (v) localStorage.setItem('hlv-k' + i, v); return localStorage.getItem('hlv-k' + i); } catch (e) { return null; } }
  function panel(i, def, segs, tot, label, kinds, drawFn) {
    kinds = kinds || KINDS; drawFn = drawFn || draw;
    var p = D.createElement('div'); p.className = 'hlv2-p';
    var tabs = D.createElement('div'); tabs.className = 'hlv2-t'; tabs.setAttribute('role', 'tablist');
    var area = D.createElement('div'); area.className = 'hlv2-c';
    var cur = pref(i) || def; if (!kinds.some(function (kd) { return kd[0] === cur; })) cur = def;
    function show(k) {
      cur = k; area.innerHTML = ''; var g = drawFn(k, segs, tot); g.setAttribute('aria-label', label); area.appendChild(g);
      [].forEach.call(tabs.children, function (b) { b.setAttribute('aria-selected', b.getAttribute('data-k') === k ? 'true' : 'false'); });
    }
    kinds.forEach(function (kd) {
      var b = D.createElement('button'); b.type = 'button'; b.setAttribute('role', 'tab'); b.setAttribute('data-k', kd[0]); b.title = KLAB[kd[0]]; b.setAttribute('aria-label', KLAB[kd[0]]);
      var ic = svgEl('svg', { viewBox: '0 0 24 24', 'aria-hidden': 'true' }); ic.appendChild(svgEl('path', { d: kd[1] })); b.appendChild(ic);
      b.addEventListener('click', function () { pref(i, kd[0]); show(kd[0]); });
      tabs.appendChild(b);
    });
    p.appendChild(tabs); p.appendChild(area); show(cur);
    return p;
  }
  function build(segs, sig) {
    var tot = segs.reduce(function (a, s) { return a + s.v; }, 0);
    if (!(tot > 0)) return null;
    var box = D.createElement('div'); box.className = 'hlv'; box.setAttribute('data-hlv', sig); box.setAttribute('data-hlv2', '1');
    var lab = segs.map(function (s) { return s.l + ' ' + pctTxt(s.v / tot * 100); }).join(', ');
    var g = D.createElement('div'); g.className = 'hlv2-g';
    g.appendChild(panel(1, 'donut', segs, tot, lab)); g.appendChild(panel(2, 'bars', segs, tot, lab));
    var ul = D.createElement('ul');
    segs.forEach(function (s) {
      var li = D.createElement('li'); var dot = D.createElement('i'); dot.style.background = s.c;
      var sp = D.createElement('span'); sp.textContent = s.l; var b = D.createElement('b'); b.textContent = pctTxt(s.v / tot * 100);
      li.appendChild(dot); li.appendChild(sp); li.appendChild(b); ul.appendChild(li);
    });
    box.appendChild(g); box.appendChild(ul);
    return box;
  }

  function colorOf(el) { return (el.style.background || el.style.backgroundColor || '').trim(); }

  /* ---- 1) stacked bars ---- */
  function fromBar(bar) {
    var is = [].filter.call(bar.children, function (x) { return x.tagName === 'I' && /%/.test(x.style.width); });
    if (is.length < 2) return null;
    var leg = bar.nextElementSibling; if (!leg || !/legend/.test(leg.className)) leg = bar.parentNode.querySelector('.legend');
    var ls = leg ? [].slice.call(leg.children) : [];
    var segs = [], sum = 0;
    is.forEach(function (x, k) {
      var w = parseFloat(x.style.width) || 0; sum += w;
      var c = colorOf(x) || PAL[k % PAL.length];
      var l = ls[k] ? ls[k].textContent.trim() : '';
      if (w > 0.05) segs.push({ v: w, c: c, l: l || ('#' + (k + 1)) });
    });
    if (segs.length < 2 || sum < 85 || sum > 115) return null;
    return { segs: segs, hide: [bar].concat(leg ? [leg] : []) };
  }

  /* ---- 2) breakdown lists ---- */
  var DOTK = /^(de|nl|it|es|pt|tr|id|vi|da|nb|no|el|ro|sr|hr|sl|cs|sk|pl|hu)/.test((D.documentElement.lang || '').toLowerCase());
  function num(t) {
    t = (t || '').replace(/[\u00a0\s'’]/g, ''); if (/%/.test(t)) return null;
    if (/(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\d|\d{4}[-./]\d{1,2}[-./]\d{1,2}|\d{1,2}[:]\d{2}|[월화수목금토일]요일|\d+월\d+일|#[0-9a-fA-F]{3,8}\b/.test(t)) return null;
    var m = t.match(/^(.*?)(\d[\d.,]*)/); if (!m) return null;
    var neg = /[−\-–]/.test(m[1]), s = m[2].replace(/[.,]$/, '');
    var lc = s.lastIndexOf(','), ld = s.lastIndexOf('.');
    if (lc > -1 && ld > -1) s = lc > ld ? s.replace(/\./g, '').replace(',', '.') : s.replace(/,/g, '');
    else if (lc > -1) s = /^\d{1,3}(,\d{3})+$/.test(s) ? s.replace(/,/g, '') : s.replace(/,/g, '.');
    else if (ld > -1 && (s.split('.').length > 2 || (DOTK && /^\d{1,3}(\.\d{3})+$/.test(s)))) s = s.replace(/\./g, '');
    var v = parseFloat(s); return isFinite(v) ? { v: v, neg: neg } : null;
  }
  function rowsKv(kv) {
    var c = [].slice.call(kv.children), r = [];
    for (var i = 0; i + 1 < c.length; i += 2) { var l0 = c[i].cloneNode(true); [].forEach.call(l0.querySelectorAll('small,em,.sub,.c,br'), function (x) { x.remove(); });
      r.push({ l: l0.textContent.trim(), t: c[i + 1].textContent.trim(), cls: (c[i].className + ' ' + c[i + 1].className) }); }
    return r;
  }
  function rowsTable(tb) {
    return [].map.call(tb.querySelectorAll('tr'), function (tr) {
      var td = tr.querySelectorAll('td,th'); if (td.length !== 2) return null;
      var l0 = td[0].cloneNode(true); [].forEach.call(l0.querySelectorAll('small,em,.sub,.c,br'), function (s) { s.remove(); });
      return { l: l0.textContent.trim(), t: td[1].textContent.trim(), cls: tr.className };
    }).filter(Boolean);
  }
  function unit(t) { return (t || '').replace(/[\d.,\s\u00a0'’−\-–+()]/g, ''); }
  function fromRows(rows) {
    var R = [];
    rows.forEach(function (r) { var n = num(r.t); if (n) R.push({ l: r.l, v: n.v, neg: n.neg || /\bneg\b/.test(r.cls), t: /\b(t|netr|net|tot)\b/.test(r.cls), tot: /\btot\b/.test(r.cls), u: unit(r.t) }); });
    if (R.length < 3) return null;
    var k = -1; for (var i = 0; i < R.length; i++) if (R[i].t && !R[i].tot && !R[i].neg) { k = i; break; }
    if (k < 1) return null;
    var T = R[k], pre = R.slice(0, k).filter(function (x) { return !x.tot && !/^[•·\-–—*]/.test(x.l); });
    if (!pre.every(function (x) { return x.u === T.u; })) return null;
    var tol = function (a, b) { return Math.abs(a - b) <= Math.max(Math.abs(b) * 0.001, pre.length * 0.51); };
    var segs = null, negs = pre.filter(function (x) { return x.neg && x.v !== 0; });
    var pos = pre.filter(function (x) { return !x.neg; });
    var nsum = negs.reduce(function (a, x) { return a + Math.abs(x.v); }, 0);
    if (negs.length && pos.length === 1 && T.v > 0 && tol(T.v + nsum, pos[0].v)) {           // gross − deductions = net
      segs = [{ l: T.l, v: T.v }].concat(negs.map(function (x) { return { l: x.l, v: Math.abs(x.v) }; }));
    } else if (negs.length && pos.length === 0 && T.v > 0) {                                  // deductions … net (gross not listed)
      segs = [{ l: T.l, v: T.v }].concat(negs.map(function (x) { return { l: x.l, v: Math.abs(x.v) }; }));
    } else if (!negs.length && pos.length >= 2 && tol(pos.reduce(function (a, x) { return a + x.v; }, 0), T.v)) { // parts = total
      var ps = pos.reduce(function (a, x) { return a + x.v; }, 0);
      if (pos.some(function (x) { return x.v > 0 && tol(ps - x.v, T.v); })) return null;               // ambiguous: a part is not needed
      segs = pos.filter(function (x) { return x.v > 0; }).map(function (x) { return { l: x.l, v: x.v }; });
    }
    if (!segs || segs.length < 2) return null;
    if (segs.length > 9) { var rest = segs.slice(8).reduce(function (a, x) { return a + x.v; }, 0); segs = segs.slice(0, 8).concat([{ l: '…', v: rest }]); }
    segs.forEach(function (x, j) { x.c = x.l === '…' ? '#A0AEC8' : PAL[j % PAL.length]; });
    return { segs: segs, hide: [] };
  }

  function place(anchor, res, sig) {
    var prev = anchor.previousElementSibling;
    if (prev && prev.className === 'hlv' && !prev.hasAttribute('data-hlx')) { if (prev.getAttribute('data-hlv') === sig) return; prev.remove(); }
    var box = build(res.segs, sig); if (!box) return;
    anchor.parentNode.insertBefore(box, anchor);
    res.hide.forEach(function (h) { h.style.display = 'none'; });
  }

  function scan() {
    var done = [];
    [].forEach.call(D.querySelectorAll('.bar, .split'), function (bar) {
      if (bar.closest('.hlv,nav,header,footer')) return;
      var res = fromBar(bar); if (!res) return;
      var sig = 'b' + [].map.call(bar.children, function (x) { return x.style.width + colorOf(x); }).join('|');
      var leg = res.hide[1]; if (leg) sig += leg.textContent;
      place(bar, res, sig); done.push(bar.closest('section,article,div') || bar.parentNode);
    });
    [].forEach.call(D.querySelectorAll('.kv, table'), function (el) {
      if (el.closest('.hlv,nav,header,footer,.help,.faq,details')) return;
      var host = el.closest('[aria-live],#out,#result,.result,.res'); if (!host) return;
      if (host.querySelector('.hlv[data-hlv^="b"]')) return;
      var rows = el.tagName === 'TABLE' ? rowsTable(el) : rowsKv(el);
      var res = fromRows(rows); if (!res) return;
      var sig = 'r' + res.segs.map(function (s) { return s.l + s.v; }).join('|');
      place(el, res, sig);
    });
  }

  /* ---- 3) extra infographics: trend lines (tables), comparison bars, rate gauges ---- */
  function pctOf(t) { var m = (t || '').replace(/[ \s]/g, '').match(/^[^\d−\-]*([−\-]?\d[\d.,]*)%$/); if (!m) return null; var n = num(m[1]); return n ? (m[1].charAt(0) === '−' || m[1].charAt(0) === '-' ? -n.v : n.v) : null; }
  function fmtN(v) { var a = Math.abs(v); return a >= 1e9 ? (v / 1e9).toFixed(a >= 1e10 ? 0 : 1) + 'B' : a >= 1e6 ? (v / 1e6).toFixed(a >= 1e7 ? 0 : 1) + 'M' : a >= 1e4 ? Math.round(v / 1e3) + 'k' : (Math.round(v * 100) / 100).toLocaleString(); }
  function box(kind, title, sig) { var b = D.createElement('div'); b.className = 'hlx'; b.setAttribute('data-hlx', kind + sig); var h = D.createElement('h4'); h.textContent = title; b.appendChild(h); return b; }
  function putAfter(el, b) {
    var nx = el.nextElementSibling;
    if (nx && nx.hasAttribute && nx.hasAttribute('data-hlx')) { if (nx.getAttribute('data-hlx') === b.getAttribute('data-hlx')) return nx; nx.remove(); }
    el.parentNode.insertBefore(b, el.nextSibling); return b;
  }
  function prune(host, keep) {   /* drop charts left over from an earlier result (e.g. a ring that showed NaN while a field was empty) */
    [].forEach.call(host.querySelectorAll('[data-hlx]'), function (x) { if (x !== keep && x.getAttribute('data-hlx') !== 'u' && !(keep && keep.contains(x))) x.remove(); });
  }
  function bars(items, sig) {   /* comparison — 2 graphs with a type picker (rings, bars, columns) */
    var mx = Math.max.apply(null, items.map(function (x) { return x.v; })); if (!(mx > 0)) return null;
    var bx = D.createElement('div'); bx.className = 'hlv'; bx.setAttribute('data-hlx', 'b' + sig); bx.classList.add('hlx-r'); bx.setAttribute('data-hlv2', '1');
    items.forEach(function (x, k) { x.c = PAL[k % PAL.length]; });
    var lab = items.map(function (x) { return x.l + ' ' + x.t; }).join(', ');
    var g = D.createElement('div'); g.className = 'hlv2-g';
    g.appendChild(panel(3, 'rings', items, 0, lab, CKINDS, drawC)); g.appendChild(panel(4, 'hbar', items, 0, lab, CKINDS, drawC));
    var ul = D.createElement('ul');
    items.forEach(function (x) { var li = D.createElement('li'), dot = D.createElement('i'), sp = D.createElement('span'), b = D.createElement('b'); dot.style.background = x.c; sp.textContent = x.l; b.textContent = x.t; li.appendChild(dot); li.appendChild(sp); li.appendChild(b); ul.appendChild(li); });
    bx.appendChild(g); bx.appendChild(ul); return bx;
  }
  function gauges(items, sig) {
    var b = box('g', T.rate, sig), g = D.createElement('div'); g.className = 'gg';
    items.forEach(function (x, k) {
      var f = D.createElement('figure'), svg = D.createElementNS(NS, 'svg'); svg.setAttribute('translate', 'no'); svg.setAttribute('viewBox', '0 0 100 100'); svg.setAttribute('width', 96); svg.setAttribute('height', 96);
      var R = 40, C = 2 * Math.PI * R, p = Math.max(0, Math.min(100, x.v));
      [['#EEF1F6', C], [PAL[k % PAL.length], C * p / 100]].forEach(function (a, j) {
        var c = D.createElementNS(NS, 'circle'); c.setAttribute('cx', 50); c.setAttribute('cy', 50); c.setAttribute('r', R); c.setAttribute('fill', 'none');
        c.setAttribute('stroke', a[0]); c.setAttribute('stroke-width', 12); c.setAttribute('stroke-linecap', j ? 'round' : 'butt');
        c.setAttribute('stroke-dasharray', a[1] + ' ' + C); c.setAttribute('transform', 'rotate(-90 50 50)'); svg.appendChild(c);
      });
      var t = D.createElementNS(NS, 'text'); t.setAttribute('x', 50); t.setAttribute('y', 56); t.setAttribute('text-anchor', 'middle');
      t.setAttribute('style', 'font:800 17px system-ui,sans-serif;fill:#12305C'); t.textContent = x.t; svg.appendChild(t);
      var cap = D.createElement('figcaption'); cap.textContent = x.l; f.appendChild(svg); f.appendChild(cap); g.appendChild(f);
    });
    b.appendChild(g); return b;
  }
  function lines(xs, series, sig) {
    var W = 600, H = 220, L = 48, Rr = 12, Tp = 12, Bt = 28, all = [];
    series.forEach(function (s) { all = all.concat(s.v); });
    var mn = Math.min(0, Math.min.apply(null, all)), mx = Math.max.apply(null, all); if (!(mx > mn)) return null;
    var X = function (i) { return L + (W - L - Rr) * (xs.length < 2 ? 0 : i / (xs.length - 1)); }, Y = function (v) { return Tp + (H - Tp - Bt) * (1 - (v - mn) / (mx - mn)); };
    var b = box('l', T.trend, sig), svg = D.createElementNS(NS, 'svg'); svg.setAttribute('translate', 'no'); svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H); svg.setAttribute('class', 'ln');
    function el(n, a) { var e = D.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); svg.appendChild(e); return e; }
    for (var g = 0; g <= 4; g++) { var v = mn + (mx - mn) * g / 4, y = Y(v); el('line', { x1: L, x2: W - Rr, y1: y, y2: y, stroke: '#E6EAF1', 'stroke-width': 1 });
      var tx = el('text', { x: L - 6, y: y + 4, 'text-anchor': 'end', style: 'font:11px system-ui,sans-serif;fill:#7A8494' }); tx.textContent = fmtN(v); }
    var step = Math.max(1, Math.ceil(xs.length / 7));
    xs.forEach(function (x, i) { if (i % step && i !== xs.length - 1) return; var t = el('text', { x: X(i), y: H - 8, 'text-anchor': 'middle', style: 'font:11px system-ui,sans-serif;fill:#7A8494' }); t.textContent = x.length > 8 ? x.slice(0, 8) : x; });
    series.forEach(function (s, k) {
      var c = PAL[k % PAL.length], pts = s.v.map(function (v, i) { return X(i) + ',' + Y(v); }).join(' ');
      if (series.length === 1) el('polygon', { points: X(0) + ',' + Y(mn) + ' ' + pts + ' ' + X(s.v.length - 1) + ',' + Y(mn), fill: c, 'fill-opacity': .12 });
      el('polyline', { points: pts, fill: 'none', stroke: c, 'stroke-width': 3, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
    });
    svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', series.map(function (s) { return s.l; }).join(', '));
    b.appendChild(svg);
    var lg = D.createElement('div'); lg.className = 'lg';
    series.forEach(function (s, k) { var sp = D.createElement('span'), i = D.createElement('i'); i.style.background = PAL[k % PAL.length]; sp.appendChild(i); sp.appendChild(D.createTextNode(s.l)); lg.appendChild(sp); });
    b.appendChild(lg); return b;
  }
  function fromTable(tb) {
    var trs = [].slice.call(tb.querySelectorAll('tr')); if (trs.length < 4) return null;
    var head = trs[0].querySelectorAll('th').length ? [].map.call(trs[0].children, function (c) { return c.textContent.trim(); }) : null;
    var body = trs.slice(head ? 1 : 0).map(function (tr) { return [].map.call(tr.children, function (c) { return c.textContent.trim(); }); })
      .filter(function (r) { return r.length >= 2; });
    if (body.length < 3 || !head) return null;
    var nc = head.length, cols = [];
    for (var c = 1; c < nc && cols.length < 3; c++) {
      var vals = [], u = null, ok = true;
      for (var r = 0; r < body.length; r++) { var t = body[r][c]; if (t == null) { ok = false; break; } var n = num(t); if (!n || /%/.test(t)) { ok = false; break; }
        var uu = unit(t); if (u === null) u = uu; else if (uu !== u) { ok = false; break; } vals.push(n.neg ? -n.v : n.v); }
      if (ok && vals.some(function (v) { return v !== vals[0]; })) cols.push({ l: head[c], v: vals, u: u });
    }
    if (!cols.length) return null;
    var u0 = cols[0].u; cols = cols.filter(function (x) { return x.u === u0; });
    var xs = body.map(function (r) { return r[0]; });
    if (xs.length > 60) { var k = Math.ceil(xs.length / 60); xs = xs.filter(function (_, i) { return i % k === 0; }); cols.forEach(function (c) { c.v = c.v.filter(function (_, i) { return i % k === 0; }); }); }
    return { xs: xs, s: cols };
  }
  function headRows(host) {
    var bg = host.querySelector('.big'); if (!bg) return [];
    var out = [], sp = bg.querySelector('span,.k'), bb = bg.querySelector('b,strong');
    if (bb && sp) out.push({ l: sp.textContent.trim().replace(/[:=]$/, ''), t: bb.textContent.trim() });
    var em = bg.querySelector('em,.sub'); if (em) em.textContent.split(/\s[·•|]\s|;\s/).forEach(function (part) {
      var m = part.trim().match(/^(.*[^\d\s.,−\-])\s*[:=]?\s*([−\-]?[^\d\s]{0,4}\s?\d[\d.,\s ]*\s?[^\d\s.,]{0,4})$/); if (m && m[1].length < 40) out.push({ l: m[1].trim(), t: m[2].trim() }); });
    return out;
  }
  function listRows(host) {
    var r = [];
    [].forEach.call(host.querySelectorAll('ul.lines li, .total'), function (li) { var c = li.children; if (c.length === 2 && !/\bsub\b/.test(li.className)) r.push({ l: c[0].textContent.trim(), t: c[1].textContent.trim(), cls: li.className }); });
    return r;
  }
  function single(host, sig) {
    return null; /* 값 하나만 있는 결과에 붙던 장식 도넛은 정보가 없고 색·글자가 어긋나서 끔 */
    var bg = host.querySelector('.big,.total,.hero-res'); if (!bg) return null;
    var bb = bg.querySelector('b,strong') || bg, sp = bg.querySelector('span,.k');
    var v = bb.textContent.trim(); if (!v || v.length > 26 || /NaN|Infinity/.test(v)) return null;
    var bx = D.createElement('div'); bx.className = 'hlv hlx-s'; bx.setAttribute('data-hlx', 's' + sig);
    var svg = D.createElementNS(NS, 'svg'); svg.setAttribute('translate', 'no'); svg.setAttribute('viewBox', '0 0 120 120'); svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', (sp ? sp.textContent.trim() + ' ' : '') + v);
    var gid = 'hlg' + Math.random().toString(36).slice(2, 7), df = D.createElementNS(NS, 'defs'), lg = D.createElementNS(NS, 'linearGradient');
    lg.setAttribute('id', gid); lg.setAttribute('x1', 0); lg.setAttribute('y1', 0); lg.setAttribute('x2', 1); lg.setAttribute('y2', 1);
    [['0', '#4F46E5'], ['.55', '#7C3AED'], ['1', '#EC4899']].forEach(function (x) { var st = D.createElementNS(NS, 'stop'); st.setAttribute('offset', x[0]); st.setAttribute('stop-color', x[1]); lg.appendChild(st); });
    df.appendChild(lg); svg.appendChild(df);
    var c = D.createElementNS(NS, 'circle'); c.setAttribute('cx', 60); c.setAttribute('cy', 60); c.setAttribute('r', 48); c.setAttribute('fill', 'none'); c.setAttribute('stroke', 'url(#' + gid + ')'); c.setAttribute('stroke-width', 14); svg.appendChild(c);
    var t = D.createElementNS(NS, 'text'); t.setAttribute('x', 60); t.setAttribute('y', 65); t.setAttribute('text-anchor', 'middle');
    t.setAttribute('style', 'font:800 ' + (v.length > 14 ? 10 : v.length > 11 ? 12 : v.length > 8 ? 15 : 19) + 'px system-ui,sans-serif;fill:#12305C'); t.textContent = v; svg.appendChild(t);
    var ul = D.createElement('ul'), li = D.createElement('li'), dot = D.createElement('i'), s1 = D.createElement('span'), b1 = D.createElement('b');
    dot.style.background = '#4F46E5'; s1.textContent = sp ? sp.textContent.trim() : ''; b1.textContent = v; li.appendChild(dot); li.appendChild(s1); li.appendChild(b1); ul.appendChild(li);
    bx.appendChild(svg); bx.appendChild(ul); return { box: bx, anchor: bg };
  }
  function extra() {
    var hosts = [].slice.call(D.querySelectorAll('[aria-live],#out,#result')).filter(function (h, i, a) { return !h.closest('nav,header,footer,.hlv') && !a.some(function (o) { return o !== h && o.contains(h); }); });
    hosts.forEach(function (host) {
      if (!host.textContent.trim() || host.querySelector('.hlv[data-hlv], [data-hlx="u"]')) return;
      var rows = headRows(host).concat(listRows(host));
      [].forEach.call(host.querySelectorAll('.kv, table'), function (el) { if (!el.closest('.hlv,.hlx')) rows = rows.concat(el.tagName === 'TABLE' ? rowsTable(el) : rowsKv(el)); });
      var anchor = host.querySelector('.kv, table, ul.lines, .total, .big') || host.lastElementChild; if (!anchor) return;
      if (anchor.closest('.scroll')) anchor = anchor.closest('.scroll');
      var nums = [], pcs = [], seen = {};
      rows.forEach(function (r) { var p = pctOf(r.t); if (p !== null) { if (p >= 0 && p <= 100 && pcs.length < 4) pcs.push({ l: stripNum(r.l), v: p, t: r.t.replace(/\s/g, '') }); return; }
        var n = num(r.t); if (!n || !(n.v > 0)) return; var u = unit(r.t), key = u + '|' + n.v; if (seen[key]) return; seen[key] = 1; nums.push({ l: r.l, v: n.v, t: r.t, u: u }); });
      var groups = {}; nums.forEach(function (x) { (groups[x.u] = groups[x.u] || []).push(x); });
      var best = null; for (var u in groups) if (u && (!best || groups[u].length > best.length)) best = groups[u];
      var b = null;
      if (best && best.length >= 2) { best = best.slice(0, 6); b = bars(best, best.map(function (x) { return x.l + x.v; }).join('|')); }
      else if (pcs.length) b = gauges(pcs, pcs.map(function (x) { return x.l + x.v; }).join('|'));
      if (b) { prune(host, putAfter(anchor, b)); return; }
      var bgx = host.querySelector('.big,.total,.hero-res'); var sg = bgx && single(host, bgx.textContent.slice(0, 120)); prune(host, sg ? putAfter(sg.anchor, sg.box) : null);
    });
  }
  var tm = null;
  function later() { if (tm) return; tm = setTimeout(function () { tm = null; try { scan(); } catch (e) { } try { extra(); } catch (e) { } }, 80); }
  function start() {
    later();
    try { new MutationObserver(function (ms) { for (var i = 0; i < ms.length; i++) { var t = ms[i].target; if (t.closest && t.closest('.hlv,.hlx,.hlx-r')) continue; later(); return; } })
      .observe(D.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['style'], characterData: true }); } catch (e) { }
  }
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', start); else start();
})();
