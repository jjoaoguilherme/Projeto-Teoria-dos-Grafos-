"""Infraestrutura de medição; não define os casos finais do dataset.

[IA] Codex – implementação de medições, ambiente e exportação de experimentos.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import time

from src.graphs.algorithms import BFS, DFS, bellman_ford, djikstra

ALGORITMOS = {'BFS': BFS, 'DFS': DFS, 'DIJKSTRA': djikstra,
              'BELLMAN_FORD': bellman_ford}
RAIZ = Path(__file__).resolve().parents[2]


def registrar_ambiente():
    """Coleta metadados fora da região cronometrada, sem dados pessoais."""
    try:
        commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=RAIZ,
                                capture_output=True, text=True, check=True).stdout.strip()
        alteracoes = subprocess.run(['git', 'status', '--porcelain'], cwd=RAIZ,
                                    capture_output=True, text=True, check=True).stdout
        modificado = bool(alteracoes)
    except (OSError, subprocess.CalledProcessError):
        commit, modificado = None, None
    relogio = time.get_clock_info('perf_counter')
    return {'python': platform.python_version(), 'implementacao_python': platform.python_implementation(),
            'sistema': platform.system(), 'versao_sistema': platform.release(),
            'arquitetura': platform.machine(), 'processador': platform.processor() or None,
            'commit': commit, 'diretorio_com_alteracoes': modificado,
            'relogio': 'time.perf_counter', 'resolucao_relogio_segundos': relogio.resolution}


def medir_algoritmo(algoritmo, vertices, arestas, inicio, repeticoes=5,
                    tarefa='caminhos_a_partir_da_origem', identificacao=None):
    """Mede chamadas independentes com a mesma entrada, pelo menos cinco vezes.

    Aceita os nomes de ALGORITMOS ou uma função com contrato
    (vertices, arestas, inicio). Identificadores de origem devem ser JSON
    serializáveis. Leitura, preparação, validação externa e exportação ficam
    fora do relógio; validações internas do algoritmo fazem parte da chamada.
    Exceções propagam: uma execução recusada não vira tempo de sucesso.
    """
    if isinstance(repeticoes, bool) or not isinstance(repeticoes, int) or repeticoes < 5:
        raise ValueError('Use pelo menos cinco repetições inteiras.')
    if isinstance(algoritmo, str):
        if algoritmo not in ALGORITMOS:
            raise ValueError('Algoritmo desconhecido: ' + algoritmo)
        nome, funcao = algoritmo, ALGORITMOS[algoritmo]
    else:
        if not callable(algoritmo):
            raise ValueError('Informe o nome do algoritmo ou uma função.')
        funcao = algoritmo
        nome = getattr(funcao, '__name__', type(funcao).__name__)
    vertices = list(vertices)
    arestas = list(arestas)
    # Confere antes de medir que os metadados podem ser exportados.
    json.dumps({'origem': inicio, 'identificacao': identificacao}, allow_nan=False)
    tempos = []
    estados_resultado = []
    for _ in range(repeticoes):
        comeco = time.perf_counter()
        resultado = funcao(vertices, arestas, inicio)
        fim = time.perf_counter()
        tempos.append(fim - comeco)
        estados_resultado.append('CICLO_NEGATIVO' if isinstance(resultado, dict)
                                and resultado.get('tem_ciclo_negativo') else 'OK')
        # Libera o retorno fora da medição, antes de iniciar a próxima chamada.
        del resultado
    return {'algoritmo': nome, 'tarefa': tarefa, 'origem': inicio,
            'identificacao': identificacao or {}, 'vertices': len(vertices),
            'arestas': len(arestas), 'repeticoes': repeticoes, 'unidade': 'segundos',
            'tempos_segundos': tempos, 'tempo_medio_segundos': sum(tempos) / repeticoes,
            'status_execucoes': estados_resultado}


def exportar_relatorio(experimentos, caminho='out/parte2/parte2_report.json',
                       ambiente=None, demonstracao=False):
    """Grava um relatório completo; o chamador reúne todos os casos na lista.

    Substitui o arquivo indicado, sem acumular medições de sessões diferentes.
    Não execute esta função dentro da região cronometrada.
    """
    dados = {'versao_formato': 1, 'gerado_em_utc': datetime.now(timezone.utc).isoformat(),
             'demonstracao': demonstracao,
             'ambiente': registrar_ambiente() if ambiente is None else ambiente,
             'metodo': {'relogio': 'time.perf_counter', 'unidade': 'segundos',
                        'escopo': 'chamada completa do algoritmo, incluindo validações internas',
                        'fora_da_medicao': ['leitura', 'construção do grafo', 'exportação', 'impressão'],
                        'aquecimento': 'nenhum', 'ordem': 'sequencial; mesma entrada em cada repetição'},
             'experimentos': list(experimentos)}
    texto = json.dumps(dados, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding='utf-8')
    return destino



def executar_bfs_dfs_dataset(caminho, fontes, repeticoes=5,
                             destino='out/parte2/bfs_dfs_report.json'):
    """Mede BFS/DFS nas fontes indicadas; não executa os demais casos da Parte 2.
    
    """
    from src.parte2.dados import carregar_dataset

    dados = carregar_dataset(caminho)
    grafo = dados['grafo']
    vertices, arestas = grafo.vertices, grafo.arestas
    desconhecidas = [fonte for fonte in fontes if fonte not in set(vertices)]
    if desconhecidas:
        raise ValueError('Fontes não encontradas no dataset: ' + ', '.join(desconhecidas))
    ambiente = registrar_ambiente()
    experimentos = []
    for nome in ('BFS', 'DFS'):
        for fonte in fontes:
            print(f'Executando {nome} a partir de {fonte} ({repeticoes} repetições)...', flush=True)
            medicao = medir_algoritmo(nome, vertices, arestas, fonte, repeticoes,
                                     identificacao={'dataset': str(caminho),
                                                    'origem_tipo': 'subreddit',
                                                    'caso': 'BFS_DFS_TRES_FONTES'})
            experimentos.append(medicao)
            print(f'  Média: {medicao["tempo_medio_segundos"]:.4f}s', flush=True)
    return exportar_relatorio(experimentos, destino, ambiente, demonstracao=False)

def main():
    """Permite executar a demonstração ou as seis medições BFS/DFS no Reddit."""
    import argparse
    parser = argparse.ArgumentParser(description='Infraestrutura de medições da Parte 2.')
    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument('--demonstracao', action='store_true')
    modo.add_argument('--bfs-dfs', action='store_true',
                      help='Executa BFS e DFS em três fontes do dataset real.')
    parser.add_argument('--arquivo', help='Caminho do arquivo TSV, para --bfs-dfs.')
    parser.add_argument('--fontes', nargs=3,
                        metavar=('FONTE1', 'FONTE2', 'FONTE3'),
                        help='Três subreddits de origem para --bfs-dfs.')
    parser.add_argument('--repeticoes', type=int, default=5)
    parser.add_argument('--out', help='Caminho do JSON de saída.')
    args = parser.parse_args()
    if args.bfs_dfs and not args.arquivo:
        parser.error('--bfs-dfs exige --arquivo.')
    if args.demonstracao and (args.arquivo or args.fontes):
        parser.error('--arquivo e --fontes são opções exclusivas de --bfs-dfs.')
    if args.repeticoes < 5:
        parser.error('É necessário executar pelo menos cinco repetições.')
    try:
        if args.bfs_dfs:
            fontes = args.fontes or ['subredditdrama', 'bestof', 'titlegore']
            if len(set(fontes)) != 3:
                parser.error('Informe três fontes distintas.')
            destino = executar_bfs_dfs_dataset(
                args.arquivo, fontes, args.repeticoes,
                args.out or 'out/parte2/bfs_dfs_report.json')
            print(f'Medições BFS/DFS salvas em {destino}')
        else:
            vertices = ['A', 'B', 'C', 'D']
            arestas = [('A', 'B', 4), ('A', 'C', 3), ('C', 'B', 2),
                       ('B', 'D', 5), ('C', 'D', 6)]
            ambiente = registrar_ambiente()
            experimentos = [medir_algoritmo(nome, vertices, arestas, 'A', args.repeticoes,
                                           identificacao={'grafo': 'exemplo pequeno; não é o dataset'})
                            for nome in ALGORITMOS]
            destino = exportar_relatorio(experimentos,
                                        args.out or 'out/parte2/demonstracao_report.json',
                                        ambiente, demonstracao=True)
            print(f'Demonstração salva em {destino}')
    except (ValueError, OSError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
