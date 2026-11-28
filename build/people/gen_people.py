"""People pages ("Edad de los famosos" / "Idade dos famosos") built at deploy from data-people (Wikidata facts).
Numbers are written into the HTML (age, days, next birthday, World Cup ages, age at each milestone) and change every day.
One design per category (futbolista · politico · cantante · actor · empresario). No photos; kit/initials card instead.
Usage: python3 build/people/gen_people.py _site"""
import datetime as dt, html, json, os, re, sys, unicodedata

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
B = 'https://honglifecalc.com'
D = json.load(open(os.path.join(SITE, 'people-data', 'people.json'), encoding='utf-8'))
REG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'people.json'), encoding='utf-8'))
TODAY = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).date()
E = lambda s: html.escape(str(s), quote=True)

L10N = {
 'es': dict(dir='/es/edad/', shell='arg/calculadora-vacaciones.html', shell_url='/arg/calculadora-vacaciones.html', locale='es-AR', hub='Famosos en números',
            hub_lead='Edad, altura y momentos clave de los famosos en números, y cómo te comparás con ellos.', age='edad', years='años', months='meses', days='días',
            mes=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'], home='Inicio',
            signs=['Capricornio','Acuario','Piscis','Aries','Tauro','Géminis','Cáncer','Leo','Virgo','Libra','Escorpio','Sagitario'],
            zod=['Rata','Buey','Tigre','Conejo','Dragón','Serpiente','Caballo','Cabra','Mono','Gallo','Perro','Cerdo'], src='Datos'),
 'en': dict(dir='/us/age/', shell='us/electricity-cost-calculator.html', shell_url='/us/electricity-cost-calculator.html', locale='en-US', hub='Famous People in Numbers',
            hub_lead='How old famous people are today, how tall they are, their big moments by age, and how you compare.', age='age', years='years', months='months', days='days',
            mes=['January','February','March','April','May','June','July','August','September','October','November','December'], home='Home',
            signs=['Capricorn','Aquarius','Pisces','Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius'],
            zod=['Rat','Ox','Tiger','Rabbit','Dragon','Snake','Horse','Goat','Monkey','Rooster','Dog','Pig'], src='Data'),
 'pt': dict(dir='/br/idade/', shell='br/calculadora-ferias.html', shell_url='/br/calculadora-ferias.html', locale='pt-BR', hub='Famosos em números',
            hub_lead='Idade, altura e momentos marcantes dos famosos em números, e como você se compara com eles.', age='idade', years='anos', months='meses', days='dias',
            mes=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'], home='Início',
            signs=['Capricórnio','Aquário','Peixes','Áries','Touro','Gêmeos','Câncer','Leão','Virgem','Libra','Escorpião','Sagitário'],
            zod=['Rato','Búfalo','Tigre','Coelho','Dragão','Serpente','Cavalo','Cabra','Macaco','Galo','Cão','Porco'], src='Dados'),
}
T = {  # phrases
 'es': dict(has='tiene', born='Nació el', in_='en', turns='Cumplirá', on='el', within='dentro de', today='Edad hoy', lived='Días vividos', nextb='Próximo cumpleaños',
            inD='en', height='Altura', sign='Signo · horóscopo chino', cups='¿Cuántos años tendrá en los Mundiales?', career='Su carrera según su edad',
            cmp='Comparate con', yourb='Tu fecha de nacimiento', yourh='Tu altura (cm)', others='Otros famosos', faq='Preguntas frecuentes',
            q_age='¿Cuántos años tiene {n}?', q_h='¿Cuánto mide {n}?', q_cup='¿Qué edad tendrá {n} en el Mundial 2030?', q_sign='¿De qué signo es {n}?',
            q_office='¿A qué edad asumió {n} como {p}?', q_since='¿Desde cuándo {n} se dedica a lo suyo?', q_found='¿A qué edad fundó {n} {c}?',
            office='Cargos y edad al asumir', inoffice='lleva {d} días en el cargo', founded='Empresas que fundó', company_age='la empresa tiene {y} años',
            work='Años de carrera', since='desde {y}', award='premio', team='equipo', start='Llega a', debut='Debut en la', cup='Mundial',
            older='mayor', younger='menor', cmp_txt='{n} es <b>{y} años {w}</b> que vos. Cuando {n} tenía tu edad ({a}) era <b>{yr}</b>.',
            cmp_h=' Medís <b>{d} cm {w}</b> que {n}.', more='más', less='menos', you='Vos', note='Sin fotos ni datos de la vida privada. Datos públicos de Wikidata (CC0).',
            upd='Actualizado', range='entre {a} y {b}', yr='año'),
 'pt': dict(has='tem', born='Nasceu em', in_='em', turns='Fará', on='em', within='daqui a', today='Idade hoje', lived='Dias vividos', nextb='Próximo aniversário',
            inD='em', height='Altura', sign='Signo · horóscopo chinês', cups='Quantos anos terá nas Copas do Mundo?', career='A carreira pela idade',
            cmp='Compare-se com', yourb='Sua data de nascimento', yourh='Sua altura (cm)', others='Outros famosos', faq='Perguntas frequentes',
            q_age='Quantos anos tem {n}?', q_h='Quanto mede {n}?', q_cup='Quantos anos {n} terá na Copa de 2030?', q_sign='Qual é o signo de {n}?',
            q_office='Com que idade {n} assumiu como {p}?', q_since='Desde quando {n} atua?', q_found='Com que idade {n} fundou {c}?',
            office='Cargos e idade ao assumir', inoffice='está há {d} dias no cargo', founded='Empresas que fundou', company_age='a empresa tem {y} anos',
            work='Anos de carreira', since='desde {y}', award='prêmio', team='time', start='Chega ao', debut='Estreia na', cup='Copa',
            older='mais velho', younger='mais novo', cmp_txt='{n} é <b>{y} anos {w}</b> que você. Quando {n} tinha a sua idade ({a}) era <b>{yr}</b>.',
            cmp_h=' Você mede <b>{d} cm {w}</b> que {n}.', more='a mais', less='a menos', you='Você', note='Sem fotos nem dados da vida privada. Dados públicos do Wikidata (CC0).',
            upd='Atualizado', range='entre {a} e {b}', yr='ano'),
 'en': dict(has='is', born='Born', in_='in', turns='Turns', on='on', within='in', today='Age today', lived='Days alive', nextb='Next birthday',
            inD='in', height='Height', sign='Zodiac · Chinese zodiac', cups='How old at the next World Cups?', career='Career by age',
            cmp='Compare yourself with', yourb='Your date of birth', yourh='Your height (cm)', others='More famous people', faq='FAQ',
            q_age='How old is {n}?', q_h='How tall is {n}?', q_cup='How old will {n} be at the 2030 World Cup?', q_sign="What is {n}'s zodiac sign?",
            q_office='How old was {n} when first taking office as {p}?', q_since='When did {n} start their career?', q_found='How old was {n} when founding {c}?',
            office='Office and age at taking office', inoffice='{d} days in office', founded='Companies founded', company_age='the company is {y} years old',
            work='Years in the business', since='since {y}', award='award', team='team', start='Joins', debut='Debut for', cup='World Cup',
            older='older', younger='younger', cmp_txt='{n} is <b>{y} years {w}</b> than you. When {n} was your age ({a}) it was <b>{yr}</b>.',
            cmp_h=' You are <b>{d} cm {w}</b> than {n}.', more='taller', less='shorter', you='You', note='No photos and no private life. Public facts from Wikidata (CC0).',
            upd='Updated', range='{a}–{b}', yr='year'),
}
CUPS = [('2026', '2026-06-11'), ('2030', '2030-06-08'), ('2034', '2034-06-01')]  # opening days (2034: month known, day approximate → shown as age range)


