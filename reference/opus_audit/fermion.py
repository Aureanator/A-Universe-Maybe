# Opus audit script 5 (verbatim). D(A4) topological spins: theta = chi_rho(g_C)/dim(rho),
# i.e. a charge's character evaluated on its OWN flux (self-Aharonov-Bohm).
# Output: order-2 flux x V4 characters W2,W3 -> theta = -1 (fermionic TWIST candidates);
# order-3 flux x Z3 characters -> 1, omega, omega^2 (anyonic). NOTE: twist != exchange
# statistics; R/F symbols needed before claiming fermions. See README.md.
import itertools
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

q2 = next(p for p in A4 if order(p)==2)
V = [p for p in A4 if order(p)<=2]     # centralizer of q2 = V4 itself
print("q2 =", q2, "  V4 =", V)

# character table of V4, indexed consistently with V's own ordering
e_,a_,b_,ab_ = V
charsV4 = {'W0':[1,1,1,1], 'W1':[1,1,-1,-1], 'W2':[1,-1,1,-1], 'W3':[1,-1,-1,1]}
qpos = V.index(q2)
print("q2 sits at position", qpos, "in [e,a,b,ab] =", V)
for name,ch in charsV4.items():
    theta = ch[qpos]           # theta = pi(g)/dim(pi), dim=1 here
    print(f"dyon (order-2 class, {name}): theta = {theta}  {'<-- FERMION CANDIDATE' if theta==-1 else ''}")

print()
threes=[p for p in A4 if order(p)==3]
seed=threes[0]
Hc = [h for h in A4 if mul(mul(h,seed),inv(h))==seed]
print("centralizer of order-3 seed:", Hc)
import cmath
w = cmath.exp(2j*cmath.pi/3)
qpos3 = Hc.index(seed)
for name,val in (('V0',1),('V1',w),('V2',w**2)):
    theta = val**qpos3 if False else None
# simpler: theta for irrep chi_k of Z3=<seed> is chi_k(seed) = w^k
for k in range(3):
    theta = w**k
    print(f"dyon (order-3 class, chi_{k}): theta = {theta:.3f}")
