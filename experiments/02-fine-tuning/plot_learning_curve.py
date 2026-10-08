"""Experiment 02: learning curve for Ettin-32M (mean field score on the 600 test excerpts vs training excerpts).
Scores from the sweep 2 runs' metrics.json; writes results/learning_curve.png.

Usage: uv run --with matplotlib plot_learning_curve.py
"""

import matplotlib.pyplot as plt

RANDOM = [(1000, 66.2), (2500, 72.6), (5000, 75.6), (10000, 77.0)]  # random sample only
FULL = (28664, 80.4)  # random 10,000 + balanced 18,664
INK, MUTED, SERIES, SURFACE = "#0b0b0b", "#52514e", "#2a78d6", "#fcfcfb"

fig, ax = plt.subplots(figsize=(7, 4.2), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
ax.plot(*zip(*RANDOM), color=SERIES, lw=2, marker="o", ms=8, mec=SURFACE, mew=2, label="random excerpts")
ax.plot(*FULL, marker="D", ms=8, color=SERIES, mfc=SURFACE, mew=2, linestyle="none", label="+ balanced rare-label excerpts")
for x, y in RANDOM + [FULL]:
    ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, color=INK)
for y, text in ((88.8, "LLM vs LLM 88.8"), (72.5, "Jev zero-shot 72.5")):
    ax.axhline(y, color=MUTED, lw=1, ls="--")
    ax.text(1000, y + 0.6, text, fontsize=9, color=MUTED)
ax.set_xscale("log")
ax.set_xticks([1000, 2500, 5000, 10000, 28664], ["1,000", "2,500", "5,000", "10,000", "28,664"])
ax.minorticks_off()
ax.set_ylim(60, 92)
ax.set_xlabel("Training excerpts (log scale)", color=MUTED)
ax.set_ylabel("Mean field score, test (600 excerpts)", color=MUTED)
ax.set_title("Ettin-32M: score vs training data", loc="left", color=INK, fontsize=12)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color("#cccccc")
ax.tick_params(colors=MUTED)
ax.grid(axis="y", color="#e6e6e3", lw=0.8)
ax.legend(frameon=False, loc="lower right", labelcolor=INK)
fig.tight_layout()
fig.savefig("results/learning_curve.png", dpi=160)
