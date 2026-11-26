
"""Entrada, resolução e exportação dos labirintos."""

from pathlib import Path
import argparse
import csv
import json
import sys

# Permite executar python -m src.main ou python src/main.py.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.graphs.metricas import (
    calcular_pacote_mapa, calcular_pacote_metricas,
    calcular_metricas_percurso, exportar_pacotes_metricas,
)
from src.graphs.io import ler_mapa, exibir_mapa
from src.graphs.estados import construir_grafo_estados, verificar_vizinhos
from src.graphs.algorithms import (
    bellman_ford,
    BFS,
    DFS,
    djikstra,
    reconstruir_caminho,
)


# [IA] ChatGPT - correção de sintaxe e integração da CLI/exportações.
def resolver_mapa(caminho, fonte_consumivel=False, algoritmo='BELLMAN_FORD'):
    matriz, inicio, _ = ler_mapa(caminho)
    grafo = construir_grafo_estados(matriz, inicio, fonte_consumivel)
    estrutura = grafo['grafo']
    pacote_metricas = calcular_pacote_metricas(
        matriz, grafo, Path(caminho).stem, fonte_consumivel
    )
    grafo['metricas'] = pacote_metricas
    metricas_globais = pacote_metricas['globais']

    algoritmos = {
        'BELLMAN_FORD': bellman_ford,
        'BFS': BFS,
        'DFS': DFS,
        'DIJKSTRA': djikstra,
    }

    if algoritmo not in algoritmos:
        raise ValueError(f'Algoritmo desconhecido: {algoritmo}')

    motivo_recusa = None

    try:
        resultado = algoritmos[algoritmo](
            estrutura.vertices,
            estrutura.arestas,
            grafo['inicio']
        )

    except ValueError as erro:
        if (
            algoritmo == 'DIJKSTRA'
            and str(erro) == "Dijkstra não aceita pesos negativos."
        ):
            motivo_recusa = str(erro)
            resultado = {}
        else:
            raise

    distancia = (
        None if motivo_recusa
        else resultado['distancias']['ALVO']
    )

    ciclo_negativo = resultado.get('tem_ciclo_negativo', False)

    status = (
        'RECUSA' if motivo_recusa else
        'CICLO_NEGATIVO' if ciclo_negativo else
        'SEM_SOLUCAO' if distancia == float('inf') else
        'OK'
    )

    caminho_estados = (
        reconstruir_caminho(resultado, 'ALVO')
        if not motivo_recusa
        and distancia not in (float('inf'), float('-inf'))
        else []
    )

    percurso = []
    acumulado = 0

    pesos = {
        (origem, destino): peso
        for origem, destino, peso in grafo['arestas']
    }

    for indice, rotulo in enumerate(caminho_estados):
        if rotulo == 'ALVO':
            continue

        if indice > 0:
            anterior = caminho_estados[indice - 1]
            acumulado += pesos[(anterior, rotulo)]

        posicao, chaves, consumidos = grafo['estados'][rotulo]

        percurso.append({
            'estado': rotulo,
            'posicao': list(posicao),
            'chaves': sorted(chaves),
            'consumidos_posicoes': [
                list(p) for p in sorted(consumidos)
            ],
            'custo_acumulado': acumulado,
        })

    metricas_percurso = calcular_metricas_percurso(percurso)

    relatorio = {
        'mapa': Path(caminho).stem,
        'algoritmo': algoritmo,
        'fonte_consumivel': fonte_consumivel,
        'status': status,
        'motivo_recusa': motivo_recusa,
        'custo': metricas_percurso['custo'],
        'custo_sem_limite': distancia == float('-inf'),
        'passos': metricas_percurso['passos'],
        'arestas_ate_alvo': (
            len(caminho_estados) - 1 if caminho_estados else None
        ),
        'caminho': caminho_estados,
        'percurso': percurso,
        'classificacao_arestas': resultado.get('classificacao_arestas', []),
        'tem_ciclo': resultado.get('tem_ciclo', False),
        'metricas_globais': metricas_globais,
        'metricas_percurso': metricas_percurso,
        # Campos mantidos para os consumidores anteriores do relatório.
        'estados_alcancaveis': metricas_globais['G_est']['ordem'],
        'arcos_com_alvo': len(grafo['arestas']),
        'ciclo_negativo': resultado.get('ciclo_negativo', []),
        'arestas_ciclo': resultado.get('arestas_ciclo', []),
        'custo_ciclo': resultado.get('custo_ciclo'),
        'ciclo_afeta_alvo': (
            'ALVO' in resultado.get(
                'afetados_ciclo_negativo', set()
            )
        ),
    }

    return relatorio, grafo


