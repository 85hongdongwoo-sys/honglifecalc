"""Python copy of the Italian holiday logic used in /it/calcolo-giorni-tra-date.html (for worked examples)."""
import datetime as D
def easter(y):
    A=y%19;B=y//100;C=y%100;Dd=B//4;E=B%4;F=(B+8)//25;G=(B-F+1)//3;H=(19*A+B-Dd-G+15)%30;I=C//4;K=C%4
    L=(32+2*E+2*I-H-K)%7;M=(A+11*H+22*L)//451;mo=(H+L-7*M+114)//31;da=(H+L-7*M+114)%31+1
    return D.date(y,mo,da)
def hol(y):
    s={(1,1),(1,6),(4,25),(5,1),(6,2),(8,15),(11,1),(12,8),(12,25),(12,26)}
    if y>=2026: s.add((10,4))
    p=easter(y)+D.timedelta(1); s.add((p.month,p.day)); return s
def count(a,b,inc=False):
    a=D.date.fromisoformat(a); b=D.date.fromisoformat(b); d=(b-a).days; s=a if d>=0 else b; n=abs(d)+(1 if inc else 0)
    wd=fh=0
    for k in range(n):
        x=s+D.timedelta(k)
        if x.weekday()<5:
            wd+=1
            if (x.month,x.day) in hol(x.year): fh+=1
    if inc: d=d+1 if d>=0 else d-1
    return d,wd,wd-fh
