/* 전기차 충전소 지도 + 충전비 계산기 (나라별 정부 공식 충전소 자료, /ev/<cc>/) */
(function () {
  'use strict';
  var C = window.EVCFG, T = C.t, $ = function (id) { return document.getElementById(id); };
  var fmtN = function (x, d) { return Number(x).toLocaleString(C.locale, { maximumFractionDigits: d == null ? 1 : d, minimumFractionDigits: 0 }); };
  var money = function (x) { return Number(x).toLocaleString(C.locale, { style: 'currency', currency: C.cur, maximumFractionDigits: 2 }); };
  var num = function (id) {
    var s = String($(id).value || '').replace(/\s/g, '');
    if (s.indexOf(',') > -1 && s.indexOf('.') > -1) s = s.lastIndexOf(',') > s.lastIndexOf('.') ? s.replace(/\./g, '').replace(',', '.') : s.replace(/,/g, '');
    else s = s.replace(',', '.');
    var v = parseFloat(s); return isFinite(v) ? v : 0;
  };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var PL = [[1, 'Type 2'], [2, 'CCS'], [4, 'CHAdeMO'], [8, T.domestic], [16, 'Tesla'], [32, 'Type 1']];
  var plugs = function (b) { return PL.filter(function (p) { return b & p[0]; }).map(function (p) { return p[1]; }).join(' · ') || '–'; };
  var dist = function (a, b, c, d) { var R = 6371, r = Math.PI / 180, x = Math.sin((c - a) * r / 2), y = Math.sin((d - b) * r / 2); return 2 * R * Math.asin(Math.sqrt(x * x + Math.cos(a * r) * Math.cos(c * r) * y * y)); };
  var color = function (kw) { return kw >= 150 ? '#7C3AED' : kw >= 50 ? '#D9480F' : '#1971C2'; };

  /* ---------- calculator ---------- */
  function calc() {
    var bat = num('ev-bat'), from = num('ev-from'), to = num('ev-to'), ckw = num('ev-ckw'), car = num('ev-car'), loss = num('ev-loss'), price = num('ev-price'),
        cons = num('ev-cons'), fcons = num('ev-fcons'), fprice = num('ev-fprice');
    var out = $('ev-out');
    if (bat <= 0 || to <= from || ckw <= 0) { out.innerHTML = '<p class="ev-warn">' + T.check + '</p>'; return; }
    var into = bat * (to - from) / 100, grid = into / (1 - Math.min(Math.max(loss, 0), 50) / 100);
    var p = car > 0 ? Math.min(ckw, car) : ckw, hrs = into / p, h = Math.floor(hrs), m = Math.round((hrs - h) * 60);
    if (m === 60) { h++; m = 0; }
    var cost = grid * price, km = cons > 0 ? into / cons * 100 : 0, fuel = km * fcons / 100 * fprice;
    var rows = [[T.energy, fmtN(grid) + ' kWh'], [T.inBattery, fmtN(into) + ' kWh'], [T.time, (h ? h + ' h ' : '') + m + ' min'], [T.power, fmtN(p, 0) + ' kW']];
    if (km) rows.push([T.range, fmtN(km, 0) + ' km'], [T.per100, money(cons * price / (1 - loss / 100))]);
    if (km && fcons && fprice) rows.push([T.fuelSame, money(fuel)], [fuel > cost ? T.save : T.more, money(Math.abs(fuel - cost))]);
    out.innerHTML = '<div class="big"><span>' + T.cost + '</span><b>' + money(cost) + '</b><em>' + fmtN(from, 0) + ' → ' + fmtN(to, 0) + ' %</em></div>' +
      '<div class="kv">' + rows.map(function (r) { return '<div>' + r[0] + '</div><div>' + r[1] + '</div>'; }).join('') + '</div>' +
      '<p class="ev-note">' + T.calcNote + '</p>';
  }
  var KEEP = ['ev-bat', 'ev-from', 'ev-to', 'ev-car', 'ev-loss', 'ev-price', 'ev-cons', 'ev-fcons', 'ev-fprice'], SK = 'hl-ev-car-' + C.cc;
  try { var sv = JSON.parse(localStorage.getItem(SK) || '{}'); KEEP.forEach(function (id) { if (sv[id] != null && $(id)) $(id).value = sv[id]; }); } catch (e) {}
  function save() { try { var o = {}; KEEP.forEach(function (id) { if ($(id)) o[id] = $(id).value; }); localStorage.setItem(SK, JSON.stringify(o)); } catch (e) {} }
  ['ev-bat', 'ev-from', 'ev-to', 'ev-ckw', 'ev-car', 'ev-loss', 'ev-price', 'ev-cons', 'ev-fcons', 'ev-fprice'].forEach(function (id) { var e = $(id); if (e) e.addEventListener('input', function () { calc(); save(); draw(); }); });
  calc();
  /* 이 충전소에서 걸리는 시간·비용 (내 차 설정 기준) */
  function est(kw) {
    var bat = num('ev-bat'), from = num('ev-from'), to = num('ev-to'), car = num('ev-car'), loss = num('ev-loss'), price = num('ev-price');
    if (!kw || bat <= 0 || to <= from) return '';
    var into = bat * (to - from) / 100, p = car > 0 ? Math.min(kw, car) : kw, mins = Math.round(into / p * 60);
    var t = mins >= 60 ? Math.floor(mins / 60) + ' h ' + (mins % 60) + ' min' : mins + ' min';
    return '⏱ ' + t + ' · ' + money(into / (1 - loss / 100) * price) + ' (' + fmtN(from, 0) + '→' + fmtN(to, 0) + ' %)';
  }
  function nav(s) {
    var d = s[0] + ',' + s[1];
    return '<a href="https://www.google.com/maps/dir/?api=1&destination=' + d + '" target="_blank" rel="noopener">Google Maps</a>' +
      '<a href="https://maps.apple.com/?daddr=' + d + '" target="_blank" rel="noopener">Apple</a>' +
      '<a href="https://waze.com/ul?ll=' + d + '&navigate=yes" target="_blank" rel="noopener">Waze</a>';
  }
  function badges(b) { return (b & 64 ? '<span class="ev-b">24/7</span>' : '') + (b & 128 ? '<span class="ev-b ev-free">' + T.free + '</span>' : ''); }

  /* ---------- map ---------- */
  var meta = null, cache = {}, map, layer, here = null, minKw = 0, plugF = 0;
  function tileKeys(b) {
    var out = [], s = Math.floor(b.getSouth() * 2), n = Math.floor(b.getNorth() * 2), w = Math.floor(b.getWest() * 2), e = Math.floor(b.getEast() * 2);
    for (var a = s; a <= n; a++) for (var o = w; o <= e; o++) out.push(a + '_' + o);
    return out;
  }
  function load(keys) {
    var have = meta ? new Set(meta.tiles) : new Set();
    return Promise.all(keys.filter(function (k) { return have.has(k); }).map(function (k) {
      if (cache[k]) return cache[k];
      return (cache[k] = fetch('/ev/' + C.cc + '/t/' + k + '.json').then(function (r) { return r.json(); }).catch(function () { return []; }));
    })).then(function (a) { return [].concat.apply([], a); });
  }
  function ok(s) { return s[2] >= minKw && (!plugF || (s[6] & plugF)); }
  function popup(s, d) {
    var op = meta.ops[s[4]] || '';
    return '<div class="ev-pop"><b>' + esc(op) + '</b><br>' + esc(s[5]) + '<br><span class="ev-kw" style="background:' + color(s[2]) + '">' + (s[2] || '?') + ' kW</span> ' +
      s[3] + ' ' + T.points + ' ' + badges(s[6]) + '<br>' + esc(plugs(s[6])) + (s[8] ? '<br><small>' + esc(s[8]) + '</small>' : '') + (d != null ? '<br>' + fmtN(d) + ' km' : '') +
      '<br><b>' + est(s[2]) + '</b>' +
      '<div class="ev-btns">' + nav(s) +
      (s[7] ? '<a href="tel:' + esc(s[7].replace(/[^\d+]/g, '')) + '">' + T.call + '</a>' : '') +
      '<button type="button" data-kw="' + s[2] + '">' + T.useKw + '</button></div></div>';
  }
  function draw() {
    if (!map || !meta) return;
    var z = map.getZoom(), list = $('ev-list');
    if (z < 9) { layer.clearLayers(); list.innerHTML = '<p class="ev-note">' + T.zoomIn + '</p>'; return; }
    load(tileKeys(map.getBounds().pad(0.2))).then(function (all) {
      var b = map.getBounds(), c = here || map.getCenter(), vis = [];
      all.forEach(function (s) { if (ok(s) && b.contains([s[0], s[1]])) vis.push(s); });
      vis.forEach(function (s) { s.d = dist(c.lat, c.lng, s[0], s[1]); });
      vis.sort(function (a, b2) { return a.d - b2.d; });
      layer.clearLayers();
      vis.slice(0, 800).forEach(function (s) {
        L.circleMarker([s[0], s[1]], { radius: s[2] >= 50 ? 7 : 5, color: '#fff', weight: 1.5, fillColor: color(s[2]), fillOpacity: .9 })
          .bindPopup(function () { return popup(s, here ? s.d : null); }).addTo(layer);
      });
      var top = vis.slice(0, 15);
      list.innerHTML = '<p class="ev-cnt">' + T.inView.replace('{n}', fmtN(vis.length, 0)) + (here ? ' · ' + T.nearest : '') + '</p>' +
        (top.length ? '<ol class="ev-ol">' + top.map(function (s, i) {
          return '<li data-i="' + i + '"><div class="ev-l"><b>' + esc(meta.ops[s[4]] || '') + ' ' + badges(s[6]) + '</b><small>' + esc(s[5]) + '</small><small>' + esc(plugs(s[6])) + ' · ' + s[3] + ' ' + T.points + '</small>' +
            '<small class="ev-est">' + est(s[2]) + '</small><span class="ev-btns">' + nav(s) + (s[7] ? '<a href="tel:' + esc(s[7].replace(/[^\d+]/g, '')) + '">📞 ' + T.call + '</a>' : '') + '</span></div>' +
            '<div class="ev-r"><span class="ev-kw" style="background:' + color(s[2]) + '">' + (s[2] || '?') + ' kW</span>' + (here ? '<em>' + fmtN(s.d) + ' km</em>' : '') + '</div></li>';
        }).join('') + '</ol>' : '<p class="ev-note">' + T.none + '</p>');
      list.querySelectorAll('li[data-i]').forEach(function (li) {
        li.addEventListener('click', function (e) { if (e.target.closest('a')) return; var s = top[+li.dataset.i]; map.setView([s[0], s[1]], 16); L.popup().setLatLng([s[0], s[1]]).setContent(popup(s, here ? s.d : null)).openOn(map); });
      });
    });
  }
  function init() {
    map = L.map('ev-map', { scrollWheelZoom: false }).setView(C.center, 12);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' }).addTo(map);
    layer = L.layerGroup().addTo(map);
    map.on('moveend', draw);
    map.on('popupopen', function (e) {
      var b = e.popup.getElement().querySelector('button[data-kw]');
      if (b) b.addEventListener('click', function () { $('ev-ckw').value = b.dataset.kw; calc(); $('ev-calc').scrollIntoView({ behavior: 'smooth' }); });
    });
    fetch('/ev/' + C.cc + '/meta.json').then(function (r) { return r.json(); }).then(function (m) {
      meta = m;
      $('ev-stat').innerHTML = T.stat.replace('{s}', fmtN(m.stations, 0)).replace('{p}', fmtN(m.points, 0)).replace('{f}', fmtN(m.fast, 0)) +
        ' <a href="' + m.src_url + '" target="_blank" rel="noopener">' + esc(m.src) + '</a> (' + esc(m.license) + (m.stand ? ', ' + esc(m.stand) : '') + ')';
      draw();
    }).catch(function () { $('ev-stat').textContent = T.loadErr; });
  }
  $('ev-loc').addEventListener('click', function () {
    var b = this;
    if (!navigator.geolocation) { b.textContent = T.noGeo; return; }
    b.textContent = T.locating;
    navigator.geolocation.getCurrentPosition(function (p) {
      here = L.latLng(p.coords.latitude, p.coords.longitude);
      L.circleMarker(here, { radius: 8, color: '#fff', weight: 3, fillColor: '#111', fillOpacity: 1 }).addTo(map).bindTooltip(T.you);
      map.setView(here, 13); b.textContent = T.locDone;
    }, function () { b.textContent = T.noGeo; }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 });
  });
  var nf = $('ev-fast');
  if (nf) nf.addEventListener('click', function () {
    var go = function () {
      var c = here; load(tileKeys(L.latLngBounds([c.lat - 0.6, c.lng - 0.9], [c.lat + 0.6, c.lng + 0.9]))).then(function (all) {
        var best = null; all.forEach(function (s) { if (s[2] >= 50 && (!plugF || (s[6] & plugF))) { var d = dist(c.lat, c.lng, s[0], s[1]); if (!best || d < best.d) { best = s; best.d = d; } } });
        if (!best) { nf.textContent = T.noFast; return; }
        map.setView([best[0], best[1]], 15); L.popup().setLatLng([best[0], best[1]]).setContent(popup(best, best.d)).openOn(map);
      });
    };
    if (here) go(); else { $('ev-loc').click(); var w = setInterval(function () { if (here) { clearInterval(w); go(); } }, 300); setTimeout(function () { clearInterval(w); }, 15000); }
  });
  document.querySelectorAll('[data-minkw]').forEach(function (b) {
    b.addEventListener('click', function () { document.querySelectorAll('[data-minkw]').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); }); b.setAttribute('aria-pressed', 'true'); minKw = +b.dataset.minkw; draw(); });
  });
  var ps = $('ev-plug'); if (ps) ps.addEventListener('change', function () { plugF = +ps.value; draw(); });
  if (window.L) init(); else { var s = document.querySelector('script[src*="leaflet"]'); if (s) s.addEventListener('load', init); }
})();
