from src.graphs.algorithms import BFS, reconstruir_caminho


def test_niveis_e_inalcancavel():
    r=BFS('ABCDE',[('A','B',9),('A','C',1),('B','D',1),('C','D',1)],'A')
    assert r['distancias']=={'A':0,'B':1,'C':1,'D':2,'E':float('inf')}
    assert reconstruir_caminho(r,'D')==['A','B','D']
    assert reconstruir_caminho(r,'E')==[]
