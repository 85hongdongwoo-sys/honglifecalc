import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, add_top
P='/br/calculadora-consumo-energia.html'
TAR=0.90  # tarifa de EXEMPLO (não oficial)
AM,V1,V2=0.01885,0.04463,0.07877  # ANEEL, R$/kWh

def r2(x): return f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
def n(x,d=1):
    s=f'{x:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
    return s.rstrip('0').rstrip(',') if ',' in s else s
def mf(x): return 'R$ '+(r2(x) if abs(x)<100 else f'{round(x):,}'.replace(',','.'))

def ex(name,w,h,mn,uso):
    kd=w/1000*(h+mn/60);k=kd*30;m=k*TAR
    return [name,uso,n(kd,2)+' kWh',n(k,1)+' kWh','R$ '+r2(m),mf(m*365/30)],(k,m)

E=[ex('Chuveiro elétrico 5.500 W',5500,0,30,'30 min por dia (família)'),
   ex('Chuveiro elétrico 7.500 W',7500,0,30,'30 min por dia'),
   ex('Ar-condicionado 1.000 W',1000,8,0,'8 h por dia, potência máxima'),
   ex('Ferro de passar 1.200 W',1200,0,20,'20 min por dia'),
   ex('Secador de cabelo 1.900 W',1900,0,10,'10 min por dia'),
   ex('TV 100 W',100,5,0,'5 h por dia')]
rows=[e[0] for e in E]
k0,m0=E[0][1]

form='''<form class="card" id="form" onsubmit="return false"><h2>Seu aparelho</h2>
<label class="f"><span>Potência (W)</span><input id="w" inputmode="decimal" value="5.500"><small>Vem na etiqueta ou no manual. 1 kW = 1.000 W.</small></label>
<label class="f"><span>Horas de uso por dia</span><input id="h" inputmode="decimal" value="0"></label>
<label class="f"><span>Mais minutos por dia</span><input id="mn" inputmode="decimal" value="30"><small>Bom para chuveiro, secador e ferro (30 min = 0,5 h).</small></label>
<label class="f"><span>Tarifa do kWh (R$)</span><input id="kp" inputmode="decimal" value="0,90"><small>R$ 0,90 é só um exemplo. Use o valor do kWh com impostos (ICMS, PIS/COFINS) da sua conta de luz.</small></label>
<label class="f"><span>Dias</span><input id="d" inputmode="decimal" value="30"></label></form>'''

calc='''function calc(){const pv=id=>{const v=String($(id).value).trim();return /^0[.,]\\d+$/.test(v)?parseFloat(v.replace(',','.')):num(id)};const kw=num('w')/1000,hd=num('h')+num('mn')/60,d=Math.max(1,num('d')),p=pv('kp'),k=kw*hd*d,m=k*p;
 return big('Custo em '+nn(d,0)+' dias',mf2(m),nn(k,1)+' kWh')+kv([['Por dia',mf2(m/d)+' ('+nn(kw*hd,2)+' kWh)'],['Por hora de uso',mf2(kw*p)],['Por mês (30 dias)',mf2(m*30/d)],[O.y,mf(m*365/d)],['Tempo de uso por dia',nn(hd,2)+' h'],['Extra na bandeira amarela',mf2(k*0.01885)],['Extra na bandeira vermelha 2',mf2(k*0.07877)]])+'<p class="note">Só o gasto do aparelho. Taxas fixas da conta (como a iluminação pública) não entram. Extras das bandeiras: valores da ANEEL por kWh.</p>'}'''

