# Opus audit script 4 (verbatim). The ACTUAL GIF seed: gauge-transform it into the
# tree slice, BFS with order-2 moves, then quotient by TRUE global conjugation.
# Result: raw 64 states -> exactly 6 physical classes, sizes [4,12,12,12,12,12].
# The frozen tetra GIF explored precisely those 6 classes and nothing else.
import itertools, collections
A4 = [p for p in itertools.permutations((1,2,3,4))
      if sum(1 for i in range(4) for j in range(i+1,4) if p[i]>p[j])%2==0]
idx = {p:i for i,p in enumerate(A4)}
def mul(p,q): return tuple(p[q[i]-1] for i in range(4))
def inv(p):
    r=[0]*4
    for i in range(4): r[p[i]-1]=i+1
    return tuple(r)
E=(1,2,3,4)
def order(p):
    n=1;q=p
    while q!=E: q=mul(q,p); n+=1
    return n
twos=[p for p in A4 if order(p)==2]
def parse_perm(s):
    if s=='e': return E
    img={i:i for i in (1,2,3,4)}
    cur=[]
    for ch in s:
        if ch=='(': cur=[]
        elif ch==')':
            for a,b in zip(cur,cur[1:]+cur[:1]): img[a]=b
        elif ch.isdigit(): cur.append(int(ch))
    return tuple(img[i] for i in (1,2,3,4))

# gauge-transform the GIF's actual seed into tree gauge (A_01=A_02=A_03=e)
raw = {'01':'e','02':'(1 2 3)','03':'e','12':'e','13':'(2 4 3)','23':'e'}
raw = {k:parse_perm(v) for k,v in raw.items()}
lam = {0:E, 1:inv(raw['01']), 2:inv(raw['02']), 3:inv(raw['03'])}
def gtrans(a,i,j): return mul(mul(inv(lam[i]),a),lam[j])
A0 = gtrans(raw['12'],1,2)
B0 = gtrans(raw['13'],1,3)
C0 = gtrans(raw['23'],2,3)
print("tree-gauge seed (A,B,C):", A0,B0,C0)
start=(idx[A0], idx[B0], idx[C0])

def bfs_any(gens, start):
    seen={start}; dq=collections.deque([start])
    while dq:
        t=dq.popleft()
        for pos in range(3):
            for g in gens:
                d=list(t); d[pos]=idx[mul(A4[d[pos]],g)]
                d=tuple(d)
                if d not in seen: seen.add(d); dq.append(d)
    return seen
comp = bfs_any(twos, start)
print("reachable raw states from the ACTUAL gif seed, order-2 moves:", len(comp))

def gclass(g,t):
    A,B,C=[A4[x] for x in t]
    return (idx[mul(mul(g,A),inv(g))], idx[mul(mul(g,B),inv(g))], idx[mul(mul(g,C),inv(g))])
remaining=set(comp); classes=[]
while remaining:
    t0=next(iter(remaining))
    orb=set(gclass(g,t0) for g in A4)
    classes.append(orb & comp)
    remaining -= orb
print("distinct TRUE physical classes among these:", len(classes))
print("sizes:", sorted(len(c) for c in classes))
