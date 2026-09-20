"""Summarize complete P27 vacuum controls and plot loss/current diagnostics."""

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'reference/astra_session/data'


def summarize(d):
    if d['status'] != 'complete':
        raise ValueError('P27 run must be complete')
    releases = {r['arm']: r for r in d['release']}
    return {'n': d['n'], 'predictions': d['predictions'],
            'P26_reproduction_errors': d['P26_reproduction_errors'],
            'filtered_to_best_vacuum_loss_ratio': d['filtered_to_best_vacuum_loss_ratio'],
            'fidelities_with_F': d['fidelities_with_F'],
            'arms': {name: {
                'target_residual': d['initial'][name]['target_residual'],
                'initial_loop_weight': d['initial'][name]['loop_weight'],
                'record_vacuum_population': d['initial'][name]['record_vacuum_population'],
                'loop_loss_128': d['loop_loss_128'][name],
                'final_loop_weight': r['samples'][-1]['loop_weight'],
                'integrated_bias': r['integrated_current']['bias'],
                'first_half_bias': r['first_half_current']['bias'],
                'last_half_bias': r['last_half_current']['bias'],
                'max_instantaneous_abs_bias': r['max_instantaneous_abs_bias'],
                'max_continuity_error': r['max_continuity_error'],
                'max_bookkeeping_error': r['max_bookkeeping_error']}
                for name, r in releases.items()}}


def main():
    ds = [json.loads((DATA / f'p27_vacuum_n{n}.json').read_text()) for n in (5, 6)]
    rows = [summarize(d) for d in ds]
    summary = {'experiment': 'P27', 'runs': rows}
    (DATA / 'p27_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    p26s = [json.loads((DATA / f'p26_dressed_n{n}.json').read_text()) for n in (5, 6)]
    colors = {'Cv': '#347a53', 'Iv': '#c07d30', 'F': '#176ca2'}
    labels = ['Noisy seed', 'Compatible vacuum', 'Product vacuum', 'Filtered']
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axs = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for i, (d, old) in enumerate(zip(ds, p26s)):
        offset = (i - 0.5) * 0.35
        raw = next(r for r in old['release'] if r['arm'] == 'raw')
        raw_loss = raw['samples'][0]['loop_weight'] - raw['samples'][-1]['loop_weight']
        losses = [raw_loss] + [d['loop_loss_128'][name] for name in ['Cv', 'Iv', 'F']]
        residuals = [old['raw_seed']['target_residual']] + [d['initial'][a]['target_residual'] for a in ['Cv', 'Iv', 'F']]
        for ax, values in zip(axs[0], [losses, residuals]):
            ax.bar(np.arange(4) + offset, values, width=0.35,
                   color=['#888888'] + [colors[a] for a in ['Cv', 'Iv', 'F']],
                   hatch='' if i == 0 else '//', alpha=0.85, label=f"n={d['n']}")
        for arm in d['release']:
            name = arm['arm']
            axs[1, i].plot([r['t'] for r in arm['currents']], [r['bias'] for r in arm['currents']],
                           color=colors[name], label=name, linewidth=1.1)
        axs[1, i].set(title=f"Oriented probability-current bias, n={d['n']}", xlabel='Open-release tick',
                      ylabel='Net directed crossings / traffic')
        axs[1, i].axhline(0, color='#555555', linewidth=0.7)
        axs[1, i].ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        axs[1, i].legend()
    axs[0, 0].set(title='Loop-weight loss over 128 open ticks', ylabel='Initial loop weight minus final loop weight')
    axs[0, 1].set(title='Full-state eigenray residual', ylabel='One-tick target residual', yscale='log')
    for ax in axs[0]:
        ax.set_xticks(np.arange(4), labels, rotation=15, ha='right')
        ax.legend()
    for ax in axs.flat:
        ax.grid(axis='y', alpha=0.2)
        ax.set_axisbelow(True)
    fig.suptitle('P27: compare calm controls before attributing persistence to dressing', fontsize=14)
    path = ROOT / 'out/p27_vacuum.png'
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=160)
    print(path)


if __name__ == '__main__':
    main()