FAQ=[
("Quanto gasta um chuveiro elétrico por mês?","Um chuveiro de 5.500 W ligado 30 minutos por dia gasta 2,75 kWh por dia e "+n(k0,1)+" kWh em 30 dias. Com tarifa de R$ 0,90 por kWh, são R$ "+r2(m0)+" por mês. Na posição verão (menos potência) o gasto cai."),
("Quanto consome um ar-condicionado?","Multiplique a potência pelas horas. Um aparelho de 1.000 W ligado 8 horas gasta até 8 kWh por dia e 240 kWh por mês: até R$ 216 com tarifa de R$ 0,90. Modelos inverter desaceleram o motor quando o quarto esfria, então o gasto real costuma ser menor."),
("Como calcular o consumo de energia de um aparelho?","kWh = potência em watts ÷ 1.000 × horas de uso. Depois, custo = kWh × tarifa. Um ferro de 1.200 W usado 20 minutos por dia gasta 0,4 kWh por dia, 12 kWh por mês, ou R$ 10,80 a R$ 0,90 o kWh."),
("Qual é a bandeira tarifária de novembro e dezembro de 2026?","Em novembro de 2026 a bandeira é verde, sem cobrança extra (anúncio da ANEEL de 30/10/2026). A bandeira de dezembro sai em 27/11/2026, pelo calendário da ANEEL; até lá ainda não foi definida."),
("Quanto a bandeira vermelha aumenta a conta?","Pelos valores da ANEEL: amarela soma R$ 1,885 a cada 100 kWh, vermelha patamar 1 soma R$ 4,463 e vermelha patamar 2 soma R$ 7,877. Uma casa que gasta 200 kWh paga R$ 15,75 a mais na vermelha 2."),
("Quanto gasta uma geladeira por mês?","A geladeira liga e desliga o motor o dia todo, então a potência não ajuda muito. Use o consumo em kWh/mês da etiqueta do Inmetro (Ence) e multiplique pela sua tarifa."),
("Quem tem direito à Tarifa Social de energia?","Famílias do CadÚnico com renda por pessoa de até meio salário mínimo, quem recebe o BPC e famílias com até 3 salários mínimos que usam aparelho médico elétrico. Elas não pagam os primeiros 80 kWh do mês; só o que passar disso é cobrado. O benefício é automático, com o CadÚnico atualizado.")]

