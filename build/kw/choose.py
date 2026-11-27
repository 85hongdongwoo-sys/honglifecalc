"""자동완성 결과(kw.json) → (1) 다시 올릴 페이지 목록(release.json) (2) 바꿀 제목(titles.json).
- 다시 올리는 조건: 유사도 20% 미만(targets.txt) + 그 주제가 실제로 검색됨(자동완성에 페이지 주제어가 나옴) + 그 검색어의 핵심 단어가 본문에 있음.
- 제목: 실제 검색어를 맨 앞에 두고, 원래 제목 뒷부분(연도·세율·금액 같은 구체 정보)은 살린다. 원래 앞부분에 이미 검색어가 다 있으면 그대로 둔다.
Usage: python3 build/kw/choose.py kw.json pagetext.json build/kw"""
import json, os, re, sys, html

kw = json.load(open(sys.argv[1], encoding='utf-8'))
txt = json.load(open(sys.argv[2], encoding='utf-8'))
outdir = sys.argv[3]
STOP = set('a an the of in to for and or is how what much my your vs per on at by with does do can i from it be are de la el en y o para con por du le les des et à pour der die das und für mit von il di e per con'.split())
LATIN = re.compile(r'^[\x00-\x7fÀ-ɏ\s$€£%’\'-]+$')
SMALL = set('a an the of in to for and or vs per on at by with from de la el en y del a al du le les des et à pour und für mit von il di e'.split())
UP = set('uk us uae usa eu vat gst hst cpp ei ira hsa fha pmi emi sip fd rd ppf epf tds gpa bmi bmr tdee rpm rcf mbti iq roi apr apy ltv dti cagr npv irr pcp hp mohre ato cra hmrc irs ssa fbt kwh mpg ssi ssdi smic iva irpf ww aow nhs paye ni sdlt lbtt ltt cgt hecs help super ndis tfsa rrsp resp fhsa oas gis qpp nps gratuity'.split()) - {'gratuity'}


def words(s):
    return [w.rstrip('%') for w in re.findall(r'[\w$%€£]+', s.lower()) if w not in STOP]


def covered(phrase, body):
    ws = words(phrase)
    return bool(ws) and all(w in body for w in ws)


def tcase(s):
    if not LATIN.match(s):
        return s
    out = []
    for i, w in enumerate(s.split()):
        lw = w.lower()
        if lw in UP:
            out.append(lw.upper())
        elif i and lw in SMALL:
            out.append(lw)
        else:
            out.append(w[:1].upper() + w[1:])
    return ' '.join(out)


def head_tail(t):
    t = html.unescape(t).strip()
    t = re.sub(r'\s*[–|]\s*(Free Calculator|حاسبات Hong Life|Hong Life.*)$', '', t)
    m = re.search(r'\s[–—|]\s|:\s', t)
    return (t[:m.start()], t[m.end():]) if m else (t, '')


release, titles = [], {}
for u, v in kw.items():
    t = txt.get(u)
    if not t:
        continue
    body = t['body']
    seedw = set(words(v.get('short') or v['seed'])) or set(words(v['seed']))
    cands = []
    for s in (v.get('sugg') or []) + (v.get('sugg_short') or []):
        s = ' '.join(s.split())
        ws = set(words(s))
        # 페이지 주제어 대부분을 담고, 본문이 다루는 검색어만
        if s and s not in cands and len(ws & seedw) >= max(1, round(len(seedw) * 0.6)) and covered(s, body) and len(s) <= 60:
            cands.append(s)
    if not cands:
        continue  # 검색되는 주제가 아님 → 대기실에 남김
    def score(s):
        ws = set(words(s))
        sc = len(ws & seedw) * 3 - abs(len(ws) - len(seedw))
        if re.search(r'calculat|rechner|calcul|kalkul|計算|计算|حاسبة|hesap|simulador|simulateur', s): sc += 2
        if re.search(r'\b202[67]\b', s): sc += 1
        return sc
    cands.sort(key=score, reverse=True)
    prim = cands[0]
    release.append(u)
    head, tail = head_tail(t['title'])
    hw = set(words(head))
    if set(words(prim)) <= hw:
        continue  # 이미 검색어가 제목 앞에 있음
    CW = r'calculat|converter|rechner|calcul|kalkul|simulador|simulateur|計算|计算|حاسبة|hesap|chart'
    if re.search(CW, head, re.I) and not re.search(CW, prim, re.I):
        continue  # 계산기·변환기라는 말이 빠지면 바꾸지 않음
    if len(words(prim)) < len(hw) - 2:
        continue  # 원래보다 너무 짧아지면 바꾸지 않음
    if re.match(r'(how to|cách|example)\b', prim, re.I) or re.search(r'\b(example|vs)\b', prim, re.I):
        continue
    prim = ' '.join(re.sub(r'\b20\d\d(?:[-/–]\d{2,4})?\b', '', prim).split())   # 연도는 원래 제목의 것만 씀
    new = tcase(prim)
    keep = {w.lower(): w for w in re.findall(r'[\w%€£$]+', head)}   # 원래 제목의 대소문자(VO2, NAT, eFG 등) 유지
    new = ' '.join(keep.get(w.lower(), w) for w in new.split())
    yr = re.search(r'\b(20\d\d(?:[-/–]\d{2})?)\b', head)
    if yr and not re.search(r'\b20\d\d', new):
        new += ' ' + yr.group(1)
    tail = re.sub(r'^(Free (Online )?(Calculator|Converter))$', '', tail.strip())
    if tail:
        room = 72 - len(new) - 3
        tl = tail if len(tail) <= room else (tail[:room].rsplit(' ', 1)[0].rstrip(',;:–-') if room > 12 else '')
        if tl:
            new += ' – ' + tl
    lw = [w.lower() for w in re.findall(r'\w+', new)]
    if any(lw.count(w) > 1 and len(w) > 3 for w in set(lw)):
        continue  # 같은 말 반복
    titles[u] = {'title': new, 'primary': prim, 'old': t['title']}
json.dump(sorted(release), open(os.path.join(outdir, 'release.json'), 'w'), ensure_ascii=False, indent=0)
json.dump(titles, open(os.path.join(outdir, 'titles.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('searched-topic pages (release):', len(release), '| titles changed:', len(titles), '| of', len(kw))
