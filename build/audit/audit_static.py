"""배포된 사이트 전체 정적 검수. 사용: python3 audit_static.py _site out_dir"""
import os, re, sys, json, html, collections, urllib.parse
root, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
B = 'https://honglifecalc.com'
sm = set()
try:
    sm = {u[len(B):] for u in re.findall(r'<loc>([^<]+)</loc>', open(os.path.join(root, 'sitemap.xml'), encoding='utf-8').read())}
except Exception:
    pass
files = []
for d, ds, fs in os.walk(root):
    rel = os.path.relpath(d, root)
    if rel.split(os.sep)[0] in ('assets', '.git'):
        continue
    for f in fs:
        if f.endswith('.html'):
            files.append(os.path.join(d, f))
exists = set('/' + os.path.relpath(f, root).replace(os.sep, '/') for f in files)
def target_ok(p):
    p = urllib.parse.unquote(p.split('#')[0].split('?')[0])
    if p in exists: return True
    if p.endswith('/') and (p + 'index.html') in exists: return True
    if (p + '.html') in exists or (p + '/index.html') in exists: return True
    return os.path.exists(os.path.join(root, p.lstrip('/')))
BAD = re.compile(r'(?<![\w(])NaN(?![\w,)])|\[object Object\]|\{\{|\}\}|\bTODO\b|lorem ipsum')
HANGUL = re.compile(r'[가-힣]')
issues = collections.defaultdict(list)
titles = collections.defaultdict(list)
broken = collections.Counter()
stats = collections.Counter()
for f in files:
    p = '/' + os.path.relpath(f, root).replace(os.sep, '/')
    if p.endswith('/404.html') or '/widget/' in p or p.startswith('/embed/'):
        continue
    s = open(f, encoding='utf-8', errors='ignore').read()
    if 'http-equiv="refresh"' in s.lower():
        continue
    stats['pages'] += 1
    lang = (re.search(r'<html[^>]*\blang="([^"]+)"', s[:3000]) or [None, '?'])[1].lower()
    noidx = bool(re.search(r'<meta\s+name="(robots|googlebot)"[^>]*noindex', s, re.I))
    indexable = (p in sm or p.replace('index.html', '') in sm) and not noidx
    if indexable: stats['indexable'] += 1
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    title = html.unescape(t.group(1)).strip() if t else ''
    if not title: issues['no_title'].append(p)
    elif len(title) > 70 and lang not in ('ko', 'ja', 'zh', 'zh-tw', 'th'): issues['title_long'].append(p)
    if indexable and title: titles[title].append(p)
    if not re.search(r'<meta\s+name="description"\s+content="[^"]{20,}', s): issues['no_desc'].append(p)
    h1 = len(re.findall(r'<h1[\s>]', s))
    if h1 != 1: issues['h1_%d' % min(h1, 2)].append(p)
    body = re.sub(r'<script.*?</script>|<style.*?</style>|<template.*?</template>|<!--.*?-->', ' ', s, flags=re.S | re.I)
    text = html.unescape(re.sub(r'<[^>]+>', ' ', body))
    text = re.sub(r'\s+', ' ', text)
    m = BAD.search(text)
    if m: issues['bad_text'].append(p + ' :: ' + text[max(0, m.start() - 40):m.end() + 40])
    if indexable and len(text) < 1500: issues['thin_text'].append(p)
    yrs = re.findall(r'\b(20[12]\d)\b', title)
    if yrs and max(map(int, yrs)) < 2026 and not re.search(r'history|histor|過去|역대|since|desde|depuis|seit', title, re.I):
        issues['old_year_title'].append(p + ' :: ' + title)
    if not lang.startswith('ko'):
        hc = len(HANGUL.findall(text.replace('한국어', '')))
        if hc > 30: issues['hangul_on_foreign'].append(p + ' :: %d' % hc)
    for mm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(mm.group(1))
        except Exception: issues['jsonld_error'].append(p); break
    for img in re.findall(r'<img\b[^>]*>', s):
        if 'alt=' not in img: issues['img_no_alt'].append(p); break
    nb = 0
    for href in re.findall(r'<a\b[^>]*href="([^"]+)"', body):
        if href.startswith(('mailto:', 'tel:', 'javascript:', '#', 'data:')): continue
        if href.startswith('http'):
            if not href.startswith(B): continue
            tgt = href[len(B):] or '/'
        elif href.startswith('/'): tgt = href
        else: tgt = urllib.parse.urljoin(p, href)
        if not target_ok(tgt):
            nb += 1; broken[urllib.parse.urlsplit(tgt).path] += 1
    if nb: issues['broken_links'].append(p + ' :: %d' % nb)
    can = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', s)
    if indexable and not can: issues['no_canonical'].append(p)
dups = {k: v for k, v in titles.items() if len(v) > 1}
summary = {'stats': stats, 'counts': {k: len(v) for k, v in issues.items()}, 'dup_titles': len(dups),
           'dup_title_pages': sum(len(v) for v in dups.values()), 'broken_targets_top': broken.most_common(60)}
json.dump(summary, open(os.path.join(out, 'static_summary.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({k: v for k, v in issues.items()}, open(os.path.join(out, 'static_issues.json'), 'w'), ensure_ascii=False)
json.dump(sorted(dups.items(), key=lambda x: -len(x[1]))[:400], open(os.path.join(out, 'dup_titles.json'), 'w'), ensure_ascii=False)
print(json.dumps(summary, ensure_ascii=False, indent=1)[:4000])
