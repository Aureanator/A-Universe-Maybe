"""P32B: autonomous conserving transport; writes only to a fresh output path."""

import argparse
from collections import deque
import itertools
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from constraintnet.defect import GaugePatch
from constraintnet.defect_ops import DefectDynamics
from constraintnet.defect_transport import Z2DefectTransport
from constraintnet.seeds import make_single_tetrahedron, make_bipyramid


def shortest_path(edges, start, end):
    queue = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        if path[-1] == end:
            return path
        for a, b in edges:
            other = b if a == path[-1] else a if b == path[-1] else None
            if other is not None and other not in seen:
                seen.add(other)
                queue.append(path + [other])
    raise ValueError('disconnected endpoints')


def dense(action, dimension):
    basis = np.eye(dimension)
    return np.column_stack([action(column) for column in basis.T])


def norm(matrix):
    return float(np.linalg.norm(matrix))


def commutator(a, b):
    return norm(a @ b - b @ a)


def probe(name, cx):
    D = DefectDynamics(GaugePatch(cx))
    T = Z2DefectTransport(D, kappa=0.2)
    p = D.patch
    H0, A, _ = p.hamiltonian()
    K = dense(T.kinetic, p.dim)
    N = dense(T.number, p.dim)
    H = H0 + K
    values, vectors = np.linalg.eigh(H)
    vacuum = D.flat_vacuum()
    E0 = D.readout(vacuum)['energy']
    pairs = list(itertools.combinations(p.vertices, 2))
    paths = [shortest_path(p.edges, a, b) for a, b in pairs]
    pair_basis = np.column_stack([D.string_factor(path, [1, -1]) * vacuum for path in paths])
    # Independent combinatorial two-hard-core-boson graph, without gauge operators.
    graph = np.zeros((len(pairs), len(pairs)))
    for j, pair in enumerate(pairs):
        for a, b in p.edges:
            if (a in pair) != (b in pair):
                moved = tuple(sorted(set(pair) ^ {a, b}))
                graph[pairs.index(moved), j] -= T.kappa
    restricted = pair_basis.conj().T @ K @ pair_basis
    raw = np.diag(-T.kappa * sum(T.phases.values()))
    rng = np.random.default_rng(3202)
    random_state = rng.normal(size=p.dim) + 1j * rng.normal(size=p.dim)
    random_state /= np.linalg.norm(random_state)
    audit = {
        'hermiticity': norm(H - H.conj().T),
        'K_N_commutator': commutator(K, N), 'K_H0_commutator': commutator(K, H0),
        'K_B_commutator_max': max(norm(K * (m[None, :].astype(float) - m[:, None]))
                                  for m in D.flat_masks.values()),
        'K_A_commutator_max': max(commutator(K, a) for a in A),
        'vacuum_kinetic_norm': norm(K @ vacuum),
        'raw_N_commutator': commutator(raw, N), 'raw_H0_commutator': commutator(raw, H0),
        'raw_vacuum_pair_amplitude_norm': norm(pair_basis.conj().T @ raw @ vacuum),
        'pair_orthonormality': norm(pair_basis.conj().T @ pair_basis - np.eye(len(pairs))),
        'pair_graph_difference': norm(restricted - graph),
        'pair_sector_invariance': norm(K @ pair_basis - pair_basis @ graph),
        'random_state_continuity': max(map(abs, T.continuity_residual(random_state).values())),
        'random_state_current_max': max(map(abs, T.currents(random_state).values())),
        'eigendecomposition': norm(H @ vectors - vectors * values),
    }
    runs = []
    for index, endpoints in enumerate(pairs):
        initial = pair_basis[:, index]
        spectral = vectors.conj().T @ initial
        initial_occupation = {str(v): float(v in endpoints) for v in p.vertices}
        samples = []
        for time in [0, 0.25, 1, 3, 7]:
            state = vectors @ (np.exp(-1j * time * values) * spectral)
            readout = D.readout(state)
            occupations = {v: 1 - value for v, value in readout['star_expectations'].items()}
            amplitudes = pair_basis.conj().T @ state
            probabilities = np.abs(amplitudes) ** 2
            distances = {}
            for path, probability in zip(paths, probabilities):
                key = str(len(path) - 1)
                distances[key] = distances.get(key, 0.0) + float(probability)
            n_state = N @ state
            n_mean = float(np.vdot(state, n_state).real / readout['norm2'])
            stationary = D.evolve(initial, time)
            samples.append({
                'time': time, 'norm2': readout['norm2'], 'H0_energy': readout['energy'],
                'total_energy': float(np.vdot(state, H @ state).real / readout['norm2']),
                'number': n_mean, 'number_variance': float(np.vdot(n_state, n_state).real / readout['norm2'] - n_mean**2),
                'occupations': occupations,
                'occupation_change_max': max(abs(occupations[v] - initial_occupation[v]) for v in occupations),
                'edge_currents': {str(e): j for e, j in T.currents(state).items()},
                'continuity_residual': max(map(abs, T.continuity_residual(state).values())),
                'flatness_error': max(abs(b - 1) for b in readout['flatness_expectations'].values()),
                'pair_sector_leakage_norm': norm(state - pair_basis @ amplitudes),
                'pair_probabilities': probabilities.tolist(), 'graph_distance_probabilities': distances,
                'H0_stationary_control_error': norm(stationary - np.exp(-1j * (E0 + 2) * time) * initial),
            })
        runs.append({'endpoints': endpoints, 'preparation_path': paths[index], 'samples': samples})
    conservation = max(max(abs(s['norm2'] - 1), abs(s['number'] - 2), abs(s['number_variance']),
                           abs(s['H0_energy'] - E0 - 2), abs(s['total_energy'] - E0 - 2),
                           s['continuity_residual'], s['flatness_error'], s['pair_sector_leakage_norm'],
                           s['H0_stationary_control_error']) for r in runs for s in r['samples'])
    exact_keys = ['hermiticity', 'K_N_commutator', 'K_H0_commutator', 'K_B_commutator_max',
                  'vacuum_kinetic_norm', 'pair_orthonormality', 'pair_graph_difference',
                  'pair_sector_invariance', 'random_state_continuity', 'eigendecomposition']
    motion = max(s['occupation_change_max'] for r in runs for s in r['samples'])
    passed = (max(audit[k] for k in exact_keys) < 1e-10 and conservation < 1e-10
              and motion > 1e-3 and audit['raw_N_commutator'] > 1e-3
              and audit['raw_H0_commutator'] > 1e-3 and audit['K_A_commutator_max'] > 1e-3
              and audit['raw_vacuum_pair_amplitude_norm'] > 1e-3)
    return {'fixture': name, 'dimension': p.dim, 'vertices': p.vertices, 'edges': p.edges,
            'faces': p.faces, 'tetrahedra': list(cx.tetrahedra()), 'kappa': T.kappa,
            'vacuum_energy': E0, 'pair_order': pairs, 'audit': audit, 'runs': runs,
            'summary': {'conservation_error_max': conservation, 'occupation_change_max': motion,
                        'registered_checks_pass': bool(passed)}}


def main(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        json.dump({'experiment': 'P32B', 'status': 'initializing'}, handle)
    data = {'experiment': 'P32B', 'protocol_commit': '644e49a', 'status': 'running', 'runs': []}
    for name, cx in [('tetrahedron', make_single_tetrahedron('Z2')),
                     ('bipyramid_two', make_bipyramid('Z2', 'two'))]:
        result = probe(name, cx)
        data['runs'].append(result)
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(name, json.dumps(result['summary']), flush=True)
    passed = all(r['summary']['registered_checks_pass'] for r in data['runs'])
    data['status'] = 'complete' if passed else 'failed_checks'
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    if not passed:
        raise SystemExit('P32B failed registered checks; inspect the saved data')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args().output)
