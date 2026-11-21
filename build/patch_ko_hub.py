"""한국어 허브(/ko/index.html) 다듬기 — 배포 때 실행.
1) '분야별로 찾기' 타일을 휴대폰처럼 정사각형(아이콘 위, 이름 아래)으로 모든 화면 크기에서 통일
2) '전체 계산기' 아래 분야별 긴 목록(ci-fam)을 접고 펴는 목차로 바꾸고, 계산기 이름 검색·모두 펼치기 추가"""
import os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else '_site'
p = os.path.join(root, 'ko', 'index.html')
h = open(p, encoding='utf-8').read()
if 'id="hl-ko-hub2"' in h:
    sys.exit(0)

ICON = {'정부 지원금': 'benefit', '대출·투자·은퇴': 'money', '사업·부업': 'biz', 'AI·회사': 'ai', '집·생활': 'tools', '건강·피트니스': 'health',
        '수학·통계': 'math', '과학·공학': 'sci', 'IT·개발': 'tech', '단위 변환·규격': 'conv', '스포츠·게임': 'games'}

CSS = '''<style id="hl-ko-hub2">
/* 1) 분야 타일: 정사각형 앱 아이콘 */
html body .hl-home .hlh-tiles{display:grid!important;grid-template-columns:repeat(auto-fill,minmax(92px,1fr))!important;gap:8px!important}
html body .hl-home .hlh-tiles .hlh-tile{display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:4px!important;aspect-ratio:1/1;min-height:0!important;padding:8px 4px!important;text-align:center!important;box-sizing:border-box}
html body .hl-home .hlh-tiles .hlh-tile img{width:42px!important;height:42px!important;margin:0 0 2px!important;grid-row:auto!important}
html body .hl-home .hlh-tiles .hlh-tile b{font-size:13px!important;line-height:1.25!important;text-align:center!important;word-break:keep-all;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;max-width:100%;align-self:center!important}
html body .hl-home .hlh-tiles .hlh-tile span{font-size:11.5px!important;align-self:center!important}
@media (max-width:420px){html body .hl-home .hlh-tiles{grid-template-columns:repeat(3,minmax(0,1fr))!important}}
/* 2) 전체 목록: 접고 펴는 목차 */
.ci-tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:22px 0 10px}
.ci-tools input{flex:1 1 220px;min-width:0;font:inherit;font-size:15px;padding:11px 14px;border-radius:12px;border:1px solid #E3D7B8;background:#FFFDF6}
.ci-tools input:focus{outline:3px solid #E8C27A;outline-offset:1px}
.ci-tools button{font:inherit;font-size:14px;font-weight:700;padding:10px 14px;border-radius:12px;border:1px solid #E3D7B8;background:#FFF8E7;color:#5A4515;cursor:pointer;white-space:nowrap}
.ci-all{margin-top:6px!important;display:grid!important;gap:8px!important}
details.ci-fam{border:1px solid #EDE4CC;border-radius:16px;background:#FFFDF6;overflow:hidden}
details.ci-fam>summary{list-style:none;display:flex;align-items:center;gap:10px;padding:12px 14px;cursor:pointer;font-weight:800;font-size:16px;color:#2B2A22}
details.ci-fam>summary::-webkit-details-marker{display:none}
details.ci-fam>summary img{width:34px;height:34px;flex:none}
details.ci-fam>summary b{flex:1;min-width:0}
details.ci-fam>summary span{font-size:12px;font-weight:700;color:#8A6414;background:#FBF4E4;border:1px solid #E8C27A;border-radius:999px;padding:2px 9px}
details.ci-fam>summary::after{content:"";width:9px;height:9px;border-right:2.5px solid #B8862B;border-bottom:2.5px solid #B8862B;transform:rotate(45deg);margin:0 4px 4px 2px;transition:transform .2s}
details.ci-fam[open]>summary::after{transform:rotate(-135deg);margin-bottom:-4px}
details.ci-fam[open]>summary{border-bottom:1px solid #EDE4CC;background:#FFF8E7}
details.ci-fam ul{list-style:none;margin:0!important;padding:10px 12px 12px!important;display:grid!important;grid-template-columns:repeat(auto-fill,minmax(min(100%,210px),1fr))!important;gap:6px!important}
details.ci-fam li{min-width:0}
details.ci-fam a{display:flex!important;align-items:center;gap:6px;height:100%;box-sizing:border-box;padding:9px 11px!important;border-radius:10px;background:#fff;box-shadow:0 0 0 1px #F0E8D3;font-size:13.5px!important;line-height:1.35!important;color:#2C3A4F!important;text-decoration:none!important;word-break:keep-all;overflow-wrap:anywhere}
details.ci-fam a::after{content:"›";margin-left:auto;color:#C9A227;font-weight:800;padding-left:6px}
details.ci-fam a:hover{box-shadow:0 0 0 2px #E8C27A;color:#8A6414!important}
details.ci-fam li:first-child a{background:#FFF4D6;font-weight:700}
details.ci-fam li.ci-hide{display:none}
@media (max-width:640px){details.ci-fam ul{grid-template-columns:repeat(2,minmax(0,1fr))!important}details.ci-fam a{font-size:13px!important;padding:8px 9px!important}}
.ci-none{display:none;padding:14px;color:#6B6450;font-size:14px}
</style>'''

