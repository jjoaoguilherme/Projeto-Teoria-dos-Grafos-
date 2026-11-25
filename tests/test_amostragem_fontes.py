"""[IA] ChatGPT – desenho amostral e integração de resultados reais das funções."""
import json
from pathlib import Path
import pandas as pd
import pytest
from src.graphs.algorithms import BFS
from src.parte2.amostragem_fontes import (planejar, registrar_papeis, resumir_bfs,
                                         estimar_media_alcance, limite_variancia)
from src.parte2 import estudo_global as eg


def cadastro():
    graus=[0]*10380+[1]*24674+[2]*15570+[11]*3178+[101]*273
    return pd.DataFrame({'vizinhos_saida':graus},index=[f'c{i:05}' for i in range(len(graus))])


def test_dimensionamento_e_probabilidades():
    m=cadastro();p=planejar(m)
    assert [h['n_h'] for h in p['estratos']]==[0,122,96,94,72]
    assert p['n_amostra']==384
    assert p['margem_global_planejada_normal']<=.05
    assert all(h['margem_planejada_normal']<=.1 for h in p['estratos'])
    for r in p['amostra']:
        assert r['probabilidade_inclusao']==r['n_h']/r['N_h']
        assert r['peso_amostral']==r['N_h']/r['n_h']
    assert sum(r['peso_amostral'] for r in p['amostra'])==pytest.approx(len(m)-10380)


def test_reprodutibilidade_independente_ordem_e_semente():
    m=cadastro();p=planejar(m)
    assert p==planejar(m.iloc[::-1])
    assert p['amostra']!=planejar(m,semente=43)['amostra']
    assert len({r['origem'] for r in p['amostra']})==384


def test_papeis_sobrepostos_sem_inflar_amostra():
    m=cadastro();p=planejar(m);u=p['amostra'][0]['origem']
    r=registrar_papeis(p,m,[u,'c00000'],[(u,'c00001'),(u,'c00002')])
    item=next(x for x in r if x['origem']==u)
    assert set(item['finalidades'])=={'amostra_analitica','bfs_dfs_obrigatoria','par_dijkstra'}
    assert len(r)==385 and sum(x['amostra_analitica'] for x in r)==384
    assert next(x for x in r if x['origem']=='c00000')['probabilidade_inclusao'] is None


def test_estratos_pequenos_censitarios_e_precisao():
    m=pd.DataFrame({'vizinhos_saida':[0,1,2,101]},index=list('ABCD'))
    p=planejar(m)
    assert p['n_amostra']==3 and p['limite_variancia_media_global']==0
    for r in p['amostra']:assert r['probabilidade_inclusao']==1
    assert limite_variancia(10,10)==0
    with pytest.raises(ValueError):planejar(m,erro_global=0)


def test_resumo_bfs_ciclo_paralelas_inalcancavel():
    vertices=list('ABCD')
    arestas=[('A','B',1),('A','B',-1),('B','C',1),('C','A',-1)]
    r=resumir_bfs(BFS(vertices,arestas,'A'),4)
    assert r['alcance_total']==2 and r['proporcao_alcance']==2/3
    assert r['distancia_media_bfs']==1.5 and r['maior_distancia_bfs']==2
    z=resumir_bfs(BFS(vertices,arestas,'D'),4)
    assert z['distancia_media_bfs'] is None and z['maior_distancia_bfs']==0
    assert resumir_bfs(BFS(['A'],[],'A'),1)['proporcao_alcance'] is None


def test_estimador_exclui_extras_e_inclui_zeros_exatos():
    m=cadastro();p=planejar(m)
    rows=[{'origem':r['origem'],'proporcao_alcance':.5} for r in p['amostra']]
    e=estimar_media_alcance(p,rows)
    assert e['media_ponderada']==pytest.approx(.5*(54075-10380)/54075)
    assert e['erro_padrao_desenho_estimado']==0
    assert e['margem_conservadora']>0
    with pytest.raises(ValueError):estimar_media_alcance(p,rows+[rows[0]])
    with pytest.raises(ValueError):estimar_media_alcance(p,rows[:-1])
    with pytest.raises(ValueError):estimar_media_alcance(p,rows+[{'origem':'fora','proporcao_alcance':1}])


