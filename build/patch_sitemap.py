"""Drops URLs listed in build/sitemap_exclude.txt from sitemap.xml and sitemap-images.xml.
Pages stay online; they are only removed from the sitemaps. Runs in the deploy workflow."""
import os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
here = os.path.dirname(os.path.abspath(__file__))
B = 'https://honglifecalc.com'
ex = {B + l.strip() for l in open(os.path.join(here, 'sitemap_exclude.txt'), encoding='utf-8')
      if l.strip() and not l.startswith('#')}
for name in ('sitemap.xml', 'sitemap-images.xml'):
    p = os.path.join(root, name)
    if not os.path.isfile(p):
        continue
    s = open(p, encoding='utf-8').read()
    blocks = re.findall(r'<url>.*?</url>', s, re.S)
    keep = [b for b in blocks if re.search(r'<loc>([^<]+)</loc>', b).group(1).strip() not in ex]
    head = s[:s.index('<url>')] if blocks else s
    out = head + '\n'.join('  ' + b.strip() for b in keep) + '\n</urlset>\n'
    open(p, 'w', encoding='utf-8').write(out)
    print(name, len(blocks), '->', len(keep))
