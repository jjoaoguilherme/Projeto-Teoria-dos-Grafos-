"""Algoritmos de grafos."""

from collections import deque


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
        fila = deque(dict.fromkeys(alterados))
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

#Implentação de BFS(Breadth-First Search)
def BFS(vertices, arestas, inicio):
    #Irá trabalhar  com arestas de origem e destino e retornará um dicionario com as distâncias e predecessores    
    vertices = list(dict.fromkeys(vertices))
    arestas = list(arestas)
    conjunto_vertices = set(vertices)

    if inicio not in conjunto_vertices:
        raise ValueError("O vértice inicial não pertence ao grafo.")
    
    adjacencia = {v: [] for v in vertices}

    for origem, destinho, peso in arestas:
        if origem not in conjunto_vertices or destinho not in conjunto_vertices:
            raise ValueError("Aresta com vértice que não pertence ao grafo.")
        adjacencia[origem].append((destinho))

    distancias = {v: float('inf') for v in vertices}
    predecessores = {v: None for v in vertices}
    distancias[inicio] = 0

    fila = deque([inicio])
    # [IA] ChatGPT – registro da ordem real de retirada da fila.
    ordem_visita = []

    while fila:
        atual = fila.popleft()
        ordem_visita.append(atual)

        for vizinho in adjacencia[atual]:
            if distancias[vizinho] == float('inf'):
                distancias[vizinho] = distancias[atual] + 1
                predecessores[vizinho] = atual
                fila.append(vizinho)
    return {
        'inicio': inicio,
        'distancias': distancias,
        'predecessores': predecessores,
        'ordem_visita': ordem_visita
        
    }

def DFS(vertices, arestas, inicio):
    #Receberá arestas
    #Explora vizinhos na ordem em que aparecem na lista das arestas  
    vertices = list(dict.fromkeys(vertices))
    arestas = list(arestas)
    conjunto_vertices = set(vertices)

    if inicio not in conjunto_vertices:
        raise ValueError("O vértice inicial não pertence ao grafo.")
    
    adjacencia = {v: [] for v in vertices}

    for origem, destinho, peso in arestas:
        if origem not in conjunto_vertices or destinho not in conjunto_vertices:
            raise ValueError("Aresta com vértice que não pertence ao grafo.")
        adjacencia[origem].append((destinho))

    #Branco: Sem visita
    #Cinza: Explorando
    #Preto: Exploração completa

    cores = {v: 'branco' for v in vertices}

    distancias = {v: float('inf') for v in vertices}
    predecessores = {v: None for v in vertices}
    descoberta = {v: None for v in vertices}
    finalizacao = {v: None for v in vertices}

    ordem_visita = []
    classificacao_arestas = []
    tem_ciclo = False
    tempo = 0

    #Start vertice de partida
    cores[inicio] = 'cinza'
    distancias[inicio] = 0
    tempo +=1
    descoberta[inicio] = tempo
    ordem_visita.append(inicio)

    pilha = [(inicio, iter(adjacencia[inicio]))]

    while pilha:
        atual, vizinhos = pilha[-1]

        try:
            vizinho = next(vizinhos)

        except StopIteration:
            cores[atual] = "preto"
            tempo += 1
            finalizacao[atual] = tempo
            pilha.pop()
            continue
        if cores[vizinho] == "branco":
            classificacao_arestas.append((atual,vizinho,"arvore"))

            predecessores[vizinho] = atual
            distancias[vizinho] = distancias[atual] + 1

            cores[vizinho] = "cinza"
            tempo += 1
            descoberta[vizinho] = tempo
            ordem_visita.append(vizinho)

            pilha.append((vizinho, iter(adjacencia[vizinho])))

        elif cores[vizinho] == "cinza":
            classificacao_arestas.append((atual,vizinho,"retorno"))
            tem_ciclo = True

        else:
            if descoberta[atual] < descoberta[vizinho]:
                tipo = "avanco"
            else:
                tipo = "cruzamento"

            classificacao_arestas.append((atual,vizinho,tipo))   

    return{
        "inicio": inicio,
        'distancias': distancias,
        'predecessores': predecessores,
        'ordem_visita': ordem_visita,
        'descoberta': descoberta,
        'finalizacao': finalizacao,
        'classificacao_arestas': classificacao_arestas,
        'tem_ciclo': tem_ciclo,} 


