/* hl-viz: turns calculator result breakdowns into a donut infographic.
   Uses only numbers the calculator itself printed:
   1) stacked bars (.bar / .split with <i style="width:%">) + their .legend
   2) breakdown lists (.kv grid or table) where  first amount = sum of minus rows + last total row (checked to 0.5%) */
(function () {
  if (window.__hlViz) return; window.__hlViz = 1;
  var D = document, NS = 'http://www.w3.org/2000/svg';
  var PAL = ['#0F8A5F', '#1F5FD1', '#B8862B', '#C2413A', '#6C4BD8', '#0E8FA3', '#D9822B', '#7A8AA8', '#A34E8F', '#5B8C2A'];
  var css = '.hlv{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:14px 18px;margin:16px 0 6px;padding:14px;border:1px solid #E1E5EC;border-radius:14px;background:#FAFBFD}' +
    '.hlv svg{flex:0 0 auto;width:136px;height:136px}.hlv circle{transition:stroke-dasharray .6s ease,stroke-dashoffset .6s ease}' +
    '.hlv .c1{font:800 22px/1 system-ui,sans-serif;fill:#12305C}.hlv .c2{font:600 10.5px/1 system-ui,sans-serif;fill:#5F6875}' +
    '.hlv ul{list-style:none;margin:0;padding:0;flex:1 1 220px;min-width:0;display:grid;gap:7px}' +
    '.hlv li{display:grid;grid-template-columns:12px 1fr auto;gap:8px;align-items:center;font-size:13.5px;line-height:1.35;color:#2F343B}' +
    '.hlv li i{width:12px;height:12px;border-radius:4px}.hlv li b{font-variant-numeric:tabular-nums;color:#12305C}' +
    '.hlv li span{overflow-wrap:anywhere;word-break:keep-all}@media(max-width:380px){.hlv{gap:12px;padding:12px}.hlv svg{width:112px;height:112px}.hlv li{font-size:12.5px}}' +
'.hlx{margin:16px 0 6px;padding:14px 16px;border:1px solid #E1E5EC;border-radius:14px;background:#FAFBFD}.hlx h4{margin:0 0 10px;font:700 13px/1.3 system-ui,sans-serif;color:#5F6875;letter-spacing:.02em;text-transform:uppercase}' +
    '.hlv.hlx-r li{font-size:13px}@media(max-width:430px){.hlv.hlx-r svg,.hlv.hlx-s svg{width:108px;height:108px}}.hlx .br{display:grid;grid-template-columns:minmax(0,38%) 1fr;gap:10px;align-items:center;margin:7px 0;font-size:13.5px}.hlx .br span{overflow-wrap:anywhere;word-break:keep-all;color:#2F343B}' +
    '.hlx .br div{position:relative;height:22px;background:#EEF1F6;border-radius:7px;overflow:hidden}.hlx .br i{position:absolute;left:0;top:0;bottom:0;border-radius:7px;transition:width .6s ease}' +
    '.hlx .br b{position:absolute;right:8px;top:50%;transform:translateY(-50%);font:700 12px/1 system-ui,sans-serif;color:#12305C;font-variant-numeric:tabular-nums}' +
    '.hlx .gg{display:flex;flex-wrap:wrap;gap:14px;justify-content:space-around}.hlx .gg figure{margin:0;text-align:center;width:112px}.hlx .gg figcaption{font-size:12.5px;color:#2F343B;line-height:1.3;word-break:keep-all}' +
    '.hlx svg.ln{width:100%;height:auto;display:block}.hlx .lg{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:8px;font-size:12.5px;color:#2F343B}.hlx .lg i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}' +
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

  function build(segs, sig) {
    var tot = segs.reduce(function (a, s) { return a + s.v; }, 0);
    if (!(tot > 0)) return null;
    var box = D.createElement('div'); box.className = 'hlv'; box.setAttribute('data-hlv', sig);
    var svg = D.createElementNS(NS, 'svg'); svg.setAttribute('translate', 'no'); svg.setAttribute('viewBox', '0 0 120 120'); svg.setAttribute('role', 'img');
    var R = 46, C = 2 * Math.PI * R, off = 0, lab = [];
    var bg = D.createElementNS(NS, 'circle'); bg.setAttribute('cx', 60); bg.setAttribute('cy', 60); bg.setAttribute('r', R);
    bg.setAttribute('fill', 'none'); bg.setAttribute('stroke', '#EEF1F6'); bg.setAttribute('stroke-width', 20); svg.appendChild(bg);
    var ul = D.createElement('ul');
    segs.forEach(function (s, k) {
      var p = s.v / tot * 100, len = C * s.v / tot;
      var c = D.createElementNS(NS, 'circle'); c.setAttribute('cx', 60); c.setAttribute('cy', 60); c.setAttribute('r', R);
      c.setAttribute('fill', 'none'); c.setAttribute('stroke', s.c); c.setAttribute('stroke-width', 20);
      c.setAttribute('stroke-dasharray', Math.max(len - (segs.length > 1 && len > 2 ? 1.2 : 0), 0) + ' ' + C);
      c.setAttribute('stroke-dashoffset', -off); c.setAttribute('transform', 'rotate(-90 60 60)');
      svg.appendChild(c); off += len;
      var li = D.createElement('li'); var dot = D.createElement('i'); dot.style.background = s.c;
      var sp = D.createElement('span'); sp.textContent = s.l; var b = D.createElement('b'); b.textContent = pctTxt(p);
      li.appendChild(dot); li.appendChild(sp); li.appendChild(b); ul.appendChild(li);
      lab.push(s.l + ' ' + pctTxt(p));
    });
    var main = segs[0], mp = main.v / tot * 100;
    var t1 = D.createElementNS(NS, 'text'); t1.setAttribute('x', 60); t1.setAttribute('y', 62); t1.setAttribute('text-anchor', 'middle'); t1.setAttribute('class', 'c1'); t1.textContent = pctTxt(mp);
    var t2 = D.createElementNS(NS, 'text'); t2.setAttribute('x', 60); t2.setAttribute('y', 78); t2.setAttribute('text-anchor', 'middle'); t2.setAttribute('class', 'c2');
    var short = stripNum(main.l); t2.textContent = short.length > 16 ? short.slice(0, 15) + '…' : short;
    svg.appendChild(t1); svg.appendChild(t2); svg.setAttribute('aria-label', lab.join(', '));
    box.appendChild(svg); box.appendChild(ul);
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
  function bars(items, sig) {   /* radial (concentric ring) comparison — circular infographic */
    var mx = Math.max.apply(null, items.map(function (x) { return x.v; })); if (!(mx > 0)) return null;
    var bx = D.createElement('div'); bx.className = 'hlv'; bx.setAttribute('data-hlx', 'b' + sig); bx.classList.add('hlx-r');
    var svg = D.createElementNS(NS, 'svg'); svg.setAttribute('translate', 'no'); svg.setAttribute('viewBox', '0 0 120 120'); svg.setAttribute('role', 'img');
    var n = items.length, w = Math.max(5, Math.min(9, 40 / n)), gap = w + 2.2, ul = D.createElement('ul'), lab = [];
    items.forEach(function (x, k) {
      var R = 52 - w / 2 - k * gap, C = 2 * Math.PI * R, f = Math.max(0.012, x.v / mx) * 0.75, col = PAL[k % PAL.length];
      [['#EEF1F6', C * 0.75], [col, C * f]].forEach(function (a, j) {
        var c = D.createElementNS(NS, 'circle'); c.setAttribute('cx', 60); c.setAttribute('cy', 60); c.setAttribute('r', R); c.setAttribute('fill', 'none');
        c.setAttribute('stroke', a[0]); c.setAttribute('stroke-width', w); c.setAttribute('stroke-linecap', 'round');
        c.setAttribute('stroke-dasharray', a[1] + ' ' + C); c.setAttribute('transform', 'rotate(-90 60 60)'); svg.appendChild(c);
      });
      var li = D.createElement('li'), dot = D.createElement('i'), sp = D.createElement('span'), b = D.createElement('b');
      dot.style.background = col; sp.textContent = x.l; b.textContent = x.t; li.appendChild(dot); li.appendChild(sp); li.appendChild(b); ul.appendChild(li); lab.push(x.l + ' ' + x.t);
    });
    svg.setAttribute('aria-label', lab.join(', ')); bx.appendChild(svg); bx.appendChild(ul); return bx;
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
    [['0', '#0F8A5F'], ['.55', '#1F5FD1'], ['1', '#B8862B']].forEach(function (x) { var st = D.createElementNS(NS, 'stop'); st.setAttribute('offset', x[0]); st.setAttribute('stop-color', x[1]); lg.appendChild(st); });
    df.appendChild(lg); svg.appendChild(df);
    var c = D.createElementNS(NS, 'circle'); c.setAttribute('cx', 60); c.setAttribute('cy', 60); c.setAttribute('r', 48); c.setAttribute('fill', 'none'); c.setAttribute('stroke', 'url(#' + gid + ')'); c.setAttribute('stroke-width', 14); svg.appendChild(c);
    var t = D.createElementNS(NS, 'text'); t.setAttribute('x', 60); t.setAttribute('y', 65); t.setAttribute('text-anchor', 'middle');
    t.setAttribute('style', 'font:800 ' + (v.length > 14 ? 10 : v.length > 11 ? 12 : v.length > 8 ? 15 : 19) + 'px system-ui,sans-serif;fill:#12305C'); t.textContent = v; svg.appendChild(t);
    var ul = D.createElement('ul'), li = D.createElement('li'), dot = D.createElement('i'), s1 = D.createElement('span'), b1 = D.createElement('b');
    dot.style.background = '#1F5FD1'; s1.textContent = sp ? sp.textContent.trim() : ''; b1.textContent = v; li.appendChild(dot); li.appendChild(s1); li.appendChild(b1); ul.appendChild(li);
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
