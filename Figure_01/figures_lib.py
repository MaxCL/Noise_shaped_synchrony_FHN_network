
import numpy as np,matplotlib.pyplot as plt,glob,os
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle,FancyArrowPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

A=0.7;I=0.0;NULL_ALPHA=0.5
UMIN,UMAX=-2.5,2.0;N_SAMPLES=800;LINE_WIDTH=1.0;_DASH=(1.5,3.0,6.0,3.0)

LC_PATH='limit_cycle_sample.csv';LC_ALPHA=0.5;LC_COLOR='0.35';LC_LINEWIDTH=1.0;LC_STYLE='--'

ARROW_BODY_SCALE=1.0;ARROW_HEAD_SCALE=14.0;ARROW_LW=1.6;ARROW_ALPHA=0.95;ARROW_Z=6

NODES=50;ITERATIONS=505000;P=10;ALPHA=0.99

def _circulant_window_vec(N,i_1based,P):
    v=np.zeros(N);idx=(np.arange(i_1based-1-P,i_1based+P)%N);v[idx]=1;return v

def Cu_at(u,node,idx,P_=P):
    row=u[idx];vec=_circulant_window_vec(u.shape[1],node+1,P_);return np.dot(row-row[node],vec)

def Cv_at(v,node,idx,P_=P):
    row=v[idx];vec=_circulant_window_vec(v.shape[1],node+1,P_);return np.dot(row-row[node],vec)

def plot_fhn_nullclines(ax):
    u=np.linspace(UMIN,UMAX,N_SAMPLES);v=u-(u**3)/3.0+I
    ax.plot(u,v,color='black',lw=LINE_WIDTH,ls=(0,_DASH),alpha=NULL_ALPHA)
    ax.axvline(-ALPHA,color='black',lw=LINE_WIDTH,ls=':',alpha=NULL_ALPHA)

def plot_limit_cycle(ax,csv_path=LC_PATH):
    lc=np.genfromtxt(csv_path,delimiter=',',dtype=float)
    ax.plot(lc[:,0],lc[:,1],LC_STYLE,lw=LC_LINEWIDTH,alpha=LC_ALPHA,color=LC_COLOR)

def make_cmap():
    return LinearSegmentedColormap.from_list('cmap',[(0,'blue'),(0.45,'white'),(0.55,'white'),(1,'red')])

def add_spacetime_inset(ax,u,ia,ib,node,ia_core=None,ib_core=None,nodes=50,rect_color='green',rect_alpha=0.9,rect_lw=1.8,width='80%',height='25%',loc='upper right'):
    d=u.T;iaw,ibw=int(ia),int(ib);data=d[:,iaw:ibw+1]
    cmap=make_cmap()
    ins=inset_axes(ax,width=width,height=height,loc=loc,borderpad=0.5)
    ext=(iaw,ibw+1,0,nodes-1)
    ins.imshow(data,origin='lower',aspect='auto',cmap=cmap,vmin=-3.0,vmax=1.5,extent=ext,interpolation='none')
    ins.set_xlim(iaw,ibw+1);ins.set_ylim(0,nodes-1)
    ia_core=ia_core if ia_core is not None else iaw
    ib_core=ib_core if ib_core is not None else ibw
    ins.set_xticks([ia_core,ib_core+1]);ins.set_xticklabels([r"$t_0$",r"$t_1$"],fontsize=18)
    ins.set_yticks([0,nodes-1]);ins.set_yticklabels([1,nodes],fontsize=14)
    y0=node-0.5
    rect=Rectangle((ia_core,y0),(ib_core+1-ia_core),1.0,fill=False,edgecolor=rect_color,linewidth=rect_lw,alpha=rect_alpha)
    ins.add_patch(rect)
    return ins

def plot_node_vectors(ax,x,y,vecs,colors):
    for (vx,vy),c in zip(vecs,colors):
        end=(x+ARROW_BODY_SCALE*vx,y+ARROW_BODY_SCALE*vy)
        arr=FancyArrowPatch((x,y),end,arrowstyle='->',mutation_scale=ARROW_HEAD_SCALE,lw=ARROW_LW,color=c,alpha=ARROW_ALPHA)
        arr.set_zorder(ARROW_Z);ax.add_patch(arr)

_NOISE_CACHE=None
def _load_noise_parts(globpat='clean_noise_subset.part*.csv'):
    global _NOISE_CACHE
    if _NOISE_CACHE is not None:return _NOISE_CACHE
    files=sorted(glob.glob(globpat))
    if not files: raise FileNotFoundError('No noise CSV parts found')
    idxs=[];blocks=[]
    for p in files:
        a=np.loadtxt(p,delimiter=',',skiprows=1)
        if a.ndim==1: a=a[None,:]
        idxs.append(a[:,0].astype(int))
        blocks.append(a[:,2:])
    idxs=np.concatenate(idxs);noise=np.vstack(blocks)
    _NOISE_CACHE=(idxs,noise);return _NOISE_CACHE

def noise_at(node,abs_idx):
    idxs,noise=_load_noise_parts()
    if abs_idx<=idxs[0]: i=0
    elif abs_idx>=idxs[-1]: i=-1
    else: i=min(np.searchsorted(idxs,abs_idx),len(idxs)-1)
    return float(noise[i,node])
