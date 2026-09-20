"""P32C: full edge-space exchange algebra and a canonical fermion sign control."""

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

from p32_transport import shortest_path
from constraintnet.defect import GaugePatch
from constraintnet.defect_ops import DefectDynamics
from constraintnet.defect_transport import Z2DefectTransport
from constraintnet.seeds import make_single_tetrahedron, make_bipyramid


def fermion_hop(occupied, target, source):
    """Canonical c_target^dag c_source in the ascending vertex Fock basis."""
    if source not in occupied or target in occupied:
        return occupied, 0
    between = sum(min(source, target) < v < max(source, target) for v in occupied)
    return tuple(sorted((set(occupied) - {source}) | {target})), (-1) ** between


def fermion_sequence(initial, sequence):
    occupied, amplitude = initial, 1
    for target, source in sequence:
        occupied, factor = fermion_hop(occupied, target, source)
        amplitude *= factor
    return occupied, amplitude


def probe(name, cx):
    D = DefectDynamics(GaugePatch(cx))
    T = Z2DefectTransport(D)
    p = D.patch
    vacuum = D.flat_vacuum()
    cases = []
    for i in p.vertices:
        neighbors = sorted(b if a == i else a for a, b in p.edges if i in (a, b))
        for j, k, l in itertools.permutations(neighbors, 3):
            state = D.string_factor(shortest_path(p.edges, j, l), [1, -1]) * vacuum
            expected = D.string_factor(shortest_path(p.edges, i, k), [1, -1]) * vacuum
            left_sequence = [(i, j), (k, i), (i, l)]
            right_sequence = [(i, l), (k, i), (i, j)]
            left, right = state.copy(), state.copy()
            for a, b in left_sequence:
                left = T.directed_hop(a, b, left)
            for a, b in right_sequence:
                right = T.directed_hop(a, b, right)
            left_fock, left_sign = fermion_sequence(tuple(sorted((j, l))), left_sequence)
            right_fock, right_sign = fermion_sequence(tuple(sorted((j, l))), right_sequence)
            overlap = np.vdot(right, left)
            cases.append({
                'i_j_k_l': [i, j, k, l],
                'left_norm': float(np.linalg.norm(left)), 'right_norm': float(np.linalg.norm(right)),
                'overlap_real': float(overlap.real), 'overlap_imag': float(overlap.imag),
                'plus_sign_residual': float(np.linalg.norm(left - right)),
                'minus_sign_residual': float(np.linalg.norm(left + right)),
                'target_residual': float(max(np.linalg.norm(left - expected), np.linalg.norm(right - expected))),
                'fermion_left_sign': left_sign, 'fermion_right_sign': right_sign,
                'fermion_relative_sign': left_sign * right_sign,
                'fermion_final_occupations_correct': left_fock == right_fock == tuple(sorted((i, k))),
            })
    max_error = max(max(abs(c['left_norm'] - 1), abs(c['right_norm'] - 1),
                        abs(c['overlap_real'] - 1), abs(c['overlap_imag']),
                        c['plus_sign_residual'], c['target_residual'],
                        abs(c['minus_sign_residual'] - 2)) for c in cases)
    passed = (max_error < 1e-10 and all(c['fermion_relative_sign'] == -1
                                      and c['fermion_final_occupations_correct'] for c in cases))
    return {'fixture': name, 'dimension': p.dim, 'cases': cases,
            'summary': {'case_count': len(cases), 'edge_model_sign': '+1',
                        'fermion_control_sign': '-1', 'max_error': max_error,
                        'registered_checks_pass': bool(passed)}}


def main(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        json.dump({'experiment': 'P32C', 'status': 'initializing'}, handle)
    data = {'experiment': 'P32C', 'protocol_commit': '5c2ef6a', 'status': 'running', 'runs': []}
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
        raise SystemExit('P32C failed registered checks; inspect the saved data')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args().output)
