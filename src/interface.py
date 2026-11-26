"""Interface local das entregas e execução dos algoritmos existentes."""
import argparse
import csv
import json
import math
import mimetypes
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit, quote

RAIZ = Path(__file__).resolve().parents[1]
ALGORITMOS = ('BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD')
ACOES = {
    'parte1': 'Gerar todas as entregas da Parte 1',
    'metricas': 'Atualizar métricas dos mapas',
    'preparar': 'Baixar e preparar o dataset',
    'bfs_dfs': 'Medir BFS e DFS nas três fontes',
    'dijkstra': 'Medir Dijkstra nos cinco pares',
    'bellman_ford': 'Medir os dois casos de Bellman-Ford',
    'escalabilidade': 'Medir os quatro algoritmos em três tamanhos',
    'consolidar': 'Consolidar e verificar experimentos',
    'graficos': 'Gerar gráficos de desempenho',
    'avd': 'Gerar as seis figuras AVD',
    'planejar': 'Planejar nova amostragem AVD',
    'piloto': 'Executar piloto da nova amostragem',
    'estudo': 'Executar nova amostragem AVD',
    'testes': 'Executar os testes do projeto',
}


def caminho_publico(nome, raiz=RAIZ):
    """Restringe leitura às entregas e documentos, inclusive após resolver links."""
    raiz = Path(raiz).resolve()
    p = (raiz / nome).resolve()
    if not p.is_relative_to(raiz):
        raise ValueError('Caminho fora do projeto.')
    rel = p.relative_to(raiz)
    permitido = rel.parts and rel.parts[0] in ('out', 'docs', 'data')
    if not permitido and rel.as_posix() not in ('README.md', 'requirements.txt'):
        raise ValueError('Arquivo não disponível na interface.')
    if p.suffix.lower() not in ('.csv', '.tsv', '.json', '.png', '.svg', '.pdf', '.md', '.txt', '.html', '.docx'):
        raise ValueError('Tipo de arquivo não disponível.')
    return p


def normalizar(valor):
    if isinstance(valor, float) and not math.isfinite(valor):
        return 'Infinito' if valor > 0 else '-Infinito' if valor < 0 else None
    if isinstance(valor, dict):
        return {str(k): normalizar(v) for k, v in valor.items()}
    if isinstance(valor, (tuple, list, set)):
        return [normalizar(v) for v in valor]
    return valor


def catalogo(raiz=RAIZ):
    raiz = Path(raiz)
    mapas = [p for d in ('data/mapas', 'data/mapas_grupo') for p in sorted((raiz/d).glob('*.txt'))]
    arquivos = []
    for pasta in ('out', 'docs', 'data'):
        for p in sorted((raiz/pasta).rglob('*')):
            if not p.is_file() or p.name.startswith('.'):
                continue
            rel = p.relative_to(raiz).as_posix()
            try:
                caminho_publico(rel, raiz)
            except ValueError:
                continue
            arquivos.append({'nome': p.name, 'caminho': rel, 'bytes': p.stat().st_size,
                             'tipo': p.suffix[1:], 'cache': 'cache' in p.parts,
                             'url': '/arquivo/' + quote(rel, safe='/')})
    for nome in ('README.md', 'requirements.txt'):
        p = raiz/nome
        if p.is_file():
            arquivos.append({'nome': nome, 'caminho': nome, 'bytes': p.stat().st_size,
                             'tipo': p.suffix[1:], 'cache': False, 'url': '/arquivo/'+nome})
    return {'mapas': [{'nome': p.stem, 'caminho': p.relative_to(raiz).as_posix()} for p in mapas],
            'arquivos': arquivos, 'acoes': ACOES, 'algoritmos': ALGORITMOS,
            'dataset': (raiz/'out/parte2/arestas_dataset.csv').exists()}