def slug(s):
    s = unicodedata.normalize('NFKD', re.sub(r'\s*\(.*?\)', '', s)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def d(s): return dt.date.fromisoformat(s if len(s) == 10 else (s + '-01-01')[:10])


def bday(b, y):
    """birthday in year y (29 Feb → 28 Feb in non-leap years)"""
    try: return b.replace(year=y)
    except ValueError: return dt.date(y, 2, 28)


def age_at(b, x):
    try: bd = b.replace(year=x.year)
    except ValueError: bd = dt.date(x.year, 2, 28)
    return x.year - b.year - (x < bd)


def age_txt(b, s, t):
    """age at date s; a year-only (YYYY) or month-only (YYYY-MM) date becomes a range when the age changes inside it"""
    if not s: return None
    if len(s) == 10: return str(age_at(b, d(s)))
    if len(s) == 7:
        y, m = int(s[:4]), int(s[5:7]); lo = dt.date(y, m, 1); hi = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))
    else:
        y = int(s[:4]); lo, hi = dt.date(y, 1, 1), dt.date(y, 12, 31)
    a, c = age_at(b, lo), age_at(b, hi)
    return str(a) if a == c else f'{a}–{c}'


def n(x): return f'{x:,}'.replace(',', '.')


def sign(L, b):
    cuts = [(1, 20), (2, 19), (3, 21), (4, 20), (5, 21), (6, 21), (7, 23), (8, 23), (9, 23), (10, 23), (11, 22), (12, 22)]
    i = b.month - 1 if (b.month, b.day) >= cuts[b.month - 1] else (b.month - 2) % 12
    return L['signs'][(i + 1) % 12]


