"""Integração da interface com os algoritmos e limites de acesso local."""
import json
from pathlib import Path
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from src import interface


@pytest.mark.parametrize('texto,algoritmo,consumivel,status', [
    ('SaAG', 'BFS', False, 'OK'),
    ('SaAG', 'DFS', False, 'OK'),
    ('S+G', 'DIJKSTRA', False, 'RECUSA'),
    ('S*G', 'BELLMAN_FORD', False, 'CICLO_NEGATIVO'),
    ('S*G', 'BELLMAN_FORD', True, 'OK'),
    ('S#G', 'BFS', False, 'SEM_SOLUCAO'),
])
def test_execucao_mapa_exporta_e_anima(tmp_path, texto, algoritmo, consumivel, status):
    interface.executar_trabalho({'acao': 'mapa', 'texto': texto,
        'algoritmo': algoritmo, 'consumivel': consumivel}, tmp_path)
    d = json.loads((tmp_path/'resultado.json').read_text(encoding='utf-8'))
    assert d['relatorio']['status'] == status
    assert d['matriz'][0] == list(texto)
    assert d['estados']
    assert (tmp_path/'metricas_global.json').exists()
    if status == 'OK':
        assert d['relatorio']['percurso'][-1]['posicao'] == [0, len(texto)-1]
    if status == 'SEM_SOLUCAO':
        assert all(e['armadilha'] for e in d['estados'])


@pytest.mark.parametrize('algoritmo', interface.ALGORITMOS)
def test_dataset_reutiliza_algoritmos(tmp_path, monkeypatch, algoritmo):
    if algoritmo == 'DIJKSTRA':
        from src.graphs import algorithms
        def recusar_original(*args, **kwargs):
            raise AssertionError('Reddit deve usar a versão com heap')
        monkeypatch.setattr(algorithms, 'djikstra', recusar_original)
    monkeypatch.setattr(interface, 'RAIZ', tmp_path)
    base = tmp_path/'out/parte2'
    base.mkdir(parents=True)
    (base/'arestas_dataset.csv').write_text('origem,destino,peso\na,b,-1\nb,c,1\n', encoding='utf-8')
    pasta = tmp_path/'execucao'
    pasta.mkdir()
    interface.executar_trabalho({'acao': 'dataset', 'origem': 'a', 'destino': 'c',
                                'algoritmo': algoritmo, 'limite': 0}, pasta)
    r = json.loads((pasta/'resultado.json').read_text(encoding='utf-8'))
    assert r['caminho'] == ['a', 'b', 'c']
    assert r['distancia'] == {'BFS': 2, 'DFS': 2, 'DIJKSTRA': 4, 'BELLMAN_FORD': 0}[algoritmo]
    assert (pasta/'busca_completa.json').exists()


def test_dataset_ciclo_negativo_nao_vira_erro(tmp_path, monkeypatch):
    monkeypatch.setattr(interface, 'RAIZ', tmp_path)
    base = tmp_path/'out/parte2'
    base.mkdir(parents=True)
    (base/'arestas_dataset.csv').write_text('origem,destino,peso\na,b,-1\nb,a,-1\n', encoding='utf-8')
    interface.executar_trabalho({'acao':'dataset', 'origem':'a', 'destino':'b',
                                'algoritmo':'BELLMAN_FORD', 'limite':0}, tmp_path)
    r = json.loads((tmp_path/'resultado.json').read_text(encoding='utf-8'))
    assert r['status'] == 'CICLO_NEGATIVO'
    assert r['distancia'] == '-Infinito'
    assert r['custo_ciclo'] < 0
    assert r['caminho'] == []


@pytest.mark.parametrize('nome', ['../fora.txt', '.git/config', 'src/interface.py', 'out/../../fora.json'])
def test_caminhos_privados_recusados(tmp_path, nome):
    with pytest.raises(ValueError):
        interface.caminho_publico(nome, tmp_path)


def test_http_catalogo_paginacao_e_autorizacao(tmp_path):
    pasta = tmp_path/'out/parte1'
    pasta.mkdir(parents=True)
    (pasta/'teste.csv').write_text('origem,peso\n'+''.join(f'n{i},{i}\n' for i in range(75)), encoding='utf-8')
    (pasta/'teste.json').write_text('{"valor": 3}', encoding='utf-8')
    servidor = interface.criar_servidor(0, tmp_path)
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{servidor.server_port}'
    def get(path):
        with urlopen(url+path) as r:
            return json.load(r)
    try:
        catalogo = get('/api/catalogo')
        assert len(catalogo['arquivos']) == 2
        r = get('/api/tabela?arquivo=out/parte1/teste.csv&offset=50')
        assert len(r['linhas']) == 25 and r['total'] == 75
        assert r['linhas'][0]['origem'] == 'n50'
        assert get('/api/tabela?arquivo=out/parte1/teste.csv&busca=n74')['total'] == 1
        assert get('/api/tabela?arquivo=out/parte1/teste.json') == {'valor': 3}
        with pytest.raises(HTTPError) as e:
            urlopen(Request(url+'/api/executar', data=b'{"acao":"testes"}'))
        assert e.value.code == 403
        with pytest.raises(HTTPError) as e:
            urlopen(Request(url+'/api/executar', data=b'{"acao":"comando_arbitrario"}',
                            headers={'X-Project-Token':catalogo['token']}))
        assert e.value.code == 400
        with pytest.raises(HTTPError) as e:
            urlopen(Request(url+'/api/catalogo', headers={'Host':'outro.site'}))
        assert e.value.code == 403
    finally:
        servidor.shutdown()
        servidor.server_close()
        thread.join()
