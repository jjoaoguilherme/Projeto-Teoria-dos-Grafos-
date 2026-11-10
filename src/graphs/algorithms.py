"""Algoritmos próprios, a implementar pelo grupo e reutilizar nas duas partes.

BFS: distâncias em arestas, níveis e reconstrução de caminho.
DFS: classificação árvore/retorno/avanço/cruzamento e identificação de ciclos.
Dijkstra: menor custo com pesos não negativos; recusa de qualquer arco negativo.
Bellman-Ford: distâncias, detecção e reconstrução de ciclo negativo alcançável.
Receber grafos, sem depender de símbolos ou arquivos de mapas.
"""

# Bellman-Ford — trecho parcial enviado pelo usuário.
# [IA] Codex – explicações, revisão e organização dos trechos enviados.
# Ainda não constitui uma implementação completa de Bellman-Ford.

vertices = ["A", "B", "C", "D"]

arestas = [
    ("A", "B", 4),
    ("A", "C", 3),
    ("C", "B", -2),
    ("B", "D", 5),
    ("C", "D", 6),
]

distancias = {
    "A": 0,
    "B": float("inf"),
    "C": float("inf"),
    "D": float("inf"),
}

for origem, destino, peso in arestas:
    print(origem, destino, peso)
    novo_custo = distancias[origem] + peso

    if novo_custo < distancias[destino]:
        distancias[destino] = novo_custo