CSS = {
 'base': '''<style id="pp-css">section.app.pp{display:block!important;grid-template-columns:none!important;min-width:0;max-width:100%}
.pp-ans{font-size:18px;line-height:1.6;margin:2px 2px 16px}
.pp-hero{display:grid;grid-template-columns:150px minmax(0,1fr);gap:14px;align-items:stretch}
.pp-nums{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.pp-n{border-radius:14px;padding:10px 12px;min-width:0;border:1px solid #E2E8F0;background-color:#fff}
.pp-n small{display:block;font-size:12px;color:#64748B}.pp-n b{display:block;font-size:20px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere;color:#0F172A}
.pp-n.pp-hi{grid-column:1/-1}.pp-n.pp-hi b{font-size:28px}
.pp h2{font-size:20px;margin:24px 0 10px}
.pp-box{background-color:#fff;border:1px solid #E2E8F0;border-radius:16px;padding:14px}
.pp-tl{list-style:none;margin:0;padding:0;position:relative}.pp-tl:before{content:"";position:absolute;left:59px;top:8px;bottom:8px;width:3px;border-radius:3px;background-color:var(--pp-line,#CBD5E1)}
.pp-tl li{display:grid;grid-template-columns:48px 22px minmax(0,1fr);gap:6px;align-items:start;padding:6px 0}
.pp-tl .a{font-weight:900;text-align:right;color:#0F172A;font-variant-numeric:tabular-nums}.pp-tl .a.r{font-size:13px;padding-top:3px}
.pp-tl .o{width:14px;height:14px;border-radius:50%;margin-top:5px;background-color:var(--pp-dot,#64748B);border:3px solid #fff;box-shadow:0 0 0 2px var(--pp-line,#CBD5E1)}
.pp-tl .t{font-size:15px;overflow-wrap:anywhere}.pp-tl .t small{display:block;font-size:12.5px;color:#64748B}
.pp-cups{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.pp-cups div{border-radius:12px;padding:10px;text-align:center;background-color:#FFF8E1;border:1px solid #F5D77A;min-width:0}.pp-cups b{display:block;font-size:24px}.pp-cups small{font-size:12px;color:#7A5B00}
.pp-cmp .row{display:grid;grid-template-columns:1fr 1fr;gap:10px}.pp-cmp label{display:block;font-size:13px;font-weight:700}.pp-cmp input{display:block;width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:10px;border:1px solid #CBD5E1;border-radius:10px;margin-top:4px}
.pp-out{margin-top:10px;font-size:15px;background-color:#F5F7FB;border-radius:12px;padding:10px 12px}
.pp-sil{display:flex;align-items:flex-end;justify-content:center;gap:30px;height:230px;margin-top:12px;border-bottom:2px solid #E2E8F0}.pp-sil div{text-align:center;font-size:12.5px;color:#64748B}
.pp-oth{display:flex;flex-wrap:wrap;gap:8px}.pp-oth a{border:1px solid #E2E8F0;background-color:#fff;border-radius:999px;padding:6px 12px;font-size:14px;color:#0F172A;text-decoration:none}
@media(max-width:560px){.pp-hero{grid-template-columns:104px minmax(0,1fr);gap:10px}.pp-n b{font-size:17px}.pp-n.pp-hi b{font-size:22px}.pp-cmp .row{grid-template-columns:1fr}.pp-ans{font-size:16.5px}}
</style>''',
 'futbolista': '''<style>.pp-card{position:relative;border-radius:16px;overflow:hidden;min-height:190px;border:3px solid #0B2545}
.pp-card b{position:absolute;left:0;right:0;top:40px;text-align:center;font-size:84px;font-weight:900;color:#0B2545;text-shadow:0 2px 0 #fff}
.pp-card span{position:absolute;left:0;right:0;bottom:0;background-color:#0B2545;color:#fff;text-align:center;font-size:12.5px;font-weight:800;padding:6px 4px}
.pp{--pp-line:#74ACDF;--pp-dot:#F2B705}@media(max-width:560px){.pp-card b{font-size:60px;top:36px}.pp-card{min-height:160px}}</style>''',
 'politico': '''<style>.pp-card{position:relative;border-radius:6px;min-height:190px;background-color:#FBF8F0;border:1px solid #D9CFB4;box-shadow:0 6px 18px rgba(60,40,10,.08);display:flex;align-items:center;justify-content:center}
.pp-card b{width:96px;height:96px;border-radius:50%;border:3px double #7C2D12;color:#7C2D12;display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;font-size:34px;transform:rotate(-8deg)}
.pp-card span{position:absolute;left:8px;right:8px;bottom:8px;text-align:center;font-family:Georgia,serif;font-size:12.5px;color:#5B4A2A}
.pp{--pp-line:#C9B98E;--pp-dot:#7C2D12}.pp-n.pp-hi{background-color:#FBF8F0;border-color:#D9CFB4}</style>''',
 'cantante': '''<style>.pp-card{position:relative;border-radius:16px;min-height:190px;background-color:#120A24;overflow:hidden;display:flex;align-items:center;justify-content:center}
.pp-card:before{content:"";position:absolute;left:50%;top:-40%;width:180%;height:140%;margin-left:-90%;background:radial-gradient(ellipse at top,rgba(255,214,102,.55),transparent 60%)}
.pp-card b{position:relative;font-size:52px;font-weight:900;color:#FFD666;letter-spacing:2px}
.pp-card span{position:absolute;left:0;right:0;bottom:8px;text-align:center;font-size:12.5px;color:#E9D5FF;font-weight:700}
.pp{--pp-line:#C4B5FD;--pp-dot:#7C3AED}.pp-n.pp-hi{background-color:#120A24;border-color:#120A24}.pp-n.pp-hi small{color:#C4B5FD}.pp-n.pp-hi b{color:#FFD666}</style>''',
 'actor': '''<style>.pp-card{position:relative;border-radius:10px;min-height:190px;background-color:#111;display:flex;align-items:center;justify-content:center;border-left:14px dashed #444;border-right:14px dashed #444}
.pp-card b{font-size:50px;font-weight:900;color:#F5F5F4;font-family:Georgia,serif}
.pp-card span{position:absolute;left:0;right:0;bottom:8px;text-align:center;font-size:12px;color:#D6D3D1;letter-spacing:.12em}
.pp{--pp-line:#D6D3D1;--pp-dot:#B91C1C}</style>''',
 'atleta': '''<style>.pp-card{position:relative;border-radius:16px;min-height:190px;background-color:#0F3D2E;overflow:hidden;display:flex;align-items:center;justify-content:center;border:3px solid #0B2545}
.pp-card:before{content:"";position:absolute;inset:14px;border:2px solid rgba(255,255,255,.55);border-radius:10px}.pp-card:after{content:"";position:absolute;left:50%;top:14px;bottom:14px;border-left:2px solid rgba(255,255,255,.55)}
.pp-card b{position:relative;z-index:1;font-size:50px;font-weight:900;color:#fff;background-color:#0B2545;border-radius:50%;width:92px;height:92px;display:flex;align-items:center;justify-content:center}
.pp-card span{position:absolute;left:0;right:0;bottom:0;background-color:#0B2545;color:#fff;text-align:center;font-size:11.5px;font-weight:800;padding:6px 4px;z-index:1}
.pp{--pp-line:#86EFAC;--pp-dot:#0B2545}</style>''',
 'creador': '''<style>.pp-card{position:relative;border-radius:26px;min-height:190px;background-color:#111827;border:6px solid #1F2937;display:flex;align-items:center;justify-content:center}
.pp-card:before{content:"";position:absolute;top:8px;left:50%;width:40px;height:6px;margin-left:-20px;border-radius:3px;background-color:#374151}
.pp-card b{font-size:44px;font-weight:900;color:#fff;background:linear-gradient(135deg,#F43F5E,#8B5CF6);border-radius:18px;width:92px;height:92px;display:flex;align-items:center;justify-content:center}
.pp-card span{position:absolute;left:0;right:0;bottom:10px;text-align:center;font-size:11.5px;color:#D1D5DB;font-weight:700}
.pp{--pp-line:#F9A8D4;--pp-dot:#8B5CF6}</style>''',
 'otro': '''<style>.pp-card{position:relative;border-radius:4px 14px 14px 4px;min-height:190px;background-color:#7C2D12;border-left:12px solid #451A03;display:flex;align-items:center;justify-content:center}
.pp-card b{font-size:44px;color:#FEF3C7;font-family:Georgia,serif;border-top:2px solid #FCD34D;border-bottom:2px solid #FCD34D;padding:6px 10px}
.pp-card span{position:absolute;left:0;right:0;bottom:10px;text-align:center;font-size:11.5px;color:#FDE68A;letter-spacing:.1em}
.pp{--pp-line:#FCD34D;--pp-dot:#7C2D12}</style>''',
 'empresario': '''<style>.pp-card{position:relative;border-radius:14px;min-height:190px;background-color:#0B1220;display:flex;align-items:center;justify-content:center;font-family:Consolas,monospace}
.pp-card b{font-size:46px;color:#34D399;text-shadow:0 0 10px rgba(52,211,153,.5)}
.pp-card span{position:absolute;left:0;right:0;bottom:8px;text-align:center;font-size:12px;color:#94A3B8}
.pp{--pp-line:#94A3B8;--pp-dot:#0EA5E9}.pp-n.pp-hi{background-color:#0B1220;border-color:#0B1220}.pp-n.pp-hi small{color:#94A3B8}.pp-n.pp-hi b{color:#34D399}</style>''',
}

