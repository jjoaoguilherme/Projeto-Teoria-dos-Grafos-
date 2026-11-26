"""CLI da Parte 2: consultas e benchmark dos algoritmos existentes.

[IA] ChatGPT – integração dos executores já implementados pelo grupo.
"""
import argparse
import json
from math import isfinite
from pathlib import Path

from src.graphs.algorithms import reconstruir_caminho
from .experimentos import (
    ALGORITMOS, carregar_grafo_experimento, detalhes_busca,
    executar_bfs_dfs_dataset, executar_dijkstra, executar_bellman_ford,
    casos_bellman_ford, verificar_casos_bellman_ford, exportar_relatorio,
    registrar_ambiente,
)
from .escalabilidade import medir_escalabilidade
from .consolidar import consolidar_relatorios
from .obter_dataset import calcular_sha256


def executar_benchmark(caminho, grafo, pasta, repeticoes=5, limite_vertices=2000):
    pasta = Path(pasta)
    procedencias = verificar_casos_bellman_ford(grafo, caminho)
    fontes = ['subredditdrama', 'bestof', 'titlegore']
    executar_bfs_dfs_dataset(caminho, fontes, repeticoes,
                             pasta / 'bfs_dfs_report.json', grafo=grafo)
    exportar_relatorio(executar_dijkstra(caminho, repeticoes, grafo=grafo),
                      pasta / 'dijkstra_report.json')
    exportar_relatorio(executar_bellman_ford(casos_bellman_ford, repeticoes, procedencias),
                      pasta / 'bellman_ford_report.json')
    # Mesmo recorte-base e semente utilizados no estudo de desempenho original.
    limite = min(limite_vertices, len(grafo.vertices))
    ambiente = registrar_ambiente()
    experimentos = medir_escalabilidade(
        grafo, fontes[0], (0.1, 0.5, 1.0), repeticoes, 42, limite,
        {'arquivo': str(caminho), 'sha256': calcular_sha256(caminho)})
    exportar_relatorio(experimentos, pasta / 'escalabilidade_report.json', ambiente)
    return consolidar_relatorios(pasta)


def consultar(grafo, nome, origem, destino=None):
    vertices, arestas = grafo.vertices, grafo.arestas
    if origem not in vertices or (destino is not None and destino not in vertices):
        raise ValueError('Origem ou destino não encontrado no dataset.')
    if nome == 'DIJKSTRA':
        arestas = [(u, v, 2 - peso) for u, v, peso in arestas]
    resultado = ALGORITMOS[nome](vertices, arestas, origem)
    dados = {'algoritmo': nome, 'origem': origem, 'destino': destino,
             'vertices': len(vertices), 'arestas': len(arestas),
             'pesos': '2 - LINK_SENTIMENT' if nome == 'DIJKSTRA' else 'LINK_SENTIMENT original'}
    if nome in ('BFS', 'DFS'):
        dados.update(detalhes_busca(nome, resultado))
    if nome == 'BELLMAN_FORD':
        for campo in ('tem_ciclo_negativo', 'ciclo_negativo', 'arestas_ciclo', 'custo_ciclo'):
            dados[campo] = resultado[campo]
    if destino is not None:
        custo = resultado['distancias'][destino]
        dados['custo'] = custo if isfinite(custo) else None
        dados['status'] = ('CICLO_NEGATIVO' if custo == float('-inf') else
                           'INALCANCAVEL' if custo == float('inf') else 'OK')
        dados['caminho'] = reconstruir_caminho(resultado, destino) if isfinite(custo) else []
    else:
        dados['distancias'] = {v: d if isfinite(d) else None
                               for v, d in resultado['distancias'].items()}
    return dados


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', required=True, type=Path,
                        help='Diretório do TSV, arquivo TSV ou CSV de arcos preparado.')
    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument('--alg', choices=list(ALGORITMOS))
    modo.add_argument('--benchmark', action='store_true')
    parser.add_argument('--source', help='Subreddit de origem.')
    parser.add_argument('--target', help='Subreddit de destino.')
    parser.add_argument('--out', type=Path, default=Path('out/parte2'))
    parser.add_argument('--repeticoes', type=int, default=5)
    parser.add_argument('--limite-vertices', type=int, default=2000,
                        help='Limite do recorte-base para escalabilidade (benchmark).')
    args = parser.parse_args()
    if args.alg and not args.source:
        parser.error('--alg exige --source.')
    if args.benchmark and (args.source or args.target):
        parser.error('--benchmark utiliza os casos obrigatórios já definidos.')
    if args.repeticoes < 5 or args.limite_vertices < 3:
        parser.error('Use pelo menos 5 repetições e limite de 3 vértices.')
    caminho = args.dataset
    if caminho.is_dir():
        caminho /= 'soc-redditHyperlinks-title.tsv'
    try:
        grafo = carregar_grafo_experimento(caminho)
        if args.benchmark:
            destino = executar_benchmark(caminho, grafo, args.out,
                                          args.repeticoes, args.limite_vertices)
        else:
            if args.alg == 'BELLMAN_FORD':
                print('Aviso: Bellman-Ford no grafo completo pode demorar muito.', flush=True)
            dados = consultar(grafo, args.alg, args.source, args.target)
            dados['dataset'] = str(caminho)
            args.out.mkdir(parents=True, exist_ok=True)
            destino = args.out / f'consulta_{args.alg.lower()}.json'
            destino.write_text(json.dumps(dados, ensure_ascii=False, indent=2,
                                          allow_nan=False) + '\n', encoding='utf-8')
            if args.target is not None:
                print(json.dumps({k: dados[k] for k in ('status', 'custo', 'caminho')},
                                 ensure_ascii=False))
        print(f'Resultado salvo em {destino}')
    except (OSError, ValueError, KeyError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
