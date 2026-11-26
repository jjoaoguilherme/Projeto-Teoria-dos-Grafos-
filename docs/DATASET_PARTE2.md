# Dados e construção do grafo — Parte 2

A parte de dados de João está organizada no fluxo:

```text
Baixar o TSV → conferir o arquivo → validar os registros → construir o grafo → exportar a base
```

## 1. Obter e preparar com um comando

Execute na raiz do projeto, com as dependências instaladas:

```powershell
python -m src.parte2.preparar
```

O comando baixa o arquivo apenas se ele ainda não existir, confere seu SHA-256, valida as linhas, constrói o grafo e exporta os arquivos. Não executa os experimentos dos algoritmos.

- Fonte: [SNAP — Reddit Hyperlink Network](https://snap.stanford.edu/data/soc-RedditHyperlinks.html).
- Arquivo aprovado: `soc-redditHyperlinks-title.tsv`, com os links nos títulos.
- A aprovação deste arquivo foi confirmada por João em 24/11/2026.
- O manifesto `data/dataset_parte2/origem_dataset.json` guarda URL, tamanho, colunas e SHA-256. O hash permite conferir se outra pessoa obteve exatamente os mesmos bytes.
- O TSV grande fica fora do Git. O script e o manifesto ficam no projeto para reproduzir sua obtenção.

Também é possível executar as etapas separadamente:

```powershell
python -m src.parte2.obter_dataset
python -m src.parte2.dados --arquivo data/dataset_parte2/soc-redditHyperlinks-title.tsv --construir --out out/parte2
```

## 2. O que cada linha representa

| Campo | Uso |
| --- | --- |
| `SOURCE_SUBREDDIT` | Comunidade de origem do link; vértice de origem. |
| `TARGET_SUBREDDIT` | Comunidade de destino do link; vértice de destino. |
| `LINK_SENTIMENT` | Peso original: `-1` se a referência é negativa; `+1` se é neutra ou positiva. |
| `POST_ID` | Identificação da publicação que criou o link. |
| `TIMESTAMP` | Data e hora registradas para a publicação. |
| `PROPERTIES` | Vetor com 86 atributos textuais, preservado para AVD. |

Cada linha válida gera um arco dirigido da origem para o destino. O programa não cria o arco inverso. Os nomes viram vértices na classe `Grafo`, compartilhada com a Parte 1.

Um caminho é uma sequência de referências entre comunidades. O custo original é a soma dos sinais: número de referências não negativas menos número de referências negativas. Portanto, um custo menor não significa um caminho mais amigável ou uma menor distância física.

Um ciclo negativo volta à comunidade inicial com soma menor que zero; repetir esse circuito reduz matematicamente o custo sem limite. A execução e os casos de Bellman-Ford são responsabilidade da etapa de experimentos.

Os rótulos descrevem publicações, não relações permanentes entre comunidades. As buscas atuais usam a rede agregada e não impõem ordem cronológica aos links; um caminho não comprova transmissão temporal ou causalidade.

## 3. Qualidade e regras de preparação

O relatório conta campos vazios e espaços externos em cada coluna, duplicatas exatas, datas inválidas e vetores `PROPERTIES` que não têm 86 números finitos.

- Origem/destino ausentes, peso diferente de `-1`/`1` e linhas com quantidade errada de campos interrompem a preparação padrão. Não há exclusão silenciosa.
- `invalidos='registrar'` é uma opção explícita da API: mantém as linhas rejeitadas no retorno para revisão. Seu uso não justifica automaticamente apagar dados.
- Datas e vetores auxiliares são sinalizados quando inconsistentes; o leitor não os substitui nem apaga automaticamente registros por esse motivo.
- Os nomes e o peso são normalizados somente na representação do grafo. Os valores originais continuam no TSV e em `atributos_arestas`.
- Arcos paralelos são preservados: publicações diferentes podem citar o mesmo par de comunidades. Laços também são preservados.
- Duplicatas do registro inteiro são contadas separadamente das repetições de pares. Não se presume que dois registros iguais devam ser removidos.

Na execução do arquivo real foram encontrados **54.075 vértices, 571.927 arcos válidos, 61.140 pesos negativos e 510.787 pesos não negativos**. Houve **337.135 repetições de pares**, mas **nenhuma duplicata exata**. Não foram encontrados campos vazios, datas inválidas, vetores inválidos ou registros rejeitados pelas verificações implementadas; todos os registros foram mantidos. Isso descreve o arquivo fornecido, sem afirmar que ele cubra todas as interações do Reddit.

Como a base passa de 500 mil arcos, a equipe precisa justificar a escala e executar a amostragem dos experimentos. O módulo `src/parte2/amostragem.py` já prepara os três tamanhos; essa execução pertence à tarefa de desempenho.

## 4. Arquivos entregues ao grupo

| Arquivo | Conteúdo |
| --- | --- |
| `data/dataset_parte2/soc-redditHyperlinks-title.tsv` | Base original completa, incluindo o vetor `PROPERTIES`. |
| `data/dataset_parte2/origem_dataset.json` | Fonte, aprovação informada, tamanho e hash de identificação. |
| `out/parte2/resumo_dataset.json` | Contagens do grafo, qualidade e proveniência. |
| `out/parte2/arestas_dataset.csv` | Origem, destino e peso de cada arco. |
| `out/parte2/base_avd.csv` | Metadados das linhas válidas e `linha_arquivo`, com origem/destino/peso alinhados ao grafo. |
| `out/parte2/registros_invalidos.json` | Registros rejeitados; lista vazia nesta execução. |
| `docs/preparacao_dataset_parte2.pdf` | Relatório técnico da preparação dos dados. |

A base CSV de AVD evita repetir o vetor textual grande. `PROPERTIES` continua disponível no TSV completo e na API. O número de linha permite localizar o registro original, inclusive quando há múltiplos links da mesma publicação.

## 5. Como os colegas usam no código

```python
from src.parte2.dados import carregar_dataset
from src.graphs.algorithms import BFS

dados = carregar_dataset('data/dataset_parte2/soc-redditHyperlinks-title.tsv')
grafo = dados['grafo']
resultado = BFS(grafo.vertices, grafo.arestas, 'subredditdrama')
```

O retorno de `carregar_dataset()` contém:

- `grafo`: vértices e arcos, preservando direção, pesos, paralelos e laços.
- `atributos_arestas`: atributos completos, na mesma ordem dos arcos, com a linha do TSV. Não indexar somente pelo par origem/destino.
- `registros_invalidos`: registros rejeitados no modo explícito de registro.
- `relatorio`: contagens, escala e qualidade do arquivo.

O Dijkstra precisa receber a versão não negativa dos pesos, definida na etapa de experimentos. O grafo original entregue por este módulo mantém `-1` e `+1`.

## 6. Conferência e apresentação

```powershell
python -m pytest tests/test_dataset_parte2.py tests/test_preparacao_dataset.py -q
python -m src.interface
```

A interface local em `http://127.0.0.1:8765` apresenta a preparação dos dados e os arquivos na biblioteca de entregas, além dos resultados dos experimentos na seção Rede do Reddit. Os relatórios de tempo dos colegas são preservados; preparar os dados não refaz nem substitui suas medições.

Para explicar a sua parte: **baixei o arquivo aprovado, conferi os campos, transformei comunidades em vértices e referências em arcos, preservei os pesos e entreguei a base validada para os algoritmos e para AVD.**