KEY_AW = re.compile(r'^(FIFA )?Bal[oó]n de Oro$|^Bola de Ouro$|The Best|Bota de Oro|Chuteira de Ouro|Golden Boy|Laureus|Princesa de Asturias|Grammy|Goya|Mart[ií]n Fierro|Konex|Nobel|Oscar|Premio Gardel|Premios? Lo Nuestro', re.I)
YOUTH = re.compile(r'sub-|\bU-?\d\d|"[A-C]"|Atl[eè]tic|\sB$|juvenil|Ol[ií]mpic|base|reservas', re.I)


def fdate(lang, x):
    m = L10N[lang]['mes'][x.month - 1]
    return f'{m} {x.day}, {x.year}' if lang == 'en' else f'{x.day} de {m} de {x.year}'


def ftin(cm):
    tot = round(cm / 2.54); return f"{tot // 12}'{tot % 12}\""


def initials(lab):
    w = [x for x in re.sub(r'\(.*?\)', '', lab).split() if x[:1].isalpha()]
    return (w[0][0] + (w[-1][0] if len(w) > 1 else '')).upper()


def build(p, others):
    L = L10N[p['lang']]; t = T[p['lang']]; lab = p['label']; short = re.sub(r'\s*\(.*?\)', '', lab)
    b = d(p['birth']); dead = p.get('death')
    if dead: return None  # living people only in this section
    age = age_at(b, TODAY)
    nb = bday(b, TODAY.year)
    if nb <= TODAY: nb = bday(b, TODAY.year + 1)
    last = bday(b, nb.year - 1)
    mm = (TODAY.year - last.year) * 12 + TODAY.month - last.month; dd = TODAY.day - last.day
    if dd < 0:
        mm -= 1; dd += (TODAY.replace(day=1) - dt.timedelta(days=1)).day
    days = (TODAY - b).days; to_next = (nb - TODAY).days
    cm = p.get('cm')
    if not cm: hm = None
    elif p['lang'] == 'en': hm = f"{ftin(cm)} ({cm} cm)"
    else: hm = f"{cm / 100:.2f}".replace('.', ',') + ' m'
    cat = p['cat']; mes = L['mes']
    url = L['dir'] + slug(lab) + '.html'
    # career events
    ev = []
    if cat == 'futbolista':
        seen = set()
        for tm in sorted(p['teams'], key=lambda x: x['s'] or '9'):
            if not tm['s'] or YOUTH.search(tm['n']) or tm['n'] in seen: continue
            seen.add(tm['n']); ev.append((tm['s'], (t['debut'] + ' ' if re.search(r'selecci', tm['n'], re.I) else t['start'] + ' ') + tm['n'], t['team']))
    if cat == 'politico':
        seenP = set()
        for ps in sorted(p['positions'], key=lambda x: x['s'] or '9'):
            if ps['s'] and ps['n'] not in seenP:
                seenP.add(ps['n']); ev.append((ps['s'], ps['n'], 'cargo'))
    if cat == 'empresario':
        for c in p['founded']:
            if c['d']: ev.append((c['d'], c['n'], 'fund'))
    if p.get('work_start'):
        ev.append((p['work_start'], {'es': 'Comienzo de su carrera', 'pt': 'Início da carreira', 'en': 'Career begins'}[p['lang']], 'start'))
    cnt = {}
    for a in sorted(p['awards'], key=lambda x: x['d'] or '9'):
        if a['d'] and KEY_AW.search(a['n']):
            k = a['n']; cnt[k] = cnt.get(k, 0) + 1
            nm = (f"{cnt[k]}.º " if re.search(r'Bal[oó]n de Oro$|Bola de Ouro$', k) else '') + re.sub(r'^Anexo:', '', k)
            ev.append((a['d'], nm, t['award']))
    ev.sort(key=lambda x: x[0]); ev = ev[:24]
    tl = ''.join(f'<li><span class="a{" r" if len(e[0]) < 10 and "–" in (age_txt(b, e[0], t) or "") else ""}">{age_txt(b, e[0], t)}</span><span class="o"></span><span class="t">{E(e[1])}<small>{e[0][:4]}</small></span></li>' for e in ev)
    # card
    if cat == 'futbolista' and p.get('kit'):
        c1, c2, num, country = p['kit']
        card = f'<div class="pp-card" style="background:repeating-linear-gradient(90deg,{c1} 0 24px,{c2} 24px 48px)"><b>{E(num or initials(lab))}</b><span>{E(country)}</span></div>'
    else:
        SUB = {'es': dict(futbolista='FÚTBOL', politico='POLÍTICA', cantante='MÚSICA', actor='CINE · TV', empresario='EMPRESA', atleta='DEPORTE', creador='PANTALLA', otro='CULTURA'),
               'pt': dict(futbolista='FUTEBOL', politico='POLÍTICA', cantante='MÚSICA', actor='CINEMA · TV', empresario='EMPRESA', atleta='ESPORTE', creador='TELA', otro='CULTURA'),
               'en': dict(futbolista='SOCCER', politico='POLITICS', cantante='MUSIC', actor='FILM · TV', empresario='BUSINESS', atleta='SPORTS', creador='SCREEN', otro='IDEAS')}
        sub = SUB[p['lang']][cat]
        if cat == 'atleta' and p.get('occ'): sub = E(p['occ'][0]).upper()[:28]
        card = f'<div class="pp-card"><b>{E(initials(lab))}</b><span>{sub}</span></div>'
    # extra blocks per category
    extra = ''
    faq = [(t['q_age'].format(n=short), f"{age} {L['years']} ({b.day}/{b.month}/{b.year}).")]
    if hm: faq.append((t['q_h'].format(n=short), f"{hm} ({cm} cm)."))
    if cat == 'futbolista':
        cells = ''
        for y, s in CUPS:
            a = age_at(b, d(s)); r = f"{a}–{a + 1}" if (y == '2034' and b.month in (6, 7)) else f"{a}"
            cells += f'<div><small>{t["cup"]} {y}</small><b>{r}</b><small>{L["years"]}</small></div>'
        extra += f'<h2>{t["cups"]}</h2><div class="pp-cups">{cells}</div>'
        faq.append((t['q_cup'].format(n=short), f"{age_at(b, d('2030-06-08'))} {L['years']}."))
    if cat == 'atleta':
        H = {'es': '¿Qué edad tendrá en los próximos Juegos Olímpicos?', 'pt': 'Quantos anos terá nos próximos Jogos Olímpicos?', 'en': 'Age at the next Olympics'}[p['lang']]
        G = [('Los Angeles 2028', '2028-07-14'), ({'es': 'Invierno 2030', 'pt': 'Inverno 2030', 'en': 'Winter 2030'}[p['lang']], '2030-02-01'), ('Brisbane 2032', '2032-07-23')]
        extra += f'<h2>{H}</h2><div class="pp-cups">' + ''.join(f'<div><small>{g}</small><b>{age_at(b, d(x))}</b><small>{L["years"]}</small></div>' for g, x in G) + '</div>'
    if cat == 'politico' and p['lang'] == 'en':
        extra += f'<h2>Age on Election Day 2028</h2><div class="pp-cups"><div><small>Nov 7, 2028</small><b>{age_at(b, d("2028-11-07"))}</b><small>years</small></div><div><small>Inauguration Jan 20, 2029</small><b>{age_at(b, d("2029-01-20"))}</b><small>years</small></div><div><small>End of term 2033</small><b>{age_at(b, d("2033-01-20"))}</b><small>years</small></div></div>'
    if cat == 'politico':
        cur = [ps for ps in p['positions'] if ps['s'] and not ps['e']]
        if cur:
            prio = lambda x: (0 if re.search(r'^Presidente (del Gobierno|de la Naci|do Brasil|da Rep|de la Rep)|Primer Ministro|Primeiro-Ministro|^Rey|^Rei', x['n']) else
                              1 if re.search(r'Presidente|Gobernador|Governador|Jefe de Gobierno|Alcalde|Prefeito|Ministr', x['n']) else 2)
            ps = sorted(cur, key=lambda x: (prio(x), x['s']))[0]
            first = min(x['s'] for x in p['positions'] if x['n'] == ps['n'] and x['s'])
            t1 = {'es': 'Primera vez', 'pt': 'Primeira vez', 'en': 'First time'}[p['lang']]; t2 = {'es': 'Mandato actual', 'pt': 'Mandato atual', 'en': 'Current term'}[p['lang']]
            extra += (f'<h2>{t["office"]}</h2><div class="pp-box"><p style="margin:0 0 6px;font-size:17px"><b>{E(ps["n"])}</b></p>'
                      f'<p style="margin:0;font-size:15px">{t1}: <b>{first[:4]}</b> · {L["age"]} <b>{age_txt(b, first, t)}</b><br>'
                      f'{t2}: {t["since"].format(y=ps["s"][:4])} · {t["inoffice"].format(d=n((TODAY - d(ps["s"])).days))}</p></div>')
            faq.append((t['q_office'].format(n=short, p=ps['n']), f"{age_txt(b, first, t)} {L['years']} ({first[:4]})."))
    if cat == 'empresario' and p['founded']:
        rows = ''.join(f'<li><span class="a">{age_txt(b, c["d"], t) or "—"}</span><span class="o"></span><span class="t">{E(c["n"])}<small>{(c["d"] or "")[:4]}{" · " + t["company_age"].format(y=age_at(d(c["d"]), TODAY)) if c["d"] else ""}</small></span></li>' for c in p['founded'] if c['d'])
        if rows: extra += f'<h2>{t["founded"]}</h2><div class="pp-box"><ul class="pp-tl">{rows}</ul></div>'
    if cat in ('cantante', 'actor') and p.get('work_start'):
        ws = p['work_start']; yrs = TODAY.year - int(ws[:4])
        extra += f'<h2>{t["work"]}</h2><div class="pp-box"><p style="margin:0;font-size:16px"><b>{yrs} {L["years"]}</b> · {t["since"].format(y=ws[:4])} · {L["age"]} {age_txt(b, ws, t)}</p></div>'
        faq.append((t['q_since'].format(n=short), t['since'].format(y=ws[:4]) + f" ({yrs} {L['years']})."))
    sg = sign(L, b); zd = L['zod'][(b.year - 4) % 12]
    faq.append((t['q_sign'].format(n=short), f"{sg}. {zd}."))
    place = f" {t['in_']} {E(p['place'])}" if p.get('place') else ''
    if p['lang'] == 'en':
        ans = (f"<b>{E(short)} is {age} years old.</b> Born {fdate('en', b)}{place}. "
               f"Turns {age + 1} on {fdate('en', nb)}, in {to_next} days.")
    else:
        ans = (f"<b>{E(short)} {t['has']} {age} {L['years']}.</b> {t['born']} {fdate(p['lang'], b)}{place}. "
               f"{t['turns']} {age + 1} {t['on']} {fdate(p['lang'], nb)}, {t['within']} {to_next} {L['days']}.")
    md = p['birth'][5:10]
    same_day = [o for o in others if o['qid'] != p['qid'] and o['birth'][5:10] == md][:6]
    near = sorted([o for o in others if o['qid'] != p['qid'] and o['cat'] == cat and o not in same_day], key=lambda o: abs(d(o['birth']) - b))[:10]
    oth = ''.join('<a href="' + L['dir'] + slug(o['label']) + '.html">' + E(re.sub(r'\s*\(.*?\)', '', o['label'])) + (' 🎂' if o in same_day else '') + '</a>' for o in same_day + near)
    cmpjs = ('<script>(function(){var B=new Date(' + f'{b.year},{b.month - 1},{b.day}' + '),H=' + str(cm or 0) + ',N=' + json.dumps(short) + ',T=' + json.dumps({k: t[k] for k in ('cmp_txt', 'cmp_h', 'older', 'younger', 'more', 'less', 'you')}, ensure_ascii=False)
             + ',$=function(i){return document.getElementById(i)};function A(x,y){var a=y.getFullYear()-x.getFullYear();if(y.getMonth()<x.getMonth()||(y.getMonth()===x.getMonth()&&y.getDate()<x.getDate()))a--;return a}'
             + 'function f(n){return n.toLocaleString()}function go(){var v=$("pm").value,h=parseFloat($("ph").value)||0;if(!v)return;var m=new Date(v+"T00:00:00"),now=new Date(),diff=(m-B)/864e5,y=Math.floor(Math.abs(diff)/365.2425),my=A(m,now);'
             + 'var s=T.cmp_txt.replace(/\\{n\\}/g,N).replace("{y}",y).replace("{w}",diff>0?T.older:T.younger).replace("{a}",my).replace("{yr}",B.getFullYear()+my);'
             + 'if(H&&h)s+=T.cmp_h.replace("{d}",Math.abs(Math.round(h-H))).replace("{w}",h>H?T.more:T.less).replace("{n}",N);$("po").innerHTML=s;'
             + 'if(H&&h){var p=function(c,col,l){return \'<div><svg width="\'+Math.round(c*0.34)+\'" height="\'+c+\'" viewBox="0 0 34 100" preserveAspectRatio="none"><circle cx="17" cy="9" r="8" fill="\'+col+\'"/><path d="M5 20Q17 15 29 20L27 58L22 58L21 100L13 100L12 58L7 58Z" fill="\'+col+\'"/></svg>\'+l+"<br><b>"+c+" cm</b></div>"};$("psil").innerHTML=p(H,"#0B2545",N)+p(Math.round(h),"#74ACDF",T.you)}}'
             + '$("pm").addEventListener("input",go);$("ph").addEventListener("input",go);go()})();</script>')
    body = (f'<section class="app pp" id="calc"><p class="pp-ans">{ans}</p><div class="pp-hero">{card}<div class="pp-nums">'
            f'<div class="pp-n pp-hi"><small>{t["today"]}</small><b>{age} {L["years"]}, {mm} {L["months"]} {dd} {L["days"]}</b></div>'
            f'<div class="pp-n"><small>{t["lived"]}</small><b>{n(days)}</b></div><div class="pp-n"><small>{t["nextb"]}</small><b>{t["inD"]} {to_next} {L["days"]}</b></div>'
            + (f'<div class="pp-n"><small>{t["height"]}</small><b>{hm}</b></div>' if hm else '')
            + '<div class="pp-n"' + ('' if hm else ' style="grid-column:1/-1"') + f'><small>{t["sign"]}</small><b>{sg} · {zd}</b></div></div></div>'
            + extra
            + (f'<h2>{t["career"]}</h2><div class="pp-box"><ul class="pp-tl">{tl}</ul></div>' if tl else '')
            + f'<h2>{t["cmp"]} {E(short)}</h2><div class="pp-box pp-cmp"><div class="row"><label>{t["yourb"]}<input type="date" id="pm" value="1995-03-15"></label>'
            + f'<label>{t["yourh"]}<input id="ph" inputmode="numeric" value="175"></label></div><div class="pp-out" id="po"></div>' + ('<div class="pp-sil" id="psil"></div>' if cm else '') + '</div>'
            + (f'<h2>{t["others"]}</h2><div class="pp-oth">{oth}</div>' if oth else '')
            + cmpjs + '</section>')
    if p['lang'] == 'en':
        title = f"{short} Age: {age} Years Old" + (f" | Height {ftin(cm)}" if cm else '')
    else:
        title = f"{short} {L['age']}: {age} {L['years']}" + (f" | {t['height']} {hm}" if hm else '')
    desc = re.sub('<[^>]+>', '', ans) + (f" {t['height']}: {hm}." if hm else '')
    art = (f'<h2 id="faq">{t["faq"]}</h2>' + ''.join(f'<h3>{E(q)}</h3><p>{E(a)}</p>' for q, a in faq)
           + f'<p class="note">{L["src"]}: <a href="https://www.wikidata.org/wiki/{p["qid"]}" rel="nofollow">Wikidata {p["qid"]}</a> · {t["upd"]} {TODAY.day}/{TODAY.month}/{TODAY.year}. {t["note"]}</p>')
    return dict(url=url, title=title, desc=desc, h1=(f"How old is {E(short)}?" if p['lang'] == 'en' else f"{E(short)} {L['age']}"), lead=E(p.get('desc') or ''), css=CSS['base'] + CSS[cat], body=body, art=art, faq=faq, lang=p['lang'], name=short, age=age, cat=cat, rank=p.get('views') or p.get('sitelinks', 0))


