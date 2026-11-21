/* 오로라 예보 지도 (/geo/aurora_grid.json — NOAA OVATION, 배포 때 갱신) */
(function () {
  'use strict';
  var C = window.AUCFG, T = C.t, $ = function (id) { return document.getElementById(id); };
  var LOC = document.documentElement.lang || 'en', G = null, map, cells = {}, here = null;
  var col = function (p) { return p >= 50 ? '#E03131' : p >= 30 ? '#F08C00' : p >= 10 ? '#94D82D' : '#2B8A3E'; };
  var verdict = function (p) { var k = Object.keys(C.verdict).map(Number).filter(function (x) { return p >= x; }); return C.verdict[Math.max.apply(0, k)]; };
  var lon180 = function (l) { return l > 180 ? l - 360 : l; };
  var dist = function (a, b, c, d) { var R = 6371, r = Math.PI / 180, x = Math.sin((c - a) * r / 2), y = Math.sin((d - b) * r / 2); return 2 * R * Math.asin(Math.sqrt(x * x + Math.cos(a * r) * Math.cos(c * r) * y * y)); };
  // 태양 고도(도) — NOAA 간이식
  function sunAlt(date, lat, lon) {
    var r = Math.PI / 180, d = date / 86400000 + 2440587.5 - 2451545.0;
    var g = (357.529 + 0.98560028 * d) * r, q = 280.459 + 0.98564736 * d, L = (q + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) * r;
    var e = (23.439 - 0.00000036 * d) * r, ra = Math.atan2(Math.cos(e) * Math.sin(L), Math.cos(L)), dec = Math.asin(Math.sin(e) * Math.sin(L));
    var gmst = (18.697374558 + 24.06570982441908 * d) % 24, ha = ((gmst * 15 + lon) * r - ra);
    return Math.asin(Math.sin(lat * r) * Math.sin(dec) + Math.cos(lat * r) * Math.cos(dec) * Math.cos(ha)) / r;
  }
  function darkness(lat, lon) {
    var now = Date.now(), isDark = sunAlt(now, lat, lon) < -12, t1 = null, t2 = null;
    for (var m = 0; m <= 1440; m += 5) {
      var t = now + m * 60000, dk = sunAlt(t, lat, lon) < -12;
      if (dk && t1 === null) t1 = t;
      if (!dk && t1 !== null) { t2 = t; break; }
    }
    $('au-d').textContent = isDark ? T.yes : T.no;
    var f = function (t) { return new Date(t).toLocaleTimeString(LOC, { hour: '2-digit', minute: '2-digit' }); };
    $('au-dw').textContent = t1 === null ? T.noDark : T.darkFrom.replace('{t1}', f(t1)).replace('{t2}', t2 ? f(t2) : '…');
  }
  function at(lat, lon) {
    var k = Math.round(((lon % 360) + 360) % 360) + ',' + Math.round(lat);
    return cells[k] || 0;
  }
  function check() {
    if (!here || !G) return;
    var p = at(here.lat, here.lng), best = p;
    for (var dl = -5; dl <= 5; dl++) for (var dn = -12; dn <= 12; dn++) {
      var la = Math.round(here.lat) + dl, lo = Math.round(here.lng) + dn;
      if (dist(here.lat, here.lng, la, lo) <= 500) best = Math.max(best, at(la, lo));
    }
    $('au-p').textContent = p + ' %'; $('au-v').textContent = verdict(p); $('au-n').textContent = best + ' %';
    darkness(here.lat, here.lng);
  }
  function init() {
    map = L.map('au-map', { scrollWheelZoom: false, worldCopyJump: true }).setView(C.center, C.zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 12, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · NOAA SWPC' }).addTo(map);
    fetch('/geo/aurora_grid.json').then(function (r) { return r.json(); }).then(function (j) {
      G = j;
      j.g.forEach(function (c) { cells[c[0] + ',' + c[1]] = c[2]; });
      var BC = ['#2B8A3E', '#94D82D', '#F08C00', '#E03131'], BO = [.35, .5, .65, .75];
      (j.r || []).forEach(function (r) {
        L.rectangle([[r[0] - .5, r[1] - .5], [r[0] + .5, r[2] + .5]], { stroke: false, fillColor: BC[r[3]], fillOpacity: BO[r[3]], interactive: false }).addTo(map);
      });
      check();
    });
  }
  $('au-loc').addEventListener('click', function () {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(function (p) {
      here = L.latLng(p.coords.latitude, p.coords.longitude);
      L.circleMarker(here, { radius: 8, color: '#fff', weight: 3, fillColor: '#4DABF7', fillOpacity: 1 }).addTo(map);
      map.setView(here, Math.max(map.getZoom(), 4)); check();
    }, function () {}, { timeout: 10000, maximumAge: 600000 });
  });
  init();
})();
