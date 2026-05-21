#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import figures_lib as figlib
import sys


# -------- LaTeX / font setup (same as your current script) --------
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.titlesize": 16,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
})

# -------- Files: Pair A -> panel (a); Pair B -> panel (b) --------

# PANEL A INTERM SWITCH
U_FILE_A = "u_n_00060_c_00600_.b"
V_FILE_A = "v_n_00060_c_00600_.b"

# PANEL B NOISY SYNC
U_FILE_B = "u_n_00140_c_00600_.b"
V_FILE_B = "v_n_00140_c_00600_.b"

# -------- Shared data shape / offsets (same as before) --------
NODES = 50
START_OFFSET = 5000  # used by to_index()

# -------- Style knobs (copied from your single-set script) --------
ARROW_TARGET_LEN = 0.4
SEL_SIZE = 40
SEL_ALPHA = 0.9
DX, DY = 0.04, 0.04
LABEL_ALPHA = 0.9
OTHER_SIZE = 16
OTHER_ALPHA = 0.5
OTHER_T0_COLOR = "blue"
OTHER_T1_COLOR = "green"

# -------- Panel-specific configs (independent) --------

var_t0 = float(sys.argv[1])

PANEL_A = {
    "node": 25,
    "t0": var_t0, "t1": 269.265,
    "dt0": 2.0, "dt1": 2.0,
    "show_nullclines": True,
    "show_limit_cycle": True,
    "show_vectors": True,
    "title": r"(a)"
}
PANEL_B = {
    "node": 30,
    "t0": 409.05, "t1": 412.030,
    "dt0": 3.0, "dt1": 5.0,
    "show_nullclines": True,
    "show_limit_cycle": True,
    "show_vectors": True,
    "title": r"(b)"
}

def to_index(t_thousands, it):
    """Match your existing time->index conversion."""
    return max(0, min(it - 1, int(round(t_thousands * 1000)) + START_OFFSET))

