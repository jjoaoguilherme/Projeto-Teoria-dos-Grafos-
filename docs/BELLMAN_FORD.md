# Bellman-Ford nos mapas

Integração apoiada por IA (Codex). O algoritmo genérico em `src/graphs/algorithms.py` é reutilizado sem regras de labirinto dentro dele.

Na raiz do projeto, com Python 3.11 ou superior:

```powershell
python -m src.cli --mapa data/mapas/m05_bonus.txt --alg BELLMAN_FORD --out out/parte1
python -m src.cli --mapa data/mapas/m06_fonte.txt --alg BELLMAN_FORD --out out/parte1
python -m src.cli --mapa data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out out/parte1
```

`resolver_mapa` lê a grade, explora os estados alcançáveis, cria arcos ponderados e executa Bellman-Ford até o nó virtual ALVO. A ordem dos movimentos é N, L, S, O. Chaves e consumíveis são conjuntos imutáveis; portas exigem chave; esteiras restringem a saída; em G há somente o arco virtual para ALVO.

O bônus custa -4 na primeira entrada e 1 nas seguintes. A fonte custa -2 em toda entrada; com a opção consumível, custa -2 somente na primeira entrada e 1 nas seguintes. IDs dos bônus seguem a ordem de linha e coluna. No modo consumível, as fontes recebem IDs depois dos bônus, no mesmo campo de consumidos; as posições originais também constam no percurso.

São exportados `arestas_<mapa>.csv`, `resultado_<mapa>.json`, `solucoes.csv` e, quando aplicáveis, `percurso_mXX.json` e `ciclo_negativo_mXX.json`. O modo fonte consumível usa o sufixo `_fonte_consumivel`, evitando sobrescrever a execução normal.

`passos` conta movimentos na grade; `arestas_ate_alvo` inclui a ligação virtual de custo zero. JSON usa custo nulo quando não existe custo finito e informa separadamente se há custo sem limite. O status CICLO_NEGATIVO indica um ciclo alcançável desde S; `ciclo_afeta_alvo` indica se ele também pode alcançar a saída.

Os testes podem ser executados com `python -m unittest discover -s tests -v` ou `python -m pytest`. A CLI da Parte 1 também oferece BFS, DFS e Dijkstra; a Parte 2 reutiliza as mesmas funções genéricas.


## Bellman-Ford — Parte 2 (Reddit)

Os casos definidos em `src/parte2/experimentos.py` são recortes por seleção de arcos reais, não subgrafos induzidos. O peso original LINK_SENTIMENT é mantido (−1 ou +1). A fonte é o arquivo `soc-redditHyperlinks-title.tsv` da coleção SNAP Reddit Hyperlinks. Os registros abaixo foram conferidos nos arquivos versionados `out/parte2/base_avd.csv` (coluna linha_arquivo) e `out/parte2/arestas_dataset.csv`.

| Origem | Destino | Peso | Linha do TSV | POST_ID | TIMESTAMP |
| --- | --- | ---: | ---: | --- | --- |
| subredditdrama | nfl | -1 | 18 | 1u58yq | 2013-12-31 21:59:32 |
| 2007scape | runescape | -1 | 301317 | 3yen02 | 2015-12-27 07:45:17 |
| runescape | 2007scape | -1 | 353054 | 4dxt5o | 2016-04-08 11:52:22 |

No primeiro recorte, a origem subredditdrama alcança nfl pelo único arco selecionado e não existe retorno. No segundo, a origem 2007scape alcança um ciclo negativo formado pelos dois arcos recíprocos, com custo total −2. Outras conexões ou arcos paralelos entre essas comunidades não fazem parte dos casos selecionados. Não se afirma que o grafo completo esteja livre de outros ciclos negativos.

Reprodução e verificação da existência dos arcos:

```powershell
python -m src.parte2.experimentos --bellman-ford --arquivo out/parte2/arestas_dataset.csv
```

A opção também aceita o TSV original. O JSON inclui os arcos selecionados, o hash da base efetivamente verificada e o ciclo detectado, se houver. Cinco repetições são feitas por caso. A procedência acrescentada aos resultados históricos foi verificada posteriormente, preservando as medições originais.
