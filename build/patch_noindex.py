"""Adds <meta name="robots" content="noindex, follow"> to every page listed in build/noindex_list.txt
and drops those URLs from sitemap.xml and sitemap-images.xml. Pages stay online. Runs in the deploy workflow,
after the overlay is copied. To undo for a page, delete its line from noindex_list.txt."""
import os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
here = os.path.dirname(os.path.abspath(__file__))
B = 'https://honglifecalc.com'
paths = [l.strip() for l in open(os.path.join(here, 'noindex_list.txt'), encoding='utf-8')
         if l.strip() and not l.startswith('#')]
TAG = '<meta name="robots" content="noindex, follow">'
done = missing = 0
for p in paths:
    f = os.path.join(root, p.lstrip('/'))
    if p.endswith('/'):
        f = os.path.join(f, 'index.html')
    if not os.path.isfile(f):
        missing += 1
        continue
    s = open(f, encoding='utf-8').read()
    if re.search(r'<meta\s+name=["\']robots["\'][^>]*>', s, re.I):
        s2 = re.sub(r'<meta\s+name=["\']robots["\'][^>]*>', TAG, s, count=1, flags=re.I)
    else:
        m = re.search(r'<meta\s+charset[^>]*>', s, re.I) or re.search(r'<head[^>]*>', s, re.I)
        if not m:
            missing += 1
            continue
        s2 = s[:m.end()] + TAG + s[m.end():]
    open(f, 'w', encoding='utf-8').write(s2)
    done += 1
print('noindex pages:', done, 'missing:', missing)
ex = {B + p for p in paths}
for name in ('sitemap.xml', 'sitemap-images.xml'):
    sp = os.path.join(root, name)
    if not os.path.isfile(sp):
        continue
    s = open(sp, encoding='utf-8').read()
    blocks = re.findall(r'<url>.*?</url>', s, re.S)
    keep = [b for b in blocks if re.search(r'<loc>([^<]+)</loc>', b).group(1).strip() not in ex]
    if len(keep) == len(blocks):
        continue
    head = s[:s.index('<url>')]
    open(sp, 'w', encoding='utf-8').write(head + '\n'.join('  ' + b.strip() for b in keep) + '\n</urlset>\n')
    print(name, len(blocks), '->', len(keep))
