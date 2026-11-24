"""모든 언어 페이지 맨 위 머리글에 ☆ 즐겨찾기 · 즐겨찾기 목록 · 앱 설치 버튼을 넣고,
분야 타일 이름이 잘리는 문제(글자 아래쪽이 잘림, '단위 변환·그…'처럼 끊김)를 고친다. 배포 때 실행.
- JS: _site/assets/app.js, _site/ko/assets/app.js 끝에 덧붙임 (거의 모든 페이지가 둘 중 하나를 불러옴)
- CSS: _site/assets/hl-unify.css 끝에 덧붙임 (+ JS가 같은 CSS를 한 번 더 넣어 이 파일이 없는 페이지도 적용)
즐겨찾기는 이 기기 브라우저(localStorage 'hl-favs')에만 저장되고 서버로 보내지 않는다."""
import os, sys

root = sys.argv[1] if len(sys.argv) > 1 else '_site'
MARK = '/* hl-topbar v1 */'

CSS = (MARK + '\n'
       # 분야 타일 이름: 줄 높이를 넉넉히(윈도우 맑은 고딕에서 아래가 잘리던 문제), 좁으면 두 줄로 자연스럽게 줄바꿈
       'html body .hlh-tiles .hlh-tile b,html body .hl-home .hlh-tiles .hlh-tile b{line-height:1.45!important;padding:1px 0 2px!important;'
       'display:block!important;-webkit-line-clamp:unset!important;overflow:visible!important;white-space:normal!important;'
       'word-break:keep-all!important;overflow-wrap:anywhere!important;text-overflow:clip!important}'
       'html body .hl-home .hlh-tiles .hlh-tile{aspect-ratio:auto!important;min-height:104px!important;height:auto!important;overflow:visible!important}'
       'html body .hlh-tiles .hlh-tile span{line-height:1.4!important}'
       # 머리글 버튼 줄
       '.hl-tb{display:flex;align-items:center;gap:6px;margin-left:auto;flex:none}'
       '.hl-tb button{display:inline-flex;align-items:center;gap:5px;height:34px;padding:0 11px;border-radius:999px;border:1px solid #E3D7B8;background:#fff;color:#3A3220;'
       'font:inherit;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;line-height:1}'
       '.hl-tb button:hover{border-color:#C9A227}.hl-tb svg{width:16px;height:16px;flex:none}'
       '.hl-tb .hl-tb-star[aria-pressed="true"]{background:#FFF4D6;border-color:#C9A227;color:#8A6414}'
       '.hl-tb .hl-tb-star[aria-pressed="true"] svg{fill:#E0A800;stroke:#B8862B}'
       '.hl-tb .hl-tb-n{min-width:18px;height:18px;padding:0 5px;border-radius:999px;background:#FBF4E4;color:#8A6414;font-size:11px;display:inline-grid;place-items:center}'
       '.hl-tb .hl-tb-app{background:#2B2A22;color:#fff;border-color:#2B2A22}'
       '.hl-appbtn{display:none!important}'
       '.hlu-groups{flex-wrap:wrap!important;overflow-x:visible!important;row-gap:6px}'
       '@media(max-width:560px){.hl-tb button{padding:0 9px}.hl-tb .hl-tb-t{display:none}.hl-tb .hl-tb-app .hl-tb-t{display:inline}}'
       '@media(max-width:360px){.hl-tb .hl-tb-app .hl-tb-t{display:none}}'
       '.brandbar .in,.brand .in{display:flex;align-items:center;flex-wrap:nowrap;gap:8px;min-width:0}'
       '.brandbar .in .logo,.brand .in .logo{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
       '.brandbar .in .meta,.brand .in .flag,.brandbar .in .langs{min-width:0}'
       '@media(max-width:640px){.brandbar .in .meta{display:none}}'
       # 즐겨찾기 목록 창
       '.hl-fav{position:fixed;z-index:2147483000;top:62px;right:12px;width:min(340px,calc(100vw - 24px));max-height:70vh;overflow:auto;background:#fff;border:1px solid #E3D7B8;'
       'border-radius:16px;box-shadow:0 12px 32px rgba(0,0,0,.18);padding:12px}'
       '.hl-fav h3{margin:2px 4px 8px;font-size:15px}.hl-fav ul{list-style:none;margin:0;padding:0;display:grid;gap:6px}'
       '.hl-fav li{display:flex;align-items:center;gap:6px}.hl-fav li a{flex:1;min-width:0;padding:9px 11px;border-radius:10px;background:#FFFDF6;box-shadow:0 0 0 1px #F0E8D3;'
       'color:#2C3A4F;text-decoration:none;font-size:14px;line-height:1.35;overflow-wrap:anywhere}'
       '.hl-fav li button{flex:none;width:30px;height:30px;border-radius:999px;border:1px solid #E3D7B8;background:#fff;cursor:pointer;font-size:16px;color:#8A6414}'
       '.hl-fav p{margin:6px 4px;color:#6B6450;font-size:13.5px;line-height:1.55}'
       '.hl-tb-tip{position:fixed;z-index:2147483001;left:50%;bottom:24px;transform:translateX(-50%);width:min(420px,calc(100vw - 24px));background:#2B2A22;color:#fff;'
       'border-radius:14px;padding:12px 14px;font-size:14px;line-height:1.55;box-shadow:0 10px 28px rgba(0,0,0,.25)}'
       '\n')

