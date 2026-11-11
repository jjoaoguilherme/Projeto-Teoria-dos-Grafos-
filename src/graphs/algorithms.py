"""Algoritmos de grafos. BFS, DFS e Dijkstra ainda serão implementados."""

from collections import deque


# [IA] Codex – Bellman-Ford baseado no relaxamento escrito pelo usuário.
def bellman_ford(vertices, arestas, inicio):
    """Recebe arestas (origem, destino, peso) e retorna um dicionário.

    Distância inf: inalcançável. Distância -inf: afetado por ciclo negativo.
    O ciclo retornado é fechado, com o primeiro vértice repetido no final.
    """
    vertices = list(dict.fromkeys(vertices))
    arestas = list(arestas)
    conjunto_vertices = set(vertices)
    if inicio not in conjunto_vertices:
        raise ValueError("O vértice inicial não pertence ao grafo.")
    adjacencia = {v: [] for v in vertices}
    for origem, destino, peso in arestas:
        if origem not in conjunto_vertices or destino not in conjunto_vertices:
            raise ValueError("Aresta com vértice que não pertence ao grafo.")
        if not float('-inf') < peso < float('inf'):
            raise ValueError("Os pesos devem ser números finitos.")
        adjacencia[origem].append(destino)

    distancias = {v: float('inf') for v in vertices}
    predecessores = {v: None for v in vertices}
    arestas_predecessoras = {}
    distancias[inicio] = 0

    # Laço externo repete a passagem completa pelas arestas.
    for _ in range(len(vertices) - 1):
        alterou = False
        for origem, destino, peso in arestas:
            if distancias[origem] == float('inf'):
                continue
            novo_custo = distancias[origem] + peso
            if novo_custo < distancias[destino]:
                distancias[destino] = novo_custo
                predecessores[destino] = origem
                arestas_predecessoras[destino] = (origem, destino, peso)
                alterou = True
        if not alterou:
            break

    # Uma melhoria na passagem extra indica ciclo negativo alcançável.
    alterados = []
    for origem, destino, peso in arestas:
        if distancias[origem] == float('inf'):
            continue
        novo_custo = distancias[origem] + peso
        if novo_custo < distancias[destino]:
            distancias[destino] = novo_custo
            predecessores[destino] = origem
            arestas_predecessoras[destino] = (origem, destino, peso)
            alterados.append(destino)

    ciclo = []
    arestas_ciclo = []
    custo_ciclo = None
    afetados = set(alterados)
    if alterados:
        atual = alterados[-1]
        # Recuar |V| vezes entra no ciclo da cadeia de predecessores.
        for _ in vertices:
            atual = predecessores[atual]
        primeiro = atual
        ciclo = [primeiro]
        atual = predecessores[primeiro]
        while atual != primeiro:
            ciclo.append(atual)
            atual = predecessores[atual]
        ciclo.append(primeiro)
        ciclo.reverse()
        arestas_ciclo = [arestas_predecessoras[v] for v in ciclo[1:]]
        custo_ciclo = sum(peso for _, _, peso in arestas_ciclo)

        # Propaga a influência dos ciclos negativos aos seus descendentes.
        fila = deque(alterados)
        while fila:
            origem = fila.popleft()
            for destino in adjacencia[origem]:
                if destino not in afetados:
                    afetados.add(destino)
                    fila.append(destino)
        for v in afetados:
            distancias[v] = float('-inf')

    return {
        'inicio': inicio,
        'distancias': distancias,
        'predecessores': predecessores,
        'tem_ciclo_negativo': bool(alterados),
        'ciclo_negativo': ciclo,
        'arestas_ciclo': arestas_ciclo,
        'custo_ciclo': custo_ciclo,
        'afetados_ciclo_negativo': afetados,
    }


# reconstrução de caminhos pelos predecessores.
def reconstruir_caminho(resultado, destino):
    """Retorna [] se inalcançável; recusa destino afetado por ciclo negativo."""
    distancia = resultado['distancias'][destino]
    if distancia == float('inf'):
        return []
    if distancia == float('-inf'):
        raise ValueError('Não há menor caminho: destino afetado por ciclo negativo.')
    caminho = []
    atual = destino
    while True:
        caminho.append(atual)
        if atual == resultado['inicio']:
            break
        atual = resultado['predecessores'][atual]
    caminho.reverse()
    return caminho


if __name__ == '__main__':
    # Exemplo original do usuário; não executa ao importar o módulo.
    vertices = ['A', 'B', 'C', 'D']
    arestas = [
        ('A', 'B', 4),
        ('A', 'C', 3),
        ('C', 'B', -2),
        ('B', 'D', 5),
        ('C', 'D', 6),
    ]
    resultado = bellman_ford(vertices, arestas, 'A')
    print('Distâncias:', resultado['distancias'])
    print('Caminho até D:', reconstruir_caminho(resultado, 'D'))
    print('Ciclo negativo:', resultado['ciclo_negativo'])
