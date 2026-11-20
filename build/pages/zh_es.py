import sys,re; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html, ORIG, OUT
def setdef(path,vals):
    s=open(ORIG+path,encoding='utf-8').read()
    f=re.search(r'<form class="card" id="form".*?</form>',s,re.S).group(0)
    for k,v in vals.items(): f=re.sub(r'(<input id="%s"[^>]*value=")[^"]*'%k,lambda m:m.group(1)+v,f)
    return f
FAQ=[
("每月存多少钱才能达到目标？","每月存款 = (目标金额 − 已有存款 × (1+i)<sup>n</sup>) × i ÷ ((1+i)<sup>n</sup> − 1)，其中 i 为月利率（年利率 ÷ 12），n 为月数。按默认值（目标 14 万元、已有 1.4 万元、3 年、年利率 1.25%），每月约需存 3,422 元。"),
("3年存10万元每月要存多少？","不计利息每月约 2,778 元；按年利率 1.25%、按月复利计算，每月约 2,727 元，3 年共存入约 98,189 元，利息约 1,811 元。"),
("现在银行定期存款利率是多少？","据 2026 年 6 月的汇总，工商、建设、农业、中国银行四大行整存整取一年期 0.95%、两年期 1.05%、三年期 1.25%、五年期 1.30%，活期 0.05%。利率会调整，请以银行公布为准。"),
("利率低的时候存钱目标怎么调整？","利率越低，利息贡献越小，主要靠本金。可以延长期限、提高每月存款，或在了解风险的前提下考虑国债、大额存单等产品。"),
("这个计算是按月复利吗？","是的。计算假设每月月末存入、按月复利，已有存款的利息也计入。银行定期存款通常按存期单利计息，实际利息会略有差别。")]
rows=[['14 万元','1.4 万元','3 年','1.25%','3,422 元','约 2,807 元'],['10 万元','0','3 年','1.25%','2,727 元','约 1,811 元'],['10 万元','0','5 年','1.30%','1,614 元','约 3,161 元'],['30 万元','5 万元','5 年','1.30%','3,981 元','约 11,152 元'],['5 万元','0','1 年','0.95%','4,149 元','约 217 元']]
art='''<h2>每月存款的计算方法</h2>
<p>先算出已有存款到期时会增长到多少，剩下的差额由每月存款补足。每月存入的钱从存入起按月复利计息。</p>
<p><b>每月存款 = (目标 − 已有 × (1+i)<sup>n</sup>) × i ÷ ((1+i)<sup>n</sup> − 1)</b>，i = 年利率 ÷ 12，n = 年数 × 12。年利率为 0 时，每月存款 = (目标 − 已有) ÷ 月数。</p>
<h3>计算示例</h3>
'''+table(['目标金额','已有存款','期限','年利率','每月需存','利息约'],rows)+'''
<h3>四大行人民币存款挂牌利率（2026 年 6 月）</h3>
'''+table(['存款类型','年利率'],[['活期','0.05%'],['整存整取 一年','0.95%'],['整存整取 两年','1.05%'],['整存整取 三年','1.25%'],['整存整取 五年','1.30%']])+'''
<p class="note">工商银行、建设银行、农业银行、中国银行挂牌利率相同。利率随时可能调整，股份制银行和地方银行通常略高，请以银行官网为准。</p>
<h3>存钱小建议</h3>
<ul><li>工资到账后先存后花，设置自动转存。</li><li>把目标拆成每月金额，更容易坚持。</li><li>存款保险：同一银行每位存款人最高偿付 50 万元（本金和利息合并计算）。</li><li>利率较低时，利息占比很小，提高存款额比追求利率更有效。</li></ul>
'''+faq_html(FAQ,'常见问题')+'''
<p class="note">资料来源（2026 年 11 月 20 日核对）：四大行存款挂牌利率汇总（2026 年 6 月）；《存款保险条例》（最高偿付限额 50 万元）。计算结果仅供参考。</p>'''
print(build('/zh/savings-goal-calculator.html','存钱目标计算器 2026 – 每月要存多少钱？（含利息·按月复利）',
 '输入目标金额、已有存款、年数和年利率，算出每月需要存多少钱。附计算公式、示例表和 2026 年四大行定期存款利率。',art,FAQ,form=setdef('/zh/savings-goal-calculator.html',{'r':'1.25'})))
# ---------- Spain pensions: light update (status of IPC data) ----------
p='/es/pensiones/subida-pensiones-2027.html'
s=open(ORIG+p,encoding='utf-8').read()
s=s.replace("'oct*'","'oct'")
s=s.replace('sumando el avance de octubre (4,9 %) sube al 3,47 %','sumando el dato definitivo de octubre (4,9 %, publicado por el INE el 13 de noviembre) sube al 3,47 %')
s=s.replace('<h3>Pensión máxima y mínimas</h3>','<h3>Cuánto sube tu pensión (14 pagas)</h3>'+table(['Pensión 2026','Con +3,5 %','Con +3,6 %','Más al año (3,6 %)'],[[f'{x:,}'.replace(',','.')+' €',f'{x*1.035:,.2f}'.replace(',','X').replace('.',',').replace('X','.')+' €',f'{x*1.036:,.2f}'.replace(',','X').replace('.',',').replace('X','.')+' €',f'{x*0.036*14:,.2f}'.replace(',','X').replace('.',',').replace('X','.')+' €'] for x in (800,1000,1200,1400,1600,2000,2500)])+'<h3>Pensión máxima y mínimas</h3>',1)
s=s.replace('<article class="card help">','<article class="card help">'+__import__('enrich_lib').TBL_CSS,1)
s=s.replace('Fuentes: INE (IPC mensual)','Fuentes: INE (IPC mensual; octubre 2026 definitivo, 13/11/2026)')
import os; out=OUT+p; os.makedirs(os.path.dirname(out),exist_ok=True); open(out,'w',encoding='utf-8').write(s); print(out)
# IPC table -> wrapping grid (no horizontal scroll on mobile)
s=open(out,encoding='utf-8').read()
old=s[s.find("s+='<div class=\"scroll\">"):s.find("  return s}")]
new="""s+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:6px;margin-top:10px">'+M.map((m,k)=>'<div style="border:1px solid var(--line);border-radius:8px;padding:6px 8px;text-align:center;font-size:13px"><div style="color:var(--muted);font-size:12px">'+m+'</div><b>'+IPC[k].toFixed(1).replace('.',',')+' %</b></div>').join('')+'<div style="border:1px dashed var(--line);border-radius:8px;padding:6px 8px;text-align:center;font-size:13px"><div style="color:var(--muted);font-size:12px">nov ?</div><b>'+nov.toFixed(1).replace('.',',')+' %</b></div></div>';
  s+='<p class="note">Media de los 12 meses: '+avg.toFixed(2).replace('.',',')+' %. Octubre es el dato definitivo del INE (13 de noviembre de 2026); noviembre es el supuesto que introduces.</p>';
"""
if old: s=s.replace(old,new,1)
open(out,'w',encoding='utf-8').write(s)
