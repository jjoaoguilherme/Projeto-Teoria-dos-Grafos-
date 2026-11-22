"""Figuras e empacotamento da interface a partir de resultados exportados."""
from pathlib import Path
import json
import re


def gerar_figuras(pasta, mapas):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from .graphs.algorithms import BFS
    pasta=Path(pasta)

    def base(nome):
        matriz=mapas[nome]['matriz']
        fig,ax=plt.subplots(figsize=(14,7))
        ax.imshow([[0 if c=='#' else 1 for c in row] for row in matriz],cmap='gray',vmin=0,vmax=1)
        for i,row in enumerate(matriz):
            for j,c in enumerate(row):
                if c not in '#.':ax.text(j,i,c,ha='center',va='center',fontsize=7)
        ax.set_xlabel('Coluna');ax.set_ylabel('Linha')
        return fig,ax

    for nome in ['m03_tres_chaves','m08_grande']:
        r=json.loads((pasta/f'resultado_{nome}.json').read_text(encoding='utf-8'))
        fig,ax=base(nome);percurso=r['percurso'];labels={}
        for a,b in zip(percurso,percurso[1:]):
            layer=''.join(b['chaves']) or '-';color=plt.cm.viridis(len(b['chaves'])/4)
            ax.plot([a['posicao'][1],b['posicao'][1]],[a['posicao'][0],b['posicao'][0]],color=color,lw=2)
            labels[layer]=color
        ax.legend(handles=[Patch(color=c,label='Chaves: '+l) for l,c in labels.items()],loc='upper left',bbox_to_anchor=(1,1))
        ax.set_title('Percurso de menor custo - '+nome);fig.tight_layout();fig.savefig(pasta/f'percurso_{nome[:3]}.png',dpi=160);plt.close(fig)
    nome='m08_grande';fig,ax=base(nome)
    m=json.loads((pasta/'metricas_global.json').read_text(encoding='utf-8'))[nome]
    matriz=mapas[nome]['matriz'];z=[[float('nan')]*len(matriz[0]) for _ in matriz]
    for casa in m['multiplicidade']['por_casa']:
        i,j=casa['posicao'];z[i][j]=casa['multiplicidade']
    im=ax.imshow(z,cmap='viridis');fig.colorbar(im,ax=ax,label='Número de estados por casa')
    ax.set_title('Multiplicidade de estados - m08');fig.tight_layout();fig.savefig(pasta/'heatmap_m08.png',dpi=160);plt.close(fig)

    d=mapas['m02_uma_chave']['dados'];est=d['estados']
    fig,ax=plt.subplots(figsize=(14,8));coords={}
    for r,(pos,chaves,_) in est.items():coords[r]=(pos[1]+(14 if chaves else 0),-pos[0])
    for u,v,_ in d['arestas']:
        if u not in est or v not in est:continue
        diferente=est[u][1]!=est[v][1]
        ax.annotate('',xy=coords[v],xytext=coords[u],arrowprops={'arrowstyle':'->','color':'crimson' if diferente else 'gray','alpha':.6,'lw':1})
    for r,xy in coords.items():
        ax.scatter(*xy,color='teal' if est[r][1] else 'gold',s=65);ax.annotate(r,xy,xytext=(0,8),textcoords='offset points',fontsize=5,rotation=40)
    ax.legend(handles=[Patch(color='gold',label='Sem chaves'),Patch(color='teal',label='Chave a'),Patch(color='crimson',label='Mudança de camada')]);ax.set_title('Grafo de estados m02 em camadas');ax.set_xlabel('Coluna e deslocamento por camada');ax.set_ylabel('Linha invertida');ax.margins(.1,.4);fig.tight_layout();fig.savefig(pasta/'camadas_m02.png',dpi=180);plt.close(fig)
    r=BFS(d['vertices'],d['arestas'],d['inicio']);levels={}
    for v,n in r['distancias'].items():
        if v!='ALVO' and n!=float('inf'):levels.setdefault(n,[]).append(v)
    coords={v:(i-(len(vs)-1)/2,-n) for n,vs in levels.items() for i,v in enumerate(vs)}
    fig,ax=plt.subplots(figsize=(11,16))
    for v,xy in coords.items():
        pai=r['predecessores'][v]
        if pai in coords:ax.plot([coords[pai][0],xy[0]],[coords[pai][1],xy[1]],color='gray')
        ax.scatter(*xy,color='teal');ax.annotate(v,xy,xytext=(5,2),textcoords='offset points',fontsize=6)
    ax.set_yticks([-n for n in sorted(levels)],labels=[str(n) for n in sorted(levels)]);ax.set_xlabel('Posição no nível');ax.set_ylabel('Nível BFS');ax.set_title('Árvore BFS de estados - m02');ax.legend(handles=[Patch(color='teal',label='Estado alcançado')]);ax.margins(x=.6);fig.tight_layout();fig.savefig(pasta/'arvore_bfs_m02.png',dpi=160);plt.close(fig)