art='''<h2 id="figures" style="margin-top:4px">Números oficiais da conta de luz em 2026</h2>
'''+table(['Item','Valor','O que significa'],[
['Bandeira de novembro de 2026','Verde','Sem cobrança extra no mês.'],
['Bandeira de dezembro de 2026','Anúncio em 27/11/2026','Ainda não definida em 23/11/2026.'],
['Bandeira amarela','+ R$ 1,885 a cada 100 kWh','R$ 0,01885 por kWh.'],
['Bandeira vermelha – patamar 1','+ R$ 4,463 a cada 100 kWh','R$ 0,04463 por kWh.'],
['Bandeira vermelha – patamar 2','+ R$ 7,877 a cada 100 kWh','R$ 0,07877 por kWh.'],
['Tarifa Social (Luz do Povo)','0 a 80 kWh por mês grátis','Para famílias de baixa renda no CadÚnico e quem recebe BPC.'],
['Desconto Social','Isenção da CDE até 120 kWh por mês','CadÚnico com renda por pessoa entre meio e 1 salário mínimo.']])+'''
<p class="note"><b>Bandeira tarifária</b> é uma cor que a ANEEL define todo mês. Ela mostra se gerar energia ficou mais caro (por exemplo, quando falta chuva para as hidrelétricas). <b>CDE</b> é um encargo cobrado na conta para pagar políticas do setor elétrico. A tarifa do kWh muda de uma distribuidora para outra, por isso a calculadora usa R$ 0,90 só como exemplo.</p>
<h2 id="ex">Exemplos: quanto gasta cada aparelho</h2>
<p>Um chuveiro de 5.500 W ligado meia hora por dia gasta 2,75 kWh. Em 30 dias são '''+n(k0,1)+''' kWh. Com tarifa de R$ 0,90, a conta sobe R$ '''+r2(m0)+''' por mês. Veja outros aparelhos (30 dias, tarifa de exemplo de R$ 0,90 por kWh):</p>
<div id="examples">'''+table(['Aparelho','Uso','kWh por dia','kWh em 30 dias','Custo em 30 dias','Custo por ano'],rows)+'''</div>
<ul><li>O chuveiro de 7.500 W gasta mais que o de 5.500 W no mesmo tempo: R$ '''+r2(E[1][1][1])+''' contra R$ '''+r2(m0)+''' por mês.</li>
<li>O ar-condicionado aparece com potência máxima. Com motor inverter e quarto já frio, o gasto real fica menor.</li>
<li>Se a bandeira for vermelha patamar 2, o chuveiro de 5.500 W custa mais R$ '''+r2(k0*V2)+''' no mês ('''+n(k0,1)+''' kWh × R$ 0,07877).</li></ul>
<p class="note">Calculado com a fórmula desta página. As potências são exemplos comuns: confira a etiqueta do seu aparelho.</p>
<h2 id="how">Como funciona o cálculo</h2>
<p>A conta de luz cobra <b>kWh</b> (quilowatt-hora). Um kWh é a energia de um aparelho de 1.000 W ligado por uma hora.</p>
<ul><li><b>kWh por dia</b> = potência (W) ÷ 1.000 × horas por dia</li>
<li><b>kWh no período</b> = kWh por dia × dias</li>
<li><b>Custo</b> = kWh × tarifa (R$ por kWh)</li></ul>
<p>Os minutos viram horas: 30 minutos são 0,5 hora, 10 minutos são cerca de 0,17 hora. O custo por ano é o custo do período × 365 ÷ dias.</p>
<h3>Onde achar a tarifa certa</h3>
<p>Pegue a conta de luz. Divida o valor da energia consumida (com impostos) pelo total de kWh do mês. <b>ICMS</b> é o imposto estadual e <b>PIS/COFINS</b> são tributos federais; eles mudam de estado para estado e de mês a mês, por isso a tarifa com impostos é maior que a tarifa publicada pela ANEEL.</p>
<h3>Aparelhos que ligam e desligam</h3>
<p>Geladeira, freezer e ar-condicionado inverter não ficam na potência máxima o tempo todo. Para a geladeira, use o consumo em kWh/mês da etiqueta do Inmetro (Ence) e multiplique pela tarifa.</p>
<h2 id="tips">Dicas e erros comuns</h2>
<ul><li><b>Comece pelos aparelhos que esquentam</b>: chuveiro, ar-condicionado, ferro, secador e forno elétrico gastam muito mais que lâmpadas LED e carregadores.</li>
<li><b>Banho mais curto</b>: cada 5 minutos a menos em um chuveiro de 5.500 W economiza cerca de 0,46 kWh por banho.</li>
<li><b>Posição verão</b> no chuveiro usa menos potência que a posição inverno.</li>
<li><b>Junte roupas para passar</b>: o ferro gasta mais para esquentar de novo várias vezes.</li></ul>
<h3>Erros comuns</h3>
<ul><li>Confundir W com kWh: 1.000 W só viram 1 kWh se ficarem ligados uma hora inteira.</li>
<li>Usar a tarifa sem impostos: o valor fica mais baixo que o da conta.</li>
<li>Esquecer a bandeira: em bandeira vermelha cada kWh fica mais caro.</li>
<li>Somar a iluminação pública ao aparelho: ela é cobrada na conta de qualquer jeito.</li></ul>
<h2 id="faq" style="margin-top:22px">Perguntas frequentes</h2>'''+''.join(f'<h3>{q}</h3><p>{a}</p>' for q,a in FAQ)+'''
<p class="note">Fontes (consultadas em 23/11/2026): <a href="https://www.gov.br/aneel/pt-br/assuntos/tarifas/bandeiras-tarifarias" rel="nofollow">ANEEL – Bandeiras tarifárias</a>; <a href="https://www.gov.br/aneel/pt-br/assuntos/noticias/2026/aneel-anuncia-bandeira-verde-para-vigorar-em-novembro" rel="nofollow">ANEEL – Bandeira verde em novembro</a>; <a href="https://www.gov.br/aneel/pt-br/assuntos/noticias/2026/bandeira-tarifaria-aneel-divulga-calendario-de-acionamento-para-2026" rel="nofollow">ANEEL – Calendário das bandeiras 2026</a>; <a href="https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social" rel="nofollow">ANEEL – Tarifa Social</a>; <a href="https://www.gov.br/mme/pt-br/luzdopovo" rel="nofollow">MME – Luz do Povo</a>. Exemplos calculados com a fórmula desta página.</p>'''

if __name__=='__main__':
    out=build(P,'Calculadora de consumo de energia 2026 – Quanto gasta cada aparelho',
     'Calcule o consumo em kWh e o custo em reais de chuveiro, ar-condicionado e outros aparelhos. Bandeiras tarifárias da ANEEL e Tarifa Social em 2026.',art,FAQ,form=form,calc=calc)
    add_top(out,[('Por','Hong Life Calculators'),('Verificado em','23 de novembro de 2026'),('Fontes','ANEEL, MME')],
      [('form','Calculadora'),('figures','Números oficiais 2026'),('ex','Exemplos por aparelho'),('how','Como funciona o cálculo'),('tips','Dicas e erros comuns'),('faq','Perguntas frequentes')],'Nesta página')
    print(out)
    for r in rows: print(r)
