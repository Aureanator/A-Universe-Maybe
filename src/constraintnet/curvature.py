"""Coordinate-free curvature action and dual-support diagnostics on a fixed mesh.

The action is a chosen microscopic hypothesis. Components are geometric support
components, not a supplied particle catalogue. This module contains no scheduler.
"""

import itertools


class CurvatureState:
    """Indexed group arithmetic for local action differences; owns a labelled copy."""

    def __init__(self, cx):
        self.cx = cx.copy()
        self.elements = tuple(cx.group.elements)
        self.index = {g: i for i, g in enumerate(self.elements)}
        self.identity = self.index[cx.group.identity()]
        self.multiply = [[self.index[cx.group.multiply(a, b)] for b in self.elements]
                         for a in self.elements]
        self.inverse = [self.index[cx.group.inverse(a)] for a in self.elements]
        self.edges = tuple(cx.edges())
        self.faces = tuple(cx.faces())
        self.tets = tuple(cx.tetrahedra())
        edge_index = {e: i for i, e in enumerate(self.edges)}
        face_index = {f: i for i, f in enumerate(self.faces)}
        self.labels = [self.index[cx.label(*e)] for e in self.edges]
        self.face_edges = [(edge_index[a, b], edge_index[b, c], edge_index[a, c])
                           for a, b, c in self.faces]
        self.edge_faces = [[] for _ in self.edges]
        for fi, edges in enumerate(self.face_edges):
            for ei in edges:
                self.edge_faces[ei].append(fi)
        self.face_tets = [set() for _ in self.faces]
        self.tet_faces = []
        self.face_neighbors = [set() for _ in self.faces]
        for ti, tet in enumerate(self.tets):
            members = [face_index[tuple(f)] for f in itertools.combinations(tet, 3)]
            self.tet_faces.append(members)
            for fi in members:
                self.face_tets[fi].add(ti)
                self.face_neighbors[fi].update(set(members) - {fi})
        boundary = set(cx.boundary_faces())
        surface_edges = {tuple(e) for f in boundary for e in itertools.combinations(f, 2)}
        self.interior_edges = tuple(i for i, e in enumerate(self.edges) if e not in surface_edges)
        self.flux = [self.face_flux(i) for i in range(len(self.faces))]
        self.energy = sum(f != self.identity for f in self.flux)

    def face_flux(self, fi, changed_edge=None, new_label=None):
        a, b, c = self.face_edges[fi]
        av = new_label if a == changed_edge else self.labels[a]
        bv = new_label if b == changed_edge else self.labels[b]
        cv = new_label if c == changed_edge else self.labels[c]
        return self.multiply[self.multiply[av][bv]][self.inverse[cv]]

    def proposal(self, edge, multiplier):
        new = self.multiply[self.labels[edge]][multiplier]
        changed = {fi: self.face_flux(fi, edge, new) for fi in self.edge_faces[edge]}
        delta = sum((value != self.identity) - (self.flux[fi] != self.identity)
                    for fi, value in changed.items())
        return new, changed, delta

    def commit(self, edge, new, changed, delta):
        self.labels[edge] = new
        self.cx.set_label(*self.edges[edge], self.elements[new])
        self.cx.set_realized(*self.edges[edge], True)
        for fi, value in changed.items():
            self.flux[fi] = value
        self.energy += delta

    def components(self):
        """Dual-face connected components and loop status; includes isolated faces."""
        unseen = {i for i, f in enumerate(self.flux) if f != self.identity}
        result = []
        while unseen:
            start = min(unseen)
            unseen.remove(start)
            faces, queue = {start}, [start]
            for fi in queue:
                for nxt in self.face_neighbors[fi]:
                    if nxt in unseen:
                        unseen.remove(nxt)
                        faces.add(nxt)
                        queue.append(nxt)
            tets = {t for fi in faces for t in self.face_tets[fi]}
            loop = bool(tets) and all(len(self.face_tets[fi]) == 2 for fi in faces)
            loop = loop and all(sum(fi in faces for fi in self.tet_faces[t]) == 2 for t in tets)
            result.append({"faces": frozenset(faces), "tets": frozenset(tets),
                           "kind": "loop" if loop else "junction/open"})
        return result


class SupportLineage:
    """Overlap tracking; mergers/splits do not by themselves establish reactions."""

    def __init__(self, components, n_tets):
        self.n_tets = max(1, n_tets)
        self.next_id = 0
        self.live = {}
        self.finished = []
        self.events = {"birth": 0, "death": 0, "merge": 0, "split": 0}
        for component in components:
            self._new(component, 0)

    def _new(self, component, step):
        ident = self.next_id
        self.next_id += 1
        self.live[ident] = {"id": ident, "born": step, "faces": component["faces"],
                            "max_tet_fraction": len(component["tets"]) / self.n_tets,
                            "support_changes": 0, "always_loop": component["kind"] == "loop"}
        return ident

    def advance(self, components, step):
        previous = self.live
        owner = {f: ident for ident, record in previous.items() for f in record["faces"]}
        parents = [{owner[f] for f in comp["faces"] if f in owner} for comp in components]
        children = {ident: [] for ident in previous}
        for i, ancestors in enumerate(parents):
            for ident in ancestors:
                children[ident].append(i)
        self.events["birth"] += sum(not p for p in parents)
        self.events["death"] += sum(not c for c in children.values())
        self.events["merge"] += sum(len(p) > 1 for p in parents)
        self.events["split"] += sum(len(c) > 1 for c in children.values())
        self.live = {}
        continued = set()
        for i, comp in enumerate(components):
            ancestors = parents[i]
            if len(ancestors) == 1 and len(children[next(iter(ancestors))]) == 1:
                ident = next(iter(ancestors))
                record = dict(previous[ident])
                record["support_changes"] += comp["faces"] != record["faces"]
                record["faces"] = comp["faces"]
                record["always_loop"] &= comp["kind"] == "loop"
                record["max_tet_fraction"] = max(record["max_tet_fraction"],
                                                  len(comp["tets"]) / self.n_tets)
                self.live[ident] = record
                continued.add(ident)
            else:
                self._new(comp, step)
        for ident, record in previous.items():
            if ident not in continued:
                self.finished.append(self._close(record, step, False))

    @staticmethod
    def _close(record, step, censored):
        return {k: v for k, v in record.items() if k != "faces"} | {
            "lifetime": step - record["born"], "censored": censored}

    def report(self, step, min_lifetime=1000, max_fraction=0.2):
        records = self.finished + [self._close(r, step, True) for r in self.live.values()]
        candidates = [r for r in records if r["lifetime"] >= min_lifetime
                      and r["max_tet_fraction"] <= max_fraction]
        return {"geometric_events": dict(self.events), "branches": len(records),
                "longest_branch": max((r["lifetime"] for r in records), default=0),
                "candidate_screen_passes": candidates}
