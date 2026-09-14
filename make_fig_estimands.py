#!/usr/bin/env python3
"""Generate the manuscript's estimand-comparison figure from local results."""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


REPO = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(REPO, "revision_results.json")
OUTPUT_PATH = os.path.join(REPO, "paper", "fig_estimands.pdf")

with open(RESULTS_PATH, encoding="utf-8") as handle:
    results = json.load(handle)

COLORS = {"high": "#0072B2", "mid": "#E69F00", "low": "#009E73"}
MARKERS = {"high": "o", "mid": "s", "low": "^"}
TIER_ORDER = ("high", "mid", "low")

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 8.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.linewidth": 0.65,
        "xtick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.width": 0.6,
        "ytick.major.size": 2.5,
    }
)

policy = results["BC_policy_variants"]["any15"]
series = [
    ("Domain\nopt-out", policy["tier_means_domain"]),
    ("HT document\nmass", policy["tier_means_design_wt_doc"]),
    ("HT token\nmass", policy["tier_means_design_wt_tok"]),
]

fig, ax = plt.subplots(figsize=(3.35, 2.42))
x = list(range(len(series)))
for tier in TIER_ORDER:
    values = [100.0 * values_by_tier[tier] for _, values_by_tier in series]
    ax.plot(
        x,
        values,
        color=COLORS[tier],
        marker=MARKERS[tier],
        markersize=4.5,
        linewidth=1.3,
        markeredgecolor="white",
        markeredgewidth=0.6,
        label=tier,
        zorder=3,
    )
    for xx, yy in zip(x, values):
        offset = -1.5 if tier == "low" and xx == 0 else 1.0
        ax.text(
            xx,
            yy + offset,
            f"{yy:.1f}",
            ha="center",
            va="top" if offset < 0 else "bottom",
            fontsize=6.2,
            color=COLORS[tier],
        )

ax.set_xticks(x)
ax.set_xticklabels([label for label, _ in series], fontsize=6.9)
ax.set_xlim(-0.22, 2.22)
ax.set_ylim(0, 35)
ax.set_yticks([0, 10, 20, 30])
ax.set_ylabel("share (%)")
ax.grid(axis="y", color="#dddddd", linewidth=0.5, zorder=0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(
    handles=[
        Line2D(
            [],
            [],
            color=COLORS[tier],
            marker=MARKERS[tier],
            linewidth=1.2,
            markersize=4.2,
            markeredgecolor="white",
            markeredgewidth=0.5,
            label=tier,
        )
        for tier in TIER_ORDER
    ],
    frameon=False,
    ncol=3,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.18),
    fontsize=6.8,
    handlelength=1.0,
    columnspacing=0.8,
)
fig.subplots_adjust(left=0.18, right=0.99, bottom=0.30, top=0.82)
fig.savefig(OUTPUT_PATH, facecolor="white")
plt.close(fig)
print(f"saved {OUTPUT_PATH}")