JS = '''<script>(function(){var q=document.getElementById("ci-q"),all=document.getElementById("ci-open"),box=document.querySelector(".ci-all");if(!q||!box)return;
var fams=[].slice.call(box.querySelectorAll("details.ci-fam")),none=document.getElementById("ci-none");
function filt(){var v=q.value.trim().toLowerCase(),hit=0;fams.forEach(function(d){var n=0;d.querySelectorAll("li").forEach(function(li){var ok=!v||li.textContent.toLowerCase().indexOf(v)>-1;li.classList.toggle("ci-hide",!ok);if(ok)n++});d.style.display=n?"":"none";if(v)d.open=n>0;hit+=n});none.style.display=v&&!hit?"block":"none"}
q.addEventListener("input",filt);
all.addEventListener("click",function(){var o=!fams.every(function(d){return d.open});fams.forEach(function(d){d.open=o});all.textContent=o?"모두 접기":"모두 펼치기"});})();</script>'''

i = h.find('<div class="ci-all">')
if i < 0:
    sys.exit('ci-all not found')
last = h.rfind('class="ci-fam')
end = h.find('</section>', last) + len('</section>')
seg = h[i:end]


def head(m):
    cls, name, cnt = m.group(1), m.group(2).strip(), m.group(3)
    ic = ICON.get(name, 'look')
    return (f'<details class="ci-fam{cls}"><summary><img src="/ko/assets/art/ic-{ic}.svg" alt="" width="34" height="34" loading="lazy">'
            f'<b>{name}</b><span>{cnt}</span></summary>')


seg = re.sub(r'<section class="ci-fam([^"]*)"><h3>(.*?)<span>(\d+)</span></h3>', head, seg)
seg = seg.replace('</ul></section>', '</ul></details>')
tools = ('<div class="ci-tools"><input id="ci-q" type="search" placeholder="계산기 찾기 (예: 퇴직금, BMI)" aria-label="계산기 이름으로 찾기">'
         '<button type="button" id="ci-open">모두 펼치기</button></div><p class="ci-none" id="ci-none">찾는 계산기가 없어요. 다른 낱말로 찾아보세요.</p>')
h = h[:i] + tools + seg + h[end:]
h = h.replace('</head>', CSS + '</head>', 1)
h = h.replace('</body>', JS + '</body>', 1)
open(p, 'w', encoding='utf-8').write(h)
print('ko hub patched:', seg.count('<details class="ci-fam'), 'sections')
