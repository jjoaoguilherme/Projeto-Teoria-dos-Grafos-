# Uso de IA para ajuda de estruturação do conteúdo no Markdown

# Plano de Análise — Parte 2

## 1. Tema da pesquisa

**Estrutura, conectividade e sentimento das referências entre comunidades do Reddit (2013–2017).**

## 2. Pergunta central

Como a distribuição das conexões e dos sentimentos das referências se relaciona com a alcançabilidade, os caminhos de menor custo e os ciclos na rede de comunidades do Reddit entre 2013 e 2017?

## 3. Objetivo da análise

Investigar as características estruturais da rede de comunidades do Reddit e examinar como as conexões e os sentimentos das referências se relacionam com propriedades estudadas em Teoria dos Grafos.

A pesquisa combinará técnicas de Análise e Visualização de Dados (AVD) com algoritmos de grafos para examinar diferentes aspectos da mesma rede.

## 4. Dataset utilizado

- **Nome:** Reddit Hyperlink Network — links nos títulos.
- **Fonte:** Stanford Network Analysis Project (SNAP).
- **Arquivo:** `soc-redditHyperlinks-title.tsv`.
- **Período da pesquisa:** dezembro de 2013 a abril de 2017.
- **Representação:** grafo dirigido e ponderado.
- **Vértices:** comunidades (subreddits).
- **Arestas:** referências de uma comunidade a outra.
- **Pesos originais:** -1 (referência negativa) ou +1 (neutra ou positiva).

A investigação utilizará a rede completa dentro do período selecionado, sem restringir a análise a comunidades específicas.

## 5. Metodologia prevista

### 5.1. Análise e Visualização de Dados

Serão investigados quatro aspectos:

- **Estrutural:** organização da rede, graus, densidade e conectividade.
- **Distribucional:** distribuição das referências, sentimentos e graus.
- **Relacional:** relações entre características das comunidades.
- **Outliers:** identificação e avaliação de valores extremos.


### 5.2. Amostragem

As métricas estruturais globais foram calculadas considerando todo o dataset.

Para a análise de alcançabilidade, foi utilizada uma amostragem estratificada com semente 42, considerando o número de destinos distintos de cada comunidade.

| Grau de saída distinto | População  | Origens sorteadas |
|------------------------|-----------:|------------------:|
| 0                      | 10.380     | Censo estrutural  |
| 1                      | 24.674     | 122               |
| 2 a 10                 | 15.570     | 96                |
| 11 a 100               | 3.178      | 94                |
| Acima de 100           | 273        | 72                |
| **Total**              | **54.075** | **384**           |

As comunidades de grau de saída zero foram tratadas separadamente, pois sua alcançabilidade de outros vértices é conhecida pela própria estrutura do grafo.

### 5.3. Teoria dos Grafos

Serão utilizados os algoritmos já implementados no projeto:

- **BFS:** alcançabilidade, camadas e caminhos com menor número de arestas.
- **DFS:** exploração da rede, classificação de arestas e identificação de ciclos.
- **Dijkstra:** caminhos de menor custo com pesos transformados não negativos.
- **Bellman-Ford:** caminhos com pesos negativos e detecção de ciclos negativos.

### 5.4. Integração das disciplinas

Os resultados obtidos por AVD e pelos algoritmos serão examinados conjuntamente para investigar a pergunta central.

A documentação dos experimentos e da amostragem estabelece os limites de generalização dos resultados.

## 6. Visualizações produzidas

### 6.1. Visualizações exploratórias

1. Distribuição das comunidades por grau de saída.
2. Concentração cumulativa das referências de saída.
3. Sentimento negativo e alcançabilidade por estrato.
4. Participação em ciclos negativos de duas arestas.

### 6.2. Visualizações explanatórias

5. Distribuição da alcançabilidade por faixa de grau.
6. Alcançabilidade antes e depois da remoção de referências negativas.

## 7. Resultados e conclusões

Os resultados da análise estão disponíveis no arquivo: "Discussão acadêmica.pdf"