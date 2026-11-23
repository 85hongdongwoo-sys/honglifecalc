"""Helper used to write enriched copies of pages into overlay/ (not run at deploy)."""
import json, os, re

ORIG = os.environ.get('HL_ORIG', '/tmp/claude-0/orig')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'overlay')
TBL_CSS = ('<style>nav.tabs{flex-wrap:wrap;overflow:visible;white-space:normal}.help .tbl th,.help .tbl td{text-align:left;font-family:inherit;vertical-align:top}'
           '.help h3{margin-top:20px}.help ul{padding-left:20px}.help li{margin:4px 0}'
           '@media(max-width:640px){.help .tbl thead{display:none}.help .tbl,.help .tbl tbody,.help .tbl tr{display:block;width:100%}'
           '.help .tbl tr{border-bottom:1px solid var(--line,#E3E7EE);padding:6px 0}'
           '.help .tbl td{display:flex;justify-content:space-between;gap:12px;border:0;padding:3px 2px;text-align:right}'
           '.help .tbl td::before{content:attr(data-l);font-weight:700;color:var(--muted,#5B6B82);text-align:left;flex:0 0 44%}}</style>')


def table(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td data-l="{head[i]}">{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<div class="tw" style="overflow-x:auto"><table class="tbl"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def faq_html(faq, heading='FAQ'):
    return f'<h2 style="margin-top:22px">{heading}</h2>' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in faq)


def build(path, title, desc, article, faq, form=None, calc=None, lang_note=None):
    src = os.path.join(ORIG, path.lstrip('/') + ('index.html' if path.endswith('/') else ''))
    s = open(src, encoding='utf-8').read()
    s = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, s, count=1)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": re.sub('<[^>]+>', '', q), "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}}
        for q, a in faq]}
    ldtag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    if re.search(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage"', s):
        s = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',
                   lambda m: ldtag, s, count=1, flags=re.S)
    else:
        s = s.replace('</head>', ldtag + '</head>', 1)
    if form:
        s = re.sub(r'<form class="card" id="form".*?</form>', lambda m: form, s, count=1, flags=re.S)
    if calc:
        old = re.search(r'function calc\(\)\{.*?\n\n', s, re.S).group(0)
        s = s.replace(old, calc.rstrip('\n') + '\n\n', 1)
    sm = {}
    try:
        sm = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summaries.json'), encoding='utf-8'))
    except Exception:
        pass
    box = (f'<p class="hl-ans" style="background:#F3F8FF;border:1px solid #D6E6FD;border-radius:12px;padding:12px 14px;margin:0 0 14px;line-height:1.6">{sm[path]}</p>' if path in sm else '')
    art = '<article class="card help">' + TBL_CSS + box + article + '</article>'
    if re.search(r'<article class="card help">', s):
        s = re.sub(r'<article class="card help">.*?</article>', lambda m: art, s, count=1, flags=re.S)
    else:
        s = s.replace('</section>\n', '</section>\n' + art + '\n', 1)
    out = os.path.join(OUT, path.lstrip('/') + ('index.html' if path.endswith('/') else ''))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)
    return out


TOP_CSS = ('<style id="hl-deep-css">.hl-by{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:13px;color:#6e6e73;margin:6px 2px 12px}'
           '.hl-by b{color:#1d1d1f;font-weight:600}.hl-toc{padding:14px 18px}.hl-toc summary{font-weight:600;cursor:pointer;font-size:15px}'
           '.hl-toc ol{margin:10px 0 2px;padding-left:20px;columns:2;column-gap:28px}.hl-toc li{margin:3px 0;break-inside:avoid;font-size:14px}'
           '.hl-toc a{text-decoration:none}@media (max-width:560px){.hl-toc ol{columns:1}}</style>')


def add_top(out, by, toc, toc_title='On this page', views=None):
    """Byline + table of contents above the calculator (same markup/CSS as build/patch_deep.py),
    optional table/bar switch (/assets/hl-views.js). by = list of (label, value) pairs;
    toc = list of (id, text); views = (css selector, lang)."""
    s = open(out, encoding='utf-8').read()
    if '<!--hl:deep-->' in s:
        return out
    top = ('<!--hl:deep--><div class="hl-by">' + ''.join(f'<span>{a} <b>{b}</b></span>' for a, b in by) + '</div>'
           f'<details class="card hl-toc" open><summary>{toc_title}</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in toc) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    if 'id="hl-deep-css"' not in s:
        s = s.replace('</head>', TOP_CSS + '</head>', 1)
    if views:
        s = s.replace('</body>', f'<script src="/assets/hl-views.js?v=3" defer data-target="{views[0]}" data-lang="{views[1]}"></script></body>', 1)
    open(out, 'w', encoding='utf-8').write(s)
    return out
