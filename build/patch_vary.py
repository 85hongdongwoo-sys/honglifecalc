"""모든 페이지에 똑같이 들어간 안내 문장을 페이지 주제에 맞게 바꾼다 — 배포 때 실행 (2026-11-28).
이유: 페이지끼리 겹치는 3단어 묶음의 대부분이 '계산 방법·결과 해석' 같은 공통 제목과 그래프 설명 문장이었다.
       주제어를 넣은 제목은 읽는 사람에게도, 검색에도 더 정확하다.
- 공통 제목(h2/h3) → 주제어가 들어간 제목 (영어·한국어는 문장을 다시 쓰고, 그 밖의 언어는 '제목 – 주제')
- 그래프 설명(figcaption) → '가로축 → 세로축' (표의 머리글에서 가져옴; 같은 페이지 안의 낱말만 씀)
- 큰 링크 버튼 묶음(hl-dlink) → <nav>로 감쌈 (메뉴 역할이므로)
Usage: python3 build/patch_vary.py _site"""
import hashlib, html, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else '_site'
MARK = '<!--hl:vary-->'
LANG = re.compile(r'<html[^>]*\blang="([a-zA-Z]+)', re.I)
H1 = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S)

EN = {
    'How it is calculated': ['How the {t} is calculated', 'The {t} formula', '{T} formula, step by step', 'How we work out the {t}'],
    'How to read the result': ['Reading your {t} result', 'What your {t} result means', 'Interpreting the {t} figure'],
    'Common mistakes': ['{T} mistakes to avoid', 'Common {t} errors', 'Where {t} estimates go wrong'],
    'Worked example': ['{T} example with numbers', 'A worked {t} example', 'Example: {t} in practice'],
    'The principle': ['Why {t} works this way', 'The idea behind the {t}', '{T}: the principle'],
    'Frequently asked questions': ['{T} FAQ', '{T}: questions people ask', 'Questions about the {t}'],
    'Your numbers': ['Enter your {t} figures', 'Your {t} inputs', '{T} inputs'],
    'Step by step': ['{T}, step by step', 'Your {t} worked through'],
    'Your inputs': ['What you entered', 'Inputs used for this {t}'],
    'How this result is calculated': ['How this {t} result was worked out', 'Behind this {t} result'],
}
KO = {
    '계산 방법': ['{t} 계산 방법', '{t}은 이렇게 계산해요', '{t} 공식 풀이'],
    '결과 해석': ['{t} 결과 읽는 법', '{t} 결과가 뜻하는 것', '내 {t} 결과 해석'],
    '흔한 실수': ['{t}에서 자주 하는 실수', '{t} 계산 시 주의할 점', '{t} 실수 줄이기'],
    '예제 풀이': ['{t} 예제로 풀어보기', '숫자로 보는 {t} 예시', '{t} 계산 예시'],
    '자주 묻는 질문': ['{t} 자주 묻는 질문', '{t} 궁금한 점', '{t} Q&A'],
    '입력한 값': ['내가 넣은 {t} 값', '{t} 입력값'],
    '단계별 계산': ['{t} 단계별 풀이', '{t} 한 단계씩 보기'],
    '계산 과정': ['이 {t} 결과가 나온 과정', '{t} 계산 과정 보기'],
}
# 그 밖의 언어: 공통 제목 끝에 주제를 붙인다 (예: 'So wird gerechnet – Brutto-Netto-Rechner')
OTHER = set('''Veelgestelde vragen|Veelgemaakte fouten|Zo wordt het berekend|Zo lees je het resultaat|Het principe|Uitgewerkt voorbeeld|Stap voor stap
Najczęściej zadawane pytania|Częste błędy|Przykład obliczeń|Zasada działania|Jak to się oblicza|Jak interpretować wynik|Krok po kroku
常見問題|常见问题|計算方式|计算方法|計算範例|計算示例|计算示例|常見錯誤|常见错误|如何解讀結果|如何解读结果|逐步計算|分步计算
よくある質問|計算方法|よくある間違い|結果の読み方|計算手順
Preguntas frecuentes|Cómo se calcula|Errores frecuentes|Ejemplo resuelto|El principio|Cómo interpretar el resultado|Paso a paso
Häufig gestellte Fragen|Häufige Fragen|Häufige Fehler|So wird gerechnet|So lesen Sie das Ergebnis|Rechenbeispiel|Das Prinzip|Schritt für Schritt
Perguntas frequentes|Erros comuns|Exemplo resolvido|Como é calculado|O princípio|Como interpretar o resultado|Passo a passo
Questions fréquentes|Erreurs fréquentes|Le principe|Exemple détaillé|Méthode de calcul|Comment lire le résultat|Étape par étape
Domande frequenti|Errori comuni|Come si calcola|Il principio|Esempio svolto|Come leggere il risultato|Passo dopo passo
Pertanyaan yang sering diajukan|Kesalahan umum|Cara menghitungnya|Contoh perhitungan|Prinsipnya|Cara membaca hasil|Langkah demi langkah
अक्सर पूछे जाने वाले प्रश्न|आम गलतियाँ|सिद्धांत|हल किया गया उदाहरण|गणना कैसे होती है|परिणाम को कैसे समझें|चरण-दर-चरण
Часто задаваемые вопросы|Типичные ошибки|Пример расчёта|Принцип|Как читать результат|Как выполняется расчёт|Пошагово
الأسئلة الشائعة|طريقة الحساب|أخطاء شائعة|المبدأ|مثال محلول|كيف تقرأ النتيجة|خطوة بخطوة
Câu hỏi thường gặp|Cách tính|Lỗi thường gặp|Cách đọc kết quả|Nguyên lý|Ví dụ minh họa|Từng bước
Vanliga frågor|Vanliga misstag|Så beräknas det|Principen|Räkneexempel|Så tolkar du resultatet|Steg för steg
Soalan lazim|Kesilapan biasa|Cara membaca keputusan|Contoh pengiraan|Cara pengiraan
Sıkça sorulan sorular|Sık yapılan hatalar|Çözümlü örnek|İlke|Nasıl hesaplanır?|Sonuç nasıl yorumlanır?|Adım adım
Ofte stilte spørsmål|Vanlige feil|Regneeksempel|Slik tolker du resultatet|Prinsippet|Slik beregnes det
Ofte stillede spørgsmål|Almindelige fejl|Sådan læser du resultatet|Princippet|Sådan beregnes det|Trin for trin'''.replace('\n', '|').split('|'))

