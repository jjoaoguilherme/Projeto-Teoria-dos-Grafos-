# IA- Chatgpt: estruturação do conteúdo do arquivo no formato markdown

## População e unidade de análise

O cadastro contém a união de origens e destinos do arquivo completo: 54.075 comunidades e 571.927 referências. Nenhum registro é removido por data, grau, sentimento ou seleção de origem. O período observado é 2013–2017; o código não impõe um filtro de anos. Toda BFS utiliza todos os vértices e todas as referências da rede agregada. A comparação opcional sem referências negativas remove apenas essas arestas, preservando todos os vértices, como experimento separado.

O número de referências é o grau com multiplicidade. A estratificação usa `vizinhos_saida`: número de destinos distintos. Não confundir essas duas definições. Uma comunidade apenas destinatária também pertence à população.

## Estratos baseados no cadastro completo

| Destinos distintos | Comunidades N_h | Origens sorteadas n_h | Probabilidade n_h/N_h                        |
|--------------------|-----------------|-----------------------|----------------------------------------------|
| 0                  | 10.380          | 0                     | Não há sorteio: alcance conhecido exatamente |
| 1                  | 24.674          | 122                   | 122/24674                                    |
| 2–10               | 15.570          | 96                    | 96/15570                                     |
| 11–100             | 3.178           | 94                    | 94/3178                                      |
| >100               | 273             | 72                    | 72/273                                       |

Total sorteado: **384**. O estrato zero é um censo estrutural separado, com cobertura 1: a ausência de saídas determina alcance zero de outros vértices. Essas 10.380 comunidades não são apresentadas como buscas executadas nem como uma amostra aleatória.

Os quartis do grau de saída distinto são 1, 1 e 2. Dividir apenas por quartis criaria limites repetidos e pouca distinção da cauda. Preservam-se 0, 1 e 2–10; a faixa antiga >10 é dividida em 11–100 e >100, por ordem de grandeza, sem cortar comunidades de grau extremo. Os quantis e tamanhos reais ficam no plano exportado. Essa divisão é uma escolha descritiva explícita, não uma otimização baseada nos resultados de alcance.

## Dimensionamento antes das buscas

Variável usada para planejar: y_i = quantidade de outras comunidades alcançáveis / (N−1), limitada a [0,1]. As metas configuráveis são margem normal de referência de 10 pontos percentuais por estrato e 5 pontos percentuais para a média global, com referência de 95% (z≈1,96). São metas de planejamento, **não garantias de cobertura** e não metas de precisão para correlações ou distâncias.

Para amostragem aleatória simples sem reposição dentro de cada estrato, usa-se o limite conservador:

`Var(media_h) <= (N_h - n_h) / [4*n_h*(N_h - 1)]`.

Cada estrato não vazio começa com:

`n_h = min(N_h, max(2, ceil(N_h*z²/4 / ((N_h-1)*erro_estrato² + z²/4))))`.

Estratos unitários são censitários. Em seguida, aumenta-se uma unidade de cada vez no estrato com maior redução do limite da variância global ponderada, até satisfazer:

`z * sqrt(soma_h (N_h/N)² * limite_variancia_h) <= erro_global`.

O estrato zero tem variância zero e não exige sorteio. Na base atual, a alocação final é 122/96/94/72, total 384, e a margem normal de planejamento global é aproximadamente 0,04990. O tamanho resulta das tolerâncias declaradas e dos tamanhos reais dos estratos; não é um número escolhido depois de observar os alcances. Outras tolerâncias mudam o tamanho. Não se promete que essa seja a única alocação possível nem a alocação ótima para correlações.

O sorteio é desproporcional, favorecendo a comparação com estratos pequenos. Usa-se `random.Random`, semente principal 42, sementes por estrato `42 + índice*104729`, cadastro ordenado pelo identificador e seleção sem reposição. O índice segue a ordem 0, 1, 2–10, 11–100, >100. A lista efetivamente sorteada é exportada; a versão do Python também é registrada. Reordenar as linhas do cadastro não altera a seleção.