def djikstra(vertices, arestas, inicio):
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

        if peso < 0:
            raise ValueError("Dijkstra não aceita pesos negativos.")

        adjacencia[origem].append((destino, peso))

    distancias = {v: float('inf') for v in vertices}
    predecessores = {v: None for v in vertices}
    distancias[inicio] = 0

    visitados = set()
    ordem_visita = []

    while len(visitados) < len(vertices):

        atual = None
        menor_distancia = float('inf')

        # Seleciona o vértice não visitado com menor distância.
        for v in vertices:
            if v not in visitados:
                if distancias[v] < menor_distancia:
                    menor_distancia = distancias[v]
                    atual = v

        # Encerra caso não existam mais vértices alcançáveis.
        if atual is None:
            break

        visitados.add(atual)
        ordem_visita.append(atual)

        # Relaxamento das arestas.
        for vizinho, peso in adjacencia[atual]:
            if vizinho not in visitados:

                novo_custo = distancias[atual] + peso

                if novo_custo < distancias[vizinho]:
                    distancias[vizinho] = novo_custo
                    predecessores[vizinho] = atual

    return {
        'inicio': inicio,
        'distancias': distancias,
        'predecessores': predecessores,
        'ordem_visita': ordem_visita,
    }


def djikstra_heap(vertices, arestas, inicio):
    import heapq
    from itertools import count

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

        if peso < 0:
            raise ValueError("Dijkstra não aceita pesos negativos.")

        adjacencia[origem].append((destino, peso))

    distancias = {v: float('inf') for v in vertices}
    predecessores = {v: None for v in vertices}
    distancias[inicio] = 0

    visitados = set()
    ordem_visita = []

    ordem_vertices = {v: i for i, v in enumerate(vertices)}
    contador = count()
    fila = [(0, ordem_vertices[inicio], next(contador), inicio)]

    while fila:
        distancia_atual, _, _, atual = heapq.heappop(fila)

        if atual in visitados:
            continue

        if distancia_atual > distancias[atual]:
            continue

        visitados.add(atual)
        ordem_visita.append(atual)

        for vizinho, peso in adjacencia[atual]:
            if vizinho not in visitados:
                novo_custo = distancia_atual + peso

                if novo_custo < distancias[vizinho]:
                    distancias[vizinho] = novo_custo
                    predecessores[vizinho] = atual

                    heapq.heappush(
                        fila,
                        (
                            novo_custo,
                            ordem_vertices[vizinho],
                            next(contador),
                            vizinho
                        )
                    )

    return {
        'inicio': inicio,
        'distancias': distancias,
        'predecessores': predecessores,
        'ordem_visita': ordem_visita,
    }
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

    #Teste do Belman-Ford
    resultado = bellman_ford(vertices, arestas, 'A')
    print("---Bellman-Ford---")
    print('Distâncias:', resultado['distancias'])
    print('Caminho até D:', reconstruir_caminho(resultado, 'D'))
    print('Ciclo negativo:', resultado['ciclo_negativo'])

    #Teste do BFS
    resultado_bfs = BFS(vertices, arestas, 'A')
    print("\n---BFS---")
    print('Distâncias:', resultado_bfs['distancias'])
    print('Predecessores:', resultado_bfs['predecessores'])
    print("Caminho até D:", reconstruir_caminho(resultado_bfs, 'D'))

    #Teste do DFS
    resultado_dfs = DFS(vertices, arestas, 'A')
    print("---DFS---")
    print('Distâncias:', resultado_dfs['distancias'])
    print('Predecessores:', resultado_dfs['predecessores'])
    print('Caminho até D:', reconstruir_caminho(resultado_dfs, 'D'))
    print('Ordem de visita:', resultado_dfs['ordem_visita'])
    print('Descoberta:', resultado_dfs['descoberta'])
    print('Finalização:', resultado_dfs['finalizacao'])
    print('Classificação das arestas:', resultado_dfs['classificacao_arestas'])
    print('Tem ciclo:', resultado_dfs['tem_ciclo'])

    #Teste do Dijkstra
    arestas_dijkstra = [
        ('A', 'B', 4),
        ('A', 'C', 3),
        ('C', 'B', 2),
        ('B', 'D', 5),
        ('C', 'D', 6),
    ]

    resultado_djikstra = djikstra(vertices, arestas_dijkstra, 'A')

    print("---Djikstra---")
    print('Distâncias:', resultado_djikstra['distancias'])
    print('Predecessores:', resultado_djikstra['predecessores'])
    print('Ordem de visita:', resultado_djikstra['ordem_visita'])
    print('Caminho até D:', reconstruir_caminho(resultado_djikstra, 'D'))
    

