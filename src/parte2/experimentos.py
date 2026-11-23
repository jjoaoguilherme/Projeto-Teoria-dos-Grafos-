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


def main():
    """Exemplo pequeno, explicitamente separado dos experimentos finais."""
    import argparse
    parser = argparse.ArgumentParser(description='Demonstrar infraestrutura de medição.')
    parser.add_argument('--demonstracao', action='store_true', required=True)
    parser.add_argument('--repeticoes', type=int, default=5)
    parser.add_argument('--out', default='out/parte2/demonstracao_report.json')
    args = parser.parse_args()
    vertices = ['A', 'B', 'C', 'D']
    arestas = [('A', 'B', 4), ('A', 'C', 3), ('C', 'B', 2), ('B', 'D', 5), ('C', 'D', 6)]
    ambiente = registrar_ambiente()
    try:
        experimentos = [medir_algoritmo(nome, vertices, arestas, 'A', args.repeticoes,
                                       identificacao={'grafo': 'exemplo pequeno; não é o dataset'})
                        for nome in ALGORITMOS]
        destino = exportar_relatorio(experimentos, args.out, ambiente, demonstracao=True)
    except (ValueError, OSError) as erro:
        parser.exit(1, f'Erro: {erro}\n')
    print(f'Demonstração salva em {destino}')


if __name__ == '__main__':
    main()
