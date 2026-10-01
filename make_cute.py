import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Arc, FancyArrowPatch, Polygon, FancyBboxPatch

BG='#fdf4e3'; SKIN='#f4d0ac'; SKINL='#d9a97f'; EYE='#2b2b2b'; CHEEK='#f2a29b'
WIG='#cbb89c'; WIGL='#a8977c'; COAT='#8b3a4a'; APPLE='#e0473f'; LEAF='#5aa469'
HAIR='#f2f2f2'; HAIRL='#cfcfcf'; SWEAT='#7d8794'; GOLD='#e0a33e'; INK='#3a2f1f'

fig, ax = plt.subplots(figsize=(11,7)); fig.patch.set_facecolor(BG)
ax.set_facecolor(BG); ax.set_xlim(0,100); ax.set_ylim(0,72); ax.axis('off')

def cheeks(cx,cy):
    ax.add_patch(Circle((cx-3.6,cy-1.6),1.5,color=CHEEK,alpha=.7,zorder=6))
    ax.add_patch(Circle((cx+3.6,cy-1.6),1.5,color=CHEEK,alpha=.7,zorder=6))
def eyes(cx,cy,dx=2.4):
    for s in (-1,1):
        ax.add_patch(Circle((cx+s*dx,cy+0.6),0.95,color=EYE,zorder=7))
        ax.add_patch(Circle((cx+s*dx+0.3,cy+0.95),0.32,color='white',zorder=8))
def smile(cx,cy,w=3.2,tongue=False):
    ax.add_patch(Arc((cx,cy-1.6),w,2.6,theta1=200,theta2=340,color=EYE,lw=2,zorder=7))
    if tongue: ax.add_patch(Ellipse((cx,cy-2.7),1.6,1.2,color='#e8817e',zorder=8))

# ---------- NEWTON (left) ----------
nx,ny=28,40
# wig: curls framing the face
for a in np.linspace(120,240,7):
    x=nx+9.2*np.cos(np.radians(a)); y=ny+9.2*np.sin(np.radians(a))
    ax.add_patch(Circle((x,y),2.8,color=WIG,ec=WIGL,lw=1,zorder=2))
for i,yy in enumerate(range(0,4)):
    ax.add_patch(Circle((nx-8.5,ny-2-yy*3),2.6,color=WIG,ec=WIGL,lw=1,zorder=2))
    ax.add_patch(Circle((nx+8.5,ny-2-yy*3),2.6,color=WIG,ec=WIGL,lw=1,zorder=2))
ax.add_patch(Ellipse((nx,ny+7.5),12,7,color=WIG,ec=WIGL,lw=1,zorder=2))  # top
# coat
ax.add_patch(FancyBboxPatch((nx-8,ny-20),16,13,boxstyle="round,pad=0.3,rounding_size=2",
    fc=COAT,ec='#5f2732',lw=1.5,zorder=3))
ax.add_patch(Polygon([[nx,ny-7.5],[nx-3,ny-16],[nx+3,ny-16]],closed=True,fc='#f5ead3',ec='#5f2732',zorder=4)) # cravat
# head
ax.add_patch(Circle((nx,ny),7,color=SKIN,ec=SKINL,lw=1.2,zorder=5))
eyes(nx,ny); cheeks(nx,ny); smile(nx,ny)
ax.add_patch(Circle((nx,ny-0.4),0.5,color=SKINL,zorder=7))  # nose
# apple falling
ax.add_patch(Circle((nx,ny+20),3.1,color=APPLE,ec='#a82f28',lw=1,zorder=6))
ax.add_patch(Ellipse((nx+1.6,ny+22.6),2.2,1.1,angle=35,color=LEAF,zorder=7))
ax.plot([nx,nx],[ny+13,ny+16.5],color=INK,lw=1,ls=(0,(2,2)),zorder=5)
ax.text(nx,ny-24,"Newton",ha='center',fontsize=15,fontweight='bold',color=INK)

# ---------- EINSTEIN (right) ----------
ex,ey=72,40
# wild hair
rng=np.random.default_rng(3)
for a in np.linspace(30,330,16):
    r=9.5+rng.uniform(-0.5,1.8)
    x=ex+r*np.cos(np.radians(a)); y=ey+r*np.sin(np.radians(a))
    if y>ey-6:
        ax.add_patch(Circle((x,y),rng.uniform(2.2,3.4),color=HAIR,ec=HAIRL,lw=1,zorder=2))
ax.add_patch(Ellipse((ex,ey+8),15,8,color=HAIR,ec=HAIRL,lw=1,zorder=2))
# sweater
ax.add_patch(FancyBboxPatch((ex-8,ey-20),16,13,boxstyle="round,pad=0.3,rounding_size=2",
    fc=SWEAT,ec='#565f6b',lw=1.5,zorder=3))
# head
ax.add_patch(Circle((ex,ey),7,color=SKIN,ec=SKINL,lw=1.2,zorder=5))
eyes(ex,ey); cheeks(ex,ey)
ax.add_patch(Circle((ex,ey-0.4),0.5,color=SKINL,zorder=7))
# bushy mustache
ax.add_patch(Ellipse((ex-1.7,ny-2.2),2.6,1.5,color=HAIR,ec=HAIRL,lw=0.8,zorder=8))
ax.add_patch(Ellipse((ex+1.7,ny-2.2),2.6,1.5,color=HAIR,ec=HAIRL,lw=0.8,zorder=8))
smile(ex,ey,w=2.6)
# E=mc2 bubble
ax.add_patch(FancyBboxPatch((ex+6,ey+6),15,7,boxstyle="round,pad=0.3,rounding_size=1.5",
    fc='white',ec=INK,lw=1.4,zorder=9))
ax.text(ex+13.5,ey+9.5,"E=mc²",ha='center',va='center',fontsize=12,fontweight='bold',color=INK,zorder=10)
ax.text(ex,ey-24,"Einstein",ha='center',fontsize=15,fontweight='bold',color=INK)

# ---------- the jump ----------
ax.add_patch(FancyArrowPatch((39,54),(61,54), connectionstyle="arc3,rad=-0.45",
    arrowstyle='-|>', mutation_scale=28, lw=3, color=GOLD, ls=(0,(6,3)), zorder=4))
ax.text(50,66,"the jump!", ha='center', fontsize=20, fontweight='bold', color=GOLD, style='italic')
ax.text(50,6,"An LLM can search Newton's world brilliantly. It can't make the jump to Einstein's.",
    ha='center', fontsize=11.5, color=INK)

plt.savefig('einstein_newton_cute.png', dpi=200, bbox_inches='tight', facecolor=BG)
print("saved")
