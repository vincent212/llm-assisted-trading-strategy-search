import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BG='#0e1116'; TEXT='#e6edf3'; SUB='#b9c2cc'
BLUE='#4c8bf5'; BLUEF='#152238'; GOLD='#e0a33e'; PUR='#c07be0'; PURF='#241a2b'; DIM='#8b949e'

fig, ax = plt.subplots(figsize=(12, 6.4)); fig.patch.set_facecolor(BG)
ax.set_facecolor(BG); ax.set_xlim(0,100); ax.set_ylim(0,56); ax.axis('off')

# title
ax.text(50,52.5,"Search  vs.  the Jump", ha='center', va='center', fontsize=23, fontweight='bold', color=TEXT)

# ---- left box: the given hypothesis space (search) ----
ax.add_patch(FancyBboxPatch((5,13),37,29, boxstyle="round,pad=0.4,rounding_size=1.2",
    linewidth=2.2, edgecolor=BLUE, facecolor=BLUEF))
rng=np.random.default_rng(7)
xs=rng.uniform(9,38,220); ys=rng.uniform(16.5,36,220)
ax.scatter(xs,ys,s=12,color=BLUE,alpha=0.55,edgecolors='none')
ax.text(23.5,39.2,"the given hypothesis space", ha='center', va='center', fontsize=12.5, fontweight='bold', color=TEXT)
ax.text(23.5,10.0,"Newton's framework", ha='center', va='center', fontsize=12, color=SUB, style='italic')
ax.text(23.5,14.6,"LLM searches here — millions of candidates,\nall inside the space it was given", ha='center', va='center', fontsize=9.5, color=SUB)

# ---- right box: a new hypothesis space ----
ax.add_patch(FancyBboxPatch((62,13),33,29, boxstyle="round,pad=0.4,rounding_size=1.2",
    linewidth=2.2, edgecolor=PUR, facecolor=PURF))
ax.scatter([78.5],[27.5], s=1400, marker='*', color=GOLD, edgecolors='white', linewidths=0.6, zorder=5)
ax.text(78.5,21.0,"genuinely new alpha", ha='center', va='center', fontsize=10, color=GOLD)
ax.text(78.5,39.2,"a new hypothesis space", ha='center', va='center', fontsize=12.5, fontweight='bold', color=TEXT)
ax.text(78.5,10.0,"Einstein's framework", ha='center', va='center', fontsize=12, color=SUB, style='italic')

# ---- the jump ----
ax.add_patch(FancyArrowPatch((42.5,30),(61.5,28), connectionstyle="arc3,rad=-0.32",
    arrowstyle='-|>', mutation_scale=32, linewidth=3.0, color=GOLD, linestyle=(0,(6,3)), zorder=6))
ax.text(52,41.5,"THE  JUMP", ha='center', va='center', fontsize=15, fontweight='bold', color=GOLD)
ax.text(52,37.6,"(abduction — what LLMs can't do)", ha='center', va='center', fontsize=10.5, color=DIM, style='italic')

# subtitle
ax.text(50,3.2,"LLMs search brilliantly inside a given space. Inventing new alpha needs the jump to a new one.",
    ha='center', va='center', fontsize=11.5, color=SUB)

plt.savefig('jump_graphic.png', dpi=200, bbox_inches='tight', facecolor=BG)
print("saved jump_graphic.png")
