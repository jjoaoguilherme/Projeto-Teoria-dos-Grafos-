# Estrutura compartilhada do grafo

`src/graphs/graph.py` define `Grafo`, uma lista de adjacência dirigida ponderada.
A estrutura não contém regras de labirinto. Pode ser usada nas duas partes.

## Contrato para implementar os algoritmos

```python
from src.graphs.graph import Grafo

grafo = Grafo()
grafo.adicionar_arco("A", "B", 4)
grafo.adicionar_arco("A", "C", 2)
grafo.adicionar_vertice("isolado")

# Para BFS, DFS e Dijkstra:
for destino, peso in grafo.vizinhos("A"):
    print(destino, peso)

# Interface do Bellman-Ford existente:
from src.graphs.algorithms import bellman_ford
resultado = bellman_ford(grafo.vertices, grafo.arestas, "A")
```

- `Grafo(vertices=(), arestas=())`: aceita iteráveis de vértices e triplas (origem, destino, peso).
- `adicionar_vertice(vertice)`: preserva nós isolados; não duplica um vértice existente.
- `adicionar_arco(origem, destino, peso)`: cria os extremos se necessário; não espelha o arco.
- `vertices`: lista na ordem de inserção.
- `arestas`: lista de triplas, na ordem global de inserção.
- `adjacencia`: dicionário com listas de pares (destino, peso).
- `vizinhos(vertice)`: lista de pares na ordem de inserção. BFS/DFS podem ignorar o peso.
- `grau_entrada(vertice)` e `grau_saida(vertice)`: contam arcos, inclusive paralelos e laços. Um laço conta uma entrada e uma saída.
- `transposto()`: novo Grafo com os mesmos nós e pesos e arcos invertidos. Não modifica o original.

Vértices precisam ser hashable; rótulos de estados são strings. Pesos são int/float finitos, inclusive negativos e zero. A estrutura aceita laços e arcos paralelos; cabe ao construtor da modelagem decidir quais inserir. Dijkstra ainda deverá recusar pesos negativos.

Consultas devolvem cópias: alterá-las não altera o grafo. Para consultar somente um nó, usar `vizinhos`, evitando copiar toda a adjacência dentro de cada passo da busca. Adicionar vértice/arco e consultar graus são O(1) em média; listar vértices é O(V); listar arestas é O(E); copiar adjacência e transpor são O(V+E); consultar vizinhos copia O(grau de saída).

## Integração com os mapas

`construir_grafo_estados` continua retornando o dicionário anterior, agora com uma chave adicional:

```python
dados = construir_grafo_estados(matriz, inicio)
grafo = dados["grafo"]
inicio = dados["inicio"]
# Exemplo de consulta da entrada que o colega usará nas buscas:
vizinhos = grafo.vizinhos(inicio)
```

As chaves `vertices` e `arestas` continuam disponíveis como cópias para preservar os consumidores antigos. `registros` mantém movimento e símbolo do destino para exportação; `estados` mantém os dados do jogo. As listas de compatibilidade são retratos da construção, não sincronizam mutações posteriores no objeto. Durante as buscas, tratar o grafo construído como entrada sem modificá-lo.

O construtor preserva a ordem N, L, S, O dos movimentos, todos os nós sem saída e ALVO. `main.py` usa as listas do objeto para chamar Bellman-Ford; as exportações mantêm o formato anterior.

Os resultados próprios de BFS/DFS/Dijkstra ainda devem ser combinados com o colega. Este contrato define a entrada compartilhada; não implementa esses algoritmos.

## Verificação

Executar na raiz: `python -m unittest discover -s tests -v`.
Os testes cobrem direção, ordem, nós isolados, transposto, graus, cópias, pesos inválidos, compatibilidade com Bellman-Ford e integração com os oito mapas e a fonte consumível.
