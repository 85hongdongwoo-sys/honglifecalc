"""JP: 新NISA 積立シミュレーション (/jp/nisa-simulator.html).
The original calc lives in the shared /assets/w2.js (data-page="jpNisa"). Its math is correct (月30万円・生涯1,800万円で頭打ち),
but it capped amounts silently and accepted fractional/negative input. This page switches data-page to "jpNisa2" (w2.js then
does nothing) and adds an inline calc with the same formula + notes when a cap is hit. Input ids unchanged: monthly, ret, years."""
import sys; sys.path.insert(0, '/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P = '/jp/nisa-simulator.html'

CALC = r'''<script>(function(){'use strict';
const C=window.C,S=C.s,$=id=>document.getElementById(id);
const num=id=>{const e=$(id);if(!e)return 0;const t=String(e.value).replace(/[^\d.\-]/g,'');const v=parseFloat(t);return isFinite(v)?v:0};
const m=x=>new Intl.NumberFormat('ja-JP',{style:'currency',currency:'JPY',maximumFractionDigits:0}).format(x);
const kv=rows=>'<div class="kv">'+rows.map(r=>`<div class="${r[2]||''}">${r[0]}</div><div class="${r[2]||''}">${r[1]}</div>`).join('')+'</div>';
const big=(l,v,s)=>`<div class="big"><span>${l}</span><b>${v}</b>${s?`<em>${s}</em>`:''}</div>`;
const bar=p=>{const t=p.reduce((s,x)=>s+Math.max(0,x[1]),0)||1;return '<div class="bar">'+p.map(x=>`<i style="width:${Math.max(0,x[1])/t*100}%;background:${x[2]}"></i>`).join('')+'</div><div class="legend">'+p.map(x=>`<span style="--c:${x[2]}">${x[0]} ${m(x[1])}</span>`).join('')+'</div>'};
const note=t=>`<p class="note">${t}</p>`;
const CAPM=300000,LIFE=18000000;
function calc(){
 const mo0=Math.max(0,num('monthly')),yrs=Math.max(0,Math.min(100,Math.round(num('years')))),r=num('ret')/100;
 const mr=Math.pow(1+r,1/12)-1,mo=Math.min(mo0,CAPM);let bal=0,inv=0,full=0;const rows=[];
 for(let y=1;y<=yrs;y++){for(let k=0;k<12;k++){const room=Math.min(mo,Math.max(0,LIFE-inv));bal=(bal+room)*(1+mr);inv+=room}
  if(!full&&inv>=LIFE)full=y;rows.push([y,inv,bal])}
 const gain=bal-inv,tax=Math.max(0,gain)*.20315;
 let h=big(S.final.replace('{y}',yrs),m(bal),`${S.invested} ${m(inv)} · ${S.profit} ${m(gain)}`);
 h+=kv([[S.invested,m(inv)],[S.profit,m(gain),gain>=0?'pos':'neg'],[S.taxSaved,m(tax),'pos'],[S.taxable,m(bal-tax)],['生涯の非課税保有限度額の残り',m(Math.max(0,LIFE-inv))+' / 1,800万円']]);
 h+=bar([[S.invested,inv,'#1F5FD1'],[S.profit,gain,'#0F8A5F']]);
 h+='<div class="scroll"><table class="tbl"><tr><th>'+S.year+'</th><th>'+S.invested+'</th><th>'+S.value+'</th></tr>'+rows.map(x=>`<tr><td>${x[0]}</td><td>${m(x[1])}</td><td>${m(x[2])}</td></tr>`).join('')+'</table></div>';
 if(mo0>CAPM)h+=note('毎月'+m(mo0)+'のうち、年間投資枠360万円（月30万円）を超える分は計算に入れていません。');
 if(full)h+=note(full+'年目に生涯の非課税保有限度額1,800万円に達します。その後は新しく買わず、持っている分の運用だけを続ける計算です。');
 $('out').innerHTML=h+note(S.n2);
}
const f=$('form');f.addEventListener('input',calc);f.addEventListener('change',calc);calc();
})();</script>'''


def nisa(mo, r, yrs):
    mr = (1 + r / 100) ** (1 / 12) - 1; bal = inv = 0; full = None
    for y in range(1, yrs + 1):
        for _ in range(12):
            room = min(mo, 300000, max(0, 18000000 - inv)); bal = (bal + room) * (1 + mr); inv += room
        if full is None and inv >= 18000000: full = y
    return bal, inv, full


y = lambda x: f"{round(x):,}円"
man = lambda x: f"約{round(x/10000):,}万円"
EX = [(10000, 30), (30000, 20), (50000, 20), (100000, 15), (300000, 5)]
ex_rows = []
for mo, yr in EX:
    b3, inv, _ = nisa(mo, 3, yr); b5, _, full = nisa(mo, 5, yr)
    ex_rows.append([f"{mo//10000}万円", f"{yr}年", man(inv), man(b3), man(b5), man((b5 - inv) * .20315)])
for r in ex_rows: print(r)
b, inv, full = nisa(50000, 5, 30); print('5万30年', b, inv, full)
b, inv, full = nisa(50000, 5, 20); print('default', b, inv)

fig = [
    ['つみたて投資枠', '年120万円', '長く積み立てるのに向く、国が決めた条件を満たす投資信託などを買う枠。'],
    ['成長投資枠', '年240万円', '上場株式や投資信託などを買う枠。まとめて買うこともできます。'],
    ['年間の合計', '年360万円（月にならすと30万円）', '2つの枠は同じ年に両方使えます（併用）。'],
    ['生涯の非課税保有限度額', '1,800万円（うち成長投資枠は1,200万円まで）', '一生でNISAの中に持てる金額の上限。買ったときの金額（簿価）で数えます。'],
    ['非課税で持てる期間', '無期限', '何年持っていても、利益に税金がかかりません。'],
    ['売ったときの枠', '翌年以降に復活（簿価の分）', '売った商品の買値の分だけ、次の年から枠がまた使えます。年間の上限は変わりません。'],
    ['使える人（2026年）', '1月1日時点で18歳以上、日本に住んでいる人', '口座は1人1つ。制度は2024年から恒久化（期限なし）。'],
    ['2027年1月から（未成年）', '0〜17歳もつみたて投資枠を利用可：年60万円・上限600万円', '成長投資枠は使えません。払出しは原則18歳から（12歳以降は一定の条件で可能）。'],
    ['課税口座の税率（参考）', '20.315%', '所得税15%＋復興特別所得税0.315%（所得税額の2.1%）＋住民税5%。NISAならこれが0円。'],
]

FAQ = [
    ("新NISAで毎月3万円を20年積み立てるといくら？",
     "年5%で回ると約1,222万円です。自分で入れたお金（元本）は720万円なので、増えた分は約502万円。課税口座なら約102万円の税金がかかるところ、NISAでは0円です。年3%なら約983万円です。"),
    ("毎月5万円だと何年で1,800万円の枠を使い切る？",
     "年60万円ずつなので、30年で1,800万円に届きます。年5%で30年なら評価額は約4,093万円です。月10万円なら15年、月30万円なら5年で使い切ります。"),
    ("年間投資枠の上限はいくら？",
     "つみたて投資枠が年120万円、成長投資枠が年240万円で、合わせて年360万円です。このシミュレーションでは毎月30万円を超える分は計算に入れません。"),
    ("生涯投資枠1,800万円は売ったら戻る？",
     "戻ります。売った商品の買値（簿価）の分だけ、翌年から枠が復活します。例：100万円で買った投資信託が150万円になって売っても、戻る枠は100万円です。"),
    ("NISAで損したらどうなる？",
     "NISA口座で売って出た損失は「ないもの」とみなされます。ほかの口座の利益と相殺（損益通算）したり、翌年以降に繰り越したりはできません。"),
    ("子どもも新NISAを使える？",
     "2026年は使えません。金融庁によると、2027年1月から0〜17歳もつみたて投資枠を使えるようになります。年60万円、上限600万円で、成長投資枠は使えません。"),
]

art = '''<h2 id="figures">新NISAのルール（2026年）</h2>
<p>NISA（ニーサ）は、投資で増えたお金に税金がかからない国の制度です。ふつうの口座（課税口座）なら、利益の約2割が税金になります。</p>
''' + table(['項目', '金額・ルール', 'どういう意味？'], fig) + '''
<h2 id="ex">毎月いくら積み立てると、いくらになる？</h2>
<p>このページの計算式で出した例です。毎月の初めに積み立てて、年3%または年5%で増え続けたとします。</p>
<div id="examples">''' + table(['毎月の積立', '期間', '元本', '年3%なら', '年5%なら', '非課税になる税額（年5%）'], ex_rows) + '''</div>
<ul><li><b>毎月3万円・20年・年5%</b>：元本720万円 → 約1,222万円。増えた約502万円に税金がかかりません。</li>
<li><b>毎月5万円・20年・年5%</b>（計算機の最初の値）：元本1,200万円 → 約2,037万円。</li>
<li><b>毎月30万円</b>は年360万円で上限ぴったり。5年で1,800万円の枠を使い切り、そのあとは運用だけになります。</li></ul>
<p class="note">年3%・年5%は計算のための例で、予想ではありません。投資信託の値段は下がることもあり、元本は保証されません。</p>
<h2 id="how">計算のしくみ</h2>
<p>例：毎月3万円、年5%なら、1か月で約0.41%増えます。1か月目は3万円が約30,122円に。2か月目はそこに3万円を足して、また0.41%増えます。これを毎月くり返します。</p>
<ul><li><b>月の利回り</b> = (1 + 年利)<sup>1/12</sup> − 1。年5%なら約0.407%。</li>
<li><b>評価額</b>：毎月「(残高 + 積立額) × (1 + 月の利回り)」をくり返した金額。</li>
<li><b>運用益</b> = 評価額 − 元本。<b>非課税になる税額</b> = 運用益 × 20.315%。</li>
<li><b>上限</b>：毎月の積立は30万円まで（年360万円）。元本が1,800万円に届いたら、それ以上は積み立てない計算です。</li></ul>
<p><b>元本</b>は自分で入れたお金の合計、<b>評価額</b>はそのとき売ったらいくらになるか、という意味です。</p>
<h2 id="tips">よくある勘違いとコツ</h2>
<ul><li><b>枠は簿価で数える</b>：1,800万円は「買った金額」の上限です。値上がりして3,000万円になっても問題ありません。</li>
<li><b>使わなかった年の枠は持ち越せない</b>：年360万円を使い切らなくても、翌年に足すことはできません。生涯の1,800万円は残ります。</li>
<li><b>損は相殺できない</b>：NISAの損失は他の口座の利益と相殺できません。値下がりしやすい商品ほど注意が必要です。</li>
<li><b>口座は1人1つ</b>：金融機関を変えるときは手続きが必要です。</li>
<li><b>「何%で回るか」は約束されていない</b>：年3%・5%など、いくつかの利回りで試してみましょう。</li></ul>
<h2 id="faq" style="margin-top:22px">よくある質問</h2>''' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in FAQ) + '''
<p class="note">出典（2026年11月28日確認）：<a href="https://www.fsa.go.jp/policy/nisa2/know/index.html" rel="nofollow">金融庁 NISA特設ウェブサイト「NISAを知る」</a>；<a href="https://www.fsa.go.jp/access/r7/270/270_03.pdf" rel="nofollow">金融庁 アクセスFSA第270号（令和8年度税制改正）</a>；<a href="https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1463.htm" rel="nofollow">国税庁 No.1463 株式等を譲渡したときの課税</a>；<a href="https://www.nta.go.jp/users/gensen/nisa/pdf/0019009-091.pdf" rel="nofollow">国税庁 NISA制度の概要（パンフレット）</a>。計算結果は概算で、投資の助言ではありません。</p>'''

out = build(P, '新NISAシミュレーション 2026｜毎月3万・5万円の積立は20年でいくら？',
            '新NISAの積立シミュレーション（2026年）。毎月の積立額・年利・期間から評価額と非課税になる税額を計算。年360万円・生涯1,800万円の上限、売却後の枠復活も解説。',
            art, FAQ)
s = open(out, encoding='utf-8').read()
s = s.replace('<body data-page="jpNisa">', '<body data-page="jpNisa2">', 1)
s = s.replace('<script src="https://honglifecalc.com/assets/w2.js"></script>', '<script src="https://honglifecalc.com/assets/w2.js"></script>' + CALC, 1)
assert 'jpNisa2' in s and "'use strict';\nconst C=window.C" in s
open(out, 'w', encoding='utf-8').write(s)
add_top(out, [('作成', 'Hong Life Calculators'), ('確認日', '2026年11月28日'), ('出典', '金融庁・国税庁')],
        [('form', '計算機'), ('figures', '新NISAのルール'), ('ex', '積立の計算例'), ('how', '計算のしくみ'), ('tips', 'コツと注意点'), ('faq', 'よくある質問')],
        'このページの内容', ('#examples', 'ja'))
print(out)
