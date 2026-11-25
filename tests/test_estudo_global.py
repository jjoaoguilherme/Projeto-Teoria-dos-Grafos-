# [IA] ChatGPT – invariantes das tabelas e testemunhas de caminhos.
import pandas as pd
import pytest
from src.parte2.estudo_global import preparar_tabelas, documentar_caminho, selecionar_fontes
from src.graphs.algorithms import djikstra


def base():
    return pd.DataFrame([
        [2,'A','B','p1','2013-12-31',-1],
        [3,'A','B','p2','2014-01-01',1],
        [4,'B','A','p3','2015-01-01',-1],
        [5,'B','C','p4','2017-04-30',1],
    ],columns=['linha_arquivo','SOURCE_SUBREDDIT','TARGET_SUBREDDIT','POST_ID','TIMESTAMP','LINK_SENTIMENT'])


def test_multigrafo_densidade_ciclos_e_ausencia_estrutural():
    m,mes,ciclos,outliers,r=preparar_tabelas(base())
    assert r['referencias']==4 and r['pares_distintos']==3
    assert r['densidade_suporte_simples_sem_lacos']==.5
    assert m.loc['A','referencias_saida']==2 and m.loc['A','vizinhos_saida']==1
    assert m.loc['A','proporcao_negativas_saida']==.5
    assert pd.isna(m.loc['C','proporcao_negativas_saida'])
    assert ciclos.values.tolist()==[['A','B']]
    assert r['comunidades_em_ciclo_negativo_duas_arestas']==2
    assert mes.referencias.sum()==4


def test_testemunha_respeita_peso_entre_paralelas():
    resultado=djikstra(['A','B'], [('A','B',3),('A','B',1)],'A')
    indice={('A','B'):[{'peso':-1,'post_id':'p1'},{'peso':1,'post_id':'p2'}]}
    doc=documentar_caminho(resultado,'B',indice,True)
    assert doc['arestas'][0]['post_id']=='p2'
    assert doc['custo_transformado']==resultado['distancias']['B']==1


def test_entrada_invalida_nao_e_excluida_silenciosamente():
    df=base(); df.loc[0,'TIMESTAMP']='invalida'
    with pytest.raises(ValueError): preparar_tabelas(df)
    df=base(); df.loc[0,'TIMESTAMP']='2012-01-01'
    assert preparar_tabelas(df)[-1]['data_minima'].startswith('2012')


def test_amostra_reproduzivel_sem_repeticoes():
    m,*_=preparar_tabelas(base())
    plano=selecionar_fontes(m)
    assert plano==selecionar_fontes(m)
    origens=[r['origem'] for r in plano['amostra']]
    assert len(origens)==len(set(origens))==2
    assert next(h for h in plano['estratos'] if h['estrato']=='grau_0')['avaliados_exatamente_sem_bfs']==1
