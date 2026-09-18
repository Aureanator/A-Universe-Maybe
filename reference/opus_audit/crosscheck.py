# Opus audit script 3 (verbatim). Order-2 moves from the IDENTITY seed: raw BFS
# gives 64 states (= 4^3, confirming the gauge-fix identity), but the "22 classes"
# are intersections of conjugation orbits with the component — NOT physical classes.
# See crosscheck2.py for the correct count on the actual GIF seed (answer: 6).
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

start=(idx[E],idx[E],idx[E])
comp64 = bfs_any(twos, start)
print("raw reachable set size:", len(comp64))

def gclass(g, t):
    A,B,C=[A4[x] for x in t]
    return (idx[mul(mul(g,A),inv(g))], idx[mul(mul(g,B),inv(g))], idx[mul(mul(g,C),inv(g))])

# how many distinct global-conjugation classes (of the full 178) appear in comp64?
seen_full=set(); classes=[]
remaining=set(comp64)
while remaining:
    t0=next(iter(remaining))
    orb=set(gclass(g,t0) for g in A4)
    classes.append(orb & comp64)
    remaining -= orb
print("distinct residual-gauge classes represented in the 64-set:", len(classes))
print("class sizes (within the 64):", sorted(len(c) for c in classes))
