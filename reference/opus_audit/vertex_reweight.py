# Opus audit script 1 (verbatim, incl. both appended debug sections).
# Confirms 82 ORDERED face-class signatures via the true 6-edge holonomy formula in
# tree gauge; shows pure multiset sorting gives 20 ("signatures" as quoted in the memo),
# while TRUE vertex-relabeling orbits are 13 (A4) / 11 (S4). The debug sections show why:
# relabeling can invert edges (A_ji = A_ij^-1) and inversion swaps order-3 chirality,
# so one orbit spans several sorted tuples. See README.md for the consequence for our docs.
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
threes=[p for p in A4 if order(p)==3]
seed=threes[0]
C3A=set(mul(mul(g,seed),inv(g)) for g in A4)
def cls(p):
    o=order(p)
    if o==1: return 'I'
    if o==2: return '2'
    return '3a' if p in C3A else '3b'

EDGES=['01','02','03','12','13','23']
FACES=[(0,1,2),(0,1,3),(0,2,3),(1,2,3)]  # face i = omit vertex i (0,1,2,3 -> which vertex missing: 3,2,1,0)
def A(cfg,i,j):
    e=f'{min(i,j)}{max(i,j)}'
    g=cfg[e]
    return g if i<j else inv(g)
def hol(cfg,f):
    i,j,k=f
    return mul(mul(A(cfg,i,j),A(cfg,j,k)),A(cfg,k,i))
def sig_ordered(cfg):
    return tuple(cls(hol(cfg,f)) for f in FACES)

# enumerate the 82 realizable *ordered* signatures directly over full 6-edge space
# (use the gauge-fixed-free representation isn't needed; sample via random search
# augmented with exhaustive check on a coarser handle: reuse earlier finding that
# the (A,BC^-1,BA^-1,C) 3-var parametrization already gives all 82; confirm here
# with the true 6-edge holonomy formula for cross-check)
found=set()
rng=np.random.default_rng(0)
# exhaustive-ish: loop A_12,A_13,A_23 freely, fix A_01=A_02=A_03=identity (tree)
for a12 in A4:
    for a13 in A4:
        for a23 in A4:
            cfg={'01':E,'02':E,'03':E,'12':a12,'13':a13,'23':a23}
            found.add(sig_ordered(cfg))
print('distinct ORDERED signatures (tree-gauge, 6-edge formula):', len(found))

# Now: vertex relabeling. A permutation sigma of {0,1,2,3} acts on an edge {i,j}
# by sending it to {sigma(i),sigma(j)}; the new edge's value is old value if
# sigma preserves order, else its inverse. It also permutes the tree, so a
# relabeled configuration generally is NOT in tree-gauge for the *same* tree.
# To test the induced action on the *signature* cleanly, work with an explicit
# full 6-edge configuration builder + apply sigma directly, no tree assumption.
def relabel(cfg, sigma):
    new={}
    for e in EDGES:
        i,j=int(e[0]),int(e[1])
        si,sj=sigma[i],sigma[j]
        ne=f'{min(si,sj)}{max(si,sj)}'
        val=cfg[e]
        new[ne]= val if si<sj else inv(val)
    return new

S4 = list(itertools.permutations((0,1,2,3)))
A4_vertex = [s for s in S4 if sum(1 for i in range(4) for j in range(i+1,4) if s[i]>s[j])%2==0]

# build one representative config for each of the 82 signatures (tree-gauge)
reps={}
for a12 in A4:
    for a13 in A4:
        for a23 in A4:
            cfg={'01':E,'02':E,'03':E,'12':a12,'13':a13,'23':a23}
            s=sig_ordered(cfg)
            if s not in reps: reps[s]=cfg
print('collected reps for', len(reps), 'signatures')

def orbit_count(group):
    seen=set(); norbits=0
    sigs=list(reps.keys())
    remaining=set(sigs)
    while remaining:
        s0=next(iter(remaining))
        orb=set()
        cfg0=reps[s0]
        for g in group:
            cfg1=relabel(cfg0,g)
            orb.add(sig_ordered(cfg1))
        remaining -= orb
        norbits+=1
    return norbits

print('orbits under full S4 vertex relabeling (24 elts):', orbit_count(S4))
print('orbits under A4 (orientation-preserving) vertex relabeling only (12 elts):', orbit_count(A4_vertex))

sorted_sigs=set(tuple(sorted(s)) for s in reps.keys())
print('sorted-tuple count (pure "sort", no group used):', len(sorted_sigs))

print("\n--- debugging why S4/A4-vertex quotient (11/13) differs from pure sort (20) ---")
# pick one signature, apply all of S4, see what it maps to (as ordered tuples)
s0 = sorted(reps.keys())[5]
cfg0 = reps[s0]
print("start signature:", s0)
images=set()
for g in S4:
    cfg1=relabel(cfg0,g)
    images.add(sig_ordered(cfg1))
print("all S4 images (ordered):")
for im in sorted(images): print("   ", im, "  sorted:", tuple(sorted(im)))
print("distinct sorted-versions among these images:", len(set(tuple(sorted(im)) for im in images)))

print("\n--- test with a 3a/3b-containing signature ---")
cand = [s for s in reps if '3a' in s or '3b' in s][0]
cfg0=reps[cand]
print("start:", cand)
images=set()
for g in S4:
    images.add(sig_ordered(relabel(cfg0,g)))
for im in sorted(images): print("   ", im)
print("distinct images:", len(images), " distinct sorted-versions:", len(set(tuple(sorted(im)) for im in images)))
