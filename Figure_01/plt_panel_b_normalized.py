#!/usr/bin/env python3
"""
Panel (b) only — normalized vectors. Matches panel (b) of figure01_from_git.png.
Output: panel_b_normalized.png
"""

import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle, FancyArrowPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.titlesize": 16,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
})

# ── Data files ────────────────────────────────────────────────────────────────
U_CSV_B  = "/tmp/fhn_repo/Figure_01/u_n_00140_c_00600_.csv"
V_CSV_B  = "/tmp/fhn_repo/Figure_01/v_n_00140_c_00600_.csv"
LC_PATH  = "/tmp/fhn_repo/Figure_01/limit_cycle_sample.csv"
NOISE_GLOB = "/tmp/fhn_repo/Figure_01/clean_noise_subset.part*.csv"

NODES        = 50
START_OFFSET = 5000

# ── Panel (b) configuration ───────────────────────────────────────────────────
PANEL_B = dict(node=30, t0=409.05, t1=412.01, dt0=3.0, dt1=5.0,
               title=r"(b)", show_nullclines=True, show_limit_cycle=True, show_vectors=True)

# ── FHN / style constants ─────────────────────────────────────────────────────
_A     = 0.99
_I     = 0.0
_P     = 10
_UMIN, _UMAX = -2.5, 2.0
_DASH  = (1.5, 3.0, 6.0, 3.0)
_ARROW_BODY  = 1.0
_ARROW_HEAD  = 14.0
_ARROW_LW    = 1.6
_ARROW_ALPHA = 0.95
_ARROW_Z     = 6
_L = 0.4   # normalized arrow length

# ── Helpers ───────────────────────────────────────────────────────────────────
def _circulant_window_vec(N, i_1based, P):
    v = np.zeros(N)
    idx = np.arange(i_1based - 1 - P, i_1based + P) % N
    v[idx] = 1
    return v

def Cu_at(u, node, idx):
    row = u[idx]
    vec = _circulant_window_vec(u.shape[1], node + 1, _P)
    return np.dot(row - row[node], vec)

def Cv_at(v, node, idx):
    row = v[idx]
    vec = _circulant_window_vec(v.shape[1], node + 1, _P)
    return np.dot(row - row[node], vec)

def plot_fhn_nullclines(ax):
    u = np.linspace(_UMIN, _UMAX, 800)
    v = u - (u**3) / 3.0 + _I
    ax.plot(u, v, color="black", lw=1.0, ls=(0, _DASH), alpha=0.5)
    ax.axvline(-_A, color="black", lw=1.0, ls=":", alpha=0.5)

def plot_limit_cycle(ax):
    lc = np.genfromtxt(LC_PATH, delimiter=",", dtype=float)
    ax.plot(lc[:, 0], lc[:, 1], "--", lw=1.0, alpha=0.5, color="0.35")

def _make_cmap():
    return LinearSegmentedColormap.from_list(
        "cmap", [(0, "blue"), (0.45, "white"), (0.55, "white"), (1, "red")]
    )

def add_spacetime_inset(ax, u_mat, ia, ib, node, ia_core, ib_core):
    data = u_mat.T[:, int(ia):int(ib) + 1]
    ins = inset_axes(ax, width="80%", height="25%", loc="upper right", borderpad=0.5)
    ins.imshow(data, origin="lower", aspect="auto", cmap=_make_cmap(),
               vmin=-3.0, vmax=1.5, extent=(ia, ib + 1, 0, NODES - 1), interpolation="none")
    ins.set_xlim(ia, ib + 1)
    ins.set_ylim(0, NODES - 1)
    ins.set_xticks([ia_core, ib_core + 1])
    ins.set_xticklabels([r"$t_0$", r"$t_1$"], fontsize=18)
    ins.set_yticks([0, NODES - 1])
    ins.set_yticklabels([1, NODES], fontsize=14)
    rect = Rectangle((ia_core, node - 0.5), ib_core + 1 - ia_core, 1.0,
                     fill=False, edgecolor="black", linewidth=0.5, alpha=0.7)
    ins.add_patch(rect)

def plot_node_vectors(ax, x, y, vecs, colors):
    for (vx, vy), c in zip(vecs, colors):
        arr = FancyArrowPatch(
            (x, y), (x + _ARROW_BODY * vx, y + _ARROW_BODY * vy),
            arrowstyle="->", mutation_scale=_ARROW_HEAD,
            lw=_ARROW_LW, color=c, alpha=_ARROW_ALPHA
        )
        arr.set_zorder(_ARROW_Z)
        ax.add_patch(arr)

