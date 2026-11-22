import pytest
from src.graphs.io import ler_mapa


@pytest.mark.parametrize('texto',['###\n#SG#','SSG','S..','G..','S@G'])
def test_mapas_invalidos(tmp_path,texto):
    p=tmp_path/'mapa.txt';p.write_text(texto,encoding='utf-8')
    with pytest.raises(ValueError):ler_mapa(p)


def test_comentarios_multiplas_saidas_e_linhas_finais(tmp_path):
    p=tmp_path/'mapa.txt';p.write_text(';comentario\nGSG\n\n',encoding='utf-8-sig')
    matriz,inicio,_=ler_mapa(p)
    assert matriz==[list('GSG')]
    assert inicio==(0,1)
