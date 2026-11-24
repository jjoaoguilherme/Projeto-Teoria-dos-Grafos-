import csv
import io
import json

import pytest

from src.parte2.dados import carregar_dataset, exportar_dataset
from src.parte2 import obter_dataset as download


def test_qualidade_preserva_duplicatas_e_atributos_auxiliares(tmp_path):
    vetor = ','.join(['0'] * 86)
    invalido = ','.join(['nan'] + ['0'] * 85)
    header = 'SOURCE_SUBREDDIT\tTARGET_SUBREDDIT\tLINK_SENTIMENT\tPOST_ID\tTIMESTAMP\tPROPERTIES\n'
    linha = f'a\tb\t-1\tp1\t2020-01-01 10:00:00\t{vetor}\n'
    caminho = tmp_path / 'reddit.tsv'
    caminho.write_text(header + linha + linha + f'b\tc\t1\t\tdata-invalida\t{invalido}\n', encoding='utf-8')
    dados = carregar_dataset(caminho)
    q = dados['relatorio']['qualidade']
    assert dados['grafo'].arestas == [('a', 'b', -1), ('a', 'b', -1), ('b', 'c', 1)]
    assert q['duplicatas_exatas'] == 1
    assert q['faltantes_por_coluna']['POST_ID'] == 1
    assert q['datas_invalidas'] == 1
    assert q['properties']['vetores_invalidos'] == 1
    assert dados['atributos_arestas'][2]['atributos']['PROPERTIES'] == invalido
    exportar_dataset(dados, tmp_path / 'out')
    with (tmp_path / 'out/base_avd.csv').open(encoding='utf-8', newline='') as arquivo:
        rows = list(csv.DictReader(arquivo))
    assert [r['linha_arquivo'] for r in rows] == ['2', '3', '4']
    assert 'PROPERTIES' not in rows[0]
    assert rows[2]['TIMESTAMP'] == 'data-invalida'


def test_base_avd_alinhada_aos_vertices_normalizados(tmp_path):
    caminho = tmp_path / 'reddit.tsv'
    caminho.write_text('SOURCE_SUBREDDIT\tTARGET_SUBREDDIT\tLINK_SENTIMENT\n a \t b \t -1 \n', encoding='utf-8')
    dados = carregar_dataset(caminho)
    assert dados['relatorio']['qualidade']['espacos_externos_por_coluna']['SOURCE_SUBREDDIT'] == 1
    assert dados['atributos_arestas'][0]['atributos']['SOURCE_SUBREDDIT'] == ' a '
    exportar_dataset(dados, tmp_path / 'out')
    with (tmp_path / 'out/base_avd.csv').open(encoding='utf-8', newline='') as arquivo:
        row = next(csv.DictReader(arquivo))
    assert (row['SOURCE_SUBREDDIT'], row['TARGET_SUBREDDIT'], row['LINK_SENTIMENT']) == ('a', 'b', '-1')


class Resposta(io.BytesIO):
    def __init__(self, conteudo, tamanho=None):
        super().__init__(conteudo)
        self.headers = {'Content-Length': str(len(conteudo) if tamanho is None else tamanho)}


def test_download_reproduzivel_e_verificacao_de_integridade(tmp_path, monkeypatch):
    conteudo = b'SOURCE_SUBREDDIT\tTARGET_SUBREDDIT\tLINK_SENTIMENT\na\tb\t-1\n'
    chamadas = []
    def resposta(url, timeout):
        chamadas.append(url)
        return Resposta(conteudo)
    monkeypatch.setattr(download, 'urlopen', resposta)
    destino = tmp_path / download.NOME
    assert download.obter_dataset(destino) == destino
    origem = json.loads((tmp_path / 'origem_dataset.json').read_text(encoding='utf-8'))
    assert origem['sha256'] == download.calcular_sha256(destino)
    download.obter_dataset(destino)
    assert chamadas == [download.URL]
    destino.write_bytes(conteudo + b'alterado')
    with pytest.raises(ValueError, match='difere'):
        download.obter_dataset(destino)


def test_download_incompleto_nao_vira_arquivo_final(tmp_path, monkeypatch):
    monkeypatch.setattr(download, 'urlopen', lambda *a, **k: Resposta(b'incompleto', 100))
    destino = tmp_path / download.NOME
    with pytest.raises(ValueError, match='incompleto'):
        download.obter_dataset(destino)
    assert not destino.exists()


def test_resposta_sem_colunas_do_reddit_nao_vira_dataset(tmp_path, monkeypatch):
    monkeypatch.setattr(download, 'urlopen', lambda *a, **k: Resposta(b'<html>erro</html>'))
    destino = tmp_path / download.NOME
    with pytest.raises(ValueError, match='colunas esperadas'):
        download.obter_dataset(destino)
    assert not destino.exists()
