import pytest
from src.graphs.algorithms import djikstra, djikstra_heap, reconstruir_caminho


@pytest.mark.parametrize("executar", [djikstra, djikstra_heap])
def test_pesos_e_zero(executar):
    r=executar('ABCDE',[('A','B',8),('A','C',1),('C','B',0),('B','D',2)],'A')
    assert r['distancias']['D']==3
    assert reconstruir_caminho(r,'D')==['A','C','B','D']
    assert r['distancias']['E']==float('inf')


@pytest.mark.parametrize("executar", [djikstra, djikstra_heap])
def test_recusa_arco_negativo_inclusive_inalcancavel(executar):
    with pytest.raises(ValueError,match='negativos'):
        executar('ABCD',[('C','D',-1)],'A')


def test_versoes_preservam_desempates_paralelos_e_inalcancaveis():
    vertices = ['S', 'B', 'A', 'C', 'X']
    arestas = [('S', 'A', 1), ('S', 'B', 8), ('S', 'B', 1),
               ('A', 'C', 0), ('B', 'C', 0), ('B', 'B', 0)]
    original = djikstra(vertices, arestas, 'S')
    assert original['ordem_visita'] == ['S', 'B', 'A', 'C']
    assert reconstruir_caminho(original, 'C') == ['S', 'B', 'C']
    assert djikstra_heap(vertices, arestas, 'S') == original


def test_selecao_por_parte():
    from src import main
    from src.parte2 import experimentos, estudo_global
    assert main.djikstra is djikstra
    assert experimentos.ALGORITMOS['DIJKSTRA'] is djikstra_heap
    assert experimentos.djikstra is djikstra_heap
    assert estudo_global.djikstra is djikstra_heap
