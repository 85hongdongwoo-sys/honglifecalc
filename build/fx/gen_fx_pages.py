# 나라별 환율 계산기 페이지 (ECB 기준환율) — 배포 때 _site 의 그 나라 페이지 틀로 만들고, 오늘 환율을 본문 숫자로 박는다.
# 사용: python3 build/fx/gen_fx_pages.py _site
import html, json, os, re, sys, time

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
B = 'https://honglifecalc.com'
FX = json.load(open(os.path.join(SITE, 'fx', 'latest.json')))
R, DATE = FX['rates'], FX['date']
E = lambda s: html.escape(str(s), quote=True)

# 나라: (언어, 기본 통화, 함께 볼 통화)
C = {
 'us': ('en', 'USD', ['EUR', 'GBP', 'CAD', 'MXN', 'JPY', 'CNY', 'INR', 'AUD', 'CHF', 'KRW']),
 'uk': ('en', 'GBP', ['EUR', 'USD', 'PLN', 'INR', 'AUD', 'CAD', 'JPY', 'CHF', 'TRY', 'ZAR']),
 'ca': ('en', 'CAD', ['USD', 'EUR', 'GBP', 'INR', 'CNY', 'MXN', 'JPY', 'AUD', 'PHP', 'KRW']),
 'au': ('en', 'AUD', ['USD', 'EUR', 'GBP', 'NZD', 'JPY', 'CNY', 'INR', 'SGD', 'IDR', 'THB']),
 'ie': ('en', 'EUR', ['GBP', 'USD', 'PLN', 'CAD', 'AUD', 'INR', 'CHF', 'JPY', 'CNY', 'BRL']),
 'in': ('en', 'INR', ['USD', 'EUR', 'GBP', 'AUD', 'CAD', 'SGD', 'JPY', 'CNY', 'MYR', 'THB']),
 'ph': ('en', 'PHP', ['USD', 'EUR', 'JPY', 'KRW', 'SGD', 'AUD', 'CAD', 'GBP', 'HKD', 'CNY']),
 'sg': ('en', 'SGD', ['USD', 'MYR', 'EUR', 'CNY', 'JPY', 'AUD', 'GBP', 'IDR', 'THB', 'INR']),
 'za': ('en', 'ZAR', ['USD', 'EUR', 'GBP', 'AUD', 'CNY', 'INR', 'JPY', 'CHF', 'BRL', 'CAD']),
 'nz': ('en', 'NZD', ['AUD', 'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'INR', 'PHP', 'SGD', 'CAD']),
 'en': ('en', 'USD', ['EUR', 'GBP', 'JPY', 'CNY', 'INR', 'CAD', 'AUD', 'CHF', 'MXN', 'KRW']),
 'de': ('de', 'EUR', ['USD', 'GBP', 'CHF', 'PLN', 'TRY', 'CZK', 'JPY', 'CNY', 'SEK', 'DKK']),
 'at': ('de', 'EUR', ['USD', 'CHF', 'GBP', 'HUF', 'CZK', 'PLN', 'TRY', 'JPY', 'CNY', 'RON']),
 'ch': ('de', 'CHF', ['EUR', 'USD', 'GBP', 'JPY', 'CNY', 'SEK', 'PLN', 'TRY', 'CAD', 'AUD']),
 'fr': ('fr', 'EUR', ['USD', 'GBP', 'CHF', 'CAD', 'JPY', 'CNY', 'TRY', 'PLN', 'SEK', 'ZAR']),
 'be': ('fr', 'EUR', ['USD', 'GBP', 'CHF', 'CAD', 'TRY', 'PLN', 'JPY', 'CNY', 'SEK', 'RON']),
 'es': ('es', 'EUR', ['USD', 'MXN', 'GBP', 'BRL', 'CHF', 'JPY', 'CNY', 'CAD', 'TRY', 'PLN']),
 'mx': ('es', 'MXN', ['USD', 'EUR', 'CAD', 'GBP', 'JPY', 'CNY', 'BRL', 'KRW', 'CHF', 'INR']),
 'it': ('it', 'EUR', ['USD', 'GBP', 'CHF', 'JPY', 'CNY', 'TRY', 'PLN', 'RON', 'BRL', 'CAD']),
 'nl': ('nl', 'EUR', ['USD', 'GBP', 'TRY', 'PLN', 'CHF', 'JPY', 'CNY', 'IDR', 'SEK', 'NOK']),
 'pt': ('pt', 'BRL', ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'CAD', 'CHF', 'MXN', 'AUD', 'INR']),
 'br': ('pt', 'BRL', ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'CAD', 'CHF', 'MXN', 'AUD', 'INR']),
 'pl': ('pl', 'PLN', ['EUR', 'USD', 'GBP', 'CHF', 'CZK', 'NOK', 'SEK', 'TRY', 'JPY', 'HUF']),
 'se': ('sv', 'SEK', ['EUR', 'USD', 'NOK', 'DKK', 'GBP', 'PLN', 'THB', 'CHF', 'JPY', 'TRY']),
 'no': ('nb', 'NOK', ['EUR', 'USD', 'SEK', 'DKK', 'GBP', 'PLN', 'THB', 'CHF', 'JPY', 'ISK']),
 'dk': ('da', 'DKK', ['EUR', 'USD', 'SEK', 'NOK', 'GBP', 'PLN', 'THB', 'CHF', 'TRY', 'JPY']),
 'tr': ('tr', 'TRY', ['USD', 'EUR', 'GBP', 'CHF', 'JPY', 'CNY', 'CAD', 'AUD', 'SEK', 'NOK']),
 'id': ('id', 'IDR', ['USD', 'EUR', 'SGD', 'MYR', 'JPY', 'CNY', 'AUD', 'KRW', 'THB', 'GBP']),
 'my': ('ms', 'MYR', ['USD', 'SGD', 'EUR', 'CNY', 'IDR', 'THB', 'JPY', 'GBP', 'AUD', 'INR']),
 'jp': ('ja', 'JPY', ['USD', 'EUR', 'KRW', 'CNY', 'GBP', 'AUD', 'THB', 'CHF', 'CAD', 'SGD']),
 'zh': ('zh', 'CNY', ['USD', 'EUR', 'JPY', 'KRW', 'HKD', 'GBP', 'AUD', 'SGD', 'THB', 'CAD']),
 'hi': ('hi', 'INR', ['USD', 'EUR', 'GBP', 'AUD', 'CAD', 'SGD', 'JPY', 'CNY', 'MYR', 'THB']),
}

