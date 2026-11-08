"""Leitura de mapas e erros de entrada exigidos na etapa 1."""

# [IA] Codex – testes de leitura e validação dos mapas.
from pathlib import Path

import pytest

from src.graphs.io import ErroMapa, ler_mapa


def gravar(tmp_path, texto):
    caminho = tmp_path / "mapa.txt"
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def test_grade_e_posicoes(tmp_path):
    caminho = gravar(
        tmp_path,
        "; comentário\n#########\n#S.a.+.G#\n; outra linha\n#+b.a.G.#\n#########\n\n",
    )
    mapa = ler_mapa(caminho)
    assert mapa.grade == (
        "#########", "#S.a.+.G#", "#+b.a.G.#", "#########"
    )
    assert (mapa.altura, mapa.largura) == (4, 9)
    assert mapa.inicio == (1, 1)
    assert mapa.saidas == ((1, 7), (2, 6))
    assert mapa.chaves == {"a": ((1, 3), (2, 4)), "b": ((2, 2),)}
    assert mapa.bonus == {0: (1, 5), 1: (2, 1)}


@pytest.mark.parametrize(
    ("texto", "mensagem"),
    [
        ("#####\n#SG#\n#####", "não retangular"),
        ("######\n#SS.G#\n######", "exatamente um S; encontrados 2"),
        ("#####\n#...#\n#..G#", "exatamente um S; encontrados 0"),
        ("#####\n#S..#\n#####", "pelo menos um G"),
        ("#####\n#S@G#\n#####", "símbolo '@' na linha 2, coluna 3"),
        ("#####\n#S G#\n#####", "símbolo ' '"),
        ("#####\n\n#S.G#\n#####", "linha vazia na linha 2"),
        ("\n#SG#", "linha vazia na linha 1"),
        ("", "grade está vazia"),
        ("; só comentários\n\n", "grade está vazia"),
    ],
)
def test_rejeita_mapa_invalido(tmp_path, texto, mensagem):
    with pytest.raises(ErroMapa) as capturado:
        ler_mapa(gravar(tmp_path, texto))
    assert mensagem in str(capturado.value)


def test_erro_indica_linha_original_do_arquivo(tmp_path):
    caminho = gravar(tmp_path, "; comentário\n#####\n#S@G#\n#####")
    with pytest.raises(ErroMapa, match="linha 3, coluna 3"):
        ler_mapa(caminho)


def test_aceita_todos_os_simbolos_e_nao_exige_paredes_na_borda(tmp_path):
    mapa = ler_mapa(gravar(tmp_path, "S.G,~abcdABCD><^v+*#"))
    assert mapa.altura == 1
    assert mapa.grade[0] == "S.G,~abcdABCD><^v+*#"


def test_nao_verifica_solvabilidade(tmp_path):
    mapa = ler_mapa(gravar(tmp_path, "#######\n#S#A#G#\n#######"))
    assert mapa.inicio == (1, 1)
    assert mapa.saidas == ((1, 5),)


def test_aceita_bom_crlf_e_sem_quebra_final(tmp_path):
    caminho = tmp_path / "mapa.txt"
    caminho.write_bytes(b"\xef\xbb\xbf#####\r\n#S.G#\r\n#####")
    assert ler_mapa(str(caminho)).grade == ("#####", "#S.G#", "#####")


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(ErroMapa, match="Não foi possível ler"):
        ler_mapa(tmp_path / "inexistente.txt")


def test_utf8_invalido(tmp_path):
    caminho = tmp_path / "mapa.txt"
    caminho.write_bytes(b"\xff\xfe")
    with pytest.raises(ErroMapa, match="Não foi possível ler"):
        ler_mapa(caminho)


@pytest.mark.parametrize("caminho", sorted(
    (Path(__file__).resolve().parents[1] / "data" / "mapas").glob("*.txt")
), ids=lambda caminho: caminho.stem)
def test_mapas_fornecidos(caminho):
    mapa = ler_mapa(caminho)
    assert mapa.grade[mapa.inicio[0]][mapa.inicio[1]] == "S"
    assert mapa.saidas
    if caminho.stem == "m08_grande":
        assert (mapa.altura, mapa.largura) == (31, 71)
