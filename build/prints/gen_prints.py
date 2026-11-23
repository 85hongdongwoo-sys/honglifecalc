"""Build the /prints/ shop pages from _site/prints/data/items.json (data-prints branch).
Uses an existing English page as the shell (head, brand bar, footer). All shop pages are noindex until
checkout is connected (set LIVE = True then, and add the collection pages to the sitemap)."""
import html, json, os, re, sys
SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
LIVE = False
B = 'https://honglifecalc.com'
E = lambda s: html.escape(str(s or ''), quote=True)
D = json.load(open(os.path.join(SITE, 'prints/data/items.json'), encoding='utf-8'))
tpl = open(os.path.join(SITE, 'en/korea-severance-pay-calculator.html'), encoding='utf-8').read()
tpl = re.sub(r'(?s)<script type="application/ld\+json">.*?</script>', '', tpl)
tpl = re.sub(r'(href|src)="\.\./', r'\1="/', tpl)
tpl = re.sub(r'href="(?!/|https?:|mailto:|#)([^"]+)"', r'href="/en/\1"', tpl)
tpl = re.sub(r'<meta property="og:image[^>]*>|<meta name="twitter:image"[^>]*>|<link rel="alternate" hreflang[^>]*>', '', tpl)
tpl = re.sub(r'(?s)<!--hl:img-->.*?<!--/hl:img-->', '', tpl)
HEAD_END = tpl.index('<div class="wrap">') + len('<div class="wrap">')
FOOT_START = tpl.index('<footer>')
CSS = ('<style>.pg{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin:12px 0}'
       '.pg a{display:block;text-decoration:none;color:inherit}.pg img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:10px;background:#EEF1F5}'
       '.pg span{display:block;font-size:13px;line-height:1.35;margin-top:6px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}'
       '.pg small{color:#6e6e73;font-size:12px}.pv img{width:100%;height:auto;border-radius:12px;background:#EEF1F5}'
       '.buy{display:grid;gap:10px}.buy .opt{display:flex;justify-content:space-between;gap:12px;align-items:center;border:1px solid #E3E7EE;border-radius:12px;padding:12px 14px}'
       '.buy button{font:inherit;padding:8px 14px;border-radius:999px;border:0;background:#C9D1DC;color:#3A4659}'
       '#q{width:100%;font:inherit;padding:12px 14px;border:1px solid #C9D1DC;border-radius:12px;box-sizing:border-box}</style>')


def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-')
    return s[:60].strip('-') or 'artwork'


def page(path, title, desc, body, ld=None):
    url = B + path
    h = tpl[:HEAD_END]
    h = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', h, count=1)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h, count=1)
    for p, v in (('og:title', title), ('og:description', desc), ('og:url', url), ('og:image:alt', title)):
        h = re.sub(r'(<meta property="' + p + r'" content=")[^"]*', lambda m: m.group(1) + E(v), h, count=1)
    extra = CSS + ('' if LIVE else '<meta name="robots" content="noindex,follow">')
    if ld:
        extra += '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    h = h.replace('</head>', extra + '</head>', 1)
    h = h.replace('<a class="logo" href="./">', '<a class="logo" href="/en/">')
    out = h + body + tpl[FOOT_START:].replace('<a href="/en/./">All calculators</a>', '<a href="/prints/">Prints home</a> · <a href="/en/">Calculators</a>')
    f = os.path.join(SITE, path.lstrip('/') + ('index.html' if path.endswith('/') else ''))
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(out)


items = D['items']; colls = [c for c in D['collections'] if c['count']]
by = {c['slug']: [i for i in items if i['coll'] == c['slug']] for c in colls}
for i in items:
    i['path'] = f"/prints/{i['coll']}/{i['id']}-{slugify(i['title'])}.html"


def card(i):
    who = i['artist'] or i['culture'] or ''
    return (f'<a href="{i["path"]}"><img src="/prints/img/{i["id"]}-t.webp" alt="{E(i["title"])}" loading="lazy" width="420" height="420">'
            f'<span>{E(i["title"])}</span><small>{E(who)}{" · " if who and i["date"] else ""}{E(i["date"])}</small></a>')


PRICING = ('<h2 id="pricing">Prices</h2>'
           '<div class="buy">'
           '<div class="opt"><div><b>Print-ready file</b><br><small>High-resolution JPEG, colour-checked, cropped for A4 · A3 · A2 · 8×10 · 11×14 · 16×20 in</small></div><b>$5</b></div>'
           '<div class="opt"><div><b>Collection pack</b><br><small>Every file in one collection, one download</small></div><b>$19</b></div>'
           '<div class="opt"><div><b>Unlimited</b><br><small>Download anything in the shop while subscribed</small></div><b>$9 / month</b></div>'
           '<div class="opt"><div><b>Framed or poster print</b><br><small>Printed and shipped to your door</small></div><b>Soon</b></div>'
           '</div><p class="note">Checkout is not open yet. Prices are what we plan to charge at launch.</p>')
ABOUT = ('<h2 id="why">What you are paying for</h2><ul>'
         '<li><b>The artworks are public domain.</b> Every image here is marked public domain (CC0) by the museum that holds it, so anyone may use it freely – we always link to the museum’s own page.</li>'
         '<li><b>You pay for the work and the convenience:</b> finding the best pieces, checking the rights, colour-correcting and cropping each file to standard frame sizes, ready to print.</li>'
         '<li><b>Honest credits:</b> each artwork shows the artist, date and museum source. We never claim to own the art.</li></ul>')

