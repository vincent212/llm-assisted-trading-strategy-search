import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Arc, FancyArrowPatch, Polygon, FancyBboxPatch

BG='#eef1f5'; INK='#1f2d3d'; MUT='#5b6675'
SKIN='#e7c6a5'; SKINL='#c99f79'; EYE='#26303b'
WIG='#b7b2a6'; WIGL='#948f83'; COAT='#3a4a63'; COATL='#28374d'; APPLE='#c0483f'; LEAF='#5a7d5a'
HAIR='#dfe4ea'; HAIRL='#c0c7d0'; SWEAT='#5f7085'; SWEATL='#48566a'; ACC='#c8862c'

fig, ax = plt.subplots(figsize=(12,8.4)); fig.patch.set_facecolor(BG)
ax.set_facecolor(BG); ax.set_xlim(0,100); ax.set_ylim(0,86); ax.axis('off')

# ---------- title ----------
ax.text(50,82,"Einstein vs Newton", ha='center', fontsize=25, fontweight='bold', color=INK)
ax.text(50,76.3,"Why LLMs Cannot Invent New Alpha", ha='center', fontsize=15, color=MUT)

def eyes(cx,cy,dx=2.4):
    for s in (-1,1): ax.add_patch(Circle((cx+s*dx,cy+0.6),0.85,color=EYE,zorder=7))
def smile(cx,cy,w=3.0):
    ax.add_patch(Arc((cx,cy-1.4),w,2.2,theta1=205,theta2=335,color=EYE,lw=1.8,zorder=7))

# ---------- NEWTON ----------
nx,ny=27,40
for a in np.linspace(120,240,7):
    x=nx+9.2*np.cos(np.radians(a)); y=ny+9.2*np.sin(np.radians(a))
    ax.add_patch(Circle((x,y),2.8,color=WIG,ec=WIGL,lw=1,zorder=2))
for yy in range(0,4):
    ax.add_patch(Circle((nx-8.5,ny-2-yy*3),2.6,color=WIG,ec=WIGL,lw=1,zorder=2))
    ax.add_patch(Circle((nx+8.5,ny-2-yy*3),2.6,color=WIG,ec=WIGL,lw=1,zorder=2))
ax.add_patch(Ellipse((nx,ny+7.5),12,7,color=WIG,ec=WIGL,lw=1,zorder=2))
ax.add_patch(FancyBboxPatch((nx-8,ny-20),16,13,boxstyle="round,pad=0.3,rounding_size=2",fc=COAT,ec=COATL,lw=1.5,zorder=3))
ax.add_patch(Polygon([[nx,ny-7.5],[nx-3,ny-16],[nx+3,ny-16]],closed=True,fc='#e9edf2',ec=COATL,zorder=4))
ax.add_patch(Circle((nx,ny),7,color=SKIN,ec=SKINL,lw=1.2,zorder=5))
eyes(nx,ny); smile(nx,ny); ax.add_patch(Circle((nx,ny-0.4),0.5,color=SKINL,zorder=7))
ax.add_patch(Circle((nx,ny+20),3.0,color=APPLE,ec='#8f342e',lw=1,zorder=6))
ax.add_patch(Ellipse((nx+1.6,ny+22.4),2.0,1.0,angle=35,color=LEAF,zorder=7))
ax.plot([nx,nx],[ny+13,ny+16.5],color=MUT,lw=1,ls=(0,(2,2)),zorder=5)
ax.text(nx,ny-24.5,"NEWTON",ha='center',fontsize=16,fontweight='bold',color=INK)
ax.text(nx,ny-28.8,"searches within the given framework",ha='center',fontsize=11.5,color=MUT,style='italic')

# ---------- EINSTEIN ----------
ex,ey=73,40
rng=np.random.default_rng(3)
for a in np.linspace(30,330,16):
    r=9.5+rng.uniform(-0.5,1.8); x=ex+r*np.cos(np.radians(a)); y=ey+r*np.sin(np.radians(a))
    if y>ey-6: ax.add_patch(Circle((x,y),rng.uniform(2.2,3.4),color=HAIR,ec=HAIRL,lw=1,zorder=2))
ax.add_patch(Ellipse((ex,ey+8),15,8,color=HAIR,ec=HAIRL,lw=1,zorder=2))
ax.add_patch(FancyBboxPatch((ex-8,ey-20),16,13,boxstyle="round,pad=0.3,rounding_size=2",fc=SWEAT,ec=SWEATL,lw=1.5,zorder=3))
ax.add_patch(Circle((ex,ey),7,color=SKIN,ec=SKINL,lw=1.2,zorder=5))
eyes(ex,ey); ax.add_patch(Circle((ex,ey-0.4),0.5,color=SKINL,zorder=7))
ax.add_patch(Ellipse((ex-1.7,ey-2.2),2.6,1.4,color=HAIR,ec=HAIRL,lw=0.8,zorder=8))
ax.add_patch(Ellipse((ex+1.7,ey-2.2),2.6,1.4,color=HAIR,ec=HAIRL,lw=0.8,zorder=8))
smile(ex,ey,w=2.4)
ax.add_patch(FancyBboxPatch((ex+6,ey+6),15,7,boxstyle="round,pad=0.3,rounding_size=1.5",fc='white',ec=INK,lw=1.4,zorder=9))
ax.text(ex+13.5,ey+9.5,"E=mc²",ha='center',va='center',fontsize=12,fontweight='bold',color=INK,zorder=10)
ax.text(ex,ey-24.5,"EINSTEIN",ha='center',fontsize=16,fontweight='bold',color=INK)
ax.text(ex,ey-28.8,"invents a new framework",ha='center',fontsize=11.5,color=MUT,style='italic')

# ---------- the jump ----------
ax.add_patch(FancyArrowPatch((39,54),(61,54), connectionstyle="arc3,rad=-0.45",
    arrowstyle='-|>', mutation_scale=28, lw=3, color=ACC, ls=(0,(6,3)), zorder=4))
ax.text(50,62.5,"the jump", ha='center', fontsize=14, color=ACC, style='italic', fontweight='bold')
ax.text(50,4,"An LLM searches Newton's world brilliantly — it cannot make the jump to Einstein's.",
    ha='center', fontsize=16, color=INK)
plt.savefig('einstein_newton.png', dpi=200, bbox_inches='tight', facecolor=BG)
print("saved")
