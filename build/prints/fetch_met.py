"""Fetch public-domain artworks from The Met Open Access API (runs in GitHub Actions; museum hosts are
blocked in the Claude sandbox). Keeps only objects the API marks isPublicDomain=true with an image.
Writes <out>/prints/data/items.json + watermarked previews <out>/prints/img/<id>.webp and thumbs.
Usage: python3 fetch_met.py OUT [PER_COLLECTION]"""
import io, json, os, sys, time, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]; PER = int(sys.argv[2]) if len(sys.argv) > 2 else 40
API = 'https://collectionapi.metmuseum.org/public/collection/v1'
UA = {'User-Agent': 'HongLifePrints/1.0 (+https://honglifecalc.com/prints/)'}
# slug, title, search query, departmentId (0 = any)
COLL = [
    ('korean-art', 'Korean Art', 'Korea', 6),
    ('japanese-woodblock-prints', 'Japanese Woodblock Prints', 'ukiyo-e', 6),
    ('chinese-landscapes', 'Chinese Landscape Paintings', 'landscape China', 6),
    ('botanical-prints', 'Botanical Prints', 'botanical', 0),
    ('birds', 'Birds', 'bird', 9),
    ('vintage-maps', 'Vintage Maps', 'map', 9),
    ('impressionist-landscapes', 'Impressionist Landscapes', 'landscape impressionism', 11),
    ('flowers-still-life', 'Flowers & Still Life', 'flowers still life', 11),
]


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 + i * 3)


def font(sz):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def preview(raw, oid, img_dir):
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    w0, h0 = im.size
    big = im.copy(); big.thumbnail((900, 900))
    d = ImageDraw.Draw(big, 'RGBA'); f = font(max(14, big.width // 28)); t = 'honglifecalc.com/prints'
    tw = d.textlength(t, font=f)
    for k in range(-1, 3):  # diagonal repeat, light
        y = big.height * (0.2 + 0.25 * k)
        d.text(((big.width - tw) / 2, y), t, font=f, fill=(255, 255, 255, 70), stroke_width=1, stroke_fill=(0, 0, 0, 45))
    big.save(os.path.join(img_dir, f'{oid}.webp'), 'WEBP', quality=78)
    th = im.copy(); th.thumbnail((420, 420)); th.save(os.path.join(img_dir, f'{oid}-t.webp'), 'WEBP', quality=72)
    return w0, h0


def main():
    data_dir = os.path.join(OUT, 'prints', 'data'); img_dir = os.path.join(OUT, 'prints', 'img')
    os.makedirs(data_dir, exist_ok=True); os.makedirs(img_dir, exist_ok=True)
    items, colls, seen = [], [], set()
    for slug, title, q, dept in COLL:
        qs = {'q': q, 'hasImages': 'true', 'isPublicDomain': 'true'}
        if dept:
            qs['departmentId'] = dept
        ids = json.loads(get(API + '/search?' + urllib.parse.urlencode(qs))).get('objectIDs') or []
        got = []
        for oid in ids:
            if len(got) >= PER:
                break
            if oid in seen:
                continue
            try:
                o = json.loads(get(f'{API}/objects/{oid}'))
            except Exception:
                continue
            if o.get('isPublicDomain') is not True or not o.get('primaryImageSmall') or not o.get('primaryImage'):
                continue
            try:
                w0, h0 = preview(get(o['primaryImageSmall']), oid, img_dir)
            except Exception:
                continue
            seen.add(oid); got.append(oid)
            items.append({'id': oid, 'coll': slug, 'title': o.get('title') or 'Untitled',
                          'artist': o.get('artistDisplayName') or '', 'artistBio': o.get('artistDisplayBio') or '',
                          'date': o.get('objectDate') or '', 'culture': o.get('culture') or '', 'period': o.get('period') or '',
                          'medium': o.get('medium') or '', 'dims': o.get('dimensions') or '', 'dept': o.get('department') or '',
                          'credit': o.get('creditLine') or '', 'url': o.get('objectURL') or '', 'image': o['primaryImage'],
                          'tags': [t.get('term') for t in (o.get('tags') or []) if t.get('term')][:8],
                          'pw': w0, 'ph': h0, 'license': 'CC0 (Met Open Access, isPublicDomain=true)',
                          'checked': time.strftime('%Y-%m-%d')})
            time.sleep(0.05)
        colls.append({'slug': slug, 'title': title, 'count': len(got)})
        print(slug, len(got), 'of', len(ids))
    json.dump({'source': 'The Metropolitan Museum of Art Open Access API', 'fetched': time.strftime('%Y-%m-%d'),
               'collections': colls, 'items': items}, open(os.path.join(data_dir, 'items.json'), 'w'), ensure_ascii=False)
    print('items', len(items))


main()
