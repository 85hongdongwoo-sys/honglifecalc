"""Shared builder for live-camera calculator pages (2026-11-24).
Takes an existing page of the same country as the template (header, brand, footer, ads stay the same) and
replaces hero, calculator, article and script. Writes overlay/<path> and registers the page in build/new_pages.json."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html  # noqa: F401
from pagekit import register

B = 'https://honglifecalc.com'

CAM_CSS = '''<style id="lc-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.lc-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.lc-row .f{min-width:0}
.lc-live{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;color:#1f7a3a;background:#EAF6EE;border:1px solid #CBE8D4;border-radius:999px;padding:2px 10px;margin:0 0 10px}
.lc-live i{width:8px;height:8px;border-radius:50%;background:#1f9d4a;animation:lcp 1.6s infinite}@keyframes lcp{50%{opacity:.3}}
.lc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin:10px 0}
.lc-cam{margin:0;background:#0f172a;border-radius:12px;overflow:hidden;position:relative;min-width:0}
.lc-cam img,.lc-cam video{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#1e293b}
.lc-cam figcaption{background:#fff;color:#1d1d1f;font-size:13px;line-height:1.35;padding:7px 9px;border:1px solid #e5e7eb;border-top:0;border-radius:0 0 12px 12px}
.lc-cam figcaption b{display:block;font-size:13.5px}
.lc-cam .lc-t{position:absolute;top:8px;left:8px;background:rgba(0,0,0,.62);color:#fff;font-size:11.5px;padding:2px 7px;border-radius:6px}
.lc-err{background:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.lc-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
.lc-h{font-size:16px;margin:18px 0 6px;color:#12305C}
.lc-sw{display:inline-flex;background:#ececf0;border-radius:9px;padding:2px;margin:4px 0 8px}
.lc-sw button{border:0;background:transparent;font:inherit;font-size:13px;padding:6px 14px;border-radius:7px;color:#3a3a3c;cursor:pointer;min-height:32px}
.lc-sw button[aria-pressed="true"]{background:#fff;color:#1d1d1f;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.lc-plot{display:flex;align-items:flex-end;gap:14px;height:210px;margin:12px 4px 8px;padding:0 6px 0;overflow-x:auto;overflow-y:hidden}.lc-pw{padding-bottom:44px;position:relative}
.lc-col{flex:1 0 56px;min-width:56px;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;position:relative}
.lc-col span{display:block;width:70%;max-width:64px;border-radius:5px 5px 0 0;background:#3B82F6}
.lc-col em{font-style:normal;font-size:11.5px;font-weight:700;color:#1d1d1f;margin-bottom:4px;white-space:nowrap}
.lc-col small{display:block;font-size:11px;color:#3a3a3c;text-align:center;line-height:1.2;height:40px;overflow:hidden;margin-top:6px;width:100%;word-break:break-word}.lc-col .lc-bar{flex:1;border-bottom:1px solid #c7c7cc;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;width:100%}
.lc-btn{display:block;width:100%;min-height:44px;border:0;border-radius:10px;background:#12305C;color:#fff;font:inherit;font-weight:600;cursor:pointer;padding:0 12px}.lc-btn:active{opacity:.85}
.lc-pick{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 2px}
.lc-pick button{border:1px solid #d1d5db;background:#fff;border-radius:999px;padding:5px 11px;font:inherit;font-size:13px;cursor:pointer;min-height:32px}
.lc-pick button[aria-pressed="true"]{background:#12305C;color:#fff;border-color:#12305C}
@media(max-width:480px){.lc-row{grid-template-columns:1fr}.lc-grid{grid-template-columns:1fr 1fr;gap:8px}.lc-cam figcaption{font-size:12px}.lc-plot{gap:8px}}
</style>'''

# shared front-end helpers: number parsing, chart/table switch, vertical bar chart
JS_HELPERS = r'''
const $=id=>document.getElementById(id);
const num=id=>{const v=parseFloat(String($(id).value).replace(/[^\d.\-]/g,''));return isFinite(v)?v:0};
let VIEW='table';
function bars(items,fmt){const top=Math.max.apply(null,items.map(x=>x[1]))||1;
  return '<div class="lc-plot">'+items.map(x=>'<div class="lc-col"><div class="lc-bar"><em>'+fmt(x[1])+'</em><span style="height:'+Math.max(1,x[1]/top*78).toFixed(1)+'%"></span></div><small>'+x[0]+'</small></div>').join('')+'</div>'}
function tbl(head,rows){return '<div class="tw" style="overflow-x:auto"><table class="tbl"><thead><tr>'+head.map(h=>'<th>'+h+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+r.map(c=>'<td>'+c+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'}
function sw(tableHtml,chartHtml,L){return '<div class="lc-sw" role="group"><button type="button" data-v="table" aria-pressed="'+(VIEW==='table')+'">'+L[0]+'</button><button type="button" data-v="chart" aria-pressed="'+(VIEW==='chart')+'">'+L[1]+'</button></div><div data-p="table"'+(VIEW==='table'?'':' hidden')+'>'+tableHtml+'</div><div data-p="chart"'+(VIEW==='chart'?'':' hidden')+'>'+chartHtml+'</div>'}
document.addEventListener('click',e=>{const b=e.target.closest('.lc-sw button');if(!b)return;VIEW=b.dataset.v;
  b.parentNode.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  const box=b.parentNode.parentNode;['table','chart'].forEach(v=>{const p=box.querySelector(':scope>[data-p="'+v+'"]');if(p)p.hidden=v!==VIEW})});
'''


def make(cc, slug, template, title, desc, h1, hero_badge, hero_p, form, js, art, faq, toc, checked, data_by, lang,
         currency, crumb_all, after, label, by='By', checked_w='Checked', data_w='Data', toc_w='On this page'):
    path = f'/{cc}/{slug}'
    url = B + path
    s = open(os.path.join(ORIG, cc, template), encoding='utf-8').read()
    old = f'{B}/{cc}/{template}'
    s = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + h1, s, count=1)
    s = s.replace(old, url)
    assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": h1, "url": url, "description": desc,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": lang,
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": currency}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": B + "/"},
              {"@type": "ListItem", "position": 2, "name": crumb_all, "item": f"{B}/{cc}/"},
              {"@type": "ListItem", "position": 3, "name": h1, "item": url}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": re.sub('<[^>]+>', '', q), "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in faq]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CAM_CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', lambda m: f'<header class="hero"><div class="in"><span class="year">{hero_badge}</span>'
               f'<h1>{h1}</h1><p>{hero_p}</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + form + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>{by} <b>Hong Life Calculators</b></span><span>{checked_w} <b>{checked}</b></span>'
           f'<span>{data_w} <b>{data_by}</b></span></div><details class="card hl-toc" open><summary>{toc_w}</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in toc) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + art + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: "<script>\n(function(){'use strict';" + JS_HELPERS + js + '\n})();\n</script>', s, count=1, flags=re.S)
    s = s.replace('<script src="/assets/hl-viz.js" defer></script>', '')
    assert 'id="how"' in s and 'id="faq"' in s and 'lc-css' in s
    out = os.path.join(OUT, path.lstrip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)
    register(ORIG, [{'url': path, 'hub': f'/{cc}/index.html', 'after': f'/{cc}/{after}', 'label': label}])
    print(out, len(s))
    return out