JS = r'''
/* hl-topbar v1 — 즐겨찾기(☆)·즐겨찾기 목록·앱 설치 버튼 (모든 언어) */
(function(){var w=window,d=document;if(d.querySelector(".hl-tb"))return;
var L=(d.documentElement.lang||"en").toLowerCase(),L2=L.slice(0,2),ZT=/^zh-(tw|hk|hant)/.test(L);
var T={ko:["즐겨찾기","즐겨찾기 목록","앱 설치","즐겨찾기한 계산기가 없어요. 계산기 페이지 위쪽 ☆을 누르면 여기에 모여요.","빼기","아이폰: 아래쪽 공유 버튼(□↑) → '홈 화면에 추가'를 누르면 앱처럼 쓸 수 있어요.","브라우저 메뉴(⋮ 또는 …)에서 '앱 설치' 또는 '홈 화면에 추가'를 누르면 앱처럼 쓸 수 있어요.","이미 앱으로 설치돼 있어요.","이 기기에만 저장돼요."],
en:["Favorite","Favorites","Install app","No favorites yet. Tap ☆ at the top of any calculator to save it here.","Remove","iPhone: tap Share (□↑) → 'Add to Home Screen' to use it like an app.","Open the browser menu (⋮ or …) and choose 'Install app' or 'Add to Home screen'.","Already installed as an app.","Saved on this device only."],
ja:["お気に入り","お気に入り一覧","アプリを追加","お気に入りはまだありません。計算ページ上部の☆を押すとここに保存されます。","削除","iPhone：共有ボタン(□↑)→「ホーム画面に追加」でアプリのように使えます。","ブラウザのメニュー(⋮/…)から「アプリをインストール」または「ホーム画面に追加」を選んでください。","すでにアプリとして追加済みです。","この端末にのみ保存されます。"],
zh:ZT?["收藏","收藏清單","安裝 App","還沒有收藏。點計算頁上方的☆即可存到這裡。","移除","iPhone：點分享(□↑)→「加入主畫面」即可像 App 一樣使用。","在瀏覽器選單(⋮ 或 …)選擇「安裝應用程式」或「加到主畫面」。","已安裝為 App。","只儲存在這台裝置。"]:["收藏","收藏列表","安装应用","还没有收藏。点计算页上方的☆即可保存到这里。","移除","iPhone：点分享(□↑)→「添加到主屏幕」即可像应用一样使用。","在浏览器菜单(⋮ 或 …)选择「安装应用」或「添加到主屏幕」。","已安装为应用。","仅保存在本设备。"],
es:["Favorito","Favoritos","Instalar app","Aún no hay favoritos. Toca ☆ arriba en cualquier calculadora para guardarla aquí.","Quitar","iPhone: toca Compartir (□↑) → 'Agregar a inicio'.","Abre el menú del navegador (⋮ o …) y elige 'Instalar app' o 'Agregar a la pantalla de inicio'.","Ya está instalada como app.","Solo se guarda en este dispositivo."],
fr:["Favori","Favoris","Installer l’app","Aucun favori. Touchez ☆ en haut d’un calculateur pour l’enregistrer ici.","Retirer","iPhone : Partager (□↑) → « Sur l’écran d’accueil ».","Ouvrez le menu du navigateur (⋮ ou …) puis « Installer l’application » ou « Ajouter à l’écran d’accueil ».","Déjà installée comme app.","Enregistré sur cet appareil uniquement."],
de:["Favorit","Favoriten","App installieren","Noch keine Favoriten. Tippe oben in einem Rechner auf ☆, um ihn hier zu speichern.","Entfernen","iPhone: Teilen (□↑) → „Zum Home-Bildschirm“.","Öffne das Browsermenü (⋮ oder …) und wähle „App installieren“ oder „Zum Startbildschirm hinzufügen“.","Bereits als App installiert.","Nur auf diesem Gerät gespeichert."],
pt:["Favorito","Favoritos","Instalar app","Ainda não há favoritos. Toque em ☆ no topo de uma calculadora para salvá-la aqui.","Remover","iPhone: toque em Compartilhar (□↑) → 'Adicionar à Tela de Início'.","Abra o menu do navegador (⋮ ou …) e escolha 'Instalar app' ou 'Adicionar à tela inicial'.","Já instalado como app.","Salvo só neste aparelho."],
it:["Preferito","Preferiti","Installa app","Nessun preferito. Tocca ☆ in alto in un calcolatore per salvarlo qui.","Rimuovi","iPhone: Condividi (□↑) → 'Aggiungi alla schermata Home'.","Apri il menu del browser (⋮ o …) e scegli 'Installa app' o 'Aggiungi a schermata Home'.","Già installata come app.","Salvato solo su questo dispositivo."],
nl:["Favoriet","Favorieten","App installeren","Nog geen favorieten. Tik bovenaan een rekenhulp op ☆ om hem hier te bewaren.","Verwijderen","iPhone: Deel (□↑) → 'Zet op beginscherm'.","Open het browsermenu (⋮ of …) en kies 'App installeren' of 'Toevoegen aan startscherm'.","Al geïnstalleerd als app.","Alleen op dit apparaat bewaard."],
pl:["Ulubione","Lista ulubionych","Zainstaluj","Brak ulubionych. Dotknij ☆ u góry kalkulatora, aby zapisać go tutaj.","Usuń","iPhone: Udostępnij (□↑) → „Do ekranu początk.”.","Otwórz menu przeglądarki (⋮ lub …) i wybierz „Zainstaluj aplikację” lub „Dodaj do ekranu głównego”.","Już zainstalowano jako aplikację.","Zapisane tylko na tym urządzeniu."],
id:["Favorit","Daftar favorit","Pasang aplikasi","Belum ada favorit. Ketuk ☆ di atas kalkulator untuk menyimpannya di sini.","Hapus","iPhone: ketuk Bagikan (□↑) → 'Tambah ke Layar Utama'.","Buka menu browser (⋮ atau …) lalu pilih 'Instal aplikasi' atau 'Tambahkan ke layar utama'.","Sudah terpasang sebagai aplikasi.","Hanya disimpan di perangkat ini."],
ms:["Kegemaran","Senarai kegemaran","Pasang apl","Belum ada kegemaran. Ketik ☆ di atas kalkulator untuk simpan di sini.","Buang","iPhone: ketik Kongsi (□↑) → 'Tambah ke Skrin Utama'.","Buka menu pelayar (⋮ atau …) dan pilih 'Pasang apl' atau 'Tambah ke skrin utama'.","Sudah dipasang sebagai apl.","Disimpan pada peranti ini sahaja."],
ru:["Избранное","Список избранного","Установить","Пока нет избранного. Нажмите ☆ вверху калькулятора, чтобы сохранить его здесь.","Убрать","iPhone: «Поделиться» (□↑) → «На экран Домой».","Откройте меню браузера (⋮ или …) и выберите «Установить приложение» или «Добавить на главный экран».","Уже установлено как приложение.","Сохраняется только на этом устройстве."],
tr:["Favori","Favoriler","Uygulamayı yükle","Henüz favori yok. Bir hesaplayıcının üstündeki ☆ simgesine dokunun.","Kaldır","iPhone: Paylaş (□↑) → 'Ana Ekrana Ekle'.","Tarayıcı menüsünü (⋮ veya …) açıp 'Uygulamayı yükle' veya 'Ana ekrana ekle'yi seçin.","Zaten uygulama olarak yüklü.","Yalnızca bu cihazda saklanır."],
vi:["Yêu thích","Danh sách yêu thích","Cài ứng dụng","Chưa có mục yêu thích. Chạm ☆ ở đầu trang máy tính để lưu vào đây.","Bỏ","iPhone: chạm Chia sẻ (□↑) → 'Thêm vào MH chính'.","Mở menu trình duyệt (⋮ hoặc …) và chọn 'Cài đặt ứng dụng' hoặc 'Thêm vào màn hình chính'.","Đã cài như ứng dụng.","Chỉ lưu trên thiết bị này."],
hi:["पसंदीदा","पसंदीदा सूची","ऐप इंस्टॉल","अभी कोई पसंदीदा नहीं। किसी कैलकुलेटर के ऊपर ☆ दबाएँ।","हटाएँ","iPhone: शेयर (□↑) → 'होम स्क्रीन में जोड़ें'।","ब्राउज़र मेनू (⋮ या …) खोलकर 'ऐप इंस्टॉल करें' या 'होम स्क्रीन में जोड़ें' चुनें।","पहले से ऐप के रूप में इंस्टॉल है।","केवल इस डिवाइस पर सहेजा जाता है।"],
ar:["المفضلة","قائمة المفضلة","ثبّت التطبيق","لا توجد مفضلة بعد. اضغط ☆ أعلى أي حاسبة لحفظها هنا.","إزالة","آيفون: مشاركة (□↑) ← «إضافة إلى الشاشة الرئيسية».","افتح قائمة المتصفح (⋮ أو …) واختر «تثبيت التطبيق» أو «إضافة إلى الشاشة الرئيسية».","مثبّت بالفعل كتطبيق.","يُحفظ على هذا الجهاز فقط."],
sv:["Favorit","Favoriter","Installera app","Inga favoriter än. Tryck på ☆ högst upp i en kalkylator.","Ta bort","iPhone: Dela (□↑) → 'Lägg till på hemskärmen'.","Öppna webbläsarens meny (⋮ eller …) och välj 'Installera app' eller 'Lägg till på startskärmen'.","Redan installerad som app.","Sparas bara på den här enheten."],
da:["Favorit","Favoritter","Installer app","Ingen favoritter endnu. Tryk på ☆ øverst i en beregner.","Fjern","iPhone: Del (□↑) → 'Føj til hjemmeskærm'.","Åbn browsermenuen (⋮ eller …) og vælg 'Installer app' eller 'Føj til startskærm'.","Allerede installeret som app.","Gemmes kun på denne enhed."],
no:["Favoritt","Favoritter","Installer app","Ingen favoritter ennå. Trykk på ☆ øverst i en kalkulator.","Fjern","iPhone: Del (□↑) → 'Legg til på Hjem-skjerm'.","Åpne nettlesermenyen (⋮ eller …) og velg 'Installer app' eller 'Legg til på startskjermen'.","Allerede installert som app.","Lagres bare på denne enheten."]};
T.nb=T.no;var S=T[L2]||T.en;
var SV='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3.5l2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/></svg>';
var LV='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/></svg>';
var AV='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>';
function get(){try{return JSON.parse(localStorage.getItem("hl-favs")||"[]")}catch(e){return[]}}
function put(a){try{localStorage.setItem("hl-favs",JSON.stringify(a.slice(0,60)))}catch(e){}}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
var path=location.pathname.replace(/index\.html$/,"");
var isHub=/^\/([a-z]{2,3}\/)?$/.test(path)||/^\/(ko|en)\/$/.test(path);
var h1=d.querySelector("h1"),title=((h1&&h1.textContent)||d.title.split("|")[0]).replace(/\s+/g," ").trim().slice(0,70);
if(!d.getElementById("hl-tb-css")){var st=d.createElement("style");st.id="hl-tb-css";st.textContent=__CSS__;(d.head||d.documentElement).appendChild(st)}
var host=d.querySelector(".brandbar .in")||d.querySelector(".brand .in");
var bar=d.createElement("div");bar.className="hl-tb";
var star=null;
if(!isHub){star=d.createElement("button");star.type="button";star.className="hl-tb-star";star.innerHTML=SV+'<span class="hl-tb-t">'+esc(S[0])+"</span>";bar.appendChild(star)}
var lst=d.createElement("button");lst.type="button";lst.className="hl-tb-list";lst.setAttribute("aria-label",S[1]);lst.innerHTML=LV+'<span class="hl-tb-t">'+esc(S[1])+'</span><span class="hl-tb-n"></span>';bar.appendChild(lst);
var app=d.createElement("button");app.type="button";app.className="hl-tb-app";app.innerHTML=AV+'<span class="hl-tb-t">'+esc(S[2])+"</span>";
var standalone=(w.matchMedia&&w.matchMedia("(display-mode: standalone)").matches)||navigator.standalone;
if(!standalone)bar.appendChild(app);
if(host){host.appendChild(bar)}else{bar.style.cssText="position:fixed;top:8px;right:8px;z-index:2147482000";d.body.appendChild(bar)}
function sync(){var a=get(),on=a.some(function(x){return x.u===path});if(star){star.setAttribute("aria-pressed",on?"true":"false");star.title=S[0]}
  var n=lst.querySelector(".hl-tb-n");n.textContent=a.length;n.style.display=a.length?"":"none"}
sync();
if(star)star.onclick=function(){var a=get(),i=-1;a.forEach(function(x,k){if(x.u===path)i=k});if(i>=0)a.splice(i,1);else a.unshift({u:path,t:title});put(a);sync();
  try{w.gtag&&gtag("event","fav_"+(i>=0?"remove":"add"))}catch(e){}};
var pane=null;
function close(){if(pane){pane.remove();pane=null}}
lst.onclick=function(e){e.stopPropagation();if(pane){close();return}var a=get();pane=d.createElement("div");pane.className="hl-fav";pane.setAttribute("role","dialog");
  pane.innerHTML="<h3>★ "+esc(S[1])+"</h3>"+(a.length?"<ul>"+a.map(function(x,k){return'<li><a href="'+esc(x.u)+'">'+esc(x.t)+'</a><button type="button" data-k="'+k+'" aria-label="'+esc(S[4])+'">×</button></li>'}).join("")+"</ul>":"<p>"+esc(S[3])+"</p>")+"<p>"+esc(S[8])+"</p>";
  d.body.appendChild(pane);pane.addEventListener("click",function(ev){ev.stopPropagation();var b=ev.target.closest("button[data-k]");if(!b)return;var a=get();a.splice(+b.getAttribute("data-k"),1);put(a);sync();close();lst.click()})};
d.addEventListener("click",close);d.addEventListener("keydown",function(e){if(e.key==="Escape")close()});
var deferred=null,tip=null;
w.addEventListener("beforeinstallprompt",function(e){deferred=e});
w.addEventListener("appinstalled",function(){app.remove()});
function say(m){if(tip)tip.remove();tip=d.createElement("div");tip.className="hl-tb-tip";tip.setAttribute("role","status");tip.textContent=m;d.body.appendChild(tip);setTimeout(function(){tip&&tip.remove();tip=null},9000)}
app.onclick=function(){try{w.gtag&&gtag("event","a2hs_topbar")}catch(e){}
  if(deferred){deferred.prompt();(deferred.userChoice||Promise.resolve({})).then(function(r){if(r&&r.outcome==="accepted")app.remove()});deferred=null;return}
  var ua=navigator.userAgent||"";if(/iPhone|iPad|iPod/.test(ua)){say(S[5]);return}
  say(S[6])};

/* 어두운 배경(풀밭·남색 상자) 위 어두운 글자 → 흰색으로 (모든 페이지) */
function lum(c){var m=c&&c.match(/[\d.]+/g);if(!m)return 1;var a=m.length>3?+m[3]:1;if(a<.5)return -1;return(.2126*m[0]+.7152*m[1]+.0722*m[2])/255}
function bgOf(e){while(e&&e.nodeType===1){var cs=getComputedStyle(e),l=lum(cs.backgroundColor);if(l>=0)return l;if(cs.backgroundImage&&cs.backgroundImage!=="none"&&e!==d.documentElement){var g=cs.backgroundImage.match(/rgba?\([^)]*\)/);if(/gradient/.test(cs.backgroundImage)&&g){var l3=lum(g[0]);if(l3>=0)return l3}return .3}e=e.parentElement}return 1}
function fix(){var all=d.body?d.body.getElementsByTagName("*"):[],i,e,own,n;for(i=0;i<all.length;i++){e=all[i];if(/^(INPUT|SELECT|TEXTAREA|OPTION|SVG|PATH|SCRIPT|STYLE|IMG|CANVAS)$/i.test(e.tagName))continue;
  own=!1;for(n=e.firstChild;n;n=n.nextSibling)if(n.nodeType===3&&n.nodeValue.trim()){own=!0;break}if(!own)continue;
  var c=getComputedStyle(e).color;if(lum(c)>.55)continue;if(bgOf(e)<.36){e.style.setProperty("color","#fff","important");if(e.tagName==="A")e.style.setProperty("text-decoration","underline")}}}
if(d.readyState==="complete")fix();else w.addEventListener("load",fix);setTimeout(fix,2500);

/* 좌우 폭 맞추기: 본문 밖에 붙은 상자(머리 그림·공유·최근 사용·바닥글)를 본문 카드와 같은 좌우 선에 맞춤 */
function align(){try{var m=d.querySelector("main.wrap,main,.wrap");if(!m)return;var k=m.children,ref=null,i;
  for(i=0;i<k.length;i++){var r0=k[i].getBoundingClientRect(),cs0=getComputedStyle(k[i]);if(r0.width>120&&r0.height>40&&cs0.position!=="fixed"&&cs0.position!=="absolute"){ref=r0;break}}
  if(!ref)return;var W=d.documentElement.clientWidth,L=Math.round(ref.left),R=Math.round(W-ref.right);if(L<0||R<0||L+R>W*.5)return;
  var t=d.querySelectorAll("body>header.hero,body>.hl-share,body>.hl-rel,body>footer,body>.hl-recent");
  for(i=0;i<t.length;i++){var e=t[i];e.style.setProperty("box-sizing","border-box","important");e.style.setProperty("width","auto","important");e.style.setProperty("max-width","none","important");
    e.style.setProperty("margin-left",L+"px","important");e.style.setProperty("margin-right",R+"px","important")}}catch(x){}}
if(d.readyState==="complete")align();else w.addEventListener("load",align);setTimeout(align,1200);setTimeout(align,3200);
var at;w.addEventListener("resize",function(){clearTimeout(at);at=setTimeout(align,150)});
})();
'''


def main():
    import json
    n = 0
    for rel in ('assets/app.js', 'ko/assets/app.js'):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            continue
        s = open(p, encoding='utf-8').read()
        if 'hl-topbar v1' in s:
            continue
        open(p, 'a', encoding='utf-8').write('\n' + JS.replace('__CSS__', json.dumps(CSS)))
        n += 1
    p = os.path.join(root, 'assets', 'hl-unify.css')
    if os.path.exists(p):
        s = open(p, encoding='utf-8').read()
        if MARK not in s:
            open(p, 'a', encoding='utf-8').write('\n' + CSS)
            n += 1
    print('topbar patched files:', n)


if __name__ == '__main__':
    main()