## Exploração e estimação

Para comparar faixas, descrever resultados dentro dos estratos e declarar o desenho desproporcional. Não interpretar a média simples das 384 observações como média de todas as comunidades.

Para a média global de y, usa-se `soma_h (N_h/N)*media_h`, com contribuição exatamente zero do estrato sem saídas. Cada observação sorteada tem probabilidade `n_h/N_h`, peso de expansão `N_h/n_h` e peso na média global `N_h/(N*n_h)`. As origens obrigatórias não sorteadas nunca entram nesse estimador.

O erro padrão estimado usa a variância amostral dentro dos estratos e correção de população finita. Como amostras homogêneas podem produzir erro padrão estimado zero, exporta-se adicionalmente um intervalo conservador de Chebyshev, com margem `sqrt(limite_variancia_global/(1-confianca))`, truncado em [0,1]. A margem conservadora pode superar a meta normal de planejamento. Esse intervalo usa o desenho probabilístico para uma população finita fixa; não pressupõe independência dos valores de alcance entre comunidades conectadas. A seleção entre estratos é separada.

Não são geradas correlações amostrais com alegação de validade populacional. Correlações envolvendo alcance, distâncias ou remoção de referências negativas precisam de tratamento inferencial próprio se o grupo quiser inferência além da exploração. Os pesos não tornam automaticamente uma correlação comum válida. O tamanho foi planejado para a média da fração alcançada, não para efeitos raros, subgrupos não planejados ou força de associação.

As tabelas estruturais, distribuições, séries mensais, sentimentos e correlações entre atributos calculados para todas as comunidades continuam exatas **para o arquivo observado**. Proporções sem denominador continuam indefinidas; correlações globais com valores indefinidos usam as observações em que ambas as variáveis estão definidas (exclusão por par), não zeros inventados. Não são afirmações sobre todo o Reddit fora da coleta nem evidência causal.

## Papéis e execução

1. `amostra_analitica`: somente origens sorteadas.
2. `bfs_dfs_obrigatoria`: `subredditdrama`, `bestof`, `titlegore`.
3. `par_dijkstra`: origens dos cinco pares existentes; incluem `xboxone`, `fitnesscirclejerk`, `jleague`, `bestof`, `subredditdrama`.

Os papéis podem se sobrepor. O registro tem uma linha por origem e lista todas as finalidades. Na seleção atual são 388 origens distintas: 384 sorteadas mais quatro adicionais. Uma origem obrigatória só participa da estimativa se também tiver sido sorteada pelo procedimento independente. Não é acrescentada à amostra por conveniência.

BFS roda uma vez por origem e configuração; DFS apenas nas três obrigatórias; Dijkstra uma vez por origem dos pares, reaproveitando o resultado para seus destinos. As funções são importadas de `src/graphs/algorithms.py`, que não foi modificado. Não há importação, chamada nem dependência obrigatória de `verificar_casos_bf.py`. Os resultados existentes de Bellman-Ford e os relatórios de desempenho ficam preservados.

Há três fases: planejamento (sem buscas), piloto e execução. O piloto mede até três origens já sorteadas por estrato ativo e reutiliza seus resultados. A estimativa operacional usa o maior tempo observado por estrato, multiplicado pela quantidade selecionada, com fator 1,5. É uma previsão operacional aproximada, não benchmark nem intervalo de confiança. O limite padrão de 900 segundos compara essa previsão das BFS da amostra; não é um timeout nem garantia do tempo total. Leitura, exportação, buscas das origens extras, DFS e Dijkstra têm custo adicional. Uma máquina lenta pode ultrapassar a previsão. Se o piloto exceder o limite, a execução é interrompida sem diminuir a amostra; é possível ajustar conscientemente `--limite-segundos`.