# 언어별 문구 ({c}=기본 통화, {o}=첫 상대 통화)
T = {
 'en': dict(slug='currency-converter.html', title='Currency Converter {c} – Today’s Exchange Rates ({o}, EUR, GBP …)', desc='Convert {c} to {o} and 30 currencies with the official European Central Bank reference rates, updated every working day. Add your bank or card fee to see what you really pay, and check the 90-day trend.',
           h1='<b>Currency</b> Converter', sub='Official ECB reference rates, updated every working day – with bank-fee estimate and 90-day trend.',
           amount='Amount', frm='From', to='To', swap='Swap', fee='Bank / card fee (%)', feeNote='Banks and cards usually add 1–3 % on top of the reference rate. Enter yours to see what you really pay.',
           res='Result', rate='Exchange rate', inv='Inverse rate', withFee='With fee you pay / get', trend='90-day trend', hi='High', lo='Low', chg='Change',
           table='{c} against major currencies today', col1='1 {c} =', col2='1 unit in {c}', asof='ECB reference rate of {d}', src='Source: European Central Bank – euro foreign exchange reference rates (for information purposes).',
           q1='How much is 100 {c} in {o} today?', a1='At the ECB reference rate of {d}, 100 {c} = {v} {o}. Banks and exchange offices add their own margin, so the amount you receive is usually a little lower.',
           q2='When are the exchange rates updated?', a2='The European Central Bank publishes reference rates on every working day at around 16:00 CET. This page updates automatically after that.',
           q3='Why does my bank show a different rate?', a3='The ECB rate is a mid-market reference rate. Banks and card issuers add a spread or fee (often 1–3 %). Enter that percentage in the fee field to estimate the real cost.'),
 'de': dict(slug='waehrungsrechner.html', title='Währungsrechner {c} – aktueller Wechselkurs ({o}, USD, GBP …)', desc='{c} in {o} und 30 weitere Währungen umrechnen – mit den offiziellen Referenzkursen der Europäischen Zentralbank, an jedem Arbeitstag aktualisiert. Mit Bank-/Kartengebühr und 90-Tage-Verlauf.',
           h1='<b>Währungs</b>rechner', sub='Offizielle EZB-Referenzkurse, jeden Arbeitstag aktuell – mit Gebühren-Schätzung und 90-Tage-Verlauf.',
           amount='Betrag', frm='Von', to='In', swap='Tauschen', fee='Bank-/Kartengebühr (%)', feeNote='Banken und Karten schlagen meist 1–3 % auf den Referenzkurs auf. Tragen Sie Ihren Aufschlag ein, um den echten Betrag zu sehen.',
           res='Ergebnis', rate='Wechselkurs', inv='Umgekehrt', withFee='Mit Gebühr zahlen / erhalten Sie', trend='Verlauf 90 Tage', hi='Hoch', lo='Tief', chg='Veränderung',
           table='{c} gegenüber wichtigen Währungen heute', col1='1 {c} =', col2='1 Einheit in {c}', asof='EZB-Referenzkurs vom {d}', src='Quelle: Europäische Zentralbank – Euro-Referenzkurse (nur zu Informationszwecken).',
           q1='Wie viel sind 100 {c} in {o} heute?', a1='Zum EZB-Referenzkurs vom {d} sind 100 {c} = {v} {o}. Banken und Wechselstuben rechnen eine eigene Marge ein, daher erhalten Sie meist etwas weniger.',
           q2='Wann werden die Kurse aktualisiert?', a2='Die Europäische Zentralbank veröffentlicht die Referenzkurse an jedem Arbeitstag gegen 16 Uhr MEZ. Diese Seite wird danach automatisch aktualisiert.',
           q3='Warum zeigt meine Bank einen anderen Kurs?', a3='Der EZB-Kurs ist ein Mittelkurs. Banken und Kartenanbieter schlagen eine Marge oder Gebühr auf (oft 1–3 %). Tragen Sie diese im Gebührenfeld ein.'),
 'fr': dict(slug='convertisseur-devises.html', title='Convertisseur de devises {c} – taux de change du jour ({o}, USD, GBP …)', desc='Convertissez {c} en {o} et 30 devises avec les taux de référence officiels de la Banque centrale européenne, mis à jour chaque jour ouvré. Avec frais bancaires et évolution sur 90 jours.',
           h1='<b>Convertisseur</b> de devises', sub='Taux de référence officiels de la BCE, mis à jour chaque jour ouvré – avec estimation des frais et courbe sur 90 jours.',
           amount='Montant', frm='De', to='Vers', swap='Inverser', fee='Frais banque / carte (%)', feeNote='Les banques et cartes ajoutent souvent 1 à 3 % au taux de référence. Indiquez les vôtres pour voir le montant réel.',
           res='Résultat', rate='Taux de change', inv='Taux inverse', withFee='Avec frais, vous payez / recevez', trend='Évolution sur 90 jours', hi='Plus haut', lo='Plus bas', chg='Variation',
           table='{c} face aux principales devises aujourd’hui', col1='1 {c} =', col2='1 unité en {c}', asof='Taux de référence BCE du {d}', src='Source : Banque centrale européenne – taux de référence de l’euro (à titre d’information).',
           q1='Combien font 100 {c} en {o} aujourd’hui ?', a1='Au taux de référence BCE du {d}, 100 {c} = {v} {o}. Les banques et bureaux de change appliquent leur marge : vous recevez donc en général un peu moins.',
           q2='Quand les taux sont-ils mis à jour ?', a2='La Banque centrale européenne publie ses taux de référence chaque jour ouvré vers 16 h (heure de Paris). Cette page se met à jour automatiquement ensuite.',
           q3='Pourquoi ma banque affiche-t-elle un autre taux ?', a3='Le taux BCE est un cours moyen. Les banques et émetteurs de cartes ajoutent une marge ou des frais (souvent 1 à 3 %). Saisissez ce pourcentage dans le champ des frais.'),
 'es': dict(slug='conversor-divisas.html', title='Conversor de divisas {c} – tipo de cambio de hoy ({o}, USD, EUR …)', desc='Convierte {c} a {o} y 30 divisas con los tipos de referencia oficiales del Banco Central Europeo, actualizados cada día hábil. Con comisión bancaria y evolución de 90 días.',
           h1='<b>Conversor</b> de divisas', sub='Tipos de referencia oficiales del BCE, actualizados cada día hábil – con estimación de comisión y gráfico de 90 días.',
           amount='Importe', frm='De', to='A', swap='Invertir', fee='Comisión banco / tarjeta (%)', feeNote='Bancos y tarjetas suelen sumar un 1–3 % al tipo de referencia. Introduce la tuya para ver lo que pagas de verdad.',
           res='Resultado', rate='Tipo de cambio', inv='Tipo inverso', withFee='Con comisión pagas / recibes', trend='Evolución 90 días', hi='Máximo', lo='Mínimo', chg='Variación',
           table='{c} frente a las principales divisas hoy', col1='1 {c} =', col2='1 unidad en {c}', asof='Tipo de referencia del BCE del {d}', src='Fuente: Banco Central Europeo – tipos de cambio de referencia del euro (solo a título informativo).',
           q1='¿Cuánto son 100 {c} en {o} hoy?', a1='Al tipo de referencia del BCE del {d}, 100 {c} = {v} {o}. Bancos y casas de cambio aplican su propio margen, así que normalmente recibirás algo menos.',
           q2='¿Cuándo se actualizan los tipos?', a2='El Banco Central Europeo publica los tipos de referencia cada día hábil hacia las 16:00 (hora de Europa central). Esta página se actualiza automáticamente después.',
           q3='¿Por qué mi banco muestra otro tipo?', a3='El tipo del BCE es un tipo medio. Bancos y tarjetas añaden un margen o comisión (a menudo 1–3 %). Introduce ese porcentaje en el campo de comisión.'),
 'it': dict(slug='convertitore-valute.html', title='Convertitore di valute {c} – cambio di oggi ({o}, USD, GBP …)', desc='Converti {c} in {o} e 30 valute con i tassi di riferimento ufficiali della Banca centrale europea, aggiornati ogni giorno lavorativo. Con commissione bancaria e andamento a 90 giorni.',
           h1='<b>Convertitore</b> di valute', sub='Tassi di riferimento ufficiali BCE, aggiornati ogni giorno lavorativo – con stima delle commissioni e grafico a 90 giorni.',
           amount='Importo', frm='Da', to='A', swap='Inverti', fee='Commissione banca / carta (%)', feeNote='Banche e carte aggiungono spesso l’1–3 % al tasso di riferimento. Inserisci la tua per vedere quanto paghi davvero.',
           res='Risultato', rate='Tasso di cambio', inv='Tasso inverso', withFee='Con commissione paghi / ricevi', trend='Andamento 90 giorni', hi='Massimo', lo='Minimo', chg='Variazione',
           table='{c} rispetto alle principali valute oggi', col1='1 {c} =', col2='1 unità in {c}', asof='Tasso di riferimento BCE del {d}', src='Fonte: Banca centrale europea – tassi di cambio di riferimento dell’euro (a titolo informativo).',
           q1='Quanto sono 100 {c} in {o} oggi?', a1='Al tasso di riferimento BCE del {d}, 100 {c} = {v} {o}. Banche e cambiavalute applicano un proprio margine, quindi di solito ricevi un po’ meno.',
           q2='Quando vengono aggiornati i tassi?', a2='La Banca centrale europea pubblica i tassi di riferimento ogni giorno lavorativo verso le 16:00 (ora dell’Europa centrale). Questa pagina si aggiorna automaticamente.',
           q3='Perché la mia banca mostra un tasso diverso?', a3='Il tasso BCE è un cambio medio. Banche e carte aggiungono un margine o una commissione (spesso 1–3 %). Inserisci la percentuale nel campo commissione.'),
 'nl': dict(slug='valuta-omrekenen.html', title='Valuta omrekenen {c} – wisselkoers van vandaag ({o}, USD, GBP …)', desc='Reken {c} om naar {o} en 30 valuta met de officiële referentiekoersen van de Europese Centrale Bank, elke werkdag bijgewerkt. Met bank- of kaartkosten en 90-dagenverloop.',
           h1='<b>Valuta</b> omrekenen', sub='Officiële ECB-referentiekoersen, elke werkdag bijgewerkt – met kostenschatting en 90-dagenverloop.',
           amount='Bedrag', frm='Van', to='Naar', swap='Omdraaien', fee='Bank-/kaartkosten (%)', feeNote='Banken en kaarten rekenen vaak 1–3 % bovenop de referentiekoers. Vul je eigen opslag in om het echte bedrag te zien.',
           res='Resultaat', rate='Wisselkoers', inv='Omgekeerde koers', withFee='Met kosten betaal / ontvang je', trend='Verloop 90 dagen', hi='Hoogste', lo='Laagste', chg='Verandering',
           table='{c} tegenover belangrijke valuta vandaag', col1='1 {c} =', col2='1 eenheid in {c}', asof='ECB-referentiekoers van {d}', src='Bron: Europese Centrale Bank – referentiewisselkoersen van de euro (ter informatie).',
           q1='Hoeveel is 100 {c} in {o} vandaag?', a1='Tegen de ECB-referentiekoers van {d} is 100 {c} = {v} {o}. Banken en wisselkantoren rekenen een eigen marge, dus je ontvangt meestal iets minder.',
           q2='Wanneer worden de koersen bijgewerkt?', a2='De Europese Centrale Bank publiceert de referentiekoersen elke werkdag rond 16:00 uur (MET). Deze pagina wordt daarna automatisch bijgewerkt.',
           q3='Waarom toont mijn bank een andere koers?', a3='De ECB-koers is een middenkoers. Banken en kaartuitgevers rekenen een opslag of kosten (vaak 1–3 %). Vul dat percentage in bij de kosten.'),
 'pt': dict(slug='conversor-moedas.html', title='Conversor de moedas {c} – câmbio de hoje ({o}, EUR, GBP …)', desc='Converta {c} para {o} e 30 moedas com as taxas de referência oficiais do Banco Central Europeu, atualizadas a cada dia útil. Com tarifa do banco/cartão e gráfico de 90 dias.',
           h1='<b>Conversor</b> de moedas', sub='Taxas de referência oficiais do BCE, atualizadas a cada dia útil – com estimativa de tarifa e gráfico de 90 dias.',
           amount='Valor', frm='De', to='Para', swap='Inverter', fee='Tarifa banco / cartão (%)', feeNote='Bancos e cartões costumam somar 1–6 % (com IOF) à taxa de referência. Informe a sua para ver quanto paga de verdade.',
           res='Resultado', rate='Taxa de câmbio', inv='Taxa inversa', withFee='Com tarifa você paga / recebe', trend='Evolução em 90 dias', hi='Máxima', lo='Mínima', chg='Variação',
           table='{c} frente às principais moedas hoje', col1='1 {c} =', col2='1 unidade em {c}', asof='Taxa de referência do BCE de {d}', src='Fonte: Banco Central Europeu – taxas de câmbio de referência do euro (apenas para informação).',
           q1='Quanto são 100 {c} em {o} hoje?', a1='Pela taxa de referência do BCE de {d}, 100 {c} = {v} {o}. Bancos e casas de câmbio aplicam margem própria, então normalmente você recebe um pouco menos.',
           q2='Quando as taxas são atualizadas?', a2='O Banco Central Europeu publica as taxas de referência a cada dia útil por volta das 16h (horário da Europa Central). Esta página é atualizada automaticamente depois.',
           q3='Por que meu banco mostra outra taxa?', a3='A taxa do BCE é uma taxa média. Bancos e cartões somam margem e tarifas. Digite esse percentual no campo de tarifa para estimar o custo real.'),
 'pl': dict(slug='przelicznik-walut.html', title='Przelicznik walut {c} – dzisiejszy kurs ({o}, USD, GBP …)', desc='Przelicz {c} na {o} i 30 walut według oficjalnych kursów referencyjnych Europejskiego Banku Centralnego, aktualizowanych w każdy dzień roboczy. Z prowizją banku/karty i wykresem 90 dni.',
           h1='<b>Przelicznik</b> walut', sub='Oficjalne kursy referencyjne EBC, aktualizowane w każdy dzień roboczy – z prowizją i wykresem z 90 dni.',
           amount='Kwota', frm='Z', to='Na', swap='Zamień', fee='Prowizja banku / karty (%)', feeNote='Banki i karty zwykle doliczają 1–3 % do kursu referencyjnego. Wpisz swoją, aby zobaczyć realną kwotę.',
           res='Wynik', rate='Kurs', inv='Kurs odwrotny', withFee='Z prowizją płacisz / otrzymujesz', trend='Wykres 90 dni', hi='Najwyżej', lo='Najniżej', chg='Zmiana',
           table='{c} wobec głównych walut dziś', col1='1 {c} =', col2='1 jednostka w {c}', asof='Kurs referencyjny EBC z {d}', src='Źródło: Europejski Bank Centralny – referencyjne kursy euro (wyłącznie informacyjnie).',
           q1='Ile to 100 {c} w {o} dzisiaj?', a1='Według kursu referencyjnego EBC z {d} 100 {c} = {v} {o}. Banki i kantory doliczają własną marżę, więc zwykle otrzymasz trochę mniej.',
           q2='Kiedy kursy są aktualizowane?', a2='Europejski Bank Centralny publikuje kursy referencyjne w każdy dzień roboczy około 16:00 czasu środkowoeuropejskiego. Ta strona aktualizuje się potem automatycznie.',
           q3='Dlaczego mój bank pokazuje inny kurs?', a3='Kurs EBC to kurs średni. Banki i karty doliczają marżę lub prowizję (często 1–3 %). Wpisz ten procent w polu prowizji.'),
 'sv': dict(slug='valutaomvandlare.html', title='Valutaomvandlare {c} – dagens växelkurs ({o}, USD, NOK …)', desc='Räkna om {c} till {o} och 30 valutor med Europeiska centralbankens officiella referenskurser, uppdaterade varje bankdag. Med bank-/kortavgift och 90-dagarsgraf.',
           h1='<b>Valuta</b>omvandlare', sub='Officiella ECB-referenskurser, uppdaterade varje bankdag – med avgiftsuppskattning och 90-dagarsgraf.',
           amount='Belopp', frm='Från', to='Till', swap='Byt', fee='Bank-/kortavgift (%)', feeNote='Banker och kort lägger ofta på 1–3 % på referenskursen. Fyll i din för att se vad du verkligen betalar.',
           res='Resultat', rate='Växelkurs', inv='Omvänd kurs', withFee='Med avgift betalar / får du', trend='Utveckling 90 dagar', hi='Högst', lo='Lägst', chg='Förändring',
           table='{c} mot viktiga valutor idag', col1='1 {c} =', col2='1 enhet i {c}', asof='ECB:s referenskurs {d}', src='Källa: Europeiska centralbanken – eurons referensväxelkurser (endast i informationssyfte).',
           q1='Hur mycket är 100 {c} i {o} idag?', a1='Enligt ECB:s referenskurs {d} är 100 {c} = {v} {o}. Banker och växlingskontor tar en egen marginal, så du får oftast lite mindre.',
           q2='När uppdateras kurserna?', a2='Europeiska centralbanken publicerar referenskurserna varje bankdag runt kl. 16 (centraleuropeisk tid). Sidan uppdateras automatiskt efter det.',
           q3='Varför visar min bank en annan kurs?', a3='ECB-kursen är en mittkurs. Banker och kortutgivare lägger på en marginal eller avgift (ofta 1–3 %). Fyll i den procenten i avgiftsfältet.'),
 'nb': dict(slug='valutakalkulator.html', title='Valutakalkulator {c} – dagens valutakurs ({o}, USD, SEK …)', desc='Regn om {c} til {o} og 30 valutaer med Den europeiske sentralbankens offisielle referansekurser, oppdatert hver virkedag. Med bank-/kortgebyr og 90-dagers graf.',
           h1='<b>Valuta</b>kalkulator', sub='Offisielle ECB-referansekurser, oppdatert hver virkedag – med gebyrestimat og 90-dagers graf.',
           amount='Beløp', frm='Fra', to='Til', swap='Bytt', fee='Bank-/kortgebyr (%)', feeNote='Banker og kort legger ofte på 1–3 % på referansekursen. Fyll inn ditt påslag for å se hva du faktisk betaler.',
           res='Resultat', rate='Valutakurs', inv='Omvendt kurs', withFee='Med gebyr betaler / får du', trend='Utvikling 90 dager', hi='Høyest', lo='Lavest', chg='Endring',
           table='{c} mot viktige valutaer i dag', col1='1 {c} =', col2='1 enhet i {c}', asof='ECBs referansekurs {d}', src='Kilde: Den europeiske sentralbanken – euroens referansekurser (kun til informasjon).',
           q1='Hvor mye er 100 {c} i {o} i dag?', a1='Etter ECBs referansekurs {d} er 100 {c} = {v} {o}. Banker og vekslingskontorer tar egen margin, så du får vanligvis litt mindre.',
           q2='Når oppdateres kursene?', a2='Den europeiske sentralbanken publiserer referansekursene hver virkedag rundt kl. 16 (sentraleuropeisk tid). Siden oppdateres automatisk etterpå.',
           q3='Hvorfor viser banken min en annen kurs?', a3='ECB-kursen er en midtkurs. Banker og kortutstedere legger på margin eller gebyr (ofte 1–3 %). Fyll inn prosenten i gebyrfeltet.'),
 'da': dict(slug='valutaomregner.html', title='Valutaomregner {c} – dagens valutakurs ({o}, USD, SEK …)', desc='Omregn {c} til {o} og 30 valutaer med Den Europæiske Centralbanks officielle referencekurser, opdateret hver bankdag. Med bank-/kortgebyr og 90-dages graf.',
           h1='<b>Valuta</b>omregner', sub='Officielle ECB-referencekurser, opdateret hver bankdag – med gebyroverslag og 90-dages graf.',
           amount='Beløb', frm='Fra', to='Til', swap='Byt', fee='Bank-/kortgebyr (%)', feeNote='Banker og kort lægger ofte 1–3 % oven i referencekursen. Indtast dit tillæg for at se, hvad du reelt betaler.',
           res='Resultat', rate='Valutakurs', inv='Omvendt kurs', withFee='Med gebyr betaler / får du', trend='Udvikling 90 dage', hi='Højest', lo='Lavest', chg='Ændring',
           table='{c} over for vigtige valutaer i dag', col1='1 {c} =', col2='1 enhed i {c}', asof='ECB-referencekurs {d}', src='Kilde: Den Europæiske Centralbank – euroens referencekurser (kun til orientering).',
           q1='Hvor meget er 100 {c} i {o} i dag?', a1='Til ECB-referencekursen {d} er 100 {c} = {v} {o}. Banker og vekselkontorer lægger deres egen margin på, så du får som regel lidt mindre.',
           q2='Hvornår opdateres kurserne?', a2='Den Europæiske Centralbank offentliggør referencekurserne hver bankdag omkring kl. 16 (dansk tid). Siden opdateres automatisk derefter.',
           q3='Hvorfor viser min bank en anden kurs?', a3='ECB-kursen er en midterkurs. Banker og kortudstedere lægger en margin eller et gebyr på (ofte 1–3 %). Indtast procenten i gebyrfeltet.'),
 'tr': dict(slug='doviz-cevirici.html', title='Döviz Çevirici {c} – bugünkü kur ({o}, EUR, GBP …)', desc='{c} tutarını {o} ve 30 para birimine Avrupa Merkez Bankası’nın resmi referans kurlarıyla çevirin; her iş günü güncellenir. Banka/kart masrafı ve 90 günlük grafik dahil.',
           h1='<b>Döviz</b> Çevirici', sub='Resmi ECB referans kurları, her iş günü güncel – masraf tahmini ve 90 günlük grafikle.',
           amount='Tutar', frm='Kaynak', to='Hedef', swap='Değiştir', fee='Banka / kart masrafı (%)', feeNote='Bankalar ve kartlar genelde referans kura %1–3 ekler. Gerçekte ödeyeceğinizi görmek için kendi oranınızı girin.',
           res='Sonuç', rate='Kur', inv='Ters kur', withFee='Masrafla ödediğiniz / aldığınız', trend='90 günlük seyir', hi='En yüksek', lo='En düşük', chg='Değişim',
           table='{c} bugün başlıca para birimlerine karşı', col1='1 {c} =', col2='1 birim {c} olarak', asof='ECB referans kuru, {d}', src='Kaynak: Avrupa Merkez Bankası – euro referans döviz kurları (yalnızca bilgi amaçlı).',
           q1='Bugün 100 {c} kaç {o}?', a1='ECB’nin {d} tarihli referans kuruyla 100 {c} = {v} {o}. Bankalar ve döviz büroları kendi marjlarını eklediği için genellikle biraz daha az alırsınız.',
           q2='Kurlar ne zaman güncellenir?', a2='Avrupa Merkez Bankası referans kurlarını her iş günü Orta Avrupa saatiyle 16:00 civarında yayımlar. Bu sayfa ardından otomatik güncellenir.',
           q3='Bankam neden farklı kur gösteriyor?', a3='ECB kuru bir orta kurdur. Bankalar ve kartlar marj veya masraf ekler (çoğu zaman %1–3). Bu yüzdeyi masraf alanına girin.'),
 'id': dict(slug='konversi-mata-uang.html', title='Konversi Mata Uang {c} – Kurs Hari Ini ({o}, SGD, EUR …)', desc='Konversi {c} ke {o} dan 30 mata uang dengan kurs referensi resmi Bank Sentral Eropa, diperbarui setiap hari kerja. Dengan biaya bank/kartu dan grafik 90 hari.',
           h1='<b>Konversi</b> Mata Uang', sub='Kurs referensi resmi ECB, diperbarui setiap hari kerja – dengan perkiraan biaya dan grafik 90 hari.',
           amount='Jumlah', frm='Dari', to='Ke', swap='Tukar', fee='Biaya bank / kartu (%)', feeNote='Bank dan kartu biasanya menambah 1–3 % dari kurs referensi. Masukkan biaya Anda untuk melihat jumlah sebenarnya.',
           res='Hasil', rate='Kurs', inv='Kurs kebalikan', withFee='Dengan biaya Anda bayar / terima', trend='Tren 90 hari', hi='Tertinggi', lo='Terendah', chg='Perubahan',
           table='{c} terhadap mata uang utama hari ini', col1='1 {c} =', col2='1 unit dalam {c}', asof='Kurs referensi ECB tanggal {d}', src='Sumber: Bank Sentral Eropa – kurs referensi euro (hanya untuk informasi).',
           q1='Berapa 100 {c} dalam {o} hari ini?', a1='Dengan kurs referensi ECB tanggal {d}, 100 {c} = {v} {o}. Bank dan money changer menambahkan margin sendiri, jadi biasanya Anda menerima sedikit lebih kecil.',
           q2='Kapan kurs diperbarui?', a2='Bank Sentral Eropa menerbitkan kurs referensi setiap hari kerja sekitar pukul 16.00 waktu Eropa Tengah. Halaman ini diperbarui otomatis setelahnya.',
           q3='Mengapa bank saya menunjukkan kurs berbeda?', a3='Kurs ECB adalah kurs tengah. Bank dan penerbit kartu menambah margin atau biaya (sering 1–3 %). Masukkan persentase itu di kolom biaya.'),
 'ms': dict(slug='penukar-mata-wang.html', title='Penukar Mata Wang {c} – Kadar Pertukaran Hari Ini ({o}, SGD, EUR …)', desc='Tukar {c} kepada {o} dan 30 mata wang dengan kadar rujukan rasmi Bank Pusat Eropah, dikemas kini setiap hari bekerja. Dengan caj bank/kad dan graf 90 hari.',
           h1='<b>Penukar</b> Mata Wang', sub='Kadar rujukan rasmi ECB, dikemas kini setiap hari bekerja – dengan anggaran caj dan graf 90 hari.',
           amount='Jumlah', frm='Daripada', to='Kepada', swap='Tukar', fee='Caj bank / kad (%)', feeNote='Bank dan kad biasanya menambah 1–3 % pada kadar rujukan. Masukkan caj anda untuk melihat jumlah sebenar.',
           res='Keputusan', rate='Kadar pertukaran', inv='Kadar songsang', withFee='Dengan caj anda bayar / terima', trend='Trend 90 hari', hi='Tertinggi', lo='Terendah', chg='Perubahan',
           table='{c} berbanding mata wang utama hari ini', col1='1 {c} =', col2='1 unit dalam {c}', asof='Kadar rujukan ECB {d}', src='Sumber: Bank Pusat Eropah – kadar pertukaran rujukan euro (untuk makluman sahaja).',
           q1='Berapakah 100 {c} dalam {o} hari ini?', a1='Pada kadar rujukan ECB {d}, 100 {c} = {v} {o}. Bank dan pengurup wang menambah margin sendiri, jadi biasanya anda menerima sedikit kurang.',
           q2='Bilakah kadar dikemas kini?', a2='Bank Pusat Eropah menerbitkan kadar rujukan setiap hari bekerja sekitar jam 4 petang waktu Eropah Tengah. Halaman ini dikemas kini secara automatik selepas itu.',
           q3='Kenapa bank saya menunjukkan kadar lain?', a3='Kadar ECB ialah kadar tengah. Bank dan pengeluar kad menambah margin atau caj (selalunya 1–3 %). Masukkan peratusan itu dalam ruangan caj.'),
 'ja': dict(slug='kawase-keisan.html', title='為替計算機 {c} – 今日の為替レート（{o}・ユーロ・ポンドなど）', desc='{c}を{o}など30通貨に換算。欧州中央銀行（ECB）の公式参照レートを営業日ごとに自動更新。銀行・カード手数料の上乗せと90日チャートも見られます。',
           h1='<b>為替</b>計算機', sub='ECB公式参照レートを営業日ごとに更新。手数料込みの金額と90日の推移も。',
           amount='金額', frm='元の通貨', to='換算先', swap='入れ替え', fee='銀行・カード手数料（%）', feeNote='銀行やカードは参照レートに1〜3％程度上乗せすることが多いです。実際の金額を見るには手数料率を入れてください。',
           res='結果', rate='為替レート', inv='逆レート', withFee='手数料込みで払う／受け取る額', trend='90日の推移', hi='最高', lo='最安', chg='変化',
           table='主要通貨に対する{c}（本日）', col1='1 {c} =', col2='1単位あたりの{c}', asof='ECB参照レート（{d}）', src='出典：欧州中央銀行（ECB）ユーロ参照為替レート（情報提供目的）。',
           q1='今日、100{c}は何{o}ですか？', a1='{d}のECB参照レートでは、100 {c} = {v} {o}です。銀行や両替所は独自の手数料を上乗せするため、実際に受け取る額は少し少なくなるのが普通です。',
           q2='レートはいつ更新されますか？', a2='欧州中央銀行は営業日ごとに中央ヨーロッパ時間16時ごろ参照レートを公表します。このページはその後自動で更新されます。',
           q3='銀行のレートと違うのはなぜ？', a3='ECBレートは仲値です。銀行やカード会社は手数料やスプレッド（1〜3％程度が多い）を上乗せします。その率を手数料欄に入れてください。'),
 'zh': dict(slug='huilv-huansuan.html', title='汇率换算 {c} – 今日汇率（{o}、欧元、英镑等）', desc='用欧洲央行（ECB）官方参考汇率把{c}换算成{o}等30种货币，每个工作日自动更新。可加银行/银行卡手续费，并查看90天走势。',
           h1='<b>汇率</b>换算', sub='欧洲央行官方参考汇率，每个工作日更新 – 含手续费估算和90天走势。',
           amount='金额', frm='从', to='换成', swap='互换', fee='银行/银行卡手续费（%）', feeNote='银行和银行卡通常在参考汇率上加收1–3%。填入你的费率，看看实际要付多少。',
           res='结果', rate='汇率', inv='反向汇率', withFee='含手续费需付／可得', trend='90天走势', hi='最高', lo='最低', chg='变化',
           table='今日{c}对主要货币', col1='1 {c} =', col2='1单位折合{c}', asof='欧洲央行参考汇率（{d}）', src='来源：欧洲央行欧元参考汇率（仅供参考）。',
           q1='今天100{c}等于多少{o}？', a1='按{d}欧洲央行参考汇率，100 {c} = {v} {o}。银行和兑换点会加收差价，实际到手通常略少。',
           q2='汇率什么时候更新？', a2='欧洲央行在每个工作日欧洲中部时间16点左右公布参考汇率，本页随后自动更新。',
           q3='为什么银行的汇率不一样？', a3='欧洲央行汇率是中间价，银行和发卡机构会加收差价或手续费（常见1–3%）。把这个比例填进手续费栏即可估算。'),
 'hi': dict(slug='currency-converter.html', title='मुद्रा परिवर्तक {c} – आज की विनिमय दर ({o}, EUR, GBP …)', desc='यूरोपीय सेंट्रल बैंक की आधिकारिक संदर्भ दरों से {c} को {o} और 30 मुद्राओं में बदलें, हर कार्यदिवस अपडेट। बैंक/कार्ड शुल्क और 90 दिन का चार्ट भी।',
           h1='<b>मुद्रा</b> परिवर्तक', sub='ECB की आधिकारिक संदर्भ दरें, हर कार्यदिवस अपडेट – शुल्क अनुमान और 90 दिन के चार्ट के साथ।',
           amount='राशि', frm='से', to='में', swap='बदलें', fee='बैंक / कार्ड शुल्क (%)', feeNote='बैंक और कार्ड आमतौर पर संदर्भ दर पर 1–3 % जोड़ते हैं। असली राशि देखने के लिए अपना शुल्क डालें।',
           res='परिणाम', rate='विनिमय दर', inv='उल्टी दर', withFee='शुल्क सहित आप देंगे / पाएंगे', trend='90 दिन का रुझान', hi='उच्चतम', lo='न्यूनतम', chg='बदलाव',
           table='आज प्रमुख मुद्राओं के मुकाबले {c}', col1='1 {c} =', col2='1 इकाई {c} में', asof='ECB संदर्भ दर, {d}', src='स्रोत: यूरोपीय सेंट्रल बैंक – यूरो संदर्भ विनिमय दरें (केवल जानकारी के लिए)।',
           q1='आज 100 {c} कितने {o} हैं?', a1='{d} की ECB संदर्भ दर पर 100 {c} = {v} {o}। बैंक और मनी एक्सचेंज अपना मार्जिन जोड़ते हैं, इसलिए आमतौर पर थोड़ा कम मिलता है।',
           q2='दरें कब अपडेट होती हैं?', a2='यूरोपीय सेंट्रल बैंक हर कार्यदिवस मध्य यूरोपीय समय लगभग 16:00 बजे संदर्भ दरें जारी करता है। यह पेज उसके बाद अपने आप अपडेट होता है।',
           q3='मेरा बैंक अलग दर क्यों दिखाता है?', a3='ECB दर मध्य दर है। बैंक और कार्ड जारीकर्ता मार्जिन या शुल्क (अक्सर 1–3 %) जोड़ते हैं। वह प्रतिशत शुल्क वाले खाने में डालें।'),
}
DEC_COMMA = {'de', 'fr', 'es', 'it', 'nl', 'pt', 'pl', 'sv', 'nb', 'da', 'tr', 'id'}
GROUP = {'de': '.', 'es': '.', 'it': '.', 'nl': '.', 'pt': '.', 'da': '.', 'tr': '.', 'id': '.', 'fr': ' ', 'pl': ' ', 'sv': ' ', 'nb': ' '}


