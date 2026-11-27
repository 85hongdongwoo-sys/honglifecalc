/* Hong Life: Table / vertical column chart switch for result tables.
   <script src="/assets/hl-views.js" defer data-target="#out" data-lang="en"></script>
   Every money table inside the target gets a two-button switch. Bars are plain HTML,
   so they wrap on small screens instead of being cut off. */
(function () {
  'use strict';
  var me = document.currentScript;
  var SEL = (me && me.getAttribute('data-target')) || '#out';
  var LANG = (me && me.getAttribute('data-lang')) || document.documentElement.lang.slice(0, 2) || 'en';
  var TXT = {
    en: ['Table', 'Chart'], ko: ['표', '그래프'], es: ['Tabla', 'Gráfico'], de: ['Tabelle', 'Diagramm'],
    fr: ['Tableau', 'Graphique'], ja: ['表', 'グラフ'], pt: ['Tabela', 'Gráfico'], it: ['Tabella', 'Grafico'],
    nl: ['Tabel', 'Grafiek'], pl: ['Tabela', 'Wykres'], sv: ['Tabell', 'Diagram'], da: ['Tabel', 'Diagram'],
    no: ['Tabell', 'Diagram'], nb: ['Tabell', 'Diagram'], tr: ['Tablo', 'Grafik'], id: ['Tabel', 'Grafik'],
    ms: ['Jadual', 'Carta'], vi: ['Bảng', 'Biểu đồ'], zh: ['表格', '图表'], tw: ['表格', '圖表'], ru: ['Таблица', 'График'],
    hi: ['तालिका', 'चार्ट'], ar: ['جدول', 'رسم بياني']
  }[LANG] || ['Table', 'Chart'];
  var LAST = me && me.getAttribute('data-series') === 'last';
  var KEY = 'hlView';
  var COLORS = ['#3B82F6', '#F59E0B', '#10B981', '#8B5CF6'];

  function pref() { try { return localStorage.getItem(KEY) || 'table'; } catch (e) { return 'table'; } }
  function setPref(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function money(s) {
    s = (s || '').trim();
    if (!s || s.indexOf('%') >= 0 || !/\d/.test(s)) return null;
    if (/[−-]\s*[$€£¥₩]?\s*\d/.test(s)) return null; // deductions shown as negatives: keep in table only
    var n = parseFloat(s.replace(/[^0-9.]/g, ''));
    return isFinite(n) ? n : null;
  }

  function cellsOf(tr) { return Array.prototype.map.call(tr.children, function (c) { return c.textContent.trim(); }); }

  function build(table) {
    var head = table.querySelector('thead tr');
    var heads = head ? cellsOf(head) : [];
    var rows = Array.prototype.map.call(table.querySelectorAll('tbody tr'), cellsOf);
    if (rows.length < 2) return null;
    var ncol = Math.max.apply(null, rows.map(function (r) { return r.length; }));
    var num = [];
    for (var c = 1; c < ncol; c++) {
      var hits = rows.filter(function (r) { return money(r[c]) !== null; }).length;
      if (hits >= 2) num.push(c);
    }
    if (!num.length) return null;
    // 단위가 같은 열끼리만 한 그래프에 넣는다 (예: "$1,200"과 "12 months"는 섞지 않음)
    function unit(t) { var m = (t || '').trim().match(/^([^\d]*)[\d.,\s]+(.*)$/); return m ? m[1].trim() + '|' + m[2].trim() : '|'; }
    function colUnit(c) { var f = {}, best = '', n = 0; rows.forEach(function (r) { if (money(r[c]) === null) return; var u = unit(r[c]); f[u] = (f[u] || 0) + 1; if (f[u] > n) { n = f[u]; best = u; } }); return best; }
    var want = colUnit(num[num.length - 1]);
    num = num.filter(function (c) { return colUnit(c) === want; });
    // one money column = one series; for "Income | Tax" style tables use the last money column
    var series = !LAST && num.length > 1 && heads.length ? num : [num[num.length - 1]];
    var other = [];
    for (c = 1; c < ncol; c++) if (series.indexOf(c) < 0) other.push(c);
    var data = rows.map(function (r) {
      return { label: r[0], sub: other.map(function (i) { return r[i]; }).filter(Boolean).join(' · '),
               vals: series.map(function (i) { return { v: money(r[i]), t: r[i] }; }) };
    }).filter(function (d) { return d.vals.some(function (x) { return x.v !== null; }); });
    if (data.length < 2 && series.length < 2) return null;
    var max = 0;
    data.forEach(function (d) { d.vals.forEach(function (x) { if (x.v > max) max = x.v; }); });
    if (!max) return null;
    // 세로 막대(column) 그래프: 눈금선 + 값 + 아래 이름. 항목이 많으면 잘리지 않고 옆으로 밀어 볼 수 있다.
    var aff = ['', want.split('|')[0], want.split('|')[1] ? ' ' + want.split('|')[1] : ''];
    if (/^[%]/.test(aff[2].trim())) aff[2] = aff[2].trim();
    function nice(m) { var p = Math.pow(10, Math.floor(Math.log(m) / Math.LN10)), f = m / p, st = [1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10];
      for (var i = 0; i < st.length; i++) if (f <= st[i] + 1e-9) return st[i] * p; return 10 * p; }
    var top = nice(max / 4) * 4, loc = document.documentElement.lang || LANG;
    function fmt(v) { var a = Math.abs(v), d = a >= 100 || v === 0 ? 0 : a >= 10 ? 1 : 2; return aff[1] + v.toLocaleString(loc, { maximumFractionDigits: d }) + aff[2]; }
    var h = '';
    if (series.length > 1) {
      h += '<div class="hlsw-leg">' + series.map(function (i, k) {
        return '<span><i style="background:' + COLORS[k % 4] + '"></i>' + (heads[i] || '') + '</span>';
      }).join('') + '</div>';
    }
    var grid = '';
    for (var g = 4; g >= 0; g--) grid += '<div class="hlsw-gl" style="bottom:' + (g * 25) + '%"><span>' + fmt(top * g / 4) + '</span></div>';
    var gw = Math.max(28, series.length * 10 + 8);
    var lw = Math.max(fmt(top).length, fmt(top / 4).length) * 7 + 12;
    h += '<div class="hlsw-col"><div class="hlsw-plot" style="margin-left:' + lw + 'px;min-width:' + (data.length * gw + 8) + 'px">' + grid + '<div class="hlsw-groups">';
    data.forEach(function (d) {
      h += '<div class="hlsw-g"><div class="hlsw-cols">';
      d.vals.forEach(function (x, k) {
        var ht = x.v ? Math.max(0.8, x.v / top * 100) : 0;
        h += '<div class="hlsw-c" tabindex="0" title="' + (d.label + ': ' + (x.t || '—')).replace(/"/g, '&quot;') + '"><em>' + (x.t || '') + '</em>' +
             '<span style="height:' + ht.toFixed(1) + '%;background:' + COLORS[(series.length > 1 ? k : 0) % 4] + '"></span></div>';
      });
      h += '</div><div class="hlsw-x" title="' + (d.label + (d.sub ? ' · ' + d.sub : '')).replace(/"/g, '&quot;') + '"><b>' + d.label + '</b>' + (d.sub ? '<small>' + d.sub + '</small>' : '') + '</div></div>';
    });
    return h + '</div></div></div>';
  }

  var busy = false;
  function apply() {
    var roots = document.querySelectorAll(SEL);
    if (!roots.length) return;
    busy = true;
    Array.prototype.forEach.call(roots, function (root) { Array.prototype.forEach.call(root.querySelectorAll('table'), function (t) {
      if (t.getAttribute('data-hlsw')) return;
      t.setAttribute('data-hlsw', '1');
      var chart = build(t);
      if (!chart) return;
      var box = document.createElement('div');
      box.className = 'hlsw';
      box.innerHTML = '<div class="hlsw-sw" role="group">' +
        '<button type="button" data-v="table">' + TXT[0] + '</button>' +
        '<button type="button" data-v="bars">' + TXT[1] + '</button></div><div class="hlsw-chart"></div>';
      var wrap = t.parentNode && t.parentNode.classList && t.parentNode.classList.contains('tblwrap') ? t.parentNode : t;
      wrap.parentNode.insertBefore(box, wrap);
      box.appendChild(wrap);
      box._tab = wrap;
      box.querySelector('.hlsw-chart').innerHTML = chart;
      show(box, pref());
      box.querySelector('.hlsw-sw').addEventListener('click', function (e) {
        var v = e.target.getAttribute('data-v');
        if (!v) return;
        setPref(v);
        Array.prototype.forEach.call(document.querySelectorAll('.hlsw'), function (b) { show(b, v); });
      });
    }); });
    busy = false;
  }
  function show(box, v) {
    (box._tab || box.querySelector('table')).style.display = v === 'bars' ? 'none' : '';
    box.querySelector('.hlsw-chart').style.display = v === 'bars' ? '' : 'none';
    Array.prototype.forEach.call(box.querySelectorAll('.hlsw-sw button'), function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-v') === v ? 'true' : 'false');
    });
    var col = box.querySelector('.hlsw-col');
    if (col && v === 'bars') {
      var edge = function () { col.classList.toggle('hlsw-more', col.scrollLeft + col.clientWidth < col.scrollWidth - 4); };
      if (!col._e) { col._e = 1; col.addEventListener('scroll', edge, { passive: true }); window.addEventListener('resize', edge); }
      edge();
    }
  }

  var css = document.createElement('style');
  css.textContent =
    '.hlsw{margin:10px 0;width:100%;max-width:100%;min-width:0}' +
    '.hlsw-sw{display:inline-flex;background:#ececf0;border-radius:9px;padding:2px;margin:0 0 8px}' +
    '.hlsw-sw button{border:0;background:transparent;font:inherit;font-size:13px;padding:6px 14px;border-radius:7px;color:#3a3a3c;cursor:pointer;min-height:32px}' +
    '.hlsw-sw button[aria-pressed=true]{background:#fff;color:#1d1d1f;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.12)}' +
    '.hlsw-leg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:#6e6e73;margin:0 0 6px}' +
    '.hlsw-leg i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}' +
    '.hlsw-col{width:100%;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;padding:18px 0 0}' +
    '.hlsw-plot{position:relative;height:230px;margin:0 6px 64px 52px}' +
    '.hlsw-more{-webkit-mask-image:linear-gradient(90deg,#000 85%,transparent);mask-image:linear-gradient(90deg,#000 85%,transparent)}' +
    '.hlsw-gl{position:absolute;left:0;right:0;border-top:1px solid #ececf0;height:0}' +
    '.hlsw-gl:first-child{border-top-color:#ececf0}.hlsw-gl:last-of-type{border-top:1px solid #c7c7cc}' +
    '.hlsw-gl span{position:absolute;right:100%;top:-8px;padding-right:8px;font-size:11px;color:#8e8e93;white-space:nowrap;font-variant-numeric:tabular-nums}' +
    '.hlsw-groups{position:absolute;inset:0;display:flex;align-items:stretch}' +
    '.hlsw-g{flex:1 1 0;min-width:0;display:flex;flex-direction:column;position:relative}' +
    '.hlsw-cols{flex:1;display:flex;align-items:flex-end;justify-content:center;gap:4px;padding:0 4px}' +
    '.hlsw-c{outline:0;flex:0 1 24px;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;min-width:8px}' +
    '.hlsw-c span{display:block;width:100%;border-radius:4px 4px 0 0;transition:height .3s}' +
    '.hlsw-c em{font-style:normal;font-size:10.5px;color:#3a3a3c;white-space:nowrap;margin-bottom:3px;font-variant-numeric:tabular-nums;display:none}' +
    '.hlsw-plot:hover .hlsw-c em,.hlsw-c:focus-within em{display:block}' +
    '.hlsw-x{position:absolute;top:100%;left:1px;right:1px;padding-top:6px;text-align:center;font-size:12px;line-height:1.3;color:#3a3a3c;word-break:keep-all;overflow-wrap:break-word}' +
    '@media (max-width:480px){.hlsw-x{font-size:11px}.hlsw-x small{font-size:10px}}' +
    '.hlsw-x b,.hlsw-x small{display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden}' +
    '.hlsw-x b{font-weight:600;-webkit-line-clamp:2}.hlsw-x small{color:#8e8e93;font-size:11px;-webkit-line-clamp:1}' +
    '@media (prefers-reduced-motion:reduce){.hlsw-c span{transition:none}}';
  document.head.appendChild(css);

  function start() {
    apply();
    if (!window.MutationObserver) return;
    var timer;
    var mo = new MutationObserver(function () {
      if (busy) return;
      clearTimeout(timer);
      timer = setTimeout(apply, 30);
    });
    Array.prototype.forEach.call(document.querySelectorAll(SEL), function (root) { mo.observe(root, { childList: true, subtree: true }); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
