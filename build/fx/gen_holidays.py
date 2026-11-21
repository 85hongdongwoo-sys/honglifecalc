# 나라별 공휴일 페이지 (내년 연도) — 공휴일 표, 다음 공휴일까지 D-day, 연휴·징검다리(브리지) 추천, 연차 계획, 월별 근무일, 캘린더 내보내기
# 데이터: Nager.Date 공개 API (build/fx/fetch_hol.py → _site/hol/<CC>-<YEAR>.json). 사용: python3 build/fx/gen_holidays.py _site
import datetime as dt, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pagekit import B, E, build_page, faq_ld, app_ld, faq_html, register

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
HOL = os.path.join(SITE, 'hol')
THIS = dt.date.today().year
YEAR = THIS + 1 if dt.date.today().month >= 9 else THIS  # 가을부터는 내년 페이지가 검색 대목

C = {  # 폴더: (나라 코드, 언어, 나라 이름)
 'us': ('US', 'en', 'the US'), 'uk': ('GB', 'en', 'the UK'), 'ca': ('CA', 'en', 'Canada'), 'au': ('AU', 'en', 'Australia'), 'ie': ('IE', 'en', 'Ireland'),
 'nz': ('NZ', 'en', 'New Zealand'), 'za': ('ZA', 'en', 'South Africa'), 'sg': ('SG', 'en', 'Singapore'), 'ph': ('PH', 'en', 'the Philippines'),
 'in': ('IN', 'en', 'India'), 'ng': ('NG', 'en', 'Nigeria'),
 'de': ('DE', 'de', 'Deutschland'), 'at': ('AT', 'de', 'Österreich'), 'ch': ('CH', 'de', 'der Schweiz'),
 'fr': ('FR', 'fr', 'France'), 'be': ('BE', 'fr', 'Belgique'),
 'es': ('ES', 'es', 'España'), 'mx': ('MX', 'es', 'México'), 'cl': ('CL', 'es', 'Chile'), 'co': ('CO', 'es', 'Colombia'), 'arg': ('AR', 'es', 'Argentina'),
 'it': ('IT', 'it', 'Italia'), 'nl': ('NL', 'nl', 'Nederland'), 'br': ('BR', 'pt', 'Brasil'), 'pl': ('PL', 'pl', 'Polsce'),
 'se': ('SE', 'sv', 'Sverige'), 'no': ('NO', 'nb', 'Norge'), 'dk': ('DK', 'da', 'Danmark'), 'tr': ('TR', 'tr', 'Türkiye'),
 'id': ('ID', 'id', 'Indonesia'), 'my': ('MY', 'ms', 'Malaysia'), 'jp': ('JP', 'ja', '日本'), 'zh': ('CN', 'zh', '中国'),
}

