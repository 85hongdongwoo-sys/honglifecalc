/* 실시간 지진 지도 (USGS GeoJSON 피드, 배포 때 넣은 최근 7일 M4.5+ 스냅샷으로 먼저 그림) */
(function () {
  'use strict';
  var C = window.QKCFG, T = C.t, $ = function (id) { return document.getElementById(id); };
  var LOC = document.documentElement.lang || 'en';
  var FEED = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/';
  var st = { mag: '4.5', per: 'week', sort: 'time', near: false }, here = null, data = [], map, layer, me;
  try { var sv = JSON.parse(localStorage.getItem('hl-qk') || '{}'); ['mag', 'per'].forEach(function (k) { if (sv[k]) st[k] = sv[k]; }); } catch (e) {}
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var nf = function (x, d) { return Number(x).toLocaleString(LOC, { maximumFractionDigits: d, minimumFractionDigits: d }); };
  var rtf = null; try { rtf = new Intl.RelativeTimeFormat(LOC, { numeric: 'auto', style: 'short' }); } catch (e) {}
  function ago(ms) {
    var s = (ms - Date.now()) / 1000, a = Math.abs(s);
    if (!rtf) return new Date(ms).toLocaleString(LOC);
    if (a < 3600) return rtf.format(Math.round(s / 60), 'minute');
    if (a < 86400) return rtf.format(Math.round(s / 3600), 'hour');
    return rtf.format(Math.round(s / 86400), 'day');
  }
  var dist = function (a, b, c, d) { var R = 6371, r = Math.PI / 180, x = Math.sin((c - a) * r / 2), y = Math.sin((d - b) * r / 2); return 2 * R * Math.asin(Math.sqrt(x * x + Math.cos(a * r) * Math.cos(c * r) * y * y)); };
  var col = function (t) { var h = (Date.now() - t) / 3600000; return h < 1 ? '#D7263D' : h < 24 ? '#F28C28' : '#E9C46A'; };
  var magCol = function (m) { return m >= 7 ? '#7F1D1D' : m >= 6 ? '#B42318' : m >= 5 ? '#D9480F' : m >= 4 ? '#E67700' : '#5B6B82'; };
  function fromFeed(j) {
    return j.features.filter(function (f) { return f.properties.mag != null; }).map(function (f) {
      var g = f.geometry.coordinates, p = f.properties;
      return [g[1], g[0], g[2] || 0, p.mag, p.time, p.place || '', p.tsunami || 0, p.url, p.felt || 0];
    });
  }
  function pop(q) {
    var d = here ? dist(here.lat, here.lng, q[0], q[1]) : null;
    return '<div style="font-size:13px;line-height:1.5;max-width:240px"><b style="font-size:15px">M' + nf(q[3], 1) + '</b> ' + esc(q[5]) +
      '<br>' + new Date(q[4]).toLocaleString(LOC) + ' (' + ago(q[4]) + ')<br>' + T.depth + ' ' + nf(q[2], 0) + ' km' +
      (d != null ? '<br><b>' + nf(d, 0) + ' ' + T.away + '</b>' : '') + (q[6] ? '<br><span class="qk-tsu">' + T.tsu + '</span>' : '') +
      '<br><a href="' + esc(q[7]) + '" target="_blank" rel="noopener">USGS ↗</a> · <a href="' + esc(q[7]) + '/tellus" target="_blank" rel="noopener">' + T.felt + '</a></div>';
  }
  function draw() {
    var list = data.filter(function (q) { return !st.near || !here || dist(here.lat, here.lng, q[0], q[1]) <= 500; });
    layer.clearLayers();
    list.slice().sort(function (a, b) { return a[3] - b[3]; }).forEach(function (q) {
      L.circleMarker([q[0], q[1]], { radius: Math.max(3, Math.min(28, Math.pow(2, q[3] - 2.2))), color: '#222', weight: .8, fillColor: col(q[4]), fillOpacity: .78 })
        .bindPopup(function () { return pop(q); }).addTo(layer);
    });
    var s = list.slice();
    if (st.sort === 'mag') s.sort(function (a, b) { return b[3] - a[3]; });
    else if (st.sort === 'near' && here) s.sort(function (a, b) { return dist(here.lat, here.lng, a[0], a[1]) - dist(here.lat, here.lng, b[0], b[1]); });
    else s.sort(function (a, b) { return b[4] - a[4]; });
    s = s.slice(0, 25);
    $('qk-list').innerHTML = s.length ? s.map(function (q, i) {
      var d = here ? dist(here.lat, here.lng, q[0], q[1]) : null;
      return '<li data-i="' + i + '"><span class="qk-m" style="background:' + magCol(q[3]) + '">' + nf(q[3], 1) + '</span><div><b>' + esc(q[5]) + (q[6] ? '<span class="qk-tsu">' + T.tsu + '</span>' : '') + '</b>' +
        '<small>' + ago(q[4]) + ' · ' + new Date(q[4]).toLocaleString(LOC, { dateStyle: 'short', timeStyle: 'short' }) + '</small><small>' + T.depth + ' ' + nf(q[2], 0) + ' km' + (d != null ? ' · <b style="display:inline;font-size:12.5px">' + nf(d, 0) + ' ' + T.away + '</b>' : '') + '</small></div></li>';
    }).join('') : '<li>' + T.none + '</li>';
    $('qk-list').querySelectorAll('li[data-i]').forEach(function (li) {
      li.addEventListener('click', function () { var q = s[+li.dataset.i]; map.setView([q[0], q[1]], Math.max(map.getZoom(), 6)); L.popup().setLatLng([q[0], q[1]]).setContent(pop(q)).openOn(map); });
    });
  }
  function load() {
    try { localStorage.setItem('hl-qk', JSON.stringify({ mag: st.mag, per: st.per })); } catch (e) {}
    var name = st.mag === 'significant' ? 'significant_' + st.per : st.mag + '_' + st.per;
    fetch(FEED + name + '.geojson', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (j) {
      data = fromFeed(j); draw();
      $('qk-live').textContent = T.live.replace('{t}', new Date().toLocaleTimeString(LOC, { hour: '2-digit', minute: '2-digit' }));
    }).catch(function () { if (!data.length) { data = C.snap; draw(); } });
  }
  function press(sel, b) { document.querySelectorAll(sel).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); }
  function init() {
    map = L.map('qk-map', { scrollWheelZoom: false, worldCopyJump: true }).setView(C.center, C.zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · USGS' }).addTo(map);
    layer = L.layerGroup().addTo(map);
    data = C.snap.slice(); draw();
    document.querySelectorAll('[data-mag]').forEach(function (b) { if (b.dataset.mag === st.mag) press('[data-mag]', b); b.addEventListener('click', function () { st.mag = b.dataset.mag; press('[data-mag]', b); load(); }); });
    document.querySelectorAll('[data-per]').forEach(function (b) { if (b.dataset.per === st.per) press('[data-per]', b); b.addEventListener('click', function () { st.per = b.dataset.per; press('[data-per]', b); load(); }); });
    document.querySelectorAll('[data-sort]').forEach(function (b) { b.addEventListener('click', function () { st.sort = b.dataset.sort; press('[data-sort]', b); if (st.sort === 'near' && !here) $('qk-loc').click(); draw(); }); });
    $('qk-near').addEventListener('click', function () { st.near = !st.near; this.setAttribute('aria-pressed', st.near ? 'true' : 'false'); if (st.near && !here) $('qk-loc').click(); draw(); });
    $('qk-loc').addEventListener('click', function () {
      var b = this; if (!navigator.geolocation) return;
      navigator.geolocation.getCurrentPosition(function (p) {
        here = L.latLng(p.coords.latitude, p.coords.longitude);
        if (me) me.remove(); me = L.circleMarker(here, { radius: 8, color: '#fff', weight: 3, fillColor: '#1971C2', fillOpacity: 1 }).addTo(map);
        L.circle(here, { radius: 500000, color: '#1971C2', weight: 1, fill: false, dashArray: '4 6' }).addTo(map);
        map.setView(here, 5); b.setAttribute('aria-pressed', 'true'); draw();
      }, function () {}, { timeout: 10000, maximumAge: 600000 });
    });
    load();
    setInterval(function () { if (document.visibilityState === 'visible') load(); }, 120000);
  }
  init();
})();
