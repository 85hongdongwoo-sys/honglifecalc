import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
P='/br/calculadora-nota-enem-sisu.html'
FAQ=[
("Como calcular a média ponderada do Sisu?","Multiplique cada nota do Enem pelo peso que o curso dá àquela prova, some os resultados e divida pela soma dos pesos. Ex.: notas 640, 650, 600, 700 e 820 com pesos 1, 1, 2, 3 e 2 dão 6.230 ÷ 9 = 692,22."),
("Quando sai a nota do Enem 2026?","O Inep informou que os resultados do Enem 2026 serão divulgados em 18 de janeiro de 2027. As provas foram aplicadas em 8 e 15 de novembro de 2026."),
("Quais edições do Enem valem para o Sisu?","No Sisu 2026 valeram as notas do Enem 2023, 2024 ou 2025, e o sistema usou a edição com a melhor média para cada curso. Não valem edições feitas como treineiro nem edições com nota zero na redação. As regras do Sisu 2027 saem no edital do MEC."),
("Quem tira zero na redação pode usar o Sisu?","Não com aquela edição: o edital exige nota da redação superior a zero. Se você tem outra edição válida com redação acima de zero, ela pode ser usada."),
("Onde vejo os pesos e a nota mínima do meu curso?","Na página do curso no portal do Sisu, durante as inscrições, e no termo de adesão da instituição. Cada instituição define os pesos e as notas mínimas de cada prova."),
("Como funciona o desempate no Sisu?","Em caso de empate na média, o edital do Sisu 2026 considera, nesta ordem, a nota da redação, Linguagens, Matemática, Ciências da Natureza e Ciências Humanas."),
]
art='''<h2>Como a nota do Sisu é calculada</h2>
<p><b>Média ponderada = (L × pL + CH × pCH + CN × pCN + M × pM + R × pR) ÷ (pL + pCH + pCN + pM + pR)</b>, em que L, CH, CN, M e R são suas notas no Enem (Linguagens, Ciências Humanas, Ciências da Natureza, Matemática e Redação) e p são os pesos do curso. Com todos os pesos iguais a 1, a média ponderada é igual à média simples. A calculadora mostra as duas.</p>
<h3>Exemplos</h3>
'''+table(['Notas (L / CH / CN / M / R)','Pesos (L / CH / CN / M / R)','Média ponderada','Média simples'],[
['600 / 620 / 580 / 650 / 800','1 / 1 / 1 / 1 / 1','650,00','650,00'],
['640 / 650 / 600 / 700 / 820 (padrão)','1 / 1 / 2 / 3 / 2','692,22','682,00'],
['650 / 640 / 700 / 720 / 880','1 / 1 / 3 / 2 / 3','747,00','718,00'],
['680 / 690 / 580 / 600 / 900','3 / 3 / 1 / 1 / 3','726,36','690,00'],
['600 / 610 / 650 / 780 / 760','1 / 1 / 2 / 4 / 2','715,00','680,00'],
])+'''
<p class="note">Calculado com a fórmula desta página. Pesos de exemplo: confira os pesos reais do seu curso no Sisu. Repare que a mesma pessoa pode ter médias bem diferentes em cursos com pesos diferentes.</p>
<h3>Datas e números oficiais</h3>
'''+table(['Item','Informação'],[
['Provas do Enem 2026','8 e 15 de novembro de 2026 (reaplicação em 15 e 16 de dezembro)'],
['Inscrições confirmadas no Enem 2026','5.051.345 (Painel Enem, 23/10/2026)'],
['Resultado do Enem 2026','18 de janeiro de 2027'],
['Sisu 2026 (referência)','inscrições de 19 a 23/1/2026; chamada regular única em 29/1/2026; edição única no ano'],
['Edições aceitas no Sisu 2026','Enem 2023, 2024 ou 2025 (vale a de melhor média)'],
['Redação','5 competências de 0 a 200 pontos, máximo 1.000; nota final = média de dois avaliadores'],
])+'''
<p class="note">O cronograma do Sisu 2027 ainda não tinha sido publicado pelo MEC em 21/11/2026.</p>
<h3>Dicas</h3>
<ul><li><b>Simule vários cursos</b>: troque só os pesos para ver em qual curso suas notas rendem mais.</li>
<li><b>Confira a nota mínima</b>: algumas instituições exigem nota mínima em provas específicas ou na média; abaixo dela a inscrição não é aceita naquele curso.</li>
<li><b>Nota de corte não é fixa</b>: ela muda a cada dia de inscrição conforme os candidatos se inscrevem; use a média ponderada para comparar com a nota de corte parcial.</li>
<li><b>Modalidade de concorrência</b>: cotas e ações afirmativas têm notas de corte próprias.</li>
<li><b>Bônus regionais</b>: algumas instituições aplicam bônus sobre a média; ele não está incluído neste cálculo.</li></ul>
'''+faq_html(FAQ,'Perguntas frequentes')+'''
<p class="note">Fontes (consulta em 21/11/2026): <a href="https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/resultados-do-enem-serao-divulgados-em-18-de-janeiro" rel="nofollow">Inep — resultados do Enem 2026 em 18 de janeiro</a>; <a href="https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/painel-enem-2026-apresenta-perfil-dos-participantes-do-exame" rel="nofollow">Inep — Painel Enem 2026</a>; <a href="https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/enem-2026-cartilha-da-redacao-esta-disponivel" rel="nofollow">Inep — Cartilha da Redação 2026</a>; Edital SESu/MEC nº 29, de 22 de dezembro de 2025 (Sisu 2026); <a href="https://agenciagov.ebc.com.br/noticias/202601/inscricoes-no-sisu-2026-comecam-segunda-19" rel="nofollow">Agência Gov — inscrições no Sisu 2026</a>; Portaria Normativa MEC nº 21/2012 (pesos e notas mínimas definidos pelas instituições). Cálculo orientativo.</p>'''
print(build(P,'Calculadora Sisu 2027 – média ponderada do Enem com os pesos do curso',
 'Calcule sua média ponderada do Enem para o Sisu com os pesos do seu curso. Fórmula, exemplos, data do resultado do Enem 2026 (18/1/2027) e regras do Sisu.',art,FAQ))