W = {  # 요일(월~일), 월
 'en': (['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']),
 'de': (['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'], ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']),
 'fr': (['lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.', 'dim.'], ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']),
 'es': (['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom'], ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']),
 'it': (['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom'], ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']),
 'nl': (['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo'], ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']),
 'pt': (['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom'], ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']),
 'pl': (['pon.', 'wt.', 'śr.', 'czw.', 'pt.', 'sob.', 'niedz.'], ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec', 'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień']),
 'sv': (['mån', 'tis', 'ons', 'tors', 'fre', 'lör', 'sön'], ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december']),
 'nb': (['man.', 'tir.', 'ons.', 'tor.', 'fre.', 'lør.', 'søn.'], ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'desember']),
 'da': (['man.', 'tirs.', 'ons.', 'tors.', 'fre.', 'lør.', 'søn.'], ['januar', 'februar', 'marts', 'april', 'maj', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'december']),
 'tr': (['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'], ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']),
 'id': (['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'], ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']),
 'ms': (['Isn', 'Sel', 'Rab', 'Kha', 'Jum', 'Sab', 'Ahd'], ['Januari', 'Februari', 'Mac', 'April', 'Mei', 'Jun', 'Julai', 'Ogos', 'September', 'Oktober', 'November', 'Disember']),
 'ja': (['月', '火', '水', '木', '金', '土', '日'], [f'{i}月' for i in range(1, 13)]),
 'zh': (['周一', '周二', '周三', '周四', '周五', '周六', '周日'], [f'{i}月' for i in range(1, 13)]),
}

T = {
 'en': dict(slug='public-holidays-{y}.html', title='Public Holidays {y} in {n} – Dates, Long Weekends & Working Days',
            desc='All {c} public holidays in {n} for {y} with dates and weekdays, the next holiday countdown, long weekends, the best bridge days to take off, working days per month and a calendar download.',
            h1='<b>Public holidays</b> {y}', sub='Dates, long weekends, bridge days and working days for {n} – with a leave planner.',
            next='Next public holiday', inD='in {d} days', today='today', tbl='Public holidays in {n} {y}', cols=['Date', 'Day', 'Holiday'], reg='regional', all='Nationwide only',
            sum='There are {c} nationwide public holidays in {n} in {y}; {w} of them fall on a weekday (Mon–Fri).',
            longT='Long weekends in {y}', longR='{a} – {b}: {d} days off', bridgeT='Best bridge days to take off in {y}', bridgeR='Take {k} day(s) off ({x}) → {d} days off in a row ({a} – {b})',
            planT='Leave planner', planL='Leave days you can use', planR='With {k} leave days you get {d} days off in total:', wdT='Working days per month in {y}', wdC=['Month', 'Working days', 'Holidays on weekdays'], tot='Total',
            ics='📅 Add all to my calendar (.ics)', src='Holiday data: Nager.Date (open source), checked {s}. Regional holidays and one-off changes can apply – check official announcements.',
            faq=[('How many public holidays are there in {n} in {y}?', 'There are {c} nationwide public holidays in {n} in {y}. {w} of them fall on a weekday, so they reduce the number of working days.'),
                 ('What is a bridge day?', 'A working day between a public holiday and the weekend. Taking just that day off turns a single holiday into a long weekend – this page lists the best ones for {y}.'),
                 ('How many working days are there in {y}?', 'With a Monday–Friday week and nationwide holidays only, {y} has {t} working days in {n}. Regional holidays reduce this further where they apply.')]),
 'de': dict(slug='feiertage-{y}.html', title='Feiertage {y} in {n} – Brückentage, lange Wochenenden & Arbeitstage',
            desc='Alle {c} gesetzlichen Feiertage {y} in {n} mit Datum und Wochentag, Countdown zum nächsten Feiertag, Brückentage, lange Wochenenden, Arbeitstage pro Monat und Kalender-Download.',
            h1='<b>Feiertage</b> {y}', sub='Termine, Brückentage, lange Wochenenden und Arbeitstage – mit Urlaubsplaner.',
            next='Nächster Feiertag', inD='in {d} Tagen', today='heute', tbl='Gesetzliche Feiertage {y} in {n}', cols=['Datum', 'Tag', 'Feiertag'], reg='regional', all='Nur bundesweit',
            sum='In {n} gibt es {y} {c} landesweite Feiertage; {w} davon fallen auf einen Werktag (Mo–Fr).',
            longT='Lange Wochenenden {y}', longR='{a} – {b}: {d} freie Tage', bridgeT='Die besten Brückentage {y}', bridgeR='{k} Urlaubstag(e) nehmen ({x}) → {d} Tage am Stück frei ({a} – {b})',
            planT='Urlaubsplaner', planL='Urlaubstage, die Sie einsetzen möchten', planR='Mit {k} Urlaubstagen haben Sie insgesamt {d} freie Tage:', wdT='Arbeitstage pro Monat {y}', wdC=['Monat', 'Arbeitstage', 'Feiertage an Werktagen'], tot='Summe',
            ics='📅 Alle in meinen Kalender (.ics)', src='Feiertagsdaten: Nager.Date (Open Source), Stand {s}. Regionale Feiertage und Sonderregelungen sind möglich – maßgeblich sind die amtlichen Bekanntmachungen.',
            faq=[('Wie viele Feiertage gibt es {y} in {n}?', '{y} gibt es in {n} {c} landesweite Feiertage. {w} davon fallen auf einen Werktag und verringern die Zahl der Arbeitstage.'),
                 ('Was ist ein Brückentag?', 'Ein Arbeitstag zwischen Feiertag und Wochenende. Wer nur diesen Tag frei nimmt, bekommt ein langes Wochenende – die besten Brückentage {y} stehen auf dieser Seite.'),
                 ('Wie viele Arbeitstage hat {y}?', 'Bei einer 5-Tage-Woche und nur landesweiten Feiertagen hat {y} in {n} {t} Arbeitstage. Regionale Feiertage verringern die Zahl je nach Bundesland bzw. Kanton.')]),
 'fr': dict(slug='jours-feries-{y}.html', title='Jours fériés {y} en {n} – ponts, week-ends prolongés et jours ouvrés',
            desc='Les {c} jours fériés {y} en {n} avec date et jour, compte à rebours, ponts à poser, week-ends prolongés, jours ouvrés par mois et export calendrier.',
            h1='<b>Jours fériés</b> {y}', sub='Dates, ponts, week-ends prolongés et jours ouvrés – avec planificateur de congés.',
            next='Prochain jour férié', inD='dans {d} jours', today='aujourd’hui', tbl='Jours fériés {y} en {n}', cols=['Date', 'Jour', 'Férié'], reg='régional', all='National uniquement',
            sum='La {n} compte {c} jours fériés nationaux en {y} ; {w} tombent un jour de semaine (lun.–ven.).',
            longT='Week-ends prolongés {y}', longR='{a} – {b} : {d} jours de repos', bridgeT='Les meilleurs ponts {y}', bridgeR='Posez {k} jour(s) ({x}) → {d} jours de repos d’affilée ({a} – {b})',
            planT='Planificateur de congés', planL='Jours de congé à poser', planR='Avec {k} jours de congé, vous obtenez {d} jours de repos au total :', wdT='Jours ouvrés par mois en {y}', wdC=['Mois', 'Jours ouvrés', 'Fériés en semaine'], tot='Total',
            ics='📅 Tout ajouter à mon agenda (.ics)', src='Données : Nager.Date (open source), vérifié le {s}. Des jours fériés régionaux peuvent s’appliquer – référez-vous aux textes officiels.',
            faq=[('Combien de jours fériés en {y} en {n} ?', 'La {n} compte {c} jours fériés nationaux en {y}, dont {w} tombent un jour de semaine.'),
                 ('Qu’est-ce qu’un pont ?', 'Un jour travaillé coincé entre un jour férié et le week-end. En le posant, on obtient un long week-end – les meilleurs ponts {y} sont listés ici.'),
                 ('Combien de jours ouvrés en {y} ?', 'Sur la base d’une semaine du lundi au vendredi et des fériés nationaux, {y} compte {t} jours ouvrés en {n}.')]),
 'es': dict(slug='dias-festivos-{y}.html', title='Días festivos {y} en {n} – puentes, fines de semana largos y días laborables',
            desc='Los {c} días festivos {y} en {n} con fecha y día, cuenta atrás, mejores puentes, fines de semana largos, días laborables por mes y descarga para el calendario.',
            h1='<b>Días festivos</b> {y}', sub='Fechas, puentes, fines de semana largos y días laborables – con planificador de vacaciones.',
            next='Próximo festivo', inD='en {d} días', today='hoy', tbl='Días festivos {y} en {n}', cols=['Fecha', 'Día', 'Festivo'], reg='regional', all='Solo nacionales',
            sum='{n} tiene {c} festivos nacionales en {y}; {w} caen en día laborable (lun–vie).',
            longT='Fines de semana largos {y}', longR='{a} – {b}: {d} días libres', bridgeT='Los mejores puentes {y}', bridgeR='Pide {k} día(s) ({x}) → {d} días libres seguidos ({a} – {b})',
            planT='Planificador de vacaciones', planL='Días de vacaciones a usar', planR='Con {k} días de vacaciones tienes {d} días libres en total:', wdT='Días laborables por mes {y}', wdC=['Mes', 'Días laborables', 'Festivos entre semana'], tot='Total',
            ics='📅 Añadir todo a mi calendario (.ics)', src='Datos: Nager.Date (código abierto), revisado el {s}. Puede haber festivos regionales o cambios – consulta el calendario oficial.',
            faq=[('¿Cuántos festivos hay en {y} en {n}?', '{n} tiene {c} festivos nacionales en {y}; {w} caen entre semana.'),
                 ('¿Qué es un puente?', 'Un día laborable entre un festivo y el fin de semana. Si lo pides libre, consigues un fin de semana largo; aquí están los mejores de {y}.'),
                 ('¿Cuántos días laborables tiene {y}?', 'Con semana de lunes a viernes y solo festivos nacionales, {y} tiene {t} días laborables en {n}.')]),
 'it': dict(slug='giorni-festivi-{y}.html', title='Giorni festivi {y} in {n} – ponti, weekend lunghi e giorni lavorativi',
            desc='Tutti i {c} giorni festivi {y} in {n} con data e giorno, conto alla rovescia, ponti migliori, weekend lunghi, giorni lavorativi per mese e calendario da scaricare.',
            h1='<b>Giorni festivi</b> {y}', sub='Date, ponti, weekend lunghi e giorni lavorativi – con pianificatore delle ferie.',
            next='Prossima festività', inD='tra {d} giorni', today='oggi', tbl='Giorni festivi {y} in {n}', cols=['Data', 'Giorno', 'Festività'], reg='regionale', all='Solo nazionali',
            sum='In {n} ci sono {c} festività nazionali nel {y}; {w} cadono in un giorno feriale (lun–ven).',
            longT='Weekend lunghi {y}', longR='{a} – {b}: {d} giorni liberi', bridgeT='I ponti migliori del {y}', bridgeR='Prendi {k} giorno/i ({x}) → {d} giorni liberi di fila ({a} – {b})',
            planT='Pianificatore ferie', planL='Giorni di ferie da usare', planR='Con {k} giorni di ferie ottieni {d} giorni liberi in totale:', wdT='Giorni lavorativi per mese {y}', wdC=['Mese', 'Giorni lavorativi', 'Festivi infrasettimanali'], tot='Totale',
            ics='📅 Aggiungi tutto al calendario (.ics)', src='Dati: Nager.Date (open source), verificato il {s}. Possono valere feste patronali o modifiche – fa fede il calendario ufficiale.',
            faq=[('Quanti giorni festivi ci sono nel {y} in {n}?', 'In {n} ci sono {c} festività nazionali nel {y}; {w} cadono in un giorno feriale.'),
                 ('Cos’è un ponte?', 'Un giorno lavorativo tra una festività e il weekend: prendendolo di ferie si ottiene un weekend lungo. Qui trovi i migliori del {y}.'),
                 ('Quanti giorni lavorativi ha il {y}?', 'Con settimana dal lunedì al venerdì e solo festività nazionali, il {y} ha {t} giorni lavorativi in {n}.')]),
 'nl': dict(slug='feestdagen-{y}.html', title='Feestdagen {y} in {n} – vrije dagen, lange weekenden en werkdagen',
            desc='Alle {c} officiële feestdagen {y} in {n} met datum en weekdag, aftellen, slimme brugdagen, lange weekenden, werkdagen per maand en agenda-download.',
            h1='<b>Feestdagen</b> {y}', sub='Data, brugdagen, lange weekenden en werkdagen – met verlofplanner.',
            next='Volgende feestdag', inD='over {d} dagen', today='vandaag', tbl='Feestdagen {y} in {n}', cols=['Datum', 'Dag', 'Feestdag'], reg='regionaal', all='Alleen landelijk',
            sum='{n} heeft in {y} {c} landelijke feestdagen; {w} vallen op een werkdag (ma–vr).',
            longT='Lange weekenden {y}', longR='{a} – {b}: {d} dagen vrij', bridgeT='Beste brugdagen {y}', bridgeR='Neem {k} dag(en) vrij ({x}) → {d} dagen achter elkaar vrij ({a} – {b})',
            planT='Verlofplanner', planL='Verlofdagen die je wilt inzetten', planR='Met {k} verlofdagen ben je in totaal {d} dagen vrij:', wdT='Werkdagen per maand {y}', wdC=['Maand', 'Werkdagen', 'Feestdagen op werkdagen'], tot='Totaal',
            ics='📅 Alles in mijn agenda (.ics)', src='Gegevens: Nager.Date (open source), gecontroleerd op {s}. Of een feestdag een vrije dag is, hangt af van je cao of werkgever.',
            faq=[('Hoeveel feestdagen zijn er in {y} in {n}?', '{n} heeft in {y} {c} landelijke feestdagen; {w} vallen op een werkdag.'),
                 ('Wat is een brugdag?', 'Een werkdag tussen een feestdag en het weekend. Neem je die vrij, dan heb je een lang weekend – de beste van {y} staan hier.'),
                 ('Hoeveel werkdagen heeft {y}?', 'Bij een werkweek van maandag tot en met vrijdag en alleen landelijke feestdagen heeft {y} {t} werkdagen in {n}.')]),
 'pt': dict(slug='feriados-{y}.html', title='Feriados {y} no {n} – emendas, feriadões e dias úteis',
            desc='Os {c} feriados nacionais de {y} no {n} com data e dia da semana, contagem regressiva, melhores emendas, feriadões, dias úteis por mês e download para a agenda.',
            h1='<b>Feriados</b> {y}', sub='Datas, emendas, feriadões e dias úteis – com planejador de férias.',
            next='Próximo feriado', inD='em {d} dias', today='hoje', tbl='Feriados {y} no {n}', cols=['Data', 'Dia', 'Feriado'], reg='regional', all='Só nacionais',
            sum='O {n} tem {c} feriados nacionais em {y}; {w} caem em dia útil (seg–sex).',
            longT='Feriadões {y}', longR='{a} – {b}: {d} dias de folga', bridgeT='Melhores emendas {y}', bridgeR='Tire {k} dia(s) ({x}) → {d} dias de folga seguidos ({a} – {b})',
            planT='Planejador de folgas', planL='Dias de folga que você pode usar', planR='Com {k} dias de folga você tem {d} dias livres no total:', wdT='Dias úteis por mês {y}', wdC=['Mês', 'Dias úteis', 'Feriados em dia útil'], tot='Total',
            ics='📅 Adicionar tudo à agenda (.ics)', src='Dados: Nager.Date (código aberto), verificado em {s}. Feriados estaduais e municipais podem valer – confira o calendário oficial.',
            faq=[('Quantos feriados nacionais tem {y} no {n}?', 'O {n} tem {c} feriados nacionais em {y}; {w} caem em dia útil.'),
                 ('O que é emenda de feriado?', 'Um dia útil entre o feriado e o fim de semana. Ao folgar nesse dia, você ganha um feriadão – as melhores emendas de {y} estão aqui.'),
                 ('Quantos dias úteis tem {y}?', 'Com semana de segunda a sexta e só feriados nacionais, {y} tem {t} dias úteis no {n}.')]),
 'pl': dict(slug='dni-wolne-{y}.html', title='Dni wolne od pracy {y} w {n} – długie weekendy i dni robocze',
            desc='Wszystkie {c} dni ustawowo wolne {y} w {n} z datą i dniem tygodnia, odliczaniem, długimi weekendami, najlepszymi dniami do wzięcia urlopu, dniami roboczymi i plikiem do kalendarza.',
            h1='<b>Dni wolne</b> {y}', sub='Daty, długie weekendy, mostki i dni robocze – z planerem urlopu.',
            next='Najbliższe święto', inD='za {d} dni', today='dziś', tbl='Dni ustawowo wolne {y} w {n}', cols=['Data', 'Dzień', 'Święto'], reg='regionalne', all='Tylko ogólnopolskie',
            sum='W {n} w {y} r. jest {c} dni ustawowo wolnych; {w} przypada w dzień roboczy (pon.–pt.).',
            longT='Długie weekendy {y}', longR='{a} – {b}: {d} dni wolnego', bridgeT='Najlepsze mostki {y}', bridgeR='Weź {k} dz. urlopu ({x}) → {d} dni wolnego z rzędu ({a} – {b})',
            planT='Planer urlopu', planL='Dni urlopu do wykorzystania', planR='Z {k} dniami urlopu masz łącznie {d} dni wolnego:', wdT='Dni robocze w miesiącach {y}', wdC=['Miesiąc', 'Dni robocze', 'Święta w dni robocze'], tot='Razem',
            ics='📅 Dodaj wszystko do kalendarza (.ics)', src='Dane: Nager.Date (open source), sprawdzono {s}. Za święto w sobotę przysługuje dzień wolny – wg przepisów Kodeksu pracy.',
            faq=[('Ile dni wolnych jest w {y} r. w {n}?', 'W {n} w {y} r. jest {c} dni ustawowo wolnych; {w} przypada w dzień roboczy.'),
                 ('Co to jest mostek?', 'Dzień roboczy między świętem a weekendem. Biorąc go wolny, zyskujesz długi weekend – najlepsze mostki {y} są tutaj.'),
                 ('Ile dni roboczych ma {y} r.?', 'Przy tygodniu pon.–pt. i świętach ogólnopolskich {y} r. ma {t} dni roboczych (bez odbioru za święto w sobotę).')]),
 'sv': dict(slug='helgdagar-{y}.html', title='Röda dagar {y} i {n} – klämdagar, långhelger och arbetsdagar',
            desc='Alla {c} röda dagar {y} i {n} med datum och veckodag, nedräkning, bästa klämdagarna, långhelger, arbetsdagar per månad och kalenderfil.',
            h1='<b>Röda dagar</b> {y}', sub='Datum, klämdagar, långhelger och arbetsdagar – med semesterplanerare.',
            next='Nästa röda dag', inD='om {d} dagar', today='i dag', tbl='Röda dagar {y} i {n}', cols=['Datum', 'Dag', 'Helgdag'], reg='regional', all='Bara rikstäckande',
            sum='{n} har {c} allmänna helgdagar {y}; {w} infaller på en vardag (mån–fre).',
            longT='Långhelger {y}', longR='{a} – {b}: {d} lediga dagar', bridgeT='Bästa klämdagarna {y}', bridgeR='Ta {k} semesterdag(ar) ({x}) → {d} lediga dagar i rad ({a} – {b})',
            planT='Semesterplanerare', planL='Semesterdagar du vill använda', planR='Med {k} semesterdagar blir du ledig {d} dagar totalt:', wdT='Arbetsdagar per månad {y}', wdC=['Månad', 'Arbetsdagar', 'Helgdagar på vardagar'], tot='Totalt',
            ics='📅 Lägg till alla i kalendern (.ics)', src='Data: Nager.Date (öppen källkod), kontrollerad {s}. Midsommarafton, julafton och nyårsafton är ofta lediga enligt avtal men inte röda dagar.',
            faq=[('Hur många röda dagar finns det {y}?', '{n} har {c} allmänna helgdagar {y}; {w} infaller på en vardag.'),
                 ('Vad är en klämdag?', 'En vardag mellan en röd dag och helgen. Tar du ledigt den dagen får du en långhelg – årets bästa klämdagar står här.'),
                 ('Hur många arbetsdagar har {y}?', 'Med måndag–fredag och allmänna helgdagar har {y} {t} arbetsdagar i {n}.')]),
 'nb': dict(slug='helligdager-{y}.html', title='Helligdager {y} i {n} – inneklemte dager, langhelger og arbeidsdager',
            desc='Alle {c} offentlige helligdager {y} i {n} med dato og ukedag, nedtelling, beste inneklemte dager, langhelger, arbeidsdager per måned og kalenderfil.',
            h1='<b>Helligdager</b> {y}', sub='Datoer, inneklemte dager, langhelger og arbeidsdager – med ferieplanlegger.',
            next='Neste helligdag', inD='om {d} dager', today='i dag', tbl='Helligdager {y} i {n}', cols=['Dato', 'Dag', 'Helligdag'], reg='regional', all='Kun nasjonale',
            sum='{n} har {c} offentlige helligdager i {y}; {w} faller på en ukedag (man–fre).',
            longT='Langhelger {y}', longR='{a} – {b}: {d} fridager', bridgeT='Beste inneklemte dager {y}', bridgeR='Ta {k} feriedag(er) ({x}) → {d} fridager på rad ({a} – {b})',
            planT='Ferieplanlegger', planL='Feriedager du vil bruke', planR='Med {k} feriedager får du {d} fridager totalt:', wdT='Arbeidsdager per måned {y}', wdC=['Måned', 'Arbeidsdager', 'Helligdager på ukedager'], tot='Totalt',
            ics='📅 Legg alle i kalenderen (.ics)', src='Data: Nager.Date (åpen kildekode), sjekket {s}.',
            faq=[('Hvor mange helligdager er det i {y}?', '{n} har {c} offentlige helligdager i {y}; {w} faller på en ukedag.'),
                 ('Hva er en inneklemt dag?', 'En arbeidsdag mellom en helligdag og helgen. Tar du fri den dagen, får du langhelg – årets beste står her.'),
                 ('Hvor mange arbeidsdager er det i {y}?', 'Med mandag–fredag og nasjonale helligdager har {y} {t} arbeidsdager i {n}.')]),
 'da': dict(slug='helligdage-{y}.html', title='Helligdage {y} i {n} – inneklemte dage, lange weekender og arbejdsdage',
            desc='Alle {c} helligdage {y} i {n} med dato og ugedag, nedtælling, bedste inneklemte dage, lange weekender, arbejdsdage pr. måned og kalenderfil.',
            h1='<b>Helligdage</b> {y}', sub='Datoer, lange weekender og arbejdsdage – med ferieplanlægger.',
            next='Næste helligdag', inD='om {d} dage', today='i dag', tbl='Helligdage {y} i {n}', cols=['Dato', 'Dag', 'Helligdag'], reg='regional', all='Kun landsdækkende',
            sum='{n} har {c} helligdage i {y}; {w} falder på en hverdag (man–fre).',
            longT='Lange weekender {y}', longR='{a} – {b}: {d} fridage', bridgeT='Bedste inneklemte dage {y}', bridgeR='Tag {k} feriedag(e) ({x}) → {d} fridage i træk ({a} – {b})',
            planT='Ferieplanlægger', planL='Feriedage du vil bruge', planR='Med {k} feriedage får du {d} fridage i alt:', wdT='Arbejdsdage pr. måned {y}', wdC=['Måned', 'Arbejdsdage', 'Helligdage på hverdage'], tot='I alt',
            ics='📅 Føj alle til kalenderen (.ics)', src='Data: Nager.Date (open source), tjekket {s}. Store bededag er afskaffet som helligdag fra 2024.',
            faq=[('Hvor mange helligdage er der i {y}?', '{n} har {c} helligdage i {y}; {w} falder på en hverdag.'),
                 ('Hvad er en inneklemt dag?', 'En arbejdsdag mellem en helligdag og weekenden. Holder du fri den dag, får du en lang weekend – årets bedste står her.'),
                 ('Hvor mange arbejdsdage er der i {y}?', 'Med mandag–fredag og helligdage har {y} {t} arbejdsdage i {n}.')]),
 'tr': dict(slug='resmi-tatiller-{y}.html', title='{y} Resmi Tatiller ({n}) – Köprü Günleri, Uzun Hafta Sonları ve İş Günleri',
            desc='{y} yılındaki {c} resmi tatil, tarih ve gün, geri sayım, köprü günleri, uzun hafta sonları, aylara göre iş günü sayısı ve takvime ekleme.',
            h1='<b>Resmi tatiller</b> {y}', sub='Tarihler, köprü günleri, uzun hafta sonları ve iş günleri – izin planlayıcı ile.',
            next='Sıradaki resmi tatil', inD='{d} gün sonra', today='bugün', tbl='{y} resmi tatilleri ({n})', cols=['Tarih', 'Gün', 'Tatil'], reg='bölgesel', all='Yalnızca ulusal',
            sum='{n} genelinde {y} yılında {c} resmi tatil var; {w} tanesi hafta içine denk geliyor.',
            longT='{y} uzun hafta sonları', longR='{a} – {b}: {d} gün tatil', bridgeT='{y} en iyi köprü günleri', bridgeR='{k} gün izin al ({x}) → art arda {d} gün tatil ({a} – {b})',
            planT='İzin planlayıcı', planL='Kullanabileceğin izin günü', planR='{k} gün izinle toplam {d} gün tatil:', wdT='{y} aylara göre iş günleri', wdC=['Ay', 'İş günü', 'Hafta içi tatiller'], tot='Toplam',
            ics='📅 Hepsini takvime ekle (.ics)', src='Veri: Nager.Date (açık kaynak), kontrol tarihi {s}. Arife yarım günleri ve idari izinler resmi kararlara bağlıdır.',
            faq=[('{y} yılında kaç resmi tatil var?', '{n} genelinde {y} yılında {c} resmi tatil var; {w} tanesi hafta içine denk geliyor.'),
                 ('Köprü günü nedir?', 'Resmi tatil ile hafta sonu arasında kalan iş günüdür. O günü izinli geçirirsen uzun bir hafta sonu yaparsın; {y} için en iyileri burada.'),
                 ('{y} yılında kaç iş günü var?', 'Pazartesi–cuma çalışma ve ulusal tatillere göre {y} yılında {t} iş günü vardır.')]),
 'id': dict(slug='hari-libur-{y}.html', title='Hari Libur Nasional {y} – Tanggal Merah, Long Weekend & Hari Kerja ({n})',
            desc='Daftar {c} hari libur nasional {y} di {n} lengkap dengan tanggal dan hari, hitung mundur, long weekend, hari kejepit terbaik, hari kerja per bulan, dan unduh kalender.',
            h1='<b>Hari libur</b> {y}', sub='Tanggal merah, long weekend, hari kejepit, dan hari kerja – dengan perencana cuti.',
            next='Libur berikutnya', inD='{d} hari lagi', today='hari ini', tbl='Hari libur nasional {y} di {n}', cols=['Tanggal', 'Hari', 'Libur'], reg='regional', all='Hanya nasional',
            sum='{n} memiliki {c} hari libur nasional pada {y}; {w} jatuh pada hari kerja (Sen–Jum).',
            longT='Long weekend {y}', longR='{a} – {b}: {d} hari libur', bridgeT='Hari kejepit terbaik {y}', bridgeR='Ambil cuti {k} hari ({x}) → libur {d} hari berturut-turut ({a} – {b})',
            planT='Perencana cuti', planL='Jumlah cuti yang bisa dipakai', planR='Dengan {k} hari cuti, total libur {d} hari:', wdT='Hari kerja per bulan {y}', wdC=['Bulan', 'Hari kerja', 'Libur di hari kerja'], tot='Total',
            ics='📅 Tambahkan semua ke kalender (.ics)', src='Data: Nager.Date (sumber terbuka), dicek {s}. Cuti bersama ditetapkan lewat SKB 3 Menteri – cek pengumuman resmi.',
            faq=[('Ada berapa hari libur nasional {y}?', '{n} memiliki {c} hari libur nasional pada {y}; {w} jatuh pada hari kerja.'),
                 ('Apa itu hari kejepit?', 'Hari kerja di antara hari libur dan akhir pekan. Jika mengambil cuti di hari itu, Anda mendapat long weekend – yang terbaik di {y} ada di sini.'),
                 ('Berapa hari kerja di {y}?', 'Dengan lima hari kerja (Senin–Jumat) dan libur nasional, {y} memiliki {t} hari kerja.')]),
 'ms': dict(slug='cuti-umum-{y}.html', title='Cuti Umum {y} {n} – Hujung Minggu Panjang & Hari Bekerja',
            desc='Senarai {c} cuti umum {y} di {n} dengan tarikh dan hari, kiraan detik, hujung minggu panjang, hari terbaik untuk ambil cuti, hari bekerja sebulan dan muat turun kalendar.',
            h1='<b>Cuti umum</b> {y}', sub='Tarikh, hujung minggu panjang dan hari bekerja – dengan perancang cuti.',
            next='Cuti umum seterusnya', inD='{d} hari lagi', today='hari ini', tbl='Cuti umum {y} di {n}', cols=['Tarikh', 'Hari', 'Cuti'], reg='negeri', all='Kebangsaan sahaja',
            sum='{n} mempunyai {c} cuti umum kebangsaan pada {y}; {w} jatuh pada hari bekerja (Isn–Jum).',
            longT='Hujung minggu panjang {y}', longR='{a} – {b}: {d} hari cuti', bridgeT='Hari terbaik untuk ambil cuti {y}', bridgeR='Ambil {k} hari cuti ({x}) → {d} hari cuti berturut-turut ({a} – {b})',
            planT='Perancang cuti', planL='Hari cuti tahunan yang boleh digunakan', planR='Dengan {k} hari cuti, jumlah cuti {d} hari:', wdT='Hari bekerja sebulan {y}', wdC=['Bulan', 'Hari bekerja', 'Cuti pada hari bekerja'], tot='Jumlah',
            ics='📅 Tambah semua ke kalendar (.ics)', src='Data: Nager.Date (sumber terbuka), disemak {s}. Cuti negeri dan pengumuman kerajaan boleh berubah.',
            faq=[('Berapa banyak cuti umum pada {y}?', '{n} mempunyai {c} cuti umum kebangsaan pada {y}; {w} jatuh pada hari bekerja.'),
                 ('Bila hujung minggu panjang?', 'Senarai hujung minggu panjang dan hari terbaik untuk ambil cuti {y} ada di halaman ini.'),
                 ('Berapa hari bekerja pada {y}?', 'Dengan minggu Isnin–Jumaat dan cuti kebangsaan, {y} mempunyai {t} hari bekerja.')]),
 'ja': dict(slug='shukujitsu-{y}.html', title='{y}年の祝日一覧 – 連休・有給で大型連休にする日・営業日数（{n}）',
            desc='{y}年の{n}の祝日{c}日を日付・曜日つきで一覧。次の祝日までのカウントダウン、3連休、有給を取ると大型連休になる日、月別の営業日数、カレンダー登録も。',
            h1='{y}年の<b>祝日</b>', sub='祝日・連休・有給の取りどき・営業日数がひと目でわかる。',
            next='次の祝日', inD='あと{d}日', today='今日', tbl='{y}年の祝日一覧', cols=['日付', '曜日', '祝日'], reg='地域', all='全国のみ',
            sum='{y}年の{n}の祝日は{c}日で、そのうち{w}日が平日（月〜金）です。',
            longT='{y}年の連休', longR='{a}〜{b}：{d}連休', bridgeT='{y}年 有給を取ると大型連休になる日', bridgeR='{x}に{k}日休む → {d}連休（{a}〜{b}）',
            planT='有給プランナー', planL='使える有給休暇の日数', planR='有給{k}日で合計{d}日休めます：', wdT='{y}年の月別営業日数', wdC=['月', '営業日', '平日の祝日'], tot='合計',
            ics='📅 カレンダーにまとめて登録（.ics）', src='祝日データ：Nager.Date（オープンソース）、{s}確認。正式な祝日は内閣府の発表をご確認ください。',
            faq=[('{y}年の祝日は何日？', '{y}年の祝日は{c}日で、そのうち{w}日が平日にあたります。'),
                 ('有給を取るならいつがお得？', '祝日と週末の間の平日に有給を取ると連休が長くなります。{y}年のおすすめ日はこのページに載せています。'),
                 ('{y}年の営業日数は？', '土日と祝日を除くと、{y}年の営業日は{t}日です（年末年始休暇は含みません）。')]),
 'zh': dict(slug='jiejiari-{y}.html', title='{y}年法定节假日 – 放假安排、长假与工作日天数（{n}）',
            desc='{y}年{n}法定节假日{c}天的日期与星期、距离下一个假日的倒计时、长周末、请假拼长假建议、每月工作日天数，并可导入日历。',
            h1='{y}年<b>法定节假日</b>', sub='日期、长假、请假攻略和工作日天数一目了然。',
            next='下一个节假日', inD='还有{d}天', today='今天', tbl='{y}年法定节假日', cols=['日期', '星期', '节日'], reg='地区', all='仅全国',
            sum='{y}年{n}共有{c}个法定节假日，其中{w}个在工作日（周一至周五）。',
            longT='{y}年长假', longR='{a} – {b}：连休{d}天', bridgeT='{y}年请假拼长假推荐', bridgeR='请假{k}天（{x}）→ 连休{d}天（{a} – {b}）',
            planT='请假规划', planL='可用年假天数', planR='用{k}天年假，共可休息{d}天：', wdT='{y}年每月工作日', wdC=['月份', '工作日', '工作日内的假日'], tot='合计',
            ics='📅 全部导入日历（.ics）', src='数据：Nager.Date（开源），{s}核对。中国的调休安排以国务院办公厅通知为准，本页未计入调休上班日。',
            faq=[('{y}年有多少个法定节假日？', '{y}年{n}共有{c}个法定节假日，其中{w}个在工作日。'),
                 ('怎么请假最划算？', '在节假日与周末之间的工作日请假可以拼成长假，本页列出了{y}年的推荐日期。'),
                 ('{y}年有多少个工作日？', '按周一至周五计算并扣除法定节假日，{y}年约有{t}个工作日（未计入调休）。')]),
}


def fmt_d(d, lang):
    wk, mo = W[lang]
    if lang in ('ja', 'zh'):
        return f'{d.month}月{d.day}日'
    if lang == 'en':
        return f'{mo[d.month - 1][:3]} {d.day}'
    if lang in ('de', 'nb', 'da', 'pl'):
        return f'{d.day}. {mo[d.month - 1]}'
    return f'{d.day} {mo[d.month - 1]}'


def load(cc, y):
    p = os.path.join(HOL, f'{cc}-{y}.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def off_days(y, nat):
    s = set()
    d = dt.date(y, 1, 1)
    while d.year == y:
        if d.weekday() >= 5 or d in nat:
            s.add(d)
        d += dt.timedelta(1)
    return s


def blocks(y, off):
    out, d, cur = [], dt.date(y, 1, 1), None
    while d.year == y:
        if d in off:
            cur = [d, d] if not cur else [cur[0], d]
        elif cur:
            out.append(cur); cur = None
        d += dt.timedelta(1)
    if cur:
        out.append(cur)
    return out


def bridges(y, off, nat):
    """휴일 블록 사이의 1~2일 근무일을 쉬면 생기는 연휴 (공휴일이 낀 경우만)"""
    bl = blocks(y, off)
    res = []
    for i in range(len(bl) - 1):
        gap = (bl[i + 1][0] - bl[i][1]).days - 1
        if 1 <= gap <= 2:
            a, b = bl[i][0], bl[i + 1][1]
            if not any(a <= h <= b for h in nat):
                continue
            days = [bl[i][1] + dt.timedelta(k + 1) for k in range(gap)]
            res.append({'k': gap, 'x': days, 'a': a, 'b': b, 'd': (b - a).days + 1})
    res.sort(key=lambda r: (-r['d'] / r['k'], -r['d']))
    return res


def build(folder):
    cc, lang, nm = C[folder]
    t = T[lang]
    H = {y: load(cc, y) for y in (YEAR - 1, YEAR)}
    if not H[YEAR]:
        return None
    hs = H[YEAR]
    nat = {dt.date.fromisoformat(h['date']) for h in hs if h.get('global', True)}
    natlist = sorted((h for h in hs if h.get('global', True)), key=lambda h: h['date'])
    natn = sorted({h['date'] for h in hs if h.get('global', True)})
    c = len(natn)
    wkd = sum(1 for d in natn if dt.date.fromisoformat(d).weekday() < 5)
    off = off_days(YEAR, nat)
    total_wd = sum(1 for k in range(366) if (dt.date(YEAR, 1, 1) + dt.timedelta(k)).year == YEAR and (dt.date(YEAR, 1, 1) + dt.timedelta(k)) not in off)
    F = lambda s: s.replace('{y}', str(YEAR)).replace('{n}', nm).replace('{c}', str(c)).replace('{w}', str(wkd)).replace('{t}', str(total_wd)).replace('{s}', dt.date.today().isoformat())
    wk = W[lang][0]
    rows = ''
    seen = set()
    for h in sorted(hs, key=lambda h: h['date']):
        d = dt.date.fromisoformat(h['date'])
        key = (h['date'], h['localName'])
        if key in seen:
            continue
        seen.add(key)
        regional = not h.get('global', True)
        nmx = h['localName'] if lang != 'en' else h['name']
        alt = h['name'] if lang != 'en' and h['name'] != h['localName'] else ''
        regs = ', '.join(x.split('-')[-1] for x in (h.get('counties') or [])[:12])
        rows += (f'<tr data-d="{h["date"]}"{" class=hd-reg" if regional else ""}><td>{fmt_d(d, lang)}</td><td>{wk[d.weekday()]}</td><td><b>{E(nmx)}</b>'
                 + (f'<small>{E(alt)}</small>' if alt else '') + (f'<small class="hd-r">{E(t["reg"])}: {E(regs)}</small>' if regional and regs else '') + '</td></tr>')
    lw = [b for b in blocks(YEAR, off) if (b[1] - b[0]).days + 1 >= 3]
    longs = ''.join(f'<li>{E(F(t["longR"]).replace("{a}", fmt_d(a, lang)).replace("{b}", fmt_d(b, lang)).replace("{d}", str((b - a).days + 1)))}</li>' for a, b in lw)
    br = bridges(YEAR, off, nat)[:8]
    brs = ''.join(f'<li>{E(F(t["bridgeR"]).replace("{k}", str(r["k"])).replace("{x}", ", ".join(fmt_d(x, lang) for x in r["x"])).replace("{a}", fmt_d(r["a"], lang)).replace("{b}", fmt_d(r["b"], lang)).replace("{d}", str(r["d"])))}</li>' for r in br)
    mo = W[lang][1]
    wd_rows, tot = '', 0
    for m in range(1, 13):
        days = [dt.date(YEAR, m, 1) + dt.timedelta(k) for k in range(31) if (dt.date(YEAR, m, 1) + dt.timedelta(k)).month == m]
        w_ = sum(1 for d in days if d not in off)
        hw = sum(1 for d in days if d in nat and d.weekday() < 5)
        tot += w_
        wd_rows += f'<tr><td>{E(mo[m - 1])}</td><td><b>{w_}</b></td><td>{hw}</td></tr>'
    wd_rows += f'<tr class="hd-tot"><td>{E(t["tot"])}</td><td><b>{tot}</b></td><td>{wkd}</td></tr>'
    faq = [(F(q), F(a)) for q, a in t['faq']]
    slug = t['slug'].replace('{y}', str(YEAR))
    url = f'{B}/{folder}/{slug}'
    has_reg = any(not h.get('global', True) for h in hs)
    body = (f'<header class="hero"><div class="in"><span class="year">{YEAR}</span><h1>{F(t["h1"])}</h1><p>{E(F(t["sub"]))}</p></div></header>\n<main class="wrap">\n'
            f'<section class="card hd-next" id="hd-next"><span>{E(t["next"])}</span><b id="hd-nn">–</b><em id="hd-nd"></em></section>\n'
            f'<section class="card"><h2>{E(F(t["tbl"]))}</h2><p>{E(F(t["sum"]))}</p>'
            + (f'<label class="hd-sw"><input type="checkbox" id="hd-nat"> {E(t["all"])}</label>' if has_reg else '') +
            f'<div style="overflow-x:auto"><table class="hd-t"><thead><tr>' + ''.join(f'<th>{E(x)}</th>' for x in t['cols']) + f'</tr></thead><tbody>{rows}</tbody></table></div>'
            f'<button type="button" class="hd-ics" id="hd-ics">{E(t["ics"])}</button></section>\n'
            f'<section class="card"><h2>{E(F(t["bridgeT"]))}</h2><ol class="hd-l">{brs}</ol>'
            f'<div class="hd-plan"><h3>{E(t["planT"])}</h3><label class="f"><span>{E(t["planL"])}</span><input id="hd-k" inputmode="numeric" value="3"></label><div id="hd-pr"></div></div></section>\n'
            f'<section class="card"><h2>{E(F(t["longT"]))}</h2><ul class="hd-l">{longs}</ul></section>\n'
            f'<section class="card"><h2>{E(F(t["wdT"]))}</h2><table class="hd-t hd-w"><thead><tr>' + ''.join(f'<th>{E(x)}</th>' for x in t['wdC']) + f'</tr></thead><tbody>{wd_rows}</tbody></table>'
            f'<p class="hd-src">{E(F(t["src"]))}</p></section>\n' + faq_html(faq) + '\n</main>')
    css = ('<style id="hd-css">.hd-next{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px}.hd-next span{font-size:14px;color:#6E6E73;width:100%}.hd-next b{font-size:24px;color:#1D1D1F}.hd-next em{font-style:normal;font-weight:800;color:#2F6B2A;font-size:18px}'
           '.hd-t{width:100%;border-collapse:collapse;font-size:15px}.hd-t th,.hd-t td{padding:10px 6px;border-bottom:.5px solid rgba(60,60,67,.18);text-align:left;vertical-align:top}.hd-t thead th{font-size:12.5px;color:#6E6E73;font-weight:600}'
           '.hd-t td:first-child{white-space:nowrap;font-variant-numeric:tabular-nums}.hd-t td small{display:block;font-size:12.5px;color:#6E6E73}.hd-t small.hd-r{color:#8A6414}.hd-t tr.hd-reg td{color:#6E6E73}'
           '.hd-t tr.hd-past td{opacity:.45}.hd-t tr.hd-on td{background:#EEF7EC}.hd-w td:nth-child(2),.hd-w td:nth-child(3),.hd-w th:nth-child(2),.hd-w th:nth-child(3){text-align:right}.hd-tot td{font-weight:800}'
           '.hd-l{margin:0;padding-left:20px;line-height:1.6}.hd-l li{margin:6px 0}.hd-plan{margin-top:16px;padding-top:12px;border-top:.5px solid rgba(60,60,67,.18)}.hd-plan h3{margin:0 0 8px}'
           '#hd-pr{font-size:15px;line-height:1.6}#hd-pr b{color:#2F6B2A}.hd-ics{margin-top:12px;font:inherit;font-weight:700;padding:12px 16px;border-radius:12px;border:0;background:#F2F2F7;cursor:pointer;width:100%}'
           '.card label.hd-sw{display:flex!important;flex-direction:row!important;align-items:center;gap:10px;font-size:15px;font-weight:600;margin:6px 0 10px;min-height:40px;cursor:pointer}.card label.hd-sw input{width:22px!important;height:22px;min-height:0!important;margin:0;padding:0!important;accent-color:#2F6B2A;flex:none}.hd-src{font-size:13px;color:#6E6E73;margin-top:12px}</style>')
    cfg = {'y': YEAR, 'lang': lang, 'loc': None, 'h': [[h['date'], h['localName'] if lang != 'en' else h['name'], 1 if h.get('global', True) else 0] for h in hs],
           'nat': natn, 't': {k: F(t[k]) for k in ('inD', 'today', 'planR', 'tbl')}, 'name': nm, 'slug': slug}
    js = r'''<script>(function(){var C=window.HDCFG,$=function(i){return document.getElementById(i)};var L=document.documentElement.lang||'en';
function D(s){var p=s.split('-');return new Date(+p[0],+p[1]-1,+p[2])}var now=new Date();now.setHours(0,0,0,0);
var up=C.h.filter(function(h){return h[2]&&D(h[0])>=now}).sort(function(a,b){return a[0]<b[0]?-1:1})[0];
if(up){var dd=Math.round((D(up[0])-now)/864e5);$('hd-nn').textContent=up[1]+' · '+D(up[0]).toLocaleDateString(L,{weekday:'short',month:'long',day:'numeric'});$('hd-nd').textContent=dd?C.t.inD.replace('{d}',dd):C.t.today;}else{$('hd-next').style.display='none'}
document.querySelectorAll('.hd-t tbody tr[data-d]').forEach(function(r){var d=D(r.dataset.d);if(d<now)r.classList.add('hd-past');if(up&&r.dataset.d===up[0])r.classList.add('hd-on')});
var nb=$('hd-nat');if(nb)nb.addEventListener('change',function(){document.querySelectorAll('tr.hd-reg').forEach(function(r){r.style.display=nb.checked?'none':''})});
/* 연차 계획: 쉬는 날 집합에 휴가일을 하나씩 더해 가장 길어지는 곳부터 */
var Y=C.y,nat={};C.nat.forEach(function(d){nat[d]=1});function key(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)}
function offset(d,n){return new Date(d.getFullYear(),d.getMonth(),d.getDate()+n)}
function score(off){var tot=0,run=0,hol=false,d=new Date(Y,0,1);while(d.getFullYear()===Y){var kk=key(d);if(off[kk]){run++;if(nat[kk])hol=true}else{if(run>=3)tot+=run;run=0;hol=false}d=offset(d,1)}if(run>=3)tot+=run;return tot}
function plan(k){var off={},d=new Date(Y,0,1);while(d.getFullYear()===Y){var w=d.getDay();if(w===0||w===6||nat[key(d)])off[key(d)]=1;d=offset(d,1)}
var base=score(off),picks=[];for(var n=0;n<k;n++){var best=null,bg=0;d=new Date(Y,0,1);while(d.getFullYear()===Y){var kk=key(d);if(!off[kk]&&d>=now){off[kk]=1;var g=score(off)-base;if(g>bg){bg=g;best=kk}delete off[kk]}d=offset(d,1)}
if(!best)break;off[best]=1;base+=bg;picks.push(best)}
var blocks=[],seen={};picks.sort().forEach(function(p){var a=D(p),b=D(p);while(off[key(offset(a,-1))])a=offset(a,-1);while(off[key(offset(b,1))])b=offset(b,1);var s=key(a);if(!seen[s]){seen[s]=1;blocks.push([a,b])}});
var tot=0,f=function(x){return x.toLocaleDateString(L,{month:'short',day:'numeric',weekday:'short'})};blocks.forEach(function(b){tot+=Math.round((b[1]-b[0])/864e5)+1});
$('hd-pr').innerHTML=picks.length?'<p>'+C.t.planR.replace('{k}',picks.length).replace('{d}','<b>'+tot+'</b>')+'</p><ul class="hd-l">'+blocks.map(function(b){return '<li>'+f(b[0])+' – '+f(b[1])+' (<b>'+(Math.round((b[1]-b[0])/864e5)+1)+'</b>)</li>'}).join('')+'</ul>':''}
var ki=$('hd-k');ki.addEventListener('input',function(){var k=Math.max(0,Math.min(20,parseInt(ki.value,10)||0));plan(k)});plan(3);
$('hd-ics').addEventListener('click',function(){var s='BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//honglifecalc.com//holidays//EN\r\n';C.h.filter(function(h){return h[2]}).forEach(function(h,i){var a=h[0].replace(/-/g,''),n=D(h[0]);n.setDate(n.getDate()+1);s+='BEGIN:VEVENT\r\nUID:'+a+'-'+i+'@honglifecalc.com\r\nDTSTART;VALUE=DATE:'+a+'\r\nDTEND;VALUE=DATE:'+key(n).replace(/-/g,'')+'\r\nSUMMARY:'+h[1].replace(/[,;]/g,' ')+'\r\nTRANSP:TRANSPARENT\r\nEND:VEVENT\r\n'});s+='END:VCALENDAR\r\n';
var u=URL.createObjectURL(new Blob([s],{type:'text/calendar'})),a=document.createElement('a');a.href=u;a.download=C.slug.replace('.html','.ics');document.body.appendChild(a);a.click();a.remove()});
})();</script>'''
    return build_page(SITE, folder, slug, F(t['title']), F(t['desc']), body,
                      ld=[app_ld(F(t['title']).split(' – ')[0], url, 'ReferenceApplication', {"dateModified": dt.date.today().isoformat()}), faq_ld(faq),
                          {"@context": "https://schema.org", "@type": "ItemList", "name": F(t['tbl']), "itemListElement": [
                              {"@type": "ListItem", "position": i + 1, "item": {"@type": "Event", "name": (h['localName'] if lang != 'en' else h['name']), "startDate": h['date'],
                                                                                 "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "location": {"@type": "Country", "name": nm}}}
                              for i, h in enumerate(natlist[:40])]}],
                      head_extra=css, tail_extra=f'<script>window.HDCFG={json.dumps(cfg, ensure_ascii=False, separators=(",", ":"))};</script>' + js, marker='data-hl-hol')


made = [build(f) for f in C]
register(SITE, made)
print('holiday pages:', sum(1 for m in made if m), 'year', YEAR)
