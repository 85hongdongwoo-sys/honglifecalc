"""JP: 外干しカレンダー — 気象庁の週間天気予報（JSON）で外干しできる日を判定し、乾燥機の電気代の節約額を計算。
出典: 気象庁ホームページ（https://www.jma.go.jp/bosai/forecast/）の天気予報を加工して作成。ブラウザから直接取得（CORS 可、2026-11-24 確認）。
テンプレート: /jp/denkidai-keisan.html。出力: overlay/jp/sotoboshi-calendar.html"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from enrich_lib import ORIG, OUT, TBL_CSS, TOP_CSS, table, faq_html

PATH = '/jp/sotoboshi-calendar.html'
URL = 'https://honglifecalc.com' + PATH
TITLE = '外干しカレンダー｜週間天気で洗濯物を外に干せる日と乾燥機代の節約額【2026】'
H1 = '外干しカレンダー'
DESC = ('気象庁の週間天気予報から、この先7日間で洗濯物を外に干せる日を都道府県ごとに判定。'
        '乾燥機を使わずに済む回数と、電気代の節約額（週・年）を計算します。')
DATE_JA = '2026年11月24日'

CSS = '''<style id="sb-css">
.f small{display:block;color:var(--muted,#5B6B82);font-size:12.5px;margin-top:4px}
.sb-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:start}.sb-row .f{min-width:0}
.sb-live{display:inline-flex;align-items:baseline;gap:6px;font-size:12.5px;font-weight:700;color:#1f4f8a;background:#EAF1FB;border:1px solid #CFDDF3;border-radius:999px;padding:2px 10px;margin:0 0 10px;max-width:100%;flex-wrap:wrap}
.sb-week{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px;margin:4px 0 12px}
.sb-day{position:relative;border:1px solid #E3EAF4;border-radius:14px;padding:8px 4px 10px;text-align:center;background-color:#fff!important;min-width:0;animation:sbin .45s ease both}
@keyframes sbin{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.sb-day.ok{background-image:linear-gradient(180deg,#FFF8E1,#fff 60%);background-color:#FFF8E1!important;border-color:#F5D77A}
.sb-day.cl{background-image:linear-gradient(180deg,#F1F5F9,#fff 60%);background-color:#F8FAFC!important}
.sb-day.ng{background-image:linear-gradient(180deg,#E8F0FB,#fff 60%);background-color:#EEF4FC!important;border-color:#C9D8EE}
.sb-d{font-size:12px;color:#5B6B82;white-space:nowrap}.sb-d b{display:block;font-size:14px;color:#1d1d1f}
.sb-ic{font-size:30px;line-height:1.2;margin:4px 0 2px;display:block}
.sb-day.ok .sb-ic{animation:sbsun 6s linear infinite}@keyframes sbsun{to{transform:rotate(360deg)}}
.sb-pop{position:relative;width:44px;height:44px;margin:2px auto}
.sb-pop svg{width:44px;height:44px;display:block}.sb-pop span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#1f4f8a}
.sb-mark{display:inline-block;margin-top:4px;font-size:15px;font-weight:800;border-radius:999px;padding:1px 9px}
.sb-day.ok .sb-mark{background:#FDE68A;color:#7A4B00}.sb-day.cl .sb-mark{background:#E2E8F0;color:#334155}.sb-day.ng .sb-mark{background:#DBEAFE;color:#1E3A8A}
.sb-t{font-size:11.5px;color:#3a3a3c;margin-top:4px;white-space:nowrap}.sb-t .mx{color:#DC2626}.sb-t .mn{color:#2563EB}
.sb-sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:6px 0 10px}
.sb-sum div{background:#F5F8FC;border:1px solid #E3EAF4;border-radius:12px;padding:9px 11px;min-width:0}
.sb-sum b{display:block;font-size:20px;color:#12305C;overflow-wrap:anywhere}.sb-sum span{font-size:12px;color:#5B6B82}
.sb-sum .hi{background:#FFF8E1;border-color:#F5D77A}.sb-sum .hi b{color:#7A4B00}
.sb-leg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:#5B6B82;margin:2px 0 4px}
.sb-err{background:#FFF4E5;border:1px solid #F5D9A8;border-radius:10px;padding:10px 12px;font-size:14px}
.sb-src{font-size:12.5px;color:#6e6e73;margin-top:10px}
@media(max-width:640px){.sb-row{grid-template-columns:1fr}.sb-sum{grid-template-columns:1fr}
 .sb-week{grid-template-columns:repeat(4,minmax(0,1fr))}.sb-ic{font-size:26px}}
@media(prefers-reduced-motion:reduce){.sb-day,.sb-day.ok .sb-ic{animation:none}}
</style>'''

FORM = '''<form class="card" id="form" onsubmit="return false"><h2>地域と洗濯の条件</h2>
<label class="f"><span>都道府県（予報区）</span><select id="pref"><option value="130000">東京都</option></select><small>気象庁の予報区ごとの週間天気予報を使います。</small></label>
<label class="f"><span>地域</span><select id="sub"></select></label>
<div class="sb-row"><label class="f"><span>1週間の洗濯回数</span><input id="wash" inputmode="decimal" value="5"></label>
<label class="f"><span>乾燥機1回の消費電力量（kWh）</span><input id="kwh" inputmode="decimal" value="1.5"><small>取扱説明書やカタログの「消費電力量（洗濯〜乾燥）」を入れてください。</small></label></div>
<label class="f"><span>電気料金の単価（円/kWh）</span><input id="yen" inputmode="decimal" value="31"><small>検針票やご契約プランの単価（税込）。</small></label>
</form><section class="card" id="out" aria-live="polite"><p>気象庁の予報を読み込んでいます…</p></section>'''

JS = r'''<script>
(function(){'use strict';
const $=id=>document.getElementById(id);
const num=id=>{const v=parseFloat(String($(id).value).replace(/[,，\s]/g,'').replace('．','.'));return isFinite(v)?v:0};
const yen=x=>Math.round(x).toLocaleString('ja-JP')+'円';
const BASE='https://www.jma.go.jp/bosai/';
const WD=['日','月','火','水','木','金','土'];
let areas=null,fc=null,busy=0;
function cat(code){const c=String(code||'')[0];return c==='1'?'sun':c==='2'?'cloud':c==='3'?'rain':c==='4'?'snow':'cloud'}
const ICON={sun:'☀️',cloud:'☁️',rain:'☔',snow:'⛄'};
const LABEL={sun:'晴れ',cloud:'くもり',rain:'雨',snow:'雪'};
function judge(c,pop){if(c==='rain'||c==='snow'||pop>=50)return['ng','×','部屋干し'];if(pop<=20&&c==='sun')return['ok','◎','外干し日和'];if(pop<=20)return['cl','○','外干しOK'];return['cl','△','様子見']}
function ring(p){const r=18,L=2*Math.PI*r,v=Math.max(0,Math.min(100,p));return '<svg viewBox="0 0 44 44"><circle cx="22" cy="22" r="'+r+'" fill="none" stroke="#E3EAF4" stroke-width="5"/><circle cx="22" cy="22" r="'+r+'" fill="none" stroke="#3B82F6" stroke-width="5" stroke-linecap="round" stroke-dasharray="'+(L*v/100).toFixed(1)+' '+L.toFixed(1)+'" transform="rotate(-90 22 22)"/></svg>'}
async function loadAreas(){areas=await fetch(BASE+'common/const/area.json').then(r=>r.json());
 const offs=Object.entries(areas.offices).sort((a,b)=>a[0]<b[0]?-1:1);
 $('pref').innerHTML=offs.map(([k,v])=>'<option value="'+k+'"'+(k==='130000'?' selected':'')+'>'+v.name+'</option>').join('')}
async function loadFc(){const id=$('pref').value;fc=await fetch(BASE+'forecast/data/forecast/'+id+'.json').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json()});
 const w=fc[1]&&fc[1].timeSeries&&fc[1].timeSeries[0];if(!w)throw new Error('週間予報なし');
 $('sub').innerHTML=w.areas.map((a,i)=>'<option value="'+i+'">'+a.area.name+'</option>').join('');$('sub').disabled=w.areas.length<2}
function todayPop(sub){const s=fc[0].timeSeries.find(t=>t.areas[0].pops);if(!s)return null;const a=s.areas[Math.min(sub,s.areas.length-1)];const d=(fc[1].timeSeries[0].timeDefines[0]||'').slice(0,10);
 let m=null;s.timeDefines.forEach((t,i)=>{if(t.slice(0,10)===d&&a.pops[i]!==''){m=Math.max(m==null?0:m,+a.pops[i])}});return m}
function draw(){if(!fc)return;const sub=+$('sub').value||0,W=fc[1].timeSeries[0],A=W.areas[sub],T=fc[1].timeSeries[1],TA=T&&T.areas[Math.min(sub,T.areas.length-1)];
 const wash=Math.max(0,num('wash')),kwh=Math.max(0,num('kwh')),y=Math.max(0,num('yen'));
 const days=W.timeDefines.map((t,i)=>{let pop=A.pops[i]===''?todayPop(sub):+A.pops[i];if(pop==null)pop=0;const c=cat(A.weatherCodes[i]);const j=judge(c,pop);
  return{d:new Date(t),c,pop,j,mx:TA&&TA.tempsMax[i]!==''?+TA.tempsMax[i]:null,mn:TA&&TA.tempsMin[i]!==''?+TA.tempsMin[i]:null}});
 const ok=days.filter(x=>x.j[0]!=='ng'&&x.j[1]!=='△').length,good=days.filter(x=>x.j[0]==='ok').length;
 const per=wash/7,saved=per*ok,yenWeek=saved*kwh*y,yenYear=yenWeek*52;
 let h='<span class="sb-live">☁️ 気象庁 週間天気予報 · '+A.area.name+' · 発表 '+new Date(fc[1].reportDatetime).toLocaleString('ja-JP',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'})+'</span>';
 h+='<div class="sb-week">'+days.map((x,i)=>'<div class="sb-day '+x.j[0]+'" style="animation-delay:'+(i*70)+'ms"><div class="sb-d"><b>'+(x.d.getMonth()+1)+'/'+x.d.getDate()+'</b>('+WD[x.d.getDay()]+')</div><span class="sb-ic" aria-label="'+LABEL[x.c]+'">'+ICON[x.c]+'</span><div class="sb-pop" title="降水確率">'+ring(x.pop)+'<span>'+x.pop+'%</span></div><span class="sb-mark">'+x.j[1]+'</span><div class="sb-t">'+(x.mx!=null?'<span class="mx">'+x.mx+'°</span>/<span class="mn">'+x.mn+'°</span>':'&nbsp;')+'</div></div>').join('')+'</div>';
 h+='<div class="sb-leg"><span>◎ 晴れ・降水確率20%以下</span><span>○ くもり・20%以下</span><span>△ 30〜40%</span><span>× 雨・雪・50%以上</span><span>円 = 降水確率</span></div>';
 h+='<div class="sb-sum"><div class="hi"><span>外に干せる日（◎○）</span><b>7日中 '+ok+'日</b><span>うち外干し日和（◎）'+good+'日</span></div>'
  +'<div><span>乾燥機を使わずに済む回数</span><b>約 '+saved.toLocaleString('ja-JP',{maximumFractionDigits:1})+'回</b><span>週'+wash+'回 × '+ok+'/7日</span></div>'
  +'<div class="hi"><span>今週の節約額</span><b>'+yen(yenWeek)+'</b><span>毎週この天気なら年 '+yen(yenYear)+'</span></div></div>';
 h+='<p class="sb-src">出典：気象庁ホームページ（週間天気予報）を加工して作成。外干しの判定は降水確率と天気の種類から当サイトが計算したもので、気象庁の発表ではありません。節約額 = 回数 × '+kwh+' kWh × '+y+' 円。</p>';
 $('out').innerHTML=h}
async function run(newPref){const id=++busy;try{if(!areas)await loadAreas();if(newPref||!fc)await loadFc();if(id===busy)draw()}catch(e){if(id===busy)$('out').innerHTML='<p class="sb-err">気象庁の予報を読み込めませんでした（'+e.message+'）。少し時間をおいて再度お試しください。</p>'}}
$('pref').addEventListener('change',()=>run(true));$('sub').addEventListener('change',draw);
['wash','kwh','yen'].forEach(id=>$(id).addEventListener('input',draw));
run(true);
})();
</script>'''

FAQ = [
 ("外干しの判定はどう決めていますか？",
  "気象庁の週間天気予報の「天気」と「降水確率」から判定しています。晴れで降水確率20%以下は◎、くもりで20%以下は○、30〜40%は△、雨・雪の予報か50%以上は×です。当サイトの目安で、気象庁の発表ではありません。"),
 ("予報はいつ更新されますか？",
  "気象庁の週間天気予報は毎日11時と17時ごろに発表されます。このページは開くたびに最新の予報を読み込みます。"),
 ("乾燥機の消費電力量はどこで分かりますか？",
  "取扱説明書やメーカーのカタログの仕様表にある「消費電力量（洗濯〜乾燥）」を見てください。ヒートポンプ式とヒーター式で大きく違います。"),
 ("電気料金の単価は？",
  "検針票（電気ご使用量のお知らせ）やご契約プランの料金表にある1kWhあたりの単価（税込）を入れてください。初期値の31円は計算例です。"),
 ("花粉や黄砂の日は？",
  "この判定は天気と降水確率だけを見ています。花粉・黄砂・PM2.5が気になる日は、晴れでも部屋干しを選んでください。"),
]

ART = '''<p><b>ひと目でわかる：</b>都道府県を選ぶと、気象庁の週間天気予報から<b>この先7日間の外干しできる日</b>を◎○△×で表示し、乾燥機を使わずに済む回数と<b>電気代の節約額</b>を計算します。</p>
<h2 id="how">計算のしかた</h2>
<ul><li><b>外に干せる日</b> = 判定が◎か○の日</li>
<li><b>乾燥機を使わずに済む回数</b> = 1週間の洗濯回数 ×（外に干せる日 ÷ 7）</li>
<li><b>節約額</b> = 回数 × 乾燥機1回の消費電力量（kWh）× 電気料金の単価（円/kWh）</li>
<li><b>1年の節約額</b> = 週の節約額 × 52（毎週同じ天気だった場合の目安）</li></ul>
<h3 id="rei">計算例</h3>
''' + table(['条件', '計算', '結果'], [
    ['週5回洗濯・外干しできる日 4日', '5 × 4 ÷ 7', '約2.9回'],
    ['乾燥機 1.5 kWh・単価 31円', '2.9 × 1.5 × 31', '約133円／週'],
    ['同じ条件が1年続くと', '133円 × 52', '約6,900円／年'],
    ['乾燥機 3.0 kWh（ヒーター式の例）', '2.9 × 3.0 × 31', '約266円／週'],
]) + '''
<h3 id="hantei">判定の基準</h3>
''' + table(['判定', '条件', 'おすすめ'], [
    ['◎ 外干し日和', '晴れ、降水確率20%以下', '朝から外に干す'],
    ['○ 外干しOK', 'くもり、降水確率20%以下', '乾きにくいので風通しよく'],
    ['△ 様子見', '降水確率30〜40%', '取り込める日に。部屋干しも用意'],
    ['× 部屋干し', '雨・雪の予報、または降水確率50%以上', '部屋干しか乾燥機'],
]) + '''
<h3>上手に外干しするコツ</h3>
<ul><li>午前中に干して、15時ごろまでに取り込むと湿気を吸いにくくなります。</li>
<li>厚手のものは外側、薄手は内側に干すと風が通ります。</li>
<li>冬は気温が低くても、晴れて風があれば乾きます。</li></ul>
''' + faq_html(FAQ, heading='よくある質問').replace('<h2 style="margin-top:22px">よくある質問</h2>', '<h2 id="faq" style="margin-top:22px">よくある質問</h2>') + f'''
<p class="note">出典（{DATE_JA}確認）：<a href="https://www.jma.go.jp/bosai/forecast/" rel="nofollow">気象庁ホームページ「天気予報」（週間天気予報）</a>を加工して作成。利用条件：<a href="https://www.jma.go.jp/jma/kishou/info/coment.html" rel="nofollow">気象庁ホームページについて</a>。関連：<a href="/jp/denkidai-keisan.html">電気代計算</a>。</p>'''

TOC = [('form', '計算ツール'), ('how', '計算のしかた'), ('rei', '計算例'), ('hantei', '判定の基準'), ('faq', 'よくある質問')]


def main():
    s = open(os.path.join(ORIG, 'jp/denkidai-keisan.html'), encoding='utf-8').read()
    old = 'https://honglifecalc.com/jp/denkidai-keisan.html'
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, s, count=1)
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + H1, s, count=1)
    s = s.replace(old, URL)
    assert old not in s
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": H1, "url": URL, "description": DESC,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "ja-JP",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Hong Life", "item": "https://honglifecalc.com/"},
              {"@type": "ListItem", "position": 2, "name": "計算ツール一覧", "item": "https://honglifecalc.com/jp/"},
              {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld)
                  + CSS + TOP_CSS + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', '<header class="hero"><div class="in"><span class="year">🇯🇵 気象庁の予報で毎日更新</span>'
               f'<h1>{H1}</h1><p>この先7日間、洗濯物を外に干せる日はいつ？乾燥機の電気代はいくら浮く？</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: '<section class="app">' + FORM + '</section>', s, count=1, flags=re.S)
    top = (f'<!--hl:deep--><div class="hl-by"><span>作成 <b>Hong Life 計算ツール</b></span><span>確認日 <b>{DATE_JA}</b></span>'
           '<span>データ <b>気象庁（加工して作成）</b></span></div><details class="card hl-toc" open><summary>目次</summary><ol>'
           + ''.join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC) + '</ol></details>')
    s = s.replace('<section class="app">', top + '<section class="app">', 1)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + TBL_CSS + ART + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", lambda m: JS, s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    assert 'forecast/data/forecast/' in s and 'id="pref"' in s and 'id="hantei"' in s and 'hl-viz' not in s
    out = os.path.join(OUT, PATH.lstrip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)
    print(out, len(s))


main()