def executar_trabalho(dados, pasta):
    """Executado em processo separado; nunca recebe comandos de shell."""
    from src.main import resolver_mapa, exportar_resultado
    from src.graphs.io import ler_mapa
    from src.graphs.analises import estados_armadilha, exportar_armadilhas
    pasta = Path(pasta)
    acao = dados['acao']
    if acao == 'mapa':
        algoritmo = dados.get('algoritmo', 'BFS')
        if algoritmo not in ALGORITMOS:
            raise ValueError('Algoritmo inválido.')
        if dados.get('texto'):
            caminho = pasta / 'mapa_importado.txt'
            caminho.write_text(dados['texto'], encoding='utf-8')
        else:
            caminho = caminho_publico(dados.get('mapa', ''))
            if caminho.parent not in (RAIZ/'data/mapas', RAIZ/'data/mapas_grupo'):
                raise ValueError('Escolha um mapa disponível ou importe um TXT.')
        relatorio, grafo = resolver_mapa(caminho, bool(dados.get('consumivel')), algoritmo)
        exportar_resultado(relatorio, grafo, pasta)
        exportar_armadilhas(grafo, relatorio['mapa'], pasta)
        armadilhas = set(estados_armadilha(grafo))
        matriz, _, _ = ler_mapa(caminho)
        resultado = {'tipo': 'mapa', 'relatorio': relatorio, 'matriz': matriz,
                     'camadas': grafo['metricas']['camadas'],
                     'graus': grafo['metricas']['graus'],
                     'estados': [{'rotulo': r, 'posicao': e[0], 'chaves': ''.join(sorted(e[1])) or '-',
                                  'armadilha': r in armadilhas} for r, e in grafo['estados'].items()]}
    elif acao == 'dataset':
        from src.parte2.escalabilidade import carregar_arestas_preparadas
        from src.graphs.graph import Grafo
        from src.graphs.algorithms import BFS, DFS, djikstra_heap as djikstra, bellman_ford, reconstruir_caminho
        from random import Random
        algoritmo = dados.get('algoritmo', 'BFS')
        if algoritmo not in ALGORITMOS:
            raise ValueError('Algoritmo inválido.')
        g = carregar_arestas_preparadas(RAIZ/'out/parte2/arestas_dataset.csv')
        origem, destino = dados.get('origem', '').strip(), dados.get('destino', '').strip()
        if origem not in g.vertices or (destino and destino not in g.vertices):
            raise ValueError('Origem ou destino não existe no dataset.')
        limite = int(dados.get('limite', 2000))
        if limite not in (0, 200, 1000, 2000):
            raise ValueError('Tamanho inválido.')
        if limite:
            obrigatorios = {origem, destino} if destino else {origem}
            candidatos = [v for v in g.vertices if v not in obrigatorios]
            Random(42).shuffle(candidatos)
            selecionados = obrigatorios | set(candidatos[:max(0, limite-len(obrigatorios))])
            g = Grafo([v for v in g.vertices if v in selecionados],
                      [(u,v,p) for u,v,p in g.arestas if u in selecionados and v in selecionados])
        arestas = [(u,v,2-p) for u,v,p in g.arestas] if algoritmo == 'DIJKSTRA' else g.arestas
        inicio = time.perf_counter()
        r = {'BFS': BFS, 'DFS': DFS, 'DIJKSTRA': djikstra, 'BELLMAN_FORD': bellman_ford}[algoritmo](g.vertices, arestas, origem)
        tempo = time.perf_counter()-inicio
        caminho = (reconstruir_caminho(r, destino)
                   if destino and r['distancias'][destino] != float('-inf') else [])
        resultado = {'tipo': 'dataset', 'algoritmo': algoritmo, 'origem': origem, 'destino': destino,
                     'vertices': len(g.vertices), 'arcos': len(g.arestas), 'segundos': tempo,
                     'escopo': 'Base completa' if not limite else f'Recorte induzido de até {limite} vértices; semente 42; origem/destino preservados',
                     'pesos': '2 - LINK_SENTIMENT' if algoritmo == 'DIJKSTRA' else 'LINK_SENTIMENT original',
                     'status': ('CICLO_NEGATIVO' if r.get('tem_ciclo_negativo') else
                                'SEM_SOLUCAO' if destino and not caminho else 'OK'),
                     'caminho': caminho, 'distancia': r['distancias'].get(destino) if destino else None,
                     'alcancaveis': sum(d != float('inf') for d in r['distancias'].values()),
                     'tem_ciclo': r.get('tem_ciclo', r.get('tem_ciclo_negativo')),
                     'ciclo_negativo': r.get('ciclo_negativo', []), 'custo_ciclo': r.get('custo_ciclo')}
        (pasta/'busca_completa.json').write_text(json.dumps(normalizar(r), ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        executar_acao(acao, dados)
        resultado = {'tipo': 'acao', 'acao': acao, 'mensagem': 'Execução concluída. O catálogo já pode ser atualizado.'}
    (pasta/'resultado.json').write_text(json.dumps(normalizar(resultado), ensure_ascii=False, indent=2), encoding='utf-8')
    print('Concluído.', flush=True)


def executar_acao(acao, dados):
    """Despacha apenas operações conhecidas; parâmetros são validados."""
    if acao == 'parte1':
        from src.solve import gerar_parte1
        gerar_parte1()
    elif acao == 'metricas':
        from src.graphs.metricas import calcular_pacote_mapa, exportar_pacotes_metricas
        mapas = [p for d in ('data/mapas', 'data/mapas_grupo') for p in sorted((RAIZ/d).glob('*.txt'))]
        exportar_pacotes_metricas([calcular_pacote_mapa(p) for p in mapas], RAIZ/'out/parte1')
    elif acao == 'preparar':
        from src.parte2.preparar import preparar_dataset
        preparar_dataset()
    elif acao in ('bfs_dfs', 'dijkstra', 'bellman_ford'):
        from src.parte2.experimentos import executar_bfs_dfs_dataset, executar_dijkstra, executar_bellman_ford, casos_bellman_ford, exportar_relatorio
        tsv = RAIZ/'data/dataset_parte2/soc-redditHyperlinks-title.tsv'
        if acao == 'bfs_dfs':
            executar_bfs_dfs_dataset(tsv, ['subredditdrama', 'bestof', 'titlegore'], 5, RAIZ/'out/parte2/bfs_dfs_report.json')
        else:
            r = executar_dijkstra(tsv, 5) if acao == 'dijkstra' else executar_bellman_ford(casos_bellman_ford, 5)
            exportar_relatorio(r, RAIZ/f'out/parte2/{acao}_report.json')
    elif acao == 'escalabilidade':
        from src.parte2.escalabilidade import main
        sys.argv = ['escalabilidade', '--origem', 'subredditdrama', '--proporcoes', '.1', '.5', '1', '--limite-vertices', '2000']
        main()
    elif acao == 'consolidar':
        from src.parte2.consolidar import consolidar_relatorios
        from src.parte2.verificar_experimentos import verificar_pasta
        consolidar_relatorios()
        r = verificar_pasta()
        (RAIZ/'out/parte2/verificacao_experimentos.json').write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding='utf-8')
        if not r['medicoes_validas'] or not r['consolidado_consistente']:
            raise ValueError('Relatórios inconsistentes; consulte a verificação.')
    elif acao == 'graficos':
        from importlib import import_module
        from src.parte2.graficos_escalabilidade import gerar_graficos
        from src.parte2.tabela_complexidades import gerar_tabela
        import_module('src.parte2.visualizações').gerar_graficos('out/parte2/parte2_report.json')
        gerar_graficos('out/parte2/escalabilidade_report.json')
        gerar_tabela()
    elif acao == 'avd':
        from src.parte2.figuras_avd import main
        base = 'out/interface/estudo_avd' if (RAIZ/'out/interface/estudo_avd/CONCLUIDO.json').exists() else 'out/parte2/global_amostragem_v2'
        sys.argv = ['figuras_avd', '--base', base]
        main()
    elif acao in ('planejar', 'piloto', 'estudo'):
        from src.parte2.estudo_global import executar
        executar('out/parte2/base_avd.csv', 'out/interface/estudo_avd',
                 'executar' if acao == 'estudo' else acao,
                 'out/parte2/global_amostragem_v2/globais', comparar_nao_negativas=True)
    elif acao == 'testes':
        import pytest
        if pytest.main(['-q']) != 0:
            raise ValueError('Há testes com falha; consulte o log.')
    else:
        raise ValueError('Ação desconhecida.')


class Trabalhos:
    def __init__(self, raiz=RAIZ):
        self.raiz = Path(raiz)
        self.lock = threading.Lock()
        self.itens = {}

    def iniciar(self, dados):
        if dados.get('acao') not in (*ACOES, 'mapa', 'dataset'):
            raise ValueError('Ação desconhecida.')
        with self.lock:
            if any(t['status'] == 'executando' for t in self.itens.values()):
                raise ValueError('Já existe uma execução em andamento. Aguarde ou cancele.')
            chave = secrets.token_hex(8)
            pasta = self.raiz/'out/interface'/chave
            pasta.mkdir(parents=True)
            log = (pasta/'execucao.log').open('w', encoding='utf-8')
            env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
            processo = subprocess.Popen([sys.executable, '-m', 'src.interface', '--worker', str(pasta)],
                cwd=self.raiz, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', env=env,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            processo.stdin.write(json.dumps(dados))
            processo.stdin.close()
            item = {'id': chave, 'status': 'executando', 'acao': dados['acao'], 'pasta': pasta,
                    'processo': processo, 'inicio': time.time(), 'log_handle': log}
            self.itens[chave] = item
            threading.Thread(target=self._esperar, args=(item,), daemon=True).start()
            return chave

    def _esperar(self, item):
        try:
            codigo = item['processo'].wait(timeout=3600)
            with self.lock:
                if item['status'] == 'executando':
                    item['status'] = 'concluido' if codigo == 0 else 'erro'
        except subprocess.TimeoutExpired:
            item['processo'].kill()
            item['processo'].wait()
            item['status'] = 'tempo_esgotado'
        finally:
            item['log_handle'].close()

    def cancelar(self, chave):
        with self.lock:
            t = self.itens[chave]
            if t['status'] == 'executando':
                t['status'] = 'cancelado'
                t['processo'].terminate()

    def estado(self, chave):
        with self.lock:
            t = self.itens[chave]
            resultado = {k: t[k] for k in ('id', 'status', 'acao', 'inicio')}
            arquivo = t['pasta']/'execucao.log'
            with arquivo.open('rb') as f:
                f.seek(max(0, arquivo.stat().st_size-20000))
                resultado['log'] = f.read().decode('utf-8', errors='replace')
            p = t['pasta']/'resultado.json'
            if t['status'] == 'concluido' and p.exists():
                resultado['resultado'] = json.loads(p.read_text(encoding='utf-8'))
            resultado['pasta'] = t['pasta'].relative_to(self.raiz).as_posix()
            return resultado


def criar_servidor(porta=8765, raiz=RAIZ):
    raiz = Path(raiz)
    trabalhos = Trabalhos(raiz)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def enviar_json(self, obj, status=200):
            corpo = json.dumps(obj, ensure_ascii=False, allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def host_valido(self):
            return self.headers.get('Host') in {
                f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}

        def do_GET(self):
            if not self.host_valido():
                self.send_error(403)
                return
            try:
                url = urlsplit(self.path)
                rota = unquote(url.path)
                params = parse_qs(url.query)
                if rota == '/api/catalogo':
                    self.enviar_json({**catalogo(raiz), 'token': token,
                                      'trabalhos': [trabalhos.estado(k) for k in list(trabalhos.itens)]})
                    return
                if rota.startswith('/api/trabalho/'):
                    self.enviar_json(trabalhos.estado(rota.rsplit('/', 1)[-1]))
                    return
                if rota == '/api/tabela':
                    p = caminho_publico(params.get('arquivo', [''])[0], raiz)
                    offset = max(0, int(params.get('offset', ['0'])[0]))
                    busca = params.get('busca', [''])[0].casefold()
                    if p.suffix in ('.csv', '.tsv'):
                        linhas, total = [], 0
                        with p.open(encoding='utf-8-sig', newline='') as f:
                            leitor = csv.DictReader(f, delimiter='\t' if p.suffix == '.tsv' else ',')
                            colunas = leitor.fieldnames
                            for row in leitor:
                                if busca and busca not in str(row).casefold():
                                    continue
                                if offset <= total < offset+50:
                                    linhas.append(row)
                                total += 1
                        self.enviar_json({'colunas': colunas, 'linhas': linhas, 'total': total})
                    elif p.suffix == '.json':
                        obj = json.loads(p.read_text(encoding='utf-8-sig'))
                        self.enviar_json(normalizar(obj))
                    else:
                        raise ValueError('Escolha CSV, TSV ou JSON.')
                    return
                if rota in ('/', '/app.css', '/app.js'):
                    p = raiz/'src/templates'/({'/': 'interface.html', '/app.css': 'interface.css', '/app.js': 'interface.js'}[rota])
                elif rota.startswith('/arquivo/'):
                    p = caminho_publico(rota[len('/arquivo/'):], raiz)
                else:
                    self.send_error(404)
                    return
                if not p.is_file():
                    self.send_error(404)
                    return
                tipo = mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
                self.send_response(200)
                self.send_header('Content-Type', tipo + ('; charset=utf-8' if tipo.startswith('text/') else ''))
                self.send_header('Content-Length', str(p.stat().st_size))
                self.send_header('X-Content-Type-Options', 'nosniff')
                if p.suffix not in ('.html', '.css', '.js', '.png', '.svg', '.pdf'):
                    self.send_header('Content-Disposition', 'attachment')
                self.end_headers()
                with p.open('rb') as f:
                    while bloco := f.read(65536):
                        self.wfile.write(bloco)
            except (ValueError, OSError, KeyError, csv.Error) as erro:
                self.enviar_json({'erro': str(erro)}, 400)

        def do_POST(self):
            if not self.host_valido():
                self.send_error(403)
                return
            try:
                if self.headers.get('X-Project-Token') != token:
                    self.enviar_json({'erro': 'Recarregue a interface para iniciar uma execução.'}, 403)
                    return
                tamanho = int(self.headers.get('Content-Length', '0'))
                if not 0 < tamanho <= 200000:
                    raise ValueError('Requisição vazia ou grande demais.')
                dados = json.loads(self.rfile.read(tamanho))
                if self.path == '/api/executar':
                    self.enviar_json({'id': trabalhos.iniciar(dados)}, 202)
                elif self.path == '/api/cancelar':
                    trabalhos.cancelar(dados['id'])
                    self.enviar_json({'ok': True})
                else:
                    self.send_error(404)
            except (ValueError, OSError, KeyError, TypeError) as erro:
                self.enviar_json({'erro': str(erro)}, 400)

    servidor = ThreadingHTTPServer(('127.0.0.1', porta), Handler)
    servidor.trabalhos = trabalhos
    return servidor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--porta', type=int, default=8765)
    parser.add_argument('--worker', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        executar_trabalho(json.load(sys.stdin), args.worker)
        return
    servidor = criar_servidor(args.porta)
    print(f'Interface: http://127.0.0.1:{servidor.server_port}', flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for chave in list(servidor.trabalhos.itens):
            servidor.trabalhos.cancelar(chave)
        servidor.server_close()


if __name__ == '__main__':
    main()
