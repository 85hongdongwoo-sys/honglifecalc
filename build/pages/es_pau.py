import sys; sys.path.insert(0,'/home/claude/honglifecalc/build')
from enrich_lib import build, table, faq_html
P='/es/calculadora-nota-pau.html'
def e(x): return f'{x:.3f}'.replace('.',',')
def ex(nmb,cfg,m1,a1,m2,a2):
    acc=.6*nmb+.4*cfg
    if cfg<4 or acc<5: return [str(nmb).replace('.',','),str(cfg).replace('.',','),f'{m1} × {a1} · {m2} × {a2}'.replace('.',','),'—','No aprobada (prueba < 4)']
    p=sorted([m*a for m,a in ((m1,a1),(m2,a2)) if m>=5],reverse=True)[:2]
    return [str(nmb).replace('.',','),str(cfg).replace('.',','),f'{m1} × {a1} · {m2} × {a2}'.replace('.',','),e(acc),e(min(14,acc+sum(p)))]
rows=[ex(8.2,7.1,8,0.2,7.5,0.2),ex(6,5,0,0.2,0,0.2),ex(8,7,4.5,0.2,8,0.1),ex(9.5,9,9.5,0.2,9,0.2),ex(10,10,10,0.2,10,0.2),ex(7,3.8,6,0.2,6,0.2)]
rows[1][2]='sin ponderaciones'
FAQ=[
("¿Cómo se calcula la nota de acceso de la PAU?","Nota de acceso = 0,6 × media de Bachillerato + 0,4 × calificación de la prueba de acceso. Con un 8,2 en Bachillerato y un 7,1 en la prueba: 4,92 + 2,84 = 7,76. Para aprobar necesitas al menos un 4 en la prueba y un 5 en la nota de acceso."),
("¿Cuál es la nota máxima de la PAU?","14 puntos: hasta 10 de la nota de acceso y hasta 4 de las dos mejores materias ponderadas (2 × 10 × 0,2)."),
("¿Qué materias ponderan?","Cada universidad publica al inicio del curso los parámetros de ponderación (0,1 o 0,2) de cada materia para cada grado. Pueden ponderar las materias de la prueba de acceso —incluida la de modalidad— y las de la fase voluntaria, siempre que tengas al menos un 5 en ellas. Se cogen las dos que más te suben la nota."),
("¿Cuántos años vale la nota de la PAU?","La nota de acceso no caduca. Las calificaciones de las materias para la admisión (fase voluntaria) valen para el curso siguiente a la prueba y los dos cursos académicos posteriores, según el Real Decreto 534/2024."),
("¿Cuándo es la PAU 2027?","En Andalucía, la convocatoria ordinaria será el 1, 2 y 3 de junio de 2027 y la extraordinaria el 29 y 30 de junio y 1 de julio (BOJA de 16/11/2026). En Aragón, las mismas fechas. Otras comunidades publican su calendario a lo largo del curso."),
]
art='''<h2>Cómo se calculan la nota de acceso y la de admisión</h2>
<p><b>Nota de acceso = 0,6 × NMB + 0,4 × CPA</b>, donde NMB es la nota media de Bachillerato (sin Religión) y CPA la calificación de la prueba de acceso. La CPA solo cuenta si es <b>igual o superior a 4</b>, y la nota de acceso debe ser <b>al menos 5</b> (arts. 14 y 15 del Real Decreto 534/2024). Esta nota sirve para siempre.</p>
<p><b>Nota de admisión = nota de acceso + a × M1 + b × M2</b>, donde M1 y M2 son las dos materias aprobadas (5 o más) que más suben la nota en el grado que pides, y a y b sus parámetros de ponderación (0,1 o 0,2), que fija cada universidad. El máximo es 14.</p>
<h3>Ejemplos</h3>
'''+table(['Bachillerato','Prueba de acceso','Materias × ponderación','Nota de acceso','Nota de admisión'],rows)+'''
<p class="note">Calculado con la fórmula de esta página. En el tercer ejemplo la materia con 4,5 no pondera porque no llega a 5.</p>
<h3>Datos clave</h3>
'''+table(['Concepto','Regla'],[
['Peso de Bachillerato / prueba','60 % / 40 %'],
['Mínimo en la prueba de acceso','4'],
['Nota de acceso para aprobar','5'],
['Ponderaciones','0,1 o 0,2 por materia, las dos mejores'],
['Nota máxima de admisión','14'],
['Validez de la nota de acceso','indefinida'],
['Validez de las materias para admisión','el curso siguiente y los dos posteriores'],
])+'''
<h3>Calendario</h3>
'''+table(['Comunidad','PAU 2026 (ordinaria)','PAU 2027 (ordinaria / extraordinaria)'],[
['Andalucía','2, 3 y 4 de junio','1, 2 y 3 de junio / 29 y 30 de junio y 1 de julio de 2027'],
['Aragón','—','1, 2 y 3 de junio / 29 y 30 de junio y 1 de julio de 2027'],
['Madrid','1, 2, 3 y 4 de junio','pendiente de publicación'],
['Cataluña','9, 10 y 11 de junio','pendiente de publicación oficial'],
])+'''
<h3>Consejos</h3>
<ul><li><b>Mira las ponderaciones de cada universidad</b>: la misma materia puede ponderar 0,2 en una universidad y 0,1 en otra para el mismo grado, y algunas comunidades las cambian de un año a otro (Andalucía aprobó nuevos parámetros para 2026-2027 y siguientes).</li>
<li><b>La materia de modalidad también pondera</b>: no hace falta repetirla en la fase voluntaria si ya tienes un 5 o más.</li>
<li><b>Compara con la nota de corte</b> del grado del año anterior, que está en la misma escala sobre 14.</li>
<li><b>La media de Bachillerato pesa más</b> (60 %): cada punto de Bachillerato vale 0,6 en la nota de acceso; cada punto en la prueba, 0,4.</li></ul>
'''+faq_html(FAQ,'Preguntas frecuentes')+'''
<p class="note">Fuentes (consulta 21/11/2026): <a href="https://www.boe.es/eli/es/rd/2024/06/11/534" rel="nofollow">BOE — Real Decreto 534/2024</a>; <a href="https://uah.es/export/sites/uah/es/admision-y-ayudas/.galleries/Descargas-Acceso/Que_debo_saber_de_la_PAU.pdf" rel="nofollow">Universidad de Alcalá — Qué debo saber de la PAU</a>; <a href="https://juntadeandalucia.es/boja/2026/221/43" rel="nofollow">BOJA nº 221 de 16/11/2026 — calendario PAU 2027 Andalucía</a>; <a href="https://academico.unizar.es/sites/academico/files/archivos/acceso/accescomis/reuni/20260513fecha.pdf" rel="nofollow">Universidad de Zaragoza — fechas PAU 2027</a>; <a href="https://www.comunidad.madrid/node/76133" rel="nofollow">Comunidad de Madrid — PAU 2026</a>; <a href="https://www.gencat.cat/recercaiuniversitats/accesuniversitat/centres/PAU_2026_horari.pdf" rel="nofollow">Generalitat de Catalunya — horario PAU 2026</a>; <a href="https://www.upo.es/estudiantes/es/antes-del-grado/pruebas-de-acceso/Fechas-PAU-y-Procedimientos-Clave/" rel="nofollow">Universidad Pablo de Olavide — fechas PAU 2026</a>. Cálculo orientativo.</p>'''
print(build(P,'Calculadora nota PAU 2027 – nota de acceso y de admisión (sobre 14)',
 'Calcula tu nota de acceso (0,6 × Bachillerato + 0,4 × prueba) y de admisión sobre 14 con las ponderaciones 0,1 o 0,2. Reglas del RD 534/2024, ejemplos y fechas PAU 2027.',art,FAQ))