HEAD = re.compile(r'<(h2|h3)([^>]*)>([^<]{2,60})</\1>')
CAP = re.compile(r'(<figcaption>)([^<]{40,400})(</figcaption></figure>\s*<table><tr><th>)([^<]{1,80})</th><th>([^<]{1,80})</th>')
DLINK = re.compile(r'((?:<a class="hl-dlink"[^>]*>.*?</a>\s*){2,})', re.S)


def topic(s, lang):
    m = H1.search(s)
    if not m:
        return None, None
    t = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)))
    t = re.sub(r'\s*[\(（][^)）]*[\)）]\s*', ' ', t)
    t = re.split(r'\s[–—|:]\s|:\s', t)[0].strip()
    t = re.sub(r'\b20\d\d(?:[-/–]\d{2,4})?\b', '', t).strip(' -–')
    if not t or len(t) > 70:
        return None, None
    if lang == 'en':
        T = t
        low = ' '.join(w if (w.isupper() and len(w) > 1) or re.search(r'[A-Z].*[A-Z]', w) else w.lower() for w in t.split())
        return low, T[:1].upper() + T[1:]
    if lang == 'ko':
        k = re.sub(r'\s*(계산기|계산|시뮬레이터)$', '', t).strip() or t
        return k, k
    return t, t


def pick(opts, key):
    return opts[int(hashlib.md5(key.encode()).hexdigest(), 16) % len(opts)]


def vary(s, url, lang):
    t, T = topic(s, lang)
    n = 0
    if t:
        table = EN if lang == 'en' else KO if lang == 'ko' else None
        seen = set()

        def rep(m):
            nonlocal n
            tag, attrs, txt = m.group(1), m.group(2), m.group(3)
            key = html.unescape(txt).strip()
            if key in seen:
                return m.group(0)
            if table is not None and key in table:
                new = pick(table[key], url + key).format(t=t, T=T)
            elif table is None and key in OTHER:
                new = f'{key} – {t}'
            else:
                return m.group(0)
            seen.add(key); n += 1
            return f'<{tag}{attrs}>{html.escape(new, quote=False)}</{tag}>'
        s = HEAD.sub(rep, s)

    def cap(m):
        nonlocal n
        n += 1
        x, y = m.group(4).strip(), m.group(5).strip()
        return f'{m.group(1)}{x} → {y}{m.group(3)}{m.group(4)}</th><th>{m.group(5)}</th>'
    s = CAP.sub(cap, s)

    def nav(m):
        nonlocal n
        n += 1
        return '<nav class="hl-dnav" style="display:block">' + m.group(1) + '</nav>'
    if '<nav class="hl-dnav"' not in s:
        s = DLINK.sub(nav, s, count=1)
    return s, n


pages = changed = 0
for dp, dn, fn in os.walk(root):
    rel = os.path.relpath(dp, root)
    if rel != '.' and rel.split(os.sep)[0] in ('assets', 'embed'):
        continue
    for f in fn:
        if not f.endswith('.html'):
            continue
        p = os.path.join(dp, f)
        s = open(p, encoding='utf-8').read()
        if MARK in s:
            continue
        m = LANG.search(s[:800])
        if not m:
            continue
        url = '/' + os.path.relpath(p, root).replace(os.sep, '/')
        s2, n = vary(s, url, m.group(1).lower())
        pages += 1
        if n:
            s2 = s2.replace('</body>', MARK + '</body>', 1)
            open(p, 'w', encoding='utf-8').write(s2)
            changed += 1
print('vary: pages', pages, 'changed', changed)