_NOISE_CACHE = None
def _load_noise():
    global _NOISE_CACHE
    if _NOISE_CACHE is not None:
        return _NOISE_CACHE
    files = sorted(glob.glob(NOISE_GLOB))
    if not files:
        raise FileNotFoundError(f"No noise files found: {NOISE_GLOB}")
    idxs, blocks = [], []
    for p in files:
        a = np.loadtxt(p, delimiter=",", skiprows=1)
        if a.ndim == 1:
            a = a[None, :]
        idxs.append(a[:, 0].astype(int))
        blocks.append(a[:, 2:])
    _NOISE_CACHE = (np.concatenate(idxs), np.vstack(blocks))
    return _NOISE_CACHE

def noise_at(node, abs_idx):
    idxs, noise = _load_noise()
    i = min(np.searchsorted(idxs, abs_idx), len(idxs) - 1)
    if abs_idx <= idxs[0]:  i = 0
    if abs_idx >= idxs[-1]: i = len(idxs) - 1
    return float(noise[i, node])

# ── Data loading ──────────────────────────────────────────────────────────────
def load_csv(path):
    a = np.loadtxt(path, delimiter=",", skiprows=1)
    if a.ndim == 1:
        a = a[None, :]
    idx = a[:, 0].astype(int)
    data = a[:, 2:2 + NODES].astype(float)
    return idx, data

def to_abs(t):
    return int(round(t * 1000)) + START_OFFSET

def row_of(idxs, abs_idx):
    i0, i1 = int(idxs[0]), int(idxs[-1])
    return int(min(max(abs_idx, i0), i1) - i0)

# ── Panel rendering ───────────────────────────────────────────────────────────
def unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def plot_panel(ax, u_tup, v_tup, cfg, is_bottom=False):
    node, t0, t1, dt0, dt1 = cfg["node"], cfg["t0"], cfg["t1"], cfg["dt0"], cfg["dt1"]
    u_idx, u_mat = u_tup
    v_idx, v_mat = v_tup

    ia_abs  = to_abs(t0)
    ib_abs  = to_abs(t1)
    iai_abs = to_abs(t0 - dt0)
    ibi_abs = to_abs(t1 + dt1)

    ia  = row_of(u_idx, ia_abs)
    ib  = row_of(u_idx, ib_abs)
    iai = row_of(u_idx, iai_abs)
    ibi = row_of(u_idx, ibi_abs)

    ia,  ib  = sorted((ia,  ib))
    iai, ibi = sorted((iai, ibi))
    iai = max(0, min(iai, ia))
    ibi = min(max(ib, ibi), u_mat.shape[0] - 1)

    ax.set_xlim(-2.5, 2.0)
    ax.set_ylim(-1.0, 2.1)
    ax.set_aspect("equal")
    ax.grid(False)
    if is_bottom:
        ax.set_xlabel(r"$u$")
    else:
        ax.set_xlabel("")
        ax.tick_params(labelbottom=False)
    ax.set_ylabel(r"$v$", rotation=0)

    if cfg.get("show_nullclines", True): plot_fhn_nullclines(ax)
    if cfg.get("show_limit_cycle", True): plot_limit_cycle(ax)

    mask = np.ones(NODES, dtype=bool); mask[node] = False
    ax.scatter(u_mat[ib, :][mask], v_mat[ib, :][mask], s=16, c="green", alpha=0.5, zorder=4)

    u1, v1 = float(u_mat[ib, node]), float(v_mat[ib, node])
    ax.scatter([u1], [v1], s=40, c="red", alpha=0.9, zorder=5)
    ax.text(u1 + 0.04, v1 - 0.21, r"$t_1$", alpha=0.9, color="green", fontsize=18)

    Cu1 = float(Cu_at(u_mat, node, ib)); Cv1 = float(Cv_at(v_mat, node, ib))
    Lu1 = u1 - (u1**3)/3.0 - v1;  Lv1 = u1 + _A
    s1 = noise_at(node, int(u_idx[ib]))

    Cs1 = unit([Cu1, Cv1]) * _L;  Ls1 = unit([Lu1, Lv1]) * _L;  Ns1 = unit([0.0, s1]) * _L
    plot_node_vectors(ax, u1, v1, [Cs1, Ls1, Ns1], ["hotpink", "blueviolet", "teal"])

    add_spacetime_inset(ax, u_mat, iai, ibi, node, ia_core=ia, ib_core=ib)

    if cfg.get("title"):
        ax.text(0.02, 0.98, cfg["title"], transform=ax.transAxes,
                ha="left", va="top", fontsize=20, fontweight="bold")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    uB = load_csv(U_CSV_B)
    vB = load_csv(V_CSV_B)

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 3.75), dpi=300)
    plot_panel(ax, uB, vB, PANEL_B, is_bottom=True)
    plt.tight_layout()
    plt.savefig("panel_b_normalized_t_.png", bbox_inches="tight", dpi=700)
    print("Saved panel_b_normalized_t_.png")

if __name__ == "__main__":
    main()
