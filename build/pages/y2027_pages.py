"""2027 — 나라별 '무엇이 바뀌나' 페이지 (최저임금·세금·공무원 보수), 그 나라 말로, 페이지마다 다른 디자인.
모든 숫자는 공식 발표(또는 공식 발표를 옮긴 보도)를 2026-11-27에 확인한 값. 정해지지 않은 건 '미정'으로 적는다.
Writes overlay/{us,jp,de,uk,fr,es,au,br}/... ; shell = 같은 나라의 기존 계산기 페이지."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, table

CHECK = '2026-11-27'


def build(c):
    s = open(os.path.join(ORIG, c['shell']), encoding='utf-8').read()
    url = 'https://honglifecalc.com' + c['path']
    old = 'https://honglifecalc.com/' + c['shell']
    T, D, H1 = c['title'], c['desc'], c['h1']
    s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{T}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{D}">', s, count=1)
    for p, v in (('og:title', T), ('og:description', D), ('og:image:alt', H1)):
        s = re.sub(r'(<meta property="%s" content=")[^"]*' % p, lambda m: m.group(1) + v, s, count=1)
    s = s.replace(old, url)
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    faq = c['faq']
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": H1, "url": url, "description": D, "inLanguage": c['lang'], "dateModified": CHECK},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": c['crumb'], "item": "https://honglifecalc.com/" + c['path'].split('/')[1] + '/'},
              {"@type": "ListItem", "position": 3, "name": H1, "item": url}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in faq]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld) + c['css'] + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', lambda m: f'<header class="hero"><div class="in"><span class="year">{c["badge"]}</span><h1>{H1}</h1><p>{c["sub"]}</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: c['app'], s, count=1, flags=re.S)
    art = (f'<h2 id="faq">{c["faq_h"]}</h2>' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in faq) + c['extra']
           + f'<h3>{c["src_h"]}</h3><ul>' + ''.join(f'<li><a href="{u}" rel="nofollow noopener" target="_blank">{n}</a></li>' for n, u in c['src']) + '</ul>'
           + f'<p class="note">{c["note"]}</p>')
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + art + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: c['js'], s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert c['must'] in s and 'id="faq"' in s, c['path']
    out = os.path.join(OUT, c['path'].lstrip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


BASE = 'section.app.y7{display:block!important;grid-template-columns:none!important;min-width:0;max-width:100%}.y7 *{box-sizing:border-box}.y7 .ans{font-size:17px;line-height:1.65;margin:4px 2px 14px}'
PAGES = []

# ───────────────────────── 🇺🇸 US — notice board + state ticker ─────────────────────────
US_STATES = [('Colorado', 15.16, 15.71), ('Connecticut', 16.94, 17.48), ('Michigan', 13.73, 15.00), ('Rhode Island', 16.00, 17.00), ('Virginia', 12.77, 13.75)]
us_rows = ''.join(f'<li><span class="st">{n}</span><span class="was">${a:.2f}</span><b>${b:.2f}</b><i style="--w:{(b - 7.25) / (17.48 - 7.25) * 100:.0f}%"></i></li>' for n, a, b in US_STATES)
PAGES.append(dict(
    path='/us/2027-pay-changes.html', shell='us/bonus-tax-calculator.html', lang='en-US', crumb='United States',
    title='Minimum Wage 2027 by State & 2027 Federal Pay Raise (GS Freeze)', h1='2027 Pay Changes: Minimum Wage & Federal Raise',
    desc='Minimum wage 2027: Colorado $15.71, Connecticut $17.48, Michigan $15.00, Rhode Island $17.00, Virginia $13.75 from Jan 1, 2027. Federal GS pay: 0% proposed for 2027, 3.8% for many law enforcement. Federal minimum still $7.25.',
    badge='🇺🇸 Checked Nov 27, 2026', sub='What changes on January 1, 2027 — and what is still undecided.', must='id="usSel"',
    css='<style id="y7-css">' + BASE + '''
.us-wrap{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:16px}
.us-board{background-color:#0B1F3A;color:#fff;border-radius:14px;padding:16px;min-width:0}.us-board h2{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#93C5FD;margin:0 0 10px}
.us-board ul{list-style:none;margin:0;padding:0}.us-board li{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:4px 10px;align-items:baseline;padding:8px 0;border-top:1px solid rgba(255,255,255,.14);position:relative}
.us-board .st{font-weight:700}.us-board .was{font-size:13px;color:#94A3B8;text-decoration:line-through}.us-board b{font-size:20px;color:#FDE68A;font-variant-numeric:tabular-nums}
.us-board i{grid-column:1/-1;height:4px;border-radius:4px;background-color:rgba(255,255,255,.12);position:relative;overflow:hidden}.us-board i:after{content:"";position:absolute;left:0;top:0;bottom:0;width:var(--w);background-color:#F59E0B}
.us-fed{border:2px dashed #0B1F3A;border-radius:14px;padding:14px;background-color:#FFFBEB;min-width:0}.us-fed h2{font-size:18px;margin:0 0 8px}
.us-fed .pct{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:8px 0}.us-fed .pct div{background-color:#fff;border:1px solid #FDE68A;border-radius:10px;padding:8px;text-align:center}
.us-fed .pct b{display:block;font-size:22px}.us-fed .pct small{font-size:11.5px;color:#6B7280;line-height:1.3;display:block}
.us-calc{margin-top:16px;background-color:#fff;border:1px solid #E5E7EB;border-radius:14px;padding:14px}.us-calc h2{font-size:18px;margin:0 0 8px}
.us-calc label{display:block;font-weight:700;font-size:13px;margin-top:8px}.us-calc select,.us-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:10px;border:1px solid #D1D5DB;border-radius:10px;margin-top:4px;background-color:#fff}
.us-out{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:12px}.us-out div{background-color:#F3F4F6;border-radius:10px;padding:10px;min-width:0}.us-out div.n{background-color:#0B1F3A;color:#fff}
.us-out small{display:block;font-size:12px;opacity:.75}.us-out b{display:block;font-size:19px;overflow-wrap:anywhere}
@media(max-width:760px){.us-wrap{grid-template-columns:minmax(0,1fr)}}@media(max-width:460px){.us-out{grid-template-columns:1fr}.us-fed .pct{grid-template-columns:1fr}}
</style>''',
    app=f'''<section class="app y7" id="calc"><p class="ans">On <b>January 1, 2027</b> the minimum wage rises in states such as <b>Connecticut ($17.48)</b>, <b>Rhode Island ($17.00)</b>, <b>Colorado ($15.71)</b>, <b>Michigan ($15.00)</b> and <b>Virginia ($13.75)</b>. The <b>federal minimum wage stays $7.25</b>. For federal employees, the President's August 2026 plan proposes a <b>0% raise (pay freeze) for most GS employees in 2027</b>; many law enforcement positions are slated for <b>3.8%</b>. Congress has not made a final decision.</p>
<div class="us-wrap"><div class="us-board"><h2>Jan 1, 2027 · new state minimums</h2><ul>{us_rows}</ul><p style="font-size:12px;color:#94A3B8;margin:8px 0 0">Bar = distance above the $7.25 federal floor.</p></div>
<div class="us-fed"><h2>Federal pay 2027</h2><div class="pct"><div><b>0%</b><small>Most GS employees (proposed freeze)</small></div><div><b>3.8%</b><small>Many law enforcement jobs</small></div><div><b>6.7%</b><small>Added LE positions incl. 2026 catch-up</small></div></div>
<p style="font-size:14px;margin:6px 0 0">Final numbers usually come with an executive order in December. Some lawmakers are pushing for 3.8%–4.1% for everyone.</p></div></div>
<div class="us-calc"><h2>Your paycheck at the 2027 minimum</h2><label for="usSel">State<select id="usSel">{''.join(f'<option value="{a},{b}">{n}</option>' for n, a, b in US_STATES)}<option value="7.25,7.25">Federal ($7.25)</option></select></label>
<label for="usH">Hours per week<input id="usH" inputmode="decimal" value="40"></label>
<div class="us-out"><div><small>2026 per year</small><b id="us26">–</b></div><div class="n"><small>2027 per year</small><b id="us27">–</b></div><div><small>Raise per year</small><b id="usD">–</b></div></div>
<p style="font-size:13px;color:#6B7280;margin:10px 0 0">Gross pay, 52 weeks. Federal tax on it: <a href="/us/2027-tax-brackets.html">2027 tax brackets calculator</a>.</p></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const U=x=>'$'+x.toLocaleString('en-US',{maximumFractionDigits:0});
function go(){const [a,b]=$('usSel').value.split(',').map(Number),h=N($('usH').value)*52;$('us26').textContent=U(a*h);$('us27').textContent=U(b*h);$('usD').textContent='+'+U((b-a)*h)}
$('usSel').addEventListener('change',go);$('usH').addEventListener('input',go);go()})();
</script>''',
    faq_h='Frequently asked questions', src_h='Sources (checked Nov 27, 2026)',
    faq=[('What is the federal minimum wage in 2027?', 'Still $7.25 an hour. Congress has not changed it since 2009, so states with no own minimum (or a lower one) keep $7.25.'),
         ('Which states raise the minimum wage on January 1, 2027?', 'Among them: Connecticut $17.48, Rhode Island $17.00, Colorado $15.71, Michigan $15.00 and Virginia $13.75. Other states (e.g. California, Arizona, Maine, New Jersey, Ohio, Minnesota) also adjust for 2027 — check your state labor department for the exact date.'),
         ('Will federal employees get a raise in 2027?', 'Under the President\'s alternative pay plan sent in August 2026, most civilian GS employees would get 0% in 2027. Many law enforcement personnel are slated for 3.8%, and OPM is extending a 6.7% raise (3.8% plus a 2026 catch-up) to more positions. Nothing is final until the executive order, usually signed in December.'),
         ('What are the 2027 tax brackets?', 'The IRS released them on November 5, 2026: 10% up to $12,800 (single), standard deduction $16,600 single / $33,200 married filing jointly. See the <a href="/us/2027-tax-brackets.html">2027 tax brackets calculator</a>.'),
         ('How much is $15.00 an hour per year?', '$15.00 × 40 hours × 52 weeks = $31,200 gross per year.')],
    extra='<h3 id="tbl">2026 vs 2027 state minimum wage</h3>' + table(['State', '2026', 'Jan 1, 2027', 'Change'], [[n, f'${a:.2f}', f'${b:.2f}', f'+${b - a:.2f}'] for n, a, b in US_STATES]),
    src=[('Experian Employer Services — 2027 state-by-state minimum wage changes (Oct 9, 2026)', 'https://www.experian.com/blogs/employer-services/2027-state-by-state-local-minimum-wage-changes-and-posting-updates/'),
         ('Federal News Network — Trump plans civilian federal pay freeze in 2027 (Aug 2026)', 'https://federalnewsnetwork.com/pay-benefits/2026/08/trump-officially-plans-for-civilian-federal-pay-freeze-in-2027/'),
         ('Federal News Network — Some law enforcement may see 6.7% raise (Nov 2026)', 'https://federalnewsnetwork.com/pay-benefits/2026/11/some-federal-law-enforcement-personnel-may-see-6-7-raise-next-year/'),
         ('IRS — Tax inflation adjustments for tax year 2027 (Nov 5, 2026)', 'https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts')],
    note='State rates and the federal pay decision can still change. Gross figures before tax. Not legal or tax advice.'))

# ───────────────────────── 🇯🇵 JP — 給与明細 + 判子 ─────────────────────────
PAGES.append(dict(
    path='/jp/2027-kawaru-okane.html', shell='jp/denkidai-keisan.html', lang='ja-JP', crumb='日本',
    title='2027年(令和9年)に変わるお金｜最低賃金1,176円・年収の壁178万円・公務員給与', h1='2027年に変わるお金：最低賃金・年収の壁・公務員給与',
    desc='最低賃金は全国加重平均1,176円(2026年10月頃から、+55円)。所得税の年収の壁は令和8・9年分で178万円、2027年1月から源泉徴収の税額表も改正。国家公務員の月給は2026年勧告で+3.51%、ボーナス4.70月。',
    badge='🇯🇵 2026年11月27日確認', sub='時給・手取り・公務員の給料、2027年に何が変わる？', must='id="jpH"',
    css='<style id="y7-css">' + BASE + '''
.jp-meisai{border:2px solid #1F2937;border-radius:4px;background-color:#fff;min-width:0;font-family:"Hiragino Sans","Noto Sans JP",sans-serif}
.jp-meisai .hd{display:flex;justify-content:space-between;align-items:center;gap:8px;border-bottom:2px solid #1F2937;padding:8px 12px;background-color:#F3F4F6}
.jp-meisai .hd b{font-size:16px;letter-spacing:.3em}.jp-hanko{width:52px;height:52px;border:2px solid #C2410C;border-radius:50%;color:#C2410C;display:flex;align-items:center;justify-content:center;font-size:11px;line-height:1.15;text-align:center;font-weight:800;transform:rotate(-8deg);flex:0 0 auto}
.jp-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}.jp-g div{border-right:1px solid #9CA3AF;border-bottom:1px solid #9CA3AF;padding:8px 10px;min-width:0}.jp-g div:nth-child(3n){border-right:0}
.jp-g small{display:block;font-size:11.5px;color:#4B5563}.jp-g b{display:block;font-size:20px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}.jp-g em{display:block;font-style:normal;font-size:12px;color:#C2410C}
.jp-calc{margin-top:14px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px}
.jp-box{border:1px solid #D1D5DB;border-radius:10px;padding:12px;background-color:#FAFAF9;min-width:0}.jp-box h2{font-size:16px;margin:0 0 8px;border-left:4px solid #C2410C;padding-left:8px}
.jp-box label{display:block;font-size:13px;font-weight:700;margin-top:6px}.jp-box input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px}
.jp-res{margin-top:10px;font-size:15px;line-height:1.7}.jp-res b{font-size:18px}
@media(max-width:700px){.jp-calc{grid-template-columns:minmax(0,1fr)}.jp-g{grid-template-columns:minmax(0,1fr)}.jp-g div{border-right:0}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans"><b>最低賃金</b>は2026年度の改定で全国加重平均<b>1,176円</b>(+55円)になり、<b>2026年10月頃から</b>都道府県ごとに発効しました(東京1,281円・神奈川1,280円・大阪1,232円)。所得税は令和8年分・9年分の特例で<b>年収の壁が178万円</b>に上がり、<b>2027年1月から</b>給与の源泉徴収税額表も新しくなります。<b>国家公務員</b>の月給は2026年の人事院勧告で<b>平均+3.51%</b>、ボーナスは<b>年4.70月</b>です。</p>
<div class="jp-meisai"><div class="hd"><b>2027 明細</b><span class="jp-hanko">令和<br>九年</span></div>
<div class="jp-g"><div><small>最低賃金(全国加重平均)</small><b>1,176円</b><em>+55円(4.9%)</em></div><div><small>東京都の最低賃金</small><b>1,281円</b><em>全国最高水準</em></div><div><small>年収の壁(所得税)</small><b>178万円</b><em>令和8・9年分の特例</em></div>
<div><small>基礎控除</small><b>62万円＋42万円</b><em>合計所得489万円以下</em></div><div><small>給与所得控除の最低額</small><b>69万円＋5万円</b><em>令和8・9年は74万円</em></div><div><small>国家公務員 月例給</small><b>+3.51%</b><em>平均+15,056円・ボーナス4.70月</em></div></div></div>
<div class="jp-calc"><div class="jp-box"><h2>最低賃金で月いくら？</h2><label for="jpW">時給(円)<input id="jpW" inputmode="numeric" value="1176"></label><label for="jpH">1か月の労働時間<input id="jpH" inputmode="decimal" value="160"></label><div class="jp-res" id="jpR"></div></div>
<div class="jp-box"><h2>年収の壁チェック</h2><label for="jpY">給与の年収(万円)<input id="jpY" inputmode="decimal" value="150"></label><div class="jp-res" id="jpY2"></div></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const Y=x=>Math.round(x).toLocaleString('ja-JP')+'円';
function go(){const w=N($('jpW').value),h=N($('jpH').value);$('jpR').innerHTML='月 <b>'+Y(w*h)+'</b>／年 '+Y(w*h*12)+'<br>旧全国平均1,121円との差：月 '+Y((w-1121)*h);
const y=N($('jpY').value);$('jpY2').innerHTML=y<=178?'✅ 年収<b>'+y+'万円</b>は178万円以下。令和8・9年分は所得税がかかりません(給与のみ・ほかの控除なしの目安)。':'ℹ️ 178万円を超える部分に所得税がかかります。社会保険の「106万円・130万円」は別の基準です。'}
['jpW','jpH','jpY'].forEach(i=>$(i).addEventListener('input',go));go()})();
</script>''',
    faq_h='よくある質問', src_h='出典(2026年11月27日確認)',
    faq=[('2026年度(2027年まで適用)の最低賃金はいくら？', '全国加重平均は1,176円で、前年度の1,121円から55円上がりました。各都道府県で2026年10月頃から順に発効しています。東京は1,281円です。'),
         ('年収の壁178万円とは？', '令和8年分・9年分の所得税では、基礎控除62万円に特例42万円(合計所得489万円以下)が上乗せされ、給与所得控除の最低保障額も69万円＋特例5万円になります。104万円＋74万円＝178万円まで給与だけなら所得税がかかりません。'),
         ('2027年1月から何が変わる？', '令和9年1月1日以後に支払う給与・公的年金の源泉徴収税額表(月額表など)が改正内容に合わせて変わります。'),
         ('公務員の給料は2027年に上がる？', '2026年8月7日の人事院勧告で、月例給は平均15,056円(3.51%)引上げ、ボーナスは年4.70月に。2026年4月にさかのぼって適用されます。2027年分は2027年8月ごろの勧告で決まります。'),
         ('社会保険の扶養(130万円)も178万円になる？', 'なりません。178万円は所得税の話です。社会保険の106万円・130万円の基準は別です。')],
    extra='<h3 id="tbl">数字のまとめ</h3>' + table(['項目', '以前', '新しい値', '適用'], [['最低賃金(全国加重平均)', '1,121円', '1,176円', '2026年10月頃〜'], ['基礎控除(本則)', '58万円', '62万円', '令和8年分〜'], ['給与所得控除の最低保障額', '65万円', '69万円(＋特例5万円)', '令和8年分〜'], ['国家公務員 ボーナス', '4.65月', '4.70月', '2026年度']]),
    src=[('nippon.com — 最低賃金55円引き上げ、全国平均1176円に(2026年7月30日)', 'https://www.nippon.com/ja/japan-data/h02856/'),
         ('労働政策研究・研修機構 — 2026年人事院勧告(ビジネス・レーバー・トレンド)', 'https://www.jil.go.jp/kokunai/blt/backnumber/2026/10/other_01.html'),
         ('財務省 — 令和8年度税制改正の大綱(所得税)', 'https://www.mof.go.jp/tax_policy/tax_reform/outline/fy2026/08taikou_01.htm')],
    note='税額は目安です。住民税・社会保険料は別に計算されます。最終的な税制は法令をご確認ください。'))

# ───────────────────────── 🇩🇪 DE — Bescheid mit §-Absätzen ─────────────────────────
PAGES.append(dict(
    path='/de/was-aendert-sich-2027.html', shell='de/stundenlohn-rechner.html', lang='de-DE', crumb='Deutschland',
    title='Was ändert sich 2027? Mindestlohn 14,60 €, Kindergeld 267 €, Grundfreibetrag', h1='Was ändert sich 2027 beim Geld?',
    desc='2027: Mindestlohn 14,60 € (ab 1.1.), Minijob 633 €. Geplant: Grundfreibetrag 12.564 €, Kindergeld 267 € (Regierungsentwurf, noch nicht beschlossen). Bundesbeamte: 3,0 % und 2,8 % als Abschlag, Gesetz offen.',
    badge='🇩🇪 Stand 27.11.2026', sub='Mindestlohn, Steuer, Kindergeld und Besoldung – was fest ist und was noch offen.', must='id="deK"',
    css='<style id="y7-css">' + BASE + '''
.de-doc{background-color:#fff;border:1px solid #D4D4D8;border-top:6px solid #111;min-width:0;padding:16px 16px 8px;font-family:Georgia,"Times New Roman",serif}
.de-doc h2{font-family:inherit;font-size:20px;margin:0 0 2px}.de-doc .az{font-size:12px;color:#71717A;margin:0 0 10px;font-family:system-ui,sans-serif}
.de-p{display:grid;grid-template-columns:2.4em minmax(0,1fr) auto;gap:8px;padding:10px 0;border-top:1px solid #E4E4E7;align-items:start}
.de-p .n{font-weight:700;color:#B91C1C}.de-p p{margin:0;font-size:15px;line-height:1.55}.de-p small{display:block;color:#71717A;font-size:12.5px;font-family:system-ui,sans-serif}
.de-tag{font-family:system-ui,sans-serif;font-size:11.5px;font-weight:800;border-radius:4px;padding:3px 7px;white-space:nowrap}.de-tag.ok{background-color:#DCFCE7;color:#166534}.de-tag.pl{background-color:#FEF3C7;color:#92400E}.de-tag.of{background-color:#F4F4F5;color:#52525B}
.de-calc{margin-top:14px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.de-box{border:1px solid #E4E4E7;border-radius:12px;padding:12px;min-width:0}.de-box h2{font-size:16px;margin:0 0 6px}.de-box label{display:block;font-size:13px;font-weight:700;margin-top:6px}
.de-box input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D4D4D8;border-radius:8px;margin-top:4px}.de-box .r{margin-top:8px;font-size:15px;line-height:1.6}
@media(max-width:640px){.de-calc{grid-template-columns:minmax(0,1fr)}.de-p{grid-template-columns:2em minmax(0,1fr)}.de-p .de-tag{grid-column:2}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">Sicher ist: Der <b>Mindestlohn steigt am 1. Januar 2027 auf 14,60 €</b>, die Minijob-Grenze auf <b>633 €</b>. Die <b>Einkommensteuerreform 2027</b> (Grundfreibetrag <b>12.564 €</b>, Kindergeld <b>267 €</b>) ist bisher nur ein Regierungsentwurf. <b>Bundesbeamte</b> bekommen 3,0 % (seit April 2025) und 2,8 % (seit Mai 2026) als Abschlag – das Gesetz dazu fehlt noch.</p>
<div class="de-doc"><h2>Übersicht 2027</h2><p class="az">Stand 27. November 2026 · grün = beschlossen, gelb = geplant, grau = offen</p>
<div class="de-p"><span class="n">§ 1</span><p><b>Mindestlohn 14,60 € pro Stunde</b><small>2026: 13,90 € · ab 1.1.2027 · Minijob 633 €</small></p><span class="de-tag ok">beschlossen</span></div>
<div class="de-p"><span class="n">§ 2</span><p><b>Grundfreibetrag 12.564 €</b> (2028: 12.900 €)<small>2026: 12.348 € · Tarif zwischen ca. 17.800 € und 70.600 € flacher</small></p><span class="de-tag pl">Entwurf</span></div>
<div class="de-p"><span class="n">§ 3</span><p><b>Kindergeld 267 € pro Kind und Monat</b> (2028: 272 €)<small>2026: 259 € · Kinderfreibetrag 7.128 €</small></p><span class="de-tag pl">Entwurf</span></div>
<div class="de-p"><span class="n">§ 4</span><p><b>Arbeitnehmer-Pauschbetrag 1.430 €</b><small>bisher 1.230 €</small></p><span class="de-tag pl">Entwurf</span></div>
<div class="de-p"><span class="n">§ 5</span><p><b>Bundesbeamte: +3,0 % (1.4.2025) und +2,8 % (1.5.2026)</b><small>als Abschlag gezahlt · Besoldungsgesetz noch nicht beschlossen · TVöD läuft bis 31.3.2027</small></p><span class="de-tag of">offen</span></div></div>
<div class="de-calc"><div class="de-box"><h2>Mindestlohn im Monat</h2><label for="deH">Stunden pro Woche<input id="deH" inputmode="decimal" value="40"></label><div class="r" id="deR"></div></div>
<div class="de-box"><h2>Kindergeld im Jahr</h2><label for="deK">Anzahl Kinder<input id="deK" inputmode="numeric" value="2"></label><div class="r" id="deKR"></div></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(',','.').replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const E=x=>x.toLocaleString('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2})+' €';
function go(){const m=N($('deH').value)*13/3;$('deR').innerHTML='2026: '+E(13.90*m)+'<br>2027: <b>'+E(14.60*m)+'</b> (+'+E(0.70*m)+')';
const k=Math.round(N($('deK').value));$('deKR').innerHTML='2026: '+E(259*12*k)+'<br>2027 (geplant): <b>'+E(267*12*k)+'</b> (+'+E(8*12*k)+')'}
['deH','deK'].forEach(i=>$(i).addEventListener('input',go));go()})();
</script>''',
    faq_h='Häufige Fragen', src_h='Quellen (geprüft am 27.11.2026)',
    faq=[('Wie hoch ist der Mindestlohn 2027?', '14,60 € brutto pro Stunde ab 1. Januar 2027 (2026: 13,90 €). Details im <a href="/de/mindestlohn-2027.html">Mindestlohn-2027-Rechner</a>.'),
         ('Wie hoch ist der Grundfreibetrag 2027?', 'Laut Regierungsentwurf des Einkommensteuerreformgesetzes 2027: 12.564 € (2028: 12.900 €). Der Bundestag hat den Entwurf am 8. Oktober 2026 in erster Lesung beraten; beschlossen ist er noch nicht.'),
         ('Steigt das Kindergeld 2027?', 'Geplant sind 267 € pro Kind und Monat ab Januar 2027 (2026: 259 €). Auch das steht im Regierungsentwurf und ist noch nicht beschlossen.'),
         ('Bekommen Bundesbeamte 2027 mehr Geld?', 'Bisher werden 3,0 % (rückwirkend ab 1.4.2025) und 2,8 % (ab 1.5.2026) als Abschlag gezahlt. Das Gesetz soll laut Innenministerium noch 2026 ins Kabinett; eine Erhöhung für 2027 ist nicht beschlossen. Der TVöD für Bund und Kommunen läuft bis 31. März 2027.'),
         ('Wie viel bringt der Mindestlohn 2027 bei 40 Stunden?', '14,60 € × 40 × 13 ÷ 3 = 2.530,67 € brutto im Monat.')],
    extra='<h3 id="tbl">2026 und 2027 im Vergleich</h3>' + table(['', '2026', '2027', 'Status'], [['Mindestlohn', '13,90 €', '14,60 €', 'beschlossen'], ['Minijob-Grenze', '603 €', '633 €', 'beschlossen'], ['Grundfreibetrag', '12.348 €', '12.564 €', 'Entwurf'], ['Kindergeld', '259 €', '267 €', 'Entwurf']]),
    src=[('Bundesregierung — Einkommensteuerreform 2027 (Kabinett 2.9.2026)', 'https://www.bundesregierung.de/breg-de/aktuelles/einkommensteuerreform-2027-2451192'),
         ('Deutscher Bundestag — Textarchiv Einkommensteuerreform (1. Lesung 8.10.2026)', 'https://www.bundestag.de/dokumente/textarchiv/2026/kw41-de-einkommensteuerreform-1217520'),
         ('Bundesregierung — Mindestlohn (2027: 14,60 €, Minijob 633 €)', 'https://www.bundesregierung.de/breg-de/aktuelles/mindestlohn-steigt-2391010'),
         ('öffentlicher-dienst-news.de — Besoldungsgesetz Bundesbeamte (9.11.2026)', 'https://oeffentlicher-dienst-news.de/dobrindt-will-besoldungsgesetz-fuer-bundesbeamte-noch-2026-beschliessen/')],
    note='Geplante Werte können sich im Gesetzgebungsverfahren ändern. Keine Steuer- oder Rechtsberatung.'))

# ───────────────────────── 🇬🇧 UK — tear-off ticket ─────────────────────────
UK = [('National Living Wage (21+)', 12.71, 13.21), ('18–20 rate', 10.85, 11.27), ('16–17 rate', 8.00, 8.31), ('Apprentice rate', 8.00, 8.31)]
uk_t = ''.join(f'<div class="tk"><span>{n}</span><s>£{a:.2f}</s><b>£{b:.2f}</b></div>' for n, a, b in UK)
PAGES.append(dict(
    path='/uk/minimum-wage-april-2027.html', shell='uk/company-car-tax-calculator.html', lang='en-GB', crumb='United Kingdom',
    title='National Living Wage April 2027: £13.21 an hour (all rates)', h1='Minimum Wage from April 2027: £13.21',
    desc='National Living Wage rises to £13.21 an hour from April 2027 (+3.9%). 18–20: £11.27, 16–17 and apprentices: £8.31. Income tax personal allowance stays £12,570 (frozen to April 2031). Annual pay calculator.',
    badge='🇬🇧 Checked 27 Nov 2026', sub='All four minimum wage rates for 2027/28 and what your hours add up to.', must='id="ukH"',
    css='<style id="y7-css">' + BASE + '''
.uk-ticket{display:grid;grid-template-columns:minmax(0,1fr) 150px;background-color:#FFF7ED;border:1px solid #FDBA74;border-radius:14px;overflow:hidden;min-width:0}
.uk-l{padding:14px;min-width:0}.uk-l h2{font-size:14px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 8px;color:#9A3412}
.tk{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:10px;align-items:baseline;padding:8px 0;border-top:1px dotted #FDBA74}.tk span{font-weight:600}.tk s{font-size:13px;color:#A8A29E}.tk b{font-size:20px;color:#7C2D12;font-variant-numeric:tabular-nums}
.uk-r{border-left:2px dashed #FDBA74;background-color:#7C2D12;color:#FFEDD5;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:12px;position:relative}
.uk-r:before,.uk-r:after{content:"";position:absolute;left:-11px;width:20px;height:20px;border-radius:50%;background-color:#fff}.uk-r:before{top:-10px}.uk-r:after{bottom:-10px}
.uk-r b{font-size:34px;line-height:1}.uk-r small{font-size:12px;letter-spacing:.1em}
.uk-calc{margin-top:14px;border:1px solid #E7E5E4;border-radius:14px;padding:14px}.uk-calc h2{font-size:18px;margin:0 0 8px}
.uk-calc .row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.uk-calc label{display:block;font-size:13px;font-weight:700}
.uk-calc select,.uk-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D6D3D1;border-radius:8px;margin-top:4px;background-color:#fff}
.uk-o{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:12px}.uk-o div{background-color:#F5F5F4;border-radius:10px;padding:10px;min-width:0}.uk-o div.n{background-color:#7C2D12;color:#fff}.uk-o small{display:block;font-size:12px;opacity:.8}.uk-o b{display:block;font-size:19px;overflow-wrap:anywhere}
@media(max-width:600px){.uk-ticket{grid-template-columns:minmax(0,1fr)}.uk-r{border-left:0;border-top:2px dashed #FDBA74;flex-direction:row;gap:10px}.uk-r:before,.uk-r:after{display:none}.uk-calc .row,.uk-o{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app=f'''<section class="app y7" id="calc"><p class="ans">From <b>April 2027</b> the <b>National Living Wage (21 and over) rises to £13.21 an hour</b>, up 50p or <b>3.9%</b> from £12.71. The 18–20 rate becomes <b>£11.27</b>, and the 16–17 and apprentice rates <b>£8.31</b>. The government accepted these Low Pay Commission recommendations on 28 October 2026. Income tax thresholds stay frozen: the <b>personal allowance remains £12,570</b> until April 2031.</p>
<div class="uk-ticket"><div class="uk-l"><h2>Minimum wage · April 2027</h2>{uk_t}<p style="font-size:12.5px;color:#78716C;margin:8px 0 0">Accommodation offset: £11.53 a day.</p></div><div class="uk-r"><small>NLW 21+</small><b>£13.21</b><small>+3.9%</small></div></div>
<div class="uk-calc"><h2>What it means for you</h2><div class="row"><label for="ukA">Your rate<select id="ukA">{''.join(f'<option value="{a},{b}">{n}</option>' for n, a, b in UK)}</select></label><label for="ukH">Hours per week<input id="ukH" inputmode="decimal" value="37.5"></label></div>
<div class="uk-o"><div><small>2026/27 per year</small><b id="uk26">–</b></div><div class="n"><small>2027/28 per year</small><b id="uk27">–</b></div><div><small>Increase</small><b id="ukD">–</b></div></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const P=x=>'£'+x.toLocaleString('en-GB',{maximumFractionDigits:0});
function go(){const [a,b]=$('ukA').value.split(',').map(Number),h=N($('ukH').value)*52;$('uk26').textContent=P(a*h);$('uk27').textContent=P(b*h);$('ukD').textContent='+'+P((b-a)*h)}
$('ukA').addEventListener('change',go);$('ukH').addEventListener('input',go);go()})();
</script>''',
    faq_h='Frequently asked questions', src_h='Sources (checked 27 November 2026)',
    faq=[('What is the minimum wage in April 2027?', 'The National Living Wage for workers aged 21 and over will be £13.21 an hour from April 2027.'),
         ('How much is £13.21 an hour per year?', '£13.21 × 37.5 hours × 52 weeks = £25,759.50 gross a year. At 40 hours it is £27,476.80.'),
         ('What is the minimum wage for 18 to 20 year olds in 2027?', '£11.27 an hour from April 2027 (up 42p).'),
         ('Is the personal allowance going up in April 2027?', 'No. The personal allowance stays at £12,570 and the basic rate limit at £37,700 — both frozen until 5 April 2031.'),
         ('Will public sector pay rise in 2027/28?', 'Pay review body awards for 2027/28 have not been announced yet. They usually come in spring or summer.')],
    extra='<h3 id="tbl">All rates 2026/27 vs 2027/28</h3>' + table(['Rate', 'April 2026', 'April 2027', 'Increase'], [[n, f'£{a:.2f}', f'£{b:.2f}', f'+{(b - a) * 100:.0f}p'] for n, a, b in UK]),
    src=[('GOV.UK — LPC recommendations take the National Living Wage to £13.21 (28 Oct 2026)', 'https://www.gov.uk/government/news/lpc-recommendations-take-the-national-living-wage-to-1321'),
         ('GOV.UK — Maintaining income tax thresholds until 5 April 2031', 'https://www.gov.uk/government/publications/maintaining-income-tax-and-equivalent-national-insurance-contributions-thresholds-until-5-april-2031')],
    note='Rates apply from 1 April 2027. Gross pay before tax and National Insurance. Not legal or tax advice.'))

# ───────────────────────── 🇫🇷 FR — éphéméride ─────────────────────────
PAGES.append(dict(
    path='/fr/ce-qui-change-2027.html', shell='fr/calcul-cout-carburant.html', lang='fr-FR', crumb='France',
    title='Ce qui change en 2027 : SMIC 12,51 €, point d’indice gelé', h1='SMIC et fonctionnaires : ce qui change en 2027',
    desc='SMIC horaire brut 12,51 € (1 897,35 € par mois pour 35 h) depuis le 1er décembre 2026. Point d’indice des fonctionnaires : nouveau gel prévu par le budget 2027, relèvement de l’indice minimum proposé au 1er janvier 2027.',
    badge='🇫🇷 Vérifié le 27/11/2026', sub='SMIC, point d’indice, indice minimum : où en est-on pour 2027 ?', must='id="frH"',
    css='<style id="y7-css">' + BASE + '''
.fr-cal{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.fr-pg{background-color:#fff;border:1px solid #E5E7EB;border-radius:10px;overflow:hidden;box-shadow:0 2px 0 #E5E7EB;min-width:0;text-align:center}
.fr-pg .top{background-color:#1E3A8A;color:#fff;font-size:12px;letter-spacing:.12em;text-transform:uppercase;padding:6px}.fr-pg.r .top{background-color:#B91C1C}.fr-pg.g .top{background-color:#4B5563}
.fr-pg b{display:block;font-size:34px;line-height:1.1;margin:10px 6px 2px;font-family:Georgia,serif}.fr-pg p{font-size:13.5px;margin:0 10px 12px;line-height:1.45}
.fr-calc{margin-top:14px;border:1px solid #DBEAFE;background-color:#EFF6FF;border-radius:14px;padding:14px}.fr-calc h2{font-size:18px;margin:0 0 8px}
.fr-calc label{display:block;font-size:13px;font-weight:700}.fr-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #BFDBFE;border-radius:8px;margin-top:4px}
.fr-o{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:10px}.fr-o div{background-color:#fff;border-radius:10px;padding:10px;min-width:0}.fr-o small{display:block;font-size:12px;color:#6B7280}.fr-o b{display:block;font-size:19px;overflow-wrap:anywhere}
@media(max-width:640px){.fr-cal{grid-template-columns:minmax(0,1fr)}.fr-o{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">Le <b>SMIC horaire brut est de 12,51 €</b> depuis le <b>1er décembre 2026</b>, soit <b>1 897,35 € brut par mois</b> pour 35 heures. Le montant au 1er janvier 2027 n’est pas encore publié. Pour les fonctionnaires, le projet de budget 2027 prévoit un <b>nouveau gel du point d’indice</b>, et le gouvernement a proposé de <b>relever l’indice minimum au 1er janvier 2027</b>.</p>
<div class="fr-cal"><div class="fr-pg"><div class="top">1er déc. 2026</div><b>12,51 €</b><p>SMIC horaire brut<br>1 897,35 € / mois (35 h)</p></div>
<div class="fr-pg r"><div class="top">Budget 2027</div><b>Gel</b><p>Point d’indice des fonctionnaires<br>(projet, 4e année)</p></div>
<div class="fr-pg g"><div class="top">1er janv. 2027</div><b>Indice min.</b><p>Relèvement proposé : ~400 000 agents au-dessus du SMIC</p></div></div>
<div class="fr-calc"><h2>Votre SMIC brut</h2><label for="frH">Heures par semaine<input id="frH" inputmode="decimal" value="35"></label>
<div class="fr-o"><div><small>Avant (12,31 €)</small><b id="fr1">–</b></div><div><small>Depuis le 1er déc. 2026 (12,51 €)</small><b id="fr2">–</b></div></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(',','.').replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const E=x=>x.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2})+' €';
function go(){const m=N($('frH').value)*52/12;$('fr1').textContent=E(12.31*m)+' / mois';$('fr2').textContent=E(12.51*m)+' / mois'}$('frH').addEventListener('input',go);go()})();
</script>''',
    faq_h='Questions fréquentes', src_h='Sources (vérifiées le 27/11/2026)',
    faq=[('Quel est le montant du SMIC en 2027 ?', 'Depuis le 1er décembre 2026, le SMIC horaire brut est de 12,51 € (1 897,35 € brut par mois pour 35 h). La revalorisation du 1er janvier 2027 sera annoncée par décret en décembre.'),
         ('Le point d’indice augmente-t-il en 2027 ?', 'Non selon le projet de loi de finances 2027 : le gouvernement prévoit un nouveau gel du point d’indice. Le budget n’est pas encore définitivement adopté.'),
         ('Qu’est-ce que le relèvement de l’indice minimum ?', 'Le ministre de la Fonction publique a proposé de relever l’indice minimum de traitement au 1er janvier 2027 pour qu’environ 400 000 agents aient un traitement de base supérieur au SMIC.'),
         ('Combien fait le SMIC net ?', 'Le net dépend des cotisations ; utilisez notre <a href="/fr/">calculateur brut-net</a>.')],
    extra='',
    src=[('Service-Public.fr — Salaire minimum (mise à jour 26/11/2026)', 'https://www.service-public.gouv.fr/particuliers/actualites/A17008'),
         ('MoneyVox — Indice minimum relevé au 1er janvier 2027 (2/10/2026)', 'https://www.moneyvox.fr/votre-argent/actualites/110643/salaire-des-agents-publics-le-gouvernement-propose-de-relever-le-minimum-de-indice-au-1er-janvier-2027')],
    note='Montants bruts. Les mesures du budget 2027 peuvent changer pendant le débat parlementaire. Pas un conseil juridique.'))

# ───────────────────────── 🇪🇸 ES — sello de nómina ─────────────────────────
PAGES.append(dict(
    path='/es/que-cambia-2027.html', shell='es/calculadora-gasto-gasolina.html', lang='es-ES', crumb='España',
    title='SMI 2027: 1.286 € y subida de funcionarios del 4,5 %', h1='SMI 2027 y sueldo de funcionarios: qué cambia',
    desc='SMI 2027: 1.286 € al mes en 14 pagas (18.004 € al año, 42,87 € al día), +5,3 %, Real Decreto 1013/2026. Funcionarios: subida del 4,5 % en la nómina de enero de 2027 (Real Decreto-ley aprobado el 17/11/2026).',
    badge='🇪🇸 Comprobado el 27/11/2026', sub='Salario mínimo y sueldo público para 2027, con calculadora.', must='id="esS"',
    css='<style id="y7-css">' + BASE + '''
.es-n{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}
.es-card{border:2px solid #7F1D1D;border-radius:12px;padding:14px;background-color:#FFFBEB;position:relative;min-width:0;overflow:hidden}
.es-card h2{font-size:15px;text-transform:uppercase;letter-spacing:.08em;margin:0 0 8px;color:#7F1D1D}.es-card .big{font-size:40px;font-weight:900;line-height:1;color:#7F1D1D}
.es-card ul{margin:10px 0 0;padding-left:18px;font-size:14.5px;line-height:1.6}
.es-sello{position:absolute;right:10px;top:10px;border:2px solid #CA8A04;color:#CA8A04;border-radius:8px;padding:2px 8px;font-size:11px;font-weight:800;transform:rotate(8deg);background-color:#FFFBEB}
.es-calc{margin-top:14px;border:1px solid #E5E7EB;border-radius:14px;padding:14px}.es-calc h2{font-size:18px;margin:0 0 8px}
.es-calc label{display:block;font-size:13px;font-weight:700}.es-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px}
.es-o{margin-top:10px;font-size:16px;line-height:1.7}
@media(max-width:640px){.es-n{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">El <b>SMI 2027 es de 1.286 € al mes en 14 pagas</b> (<b>18.004 € al año</b>, 42,87 € al día), un <b>5,3 % más</b>, según el Real Decreto 1013/2026 (BOE del 19 de noviembre de 2026). Los <b>empleados públicos</b> suben un <b>4,5 % en 2027</b>: el Consejo de Ministros lo aprobó el 17 de noviembre de 2026 y en la Administración General del Estado se aplica en la nómina de enero.</p>
<div class="es-n"><div class="es-card"><span class="es-sello">BOE 19/11/2026</span><h2>SMI 2027</h2><div class="big">1.286 €</div><ul><li>14 pagas · 18.004 € al año</li><li>42,87 € al día</li><li>2026: 1.221 € (17.094 € al año)</li></ul></div>
<div class="es-card"><span class="es-sello">RDL 17/11/2026</span><h2>Funcionarios 2027</h2><div class="big">+4,5 %</div><ul><li>Desde la nómina de enero (AGE)</li><li>+0,5 % variable de 2026 si el IPC de 2026 supera el 1,5 %</li><li>Unos 546.000 empleados en el Estado</li></ul></div></div>
<div class="es-calc"><h2>Calcula tu subida</h2><label for="esS">Tu sueldo bruto anual 2026 (€)<input id="esS" inputmode="decimal" value="30000"></label><div class="es-o" id="esR"></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/\./g,'').replace(',','.').replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const E=x=>x.toLocaleString('es-ES',{maximumFractionDigits:0})+' €';
function go(){const s=N($('esS').value);$('esR').innerHTML='Funcionario/a con +4,5 %: <b>'+E(s*1.045)+'</b> al año (+'+E(s*0.045)+', unos '+E(s*0.045/14)+' más por paga).<br>'+(s<18004?'⚠️ Por debajo del SMI 2027 (18.004 € al año a jornada completa).':'')}$('esS').addEventListener('input',go);go()})();
</script>''',
    faq_h='Preguntas frecuentes', src_h='Fuentes (comprobadas el 27/11/2026)',
    faq=[('¿Cuánto es el SMI en 2027?', '1.286 € brutos al mes en 14 pagas, 18.004 € al año y 42,87 € al día, desde el 1 de enero de 2027 (Real Decreto 1013/2026).'),
         ('¿Cuánto sube el SMI en 2027?', 'Un 5,3 % respecto a 2026 (1.221 € en 14 pagas).'),
         ('¿Cuánto suben los funcionarios en 2027?', 'Un 4,5 %. Además puede haber un 0,5 % variable de 2026 si el IPC interanual de 2026 supera el 1,5 %, que se pagaría en el primer trimestre de 2027 con efecto desde enero de 2026.'),
         ('¿Cuánto es el SMI 2027 en 12 pagas?', '18.004 € ÷ 12 = 1.500,33 € al mes con las pagas extra prorrateadas.')],
    extra='<h3 id="tbl">SMI 2026 y 2027</h3>' + table(['', '2026', '2027'], [['Mensual (14 pagas)', '1.221 €', '1.286 €'], ['Anual', '17.094 €', '18.004 €'], ['12 pagas prorrateadas', '1.424,50 €', '1.500,33 €']]),
    src=[('Laboral-Social — El SMI sube un 5,3 % en 2027 y alcanza los 1.286 euros (RD 1013/2026, BOE 19/11/2026)', 'https://www.laboral-social.com/node/30725'),
         ('Ministerio para la Transformación Digital y de la Función Pública — Nota de prensa RDL retribuciones 2027 (17/11/2026)', 'https://digital.gob.es/content/dam/portal-mtdfp/comunicacion/comunicacion_ministro/2026/11/17-11-2026/261117_NdP_RDLretribuciones27.pdf'),
         ('BOE — Real Decreto 126/2026, SMI 2026', 'https://www.boe.es/eli/es/rd/2026/02/18/126/con')],
    note='Importes brutos. Cada administración autonómica y local aplica la subida con sus propias normas. No es asesoramiento jurídico.'))

# ───────────────────────── 🇦🇺 AU — before/after bars ─────────────────────────
PAGES.append(dict(
    path='/au/tax-cut-1-july-2027.html', shell='au/fuel-cost-calculator.html', lang='en-AU', crumb='Australia',
    title='Tax Cut 1 July 2027: 14% Rate Calculator + Minimum Wage $26.44', h1='Tax Cut from 1 July 2027: What You Save',
    desc='From 1 July 2027 the 15% tax rate on income between $18,201 and $45,000 falls to 14% (it was 16% until 30 June 2026). Up to $268 a year more. National minimum wage $26.44 an hour from 1 July 2026.',
    badge='🇦🇺 Checked 27 Nov 2026', sub='Compare your tax in 2026–27 and 2027–28.', must='id="auI"',
    css='<style id="y7-css">' + BASE + '''
.au-g{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}
.au-bars{background-color:#0F172A;color:#E2E8F0;border-radius:14px;padding:14px;min-width:0}.au-bars h2{font-size:14px;letter-spacing:.1em;text-transform:uppercase;color:#FBBF24;margin:0 0 10px}
.au-col{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;align-items:end;height:170px;border-bottom:1px solid #334155;padding-bottom:4px}
.au-col div{background-color:#38BDF8;border-radius:8px 8px 0 0;position:relative;min-height:10px}.au-col div:nth-child(2){background-color:#FBBF24}.au-col div:nth-child(3){background-color:#34D399}
.au-col div b{position:absolute;left:0;right:0;top:-22px;text-align:center;font-size:15px;color:#fff}
.au-lab{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;text-align:center;font-size:12px;margin-top:6px;color:#94A3B8}
.au-calc{border:1px solid #E5E7EB;border-radius:14px;padding:14px;min-width:0}.au-calc h2{font-size:18px;margin:0 0 8px}.au-calc label{display:block;font-size:13px;font-weight:700}
.au-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px}
.au-o div{display:flex;justify-content:space-between;gap:8px;padding:8px 0;border-bottom:1px solid #F1F5F9;font-size:15px}.au-o b{font-variant-numeric:tabular-nums}.au-o .sv{color:#047857;font-weight:800}
.au-mw{margin-top:14px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;background-color:#FEF3C7;border-radius:12px;padding:12px}.au-mw b{font-size:26px}
@media(max-width:700px){.au-g{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">From <b>1 July 2027</b> the tax rate on income between <b>$18,201 and $45,000 drops from 15% to 14%</b>. It was 16% until 30 June 2026. Anyone earning over $45,000 saves the full <b>$268 a year</b> compared with 2026–27 ($536 compared with 2025–26). The <b>national minimum wage is $26.44 an hour</b> ($1,004.90 a week) from 1 July 2026.</p>
<div class="au-g"><div class="au-bars"><h2>Rate on $18,201–$45,000</h2><div class="au-col"><div style="height:100%"><b>16%</b></div><div style="height:93.75%"><b>15%</b></div><div style="height:87.5%"><b>14%</b></div></div><div class="au-lab"><span>2025–26</span><span>2026–27</span><span>2027–28</span></div></div>
<div class="au-calc"><h2>Your tax (residents)</h2><label for="auI">Taxable income ($ a year)<input id="auI" inputmode="numeric" value="70000"></label><div class="au-o" id="auO"></div><p style="font-size:12.5px;color:#64748B;margin:8px 0 0">Income tax only, excluding the 2% Medicare levy and offsets.</p></div></div>
<div class="au-mw"><span>National minimum wage from 1 July 2026</span><b>$26.44/hr</b><span>$1,004.90 per 38-hour week</span></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const A=x=>'$'+Math.round(x).toLocaleString('en-AU');
function tax(y,r){let t=0;if(y>18200)t+=(Math.min(y,45000)-18200)*r;if(y>45000)t+=(Math.min(y,135000)-45000)*0.30;if(y>135000)t+=(Math.min(y,190000)-135000)*0.37;if(y>190000)t+=(y-190000)*0.45;return t}
function go(){const y=N($('auI').value),a=tax(y,.15),b=tax(y,.14);$('auO').innerHTML='<div><span>2026–27 (15%)</span><b>'+A(a)+'</b></div><div><span>2027–28 (14%)</span><b>'+A(b)+'</b></div><div><span>You save</span><b class="sv">'+A(a-b)+' a year</b></div>'}$('auI').addEventListener('input',go);go()})();
</script>''',
    faq_h='Frequently asked questions', src_h='Sources (checked 27 November 2026)',
    faq=[('What are the tax rates from 1 July 2027?', '0% up to $18,200; 14% from $18,201 to $45,000; 30% from $45,001 to $135,000; 37% from $135,001 to $190,000; 45% above $190,000 (residents, excluding Medicare levy).'),
         ('How much will I save from the 2027 tax cut?', 'Compared with 2026–27, 1% of your income between $18,201 and $45,000 — up to $268 a year. Compared with 2025–26 (16%), up to $536.'),
         ('Is the 2027 tax cut law?', 'Yes. The ATO says the cuts to 15% (1 July 2026) and 14% (1 July 2027) are now law.'),
         ('What is the minimum wage in Australia?', '$26.44 an hour or $1,004.90 for a 38-hour week from 1 July 2026, after the Fair Work Commission Annual Wage Review 2026.')],
    extra='<h3 id="tbl">Resident tax rates by year</h3>' + table(['Taxable income', '2025–26', '2026–27', '2027–28'], [['$0 – $18,200', '0%', '0%', '0%'], ['$18,201 – $45,000', '16%', '15%', '14%'], ['$45,001 – $135,000', '30%', '30%', '30%'], ['$135,001 – $190,000', '37%', '37%', '37%'], ['$190,001+', '45%', '45%', '45%']]),
    src=[('ATO — Personal income tax: new tax cuts for every Australian taxpayer', 'https://www.ato.gov.au/about-ato/new-legislation/in-detail/individuals/personal-income-tax-new-tax-cuts-for-every-australian-taxpayer'),
         ('Fair Work Ombudsman — Minimum wages increase from 1 July 2026', 'https://www.fairwork.gov.au/newsroom/news/annual-wage-review-2026')],
    note='Estimates for Australian residents. Medicare levy, offsets and HELP repayments are not included. Not tax advice.'))

# ───────────────────────── 🇧🇷 BR — carteira de trabalho ─────────────────────────
PAGES.append(dict(
    path='/br/salario-minimo-2027.html', shell='br/calculadora-ferias.html', lang='pt-BR', crumb='Brasil',
    title='Salário mínimo 2027: R$ 1.741 (previsto) — valor por hora e por dia', h1='Salário mínimo 2027: R$ 1.741',
    desc='O projeto de Orçamento de 2027 prevê salário mínimo de R$ 1.741 (hoje R$ 1.621), alta de 7,4%. Valor por hora (220 h) e por dia, e quem ganha até R$ 5 mil segue isento do Imposto de Renda.',
    badge='🇧🇷 Conferido em 27/11/2026', sub='Valor previsto, por hora e por dia — e como fica o IR.', must='id="brS"',
    css='<style id="y7-css">' + BASE + '''
.br-ctps{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);background-color:#1E3A8A;border-radius:14px;padding:10px;gap:10px}
.br-pg{background-color:#F8FAFC;border-radius:8px;padding:14px;min-width:0;background-image:repeating-linear-gradient(0deg,transparent 0,transparent 27px,#E2E8F0 28px)}
.br-pg h2{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#1E3A8A;margin:0 0 8px}.br-pg .v{font-size:38px;font-weight:900;color:#1E3A8A;line-height:1.05}
.br-pg dl{margin:10px 0 0;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 10px;font-size:14.5px}.br-pg dt{color:#475569}.br-pg dd{margin:0;font-weight:700;text-align:right}
.br-calc{margin-top:14px;border:1px solid #E5E7EB;border-radius:14px;padding:14px}.br-calc h2{font-size:18px;margin:0 0 8px}.br-calc label{display:block;font-size:13px;font-weight:700}
.br-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px}.br-r{margin-top:10px;font-size:15.5px;line-height:1.7}
@media(max-width:640px){.br-ctps{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">O projeto de Orçamento de 2027 (PLOA), enviado ao Congresso em 31 de agosto de 2026, prevê <b>salário mínimo de R$ 1.741 em 2027</b>, <b>R$ 120 (7,4%) a mais</b> que os R$ 1.621 de 2026. O valor ainda pode mudar conforme o INPC até novembro e é fixado por decreto no fim do ano. Quem ganha <b>até R$ 5 mil por mês</b> continua <b>isento do Imposto de Renda</b>.</p>
<div class="br-ctps"><div class="br-pg"><h2>2027 · previsto</h2><div class="v">R$ 1.741</div><dl><dt>Por hora (220 h)</dt><dd>R$ 7,91</dd><dt>Por dia (30 dias)</dt><dd>R$ 58,03</dd><dt>Aumento</dt><dd>+R$ 120</dd></dl></div>
<div class="br-pg"><h2>2026 · em vigor</h2><div class="v">R$ 1.621</div><dl><dt>Por hora (220 h)</dt><dd>R$ 7,37</dd><dt>Por dia (30 dias)</dt><dd>R$ 54,03</dd><dt>IR</dt><dd>isento até R$ 5 mil</dd></dl></div></div>
<div class="br-calc"><h2>Quantos salários mínimos você ganha?</h2><label for="brS">Seu salário bruto mensal (R$)<input id="brS" inputmode="decimal" value="3500"></label><div class="br-r" id="brR"></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/\./g,'').replace(',','.').replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const R=x=>'R$ '+x.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
function go(){const s=N($('brS').value);$('brR').innerHTML='Equivale a <b>'+(s/1621).toLocaleString('pt-BR',{maximumFractionDigits:2})+'</b> salários mínimos de 2026 e <b>'+(s/1741).toLocaleString('pt-BR',{maximumFractionDigits:2})+'</b> do previsto para 2027.<br>'+(s<=5000?'✅ Até R$ 5.000: isento de IR na tabela mensal.':'ℹ️ Acima de R$ 5.000: há IR (com redução parcial até R$ 7.350).')}$('brS').addEventListener('input',go);go()})();
</script>''',
    faq_h='Perguntas frequentes', src_h='Fontes (conferidas em 27/11/2026)',
    faq=[('Qual será o salário mínimo em 2027?', 'O PLOA 2027 prevê R$ 1.741. O valor definitivo sai por decreto no fim de 2026, depois do INPC acumulado até novembro.'),
         ('Quanto é o salário mínimo 2027 por hora?', 'R$ 1.741 ÷ 220 horas = R$ 7,91 por hora (jornada de 44 horas semanais).'),
         ('Quanto aumenta o salário mínimo em 2027?', 'R$ 120, cerca de 7,4% sobre os R$ 1.621 de 2026.'),
         ('Quem ganha salário mínimo paga Imposto de Renda?', 'Não. Desde 2026 quem ganha até R$ 5.000 por mês é isento, e há redução parcial até R$ 7.350.')],
    extra='<h3 id="tbl">Salário mínimo 2026 e 2027</h3>' + table(['', '2026', '2027 (previsto)'], [['Mensal', 'R$ 1.621,00', 'R$ 1.741,00'], ['Por dia (÷30)', 'R$ 54,03', 'R$ 58,03'], ['Por hora (÷220)', 'R$ 7,37', 'R$ 7,91'], ['Anual com 13º (×13)', 'R$ 21.073,00', 'R$ 22.633,00']]),
    src=[('Congresso em Foco — Projeto de Orçamento de 2027 prevê salário mínimo de R$ 1.741 (31/8/2026)', 'https://www.congressoemfoco.com.br/noticia/121825/projeto-de-orcamento-de-2027-preve-salario-minimo-de-r-1-741')],
    note='Valor de 2027 é previsão do governo e pode mudar. Valores brutos. Não é aconselhamento jurídico.'))


# ───────────────────────── 🇨🇦 CA — bracket staircase (CRA T4127, 124th ed.) ─────────────────────────
CA27 = [(0, .14), (60044, .205), (120088, .26), (186157, .29), (265203, .33)]
CA26 = [(0, .14), (58523, .205), (117045, .26), (181440, .29), (258482, .33)]
ca_steps = ''.join(f'<div style="--h:{40 + i * 15}%"><b>{r * 100:g}%</b><small>{"$0" if a == 0 else "$" + format(a, ",")}+</small></div>' for i, (a, r) in enumerate(CA27))
PAGES.append(dict(
    path='/ca/2027-tax-brackets.html', shell='ca/salary-after-tax-calculator.html', lang='en-CA', crumb='Canada',
    title='2027 Federal Tax Brackets Canada (CRA official): $60,044, BPA $16,879', h1='2027 Federal Tax Brackets in Canada',
    desc='Official CRA 2027 federal tax brackets (indexed 2.6%): 14% up to $60,044, 20.5% to $120,088, 26% to $186,157, 29% to $265,203, 33% above. Basic personal amount $16,879. CPP YMPE $76,700, EI max insurable $70,800.',
    badge='🇨🇦 CRA T4127 · 124th edition', sub='Brackets, basic personal amount, CPP and EI for January 1, 2027 — with a 2026 vs 2027 calculator.', must='id="caI"',
    css='<style id="y7-css">' + BASE + '''
.ca-g{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:14px}
.ca-stair{background-color:#FEF2F2;border:1px solid #FECACA;border-radius:14px;padding:14px;min-width:0}.ca-stair h2{font-size:14px;letter-spacing:.1em;text-transform:uppercase;color:#991B1B;margin:0 0 8px}
.ca-steps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;align-items:end;height:190px}
.ca-steps div{height:var(--h);background-color:#DC2626;border-radius:8px 8px 0 0;color:#fff;display:flex;flex-direction:column;justify-content:flex-start;align-items:center;padding-top:6px;min-width:0}
.ca-steps div:nth-child(odd){background-color:#B91C1C}.ca-steps b{font-size:16px}.ca-steps small{font-size:10.5px;opacity:.9;text-align:center;overflow-wrap:anywhere;padding:0 2px}
.ca-calc{border:1px solid #E5E7EB;border-radius:14px;padding:14px;min-width:0}.ca-calc h2{font-size:18px;margin:0 0 8px}.ca-calc label{display:block;font-size:13px;font-weight:700}
.ca-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px}
.ca-o div{display:flex;justify-content:space-between;gap:8px;padding:8px 0;border-bottom:1px solid #F3F4F6;font-size:15px}.ca-o b{font-variant-numeric:tabular-nums}.ca-o .sv{color:#047857}
.ca-k{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:14px}.ca-k div{background-color:#F9FAFB;border:1px solid #E5E7EB;border-radius:10px;padding:10px;min-width:0}
.ca-k small{display:block;font-size:12px;color:#6B7280}.ca-k b{display:block;font-size:18px;overflow-wrap:anywhere}
@media(max-width:760px){.ca-g{grid-template-columns:minmax(0,1fr)}.ca-k{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>''',
    app=f'''<section class="app y7" id="calc"><p class="ans">The CRA has published the <b>2027 federal tax brackets</b>, indexed by <b>2.6%</b>: <b>14%</b> on the first <b>$60,044</b>, <b>20.5%</b> up to <b>$120,088</b>, <b>26%</b> up to <b>$186,157</b>, <b>29%</b> up to <b>$265,203</b> and <b>33%</b> above. The <b>basic personal amount rises to $16,879</b> (down to $15,214 for the highest incomes). They take effect on <b>January 1, 2027</b>.</p>
<div class="ca-g"><div class="ca-stair"><h2>Federal rates 2027</h2><div class="ca-steps">{ca_steps}</div></div>
<div class="ca-calc"><h2>Federal tax: 2026 vs 2027</h2><label for="caI">Taxable income ($)<input id="caI" inputmode="numeric" value="80000"></label><div class="ca-o" id="caO"></div><p style="font-size:12.5px;color:#6B7280;margin:8px 0 0">Federal tax after the basic personal amount credit only. Provincial tax is extra: <a href="/ca/salary-after-tax-calculator.html">salary after tax calculator</a>.</p></div></div>
<div class="ca-k"><div><small>CPP max pensionable (YMPE)</small><b>$76,700</b></div><div><small>CPP2 ceiling (YAMPE)</small><b>$87,400</b></div><div><small>EI max insurable</small><b>$70,800</b></div><div><small>EI max employee premium</small><b>$1,161.12</b></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const C=x=>'$'+Math.round(x).toLocaleString('en-CA');
const B27=[[0,.14],[60044,.205],[120088,.26],[186157,.29],[265203,.33]],B26=[[0,.14],[58523,.205],[117045,.26],[181440,.29],[258482,.33]];
function tax(y,B,bmax,bmin,lo,hi){let t=0;for(let i=0;i<B.length;i++){const a=B[i][0],b=i+1<B.length?B[i+1][0]:Infinity;if(y>a)t+=(Math.min(y,b)-a)*B[i][1]}let bpa=y<=lo?bmax:(y>=hi?bmin:bmax-(bmax-bmin)*(y-lo)/(hi-lo));return Math.max(0,t-bpa*.14)}
function go(){const y=N($('caI').value),a=tax(y,B26,16452,14829,181440,258482),b=tax(y,B27,16879,15214,186157,265203);$('caO').innerHTML='<div><span>2026</span><b>'+C(a)+'</b></div><div><span>2027</span><b>'+C(b)+'</b></div><div><span>Difference</span><b class="sv">'+(b<=a?'−':'+')+C(Math.abs(a-b))+'</b></div>'}$('caI').addEventListener('input',go);go()})();
</script>''',
    faq_h='Frequently asked questions', src_h='Sources (checked November 27, 2026)',
    faq=[('What are the 2027 federal tax brackets in Canada?', '14% on taxable income up to $60,044; 20.5% from $60,044 to $120,088; 26% from $120,088 to $186,157; 29% from $186,157 to $265,203; 33% over $265,203 (CRA T4127, 124th edition, effective January 1, 2027).'),
         ('What is the indexation rate for 2027?', '2.6% (2026: 2.0%).'),
         ('What is the basic personal amount for 2027?', '$16,879 for net income up to $186,157, reducing gradually to $15,214 at $265,203 or more.'),
         ('What are the 2027 CPP and EI maximums?', 'CPP: YMPE $76,700, YAMPE $87,400, maximum employee contribution $4,209.00 plus $428.00 CPP2. EI: maximum insurable earnings $70,800, employee rate 1.64%, maximum premium $1,161.12 (outside Quebec).'),
         ('What is the federal minimum wage in 2027?', 'It is $18.15 an hour since April 1, 2026. The April 1, 2027 rate (indexed to inflation) has not been announced yet.')],
    extra='<h3 id="tbl">2026 vs 2027 federal brackets</h3>' + table(['Rate', '2026 from', '2027 from'], [[f'{r * 100:g}%', f'${a:,}', f'${b:,}'] for (a, r), (b, _) in zip(CA26, CA27)]),
    src=[('Canada Revenue Agency — T4127 Payroll Deductions Formulas, 124th Edition, effective January 1, 2027', 'https://www.canada.ca/en/revenue-agency/services/forms-publications/payroll/t4127-payroll-deductions-formulas/t4127-jan/t4127-jan-payroll-deductions-formulas-computer-programs.html'),
         ('Canada Revenue Agency — Indexation adjustment (2026 amounts)', 'https://www.canada.ca/en/revenue-agency/services/tax/individuals/frequently-asked-questions-individuals/adjustment-personal-income-tax-benefit-amounts.html'),
         ('Government of Canada — Federal minimum wage $18.15 (March 2026)', 'https://www.canada.ca/en/employment-social-development/news/2026/03/government-of-canada-raises-the-federal-minimum-wage.html')],
    note='Federal amounts only; provinces set their own brackets. Estimates, not tax advice.'))

# ───────────────────────── 🇲🇽 MX — tablero de propuestas (decisión en diciembre) ─────────────────────────
MX_P = [('Coparmex', 9.9), ('Acción Ciudadana Frente a la Pobreza', 9.5), ('Banamex (estimación)', 11.0), ('CTM y CROC', 12.0), ('Conasami (factible)', 12.0), ('UNT', 13.0), ('Sector obrero en Conasami', 15.0), ('Congreso del Trabajo (máx.)', 18.0)]
mx_rows = ''.join(f'<li><span>{n}</span><i style="--w:{p / 18 * 100:.0f}%"></i><b>{p:g}%</b><em>${315.04 * (1 + p / 100):,.2f}</em></li>' for n, p in MX_P)
PAGES.append(dict(
    path='/mx/salario-minimo-2027.html', shell='mx/calculadora-horas-extra.html', lang='es-MX', crumb='México',
    title='Salario mínimo 2027 en México: propuestas de 9.5% a 18% y cuándo se anuncia', h1='Salario mínimo 2027: ¿cuánto subirá?',
    desc='Salario mínimo 2026: $315.04 diarios (frontera norte $440.87). Para 2027 las propuestas van de 9.5% a 18%; Conasami ve factible 12% (unos $352.84 diarios). El monto se anuncia a inicios de diciembre y rige desde el 1 de enero de 2027.',
    badge='🇲🇽 Actualizado 27/11/2026', sub='Lo que se sabe antes del anuncio de Conasami y cuánto ganarías con cada propuesta.', must='id="mxP"',
    css='<style id="y7-css">' + BASE + '''
.mx-board{background-color:#14532D;color:#ECFDF5;border-radius:14px;padding:14px;min-width:0}.mx-board h2{font-size:14px;letter-spacing:.1em;text-transform:uppercase;color:#FDE68A;margin:0 0 8px}
.mx-board ul{list-style:none;margin:0;padding:0}.mx-board li{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:4px 10px;align-items:baseline;padding:7px 0;border-top:1px solid rgba(255,255,255,.15)}
.mx-board li span{font-size:14px}.mx-board li b{color:#FDE68A}.mx-board li em{font-style:normal;font-size:13px;color:#A7F3D0;font-variant-numeric:tabular-nums}
.mx-board li i{grid-column:1/-1;height:5px;border-radius:5px;background-color:rgba(255,255,255,.12);position:relative;overflow:hidden}.mx-board li i:after{content:"";position:absolute;left:0;top:0;bottom:0;width:var(--w);background-color:#F59E0B}
.mx-now{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:14px}.mx-now div{border:2px solid #14532D;border-radius:12px;padding:10px;min-width:0}.mx-now small{display:block;font-size:12px;color:#4B5563}.mx-now b{display:block;font-size:26px;color:#14532D}
.mx-calc{margin-top:14px;border:1px solid #E5E7EB;border-radius:14px;padding:14px}.mx-calc h2{font-size:18px;margin:0 0 8px}.mx-calc .row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.mx-calc label{display:block;font-size:13px;font-weight:700}.mx-calc select,.mx-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px;background-color:#fff}.mx-r{margin-top:10px;font-size:16px;line-height:1.7}
@media(max-width:560px){.mx-now,.mx-calc .row{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app=f'''<section class="app y7" id="calc"><p class="ans">El <b>salario mínimo 2027 todavía no es oficial</b>. Hoy rige el de 2026: <b>$315.04 diarios</b> en la zona general y <b>$440.87</b> en la Zona Libre de la Frontera Norte. Para 2027 las propuestas van de <b>9.5% a 18%</b>; el presidente de la Conasami considera factible <b>12%</b> (unos <b>$352.84 diarios</b>). El monto se anuncia <b>a inicios de diciembre de 2026</b> y aplica desde el <b>1 de enero de 2027</b>.</p>
<div class="mx-now"><div><small>Zona general 2026</small><b>$315.04</b><small>diarios · ≈ $9,577 al mes</small></div><div><small>Frontera norte 2026</small><b>$440.87</b><small>diarios · ≈ $13,402 al mes</small></div></div>
<div class="mx-board"><h2>Propuestas para 2027 (zona general)</h2><ul>{mx_rows}</ul></div>
<div class="mx-calc"><h2>Tu salario con cada propuesta</h2><div class="row"><label for="mxP">Aumento<select id="mxP">{''.join(f'<option value="{p:g}">{p:g}% — {n}</option>' for n, p in MX_P)}</select></label><label for="mxS">Tu salario diario 2026 ($)<input id="mxS" inputmode="decimal" value="315.04"></label></div><div class="mx-r" id="mxR"></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const P=x=>'$'+x.toLocaleString('es-MX',{minimumFractionDigits:2,maximumFractionDigits:2});
function go(){const p=N($('mxP').value)/100,s=N($('mxS').value),n=s*(1+p);$('mxR').innerHTML='Diario 2027: <b>'+P(n)+'</b> (+'+P(n-s)+')<br>Mensual (×30.4): <b>'+P(n*30.4)+'</b> · antes '+P(s*30.4)}$('mxP').value='12';['mxP','mxS'].forEach(i=>$(i).addEventListener('input',go));$('mxP').addEventListener('change',go);go()})();
</script>''',
    faq_h='Preguntas frecuentes', src_h='Fuentes (consultadas el 27/11/2026)',
    faq=[('¿Ya hay salario mínimo 2027?', 'Todavía no. Los sectores entregan propuestas hasta el 30 de noviembre y el Consejo de Representantes de la Conasami puede votar desde el 1 de diciembre; el anuncio se espera a inicios de diciembre de 2026.'),
         ('¿Cuánto es el salario mínimo 2026?', '$315.04 diarios en la zona general (subió 13%) y $440.87 en la Zona Libre de la Frontera Norte (subió 5%).'),
         ('¿Cuánto sería con 12%?', '$315.04 × 1.12 = $352.84 diarios, unos $10,726 al mes (×30.4).'),
         ('¿Cuándo empieza a aplicar?', 'El nuevo salario mínimo rige desde el 1 de enero de 2027.'),
         ('¿Cambia la jornada en 2027?', 'Según reportes, en 2027 la jornada pasa de 48 a 46 horas semanales sin reducir el sueldo, como parte de la reducción gradual hacia 40 horas.')],
    extra='<h3 id="tbl">Salario diario y mensual por propuesta</h3>' + table(['Propuesta', 'Aumento', 'Diario 2027', 'Mensual (×30.4)'], [[n, f'{p:g}%', f'${315.04 * (1 + p / 100):,.2f}', f'${315.04 * (1 + p / 100) * 30.4:,.0f}'] for n, p in MX_P]),
    src=[('Infobae México — Negociación del salario mínimo 2027 arranca con propuestas de 10% a más de 15% (26/11/2026)', 'https://www.infobae.com/mexico/2026/11/26/negociacion-del-salario-minimo-2027-arranca-con-propuestas-de-aumento-de-10-a-mas-de-15/'),
         ('Bloomberg Línea — Salario mínimo en México aumentará a $315.04 diarios para 2026', 'https://www.bloomberglinea.com/latinoamerica/mexico/salario-minimo-en-mexico-aumentara-a-mxn31504-diarios-para-2026/')],
    note='Las cifras de 2027 son propuestas y escenarios, no el monto oficial. Actualizaremos la página cuando Conasami publique la resolución.'))


# ───────────────────────── 🇺🇸 Social Security COLA 2027 — benefit check ─────────────────────────
SSA = [('Average retired worker', 2095, 2170), ('Aged couple, both receiving', 3238, 3355), ('Aged widow(er) alone', 1936, 2005), ('All disabled workers', 1642, 1701), ('SSI individual (federal)', 994, 1029), ('SSI couple (federal)', 1491, 1544), ('Max benefit at full retirement age', 4152, 4188)]
PAGES.append(dict(
    path='/us/social-security-cola-2027.html', shell='us/bonus-tax-calculator.html', lang='en-US', crumb='United States',
    title='Social Security COLA 2027: 3.6% — New Benefit Amounts & Calculator', h1='Social Security COLA 2027: 3.6%',
    desc='The 2027 Social Security COLA is 3.6%. Average retired worker benefit rises from $2,095 to $2,170 a month. SSI: $1,029 individual. Taxable maximum $192,300. Earnings test $25,560. Calculator for your new check.',
    badge='🇺🇸 SSA · checked Nov 27, 2026', sub='Your January 2027 check, the new limits, and when the money arrives.', must='id="ssB"',
    css='<style id="y7-css">' + BASE + '''
.ss-check{background-color:#F0FDF4;border:1px solid #86EFAC;border-radius:6px;padding:16px;position:relative;min-width:0;background-image:repeating-linear-gradient(135deg,rgba(22,101,52,.04) 0,rgba(22,101,52,.04) 2px,transparent 2px,transparent 10px)}
.ss-check .t{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#166534}
.ss-check .pay{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:end;border-bottom:1px solid #166534;padding:14px 0 6px}
.ss-check .pay span{font-family:Georgia,serif;font-style:italic;font-size:15px}.ss-check .pay b{font-size:30px;font-family:Georgia,serif;background-color:#fff;border:1px solid #86EFAC;padding:2px 10px;border-radius:4px}
.ss-check label{display:block;font-size:13px;font-weight:700;margin-top:12px}.ss-check input{display:block;width:100%;font:inherit;font-size:18px;padding:9px;border:1px solid #86EFAC;border-radius:6px;margin-top:4px;background-color:#fff}
.ss-check .r{margin-top:8px;font-size:15px}.ss-mic{font-family:"Courier New",monospace;font-size:12px;color:#166534;margin-top:10px;letter-spacing:.08em}
.ss-list{margin-top:14px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.ss-list div{border:1px solid #E5E7EB;border-radius:10px;padding:10px;min-width:0}.ss-list small{display:block;font-size:12px;color:#6B7280}.ss-list b{font-size:17px}.ss-list s{color:#9CA3AF;font-size:13px;margin-right:6px}
@media(max-width:560px){.ss-list{grid-template-columns:minmax(0,1fr)}.ss-check .pay{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">Social Security and SSI benefits rise <b>3.6% in 2027</b>, the largest increase in five years. The <b>average retired worker</b> goes from about <b>$2,095 to $2,170 a month</b> (+$75). The higher Social Security checks start in <b>January 2027</b>; SSI recipients get theirs on <b>December 31, 2026</b>.</p>
<div class="ss-check"><div class="t"><span>Benefit statement · 2027</span><span>COLA +3.6%</span></div><div class="pay"><span>Your new monthly benefit</span><b id="ssOut">$2,170</b></div>
<label for="ssB">Your 2026 monthly benefit before deductions ($)<input id="ssB" inputmode="decimal" value="2095"></label><div class="r" id="ssR"></div><div class="ss-mic">⑆ 0 3 6 ⑆ 2027 ⑈ estimate only</div></div>
<div class="ss-list"><div><small>Taxable maximum</small><s>$184,500</s><b>$192,300</b></div><div><small>Earnings test (under FRA)</small><s>$24,480</s><b>$25,560/yr</b></div><div><small>Earnings test (year you reach FRA)</small><s>$65,160</s><b>$67,920/yr</b></div><div><small>Quarter of coverage</small><s>$1,890</s><b>$1,970</b></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const U=x=>'$'+x.toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:0});
function go(){const b=N($('ssB').value),n=Math.floor(b*1.036);$('ssOut').textContent=U(n);$('ssR').innerHTML='+'+U(n-b)+' a month · +'+U((n-b)*12)+' a year (before any Medicare Part B change)'}$('ssB').addEventListener('input',go);go()})();
</script>''',
    faq_h='Frequently asked questions', src_h='Sources (checked November 27, 2026)',
    faq=[('What is the Social Security COLA for 2027?', '3.6%, announced by the Social Security Administration on October 14, 2026.'),
         ('How much will the average Social Security check be in 2027?', 'About $2,170 a month for all retired workers, up from $2,095 (SSA estimate for January 2027).'),
         ('When does the 2027 COLA show up?', 'In the January 2027 Social Security payment. SSI recipients receive the increase on December 31, 2026.'),
         ('What is the 2027 SSI payment?', '$1,029 a month for an individual and $1,544 for a couple (federal amounts).'),
         ('What is the Social Security wage base for 2027?', '$192,300. Earnings above this are not subject to the 6.2% Social Security tax.'),
         ('How does Social Security round the COLA?', 'The new benefit is rounded down to the next lower dollar, which is why the calculator rounds down.')],
    extra='<h3 id="tbl">2026 vs 2027 average monthly benefits</h3>' + table(['Type', 'Before COLA', 'After 3.6% COLA'], [[n, f'${a:,}', f'${b:,}'] for n, a, b in SSA]),
    src=[('SSA — Social Security Announces 3.6 Percent Benefit Increase for 2027 (Oct 14, 2026)', 'https://www.ssa.gov/news/en/press/releases/2026-10-14.html'),
         ('SSA — 2027 Social Security Changes fact sheet', 'https://www.ssa.gov/news/en/cola/factsheets/2027.html')],
    note='Medicare Part B premiums are usually deducted from the check, so the amount you receive can rise by less. Estimate only.'))

# ───────────────────────── 🇺🇸 401(k) limit 2027 — fill meters ─────────────────────────
PAGES.append(dict(
    path='/us/401k-limit-2027.html', shell='us/bonus-tax-calculator.html', lang='en-US', crumb='United States',
    title='401(k) Limit 2027: $25,500 (+$8,500 Catch-Up), IRA $7,500, HSA $4,500', h1='401(k) Contribution Limit 2027: $25,500',
    desc='IRS 2027 limits: 401(k)/403(b)/TSP $25,500, catch-up age 50+ $8,500, ages 60–63 $11,750. IRA $7,500 (+$1,100 catch-up). SIMPLE $17,500. HSA $4,500. Roth IRA phase-out $158,000–$173,000 single.',
    badge='🇺🇸 IRS · announced Nov 12, 2026', sub='How much you can put in for 2027 — and how close your paycheck percentage gets you.', must='id="kAge"',
    css='<style id="y7-css">' + BASE + '''
.k-g{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}
.k-meter{border:1px solid #E5E7EB;border-radius:14px;padding:14px;min-width:0}.k-meter h2{font-size:18px;margin:0 0 10px}
.k-bar{margin:10px 0}.k-bar .l{display:flex;justify-content:space-between;gap:8px;font-size:14px}.k-bar .tr{height:14px;border-radius:8px;background-color:#EEF2FF;overflow:hidden;margin-top:4px}.k-bar .tr i{display:block;height:100%;background-color:#4F46E5;border-radius:8px;transition:width .3s}
.k-bar.cu .tr i{background-color:#F59E0B}
.k-form label{display:block;font-size:13px;font-weight:700;margin-top:8px}.k-form select,.k-form input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px;background-color:#fff}
.k-tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.k-tiles div{background-color:#EEF2FF;border-radius:12px;padding:12px;min-width:0}.k-tiles small{display:block;font-size:12px;color:#4338CA}.k-tiles b{display:block;font-size:22px}
.k-r{margin-top:10px;font-size:15px;line-height:1.6}
@media(max-width:720px){.k-g{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">For 2027 you can defer <b>$25,500</b> into a 401(k), 403(b), most 457 plans or the federal TSP — <b>$1,000 more</b> than in 2026. Workers 50 and older can add a <b>$8,500 catch-up</b> (total $34,000), and those aged <b>60 to 63</b> can add <b>$11,750</b> instead. The <b>IRA limit stays $7,500</b> (+$1,100 catch-up) and the <b>HSA limit</b> for self-only coverage is <b>$4,500</b>.</p>
<div class="k-g"><div class="k-tiles"><div><small>401(k) / 403(b) / TSP</small><b>$25,500</b></div><div><small>Catch-up 50+</small><b>$8,500</b></div><div><small>Super catch-up 60–63</small><b>$11,750</b></div><div><small>IRA (+$1,100 at 50+)</small><b>$7,500</b></div><div><small>SIMPLE IRA</small><b>$17,500</b></div><div><small>HSA self-only</small><b>$4,500</b></div></div>
<div class="k-meter"><h2>Will your contributions hit the limit?</h2><div class="k-form"><label for="kAge">Your age in 2027<select id="kAge"><option value="0">Under 50</option><option value="8500" selected>50–59 or 64+</option><option value="11750">60–63</option></select></label><label for="kSal">Salary ($)<input id="kSal" inputmode="numeric" value="90000"></label><label for="kPct">Contribution (% of pay)<input id="kPct" inputmode="decimal" value="15"></label></div>
<div class="k-bar"><div class="l"><span>Regular limit</span><b id="kL1">–</b></div><div class="tr"><i id="kB1" style="width:0"></i></div></div><div class="k-bar cu"><div class="l"><span>Catch-up</span><b id="kL2">–</b></div><div class="tr"><i id="kB2" style="width:0"></i></div></div><div class="k-r" id="kR"></div></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const U=x=>'$'+Math.round(x).toLocaleString('en-US');
function go(){const cu=+$('kAge').value,c=N($('kSal').value)*N($('kPct').value)/100,a=Math.min(c,25500),b=Math.min(Math.max(c-25500,0),cu);
$('kL1').textContent=U(a)+' / $25,500';$('kB1').style.width=(a/25500*100)+'%';$('kL2').textContent=cu?U(b)+' / '+U(cu):'not eligible';$('kB2').style.width=cu?(b/cu*100)+'%':'0';
const max=25500+cu;$('kR').innerHTML=c>=max?'✅ You reach the full '+U(max)+'. Anything above stops.':'To max out '+U(max)+', contribute about <b>'+(max/Math.max(N($('kSal').value),1)*100).toFixed(1)+'%</b> of pay.'}
['kAge','kSal','kPct'].forEach(i=>{$(i).addEventListener('input',go);$(i).addEventListener('change',go)});go()})();
</script>''',
    faq_h='Frequently asked questions', src_h='Sources (checked November 27, 2026)',
    faq=[('What is the 401(k) limit for 2027?', '$25,500 for employee elective deferrals to 401(k), 403(b), most 457 plans and the Thrift Savings Plan (2026: $24,500).'),
         ('What is the 401(k) catch-up for 2027?', '$8,500 for ages 50 and over, or $11,750 for ages 60 to 63 under the SECURE 2.0 "super catch-up".'),
         ('What is the IRA limit for 2027?', '$7,500, unchanged from 2026, plus a $1,100 catch-up for ages 50 and over.'),
         ('What are the Roth IRA income limits for 2027?', 'The phase-out range is $158,000–$173,000 for singles and heads of household and $250,000–$260,000 for married couples filing jointly.'),
         ('What is the HSA limit for 2027?', '$4,500 for self-only coverage (2026: $4,400).'),
         ('Who is a highly compensated employee in 2027?', 'Someone who earned more than $170,000 (up from $160,000).')],
    extra='<h3 id="tbl">2026 vs 2027 limits</h3>' + table(['Limit', '2026', '2027'], [['401(k)/403(b)/TSP deferral', '$24,500', '$25,500'], ['Catch-up 50+', '$8,000', '$8,500'], ['Catch-up 60–63', '—', '$11,750'], ['IRA', '$7,500', '$7,500'], ['IRA catch-up 50+', '$1,100', '$1,100'], ['SIMPLE IRA', '$17,000', '$17,500'], ['HSA self-only', '$4,400', '$4,500'], ['Roth IRA phase-out (single)', '—', '$158,000–$173,000'], ['HCE threshold', '$160,000', '$170,000']]),
    src=[('PLANSPONSOR — IRS raises 401(k) contribution limit to $25,500, IRA limit to $7,500 (Nov 12, 2026)', 'https://www.plansponsor.com/irs-raises-401k-contribution-limit-to-25500-ira-limit-to-7500/'),
         ('IRS — 2027 cost-of-living adjustments (newsroom)', 'https://www.irs.gov/node/167581')],
    note='Employer contributions count toward a separate overall limit. Plan rules may be lower. Not tax advice.'))

# ───────────────────────── 🇵🇱 PL — pasek wypłaty ─────────────────────────
PAGES.append(dict(
    path='/pl/placa-minimalna-2027.html', shell='pl/calculator.html', lang='pl-PL', crumb='Polska',
    title='Płaca minimalna 2027: 4950 zł brutto, stawka godzinowa 32,30 zł', h1='Płaca minimalna 2027: 4950 zł brutto',
    desc='Od 1 stycznia 2027 r. minimalne wynagrodzenie wynosi 4950 zł brutto (+144 zł, 3%), a minimalna stawka godzinowa 32,30 zł. Rozporządzenie ogłoszone we wrześniu 2026 r. Kalkulator miesięczny i godzinowy.',
    badge='🇵🇱 Stan na 27.11.2026', sub='Ile wynosi najniższa krajowa i stawka godzinowa od stycznia 2027.', must='id="plH"',
    css='<style id="y7-css">' + BASE + '''
.pl-pasek{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border:2px solid #DC2626;border-radius:12px;overflow:hidden}
.pl-pasek div{padding:14px;min-width:0;border-right:2px dashed #FCA5A5;background-color:#fff}.pl-pasek div:last-child{border-right:0;background-color:#DC2626;color:#fff}
.pl-pasek small{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.8}.pl-pasek b{display:block;font-size:28px;line-height:1.15;margin-top:4px}
.pl-calc{margin-top:14px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px}
.pl-box{border:1px solid #E5E7EB;border-radius:12px;padding:12px;min-width:0}.pl-box h2{font-size:16px;margin:0 0 6px}.pl-box label{display:block;font-size:13px;font-weight:700}
.pl-box input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px}.pl-box .r{margin-top:8px;font-size:15px;line-height:1.6}
@media(max-width:620px){.pl-pasek,.pl-calc{grid-template-columns:minmax(0,1fr)}.pl-pasek div{border-right:0;border-bottom:2px dashed #FCA5A5}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">Od <b>1 stycznia 2027 r.</b> <b>płaca minimalna wynosi 4950 zł brutto</b> miesięcznie, czyli <b>o 144 zł (3%) więcej</b> niż 4806 zł w 2026 r. <b>Minimalna stawka godzinowa</b> dla umów zlecenia rośnie do <b>32,30 zł</b> (+0,90 zł). Rozporządzenie Rady Ministrów ukazało się w Dzienniku Ustaw we wrześniu 2026 r.</p>
<div class="pl-pasek"><div><small>2026</small><b>4806 zł</b><small>31,40 zł/godz.</small></div><div><small>Podwyżka</small><b>+144 zł</b><small>+0,90 zł/godz.</small></div><div><small>Od 1.01.2027</small><b>4950 zł</b><small>32,30 zł/godz.</small></div></div>
<div class="pl-calc"><div class="pl-box"><h2>Umowa zlecenie</h2><label for="plH">Liczba godzin w miesiącu<input id="plH" inputmode="decimal" value="120"></label><div class="r" id="plR"></div></div>
<div class="pl-box"><h2>Część etatu</h2><label for="plE">Wymiar etatu (np. 0,5)<input id="plE" inputmode="decimal" value="1"></label><div class="r" id="plER"></div></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(',','.').replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const Z=x=>x.toLocaleString('pl-PL',{minimumFractionDigits:2,maximumFractionDigits:2})+' zł';
function go(){const h=N($('plH').value);$('plR').innerHTML='2027: <b>'+Z(h*32.30)+'</b> brutto<br>2026: '+Z(h*31.40)+' (+'+Z(h*0.90)+')';const e=N($('plE').value);$('plER').innerHTML='Minimum przy tym wymiarze: <b>'+Z(4950*e)+'</b> brutto<br>Rocznie: '+Z(4950*e*12)}
['plH','plE'].forEach(i=>$(i).addEventListener('input',go));go()})();
</script>''',
    faq_h='Najczęstsze pytania', src_h='Źródła (stan na 27.11.2026)',
    faq=[('Ile wynosi płaca minimalna w 2027 roku?', '4950 zł brutto miesięcznie od 1 stycznia 2027 r. (w 2026 r.: 4806 zł).'),
         ('Ile wynosi minimalna stawka godzinowa w 2027 roku?', '32,30 zł brutto za godzinę (w 2026 r.: 31,40 zł). Dotyczy m.in. umów zlecenia.'),
         ('O ile wzrośnie najniższa krajowa?', 'O 144 zł brutto, czyli o około 3%.'),
         ('Czy związki zawodowe chciały więcej?', 'Tak, związki proponowały 5200 zł, a pracodawcy 4860 zł. Rada Dialogu Społecznego nie osiągnęła porozumienia, więc kwotę ustalił rząd.'),
         ('Ile wynosi płaca minimalna 2027 netto?', 'Kwota netto zależy od składek, podatku i rodzaju umowy, dlatego podajemy tu kwoty brutto ustalone w rozporządzeniu.')],
    extra='<h3 id="tbl">Płaca minimalna 2026 i 2027</h3>' + table(['', '2026', '2027'], [['Miesięcznie (brutto)', '4806 zł', '4950 zł'], ['Stawka godzinowa', '31,40 zł', '32,30 zł'], ['Rocznie (×12)', '57 672 zł', '59 400 zł']]),
    src=[('Infor Kadry — Od 1 stycznia 2027 r. płaca minimalna wyniesie 4950 zł', 'https://kadry.infor.pl/kadry/wynagrodzenia/wynagrodzenie-minimalne/7602954,od-1-stycznia-2027-r-placa-minimalna-wyniesie-4950-zl-podwyzka-o-144-zl-w-stosunku-do-2026-r-to-3-proc-czyli-wiecej-niz-przewidywano.html'),
         ('XYZ.pl — Płaca minimalna w 2027 r. Rozporządzenie trafiło do Dziennika Ustaw (15.09.2026)', 'https://xyz.pl/?p=249900'),
         ('Dziennik Ustaw 2026 poz. 1213', 'https://eli.gov.pl/eli/DU/2026/1213')],
    note='Kwoty brutto. To nie jest porada prawna.'))

# ───────────────────────── 🇳🇱 NL — leeftijdstrap ─────────────────────────
NL = [(21, 15.29), (20, 13.38), (19, 11.47), (18, 9.56), (17, 7.65), (16, 6.12), (15, 4.59)]
nl_stairs = ''.join(f'<div style="--h:{r / 15.29 * 100:.0f}%"><b>€{r:.2f}</b><small>{a}{"+" if a == 21 else ""} jr</small></div>' for a, r in reversed(NL))
PAGES.append(dict(
    path='/nl/minimumloon-2027.html', shell='nl/aow-leeftijd-berekenen.html', lang='nl-NL', crumb='Nederland',
    title='Minimumloon 2027: €15,29 per uur (alle leeftijden)', h1='Minimumloon per 1 januari 2027: €15,29',
    desc='Het wettelijk minimumloon per 1 januari 2027 is €15,29 bruto per uur voor 21 jaar en ouder. Jeugdlonen: 20 jaar €13,38, 19 €11,47, 18 €9,56, 17 €7,65, 16 €6,12, 15 €4,59. Bereken je maandloon.',
    badge='🇳🇱 Rijksoverheid · 27-11-2026', sub='Uurloon per leeftijd en wat dat per maand is.', must='id="nlA"',
    css='<style id="y7-css">' + BASE + '''
.nl-trap{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px;align-items:end;height:210px;background-color:#FFF7ED;border-radius:14px;padding:14px 10px 10px}
.nl-trap div{height:var(--h);background-color:#EA580C;border-radius:8px 8px 2px 2px;display:flex;flex-direction:column;justify-content:space-between;align-items:center;padding:6px 2px;color:#fff;min-width:0}
.nl-trap div:last-child{background-color:#9A3412}.nl-trap b{font-size:13px;overflow-wrap:anywhere;text-align:center}.nl-trap small{font-size:11px}
.nl-calc{margin-top:14px;border:1px solid #E5E7EB;border-radius:14px;padding:14px}.nl-calc h2{font-size:18px;margin:0 0 8px}.nl-calc .row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.nl-calc label{display:block;font-size:13px;font-weight:700}.nl-calc select,.nl-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px;background-color:#fff}.nl-r{margin-top:10px;font-size:16px;line-height:1.7}
@media(max-width:560px){.nl-trap b{font-size:11px}.nl-calc .row{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app=f'''<section class="app y7" id="calc"><p class="ans">Per <b>1 januari 2027</b> is het <b>minimumloon €15,29 bruto per uur</b> voor werknemers van <b>21 jaar en ouder</b>. Jongeren krijgen een percentage daarvan: <b>20 jaar €13,38</b>, 19 jaar €11,47 en 18 jaar €9,56. Er is geen vast maandbedrag meer: je maandloon hangt af van je aantal uren.</p>
<div class="nl-trap">{nl_stairs}</div>
<div class="nl-calc"><h2>Wat verdien je per maand?</h2><div class="row"><label for="nlA">Leeftijd<select id="nlA">{''.join(f'<option value="{r}">{a}{" jaar en ouder" if a == 21 else " jaar"}</option>' for a, r in NL)}</select></label><label for="nlH">Uren per week<input id="nlH" inputmode="decimal" value="38"></label></div><div class="nl-r" id="nlR"></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(',','.').replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const E=x=>'€ '+x.toLocaleString('nl-NL',{minimumFractionDigits:2,maximumFractionDigits:2});
function go(){const r=+$('nlA').value,h=N($('nlH').value),m=r*h*52/12;$('nlR').innerHTML='Per uur: <b>'+E(r)+'</b><br>Per maand (gemiddeld): <b>'+E(m)+'</b> bruto<br>Per jaar: '+E(m*12)+' (exclusief 8% vakantiegeld)'}
$('nlA').addEventListener('change',go);$('nlH').addEventListener('input',go);go()})();
</script>''',
    faq_h='Veelgestelde vragen', src_h='Bronnen (gecontroleerd op 27-11-2026)',
    faq=[('Hoe hoog is het minimumloon in 2027?', '€15,29 bruto per uur per 1 januari 2027 voor 21 jaar en ouder.'),
         ('Wat is het minimumloon voor jongeren in 2027?', '20 jaar €13,38, 19 jaar €11,47, 18 jaar €9,56, 17 jaar €7,65, 16 jaar €6,12 en 15 jaar €4,59 per uur.'),
         ('Hoeveel is het minimumloon per maand bij 38 uur?', '€15,29 × 38 × 52 ÷ 12 = €2.517,75 bruto per maand gemiddeld.'),
         ('Komt er vakantiegeld bovenop?', 'Ja, minimaal 8% vakantiegeld komt bovenop het minimumloon.'),
         ('Bestaat er nog een maandbedrag?', 'Nee, sinds 2024 geldt alleen een wettelijk minimumuurloon.')],
    extra='<h3 id="tbl">Minimumloon per leeftijd per 1 januari 2027</h3>' + table(['Leeftijd', 'Bruto per uur'], [[f'{a}{" jaar en ouder" if a == 21 else " jaar"}', f'€ {r:.2f}'.replace('.', ',')] for a, r in NL]) + '<p>Bereken ook je loon met de <a href="/nl/minimumloon-berekenen.html">minimumloon calculator</a>.</p>',
    src=[('Rijksoverheid — Bedragen minimumloon 2027', 'https://www.rijksoverheid.nl/onderwerpen/minimumloon/bedragen-minimumloon/bedragen-minimumloon-2027')],
    note='Brutobedragen. De bedragen per 1 juli 2027 worden later bekendgemaakt.'))

# ───────────────────────── 🇹🇼 TW — 紅色日曆 ─────────────────────────
PAGES.append(dict(
    path='/tw/zuidi-gongzi-2027.html', shell='tw/50-30-20-budget-calculator.html', lang='zh-Hant-TW', crumb='台灣',
    title='2027最低工資：月薪30,900元、時薪205元（115年→116年）', h1='2027年最低工資：月薪30,900元、時薪205元',
    desc='最低工資審議會2026年9月24日通過，2027年1月1日起每月最低工資30,900元（+1,400元）、每小時205元（+9元），調幅4.745%，連續第11年調漲。',
    badge='🇹🇼 2026/11/27 查核', sub='月薪、時薪、兼職月收入一次算。', must='id="twH"',
    css='<style id="y7-css">' + BASE + '''
.tw-cal{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.tw-page{background-color:#fff;border:1px solid #FECACA;border-radius:10px;overflow:hidden;text-align:center;min-width:0;box-shadow:0 3px 0 #FECACA}
.tw-page .top{background-color:#B91C1C;color:#FEF3C7;font-size:13px;padding:6px;letter-spacing:.2em}.tw-page b{display:block;font-size:40px;color:#B91C1C;margin:8px 0 0;font-variant-numeric:tabular-nums}
.tw-page p{margin:2px 10px 12px;font-size:14px;color:#4B5563}
.tw-calc{margin-top:14px;border:1px solid #FECACA;background-color:#FFF7ED;border-radius:12px;padding:14px}.tw-calc h2{font-size:17px;margin:0 0 8px}
.tw-calc label{display:block;font-size:13px;font-weight:700}.tw-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #FCA5A5;border-radius:8px;margin-top:4px;background-color:#fff}.tw-r{margin-top:10px;font-size:16px;line-height:1.7}
@media(max-width:480px){.tw-cal{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">最低工資審議會於<b>2026年9月24日</b>通過，<b>2027年1月1日起</b>每月最低工資調為<b>30,900元</b>（原29,500元，+1,400元），每小時調為<b>205元</b>（原196元，+9元），調幅<b>4.745%</b>，是連續第11年調漲。</p>
<div class="tw-cal"><div class="tw-page"><div class="top">月薪 · 2027.1.1</div><b>30,900</b><p>原 29,500 元 · +1,400</p></div><div class="tw-page"><div class="top">時薪 · 2027.1.1</div><b>205</b><p>原 196 元 · +9</p></div></div>
<div class="tw-calc"><h2>兼職時薪試算</h2><label for="twH">每月工作時數<input id="twH" inputmode="decimal" value="80"></label><div class="tw-r" id="twR"></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const T=x=>Math.round(x).toLocaleString('zh-TW')+' 元';
function go(){const h=N($('twH').value);$('twR').innerHTML='2027年：<b>'+T(h*205)+'</b>／月<br>2026年：'+T(h*196)+'（每月多 '+T(h*9)+'）'}$('twH').addEventListener('input',go);go()})();
</script>''',
    faq_h='常見問題', src_h='資料來源（2026/11/27查核）',
    faq=[('2027年最低工資是多少？', '每月30,900元、每小時205元，自2027年1月1日起實施。'),
         ('2027年最低工資漲多少？', '月薪調升1,400元、時薪調升9元，調幅4.745%。'),
         ('什麼時候通過的？', '勞動部最低工資審議會於2026年9月24日開會通過。'),
         ('兼職每月工作80小時可以領多少？', '205元×80小時＝16,400元（稅前），比2026年多720元。')],
    extra='<h3 id="tbl">2026年與2027年比較</h3>' + table(['', '2026年', '2027年'], [['每月最低工資', '29,500元', '30,900元'], ['每小時最低工資', '196元', '205元']]),
    src=[('公視新聞網 — 最低工資連11年調漲 明年月薪30900元、時薪205元', 'https://news.pts.org.tw/article/828540'),
         ('1111人力銀行 — 明年最低工資月薪30,900元、時薪205元', 'https://www.1111.com.tw/news/jobns/167643')],
    note='以上為稅前金額。實際適用以勞動部公告為準。'))

# ───────────────────────── 🇵🇹 PT — azulejo ─────────────────────────
PAGES.append(dict(
    path='/pt/salario-minimo-2027.html', shell='pt/calculadora-consumo-eletrico.html', lang='pt-PT', crumb='Portugal',
    title='Salário mínimo 2027 em Portugal: 970 € (previsto no OE2027)', h1='Salário mínimo nacional 2027: 970 €',
    desc='O Governo prevê no Orçamento do Estado para 2027 um salário mínimo de 970 € (hoje 920 €), mais 50 €. Valor anual em 14 meses: 13.580 €. Ainda falta o decreto-lei.',
    badge='🇵🇹 Verificado a 27/11/2026', sub='Valor previsto, quanto dá por ano e por hora.', must='id="ptH"',
    css='<style id="y7-css">' + BASE + '''
.pt-az{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.pt-tile{border-radius:12px;padding:16px;min-width:0;color:#1E3A8A;background-color:#F8FAFC;border:2px solid #1D4ED8;background-image:radial-gradient(circle at 0 0,transparent 18px,#DBEAFE 19px,#DBEAFE 21px,transparent 22px),radial-gradient(circle at 100% 100%,transparent 18px,#DBEAFE 19px,#DBEAFE 21px,transparent 22px)}
.pt-tile small{display:block;font-size:12px;letter-spacing:.1em;text-transform:uppercase}.pt-tile b{display:block;font-size:38px;line-height:1.1}.pt-tile p{margin:6px 0 0;font-size:14px;color:#334155}
.pt-tile.n{background-color:#1D4ED8;color:#fff;background-image:none}.pt-tile.n p{color:#DBEAFE}
.pt-calc{margin-top:14px;border:1px solid #E5E7EB;border-radius:12px;padding:14px}.pt-calc h2{font-size:17px;margin:0 0 8px}.pt-calc label{display:block;font-size:13px;font-weight:700}
.pt-calc input{display:block;width:100%;font:inherit;font-size:17px;padding:9px;border:1px solid #D1D5DB;border-radius:8px;margin-top:4px}.pt-r{margin-top:10px;font-size:16px;line-height:1.7}
@media(max-width:520px){.pt-az{grid-template-columns:minmax(0,1fr)}}
</style>''',
    app='''<section class="app y7" id="calc"><p class="ans">O relatório do <b>Orçamento do Estado para 2027</b> prevê um <b>salário mínimo nacional de 970 €</b> em 2027, mais <b>50 €</b> do que os <b>920 €</b> de 2026, em linha com o acordo de concertação social. O valor só fica oficial com o decreto-lei do Governo, normalmente publicado em dezembro.</p>
<div class="pt-az"><div class="pt-tile"><small>2026 · em vigor</small><b>920 €</b><p>12.880 € por ano (14 meses)</p></div><div class="pt-tile n"><small>2027 · previsto</small><b>970 €</b><p>13.580 € por ano (14 meses)</p></div></div>
<div class="pt-calc"><h2>Quanto dá por hora?</h2><label for="ptH">Horas por semana<input id="ptH" inputmode="decimal" value="40"></label><div class="pt-r" id="ptR"></div></div></section>''',
    js=r'''<script>
(function(){'use strict';const $=i=>document.getElementById(i);const N=s=>{const x=parseFloat(String(s).replace(',','.').replace(/[^0-9.]/g,''));return isFinite(x)?x:0};const E=x=>x.toLocaleString('pt-PT',{minimumFractionDigits:2,maximumFractionDigits:2})+' €';
function go(){const h=N($('ptH').value),m=h*52/12;$('ptR').innerHTML='2027: <b>'+E(970/m)+'</b> por hora<br>2026: '+E(920/m)+' por hora'}$('ptH').addEventListener('input',go);go()})();
</script>''',
    faq_h='Perguntas frequentes', src_h='Fontes (verificadas a 27/11/2026)',
    faq=[('Qual é o salário mínimo em 2027?', 'O Governo prevê 970 € no Orçamento do Estado para 2027. O valor final é fixado por decreto-lei, depois de ouvidos os parceiros sociais.'),
         ('Quanto aumenta o salário mínimo em 2027?', '50 € por mês face aos 920 € de 2026 (cerca de 5,4%).'),
         ('Quanto é o salário mínimo 2027 por ano?', '970 € × 14 meses = 13.580 € brutos.'),
         ('Os sindicatos pedem mais?', 'Sim. A CGTP pede 1.100 € e a UGT mais de 1.000 €; as confederações patronais opõem-se a rever a meta.')],
    extra='<h3 id="tbl">Salário mínimo 2026 e 2027</h3>' + table(['', '2026', '2027 (previsto)'], [['Mensal', '920 €', '970 €'], ['Anual (14 meses)', '12.880 €', '13.580 €'], ['Duodécimos (÷12)', '1.073,33 €', '1.131,67 €']]),
    src=[('DNoticias — Governo assume salário mínimo nos 970 euros no próximo ano (8/10/2026)', 'https://www.dnoticias.pt/2026/10/8/508265-governo-assume-salario-minimo-nos-970-euros-no-proximo-ano/'),
         ('WageIndicator — Portugal: Government sets 2027 minimum wage at €970 (31/10/2026)', 'https://wageindicator.org/ai/work/collective-bargaining-agreement/updates/2026/portugal-government-sets-2027-minimum-wage-at-970-october-31-2026/')],
    note='Valor de 2027 previsto, ainda sem decreto-lei publicado. Valores brutos.'))


if __name__ == '__main__':
    for c in PAGES:
        build(c)
