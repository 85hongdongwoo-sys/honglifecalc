/* 모든 페이지 색 통일 (2026-11-28): 예전 디자인의 크림·금색·풀색·갈색을 첫 화면 색(남색·보라 + 슬레이트 회색)으로 바꾼다.
   페이지마다 CSS가 달라도, 불러온 스타일시트의 색 값을 직접 바꾸므로 한 번에 맞춰진다.
   그래프(.hlv, svg), 플러스/마이너스 표시, 경고색(빨강)은 그대로 둔다. */
(function () {
  var SKIP_SEL = /\.hlv|svg|\.pos|\.neg|good|bad|\.up\b|\.down\b|gain|loss|success|danger|error|warn|fortune|hl-pro/i;
  function hsl(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, h = 0, s = 0, d = mx - mn;
    if (d) { s = l > .5 ? d / (2 - mx - mn) : d / (mx + mn);
      h = mx === r ? ((g - b) / d + (g < b ? 6 : 0)) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h *= 60; }
    return [h, s, l];
  }
  function map(r, g, b, prop) {
    var x = hsl(r, g, b), h = x[0], s = x[1], l = x[2];
    if (s < 0.08) return null;
    var warm = h >= 20 && h <= 66, green = h > 66 && h <= 170;
    if (!warm && !green) return null;
    var bg = /background/.test(prop), bd = /border|outline/.test(prop), txt = !bg && !bd;
    if (l >= 0.93) return bg ? '#F8FAFC' : bd ? '#E5E7EB' : '#FFFFFF';
    if (l >= 0.82) return bg ? '#EEF2FF' : bd ? '#E5E7EB' : (txt ? '#FFFFFF' : '#E5E7EB');
    if (l >= 0.7) return bd ? '#C7D2FE' : bg ? '#E0E7FF' : '#A5B4FC';
    if (l < 0.3) return txt ? '#0F172A' : (green ? '#312E81' : '#0F172A');
    if (s < 0.35 && warm) return txt ? '#64748B' : bd ? '#CBD5E1' : '#94A3B8';
    return txt ? (green ? '#4338CA' : '#4F46E5') : (green ? '#4F46E5' : '#6366F1');
  }
  var RX = /rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)(?:[,\s\/]+([\d.]+%?))?\s*\)|#([0-9a-f]{6}|[0-9a-f]{3})\b/gi;
  function conv(val, prop) {
    return val.replace(RX, function (m, r, g, b, a, hex) {
      if (hex) { if (hex.length === 3) hex = hex.replace(/./g, '$&$&'); r = parseInt(hex.substr(0, 2), 16); g = parseInt(hex.substr(2, 2), 16); b = parseInt(hex.substr(4, 2), 16); }
      var n = map(+r, +g, +b, prop); if (!n) return m;
      if (a !== undefined && a !== '1') { var R = parseInt(n.substr(1, 2), 16), G = parseInt(n.substr(3, 2), 16), B = parseInt(n.substr(5, 2), 16); return 'rgba(' + R + ',' + G + ',' + B + ',' + a + ')'; }
      return n;
    });
  }
  var PROPS = ['color', 'background-color', 'background', 'background-image', 'border-color', 'border-top-color', 'border-bottom-color', 'border-left-color', 'border-right-color', 'border', 'border-top', 'border-bottom', 'border-left', 'outline-color', 'box-shadow', 'text-decoration-color', 'fill', 'stroke', 'accent-color', 'caret-color'];
  function fixStyle(st, sel) {
    if (sel && SKIP_SEL.test(sel)) return;
    for (var i = 0; i < PROPS.length; i++) {
      var p = PROPS[i], v = st.getPropertyValue(p);
      if (!v || !/rgb|#/.test(v)) continue;
      if ((p === 'fill' || p === 'stroke') && !/^(\.|#|body|main)/.test(sel || '')) continue;
      var nv = conv(v, p);
      if (nv !== v) st.setProperty(p, nv, st.getPropertyPriority(p));
    }
    for (var j = 0; j < st.length; j++) { var q = st[j]; if (q.indexOf('--') === 0) { var vv = st.getPropertyValue(q); if (/rgb|#/.test(vv)) { var nn = conv(vv, /bg|soft|paper|cream|line|bd|border/i.test(q) ? (/line|bd|border/i.test(q) ? 'border' : 'background') : 'color'); if (nn !== vv) st.setProperty(q, nn); } } }
  }
  function walk(rules) {
    for (var i = 0; i < rules.length; i++) {
      var r = rules[i];
      if (r.cssRules && !r.style) { walk(r.cssRules); continue; }
      if (r.style) fixStyle(r.style, r.selectorText || '');
      if (r.cssRules) walk(r.cssRules);
    }
  }
  function run() {
    var ss = document.styleSheets;
    for (var i = 0; i < ss.length; i++) {
      var s = ss[i];
      if (s.ownerNode && s.ownerNode.id === 'hl-pro') continue;
      try { walk(s.cssRules); } catch (e) {}
    }
    var els = document.querySelectorAll('[style]');
    for (var k = 0; k < els.length; k++) {
      var el = els[k]; if (el.closest('svg,.hlv,.hlh-fortune,[data-keep-color]')) continue;
      fixStyle(el.style, '');
    }
  }
  run();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  window.addEventListener('load', run);
})();
