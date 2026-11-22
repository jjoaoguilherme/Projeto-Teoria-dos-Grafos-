from src.graphs.estados import construir_grafo_estados
from src.graphs.analises import estados_armadilha,comparar_modelagens


def test_mapa_minimo_contado_a_mao():
    d=construir_grafo_estados([list('SaG')],(0,0))
    assert len(d['estados'])==4
    assert len(d['arestas'])==5
    assert ('(0,0)|-|{}','(0,1)|a|{}',1) in d['arestas']
    assert estados_armadilha(d)==[]


def test_armadilha_por_esteira_e_sem_solucao():
    d=construir_grafo_estados([list('S>#G')],(0,0))
    assert estados_armadilha(d)==['(0,0)|-|{}','(0,1)|-|{}']


def test_comparacao_valida_portas():
    r=comparar_modelagens([list('SAaG')],(0,0),'teste')
    assert r[0]['passos']==3 and not r[0]['caminho_valido']
    assert r[1]['passos'] is None
    assert r[2]['passos'] is None