def fmt(x, lang, dp=None):
    if dp is None:
        dp = 2 if x >= 1 else (4 if x >= 0.01 else 6)
    s = f'{x:,.{dp}f}'
    if lang in DEC_COMMA:
        s = s.replace(',', '§').replace('.', ',').replace('§', GROUP.get(lang, '.'))
    return s


def rate(a, b):
    return R[b] / R[a]


def date_txt(lang):
    y, m, d = DATE.split('-')
    if lang in ('ja', 'zh'):
        return f'{y}年{int(m)}月{int(d)}日'
    if lang in ('en', 'hi', 'ms', 'id'):
        return f'{y}-{m}-{d}'
    return f'{d}.{m}.{y}' if lang in ('de', 'pl', 'nb', 'da', 'tr') else f'{d}/{m}/{y}'


CSS = ('<style id="fx-css">.fx-row{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:end}.fx-row select{width:100%}'
       '#fx-swap{height:46px;padding:0 12px;border-radius:10px;border:1px solid #CBD3DF;background:#fff;font:inherit;font-weight:800;cursor:pointer}'
       '.fx-note{font-size:13px;color:#5B6B82;line-height:1.55;margin:6px 0}.fx-tbl{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}'
       '.fx-kv{display:grid;grid-template-columns:auto 1fr;gap:8px 12px;margin-top:12px;font-size:14px}.fx-kv div:nth-child(even){text-align:right;font-weight:700;overflow-wrap:anywhere}'
       '.fx-tbl th,.fx-tbl td{padding:8px 6px;border-bottom:1px solid #E3E7EE;text-align:right;white-space:nowrap}.fx-tbl th:first-child,.fx-tbl td:first-child{text-align:left}'
       '.fx-tbl thead th{font-size:12px;color:#5B6B82;white-space:normal;vertical-align:bottom}.fx-tbl td small{display:block;font-size:12px;color:#5B6B82;white-space:normal;max-width:150px}.fx-tbl tbody tr{cursor:pointer}.fx-tbl tbody tr:hover{background:#F7F8FB}'
       '#fx-chart{width:100%;height:170px;display:block}.fx-st{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px;color:#5B6B82;margin-top:6px}.fx-st b{color:#12305C}'
       '.fx-chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 0}.fx-chips button{font:inherit;font-size:13px;padding:6px 10px;border-radius:999px;border:1px solid #CBD3DF;background:#fff;cursor:pointer}'
       '@media(max-width:420px){.fx-row{grid-template-columns:1fr 1fr}.fx-row #fx-swap{grid-column:1/-1;order:3}}</style>')


