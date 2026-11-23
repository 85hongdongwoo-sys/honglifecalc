"""새 페이지: 달과 나의 거리 실시간 계산기 (한국어).
계산: astronomy-engine 2.1.19 (MIT, Don Cross) — 브라우저에서 내 위치 기준(지형 중심) 달 거리를 매 순간 계산.
달 사진: NASA Scientific Visualization Studio 'Moon Phase and Libration, 2026' (SVS 5587) 시간별 프레임.
우주정거장 위치: wheretheiss.at 공개 API. 표의 보름달·근지점 숫자는 같은 라이브러리로 계산해 넣음 (2026-11-23).
템플릿 = /ko/science/free-fall-calculator.html (과학·공학 페이지와 같은 디자인). overlay/ko/science/moon-distance.html 을 쓰고,
옛 주소 /ko/moon-distance.html 은 새 주소로 옮겨 주는 안내 페이지로 바꾼다."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enrich_lib import ORIG, OUT

SLUG = 'moon-distance.html'
URL = 'https://honglifecalc.com/ko/science/' + SLUG
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
    return (f'<div class="scroll"><table class="{cls}"><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' +
            ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>')

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
faq_h = '<h3 id="faq">자주 묻는 질문</h3>' + ''.join(f'<h4 class="q">{q}</h4><p class="a">{a}</p>' for q, a in FAQ)

CSS = '''<style>
.mn-hero{display:grid;grid-template-columns:minmax(0,260px) 1fr;gap:22px;align-items:center}
.mn-img{position:relative;aspect-ratio:1;border-radius:50%;overflow:hidden;background:#05070d;box-shadow:0 0 0 1px #eadfc6}
.mn-img img,.mn-img canvas{width:100%;height:100%;display:block;object-fit:cover}.mn-img [hidden],.mn-vid[hidden],.mn-note[hidden]{display:none!important}
.mn-lab{color:var(--muted,#6b6450);font-size:13px;margin:0 0 2px}
.mn-big{font:700 clamp(30px,7vw,48px)/1.1 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:#12305C}
.mn-big small{font-size:.42em;margin-left:4px;color:var(--muted,#6b6450)}
.mn-cmp{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0 0;padding:0;list-style:none}
.mn-cmp li{background:#fffaf0;border:1px solid #eadfc6;border-radius:999px;padding:5px 11px;font-size:13px;margin:0}
.mn-cmp b{font-variant-numeric:tabular-nums}
.mn-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-top:14px}
.mn-grid div{background:#fffaf0;border:1px solid #eadfc6;border-radius:12px;padding:10px 12px}
.mn-grid span{display:block;color:var(--muted,#6b6450);font-size:12px}
.mn-grid b{display:block;font-size:16px;font-variant-numeric:tabular-nums;word-break:keep-all}
.mn-btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;align-items:center}
.mn-btn{font:inherit;font-size:14px;font-weight:700;padding:10px 14px;border-radius:12px;border:0;background:#12305C;color:#fff;cursor:pointer}
.mn-btn.ghost{background:#fffaf0;color:#12305C;border:1px solid #eadfc6}
.mn-btn:disabled{opacity:.7;cursor:default}
.mn-note{font-size:12.5px;color:var(--muted,#6b6450);margin:8px 0 0}
.mn-vid{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#000;margin-top:12px}
.mn-vid iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.hl-explain table.mt td:nth-child(2){font-variant-numeric:tabular-nums;white-space:nowrap}
.mn-ans{background:#FFF4D6;border:1px solid #eadfc6;border-radius:12px;padding:12px 14px;line-height:1.7;margin:0 0 6px}
@media(max-width:420px){.hl-explain table.mt th,.hl-explain table.mt td{white-space:normal;padding:6px 5px;font-size:13px}}
@media(max-width:640px){.mn-hero{grid-template-columns:1fr}.mn-img{max-width:220px;margin:0 auto}}
</style>'''

APP = f'''<section class="card" id="moon"><h2>지금 달과 나의 거리</h2>
 <div class="mn-hero">
  <div class="mn-img"><img id="mnImg" alt="지금 이 시각의 달 모습 (NASA)" width="730" height="730" hidden><canvas id="mnCv" width="600" height="600" aria-label="지금 달의 모양"></canvas></div>
  <div>
   <p class="mn-lab" id="mnHere">서울시청 기준</p>
   <div class="mn-big" id="mnKm" aria-live="off">계산 중…</div>
   <ul class="mn-cmp">
    <li>빛으로 <b id="mnLight">-</b></li>
    <li>자동차(시속 100km) <b id="mnCar">-</b></li>
    <li>비행기(시속 900km) <b id="mnPlane">-</b></li>
    <li>걸어서(시속 4km) <b id="mnWalk">-</b></li>
   </ul>
   <div class="mn-btns"><button type="button" class="mn-btn" id="mnGeo">📍 내 위치로 계산</button></div>
   <p class="mn-note">위치는 이 화면 계산에만 쓰고 저장하지 않아요.</p>
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
 <p class="mn-note">달 사진: NASA Scientific Visualization Studio (매시간 달 모습). 거리 계산: astronomy-engine.</p>
</section>
<section class="card" id="iss" style="margin-top:14px"><h2>국제우주정거장(ISS)과 나의 거리</h2>
 <p>지구 위 약 400km를 초속 7.7km로 도는 우주정거장이 지금 어디에 있는지, 내 위치에서 얼마나 먼지 5초마다 새로 가져와요.</p>
 <div class="mn-grid">
  <div><span>나와 ISS 사이 거리</span><b id="isKm">-</b></div>
  <div><span>ISS 높이</span><b id="isAlt">-</b></div>
  <div><span>속도</span><b id="isVel">-</b></div>
  <div><span>지금 아래 지점</span><b id="isPos">-</b></div>
 </div>
 <div class="mn-btns"><button type="button" class="mn-btn" id="isGo">우주정거장 위치 불러오기</button><button type="button" class="mn-btn ghost" id="isLive">🎥 NASA 생중계 보기</button></div>
 <div class="mn-vid" id="isVid" hidden></div>
 <p class="mn-note" id="isAlt2" hidden>영상이 안 나오면 NASA가 다른 카메라로 바꾼 거예요. <a href="https://www.youtube.com/watch?v=M3HKLzjvKPc" target="_blank" rel="noopener">두 번째 NASA 생중계</a>나 <a href="https://www.youtube.com/@NASA/streams" target="_blank" rel="noopener">NASA 생중계 목록</a>에서 보세요.</p>
 <p class="mn-note">위치: wheretheiss.at 공개 자료. 생중계: NASA 공식 유튜브 (우주정거장이 지구 밤쪽을 지날 때는 화면이 어두워요).</p>
</section>
<section class="card" id="far" style="margin-top:14px"><h2>태양·화성까지 지금 거리</h2>
 <div class="mn-grid">
  <div><span>태양까지</span><b id="suKm">-</b></div>
  <div><span>화성까지</span><b id="maKm">-</b></div>
  <div><span>화성까지 빛으로</span><b id="maLt">-</b></div>
 </div>
</section>'''

EXPLAIN = f'''<article class="card hl-explain" id="hl-explain"><h2>달까지 거리 쉽게 이해하기</h2>
<p class="mn-ans"><b>한 줄 답 (2026년):</b> 달까지 거리는 <b>평균 약 38만 4,400km</b>이고, 가까울 때 약 35만 6천km, 멀 때 약 40만 6천km예요. 2026년 가장 가까운 보름달은 <b>12월 24일</b>(약 {near26[1]:,}km)이에요.</p>
<h3 id="why">달까지 거리가 매일 바뀌는 이유</h3>
<p>달은 지구 둘레를 동그라미가 아니라 살짝 찌그러진 타원으로 돌아요. 그래서 약 27.5일마다 한 번 가장 가까운 <b>근지점</b>, 가장 먼 <b>원지점</b>을 지나요. 그 차이는 5만km 가까이 돼요.</p>
<p>여기에 지구 자전이 더해져요. 지구 반지름이 약 6,371km라서, 달이 머리 위에 있을 때는 지구 중심 기준 거리보다 최대 약 6천km 가깝고, 달이 지면 그만큼 멀어져요. 위 계산기가 <b>내 위치 기준</b>으로 계산하는 이유예요.</p>
<h3 id="full">보름달 날짜별 거리 (2026~2027년, 한국 날짜)</h3>
<p>보름달이 근지점 근처에서 뜨면 크고 밝게 보여서 흔히 <b>슈퍼문</b>이라고 불러요. 원지점 근처 보름달은 <b>미니문</b>이라고 해요. 거리는 지구 중심에서 달 중심까지예요.</p>
{full_t}
<h3 id="aps">다가오는 근지점·원지점</h3>
{aps_t}
<h3 id="cmp">달까지 거리, 이렇게 비교해 보세요</h3>
<ul>
<li><b>빛:</b> 약 1.28초. 달에서 보낸 신호가 지구에 오는 시간이에요.</li>
<li><b>자동차(시속 100km):</b> 쉬지 않고 약 160일.</li>
<li><b>비행기(시속 900km):</b> 약 17.8일.</li>
<li><b>아폴로 11호:</b> 1969년 7월 16일 발사해 3일 뒤 달 궤도에 들어갔어요.</li>
<li><b>지구 30개:</b> 지구 지름(약 1만 2,742km)을 30번 늘어놓으면 달까지 거리와 비슷해요.</li>
</ul>
{faq_h}
<p class="src">출처 (확인 {CHECKED}): 달 사진 – <a href="https://svs.gsfc.nasa.gov/5587/" rel="nofollow">NASA Scientific Visualization Studio, Moon Phase and Libration, 2026</a> · 거리·위상·뜨고 지는 시간 – <a href="https://github.com/cosinekitty/astronomy" rel="nofollow">astronomy-engine</a>(MIT 라이선스)로 계산 · 우주정거장 위치 – <a href="https://wheretheiss.at/w/developer" rel="nofollow">wheretheiss.at API</a> · 평균 거리와 해마다 멀어지는 거리 – NASA</p>
</article>
<article class="card help"><p class="note">{CHECKED} 확인. 표의 날짜·거리는 위 계산기와 같은 천문 계산으로 미리 구한 값이에요. 실제 관측에는 날씨와 지형에 따라 달 뜨는 시간이 몇 분 다를 수 있어요.</p></article>'''

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
$('isLive').addEventListener('click',function(){var v=$('isVid');v.hidden=false;if(!v.firstChild)v.innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/ROboUHfPUrU?autoplay=1&mute=1" title="NASA 생중계" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen loading="lazy"></iframe>';$('isAlt2').hidden=false});
slow();moon();setInterval(moon,100);setInterval(slow,60000);
})();
</script>'''


LD = [{"@context": "https://schema.org", "@type": "WebApplication", "name": "달까지 거리 실시간 계산기", "url": URL,
       "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "ko",
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "dateModified": "2026-11-24"},
      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
          {"@type": "ListItem", "position": 1, "name": "홍라이프 계산기", "item": "https://honglifecalc.com/ko/"},
          {"@type": "ListItem", "position": 2, "name": "과학·공학", "item": "https://honglifecalc.com/ko/science/"},
          {"@type": "ListItem", "position": 3, "name": "달까지 거리 실시간", "item": URL}]},
      {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
          {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]

src = os.path.join(ORIG, 'ko/science/free-fall-calculator.html')
s = open(src, encoding='utf-8').read()
s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s, count=1)
s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', s, count=1)
s = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', s)
for p, v in (('og:title', TITLE), ('og:description', DESC), ('og:url', URL)):
    s = re.sub(r'(<meta property="' + re.escape(p) + r'" content=")[^"]*', lambda m: m.group(1) + v, s, count=1)
s = re.sub(r'<meta property="og:image(?::type|:width|:height|:alt)?" content="[^"]*">\s*', '', s)
s = re.sub(r'<meta name="twitter:image" content="[^"]*">', '', s)
s = s.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary">')
s = re.sub(r'(?s)<script type="application/ld\+json">.*?</script>\s*', '', s)
s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in LD) + CSS + '</head>', 1)
s = re.sub(r'(?s)<header class="hero">.*?</header>',
           '<header class="hero"><div class="in"><span class="year">🔬 과학·공학 · 우주</span><h1>달까지 거리 실시간 – 지금 달과 나의 거리</h1>'
           '<p>내 위치에서 달까지 몇 km인지 매 순간 계산하고, NASA가 공개한 이 시각의 달 사진을 함께 보여 줘요.</p></div></header>', s, count=1)
m = re.search(r'(?s)<main class="wrap">(.*?)<a class="hl-dlink"', s)
s = s[:m.start(1)] + '\n' + APP + '\n' + EXPLAIN + '\n' + s[m.end(1):]
i = s.index('</footer>')
tail = s[i:]
tail = re.sub(r"(?s)<script>\s*\(function\(\)\{'use strict';.*?</script>", lambda m: JS, tail, count=1)
tail = re.sub(r'<script src="/assets/hl-(viz|live)\.js" defer></script>\s*', '', tail)
assert JS in tail
s = s[:i] + tail
assert 'id="mnKm"' in s and 'id="hl-steps"' not in s and 'free-fall' not in s.split('</head>')[1].split('<footer>')[0], 'leftover template content'
os.makedirs(os.path.join(OUT, 'ko', 'science'), exist_ok=True)
out = os.path.join(OUT, 'ko', 'science', SLUG)
open(out, 'w', encoding='utf-8').write(s)
print(out, len(s))

# 옛 주소: 새 주소로 바로 옮겨 주는 안내 페이지 (검색에는 내보내지 않음)
OLD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>달까지 거리 실시간 – 페이지가 옮겨졌어요</title>'
       f'<meta name="robots" content="noindex,follow"><link rel="canonical" href="{URL}">'
       f'<meta http-equiv="refresh" content="0; url=/ko/science/{SLUG}"></head><body>'
       f'<p>이 페이지는 <a href="/ko/science/{SLUG}">과학·공학 › 달까지 거리 실시간</a>으로 옮겨졌어요.</p>'
       f'<script>location.replace("/ko/science/{SLUG}"+location.search+location.hash)</script></body></html>')
open(os.path.join(OUT, 'ko', SLUG), 'w', encoding='utf-8').write(OLD)
