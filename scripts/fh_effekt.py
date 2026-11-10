import json
exec(open('analyse.py').read().split("print('MISSING'")[0])
for n,pos in (('Bentley','GK'),('Dubravka','GK'),('Matthews','GK'),('Kusi-Asare','FWD')): P[n]=(0,'-',pos,[0]*GW)
R=9
def p(n): return (P[n][3][R-1] or 0)
def run(xi,bench,cap):
    pos={n:P[n][2] for n in xi+bench}
    xi=xi[:];bench=bench[:]
    # auto-subs: 0 pts players replaced
    def valid(x):
        d=sum(pos[n]=='DEF' for n in x);m=sum(pos[n]=='MID' for n in x);f=sum(pos[n]=='FWD' for n in x);g=sum(pos[n]=='GK' for n in x)
        return g==1 and d>=3 and f>=1
    for n in xi[:]:
        if p(n)==0:
            for b in bench:
                if pos[b]=='GK' and pos[n]!='GK': continue
                if pos[n]=='GK' and pos[b]!='GK': continue
                if p(b)==0: continue
                t=[b if x==n else x for x in xi]
                if valid(t): xi=t;bench.remove(b);break
    tot=sum(p(n) for n in xi)+p(cap)  # captain doubled
    return tot,xi,bench
cfg={
'Henrik':(["Raya","Calafiori","De Cuyper","Konsa","Hall","Palmer","Groß","Rogers","Belloumi","Haaland","Calvert-Lewin"],["Bentley","João Pedro","Gvardiol","Cherki"],'Haaland',74),
'Næss':(["Verbruggen","Calafiori","Gvardiol","De Cuyper","Ajer","Rogers","Gibbs-White","Groß","Ødegaard","Haaland","Gonzalo"],["Kinsky","João Pedro","Davis","Manzambi"],'Haaland',67),
}
out={}
for t,(xi,b,c,fh) in cfg.items():
    tot,x2,b2=run(xi,b,c)
    print(t,'beholdt lag R9:',tot,'FH:',fh,'diff',fh-tot,'| xi pts',[(n,p(n)) for n in xi],'bench',[(n,p(n)) for n in b])
    out[t]={'fh':fh,'keep':tot}
print(json.dumps(out))
