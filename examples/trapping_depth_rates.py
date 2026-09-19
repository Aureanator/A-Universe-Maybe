"""P17 depth study: exact leak rates of the non-dark sector of the Sierpinski gasket.

The non-dark sector D^perp is the Krylov space of the exit vertex. In the Lanczos
basis L|D^perp is a Jacobi matrix J and K|D^perp = J - i Gamma e1 e1^T, so its
eigenvalues give EVERY decay rate. Lanczos runs at 400 digits (exact integer
Laplacian); termination beta < 1e-200 fixes dim D^perp. Eigenvalues at 150 digits.
Needs mpmath (pip install mpmath). Reproduce: python examples/trapping_depth_rates.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from trapping_test import sierpinski, ROOT
import mpmath as mp, time, json
def jacobi(lev, dps=400):
    mp.mp.dps=dps
    v,e,g,b=sierpinski(lev); n=len(v)
    adj=[[] for _ in range(n)]
    for i,j in e: adj[i].append(j); adj[j].append(i)
    deg=[len(a) for a in adj]
    Lmul=lambda x:[deg[i]*x[i]-mp.fsum(x[j] for j in adj[i]) for i in range(n)]
    q=[mp.mpf(0)]*n; q[b]=mp.mpf(1); qprev=[mp.mpf(0)]*n; beta=mp.mpf(0); al=[];be=[]
    while True:
        w=Lmul(q); a=mp.fsum(w[i]*q[i] for i in range(n)); al.append(a)
        w=[w[i]-a*q[i]-beta*qprev[i] for i in range(n)]
        nb=mp.sqrt(mp.fsum(x*x for x in w))
        if nb < mp.mpf(10)**(-200): break
        be.append(nb); qprev=q; q=[x/nb for x in w]; beta=nb
    return n, al, be
out={}
LEVELS = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]
for lev in LEVELS:
    t=time.time(); n,al,be=jacobi(lev)
    r=len(al); mp.mp.dps=150
    M=mp.matrix(r,r)
    for i in range(r):
        M[i,i]=al[i]
        if i<r-1: M[i,i+1]=be[i]; M[i+1,i]=be[i]
    M[0,0]=M[0,0]-1j
    ev=mp.eig(M,left=False,right=False)
    rates=sorted([-mp.im(x) for x in ev])
    out[lev]={"N":n,"krylov_dim":r,"rates":[mp.nstr(x,6) for x in rates]}
    print(lev,n,r,'slowest',[mp.nstr(x,4) for x in rates[:5]],'fastest',mp.nstr(rates[-1],4),'sum',mp.nstr(mp.fsum(rates),10),round(time.time()-t,1),flush=True)
(ROOT / 'reference/opus_session/data/trapping_depth_rates.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
