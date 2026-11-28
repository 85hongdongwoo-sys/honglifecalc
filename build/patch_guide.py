"""계산기 페이지 아래에 그 나라 언어로 쓴 '자세한 안내' 글을 붙인다 — 배포 때 실행 (2026-11-28).
글은 build/guides/<페이지 경로>.html 에 페이지마다 따로 둔다 (예: build/guides/uk/income-tax-calculator.html).
- 위치: 관련 링크 묶음(<!--hl:related-->) 바로 앞, 없으면 </main> 앞
- 글 안의 <details class="g-q"> 질문·답은 페이지의 FAQPage 구조화 데이터에 합친다 (없으면 새로 만든다)
- /assets/hl-guide.css 를 붙인다
Usage: python3 build/patch_guide.py _site"""
import html, json, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else '_site'
GDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guides')
CSS = '<link rel="stylesheet" href="/assets/hl-guide.css?v=1" id="hl-guide-css">'
MARK = '<!--hl:guide-->'
Q = re.compile(r'<details class="g-q"><summary>(.*?)</summary><div>(.*?)</div></details>', re.S)
LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def text(s):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', s)).split())


def add_faq(page, qs):
    items = [{'@type': 'Question', 'name': text(q), 'acceptedAnswer': {'@type': 'Answer', 'text': text(a)}} for q, a in qs]
    done = False

    def rep(m):
        nonlocal done
        try:
            d = json.loads(m.group(2))
        except Exception:
            return m.group(0)
        nodes = d.get('@graph', [d]) if isinstance(d, dict) else d
        for n in nodes:
            if isinstance(n, dict) and n.get('@type') == 'FAQPage' and not done:
                have = {e.get('name') for e in n.get('mainEntity', [])}
                n.setdefault('mainEntity', []).extend(i for i in items if i['name'] not in have)
                done = True
                return m.group(1) + json.dumps(d, ensure_ascii=False) + m.group(3)
        return m.group(0)
    page = LD.sub(rep, page)
    if not done and items:
        block = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': items}, ensure_ascii=False)
        page = page.replace('</head>', '<script type="application/ld+json">' + block + '</script></head>', 1)
    return page


n = 0
for dp, dn, fn in os.walk(GDIR):
    for f in fn:
        if not f.endswith('.html'):
            continue
        rel = os.path.relpath(os.path.join(dp, f), GDIR)
        target = os.path.join(root, rel)
        if not os.path.isfile(target):
            print('no page for guide:', rel); continue
        page = open(target, encoding='utf-8').read()
        if MARK in page:
            continue
        g = open(os.path.join(dp, f), encoding='utf-8').read().strip()
        g = MARK + g
        if '<!--hl:related-->' in page:
            page = page.replace('<!--hl:related-->', g + '<!--hl:related-->', 1)
        elif '</main>' in page:
            page = page.replace('</main>', g + '</main>', 1)
        else:
            page = page.replace('<footer', g + '<footer', 1)
        if 'id="hl-guide-css"' not in page:
            page = page.replace('</head>', CSS + '</head>', 1)
        page = add_faq(page, Q.findall(g))
        open(target, 'w', encoding='utf-8').write(page); n += 1
print('guides added:', n)
