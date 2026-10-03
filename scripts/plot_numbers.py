"""Render README benchmark figures from audited aggregate measurements."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
pruned = json.loads((ROOT/'eval/pruned/audit/current.json').read_text())
follow = json.loads((ROOT/'eval/random-followup/results/collection.json').read_text())
assert not pruned['source_errors'] and not follow['source_errors']
stages = [('Development',pruned['stages']['dev']),('Held-out diagnostics',pruned['stages']['heldout']),('Repository subset',pruned['stages']['real_swe']),('Random easy subset',follow['stages']['real_swe'])]
arms = ['baseline','latest','karpathy','karpathy_latest']
labels = ['No skill','SoL-Pi (ours)','Karpathy','Both skills']
colors = ['#64748b','#0284c7','#d97706','#8b5cf6']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig, axes = plt.subplots(3,4,figsize=(16,10))
for col,(title,stage) in enumerate(stages):
    assert stage['complete']
    ms=[stage['arms'][a] for a in arms]
    for row in range(3):
        ax=axes[row,col];ax.set_axisbelow(True);ax.grid(axis='y',alpha=.15);ax.set_xticks([])
    ax=axes[0,col];ax.set_title(title,fontweight='bold',pad=15)
    bars=ax.bar(np.arange(4),[m['solved']/m['n']*100 for m in ms],color=colors,width=.65)
    ax.set_ylim(0,118);ax.set_yticks([0,50,100],['0%','50%','100%'])
    for b,m in zip(bars,ms):ax.text(b.get_x()+b.get_width()/2,b.get_height()+3,f"{m['solved']}/{m['n']}",ha='center',fontweight='bold')
    ax=axes[1,col];vals=[m['tokens_per_solve']/1e6 for m in ms];bars=ax.bar(np.arange(4),vals,color=colors,width=.65);ax.set_ylim(0,max(vals)*1.30)
    for b,m,v in zip(bars,ms,vals):
        if not m['usage_complete']:b.set_hatch('///');b.set_edgecolor('#334155')
        label=('≥' if not m['usage_complete'] else '')+(f'{v:.2f}M' if v>=1 else f'{v*1000:.0f}k')
        ax.text(b.get_x()+b.get_width()/2,v+max(vals)*.035,label,ha='center',fontsize=10)
    ax=axes[2,col];vals=[m['timeouts'] for m in ms];bars=ax.bar(np.arange(4),vals,color=colors,width=.65);ax.set_ylim(0,3.7);ax.set_yticks([0,1,2,3])
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.12,str(v),ha='center')
    ax.set_xticks(range(4),['No skill','Ours','Karpathy','Both'],rotation=25,ha='right')
axes[0,0].set_ylabel('Verified solve rate ↑')
axes[1,0].set_ylabel('Tokens / solve, millions ↓')
axes[2,0].set_ylabel('Model timeouts ↓')
fig.subplots_adjust(left=.065, right=.99, top=.90, bottom=.20, hspace=.18, wspace=.24)
fig.suptitle('Distilled SoL-Pi · audited benchmark numbers',fontsize=21,fontweight='bold')
fig.legend(handles=[Patch(facecolor=c,label=l) for c,l in zip(colors,labels)]+[Patch(facecolor='white',edgecolor='#334155',hatch='///',label='Incomplete cost: lower bound')],loc='lower center',bbox_to_anchor=(.5,.07),ncol=5,frameon=False)
fig.supxlabel('Qwen3.8-27B-FP8 · Claude Code 2.1.286\nToken-axis scales differ by benchmark. Costs include failures; hatched bars cannot establish a cost ranking.\nSmall task subsets and public repair retrieval limit generalization and unaided attribution.',fontsize=10,y=.015)
(ROOT/'assets').mkdir(exist_ok=True)
fig.savefig(ROOT/'assets/benchmark-numbers.svg',bbox_inches='tight')
fig.savefig(ROOT/'assets/benchmark-numbers.png',dpi=160,bbox_inches='tight')
plt.close(fig)
print('Generated SVG and PNG from audited measurements.')