# home
tiles = ''.join(f'<a href="/prints/{c["slug"]}/"><img src="/prints/img/{by[c["slug"]][0]["id"]}-t.webp" alt="{E(c["title"])}" loading="lazy" width="420" height="420"><span><b>{E(c["title"])}</b></span><small>{c["count"]} artworks</small></a>' for c in colls)
home = ('<header class="top"><h1>Public Domain <b>Art Prints</b></h1><p class="sub">Museum masterpieces – Korean and Japanese art, botanical prints, vintage maps and more – cleaned up and sized to print and frame at home.</p></header>'
        '<section class="card help"><input id="q" type="search" placeholder="Search artworks, artists, places…" aria-label="Search artworks"><div class="pg" id="res"></div>'
        '<h2 id="collections">Collections</h2><div class="pg">' + tiles + '</div>' + PRICING + ABOUT +
        f'<p class="note">Source: The Metropolitan Museum of Art Open Access (CC0). Rights flag checked {E(D["fetched"])}. {len(items)} artworks.</p></section>'
        '<script>(function(){let D=null;const q=document.getElementById("q"),r=document.getElementById("res");'
        'q.addEventListener("input",async()=>{const v=q.value.trim().toLowerCase();if(v.length<2){r.innerHTML="";return}'
        'if(!D)D=(await (await fetch("/prints/data/index.json")).json());'
        'r.innerHTML=D.filter(x=>x.s.includes(v)).slice(0,48).map(x=>`<a href="${x.p}"><img src="/prints/img/${x.i}-t.webp" alt="" loading="lazy"><span>${x.t}</span></a>`).join("")||"<p>No artworks found.</p>"})})();</script>')
page('/prints/', 'Public Domain Art Prints – Print-Ready Museum Masterpieces', 'Print-ready public domain art from museum collections: Korean and Japanese art, botanical prints, vintage maps and more, sized for standard frames.', home)
json.dump([{'i': i['id'], 'p': i['path'], 't': E(i['title']), 's': ' '.join([i['title'], i['artist'], i['culture'], i['date'], i['medium'], ' '.join(i['tags'])]).lower()} for i in items],
          open(os.path.join(SITE, 'prints/data/index.json'), 'w'), ensure_ascii=False)

for c in colls:
    L = by[c['slug']]
    body = (f'<header class="top"><h1>{E(c["title"])} <b>Prints</b></h1><p class="sub">{c["count"]} public domain artworks from The Met, ready to print and frame.</p></header>'
            f'<section class="card help"><p><a href="/prints/">← All collections</a></p><div class="pg">' + ''.join(card(i) for i in L) + '</div>' + PRICING + '</section>')
    page(f'/prints/{c["slug"]}/', f'{c["title"]} Prints – Public Domain, Print-Ready Files', f'{c["count"]} public domain {c["title"].lower()} from The Met, colour-checked and sized for standard frames.', body,
         {"@context": "https://schema.org", "@type": "CollectionPage", "name": f'{c["title"]} Prints', "url": f'{B}/prints/{c["slug"]}/'})

for c in colls:
    L = by[c['slug']]
    for k, i in enumerate(L):
        rel = [L[(k + j) % len(L)] for j in range(1, 7) if len(L) > j]
        rows = [(n, v) for n, v in (('Artist', (i['artist'] + (' (' + i['artistBio'] + ')' if i['artistBio'] else '')).strip()), ('Date', i['date']), ('Culture', i['culture']), ('Period', i['period']),
                                     ('Medium', i['medium']), ('Original size', i['dims']), ('Museum', 'The Metropolitan Museum of Art – ' + i['dept']), ('Credit', i['credit']),
                                     ('Rights', 'Public domain (CC0) – marked by the museum; checked ' + i['checked'])) if v]
        tbl = '<table>' + ''.join(f'<tr><td>{E(n)}</td><td>{E(v)}</td></tr>' for n, v in rows) + '</table>'
        who = i['artist'] or i['culture']
        body = (f'<header class="top"><h1>{E(i["title"])}</h1><p class="sub">{E(who)}{", " + E(i["date"]) if i["date"] else ""} · public domain art print</p></header>'
                f'<section class="card help"><p><a href="/prints/{c["slug"]}/">← {E(c["title"])}</a></p>'
                f'<div class="pv"><img src="/prints/img/{i["id"]}.webp" alt="{E(i["title"])} – preview" width="900"></div>'
                '<div class="buy" style="margin-top:14px"><div class="opt"><div><b>Print-ready file</b><br><small>A4 · A3 · A2 · 8×10 · 11×14 · 16×20 in</small></div><button disabled>Checkout opens soon · $5</button></div></div>'
                '<h2>About this artwork</h2>' + tbl +
                f'<p class="note">The preview is watermarked. The museum’s own record: <a href="{E(i["url"])}" rel="nofollow">metmuseum.org</a>.</p>'
                '<h2>More from this collection</h2><div class="pg">' + ''.join(card(x) for x in rel) + '</div></section>')
        page(i['path'], f'{i["title"]}{" – " + i["artist"] if i["artist"] else ""} | Art Print'[:110], f'Print-ready public domain file of “{i["title"]}”{" by " + i["artist"] if i["artist"] else ""}{", " + i["date"] if i["date"] else ""}. Sized for standard frames; museum source credited.'[:160], body,
             {"@context": "https://schema.org", "@type": "VisualArtwork", "name": i['title'], "creator": i['artist'] or None, "dateCreated": i['date'] or None,
              "artMedium": i['medium'] or None, "image": f'{B}/prints/img/{i["id"]}.webp', "license": "https://creativecommons.org/publicdomain/zero/1.0/", "url": B + i['path']})
print('prints pages:', 1 + len(colls) + len(items))
