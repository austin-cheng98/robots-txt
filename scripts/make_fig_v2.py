#!/usr/bin/env python3
"""Figure 1 v2: original dumbbell panel (a) + conditional-blocking panel (b).

Panel (b) answers reviewer requests for the conditional-on-naming denominators:
it plots, per language, the share of AI-naming domains that issue a full block,
with a bootstrap CI and the naming count n printed at the right margin.

Run after analysis_revision.py:  python3 scripts/make_fig_v2.py
Writes figures/fig_gradient_v2.pdf.
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = json.load(open(os.path.join(ROOT, "data", "analysis_v3.json")))
rev = json.load(open(os.path.join(ROOT, "results", "revision_results.json")))
cond = rev["E_conditional_on_naming"]["per_lang"]

NAME = {"eng_Latn": "English", "deu_Latn": "German", "fra_Latn": "French", "jpn_Jpan": "Japanese",
        "ind_Latn": "Indonesian", "tha_Thai": "Thai", "tur_Latn": "Turkish",
        "azj_Latn": "Azerbaijani", "vie_Latn": "Vietnamese", "sun_Latn": "Sundanese",
        "yor_Latn": "Yoruba", "uig_Arab": "Uyghur", "gle_Latn": "Irish", "swh_Latn": "Swahili"}
TIER_C = {"high": "#0072B2", "mid": "#E69F00", "low": "#009E73"}

langs = []
for tier in ["high", "mid", "low"]:
    ts = [(l, o) for l, o in a["per_lang"].items() if o["tier"] == tier]
    ts.sort(key=lambda x: x[1]["optout"], reverse=True)
    langs.extend(ts)
ys = list(range(len(langs), 0, -1))

fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.3, 2.95), dpi=300,
                             gridspec_kw={"width_ratios": [1.0, 0.88], "wspace": 0.08})

# ---- panel (a): unconditional naming vs blocking -----------------------------
for (l, o), y in zip(langs, ys):
    c = TIER_C[o["tier"]]
    lo, hi = o["ci"]
    ax.plot([lo, hi], [y, y], color=c, lw=0.8, alpha=0.35, solid_capstyle="round", zorder=1)
    ax.plot([o["optout"], o["names"]], [y, y], color=c, lw=1.4, zorder=2)
    ax.plot(o["names"], y, "o", mfc="white", mec=c, mew=1.3, ms=5, zorder=3)
    ax.plot(o["optout"], y, "o", color=c, ms=5, zorder=4)
ax.set_yticks(ys)
ax.set_yticklabels([NAME[l] for l, _ in langs], fontsize=7)
for tick, (l, o) in zip(ax.get_yticklabels(), langs):
    tick.set_color(TIER_C[o["tier"]])
ax.set_xlim(0, 0.55)
ax.set_xlabel("Share of reachable domains", fontsize=7.5)
handles = [
    Line2D([], [], marker="o", color="#555555", ls="", ms=5, label="Blocks $\\geq$1 AI agent"),
    Line2D([], [], marker="o", mfc="white", mec="#555555", mew=1.3, ls="", ms=5,
           label="Names $\\geq$1 AI agent"),
]
ax.legend(handles=handles, fontsize=6.5, loc="lower right", frameon=False,
          handletextpad=0.3, borderaxespad=0.2)
ax.set_title("(a) Naming and blocking", fontsize=7.5, loc="left", pad=3)

# ---- panel (b): blocking conditional on naming -------------------------------
for (l, o), y in zip(langs, ys):
    c = TIER_C[o["tier"]]
    cd = cond[l]
    lo, hi = cd["cond_block_ci95"]
    bx.plot([lo, hi], [y, y], color=c, lw=0.8, alpha=0.35, solid_capstyle="round", zorder=1)
    bx.plot(cd["cond_block_rate"], y, "D", color=c, ms=4.2, zorder=4)
    bx.text(1.035, y, f"{cd['n_named']}", fontsize=6, va="center", ha="left", color="#444444")
bx.set_yticks(ys)
bx.set_yticklabels([])
bx.set_xlim(0, 1.0)
bx.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
bx.set_xlabel("Blocks $\\mid$ names $\\geq$1 AI agent", fontsize=7.5)
bx.text(1.035, len(langs) + 0.45, "$n$", fontsize=6.5, va="center", ha="left", color="#444444")
bx.set_title("(b) Conditional on naming", fontsize=7.5, loc="left", pad=3)

for axis in (ax, bx):
    axis.set_ylim(0.3, len(langs) + 0.7)
    axis.tick_params(axis="x", labelsize=7)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0)
    axis.xaxis.grid(True, color="#dddddd", lw=0.5, zorder=0)
    axis.set_axisbelow(True)
    axis.axhline(len(langs) - 4 + 0.5, color="#bbbbbb", lw=0.5, ls=":")
    axis.axhline(len(langs) - 9 + 0.5, color="#bbbbbb", lw=0.5, ls=":")

fig.tight_layout(pad=0.3)
out = os.path.join(ROOT, "figures", "fig_gradient_v2.pdf")
fig.savefig(out, bbox_inches="tight")
print("saved", out)
