"""[IA] Codex – execução de Bellman-Ford nos grafos de estados dos mapas."""
from pathlib import Path
import csv
import json

from .graphs.io import ler_mapa
from .graphs.estados import construir_grafo_estados
from .graphs.algorithms import bellman_ford, reconstruir_caminho


def resolver_mapa(caminho, fonte_consumivel=False):
    matriz, inicio, _ = ler_mapa(caminho)
    grafo = construir_grafo_estados(matriz, inicio, fonte_consumivel)
    resultado = bellman_ford(grafo['vertices'], grafo['arestas'], grafo['inicio'])
    custo = resultado['distancias']['ALVO']
    status = ('CICLO_NEGATIVO' if resultado['tem_ciclo_negativo'] else
              'SEM_SOLUCAO' if custo == float('inf') else 'OK')
    # Um ciclo alcançável pode existir sem afetar o caminho até ALVO.
    caminho_estados = (reconstruir_caminho(resultado, 'ALVO')
                       if custo not in (float('inf'), float('-inf')) else [])
    percurso = []
    acumulado = 0
    pesos = {(u, v): p for u, v, p in grafo['arestas']}
    for indice, rotulo in enumerate(caminho_estados):
        if rotulo == 'ALVO':
            continue
        if indice:
            acumulado += pesos[(caminho_estados[indice-1], rotulo)]
        posicao, chaves, consumidos = grafo['estados'][rotulo]
        percurso.append({'estado': rotulo, 'posicao': list(posicao),
                         'chaves': sorted(chaves),
                         'consumidos_posicoes': [list(p) for p in sorted(consumidos)],
                         'custo_acumulado': acumulado})
    relatorio = {
        'mapa': Path(caminho).stem, 'algoritmo': 'BELLMAN_FORD',
        'fonte_consumivel': fonte_consumivel, 'status': status,
        'custo': custo if custo not in (float('inf'), float('-inf')) else None,
        'custo_sem_limite': custo == float('-inf'),
        'passos': len(percurso)-1 if percurso else None,
        'arestas_ate_alvo': len(caminho_estados)-1 if caminho_estados else None,
        'caminho': caminho_estados, 'percurso': percurso,
        'estados_alcancaveis': len(grafo['estados']),
        'arcos_com_alvo': len(grafo['arestas']),
        'ciclo_negativo': resultado['ciclo_negativo'],
        'arestas_ciclo': resultado['arestas_ciclo'],
        'custo_ciclo': resultado['custo_ciclo'],
        'ciclo_afeta_alvo': 'ALVO' in resultado['afetados_ciclo_negativo'],
    }
    return relatorio, grafo


def exportar_resultado(relatorio, grafo, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    nome = relatorio['mapa']
    sufixo = '_fonte_consumivel' if relatorio['fonte_consumivel'] else ''
    def salvar_json(nome_arquivo, dados):
        (pasta / nome_arquivo).write_text(
            json.dumps(dados, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    salvar_json(f'resultado_{nome}{sufixo}.json', relatorio)
    if relatorio['ciclo_negativo']:
        salvar_json(f'ciclo_negativo_{nome.split("_")[0]}{sufixo}.json', {
            'estados': relatorio['ciclo_negativo'], 'arestas': relatorio['arestas_ciclo'],
            'custo': relatorio['custo_ciclo']})
    if relatorio['percurso']:
        salvar_json(f'percurso_{nome.split("_")[0]}{sufixo}.json', relatorio['percurso'])
    with (pasta / f'arestas_{nome}{sufixo}.csv').open('w', encoding='utf-8', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(['origem', 'destino', 'movimento', 'casa_destino', 'peso'])
        escritor.writerows(grafo['registros'])
    # Atualiza somente a solução deste mapa/algoritmo/modo, preservando as demais.
    arquivo_solucoes = pasta / 'solucoes.csv'
    campos = ['mapa', 'algoritmo', 'passos', 'custo', 'status', 'caminho']
    identificador = nome + sufixo
    linhas = []
    if arquivo_solucoes.exists():
        with arquivo_solucoes.open(encoding='utf-8', newline='') as arquivo:
            linhas = [linha for linha in csv.DictReader(arquivo)
                      if (linha['mapa'], linha['algoritmo']) != (identificador, 'BELLMAN_FORD')]
    linha = {campo: relatorio[campo] for campo in campos}
    linha['mapa'] = identificador
    linha['caminho'] = json.dumps(relatorio['caminho'], ensure_ascii=False)
    linhas.append(linha)
    with arquivo_solucoes.open('w', encoding='utf-8', newline='') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)