def tpl_for(cc):
    d = os.path.join(SITE, cc)
    for f in sorted(os.listdir(d)):
        if f.endswith('.html') and f != 'index.html':
            h = open(os.path.join(d, f), encoding='utf-8').read()
            if '<header class="hero">' in h and '<footer>' in h:
                return f, h
    return None, None


def build(cc):
    lang, cur, others = C[cc]
    others = [o for o in others if o in R and o != cur]
    t = T[lang]
    tf, h = tpl_for(cc)
    if not h:
        return None
    url = f'{B}/{cc}/{t["slug"]}'
    o = others[0]
    F = lambda s: s.replace('{c}', cur).replace('{o}', o).replace('{d}', date_txt(lang))
    title, desc = F(t['title']), F(t['desc'])
    v100 = fmt(100 * rate(cur, o), lang)
    faq = [(F(t['q1']), F(t['a1']).replace('{v}', v100)), (F(t['q2']), F(t['a2'])), (F(t['q3']), F(t['a3']))]
    h = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', h, count=1)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h, count=1)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(title)}">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(desc)}">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', h)
    h = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{E(title)}">', h)
    h = re.sub(r'(?s)<script type="application/ld\+json">.*?</script>', '', h)
    h = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', h)
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": title.split(' – ')[0], "url": url, "applicationCategory": "FinanceApplication",
           "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": cur}, "dateModified": DATE},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    h = h.replace('</head>', CSS + ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld) + '</head>', 1)
    rows = ''.join(f'<tr data-c="{x}"><td><b>{x}</b><small class="fx-n" data-n="{x}"></small></td><td>{fmt(rate(cur, x), lang)}</td><td>{fmt(rate(x, cur), lang)}</td></tr>' for x in others)
    opts = ''.join(f'<option value="{x}">{x}</option>' for x in sorted(R))
    body = (f'<header class="hero"><div class="in"><span class="year">{E(date_txt(lang))}</span><h1>{t["h1"]}</h1><p>{E(t["sub"])}</p></div></header>\n<main class="wrap">\n'
            f'<section class="app"><form class="card" onsubmit="return false"><label class="f"><span>{E(t["amount"])}</span><input id="fx-a" inputmode="decimal" value="100"></label>'
            f'<div class="fx-row"><label class="f"><span>{E(t["frm"])}</span><select id="fx-f">{opts}</select></label><button type="button" id="fx-swap" aria-label="{E(t["swap"])}">⇄</button>'
            f'<label class="f"><span>{E(t["to"])}</span><select id="fx-t">{opts}</select></label></div>'
            f'<div class="fx-chips" id="fx-chips">' + ''.join(f'<button type="button" data-p="{cur}-{x}">{cur} → {x}</button>' for x in others[:5]) + '</div>'
            f'<label class="f" style="margin-top:10px"><span>{E(t["fee"])}</span><input id="fx-fee" inputmode="decimal" value="0"></label><p class="fx-note">{E(t["feeNote"])}</p></form>'
            f'<section class="card" id="fx-out" role="status"><div class="big"><span>{E(t["res"])}</span><b>100 {cur} = {fmt(100 * rate(cur, o), lang)} {o}</b><em>{E(F(t["asof"]))}</em></div></section></section>\n'
            f'<section class="card"><h2>{E(t["trend"])}: <span id="fx-pair">{cur}/{o}</span></h2><svg id="fx-chart" viewBox="0 0 600 170" preserveAspectRatio="none" role="img" aria-label="{E(t["trend"])}"></svg><div class="fx-st" id="fx-st"></div></section>\n'
            f'<section class="card"><h2>{E(F(t["table"]))}</h2><div style="overflow-x:auto"><table class="fx-tbl"><thead><tr><th></th><th>{E(F(t["col1"]))}</th><th>{E(F(t["col2"]))}</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<p class="fx-note">{E(F(t["asof"]))}. {E(t["src"])}</p></section>\n'
            '<article class="card help"><h2>FAQ</h2>' + ''.join(f'<h3>{E(q)}</h3><p>{E(a)}</p>' for q, a in faq) + '</article>\n</main>\n')
    h = re.sub(r'(?s)<header class="hero">.*?(?=<footer>)', lambda m: body, h, count=1)
    cfg = {'cur': cur, 'to': o, 'lang': lang, 'loc': re.search(r'<html lang="([^"]+)"', h).group(1), 'L': {k: t[k] for k in ('res', 'rate', 'inv', 'withFee', 'hi', 'lo', 'chg')}, 'asof': F(t['asof'])}
    i = h.index('</footer>') + len('</footer>')
    rest = re.sub(r'(?s)<script>\s*\(function\(\)\{\'use strict\';.*?</script>', '', h[i:], count=1)
    h = h[:i] + rest.replace('</body>', f'<script>window.FXCFG={json.dumps(cfg, ensure_ascii=False)};</script><script src="/assets/fx.js" defer></script></body>', 1)
    out = os.path.join(SITE, cc, t['slug'])
    if os.path.exists(out) and 'FXCFG' not in open(out, encoding='utf-8').read():
        return None  # 같은 이름의 다른 페이지가 이미 있으면 건드리지 않음
    open(out, 'w', encoding='utf-8').write(h)
    return {'url': f'/{cc}/{t["slug"]}', 'hub': f'/{cc}/index.html', 'after': f'/{cc}/{tf}', 'label': title.split(' – ')[0]}


made = [p for p in (build(cc) for cc in C if os.path.isdir(os.path.join(SITE, cc))) if p]
# 새 페이지 목록에 더해 patch_newpages.py 가 사이트맵·허브 링크를 붙이게 한다
npj = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'new_pages.json')
cur = json.load(open(npj, encoding='utf-8')) if os.path.exists(npj) else []
urls = {p['url'] for p in cur}
cur += [p for p in made if p['url'] not in urls]
json.dump(cur, open(npj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 사이트맵 lastmod 를 환율 날짜로
sm = os.path.join(SITE, 'sitemap.xml'); s = open(sm, encoding='utf-8').read()
for p in made:
    loc = f'{B}{p["url"]}'
    s = re.sub(r'(<loc>' + re.escape(loc) + r'</loc><lastmod>)[^<]*', r'\g<1>' + DATE, s)
open(sm, 'w', encoding='utf-8').write(s)
print('fx pages:', len(made), 'rates', DATE)