Os resultados são salvos por origem. Reexecutar com os mesmos dados, código e parâmetros reaproveita o cache. Se algum desses componentes mudar, o programa exige outra pasta de saída em vez de misturar execuções incompatíveis. A estimação final exige a amostra completa; uma execução interrompida não é publicada como amostra concluída.

## Definições exportadas para AVD

| Campo                                | Definição                                                                                           |
|--------------------------------------|-----------------------------------------------------------------------------------------------------|
| `origem`                             | Identificador da comunidade                                                                         |
| `grau_entrada`, `grau_saida`         | Quantidade de referências, com multiplicidade; aliases de `referencias_entrada/saida`               |
| `vizinhos_entrada`, `vizinhos_saida` | Quantidade de predecessores/sucessores distintos, separadamente; não são a união dos dois conjuntos |
| `proporcao_negativas_entrada/saida`  | Negativas/referências na direção correspondente; vazio se denominador zero                          | 
| `alcance_total`                      | Outros vértices alcançáveis: exclui a origem                                                        |
| `alcancaveis_incluindo_origem`       | Alcance total + 1 nas buscas                                                                        |
| `proporcao_alcance`                  | `alcance_total/(N−1)`; indefinida se N=1                                                            |
| `distancia_media_bfs`                | Média das distâncias finitas aos outros vértices; indefinida quando não há outros alcançáveis       |
| `maior_distancia_bfs`                | Máximo entre distâncias finitas, incluindo a origem; zero quando só ela é alcançável                |
| `estrato`, `N_h`, `n_h`              | Faixa, tamanho populacional e tamanho sorteado                                                      |
| `probabilidade_inclusao`, `peso_amostral`, `peso_media_global` | Parâmetros do desenho amostral                                            |
| `alcance_so_nao_negativas`           | Alcance excluindo origem na rede sem arestas negativas; somente com a opção correspondente          |
| `perda_alcance_remocao_negativas`    | Diferença entre os alcances; experimento descritivo, sem atribuição causal                          |

CSV representa valores indefinidos como célula vazia; JSON usa `null`. O máximo zero e o alcance zero das origens sem saída são definidos matematicamente; a distância média e a proporção de negativas de saída não são substituídas por zero.

`amostra_analitica.csv` e `fontes_resultados.csv` têm exatamente as mesmas 384 linhas analíticas. `origens_experimentos.csv` registra as origens técnicas, inclusive quando sobrepostas à amostra. `censo_grau_zero.csv` contém os 10.380 casos exatos. Não concatenar os três arquivos indiscriminadamente: há sobreposição de papéis. `registro_origens.json` é a referência para deduplicação. Não tratar uma comunidade sem resultado de alcance como alcance zero ao fazer junções com as 54.075 comunidades.

## Limites de caminhos e ciclos

BFS minimiza saltos, independentemente do sentimento. Dijkstra preserva a transformação existente `custo = 2 − sentimento`: +1 vira custo 1 e −1 vira custo 3. Isso é um modelo de custo não negativo declarado, não caminho mínimo na soma original de sentimentos. Os cinco pares são estudos de caso predefinidos e não uma amostra representativa de pares da rede.

A classificação DFS e sua detecção de ciclos referem-se aos vértices alcançados pelas origens obrigatórias. A tabela global de ciclos negativos de duas arestas conta pares com uma referência −1 em cada direção; ela é exata para esse tipo de ciclo, mas não enumera todos os ciclos negativos de comprimentos arbitrários. Evidências anteriores de Bellman-Ford permanecem estudos de caso, com seu próprio escopo. A rede é agregada: caminhos e ciclos não são necessariamente sequências temporalmente realizáveis de publicações.


## Referências metodológicas

- Statistics Canada, *Probability sampling*: https://www150.statcan.gc.ca/n1/edu/power-pouvoir/ch13/prob/5214899-eng.htm
- Statistics Canada, *Survey Methodology*, formulação da variância em amostragem estratificada sem reposição: https://www150.statcan.gc.ca/n1/pub/12-001-x/2015002/article/14249/02-eng.htm

