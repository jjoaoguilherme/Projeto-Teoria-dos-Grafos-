import pytest
from src.graphs.algorithms import djikstra, reconstruir_caminho


def test_pesos_e_zero():
    r=djikstra('ABCDE',[('A','B',8),('A','C',1),('C','B',0),('B','D',2)],'A')
    assert r['distancias']['D']==3
    assert reconstruir_caminho(r,'D')==['A','C','B','D']
    assert r['distancias']['E']==float('inf')


def test_recusa_arco_negativo_inclusive_inalcancavel():
    with pytest.raises(ValueError,match='negativos'):
        djikstra('ABCD',[('C','D',-1)],'A')
