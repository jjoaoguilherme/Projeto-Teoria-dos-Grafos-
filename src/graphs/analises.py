"""Armadilhas e comparações, reutilizando os algoritmos do projeto."""
import csv
from .algorithms import BFS, bellman_ford, reconstruir_caminho
from .estados import construir_grafo_estados, construir_grafo_posicoes


def estados_armadilha(dados):
    transposto = dados['grafo'].transposto()
    busca = BFS(transposto.vertices, transposto.arestas, 'ALVO')
    return sorted(r for r in dados['estados'] if busca['distancias'][r] == float('inf'))


def exportar_armadilhas(dados, nome, pasta):
    from pathlib import Path
    caminho = Path(pasta) / f'armadilhas_{nome.split("_")[0]}.csv'
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f);w.writerow(['estado'])
        w.writerows((r,) for r in estados_armadilha(dados))
    return caminho


def comparar_modelagens(matriz, inicio, nome):
    linhas = []
    for modo in ['chao', 'parede']:
        g = construir_grafo_posicoes(matriz, modo)
        resultado = BFS(g.vertices, g.arestas, inicio)
        saidas = [v for v in g.vertices if matriz[v[0]][v[1]] == 'G']
        fim = min(saidas, key=lambda v: (resultado['distancias'][v], v))
        caminho = reconstruir_caminho(resultado, fim)
        valido = bool(caminho)
        chaves = set()
        for i,j in caminho:
            s = matriz[i][j]
            if s in 'ABCD' and s.lower() not in chaves: valido = False
            if s in 'abcd': chaves.add(s)
        linhas.append({'mapa': nome, 'abordagem': 'G_pos_portas_'+modo,
                       'passos': len(caminho)-1 if caminho else None,
                       'caminho_valido': valido,
                       'observacao': 'Validação pelas regras de chaves; sem caminho' if not caminho else
                       ('Caminho respeita portas' if valido else 'Atravessa porta sem chave')})
    dados = construir_grafo_estados(matriz, inicio)
    r = BFS(dados['vertices'], dados['arestas'], dados['inicio'])
    caminho = reconstruir_caminho(r, 'ALVO')
    linhas.append({'mapa': nome, 'abordagem': 'G_est',
                   'passos': len(caminho)-2 if caminho else None,
                   'caminho_valido': bool(caminho), 'observacao': 'Modelo com inventário'})
    return linhas


def comparar_bonus(matriz, inicio):
    g = construir_grafo_posicoes(matriz)
    pos = bellman_ford(g.vertices, g.arestas, inicio)
    d = construir_grafo_estados(matriz, inicio)
    est = bellman_ford(d['vertices'], d['arestas'], d['inicio'])
    return {'G_pos': {'ciclo_negativo': pos['ciclo_negativo'], 'custo_ciclo': pos['custo_ciclo']},
            'G_est': {'tem_ciclo_negativo': est['tem_ciclo_negativo'], 'custo': est['distancias']['ALVO']}}
