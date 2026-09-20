"""P32A: finite-patch electric pairs and the distinction between penalties and constraints.

python examples/p32_defects.py --output reference/astra_session/data/p32a_defects.json
"""

import argparse
import itertools
import json
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from constraintnet.defect import GaugePatch
from constraintnet.defect_ops import DefectDynamics
from constraintnet.reps import a4_irreps
from constraintnet.seeds import make_tetrahedron_boundary


def fixture(group):
    cx = make_tetrahedron_boundary(group)
    if group == 'A4':
        face = sorted(cx.faces())[0]
        edges = list(itertools.combinations(face, 2))
        patch = GaugePatch(cx, edges=edges, faces=[face])
        g, reps = a4_irreps()
        chars = {r.name: [r.character[g.elements.index(e)] for e in patch.els]
                 for r in reps if r.dimension == 1 and r.name != '1'}
    else:
        patch = GaugePatch(cx)
        chars = {f'k={k}': np.exp(2j * np.pi * k * np.array(patch.els) / patch.n)
                 for k in range(1, patch.n)}
    return DefectDynamics(patch), chars


def probe(group):
    D, chars = fixture(group)
    p = D.patch
    vacuum = D.flat_vacuum()
    ground = D.readout(vacuum)
    basis = np.zeros(p.dim, complex)
    basis[np.ravel_multi_index((p.e_id,) * len(p.edges), (p.n,) * len(p.edges))] = 1
    out = {'group': group, 'dimension': p.dim, 'vertices': p.vertices, 'edges': p.edges,
           'vacuum': ground, 'flat_basis_vector': D.readout(basis), 'pairs': [], 'interventions': []}
    for name, char in chars.items():
        for a, b in itertools.permutations(p.vertices, 2):
            phase = D.string_factor([a, b], char)
            pair = phase * vacuum
            r = {'character': name, 'endpoints': [a, b], **D.readout(pair)}
            E = ground['energy'] + 2
            r['energy_residual'] = float(np.linalg.norm(D.hamiltonian(pair) - E * pair))
            r['alternate_path_errors'] = [float(np.linalg.norm(D.string_factor([a, c, b], char) * vacuum - pair))
                                          for c in p.vertices if c not in (a, b)]
            r['evolution_residuals'] = {str(t): float(np.linalg.norm(D.evolve(pair, t) - np.exp(-1j * E * t) * pair))
                                       for t in (0.37, 7.25)}
            r['charged_endpoint_projection_norms'] = [float(np.linalg.norm(D.star(v, pair))) for v in (a, b)]
            out['pairs'].append(r)
        a, b, c = p.vertices[:3]
        pair = D.string_factor([a, b], char) * vacuum
        moved = D.string_factor([b, c], char) * pair
        target = D.string_factor([a, c], char) * vacuum
        erased = D.string_factor([a, c], char).conj() * moved
        intervention = {'character': name, 'initial_endpoints': [a, b], 'moved_endpoints': [a, c],
                        'moved_readout': D.readout(moved), 'move_error': float(np.linalg.norm(moved - target)),
                        'erased_readout': D.readout(erased), 'annihilation_error': float(np.linalg.norm(erased - vacuum))}
        if len(p.vertices) == 4:
            remote = D.string_factor(p.vertices[2:], char) * pair
            prior, after = D.readout(pair), D.readout(remote)
            intervention['remote_endpoint_change'] = max(abs(after['star_expectations'][str(v)] - prior['star_expectations'][str(v)])
                                                          for v in (a, b))
        out['interventions'].append(intervention)
    if group == 'Z2':
        H, _, _ = p.hamiltonian()
        rng = np.random.default_rng(32)
        state = rng.normal(size=p.dim) + 1j * rng.normal(size=p.dim)
        state /= np.linalg.norm(state)
        out['dense_evolution_error'] = float(np.linalg.norm(D.evolve(state, 0.37) - expm(-0.37j * H) @ state))
    return out


def main(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump({'experiment': 'P32A', 'status': 'initializing'}, f)
    data = {'experiment': 'P32A', 'status': 'running', 'runs': []}
    for group in ['Z2', 'Z3', 'A4']:
        r = probe(group)
        data['runs'].append(r)
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(group, 'pairs', len(r['pairs']), 'max energy residual', max(x['energy_residual'] for x in r['pairs']),
              'max path error', max(max(x['alternate_path_errors']) for x in r['pairs']), flush=True)
    data['status'] = 'complete'
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args().output)
