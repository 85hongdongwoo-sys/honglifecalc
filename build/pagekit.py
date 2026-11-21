"""나라 폴더의 기존 계산기 페이지를 틀로 새 페이지를 만든다 (머리·브랜드·바닥글·광고 그대로, 본문만 교체)."""
import html, json, os, re

B = 'https://honglifecalc.com'
E = lambda s: html.escape(str(s), quote=True)


def tpl_for(site, cc):
    d = os.path.join(site, cc)
    if not os.path.isdir(d):
        return None, None
    for f in sorted(os.listdir(d)):
        if f.endswith('.html') and f != 'index.html':
            h = open(os.path.join(d, f), encoding='utf-8').read()
            if '<header class="hero">' in h and '<footer>' in h:
                return f, h
    return None, None


def html_lang(h):
    m = re.search(r'<html lang="([^"]+)"', h)
    return m.group(1) if m else 'en'


def build_page(site, cc, slug, title, desc, body, ld=(), head_extra='', tail_extra='', marker='data-hlnew'):
    """body: <header class="hero">…</main> 까지. 반환: new_pages 항목 또는 None"""
    tf, h = tpl_for(site, cc)
    if not h:
        return None
    out = os.path.join(site, cc, slug)
    if os.path.exists(out) and marker not in open(out, encoding='utf-8').read():
        return None  # 같은 이름의 기존 페이지는 건드리지 않음
    url = f'{B}/{cc}/{slug}'
    h = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', h, count=1)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h, count=1)
    for p, v in (('og:title', title), ('og:description', desc), ('og:url', url), ('og:image:alt', title)):
        h = re.sub(r'<meta property="' + p + r'" content="[^"]*">', f'<meta property="{p}" content="{E(v)}">', h)
    h = re.sub(r'(?s)<script type="application/ld\+json">.*?</script>', '', h)
    h = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', h)
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    h = h.replace('</head>', f'<meta name="hl-new" {marker}>' + head_extra + lds + '</head>', 1)
    h = re.sub(r'(?s)<header class="hero">.*?(?=<footer>)', lambda m: body + '\n', h, count=1)
    i = h.index('</footer>') + len('</footer>')
    rest = re.sub(r'(?s)<script>\s*\(function\(\)\{\'use strict\';.*?</script>', '', h[i:], count=1)
    h = h[:i] + rest.replace('</body>', tail_extra + '</body>', 1)
    open(out, 'w', encoding='utf-8').write(h)
    return {'url': f'/{cc}/{slug}', 'hub': f'/{cc}/index.html', 'after': f'/{cc}/{tf}', 'label': title.split(' – ')[0].split(' | ')[0]}


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def app_ld(name, url, cat='UtilitiesApplication', extra=None):
    d = {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": url, "applicationCategory": cat,
         "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    d.update(extra or {})
    return d


def faq_html(faq):
    return '<article class="card help"><h2>FAQ</h2>' + ''.join(f'<h3>{E(q)}</h3><p>{E(a)}</p>' for q, a in faq) + '</article>'


def register(site, made):
    """build/new_pages.json 에 더해 patch_newpages.py 가 사이트맵·허브 링크를 붙이게 한다."""
    npj = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new_pages.json')
    cur = json.load(open(npj, encoding='utf-8')) if os.path.exists(npj) else []
    urls = {p['url'] for p in cur}
    cur += [p for p in made if p and p['url'] not in urls]
    json.dump(cur, open(npj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