def shell(lang):
    L = L10N[lang]
    return open(os.path.join(SITE, L['shell']), encoding='utf-8').read(), B + L['shell_url']


def write(pg):
    s, old = shell(pg['lang']); L = L10N[pg['lang']]
    url = B + pg['url']
    s = re.sub(r'<title>.*?</title>', f'<title>{E(pg["title"])}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(pg["desc"])}">', s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(pg['title']), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + E(pg['desc']), s, count=1)
    s = s.replace(old, url)
    s = re.sub(r'<link rel="alternate" hreflang[^>]*>', '', s)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": pg['title'], "url": url, "inLanguage": L['locale'], "dateModified": TODAY.isoformat()},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": L['home'], "item": B + "/"},
              {"@type": "ListItem", "position": 2, "name": L['hub'], "item": B + L['dir']},
              {"@type": "ListItem", "position": 3, "name": pg['name'] if 'name' in pg else pg['title'], "item": url}]}]
    if pg.get('faq'):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pg['faq']]})
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</head>', ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in ld) + pg['css'] + '</head>', 1)
    s = re.sub(r'<header class="hero">.*?</header>', f'<header class="hero"><div class="in"><span class="year">{E(L["hub"])}</span><h1>{pg["h1"]}</h1><p>{pg["lead"]}</p></div></header>', s, count=1, flags=re.S)
    s = re.sub(r'<section class="app">.*?</section></section>', lambda m: pg['body'], s, count=1, flags=re.S)
    s = re.sub(r'<article class="card help">.*?</article>', lambda m: '<article class="card help">' + pg['art'] + '</article>', s, count=1, flags=re.S)
    s = re.sub(r"<script>\n\(function\(\)\{'use strict';.*?</script>", '', s, count=1, flags=re.S)
    s = re.sub(r'<script src="/assets/hl-viz\.js[^"]*" defer></script>', '', s)
    out = os.path.join(SITE, pg['url'].lstrip('/') + ('index.html' if pg['url'].endswith('/') else ''))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)


