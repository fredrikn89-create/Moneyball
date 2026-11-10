import json,csv,sys,unicodedata
exec(open('squads.py').read())
D=json.load(open('/home/claude/moneyball/data/player_points.json'))
GW=D['gw']
byname={}
for pid,(nm,team,pos,pts) in D['players'].items():
    byname.setdefault(nm,[]).append((pid,team,pos,pts))
ALIAS={"Gibbs-White":"Gibbs-White","Igor Jesus":"Igor Jesus","B.Fernandes":"B.Fernandes","Van Hecke":"Van Hecke","M.Sangaré":"M.Sangaré","O.Dango":"O.Dango","Semenyo":"Semenyo","Yalcouyé":"Yalcouyé","Ødegaard":"Ødegaard"}
def norm(s): return unicodedata.normalize('NFC',s)
def find(nm):
    c=byname.get(nm)
    if not c:
        k=[x for x in byname if norm(x).lower()==norm(nm).lower()]
        c=byname.get(k[0]) if k else None
    if not c:
        # try prefix/contains
        k=[x for x in byname if nm.lower() in x.lower() or x.lower() in nm.lower()]
        c=[y for x in k for y in byname[x]]
    if not c: return None,[]
    best=max(c,key=lambda t:sum(p or 0 for p in t[3]))
    return best,c
missing=set();amb={}
P={}
allnames=set(n for s in S.values() for n in s)
for n in sorted(allnames):
    b,c=find(n)
    if not b: missing.add(n);continue
    if len(c)>1: amb[n]=[(x[1],x[2],sum(p or 0 for p in x[3])) for x in c]
    P[n]=b
print('MISSING',sorted(missing));print('AMBIG',amb)
json.dump({n:[b[1],b[2],b[3]] for n,b in P.items()},open('resolved.json','w'),ensure_ascii=False)

for n,pos in (('Bentley','GK'),('Dubravka','GK'),('Matthews','GK'),('Kusi-Asare','FWD')): P[n]=(0,'-',pos,[0]*GW)
def pts(n,r):
    v=P[n][3][r-1]; return v or 0
chips={}
for r in csv.DictReader(open('/tmp/claude-0/-home-claude/9e1bf317-ff7b-51ff-aed1-a5ab17bc28d1/scratchpad/dash/fpl_gameweeks_v8.csv')):
    chips[(r['lag'],int(r['gw']))]=(r['chip'],int(r['hits']))
TEAMS=['Henrik','Eirik','Bauge','Waag','Næss','Cedric','Hakki','Marius','Morten']
res={}
detail={}
for t in TEAMS:
    imm_tot=hold_tot=0;imm_nwc=hold_nwc=0;hits=0;rows=[]
    fh=[g for g in range(1,GW+1) if chips[(t,g)][0]=='Free Hit']
    def sqd(g):
        while g in fh: g-=1
        return S[(t,g)]
    for g in range(2,GW+1):
        if g in fh: continue
        prev=sqd(g-1);cur=sqd(g)
        out=sorted(prev-cur);inn=sorted(cur-prev)
        if not out: continue
        wc=chips[(t,g)][0]=='Wildcard'
        h=chips[(t,g)][1]; hits+=0 if wc else h
        # pair by position
        pr=[];oo=out[:]
        for y in inn:
            m=[x for x in oo if P[x][2]==P[y][2]] or oo
            x=m[0];oo.remove(x);pr.append((x,y))
        pr=[(x,y) for x,y in pr if P[y][2]!='GK' and P[x][2]!='GK']
        imm=sum(pts(y,g)-pts(x,g) for x,y in pr)
        hold=0;items=[]
        for x,y in pr:
            e=g
            while e+1<=GW and (e+1 in fh or y in S[(t,e+1)]): e+=1
            rr=[r for r in range(g,e+1) if r not in fh]
            d=sum(pts(y,r)-pts(x,r) for r in rr)
            hold+=d;items.append((x,y,g,e,d))
        rows.append((g,wc,h,imm,hold,items))
        imm_tot+=imm;hold_tot+=hold
        if not wc: imm_nwc+=imm;hold_nwc+=hold
    res[t]=(imm_tot,hold_tot,imm_nwc,hold_nwc,hits,rows)
for t in TEAMS:
    imm,hold,immn,holdn,hits,rows=res[t]
    print(f"\n{t}: umiddelbar {imm:+d} (uten WC {immn:+d}) | holdt-periode {hold:+d} (uten WC {holdn:+d}) | hits -{hits}")
    for g,wc,h,i,ho,items in rows:
        print(f"  R{g}{' WC' if wc else ''} hit{h}: runden {i:+d}, holdt {ho:+d}  "+'; '.join(f"{x}->{y} (R{g}-R{e}: {d:+d})" for x,y,g_,e,d in items))
