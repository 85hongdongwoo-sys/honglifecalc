"""새 페이지: 달과 나의 거리 실시간 계산기 (한국어).
계산: astronomy-engine 2.1.19 (MIT, Don Cross) — 브라우저에서 내 위치 기준(지형 중심) 달 거리를 매 순간 계산.
달 사진: NASA Scientific Visualization Studio 'Moon Phase and Libration, 2026' (SVS 5587) 시간별 프레임.
우주정거장 위치: wheretheiss.at 공개 API. 표의 보름달·근지점 숫자는 같은 라이브러리로 계산해 넣음 (2026-11-23).
템플릿 = /ko/clock.html (머리·광고·상단·푸터 유지). overlay/ko/moon-distance.html 을 쓴다."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enrich_lib import ORIG, OUT

SLUG = 'moon-distance.html'
URL = 'https://honglifecalc.com/ko/' + SLUG
TITLE = '달까지 거리 실시간 – 지금 달과 나의 거리, 보름달·슈퍼문 날짜 (2026~2027)'
DESC = ('지금 이 순간 내 위치에서 달까지 몇 km인지 초마다 계산해요. NASA 달 사진, 오늘 달 뜨는 시간, '
        '다음 보름달·슈퍼문, 국제우주정거장(ISS)까지 거리와 생중계까지 한 페이지에서.')
CHECKED = '2026년 11월 23일'

# astronomy-engine 으로 미리 계산한 값 (한국 시간)
FULL = [('2026-01-03', 362301), ('2026-02-02', 371376), ('2026-03-03', 382603), ('2026-04-02', 393585),
        ('2026-05-02', 401990), ('2026-05-31', 406126), ('2026-06-30', 405245), ('2026-07-29', 399605),
        ('2026-08-28', 390385), ('2026-09-27', 379423), ('2026-10-26', 368859), ('2026-11-24', 360754),
        ('2026-12-24', 356729), ('2027-01-22', 357635), ('2027-02-21', 363296), ('2027-03-22', 372518),
        ('2027-04-21', 383421), ('2027-05-20', 393893), ('2027-06-19', 401943), ('2027-07-19', 405968),
        ('2027-08-17', 405069), ('2027-09-16', 399341), ('2027-10-15', 389926), ('2027-11-14', 378754),
        ('2027-12-14', 368131)]
APS = [('근지점', '2026-11-26 06:02', 359335), ('원지점', '2026-12-11 15:44', 406407), ('근지점', '2026-12-24 17:32', 356641),
       ('원지점', '2027-01-07 17:08', 406597), ('근지점', '2027-01-22 06:46', 357273), ('원지점', '2027-02-03 22:31', 406178),
       ('근지점', '2027-02-19 16:30', 361004)]
y26 = [f for f in FULL if f[0].startswith('2026')]
near26, far26 = min(y26, key=lambda f: f[1]), max(y26, key=lambda f: f[1])
assert near26 == ('2026-12-24', 356729) and far26 == ('2026-05-31', 406126)

def kdate(s):
    y, m, d = s[:10].split('-')
    return f'{y}년 {int(m)}월 {int(d)}일' + (s[10:] and ' ' + s[11:16])

def tag(km):
    return '슈퍼문' if km < 360000 else '가까움' if km < 368000 else '미니문' if km > 400000 else ''

def tbl(head, rows, cls='mt'):
    return (f'<div class="tw"><table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>' +
            ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')

full_t = tbl(['보름달 (한국 날짜)', '지구 중심~달 거리', '비고'],
             [[kdate(d), f'{km:,} km', tag(km)] for d, km in FULL])
aps_t = tbl(['구분', '시각 (한국 시간)', '거리'], [[k, kdate(t), f'{km:,} km'] for k, t, km in APS])

FAQ = [
    ('달까지 거리는 몇 km예요?', '평균 약 38만 4,400km예요. 달 궤도가 타원이라 가장 가까울 때(근지점) 약 35만 6천km, 가장 멀 때(원지점) 약 40만 6천km까지 바뀌어요. 위 계산기는 지금 이 순간 내 위치에서의 거리를 초마다 보여 줘요.'),
    ('2026년 슈퍼문은 언제예요?', f'2026년 보름달 중 가장 가까운 건 12월 24일(크리스마스 이브) 보름달로 지구 중심에서 약 {near26[1]:,}km예요. 가장 먼 보름달은 5월 31일(약 {far26[1]:,}km)이었어요. 2027년 1월 22일 보름달도 약 357,635km로 가까워요.'),
    ('달까지 빛은 몇 초 걸려요?', '약 1.2~1.4초예요. 빛의 속도(초속 299,792km)로 평균 거리 38만 4,400km를 가면 약 1.28초가 걸려요. 계산기의 “빛으로” 숫자가 지금 거리 기준 값이에요.'),
    ('왜 내 위치에 따라 거리가 달라요?', '지구 반지름이 약 6,371km라서, 달이 머리 위에 있을 때는 지구 중심보다 최대 약 6천km 더 가깝고, 달이 지평선 아래 있을 때는 그만큼 멀어요. 그래서 같은 순간이라도 서울과 뉴욕의 달 거리는 수천 km 차이가 나요.'),
    ('달은 지구에서 멀어지고 있나요?', '네. 아폴로 우주인이 달에 둔 반사경으로 레이저를 쏘아 재 보면, 달은 1년에 약 3.8cm씩 지구에서 멀어지고 있어요.'),
    ('국제우주정거장(ISS)은 얼마나 멀어요?', '지상 약 400km 높이에서 초속 약 7.7km로 지구를 90분에 한 바퀴 돌아요. 그래서 내 위치에서의 거리는 400km(머리 위)부터 1만km 넘게(지구 반대편)까지 계속 바뀌어요.'),
    ('이 계산은 얼마나 정확해요?', '달 거리는 천문 계산 라이브러리(astronomy-engine)로 브라우저에서 직접 계산하며, 오차는 보통 수 km 이내예요. 위치를 허용하지 않으면 서울시청 기준으로 계산해요. 위치는 화면 계산에만 쓰고 저장하지 않아요.'),
]
faq_h = '<h2 id="faq">자주 묻는 질문</h2>' + ''.join(f'<h3>{q}</h3><p>{a}</p>' for q, a in FAQ)

CSS = '''<style>
.mn-hero{display:grid;grid-template-columns:minmax(0,300px) 1fr;gap:22px;align-items:center}
.mn-img{position:relative;aspect-ratio:1;border-radius:50%;overflow:hidden;background:#000;box-shadow:0 0 60px rgba(200,210,255,.12)}
.mn-img img,.mn-img canvas{width:100%;height:100%;display:block;object-fit:cover}
.mn-big{font:800 clamp(30px,7vw,54px)/1.1 var(--mono);letter-spacing:-.02em;color:#1d2a44;font-variant-numeric:tabular-nums;word-break:keep-all}
.mn-big small{font-size:.42em;color:var(--muted);margin-left:6px}
.mn-lab{color:var(--muted);font-size:13px;margin:0 0 4px}
.mn-cmp{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0;padding:0;list-style:none}
.mn-cmp li{background:var(--glass2);border:1px solid var(--line);border-radius:10px;padding:6px 10px;font-size:13px}
.mn-cmp b{color:#1d2a44;font-variant-numeric:tabular-nums}
.mn-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}
.mn-grid div{background:var(--glass);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.mn-grid span{display:block;color:var(--muted);font-size:12px}.mn-grid b{display:block;color:#1d2a44;font-size:16px;font-variant-numeric:tabular-nums;word-break:keep-all}
.mn-loc{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:12px;font-size:13px;color:var(--muted)}
.mn-vid{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#000;margin-top:12px}
.mn-vid iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.mn-src{font-size:12px;color:var(--muted);margin-top:8px}
.tw{overflow-x:auto;margin:10px 0}
table.mt{width:100%;border-collapse:collapse;font-size:14px}
table.mt th,table.mt td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}
table.mt th{color:#5B6B82;font-weight:700}table.mt td{color:#1d2a44}
table.mt td:nth-child(2){font-variant-numeric:tabular-nums}
.mn-ans{background:rgba(110,231,249,.08);border:1px solid rgba(110,231,249,.25);border-radius:12px;padding:12px 14px;line-height:1.65}
@media(max-width:420px){table.mt th,table.mt td{white-space:normal;padding:7px 6px;font-size:13px}table.mt td:nth-child(2){white-space:nowrap}}
@media(max-width:640px){.mn-hero{grid-template-columns:1fr}.mn-img{max-width:240px;margin:0 auto}}
</style>'''

MAIN = f'''<main>
<span class="eyebrow">● Live · 초마다 다시 계산</span>
<h1>지금 <em>달과 나의 거리</em></h1>
<p class="sub">내가 서 있는 곳에서 달까지 몇 km인지 매 순간 계산해요. NASA가 공개한 이 시각의 달 사진과 함께 보세요.</p>

<section class="card" id="moon">
 <div class="mn-hero">
  <div class="mn-img" id="mnImgBox"><img id="mnImg" alt="지금 이 시각의 달 모습 (NASA)" width="730" height="730" hidden><canvas id="mnCv" width="600" height="600" aria-label="지금 달의 모양"></canvas></div>
  <div>
   <p class="mn-lab" id="mnHere">서울시청 기준</p>
   <div class="mn-big" id="mnKm">계산 중…</div>
   <ul class="mn-cmp">
    <li>빛으로 <b id="mnLight">-</b></li>
    <li>시속 100km 자동차로 <b id="mnCar">-</b></li>
    <li>비행기(시속 900km)로 <b id="mnPlane">-</b></li>
    <li>걸어서(시속 4km) <b id="mnWalk">-</b></li>
   </ul>
   <div class="mn-loc"><button class="btn sm" id="mnGeo">📍 내 위치로 계산</button><span>위치는 이 화면 계산에만 쓰고 저장하지 않아요.</span></div>
  </div>
 </div>
 <div class="mn-grid">
  <div><span>지금 달 모양</span><b id="mnPhase">-</b></div>
  <div><span>밝게 보이는 부분</span><b id="mnIll">-</b></div>
  <div><span>오늘 달 뜨는 시간</span><b id="mnRise">-</b></div>
  <div><span>오늘 달 지는 시간</span><b id="mnSet">-</b></div>
  <div><span>다음 보름달</span><b id="mnFull">-</b></div>
  <div><span>다음 근지점 (가장 가까울 때)</span><b id="mnPeri">-</b></div>
 </div>
 <p class="mn-src" id="mnCredit">달 사진: NASA Scientific Visualization Studio (매시간 달 모습). 거리 계산: astronomy-engine.</p>
</section>

<section class="card" id="iss">
 <h2><span class="ic">🛰️</span>국제우주정거장(ISS)과 나의 거리</h2>
 <p>지구 위 약 400km를 초속 7.7km로 도는 우주정거장이 지금 어디에 있는지, 내 위치에서 얼마나 먼지 5초마다 새로 가져와요.</p>
 <div class="mn-grid">
  <div><span>나와 ISS 사이 거리</span><b id="isKm">-</b></div>
  <div><span>ISS 높이</span><b id="isAlt">-</b></div>
  <div><span>속도</span><b id="isVel">-</b></div>
  <div><span>지금 아래 지점</span><b id="isPos">-</b></div>
 </div>
 <div class="row" style="margin-top:12px"><button class="btn pri" id="isGo">우주정거장 위치 불러오기</button><button class="btn" id="isLive">🎥 NASA 생중계 보기</button></div>
 <div class="mn-vid" id="isVid" hidden></div>
 <p class="mn-src">위치: wheretheiss.at 공개 자료. 생중계: NASA 공식 유튜브 (NASA가 방송 중일 때만 나와요. 우주정거장이 지구 밤쪽을 지날 때는 화면이 어두워요).</p>
</section>

<section class="card" id="far">
 <h2><span class="ic">🪐</span>태양·화성까지 지금 거리</h2>
 <div class="mn-grid">
  <div><span>태양까지</span><b id="suKm">-</b></div>
  <div><span>화성까지</span><b id="maKm">-</b></div>
  <div><span>화성까지 빛으로</span><b id="maLt">-</b></div>
 </div>
</section>

<article class="card help" id="guide">
<p class="mn-ans"><b>한 줄 답 (2026년):</b> 달까지 거리는 <b>평균 약 38만 4,400km</b>이고, 가까울 때 약 35만 6천km, 멀 때 약 40만 6천km예요. 2026년 가장 가까운 보름달은 <b>12월 24일</b>(약 {near26[1]:,}km)이에요.</p>
<h2 id="why">달까지 거리가 매일 바뀌는 이유</h2>
<p>달은 지구 둘레를 동그라미가 아니라 살짝 찌그러진 타원으로 돌아요. 그래서 약 27.5일마다 한 번 가장 가까운 <b>근지점</b>, 가장 먼 <b>원지점</b>을 지나요. 그 차이는 5만km 가까이 돼요.</p>
<p>여기에 지구 자전이 더해져요. 지구 반지름이 약 6,371km라서, 달이 머리 위에 있을 때는 지구 중심 기준 거리보다 최대 약 6천km 가깝고, 달이 지면 그만큼 멀어져요. 위 계산기가 <b>내 위치 기준</b>으로 계산하는 이유예요.</p>
<h2 id="full">보름달 날짜별 거리 (2026~2027년, 한국 날짜)</h2>
<p>보름달이 근지점 근처에서 뜨면 크고 밝게 보여서 흔히 <b>슈퍼문</b>이라고 불러요. 반대로 원지점 근처 보름달은 <b>미니문</b>이라고 해요. 거리는 지구 중심에서 달 중심까지예요.</p>
{full_t}
<h2 id="aps">다가오는 근지점·원지점</h2>
{aps_t}
<h2 id="cmp">달까지 거리, 이렇게 비교해 보세요</h2>
<ul>
<li><b>빛:</b> 약 1.28초. 달에서 보낸 신호가 지구에 오는 시간이에요.</li>
<li><b>자동차(시속 100km):</b> 쉬지 않고 약 160일.</li>
<li><b>비행기(시속 900km):</b> 약 17.8일.</li>
<li><b>아폴로 11호:</b> 1969년 7월 16일 발사해 3일 뒤 달 궤도에 들어갔어요.</li>
<li><b>지구 30개:</b> 지구 지름(약 1만 2,742km)을 30번 늘어놓으면 달까지 거리와 비슷해요.</li>
</ul>
{faq_h}
<p class="mn-src">출처와 계산 (확인 {CHECKED}): 달 사진 – <a href="https://svs.gsfc.nasa.gov/5587/" rel="nofollow">NASA Scientific Visualization Studio, Moon Phase and Libration, 2026</a>; 거리·위상·뜨고 지는 시간 – <a href="https://github.com/cosinekitty/astronomy" rel="nofollow">astronomy-engine</a>(MIT 라이선스)로 계산; 우주정거장 위치 – <a href="https://wheretheiss.at/w/developer" rel="nofollow">wheretheiss.at API</a>; 평균 거리와 해마다 멀어지는 거리 – NASA. 표의 날짜·거리는 같은 계산으로 미리 구한 값이에요.</p>
</article>
</main>'''

JS = r'''<script src="/assets/astronomy-2.1.19.min.js"></script>
<script>
(function(){'use strict';
var $=function(i){return document.getElementById(i)},A=window.Astronomy;if(!A)return;
var KM=A.KM_PER_AU,obs=new A.Observer(37.5665,126.978,30),lat=37.5665,lon=126.978;
function f(n,d){return n.toLocaleString('ko-KR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0})}
function kst(dt){var k=new Date(dt.getTime()+9*3600e3);return (k.getUTCMonth()+1)+'월 '+k.getUTCDate()+'일 '+String(k.getUTCHours()).padStart(2,'0')+':'+String(k.getUTCMinutes()).padStart(2,'0')}
function hm(dt){var k=new Date(dt.getTime()+9*3600e3);return String(k.getUTCHours()).padStart(2,'0')+':'+String(k.getUTCMinutes()).padStart(2,'0')}
function dur(h){if(h<48)return f(h,1)+'시간';var d=h/24;if(d<730)return f(d,1)+'일';return f(d/365.25,1)+'년'}
function pname(p){if(p<7||p>=353)return '삭 (안 보여요)';if(p<83)return '초승달 → 차오르는 중';if(p<97)return '상현달 (반달)';if(p<173)return '보름 전 차오르는 달';if(p<187)return '보름달';if(p<263)return '보름 지나 기우는 달';if(p<277)return '하현달 (반달)';return '그믐달 → 기우는 중'}
function moon(){var t=new Date(),km=A.Equator(A.Body.Moon,t,obs,true,true).dist*KM;
 $('mnKm').innerHTML=f(km,1)+'<small>km</small>';
 $('mnLight').textContent=f(km/299792.458,3)+'초';$('mnCar').textContent=dur(km/100);$('mnPlane').textContent=dur(km/900);$('mnWalk').textContent=dur(km/4)}
function draw(p){var c=$('mnCv'),x=c.getContext('2d'),w=c.width,r=w/2-8,cx=w/2,cy=w/2;x.clearRect(0,0,w,w);
 x.fillStyle='#16181f';x.beginPath();x.arc(cx,cy,r,0,7);x.fill();
 var ph=p*Math.PI/180,k=Math.cos(ph),wax=p<180;x.fillStyle='#e9e6dc';x.beginPath();
 x.arc(cx,cy,r,-Math.PI/2,Math.PI/2,!wax);x.ellipse(cx,cy,Math.abs(k)*r,r,0,Math.PI/2,-Math.PI/2,(wax?k>0:k<0));x.fill()}
function slow(){var t=new Date(),p=A.MoonPhase(t),il=A.Illumination(A.Body.Moon,t).phase_fraction;
 $('mnPhase').textContent=pname(p);$('mnIll').textContent=f(il*100,1)+'%';draw(p);
 var y0=Date.UTC(2026,0,1),fr=Math.floor((t-y0)/3600e3)+1,img=$('mnImg');
 if(fr>=1&&fr<=8760){var u='https://svs.gsfc.nasa.gov/vis/a000000/a005500/a005587/frames/730x730_1x1_30p/moon.'+String(fr).padStart(4,'0')+'.jpg';
  if(img.dataset.u!==u){img.dataset.u=u;img.onload=function(){img.hidden=false;$('mnCv').hidden=true};img.onerror=function(){img.hidden=true;$('mnCv').hidden=false};img.src=u}}
 var k=new Date(t.getTime()+9*3600e3),d0=new Date(Date.UTC(k.getUTCFullYear(),k.getUTCMonth(),k.getUTCDate())-9*3600e3);
 var r=A.SearchRiseSet(A.Body.Moon,obs,+1,d0,1),s=A.SearchRiseSet(A.Body.Moon,obs,-1,d0,1);
 $('mnRise').textContent=r?hm(r.date):'오늘은 안 떠요';$('mnSet').textContent=s?hm(s.date):'오늘은 안 져요';
 var fm=A.SearchMoonPhase(180,t,40);$('mnFull').textContent=fm?kst(fm.date):'-';
 var ap=A.SearchLunarApsis(t);while(ap.kind!==0)ap=A.NextLunarApsis(ap);$('mnPeri').textContent=kst(ap.time.date)+' · '+f(ap.dist_km)+'km';
 $('suKm').textContent=f(A.GeoVector(A.Body.Sun,t,true).Length()*KM)+' km';
 var mk=A.GeoVector(A.Body.Mars,t,true).Length()*KM;$('maKm').textContent=f(mk)+' km';$('maLt').textContent=f(mk/299792.458/60,1)+'분'}
$('mnGeo').addEventListener('click',function(){if(!navigator.geolocation){$('mnHere').textContent='이 기기는 위치를 쓸 수 없어 서울시청 기준이에요';return}
 $('mnHere').textContent='위치 확인 중…';navigator.geolocation.getCurrentPosition(function(p){lat=p.coords.latitude;lon=p.coords.longitude;obs=new A.Observer(lat,lon,p.coords.altitude||0);
  $('mnHere').textContent='내 위치 기준 (저장 안 함)';slow();moon();if(window._iss)iss()},function(){$('mnHere').textContent='위치를 허용하지 않아 서울시청 기준이에요'},{enableHighAccuracy:false,timeout:10000})});
function xyz(la,lo,h){var R=6371+h,a=la*Math.PI/180,b=lo*Math.PI/180;return [R*Math.cos(a)*Math.cos(b),R*Math.cos(a)*Math.sin(b),R*Math.sin(a)]}
function iss(){fetch('https://api.wheretheiss.at/v1/satellites/25544').then(function(r){return r.json()}).then(function(d){
 var a=xyz(lat,lon,0),b=xyz(d.latitude,d.longitude,d.altitude),km=Math.hypot(a[0]-b[0],a[1]-b[1],a[2]-b[2]);
 $('isKm').textContent=f(km)+' km';$('isAlt').textContent=f(d.altitude,1)+' km';$('isVel').textContent='시속 '+f(d.velocity)+' km';
 $('isPos').textContent='위도 '+f(d.latitude,2)+'°, 경도 '+f(d.longitude,2)+'°'}).catch(function(){$('isKm').textContent='잠시 뒤 다시'})}
$('isGo').addEventListener('click',function(){if(window._iss)return;window._iss=setInterval(iss,5000);iss();this.textContent='5초마다 새로 가져오는 중';this.disabled=true});
$('isLive').addEventListener('click',function(){var v=$('isVid');v.hidden=false;if(!v.firstChild)v.innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/live_stream?channel=UCLA_DiR1FfKNvjuUpBHmylQ&autoplay=1&mute=1" title="NASA 생중계" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen loading="lazy"></iframe>'});
slow();moon();setInterval(moon,100);setInterval(slow,60000);
})();
</script>'''

LD = [{"@context": "https://schema.org", "@type": "WebApplication", "name": "달까지 거리 실시간 계산기", "url": URL,
       "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "ko",
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "dateModified": "2026-11-23"},
      {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
          {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]

src = os.path.join(ORIG, 'ko/clock.html')
s = open(src, encoding='utf-8').read()
s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', s, count=1)
s = re.sub(r'<!--hl:alt-->.*?<!--/hl:alt-->', '', s, flags=re.S)
s = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', s)
for p, v in (('og:title', TITLE), ('og:description', DESC), ('og:url', URL), ('og:image:alt', '달까지 거리 실시간')):
    s = re.sub(r'(<meta property="' + re.escape(p) + r'" content=")[^"]*', lambda m: m.group(1) + v, s, count=1)
s = re.sub(r'<meta property="og:image(?::type|:width|:height)?" content="[^"]*">\s*', '', s)
s = re.sub(r'<!--hl:img-->.*?<!--/hl:img-->', '', s, flags=re.S)
s = re.sub(r'<meta name="twitter:image" content="[^"]*">', '', s)
s = s.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary">')
s = re.sub(r'(?s)<script type="application/ld\+json">.*?</script>\s*', '', s)
s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in LD) + CSS + '</head>', 1)
s = re.sub(r'(<header class="top">.*?)<nav>.*?</nav>', r'\1', s, count=1, flags=re.S)
s = re.sub(r'(?s)<main>.*?</main>', lambda m: MAIN, s, count=1)
s = s.replace('<div class="flash" id="flash"></div>', '', 1)
i = s.index('</footer>')
tail = re.sub(r"(?s)<script>\s*\(function\(\)\{\s*const \$=id=>document\.getElementById\(id\);.*?</script>", lambda m: JS, s[i:], count=1)
assert JS in tail, 'clock script not replaced'
s = s[:i] + tail
s = s.replace('<a href="calorie.html">칼로리 계산기</a>', '<a href="clock.html">서버시간</a>', 1)
assert 'id="mnKm"' in s and 'svs.gsfc' in s and 'og:image"' not in s
os.makedirs(os.path.join(OUT, 'ko'), exist_ok=True)
out = os.path.join(OUT, 'ko', SLUG)
open(out, 'w', encoding='utf-8').write(s)
print(out, len(s))
