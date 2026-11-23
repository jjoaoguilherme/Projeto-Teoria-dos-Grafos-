import csv
import json
import pytest
from src.parte2.dados import carregar_dataset, verificar_dataset, exportar_dataset
from src.graphs.algorithms import BFS, djikstra

HEADER = 'SOURCE_SUBREDDIT\tTARGET_SUBREDDIT\tLINK_SENTIMENT\tPOST_ID\n'


def arquivo(tmp_path, linhas):
    p=tmp_path/'reddit.tsv';p.write_text(HEADER+linhas,encoding='utf-8-sig');return p


def test_grafo_direcao_pesos_atributos_e_repeticoes(tmp_path):
    p=arquivo(tmp_path,'a\tb\t-1\tp1\na\tb\t1\tp2\nb\tb\t1\tp3\n')
    d=carregar_dataset(p);g=d['grafo'];r=d['relatorio']
    assert g.vertices==['a','b']
    assert g.arestas==[('a','b',-1),('a','b',1),('b','b',1)]
    assert g.vizinhos('b')==[('b',1)]
    assert d['atributos_arestas'][0]['atributos']['POST_ID']=='p1'
    assert r['contagens']['pares_repetidos']==1 and r['contagens']['lacos']==1
    assert r['contagens']['negativos']==1
    assert not r['atinge_20_mil_arestas']


@pytest.mark.parametrize('linha',['a\tb\t0\tp','\tb\t1\tp','a\tb\t1','a\tb\t1\tp\textra'])
def test_estrito_rejeita_e_registrar_preserva(tmp_path,linha):
    p=arquivo(tmp_path,'a\tb\t1\tok\n'+linha+'\n')
    with pytest.raises(ValueError,match='Linha 3'):carregar_dataset(p)
    d=carregar_dataset(p,invalidos='registrar')
    assert d['grafo'].arestas==[('a','b',1)]
    assert d['relatorio']['contagens']['invalidos']==1
    assert len(d['registros_invalidos'])==1
    assert verificar_dataset(p)['contagens']==d['relatorio']['contagens']


def test_cabecalho_invalido(tmp_path):
    p=tmp_path/'a.tsv'
    for header in ['a\tb','SOURCE_SUBREDDIT\tSOURCE_SUBREDDIT\tLINK_SENTIMENT']:
        p.write_text(header,encoding='utf-8')
        with pytest.raises(ValueError):carregar_dataset(p)


def test_inexistente_e_politica_invalida(tmp_path):
    with pytest.raises(FileNotFoundError):carregar_dataset(tmp_path/'inexistente')
    with pytest.raises(ValueError):carregar_dataset(tmp_path/'inexistente',invalidos='outro')


def test_dataset_sem_linhas_e_sem_resultados_inventados(tmp_path):
    d=carregar_dataset(arquivo(tmp_path,''))
    assert d['grafo'].vertices==[]
    assert d['relatorio']['arestas']==0


def test_reuso_algoritmos_e_exportacao(tmp_path):
    d=carregar_dataset(arquivo(tmp_path,'a\tb\t1\tp1\nb\tc\t-1\tp2\n'))
    g=d['grafo'];r=BFS(g.vertices,g.arestas,'a')
    assert r['distancias']['c']==2
    with pytest.raises(ValueError,match='negativos'):djikstra(g.vertices,g.arestas,'a')
    exportar_dataset(d,tmp_path/'out')
    with (tmp_path/'out/arestas_dataset.csv').open(encoding='utf-8',newline='') as f:
        assert len(list(csv.DictReader(f)))==2
    assert json.loads((tmp_path/'out/resumo_dataset.json').read_text(encoding='utf-8'))['vertices']==3
