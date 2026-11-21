/* 환율 계산기 (ECB 기준환율, /fx/latest.json · /fx/hist.json) */
(function () {
  'use strict';
  var C = window.FXCFG, L = C.L, $ = function (id) { return document.getElementById(id); };
  var R = null, H = null, SK = 'hl-fx-' + C.cur;
  var dn = null; try { dn = new Intl.DisplayNames([C.loc], { type: 'currency' }); } catch (e) {}
  var name = function (c) { try { return dn ? dn.of(c) : c; } catch (e) { return c; } };
  var nf = function (x) { var a = Math.abs(x), d = a >= 1000 ? 2 : a >= 1 ? 4 : a >= 0.01 ? 5 : 7; return x.toLocaleString(C.loc, { maximumFractionDigits: d, minimumFractionDigits: a >= 1000 ? 2 : 0 }); };
  var money = function (x, c) { try { return x.toLocaleString(C.loc, { style: 'currency', currency: c, maximumFractionDigits: 2 }); } catch (e) { return nf(x) + ' ' + c; } };
  var num = function (id) { var s = String($(id).value || '').replace(/\s/g, ''); if (s.indexOf(',') > -1 && s.indexOf('.') > -1) s = s.lastIndexOf(',') > s.lastIndexOf('.') ? s.replace(/\./g, '').replace(',', '.') : s.replace(/,/g, ''); else s = s.replace(',', '.'); var v = parseFloat(s); return isFinite(v) ? v : 0; };
  var f = $('fx-f'), t = $('fx-t');
  // 통화 이름 붙이기
  [f, t].forEach(function (sel) { Array.prototype.forEach.call(sel.options, function (o) { o.textContent = o.value + ' – ' + name(o.value); }); });
  document.querySelectorAll('.fx-n').forEach(function (s) { s.textContent = name(s.dataset.n); });
  var sv = {}; try { sv = JSON.parse(localStorage.getItem(SK) || '{}'); } catch (e) {}
  f.value = sv.f || C.cur; t.value = sv.t || C.to; if (sv.a) $('fx-a').value = sv.a; if (sv.fee) $('fx-fee').value = sv.fee;
  function save() { try { localStorage.setItem(SK, JSON.stringify({ f: f.value, t: t.value, a: $('fx-a').value, fee: $('fx-fee').value })); } catch (e) {} }
  function rate(a, b) { return R[b] / R[a]; }
  function calc() {
    if (!R) return;
    var a = num('fx-a'), x = rate(f.value, t.value), fee = Math.min(Math.max(num('fx-fee'), 0), 50) / 100, v = a * x;
    var rows = [[L.rate, '1 ' + f.value + ' = ' + nf(x) + ' ' + t.value], [L.inv, '1 ' + t.value + ' = ' + nf(1 / x) + ' ' + f.value]];
    if (fee > 0) rows.push([L.withFee, money(a * (1 + fee), f.value) + ' → ' + money(v, t.value) + ' / ' + money(a, f.value) + ' → ' + money(v * (1 - fee), t.value)]);
    $('fx-out').innerHTML = '<div class="big"><span>' + L.res + '</span><b>' + money(a, f.value) + ' = ' + money(v, t.value) + '</b><em>' + C.asof + '</em></div>' +
      '<div class="fx-kv">' + rows.map(function (r) { return '<div>' + r[0] + '</div><div>' + r[1] + '</div>'; }).join('') + '</div>';
    chart();
    save();
  }
  function chart() {
    if (!H) return;
    var a = H.rates[f.value], b = H.rates[t.value], pts = [];
    H.dates.forEach(function (d, i) { if (a[i] && b[i]) pts.push([d, b[i] / a[i]]); });
    $('fx-pair').textContent = f.value + '/' + t.value;
    if (pts.length < 2) { $('fx-chart').innerHTML = ''; $('fx-st').textContent = ''; return; }
    var ys = pts.map(function (p) { return p[1]; }), mn = Math.min.apply(0, ys), mx = Math.max.apply(0, ys), pad = (mx - mn) * 0.1 || mx * 0.01;
    var X = function (i) { return 4 + i * (592 / (pts.length - 1)); }, Y = function (v) { return 160 - (v - (mn - pad)) / ((mx + pad) - (mn - pad)) * 150; };
    var dpath = pts.map(function (p, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(p[1]).toFixed(1); }).join(' ');
    var up = ys[ys.length - 1] >= ys[0], col = up ? '#2F7D32' : '#C62828';
    $('fx-chart').innerHTML = '<path d="' + dpath + ' L596 170 L4 170 Z" fill="' + col + '" opacity=".08"/><path d="' + dpath + '" fill="none" stroke="' + col + '" stroke-width="2.5" vector-effect="non-scaling-stroke"/>';
    var ch = (ys[ys.length - 1] / ys[0] - 1) * 100;
    $('fx-st').innerHTML = '<span>' + pts[0][0] + ' → ' + pts[pts.length - 1][0] + '</span><span>' + L.hi + ' <b>' + nf(mx) + '</b></span><span>' + L.lo + ' <b>' + nf(mn) + '</b></span><span>' + L.chg + ' <b style="color:' + col + '">' + (ch >= 0 ? '+' : '') + ch.toFixed(2) + ' %</b></span>';
  }
  [f, t].forEach(function (s) { s.addEventListener('change', calc); });
  ['fx-a', 'fx-fee'].forEach(function (id) { $(id).addEventListener('input', calc); });
  $('fx-swap').addEventListener('click', function () { var x = f.value; f.value = t.value; t.value = x; calc(); });
  document.querySelectorAll('#fx-chips button').forEach(function (b) { b.addEventListener('click', function () { var p = b.dataset.p.split('-'); f.value = p[0]; t.value = p[1]; calc(); }); });
  document.querySelectorAll('.fx-tbl tbody tr').forEach(function (r) { r.addEventListener('click', function () { f.value = C.cur; t.value = r.dataset.c; calc(); $('fx-out').scrollIntoView({ behavior: 'smooth', block: 'center' }); }); });
  fetch('/fx/latest.json').then(function (r) { return r.json(); }).then(function (j) { R = j.rates; calc(); });
  fetch('/fx/hist.json').then(function (r) { return r.json(); }).then(function (j) { H = j; chart(); });
})();