def atualizar_html(pasta, mapas, modelo):
    pasta=Path(pasta);modelo=Path(modelo)
    html=modelo.read_text(encoding='utf-8')
    def dado(nome,obj):
        nonlocal html
        html=re.sub(r'^const '+nome+r'=.*?;$',lambda _: 'const '+nome+'='+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';',html,flags=re.M)
    dado('bundled',{nome:[''.join(l) for l in m['matriz']] for nome,m in mapas.items()})
    dado('embeddedReports',[json.loads(p.read_text(encoding='utf-8')) for p in sorted(pasta.glob('resultado_*.json'))])
    dado('embeddedMetrics',json.loads((pasta/'metricas_global.json').read_text(encoding='utf-8')))
    overlay={nome:[{'estado':r,'posicao':list(e[0]),'chaves':''.join(sorted(e[1])) or '-', 'armadilha':r in set(m['armadilhas'])} for r,e in m['dados']['estados'].items()] for nome,m in mapas.items()}
    if 'const stateOverlay=' in html:html=re.sub(r'^const stateOverlay=.*?;$',lambda _: 'const stateOverlay='+json.dumps(overlay,ensure_ascii=False,separators=(',',':'))+';',html,flags=re.M)
    else:
        html=html.replace("'use strict';","'use strict';\nconst stateOverlay="+json.dumps(overlay,ensure_ascii=False,separators=(',',':'))+';',1)
        html=html.replace('<div class="canvas"', '<div class="controls"><label>Camada de chaves <select id="layer"><option value="*">Todas</option></select></label><label><input id="traps" type="checkbox" checked> Destacar armadilhas</label></div><div class="canvas"',1)
        html=html.replace('function render(){','function renderOriginal(){',1)
        extra="""
function render(){
 renderOriginal();
 const states=stateOverlay[currentMap]||[],layer=document.getElementById('layer').value;
 const counts=new Map();
 for(const s of states){if(layer!=='*'&&s.chaves!==layer)continue;const k=s.posicao.join(',');const c=counts.get(k)||{total:0,traps:0};c.total++;if(s.armadilha)c.traps++;counts.set(k,c)}
 for(const cell of document.getElementById('maze').children){
  const c=counts.get(cell.dataset.pos);cell.style.opacity=layer==='*'||c?'1':'.25';
  cell.style.outline=document.getElementById('traps').checked&&c?.traps?'2px solid #ff6278':'';
  cell.title=cell.dataset.pos+' | Estados nesta camada: '+(c?.total||0)+' | Armadilhas: '+(c?.traps||0);
 }
}
function fillLayers(){const sel=document.getElementById('layer');sel.innerHTML='<option value="*">Todas</option>';for(const name of [...new Set((stateOverlay[currentMap]||[]).map(s=>s.chaves))].sort()){const o=document.createElement('option');o.value=name;o.textContent=name==='-'?'Sem chaves':name;sel.append(o)}}
document.getElementById('map').addEventListener('change',()=>{fillLayers();render()});
document.getElementById('layer').addEventListener('change',render);
document.getElementById('traps').addEventListener('change',render);
fillLayers();render();
"""
        html=html.replace('</script></body>',extra+'</script></body>',1)
    (pasta/'labirinto_interativo.html').write_text(html,encoding='utf-8')