# [IA] ChatGPT - correção de colchetes e separação dos resultados por algoritmo.
def exportar_resultado(relatorio, grafo, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)

    nome = relatorio['mapa']

    sufixo_algoritmo = (
        '' if relatorio['algoritmo'] == 'BELLMAN_FORD'
        else '_' + relatorio['algoritmo'].lower()
    )

    sufixo_fonte = (
        '_fonte_consumivel'
        if relatorio['fonte_consumivel']
        else ''
    )

    sufixo = sufixo_algoritmo + sufixo_fonte

    def salvar_json(nome_arquivo, dados):
        (pasta / nome_arquivo).write_text(
            json.dumps(
                dados,
                ensure_ascii=False,
                indent=2,
                allow_nan=False
            ),
            encoding='utf-8'
        )

    salvar_json(f'resultado_{nome}{sufixo}.json', relatorio)
    exportar_pacotes_metricas([grafo['metricas']], pasta)

    if relatorio['ciclo_negativo']:
        salvar_json(
            f'ciclo_negativo_{nome.split("_")[0]}{sufixo}.json',
            {
                'estados': relatorio['ciclo_negativo'],
                'arestas': relatorio['arestas_ciclo'],
                'custo': relatorio['custo_ciclo'],
            }
        )

    if relatorio['percurso']:
        salvar_json(
            f'percurso_{nome.split("_")[0]}{sufixo}.json',
            relatorio['percurso']
        )

    with (
        pasta / f'arestas_{nome}{sufixo}.csv'
    ).open('w', encoding='utf-8', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([
            'origem',
            'destino',
            'movimento',
            'casa_destino',
            'peso'
        ])
        escritor.writerows(grafo['registros'])

   
    if relatorio['algoritmo'] == 'DFS':

        classificacoes = {
            'arvore': 0,'retorno': 0,'avanco': 0,'cruzamento': 0
        }

        for origem, destino, tipo in relatorio['classificacao_arestas']:
            classificacoes[tipo] += 1

        arquivo_dfs = pasta / 'dfs_classificacao.csv'

        campos_dfs = [
            'mapa',
            'arvore',
            'retorno',
            'avanco',
            'cruzamento']

        linhas_dfs = []

        if arquivo_dfs.exists():
            with arquivo_dfs.open(
                'r', encoding='utf-8', newline=''
            ) as arquivo:

                linhas_dfs = [
                    linha
                    for linha in csv.DictReader(arquivo)
                    if linha['mapa'] != nome
                ]

        linhas_dfs.append({
            'mapa': nome,
            'arvore': classificacoes['arvore'],
            'retorno': classificacoes['retorno'],
            'avanco': classificacoes['avanco'],
            'cruzamento': classificacoes['cruzamento']})

        with arquivo_dfs.open('w', encoding='utf-8', newline=''
        ) as arquivo:

            escritor = csv.DictWriter(
                arquivo,
                fieldnames=campos_dfs)

            escritor.writeheader()
            escritor.writerows(linhas_dfs)


    # Preserva os resultados dos outros algoritmos.
    arquivo_solucoes = pasta / 'solucoes.csv'

    campos = [
        'mapa',
        'algoritmo',
        'passos',
        'custo',
        'status',
        'caminho'
    ]

    identificador = nome + sufixo_fonte
    linhas = []

    if arquivo_solucoes.exists():
        with arquivo_solucoes.open(
            encoding='utf-8',
            newline=''
        ) as arquivo:
            linhas = [
                linha
                for linha in csv.DictReader(arquivo)
                if (
                    linha['mapa'],
                    linha['algoritmo']
                ) != (
                    identificador,
                    relatorio['algoritmo']
                )
            ]

    linha = {
        campo: relatorio[campo]
        for campo in campos
    }

    linha['mapa'] = identificador
    linha['caminho'] = json.dumps(
        relatorio['caminho'],
        ensure_ascii=False
    )

    linhas.append(linha)

    with arquivo_solucoes.open(
        'w',
        encoding='utf-8',
        newline=''
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos
        )
        escritor.writeheader()
        escritor.writerows(linhas)


def demonstrar_mapa(nome_mapa):
    raiz = Path(__file__).resolve().parent.parent
    caminho = raiz / "data" / "mapas" / f"{nome_mapa}.txt"

    try:
        matriz, inicio, fim = ler_mapa(caminho)

    except (FileNotFoundError, ValueError) as erro:
        print(erro)
        return

    exibir_mapa(matriz)

    print("\nPosição inicial:", inicio)
    print("Posição final:", fim)

    vizinhos = verificar_vizinhos(
        matriz,
        (inicio, frozenset(), frozenset())
    )

    print("\nVizinhos válidos:", vizinhos)


def main():
    # [IA] ChatGPT – indicação da ajuda da CLI da Parte 2.
    parser = argparse.ArgumentParser(
        description='Algoritmos de grafos em labirintos com estados.',
        epilog='Parte 2: python -m src.cli --dataset CAMINHO --help'
    )

    parser.add_argument(
        'nome_mapa',
        nargs='?',
        help='Demonstração antiga: m02_uma_chave'
    )

    parser.add_argument('--mapa')

    parser.add_argument('--armadilhas', action='store_true')
    parser.add_argument('--interactive', action='store_true')
    execucao = parser.add_mutually_exclusive_group()
    execucao.add_argument('--parte1-completa', action='store_true')
    execucao.add_argument(
        '--metricas',
        action='store_true',
        help='Calcula métricas de --mapa ou de todos os mapas das pastas data.'
    )
    execucao.add_argument(
        '--alg',
        choices=['BELLMAN_FORD', 'BFS', 'DFS', 'DIJKSTRA'],
        default='BELLMAN_FORD'
    )

    parser.add_argument(
        '--out',
        default='out/parte1'
    )

    parser.add_argument(
        '--fonte-consumivel',
        action='store_true'
    )

    args = parser.parse_args()

    if args.parte1_completa:
        from src.solve import gerar_parte1
        print(json.dumps(gerar_parte1(args.out), ensure_ascii=False, indent=2))
        return

    if args.metricas:
        if args.nome_mapa:
            parser.error('Com --metricas, informe o caminho usando --mapa.')
        raiz = Path(__file__).resolve().parent.parent
        caminhos = ([Path(args.mapa)] if args.mapa else
                    sorted((raiz / 'data/mapas').glob('*.txt')) +
                    sorted((raiz / 'data/mapas_grupo').glob('*.txt')))
        if not caminhos:
            parser.error('Nenhum mapa encontrado para calcular as métricas.')
        if len({p.stem for p in caminhos}) != len(caminhos):
            parser.error('Os mapas devem ter nomes distintos para a exportação.')
        try:
            metricas = [calcular_pacote_mapa(p, args.fonte_consumivel)
                        for p in caminhos]
            arquivo = exportar_pacotes_metricas(metricas, args.out)
        except (OSError, ValueError) as erro:
            parser.exit(1, f'Erro: {erro}\n')
        print(json.dumps({'mapas_processados': len(metricas),
                          'arquivo': str(arquivo)}, ensure_ascii=False, indent=2))
        return

    if args.nome_mapa:
        if args.mapa:
            parser.error(
                'Use o nome do mapa ou --mapa, não os dois.'
            )

        demonstrar_mapa(args.nome_mapa)
        return

    if not args.mapa:
        parser.error(
            'Informe --mapa ou o nome do mapa para demonstração.'
        )

    try:
        relatorio, grafo = resolver_mapa(
            args.mapa,
            args.fonte_consumivel,
            args.alg
        )

        exportar_resultado(
            relatorio,
            grafo,
            args.out
        )
        if args.armadilhas:
            from src.graphs.analises import exportar_armadilhas
            exportar_armadilhas(grafo, relatorio['mapa'], args.out)
        if args.interactive:
            from src.solve import gerar_parte1
            gerar_parte1(args.out, mapa_extra=args.mapa)

    except (OSError, ValueError) as erro:
        parser.exit(1, f'Erro: {erro}\n')

    resumo = {
        k: relatorio[k]
        for k in (
            'mapa',
            'algoritmo',
            'status',
            'motivo_recusa',
            'passos',
            'custo',
            'estados_alcancaveis',
            'custo_ciclo',
            'ciclo_afeta_alvo'
        )
    }

    print(
        json.dumps(
            resumo,
            ensure_ascii=False,
            indent=2
        )
    )


if __name__ == '__main__':
    main()
