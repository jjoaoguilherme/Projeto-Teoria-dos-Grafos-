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

Os testes podem ser executados com `python -m unittest discover -s tests -v` ou `python -m pytest`. A CLI implementa somente BELLMAN_FORD por enquanto. As métricas, comparações, outros algoritmos e visualizações do projeto continuam pendentes.
