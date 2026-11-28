"""구조화 데이터(JSON-LD) 문법 오류 고치기 — 따옴표 없는 값(예: "inLanguage": tr-TR). 배포 때 실행."""
import json, os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '_site'
RX = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
BARE = re.compile(r'(:\s*)([A-Za-z]{2,3}-[A-Za-z]{2,4})(\s*[,}\]])')
n = 0
for d, _, fs in os.walk(root):
    for f in fs:
        if not f.endswith('.html'): continue
        p = os.path.join(d, f); s = open(p, encoding='utf-8', errors='ignore').read()
        if 'ld+json' not in s: continue
        def fix(m):
            body = m.group(2)
            try: json.loads(body); return m.group(0)
            except Exception: pass
            b2 = BARE.sub(r'\1"\2"\3', body)
            try: json.loads(b2); return m.group(1) + b2 + m.group(3)
            except Exception: return m.group(0)
        s2 = RX.sub(fix, s)
        if s2 != s: open(p, 'w', encoding='utf-8').write(s2); n += 1
print('jsonld fixed pages:', n)
