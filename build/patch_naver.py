"""네이버용 정리 (배포 때 실행, patch_datemod 다음).
1) 한국어 페이지의 robots noindex → googlebot noindex 로 바꿈 (네이버는 수집 가능, 구글만 제외)
2) /sitemap-naver.xml : 한국어 페이지 전체 (구글용 sitemap.xml 은 그대로 둠)
3) /rss.xml : 최근 고친 한국어 페이지 100개 (네이버 서치어드바이저 RSS 제출용)
robots.txt 에는 넣지 않음 → 구글은 모르고, 네이버에만 직접 제출."""
import os, re, sys, html, datetime
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
B = 'https://honglifecalc.com'
ko = os.path.join(root, 'ko')
GB = '<meta name="googlebot" content="noindex, follow">'
today = datetime.date.today().isoformat()
pages, fixed = [], 0
for d, _, fs in os.walk(ko):
    for fn in fs:
        if not fn.endswith('.html'):
            continue
        f = os.path.join(d, fn)
        rel = '/' + os.path.relpath(f, root).replace(os.sep, '/')
        s = open(f, encoding='utf-8', errors='ignore').read()
        if 'http-equiv="refresh"' in s.lower() or '<title>' not in s:
            continue
        m = re.search(r'<meta\s+name=["\']robots["\'][^>]*noindex[^>]*>', s, re.I)
        if m:
            s = s[:m.start()] + ('' if 'name="googlebot"' in s else GB) + s[m.end():]
            open(f, 'w', encoding='utf-8').write(s); fixed += 1
        url = B + (rel[:-10] if rel.endswith('/index.html') else rel)
        c = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', s, re.I)
        if c and c.group(1).rstrip('/') != url.rstrip('/'):
            continue
        t = re.search(r'<title>([^<]*)</title>', s)
        ds = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)', s, re.I)
        dm = re.search(r'"dateModified"\s*:\s*"(\d{4}-\d\d-\d\d)', s)
        pages.append((dm.group(1) if dm else today, url, html.unescape(t.group(1)).strip() if t else url,
                      html.unescape(ds.group(1)).strip() if ds else ''))
pages.sort(key=lambda p: (p[0], p[1]), reverse=True)
esc = lambda x: html.escape(x, quote=True)
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += [f'  <url><loc>{esc(u)}</loc><lastmod>{d}</lastmod></url>' for d, u, _, _ in pages]
sm.append('</urlset>\n')
open(os.path.join(root, 'sitemap-naver.xml'), 'w', encoding='utf-8').write('\n'.join(sm))
def rfc(d):
    return datetime.datetime.strptime(d, '%Y-%m-%d').strftime('%a, %d %b %Y 09:00:00 +0900')
rs = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>',
      '<title>홍라이프 계산기</title>', f'<link>{B}/ko/</link>',
      '<description>생활·돈·건강·공무원·학교 계산기와 쉬운 설명</description>', '<language>ko</language>',
      f'<lastBuildDate>{rfc(today)}</lastBuildDate>']
for d, u, t, ds in pages[:100]:
    rs.append(f'<item><title>{esc(t)}</title><link>{esc(u)}</link><guid>{esc(u)}</guid>'
              f'<description>{esc(ds)}</description><pubDate>{rfc(d)}</pubDate></item>')
rs.append('</channel></rss>\n')
open(os.path.join(root, 'rss.xml'), 'w', encoding='utf-8').write('\n'.join(rs))
print('naver: robots->googlebot', fixed, '| sitemap-naver', len(pages), '| rss', min(100, len(pages)))
