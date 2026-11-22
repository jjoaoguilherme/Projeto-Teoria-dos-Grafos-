from src.graphs.algorithms import DFS


def test_quatro_tipos_e_ciclo():
    e=[('A','B',1),('A','C',1),('A','D',1),('B','C',1),('C','A',1),('D','B',1)]
    r=DFS('ABCD',e,'A')
    assert set(t for _,_,t in r['classificacao_arestas'])=={'arvore','retorno','avanco','cruzamento'}
    assert r['tem_ciclo']
    assert len(r['classificacao_arestas'])==len(e)
    assert all(r['descoberta'][v]<r['finalizacao'][v] for v in 'ABCD')