def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def _prepare_uv(u_file, v_file):
    u_vec = np.fromfile(u_file, dtype=np.float64)
    v_vec = np.fromfile(v_file, dtype=np.float64)
    it = min(u_vec.size // NODES, v_vec.size // NODES)
    u_mat = u_vec[:it * NODES].reshape(it, NODES)
    v_mat = v_vec[:it * NODES].reshape(it, NODES)
    return u_mat, v_mat

def plot_panel(ax, u_mat, v_mat, cfg, is_top=False, is_bottom=False):
    node = cfg["node"]
    t0, t1 = cfg["t0"], cfg["t1"]
    dt0, dt1 = cfg["dt0"], cfg["dt1"]

    it, N = u_mat.shape
    ia  = to_index(t0, it)
    ib  = to_index(t1, it)
    iai = to_index(t0 - dt0, it)
    ibi = to_index(t1 + dt1, it)
    if ia > ib: ia, ib = ib, ia
    if iai > ibi: iai, ibi = ibi, iai
    iai = max(0, min(iai, ia))
    ibi = min(max(ib, ibi), it - 1)

    ax.set_xlim(-2.5,  2.0)
    ax.set_ylim(-1.0,  2.1)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)

    # labels
    if is_bottom:
        ax.set_xlabel(r"$u$")
    else:
        ax.set_xlabel("")
        ax.tick_params(labelbottom=False)
    ax.set_ylabel(r"$v$", rotation=0)

    # background curves
    if cfg.get("show_nullclines", True):
        figlib.plot_fhn_nullclines(ax)
    if cfg.get("show_limit_cycle", True):
        figlib.plot_limit_cycle(ax)

    # other nodes
    mask = np.ones(N, dtype=bool); mask[node] = False
    ax.scatter(u_mat[ia, :][mask], v_mat[ia, :][mask], s=OTHER_SIZE, c=OTHER_T0_COLOR, alpha=OTHER_ALPHA, zorder=4)
    ax.scatter(u_mat[ib, :][mask], v_mat[ib, :][mask], s=OTHER_SIZE, c=OTHER_T1_COLOR, alpha=OTHER_ALPHA, zorder=4)

    # selected node + labels
    x0, y0 = u_mat[ia, node], v_mat[ia, node]
    x1, y1 = u_mat[ib, node], v_mat[ib, node]
    ax.scatter([x0], [y0], s=SEL_SIZE, c="red", alpha=SEL_ALPHA, zorder=5)
    ax.scatter([x1], [y1], s=SEL_SIZE, c="red", alpha=SEL_ALPHA, zorder=5)
    ax.text(x0 + DX, y0 + DY - 0.2, r"$t_0$", alpha=LABEL_ALPHA, color="blue")
    ax.text(x1 + DX, y1 + DY - 0.2, r"$t_1$", alpha=LABEL_ALPHA, color="green")

    # vectors (same helper signatures as your working script)
    Cu0 = figlib.Cu_at(u_mat, node, ia);   Cv0 = figlib.Cv_at(v_mat, node, ia)
    Lu0 = figlib.Lu_at(u_mat, v_mat, node, ia); Lv0 = figlib.Lv_at(u_mat, node, ia)
    Cu1 = figlib.Cu_at(u_mat, node, ib);   Cv1 = figlib.Cv_at(v_mat, node, ib)
    Lu1 = figlib.Lu_at(u_mat, v_mat, node, ib); Lv1 = figlib.Lv_at(u_mat, node, ib)
    s0  = figlib.noise_at(node, ia)
    s1  = figlib.noise_at(node, ib)

    Cs0 = unit(np.array([Cu0, Cv0], float)) * ARROW_TARGET_LEN
    Ls0 = unit(np.array([Lu0, Lv0], float)) * ARROW_TARGET_LEN
    Ns0 = unit(np.array([0.0, s0],  float)) * ARROW_TARGET_LEN
    Cs1 = unit(np.array([Cu1, Cv1], float)) * ARROW_TARGET_LEN
    Ls1 = unit(np.array([Lu1, Lv1], float)) * ARROW_TARGET_LEN
    Ns1 = unit(np.array([0.0, s1],  float)) * ARROW_TARGET_LEN

    figlib.plot_node_vectors(ax, x0, y0, vecs=np.array([Cs0, Ls0, Ns0]), colors=["hotpink", "blueviolet", "teal"])
    figlib.plot_node_vectors(ax, x1, y1, vecs=np.array([Cs1, Ls1, Ns1]), colors=["hotpink", "blueviolet", "teal"])

    # inset (u-matrix only), with core ticks at t0..t1
    figlib.add_spacetime_inset(
        ax_parent=ax, u_raw_matrix_ITxN=u_mat,
        ia_inset=iai, ib_inset=ibi, node=node,
        ia_core=ia, ib_core=ib, nodes=NODES,
        rect_color="black",
        rect_alpha=0.7, 
        rect_lw=0.5,
        width="80%", 
        height="25%", 
        loc="upper right"
    )

    # panel tag
    tag = cfg.get("title")
    if tag:
        ax.text(0.02, 0.98, tag, transform=ax.transAxes, ha="left", va="top", fontsize=14, fontweight="bold")

def main():
    # Pair A → panel (a)
    uA, vA = _prepare_uv(U_FILE_A, V_FILE_A)
    # Pair B → panel (b)
    uB, vB = _prepare_uv(U_FILE_B, V_FILE_B)

    fig, axes = plt.subplots(2, 1, figsize=(6.5, 7.5), dpi=300, sharex=False)

    plot_panel(axes[0], uA, vA, PANEL_A, is_top=True,  is_bottom=False)
    plot_panel(axes[1], uB, vB, PANEL_B, is_top=False, is_bottom=True)

    plt.tight_layout()
    plt.savefig("fig01_2sets.png", bbox_inches="tight", dpi=700)
    print("Saved fig01_2sets.png")

if __name__ == "__main__":
    main()