made = []
people = D['people']
by_lang = {}
for p in people:
    by_lang.setdefault(p['lang'], []).append(p)
for lang, ps in by_lang.items():
    pages = []
    for p in ps:
        pg = build(p, ps)
        if pg: write(pg); pages.append(pg); made.append(pg['url'])
    # hub: top people per category + one page per category (all, by age)
    L = L10N[lang]; t = T[lang]
    groups = ''
    cat_pages = []
    for cat, names in REG['cats'].items():
        rows = [pg for pg in pages if pg['cat'] == cat]
        if not rows: continue
        rows.sort(key=lambda x: -x['rank'])
        cslug = L['dir'] + slug(names['en' if lang == 'en' else lang]) + '.html'
        tbl = lambda rs: ('<div class="pp-box"><table style="width:100%;border-collapse:collapse;font-size:15px">'
                          + ''.join(f'<tr><td style="padding:7px 4px;border-bottom:1px solid #F1F5F9"><a href="{x["url"]}">{E(x["name"])}</a></td><td style="padding:7px 4px;border-bottom:1px solid #F1F5F9;text-align:right"><b>{x["age"]}</b> {L["years"]}</td></tr>' for x in rs)
                          + '</table></div>')
        more = {'es': 'Ver todos', 'pt': 'Ver todos', 'en': 'See all'}[lang]
        groups += f'<h2>{E(names[lang])} ({len(rows)})</h2>' + tbl(rows[:12]) + (f'<p style="margin:6px 2px 0"><a href="{cslug}">{more} → {E(names[lang])}</a></p>' if len(rows) > 12 else '')
        if len(rows) > 12:
            byage = sorted(rows, key=lambda x: x['age'])
            ttl = {'es': f'Edad de {names[lang].lower()} famosos', 'pt': f'Idade de {names[lang].lower()} famosos', 'en': f'Ages of famous {names[lang].lower()}'}[lang]
            cat_pages.append(dict(url=cslug, title=f'{ttl} ({TODAY.year})', desc=L['hub_lead'], h1=E(ttl), lead=E(L['hub_lead']), css=CSS['base'], lang=lang, name=names[lang],
                                  body=f'<section class="app pp" id="calc">{tbl(byage)}</section>', art=f'<p class="note">{L["src"]}: Wikidata (CC0) · {t["upd"]} {TODAY.isoformat()}.</p>'))
    hub = dict(url=L['dir'], title=f"{L['hub']} {TODAY.year}", desc=L['hub_lead'], h1=L['hub'], lead=L['hub_lead'], css=CSS['base'], lang=lang, name=L['hub'],
               body=f'<section class="app pp" id="calc">{groups}</section>', art=f'<p class="note">{L["src"]}: Wikidata (CC0) · {t["upd"]} {TODAY.isoformat()}.</p>')
    write(hub); made.append(L['dir'])
    for cp in cat_pages:
        write(cp); made.append(cp['url'])

