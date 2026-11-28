"""Spreads internal links evenly: every page in the sitemap gets a 'related' block that links to
its nearest siblings in the same folder (3 before + 3 after, wrapping around), plus the folder hub.
Before this, related blocks always pointed at the first few pages of a folder, so later pages
had only ~3 internal links and Google left them in 'Discovered - not indexed'.
Runs in the deploy workflow after patch_sitemap.py (reads the trimmed sitemap)."""
import collections, html, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else '_site'
B = 'https://honglifecalc.com'
N_SIDE = 3

HEAD = {'en': 'You may also like', 'ko': '함께 보면 좋은 계산기', 'ja': 'あわせて使いたい計算ツール',
        'zh': '相关计算器', 'de': 'Das könnte Sie auch interessieren', 'fr': 'Vous aimerez aussi',
        'es': 'También te puede interesar', 'pt': 'Você também pode gostar', 'it': 'Potrebbe interessarti anche',
        'nl': 'Misschien ook interessant', 'pl': 'Może Cię też zainteresować', 'ru': 'Вам также может пригодиться',
        'tr': 'Bunlar da ilginizi çekebilir', 'id': 'Kalkulator terkait', 'ms': 'Kalkulator berkaitan',
        'vi': 'Có thể bạn quan tâm', 'hi': 'ये कैलकुलेटर भी देखें', 'ar': 'قد يهمك أيضًا',
        'sv': 'Du kanske också gillar', 'da': 'Måske også interessant', 'nb': 'Kanskje også interessant',
        'no': 'Kanskje også interessant', 'th': 'เครื่องคำนวณที่เกี่ยวข้อง'}

def path_of(url):
    p = url[len(B):] if url.startswith(B) else url
    return p or '/'

def file_of(p):
    return os.path.join(root, p.lstrip('/') + ('index.html' if p.endswith('/') else ''))

def natkey(p):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', p)]

def clip(s, n):
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= n else s[:n - 1].rstrip(' ,.;:-–|') + '…'

sm = open(os.path.join(root, 'sitemap.xml'), encoding='utf-8').read()
urls = [path_of(u.strip()) for u in re.findall(r'<loc>([^<]+)</loc>', sm)]
pages = [p for p in urls if not p.endswith('/') and p.endswith('.html') and p.count('/') >= 2
         and os.path.isfile(file_of(p))]

meta = {}
def info(p):
    if p not in meta:
        s = open(file_of(p), encoding='utf-8', errors='ignore').read(12000)
        t = re.search(r'<title>(.*?)</title>', s, re.S)
        d = re.search(r'<meta name="description" content="([^"]*)"', s)
        t = html.unescape(t.group(1)) if t else p.rsplit('/', 1)[-1]
        t = re.split(r'\s+[|–—]\s+', t)[0]
        meta[p] = (clip(t, 70), clip(html.unescape(d.group(1)), 160) if d else '')
    return meta[p]

CSS = ''
for p in pages:
    s = open(file_of(p), encoding='utf-8', errors='ignore').read()
    m = re.search(r'<style id="hl-sw-css">.*?</style>', s, re.S)
    if m:
        CSS = m.group(0)
        break

groups = collections.defaultdict(list)
for p in pages:
    groups[p.rsplit('/', 1)[0] + '/'].append(p)

changed = 0
for folder, members in groups.items():
    members.sort(key=natkey)
    n = len(members)
    hub = folder if os.path.isfile(file_of(folder)) else None
    for i, p in enumerate(members):
        picks = []
        for k in range(1, N_SIDE + 1):
            for j in ((i - k) % n, (i + k) % n):
                q = members[j]
                if q != p and q not in picks:
                    picks.append(q)
        if not picks and not hub:
            continue
        f = file_of(p)
        s = open(f, encoding='utf-8').read()
        if 'data-hl-ring' in s:
            continue
        lang = (re.search(r'<html[^>]*\blang="([^"]+)"', s[:2000]) or [None, 'en'])[1].split('-')[0].lower()
        old = re.search(r'<h2 class="hl-rel-t"[^>]*>(.*?)</h2>', s)
        head = old.group(1) if old else HEAD.get(lang, HEAD['en'])
        items = []
        if hub:
            ht = info_hub = None
            hs = open(file_of(hub), encoding='utf-8', errors='ignore').read(12000)
            m = re.search(r'<title>(.*?)</title>', hs, re.S)
            ht = clip(re.split(r'\s+[|–—]\s+', html.unescape(m.group(1)))[0], 70) if m else '⌂'
            items.append(('./', ht, ''))
        for q in sorted(picks, key=natkey):
            t, d = info(q)
            items.append((q.rsplit('/', 1)[-1], t, d))
        lis = ''.join(f'<li><a class="hl-rel-a" href="{html.escape(h)}"><b>{html.escape(t)}</b>'
                      + (f'<span>{html.escape(d)}</span>' if d else '') + '</a></li>' for h, t, d in items)
        block = (f'<!--hl:related--><nav class="hl-rel" data-hl-ring="1" aria-labelledby="hl-rel-t">'
                 f'<h2 class="hl-rel-t" id="hl-rel-t">{head}</h2><ul class="hl-rel-l">{lis}</ul></nav>')   # 2026-11-28: 링크 묶음은 nav(본문 유사도에서 빠짐)
        if '<!--hl:related-->' in s:
            a = s.index('<!--hl:related-->')
            ends = [(s.find(e, a), e) for e in ('</section>', '</nav>') if s.find(e, a) > 0]
            i, e = min(ends)
            b = i + len(e)
            s2 = s[:a] + block + s[b:]
        elif '</main>' in s:
            s2 = s.replace('</main>', '</main>' + block, 1)
        else:
            s2 = s.replace('<footer', block + '<footer', 1)
        if 'hl-sw-css' not in s2 and CSS:
            s2 = s2.replace('</head>', CSS + '</head>', 1)
        if s2 != s:
            open(f, 'w', encoding='utf-8').write(s2)
            changed += 1
print('related ring: folders', len(groups), 'pages', len(pages), 'changed', changed)
