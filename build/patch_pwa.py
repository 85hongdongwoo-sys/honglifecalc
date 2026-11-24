#!/usr/bin/env python3
"""Per-calculator apps (PWA): every calculator page (sitemap and the rest) gets its own web app manifest, so
'Install app / Add to Home Screen' on a calculator opens THAT calculator (not the site home).
Icons and colours come from the site manifest the page used (/manifest.webmanifest or the Korean one).
Run at deploy after patch_sitemap.py:  python3 build/patch_pwa.py _site"""
import html, json, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else '_site'
SITE = 'https://honglifecalc.com'
BASES = {'/manifest.webmanifest': None, '/ko/manifest.webmanifest': None}
for b in BASES:
    try:
        BASES[b] = json.load(open(os.path.join(root, b.lstrip('/')), encoding='utf-8'))
    except Exception:
        pass
HOME = {'/manifest.webmanifest': ('Hong Life Calculators', '/?source=pwa'),
        '/ko/manifest.webmanifest': ('홍라이프 계산기', '/ko/?source=pwa')}


def fpath(p):
    return os.path.join(root, p.lstrip('/') + ('index.html' if p.endswith('/') else ''))


def wlen(s):
    # rough on-screen width: CJK/Hangul count double
    return sum(2 if ord(c) > 0x2E80 else 1 for c in s)


def short_of(title, fallback):
    t = re.split(r'\s*\|\s*', title)[0]
    t = re.split(r'\s+[—–-]\s+|\s*[(（]|\s*[:：]\s*|\s*[?？]', t)[0].strip()
    t = re.sub(r'\s+(Calculator|Calculadora|Rechner|Kalkulator|Calculateur|Calcolatore|Kalkylator|Beregner|Lommeregner)$', '', t, flags=re.I) or t
    if wlen(t) <= 24:
        return t or fallback
    out = ''
    for w in t.split(' '):
        nxt = (out + ' ' + w).strip()
        if wlen(nxt) > 24:
            break
        out = nxt
    if len(out) >= 3:
        return out.rstrip(' ·/,')
    o2 = ''
    for c in t:
        if wlen(o2 + c) > 24:
            break
        o2 += c
    return o2.rstrip(' ·/,') or fallback


def clip(s, n):
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= n else s[:n].rstrip(' ·,(-–—:')


# every page that links a site manifest (sitemap pages first, then the rest), not only the sitemap
sm = open(os.path.join(root, 'sitemap.xml'), encoding='utf-8').read()
paths = [u[len(SITE):] or '/' for u in re.findall(r'<loc>(https://honglifecalc\.com[^<]*)</loc>', sm)]
_have = set(paths)
for d, _, fs in os.walk(root):
    rel = os.path.relpath(d, root).replace(os.sep, '/')
    if rel.split('/')[0] in ('app', 'assets', 'ev', 'geo'):
        continue
    for fn in fs:
        if not fn.endswith('.html') or fn in ('404.html',):
            continue
        p = '/' + ('' if rel == '.' else rel + '/') + ('' if fn == 'index.html' else fn)
        if p not in _have:
            _have.add(p); paths.append(p)
outdir = os.path.join(root, 'app', 'm')
os.makedirs(outdir, exist_ok=True)
n = skip = 0
seen = set()
for p in paths:
    if p in ('/', '/ko/'):
        continue
    f = fpath(p)
    if not os.path.isfile(f):
        skip += 1
        continue
    s = open(f, encoding='utf-8').read()
    m = re.search(r'<link rel="manifest" href="(/manifest\.webmanifest|/ko/manifest\.webmanifest)">', s)
    if not m or not BASES.get(m.group(1)):
        skip += 1
        continue
    base = BASES[m.group(1)]
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    title = html.unescape(t.group(1)).strip() if t else p
    lang = (re.search(r'<html[^>]*\blang="([^"]+)"', s) or [None, base.get('lang', 'en')])[1]
    rtl = bool(re.search(r'<html[^>]*\bdir="rtl"', s))
    name = clip(re.split(r'\s*\|\s*', title)[0], 45)
    short = short_of(title, base.get('short_name', 'Hong Life'))
    hn, hu = HOME[m.group(1)]
    key = re.sub(r'[^a-z0-9]+', '-', p.lower().replace('.html', '')).strip('-') or 'home'
    if p.endswith('/'):
        key += '-index'
    while key in seen:
        key += '-x'
    seen.add(key)
    man = {"id": p, "name": name, "short_name": short, "description": clip(f"{hn} — {name}", 120),
           "lang": lang, "dir": "rtl" if rtl else "ltr", "start_url": p + "?source=pwa", "scope": "/",
           "display": "standalone", "theme_color": base.get("theme_color", "#244419"),
           "background_color": base.get("background_color", "#2F5520"), "icons": base.get("icons", []),
           "shortcuts": [{"name": hn, "short_name": base.get('short_name', 'Home'), "url": hu,
                          "icons": [base["icons"][0]] if base.get("icons") else []}]}
    json.dump(man, open(os.path.join(outdir, key + '.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    s = s.replace(m.group(0), f'<link rel="manifest" href="/app/m/{key}.webmanifest">', 1)
    s = re.sub(r'<link rel="manifest" href="/(ko/)?manifest\.webmanifest">\s*', '', s)  # some pages carry a duplicate link
    s = re.sub(r'<meta name="apple-mobile-web-app-title" content="[^"]*">',
               lambda _: f'<meta name="apple-mobile-web-app-title" content="{html.escape(short)}">', s, count=1)
    open(f, 'w', encoding='utf-8').write(s)
    n += 1
print('pwa: per-calculator manifests', n, '· skipped', skip)
