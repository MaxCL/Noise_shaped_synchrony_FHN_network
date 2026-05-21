#!/usr/bin/env python3
"""
Batch heatmaps for all metrics — formatted to match Figure 02 layout.

Input : all_metrics.csv  (columns: noise, coupling, <metric>, ...)
Output: formatted_<metric>_metric.png  for every metric column
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.transforms as mtransforms

# ── Config ────────────────────────────────────────────────────────────────────
CSV_PATH = "all_metrics.csv"

# Human-readable colorbar labels per metric column name
CBAR_LABELS = {
    "mean_firing_rate":      r"$\mathrm{MFR}$",
    "fano_factor":           r"$\mathrm{FF}$",
    "coefficien_of_variation": r"$\mathrm{CV}$",
    "cv2":                   r"$\mathrm{CV}_2$",
    "largest_assembly":      r"$\mathrm{LA}$",
    "assembly_variety":      r"$\mathrm{AV}$",
    "spike_contrast":        r"$\mathrm{SC}$",
    "pearson_correlation":   r"$\mathrm{PC}$",
    "autocorrelation":       r"$\mathrm{AC}$",
    "isi_distance":          r"$\mathrm{ISI}$",
    "spike_distance":        r"$\mathrm{SD}$",
    "spike_sync":            r"$\mathrm{SS}$",
}

# Desired X-tick values and labels (noise D) — same as Figure 02
DESIRED_NOISE_VALS = np.array([
    0.0, 0.001, 0.0025, 0.0055, 0.0085, 0.013, 0.019, 0.06, 0.3,
])
DESIRED_NOISE_LABELS = [
    "0.0000", "0.0010", "0.0025", "0.0055", "0.0085",
    "0.0130", "0.0190", "0.0600", "0.3000",
]

# Desired Y-tick values (coupling C) — same as Figure 02
DESIRED_COUPLING_VALS = np.round(np.arange(0.00, 0.1001, 0.02), 2)

# Highlighted row — same as Figure 02
HIGHLIGHT_COUPLING = 0.06

# Numbered circle positions along the highlighted row — same as Figure 02
D_POINTS = [0.0002, 0.0013, 0.0037, 0.0080, 0.0130, 0.0200, 0.2000]

# Filter bounds
YMIN, YMAX = 0.0, 0.1

# Circle label style
LABEL_SIZE = 11.0
LABEL_XOFF = 0.60
LABEL_YOFF = 0.20
LABEL_PAD  = 0.25


def plot_metric_heatmap(df, metric_col):
    col_map = {c.lower().strip(): c for c in df.columns}
    ncol = col_map["noise"]
    ccol = col_map["coupling"]
    mcol = col_map[metric_col.lower().strip()]

    noise_vals    = df[ncol].astype(float).to_numpy()
    coupling_vals = df[ccol].astype(float).to_numpy()
    metric_vals   = df[mcol].astype(float).to_numpy()

    mask = (coupling_vals >= YMIN) & (coupling_vals <= YMAX)
    noise_vals, coupling_vals, metric_vals = (
        noise_vals[mask], coupling_vals[mask], metric_vals[mask]
    )

    noise_unique    = np.unique(noise_vals)
    coupling_unique = np.unique(coupling_vals)

    # Build 2D grid [n_coupling × n_noise] — same orientation as Figure 02
    heatmap_data = np.full((len(coupling_unique), len(noise_unique)), np.nan)
    noise_idx    = {v: j for j, v in enumerate(noise_unique)}
    coupling_idx = {v: i for i, v in enumerate(coupling_unique)}
    for n, c, m in zip(noise_vals, coupling_vals, metric_vals):
        heatmap_data[coupling_idx[c], noise_idx[n]] = m

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
        cmap="jet",
        cbar_kws={"pad": 0.01},
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

    ax.set_xlabel(r"$D$", fontsize=23)
    ax.set_ylabel(r"$C$", fontsize=23, rotation=0)
    ax.tick_params(axis="both", which="major", labelsize=16)

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

    # Colorbar
    cbar = hm.collections[0].colorbar
    label = CBAR_LABELS.get(metric_col, metric_col)
    cbar.set_label(label, fontsize=16)
    cbar.ax.tick_params(labelsize=14)

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

    plt.tight_layout()

    dy_in = 3 / 25.4
    offset = mtransforms.ScaledTranslation(0, dy_in, fig.dpi_scale_trans)
    ax.yaxis.get_label().set_transform(
        ax.yaxis.get_label().get_transform() + offset
    )

    outfile = f"formatted_{metric_col}_metric.png"
    plt.savefig(outfile, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {outfile}")


def main():
    df = pd.read_csv(CSV_PATH)
    metric_cols = [c for c in df.columns if c not in ("noise", "coupling")]
    for metric in metric_cols:
        plot_metric_heatmap(df, metric.strip())


if __name__ == "__main__":
    main()
