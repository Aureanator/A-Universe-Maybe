# Opus audit script 2 (verbatim). Rebuilds the V4-move component from the GIF's
# actual seed in the full 6-edge space and probes vertex-gauge orbits.
# See README.md for interpretation: the "orbit size" measurement is an ARTIFACT
# (filters to d in comp => measures |gauge orbit ∩ component|, not the orbit).
import itertools, collections, numpy as np
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
V=[p for p in A4 if order(p)<=2]
EDGES=['01','02','03','12','13','23']

# rebuild the seed + V4-move-connected 4096 component from the original gif's dynamics
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
init={'01':'e','02':'(1 2 3)','03':'e','12':'e','13':'(2 4 3)','23':'e'}
start=tuple(idx[parse_perm(init[e])] for e in EDGES)

def moves_v4(t):
    out=[]
    for pos in range(6):
        for v in V:
            nv = idx[mul(A4[t[pos]], v)]
            if nv!=t[pos]:
                d=list(t); d[pos]=nv; out.append(tuple(d))
    return out

seen={start}; dq=collections.deque([start])
while dq:
    t=dq.popleft()
    for d in moves_v4(t):
        if d not in seen: seen.add(d); dq.append(d)
print('component size (should be 4096):', len(seen))

# gauge group: 4 vertex transformations (lambda_0..lambda_3) in A4, mod 1 global redundancy
def gauge_act(lams, t):
    l0,l1,l2,l3 = [A4[x] for x in lams]
    lam = {0:l0,1:l1,2:l2,3:l3}
    out=[]
    for e in EDGES:
        i,j=int(e[0]),int(e[1])
        pos=EDGES.index(e)
        a = A4[t[pos]]
        new = mul(mul(inv(lam[i]), a), lam[j])
        out.append(idx[new])
    return tuple(out)

comp=seen
rng=np.random.default_rng(0)
sizes=[]
for trial in range(6):
    t0 = comp.pop() if False else list(comp)[rng.integers(len(comp))]
    orb=set()
    for l0 in range(12):
        for l1 in range(12):
            for l2 in range(12):
                for l3 in range(12):
                    d=gauge_act((l0,l1,l2,l3), t0)
                    if d in comp: orb.add(d)
    sizes.append(len(orb))
    print('orbit size for a sample point:', len(orb))
print('sizes:', sizes)
print('4096 / 64 =', 4096/64)
