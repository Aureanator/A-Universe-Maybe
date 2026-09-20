"""P27: calm-seed controls and probability current (registered in PREDICTIONS).

python examples/p27_vacuum.py --n 5 --output <new-json-path>
Repeat for n=6. Existing outputs are never overwritten at launch.
"""

import argparse
import json
from pathlib import Path
import sys
import time

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'examples'))

from constraintnet.current import continuity_residual, cycle_transport, transport_current
from constraintnet.phase_filter import eigen_residual, phase_averages
from constraintnet.qrecord import QuantumRecordWalk
from p25_seeded import df_branches, gibbs_bath
from p26_dressed import embed_closed, flat_step, loop_distances, observables, setup


def compact_observables(Q, state, mask, distances):
    result = observables(Q, state, mask, distances)
    result.pop('record_configuration_probabilities')
    return result


def integrated_current(rows):
    signed = sum(r['signed_crossings'] for r in rows)
    traffic = sum(r['traffic'] for r in rows)
    return {'signed_crossings': signed, 'traffic': traffic,
            'bias': signed / traffic if traffic else 0.0,
            'edge_flux_sums': np.sum([r['edge_flux'] for r in rows], axis=0).tolist()}


def run(n, output):
    start = time.perf_counter()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as f:
        json.dump({'experiment': 'P27', 'n': n, 'status': 'initializing'}, f)
    p26_path = ROOT / f'reference/astra_session/data/p26_dressed_n{n}.json'
    p26 = json.loads(p26_path.read_text())
    if p26['status'] != 'complete':
        raise ValueError('P26 reference must be complete')
    cx, cycle, edges = setup(n)
    Q = QuantumRecordWalk(cx, edges, 0.1, 0.1, mode='closed')
    df, mask = df_branches(Q, cycle)
    Cv = df * Q.vac[None, :, None]
    Cv /= np.linalg.norm(Cv)
    i0 = np.ravel_multi_index((Q.e_id,) * Q.k, (12,) * Q.k)
    Iv = df[:, i0, :][:, None, :] * Q.vac[None, :, None]
    Iv /= np.linalg.norm(Iv)
    b, bath = gibbs_bath(Q, 0.14, 1)
    noisy = df * b[None, :, None]
    noisy /= np.linalg.norm(noisy)
    del df
    rec_next = Q.apply_rec(Q.vac[None, :, None])[0, :, 0]
    phase = float(np.angle(np.vdot(Q.vac, rec_next)))
    distances = loop_distances(cx, cycle, Q.walk.arcs)
    out = {'experiment': 'P27', 'status': 'filtering', 'n': n, 'pattern': 'L4',
           'couplings': [0.1, 0.1], 'record_edges': edges, 'record_configs': Q.nc,
           'vacuum_phase': phase, 'filter_T': 256, 'release_ticks': 128, 'bath': bath,
           'P26_reference': str(p26_path.relative_to(ROOT)), 'filter_progress': [],
           'initial': {}, 'release': [],
           'versions': {'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__}}

    def save():
        out['elapsed_seconds'] = time.perf_counter() - start
        output.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')

    out['decoupled_control'], _ = eigen_residual(lambda x: flat_step(Q, x), Iv, phase)
    save()
    for T, averages in phase_averages(Q.step, noisy, [phase], [64, 128, 256]):
        weight = float(np.linalg.norm(averages[0]) ** 2)
        out['filter_progress'].append({'T': T, 'weight': weight})
        save()
        print(f'n={n} filtered T={T}, weight={weight:.9f}', flush=True)
    F = averages[0] / np.linalg.norm(averages[0])
    del noisy, averages
    states = {'Cv': Cv, 'Iv': Iv, 'F': F}
    for name, state in states.items():
        report, _ = eigen_residual(Q.step, state, phase)
        report.update(compact_observables(Q, state, mask, distances))
        outgoing, current = transport_current(Q.walk, state)
        report['current'] = cycle_transport(Q.walk, outgoing, cycle)
        out['initial'][name] = report
        print(f"n={n} {name} residual={report['target_residual']:.8g} "
              f"loop={report['loop_weight']:.8f} bias={report['current']['bias']:.8g}", flush=True)
    out['fidelities_with_F'] = {name: float(abs(np.vdot(state, F)) ** 2)
                              for name, state in [('Cv', Cv), ('Iv', Iv)]}
    p26f = p26['filters'][-1]
    out['P26_reproduction_errors'] = {
        'filtered_weight': abs(weight - p26f['filtered_weight']),
        'loop_weight': abs(out['initial']['F']['loop_weight'] - p26f['loop_weight']),
        'target_residual': abs(out['initial']['F']['target_residual'] - p26f['target_residual'])}
    out['status'] = 'releasing'
    save()
    Qo = QuantumRecordWalk(cx, edges, 0.1, 0.1, mode='open')
    loop_arcs = {Q.walk.arcs[i] for i in np.flatnonzero(mask)}
    omask = np.array([a in loop_arcs for a in Qo.walk.arcs])
    odist = loop_distances(cx, cycle, Qo.walk.arcs)
    for name, state in states.items():
        psi = embed_closed(Q.walk, Qo.walk, state)
        arm = {'arm': name, 'samples': [], 'currents': [],
               'max_continuity_error': 0.0, 'max_bookkeeping_error': 0.0}
        out['release'].append(arm)
        gone = 0.0
        for t in range(129):
            if t in [0, 32, 64, 128]:
                obs = compact_observables(Qo, psi, omask, odist)
                arm['samples'].append({'t': t, 'escaped': gone, **obs})
                arm['max_bookkeeping_error'] = max(arm['max_bookkeeping_error'], abs(obs['norm2'] + gone - 1))
                save()
                print(f"n={n} release {name} t={t} loop={obs['loop_weight']:.8f}", flush=True)
            if t == 128:
                break
            outgoing, current = transport_current(Qo.walk, psi)
            flow = cycle_transport(Qo.walk, outgoing, cycle)
            after = Qo.step(psi)
            err = float(np.max(np.abs(continuity_residual(Qo.walk, psi, after, current))))
            arm['max_continuity_error'] = max(arm['max_continuity_error'], err)
            arm['currents'].append({'t': t, 'continuity_error': err, **flow})
            gone += float(np.sum(np.abs(Qo.escaped) ** 2))
            arm['max_bookkeeping_error'] = max(arm['max_bookkeeping_error'],
                                             abs(float(np.sum(np.abs(after) ** 2)) + gone - 1))
            psi = after
        arm['integrated_current'] = integrated_current(arm['currents'])
        arm['first_half_current'] = integrated_current(arm['currents'][:64])
        arm['last_half_current'] = integrated_current(arm['currents'][64:])
        arm['max_instantaneous_abs_bias'] = max(abs(r['bias']) for r in arm['currents'])
        save()
    loss = {a['arm']: a['samples'][0]['loop_weight'] - a['samples'][-1]['loop_weight'] for a in out['release']}
    out['loop_loss_128'] = loss
    out['filtered_to_best_vacuum_loss_ratio'] = loss['F'] / min(loss['Cv'], loss['Iv'])
    out['predictions'] = {
        'P27_1': (max(out['P26_reproduction_errors'].values()) < 1e-10
                  and out['decoupled_control']['target_residual'] < 1e-12
                  and all(a['max_continuity_error'] < 1e-10 and a['max_bookkeeping_error'] < 1e-10
                          for a in out['release'])),
        'P27_2': all(out['initial'][arm]['target_residual'] <= 0.2 * p26['raw_seed']['target_residual']
                     for arm in ['Cv', 'Iv']),
        'P27_3': loss['F'] >= 0.5 * min(loss['Cv'], loss['Iv']),
        'P27_4': max(out['fidelities_with_F'].values()) >= 0.95,
        'P27_5': all(max(abs(j) for j in out['initial'][a]['current']['edge_flux']) < 1e-12
                     for a in ['Cv', 'Iv'])}
    out['status'] = 'complete'
    save()
    print(f"n={n} complete: {out['predictions']}; F/vacuum loss={out['filtered_to_best_vacuum_loss_ratio']:.6f}", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, choices=[5, 6], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.n, args.output)