def test_integracao_cache_exportacao_e_sem_dependencia_bf(tmp_path,monkeypatch):
    base=tmp_path/'base.csv'
    pd.DataFrame([
        [2,'A','B','p1','2012-12-31',1],
        [3,'B','A','p2','2014-01-01',-1],
        [4,'B','C','p3','2017-04-30',1]],
        columns=['linha_arquivo','SOURCE_SUBREDDIT','TARGET_SUBREDDIT','POST_ID','TIMESTAMP','LINK_SENTIMENT']).to_csv(base,index=False)
    out=tmp_path/'novo'
    kw=dict(base=base,out=out,globais_existentes=None,fontes_obrigatorias=['A'],pares=[('A','C'),('A','B')],comparar_nao_negativas=True)
    contagens={'bfs':0,'dfs':0,'dijkstra':0}
    def contar(nome,funcao):
        def wrapper(*a,**k):contagens[nome]+=1;return funcao(*a,**k)
        return wrapper
    monkeypatch.setattr(eg,'BFS',contar('bfs',eg.BFS))
    monkeypatch.setattr(eg,'DFS',contar('dfs',eg.DFS))
    monkeypatch.setattr(eg,'djikstra',contar('dijkstra',eg.djikstra))
    eg.executar(modo='planejar',**kw)
    globais_antes={p.name:eg.sha(p) for p in (out/'globais').iterdir()}
    assert contagens=={'bfs':0,'dfs':0,'dijkstra':0}
    eg.executar(modo='piloto',**kw)
    eg.executar(modo='executar',**kw)
    assert contagens=={'bfs':4,'dfs':1,'dijkstra':1}
    antes=contagens.copy();eg.executar(modo='executar',**kw);assert contagens==antes
    amostra=pd.read_csv(out/'amostra_analitica.csv');zeros=pd.read_csv(out/'censo_grau_zero.csv')
    assert set(amostra.origem)=={'A','B'} and zeros.origem.tolist()==['C']
    assert amostra.grau_entrada.tolist()==[1,1]
    assert pd.isna(zeros.distancia_media_bfs.iloc[0])
    assert zeros.proporcao_alcance.iloc[0]==0
    assert globais_antes=={p.name:eg.sha(p) for p in (out/'globais').iterdir()}
    registro=json.loads((out/'registro_origens.json').read_text(encoding='utf8'))
    assert set(amostra.origem)=={r['origem'] for r in registro if r['amostra_analitica']}
    for r in amostra.itertuples():
        assert r.proporcao_alcance==r.alcance_total/2
        assert r.probabilidade_inclusao==r.n_h/r.N_h
    pd.testing.assert_frame_equal(amostra,pd.read_csv(out/'fontes_resultados.csv'))
    assert len(json.loads((out/'caminhos_documentados.json').read_text()))==2
    assert json.loads((out/'CONCLUIDO.json').read_text())['versao']==2
    assert 'verificar_casos_bf' not in Path(eg.__file__).read_text(encoding='utf8')
    assert not list(out.glob('*report.json'))
    with pytest.raises(ValueError):eg.executar(modo='planejar',**{**kw,'semente':43})


def test_piloto_obrigatorio_e_orcamento(tmp_path):
    base=tmp_path/'b.csv'
    pd.DataFrame([[2,'A','B','p','2020-01-01',1]],columns=['linha_arquivo','SOURCE_SUBREDDIT','TARGET_SUBREDDIT','POST_ID','TIMESTAMP','LINK_SENTIMENT']).to_csv(base,index=False)
    kw=dict(base=base,out=tmp_path/'o',globais_existentes=None,fontes_obrigatorias=[],pares=[])
    with pytest.raises(ValueError,match='piloto'):eg.executar(modo='executar',**kw)
    eg.executar(modo='piloto',**kw)
    with pytest.raises(ValueError,match='supera limite'):eg.executar(modo='executar',limite_segundos=1e-15,**kw)


def test_reuso_preserva_identificadores_e_valores_indefinidos(tmp_path):
    base=tmp_path/'base.csv'
    pd.DataFrame([[2,'nan','null','p','2013-01-01',1]],columns=[
        'linha_arquivo','SOURCE_SUBREDDIT','TARGET_SUBREDDIT','POST_ID','TIMESTAMP','LINK_SENTIMENT']).to_csv(base,index=False)
    destino=tmp_path/'saida';destino.mkdir()
    primeira,_,_=eg.carregar_globais(base,None,destino)
    segunda,_,proveniencia=eg.carregar_globais(base,destino/'globais',destino)
    pd.testing.assert_frame_equal(primeira,segunda)
    assert proveniencia['reutilizadas']
    assert eg.atributos_origem(segunda,'null')['proporcao_negativas_saida'] is None
    base.write_text(base.read_text()+'\n')
    with pytest.raises(ValueError,match='hash'):eg.carregar_globais(base,destino/'globais',destino)
