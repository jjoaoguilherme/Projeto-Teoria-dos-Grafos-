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

### 5.2. Teoria dos Grafos

Serão utilizados os algoritmos já implementados no projeto:

- **BFS:** alcançabilidade, camadas e caminhos com menor número de arestas.
- **DFS:** exploração da rede, classificação de arestas e identificação de ciclos.
- **Dijkstra:** caminhos de menor custo com pesos transformados não negativos.
- **Bellman-Ford:** caminhos com pesos negativos e detecção de ciclos negativos.

### 5.3. Integração das disciplinas

Os resultados obtidos por AVD e pelos algoritmos serão examinados conjuntamente para investigar a pergunta central.

As origens e os pares utilizados nos experimentos serão documentados, assim como os limites de generalização dos resultados.

## 6. Resultados e conclusões

### PREENCHER DPS COM AS CONCLUSÕES 