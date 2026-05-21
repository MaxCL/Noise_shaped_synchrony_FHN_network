#!/usr/bin/env python3
"""
Figure 2 — Cluster heatmap (noise D vs coupling C).
Reproduces s_B_p_3_k5_no_arrows.png from Figure_02_heatmap.ipynb.

Input : clusters_B_3_k5.csv  (columns: noise, coupling, cluster)
Output: s_B_p_3_k5_no_arrows.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.transforms as mtransforms

# ── Config ────────────────────────────────────────────────────────────────────
CSV_PATH    = "clusters_B_3_k5.csv"
OUTPUT_FILE = "s_B_p_3_k5_no_arrows.png"

CLUSTER_COLORS = {
    0: "#e41a1c",   # PN — red
    1: "#377eb8",   # QS — blue
    2: "#4daf4a",   # NS — green
    3: "#984ea3",   # CS — purple
    4: "#ff7f00",   # IS — orange
}

LABELS_MAP = {0: "PN", 1: "QS", 2: "NS", 3: "CS", 4: "IS"}

# Desired X-tick values and labels (noise D)
DESIRED_NOISE_VALS = np.array([
    0.0, 0.001, 0.0025, 0.0055, 0.0085, 0.013, 0.019, 0.06, 0.3,
])
DESIRED_NOISE_LABELS = [
    "0.0000", "0.0010", "0.0025", "0.0055", "0.0085",
    "0.0130", "0.0190", "0.0600", "0.3000",
]

# Desired Y-tick values (coupling C)
DESIRED_COUPLING_VALS = np.round(np.arange(0.00, 0.1001, 0.02), 2)

# Highlighted row
HIGHLIGHT_COUPLING = 0.06

# Numbered circle labels along the highlighted row
D_POINTS = [0.0002, 0.0013, 0.0037, 0.0080, 0.0130, 0.0200, 0.2000]

# Filter bounds
YMIN, YMAX = 0.0, 0.1

# Style
LABEL_SIZE  = 11.0
LABEL_XOFF  = 0.60
LABEL_YOFF  = 0.20
LABEL_PAD   = 0.25


def plot_labels_heatmap(labels_df):
    col_map = {c.lower(): c for c in labels_df.columns}
    ncol = col_map["noise"]
    ccol = col_map["coupling"]
    lcol = col_map["cluster"]

    noise_vals    = labels_df[ncol].astype(float).to_numpy()
    coupling_vals = labels_df[ccol].astype(float).to_numpy()
    cluster_vals  = labels_df[lcol].astype(int).to_numpy()

    # Filter by coupling range
    mask = (coupling_vals >= YMIN) & (coupling_vals <= YMAX)
    noise_vals, coupling_vals, cluster_vals = (
        noise_vals[mask], coupling_vals[mask], cluster_vals[mask]
    )

    noise_unique    = np.unique(noise_vals)
    coupling_unique = np.unique(coupling_vals)

    # Build 2D grid [n_coupling × n_noise]
    heatmap_data = np.full((len(coupling_unique), len(noise_unique)), np.nan)
    noise_idx    = {v: j for j, v in enumerate(noise_unique)}
    coupling_idx = {v: i for i, v in enumerate(coupling_unique)}
    for n, c, cl in zip(noise_vals, coupling_vals, cluster_vals):
        heatmap_data[coupling_idx[c], noise_idx[n]] = cl

    # Colormap
    min_cl  = int(np.nanmin(cluster_vals))
    max_cl  = int(np.nanmax(cluster_vals))
    classes = np.arange(min_cl, max_cl + 1)
    colors  = [CLUSTER_COLORS.get(int(cl), "gray") for cl in classes]
    cmap    = ListedColormap(colors)
    norm    = BoundaryNorm(np.arange(min_cl - 0.5, max_cl + 1.5, 1.0), ncolors=cmap.N)

    # Style
    plt.rcParams.update({
        "text.usetex":      True,
        "font.family":      "serif",
        "axes.linewidth":   1.2,
        "xtick.direction":  "in",
        "ytick.direction":  "in",
        "xtick.major.size": 6,
        "ytick.major.size": 6,
        "xtick.minor.size": 3,
        "ytick.minor.size": 3,
        "legend.frameon":   True,
        "legend.edgecolor": "black",
    })
    sns.set_theme(style="white")

    fig, ax = plt.subplots(figsize=(10, 6))

    hm = sns.heatmap(
        heatmap_data, ax=ax,
        xticklabels=np.round(noise_unique, 4),
        yticklabels=np.round(coupling_unique, 4),
        cmap=cmap, norm=norm,
        cbar_kws={"pad": 0.01, "ticks": classes},
        linewidths=0.1, linecolor="gray",
    )

    # X-ticks: desired noise values
    xticks_pos, xticks_lab = [], []
    for v, lab in zip(DESIRED_NOISE_VALS, DESIRED_NOISE_LABELS):
        hits = np.where(np.isclose(noise_unique, v, atol=1e-12))[0]
        if len(hits):
            xticks_pos.append(int(hits[0]) + 0.5)
            xticks_lab.append(lab)
    if xticks_pos:
        ax.set_xticks(xticks_pos)
        ax.set_xticklabels(xticks_lab, rotation=90, ha="center")
        ax.set_xlim(0, len(noise_unique))

    # Y-ticks: desired coupling values
    idxs = [i for i, v in enumerate(coupling_unique)
             if np.any(np.isclose(v, DESIRED_COUPLING_VALS, atol=1e-12))]
    ax.set_yticks([i + 0.5 for i in idxs])
    ax.set_yticklabels([f"{coupling_unique[i]:.2f}" for i in idxs],
                       rotation=0, va="center")

    # Axis labels
    ax.set_xlabel(r"$D$", fontsize=23)
    ax.set_ylabel(r"$C$", fontsize=23, rotation=0)
    ax.tick_params(axis="both", which="major", labelsize=16)

    # Shift Y-label down 2 mm
    dy_in = -2 / 25.4
    offset = mtransforms.ScaledTranslation(0, dy_in, fig.dpi_scale_trans)
    ax.yaxis.get_label().set_transform(
        ax.yaxis.get_label().get_transform() + offset
    )

    ax.invert_yaxis()

    # Dashed box around γ = 0.06 row
    hits = np.where(np.isclose(coupling_unique, HIGHLIGHT_COUPLING, atol=1e-12))[0]
    if len(hits):
        i = hits[0]
        ax.hlines([i, i + 1], xmin=0, xmax=len(noise_unique),
                  colors="black", linestyles="--", alpha=0.6)
        ax.vlines([0, len(noise_unique)], ymin=i, ymax=i + 1,
                  colors="black", linestyles="--", alpha=0.6)

    # Colorbar labels
    cbar = hm.collections[0].colorbar
    cbar.set_label("")
    cbar.set_ticks(classes)
    cbar.set_ticklabels(
        [r"$\mathrm{" + LABELS_MAP.get(int(cl), str(int(cl))) + "}$"
         for cl in classes]
    )
    cbar.ax.tick_params(labelsize=18)
    for text in cbar.ax.get_yticklabels():
        text.set_family("serif")

    # Numbered circle labels along γ = 0.06 row
    row_hits = np.where(np.isclose(coupling_unique, HIGHLIGHT_COUPLING, atol=1e-9))[0]
    i_row = int(row_hits[0]) if len(row_hits) else int(
        np.argmin(np.abs(coupling_unique - HIGHLIGHT_COUPLING))
    )

    up_1mm = mtransforms.ScaledTranslation(0, 1.0 / 25.4, fig.dpi_scale_trans)
    text_transform = ax.transData + up_1mm

    for k, D_val in enumerate(D_POINTS, start=1):
        j = int(np.argmin(np.abs(noise_unique - D_val)))
        ax.text(
            j + 0.5 - LABEL_XOFF, i_row + 0.5 - LABEL_YOFF,
            f"{k}", ha="center", va="center",
            fontsize=LABEL_SIZE, zorder=11,
            transform=text_transform,
            bbox=dict(boxstyle=f"circle,pad={LABEL_PAD}",
                      facecolor="white", edgecolor="black", linewidth=1.5),
        )

    return fig, ax


def main():
    df = pd.read_csv(CSV_PATH)

    fig, ax = plot_labels_heatmap(df)

    plt.tight_layout()

    # Shift Y-label up 3 mm (post-layout adjustment matching notebook)
    dy_in = 3 / 25.4
    offset = mtransforms.ScaledTranslation(0, dy_in, fig.dpi_scale_trans)
    ax.yaxis.get_label().set_transform(
        ax.yaxis.get_label().get_transform() + offset
    )

    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
