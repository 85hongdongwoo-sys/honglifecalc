"""build/new_pages.json 의 새 페이지를 sitemap.xml 에 넣고, 나라 허브(index.html)의 지정 링크 뒤에 링크를 붙인다. 배포 때 실행."""
import json, os, re, sys, time
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
B = 'https://honglifecalc.com'
pages = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new_pages.json'), encoding='utf-8'))
sm = os.path.join(root, 'sitemap.xml'); s = open(sm, encoding='utf-8').read(); add = 0
for p in pages:
    if not os.path.isfile(os.path.join(root, p['url'].lstrip('/'))):
        continue
    if f'<loc>{B}{p["url"]}</loc>' not in s:
        s = s.replace('</urlset>', f'  <url><loc>{B}{p["url"]}</loc><lastmod>{time.strftime("%Y-%m-%d")}</lastmod></url>\n</urlset>', 1); add += 1
    hp = os.path.join(root, p['hub'].lstrip('/'))
    if os.path.isfile(hp):
        h = open(hp, encoding='utf-8').read()
        if f'href="{p["url"]}"' not in h:
            m = re.search(r'href="' + re.escape(p['after']) + r'"[^>]*>[^<]*</a></li>', h)
            if m:
                h = h[:m.end()] + f'<li><a href="{p["url"]}">{p["label"]}</a></li>' + h[m.end():]
                open(hp, 'w', encoding='utf-8').write(h)
open(sm, 'w', encoding='utf-8').write(s)
print('new pages in sitemap:', add)