# sitemap
sm = os.path.join(SITE, 'sitemap.xml')
if os.path.isfile(sm):
    s = open(sm, encoding='utf-8').read()
    for u in made:
        loc = B + u
        if f'<loc>{loc}</loc>' not in s:
            s = s.replace('</urlset>', f'  <url><loc>{loc}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n</urlset>', 1)
    open(sm, 'w', encoding='utf-8').write(s)
# links from country hubs
for hubp, lang in (('arg/index.html', 'es'), ('es/index.html', 'es'), ('mx/index.html', 'es'), ('br/index.html', 'pt'), ('us/index.html', 'en')):
    fp = os.path.join(SITE, hubp)
    if not os.path.isfile(fp) or lang not in by_lang: continue
    h = open(fp, encoding='utf-8').read()
    if 'id="pp-link"' in h: continue
    L = L10N[lang]
    # 돈 계산기 목록 위쪽에서 빼고, 맨 아래 작은 링크 한 줄로만 (주제가 달라 퍼널을 흐리지 않게)
    box = f'<p id="pp-link" style="margin:22px 0 6px;font-size:13px;opacity:.75"><a href="{L["dir"]}">{L["hub"]}</a></p>'
    h2 = h.replace('</main>', box + '</main>', 1) if '</main>' in h else h
    if h2 != h: open(fp, 'w', encoding='utf-8').write(h2)
print('people pages:', len(made), made)
