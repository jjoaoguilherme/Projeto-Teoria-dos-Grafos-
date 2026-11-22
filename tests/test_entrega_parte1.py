from pathlib import Path
import json
from src.main import resolver_mapa
from src.graphs.analises import estados_armadilha
from src.graphs.io import ler_mapa


def test_mapas_proprios_cumprem_requisitos():
    base=Path(__file__).resolve().parents[1]/'data/mapas_grupo'
    r,_=resolver_mapa(base/'mapa1.txt');m,_,_=ler_mapa(base/'mapa1.txt')
    tiles=[m[x['posicao'][0]][x['posicao'][1]] for x in r['percurso']]
    assert r['status']=='OK'
    assert '+' in tiles and any(x in '><^v' for x in tiles)
    assert len(set(''.join(''.join(l) for l in m))&set('abcd'))>=3
    _,d=resolver_mapa(base/'mapa2.txt')
    assert len(estados_armadilha(d))/len(d['estados'])>=.2


def test_arquivos_obrigatorios():
    pasta=Path(__file__).resolve().parents[1]/'out/parte1'
    for name in ['camadas.json','metricas_global.json','comparacao_modelagem.csv','solucoes.csv',
                 'dfs_classificacao.csv','percurso_m03.json','ciclo_negativo_m06.json',
                 'armadilhas_m04.csv','armadilhas_m07.csv','percurso_m03.png','percurso_m08.png',
                 'camadas_m02.png','arvore_bfs_m02.png','heatmap_m08.png','labirinto_interativo.html']:
        assert (pasta/name).stat().st_size>0,name
    assert json.loads((pasta/'comparacao_bonus_m05.json').read_text(encoding='utf-8'))['G_pos']['custo_ciclo']<0
