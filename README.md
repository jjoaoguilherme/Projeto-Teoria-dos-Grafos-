# Projeto de Teoria dos Grafos e AVD

## Ambiente

Python 3.11 ou superior. Execute na raiz:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest -q
```

## Parte 1

Geração reproduzível dos dez mapas, quatro algoritmos, CSVs/JSONs, figuras e interface:

```powershell
.venv\Scripts\python -m src.cli --parte1-completa --out out/parte1
```

Execuções individuais:

```powershell
python -m src.cli --mapa data/mapas/m03_tres_chaves.txt --alg BFS --out out/parte1
python -m src.cli --mapa data/mapas/m05_bonus.txt --alg BELLMAN_FORD --out out/parte1
python -m src.cli --mapa data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out out/parte1
python -m src.cli --mapa data/mapas/m04_esteiras.txt --armadilhas --out out/parte1
python -m src.cli --metricas --out out/parte1
python -m src.cli --mapa data/mapas/m03_tres_chaves.txt --interactive --out out/parte1
```

Use o Python do ambiente virtual caso os comandos `python` acima apontem para outro interpretador.
Abra `out/parte1/labirinto_interativo.html` diretamente no navegador. A interface permite selecionar mapa/algoritmo, importar resultados, avançar manualmente, controlar velocidade, selecionar camada e destacar posições que contêm estados-armadilha. Consulte o tooltip e os CSVs para distinguir estados na mesma casa.

O manual técnico fica em `docs/manual_tecnico_parte1.pdf`, gerado a partir dos resultados por `src/relatorio.py`. Estados não incluem ALVO nas métricas; passos não incluem a ligação virtual. Dijkstra recusa pesos negativos. A geração completa substitui suas tabelas de soluções e classificação DFS, mantendo uma linha por mapa/algoritmo/modo.

## Estrutura

- `src/graphs/`: IO, estados, grafo, algoritmos, métricas e análises.
- `src/main.py`: resolução individual e exportação.
- `src/cli.py`: entrada compatível com os comandos do enunciado.
- `src/solve.py`: orquestração completa; reutiliza a resolução individual.
- `src/viz.py`: figuras e sincronização dos dados do HTML.
- `data/mapas/` e `data/mapas_grupo/`: mapas originais e próprios.
- `tests/`: testes executáveis; referências antigas em docs não são coletadas.
- `out/parte1/`: entregas reproduzíveis e versionadas.

## Parte 2

Leitura e construção do grafo do TSV implementadas em `src/parte2/dados.py`. Uso e contrato para os algoritmos em [docs/DATASET_PARTE2.md](docs/DATASET_PARTE2.md). O dataset real não está disponível nesta cópia; experimentos, obtenção reproduzível dos dados, análises e figuras continuam pendentes. A conclusão da Parte 1 não implica conclusão do projeto interdisciplinar.

## Conferência antes da entrega

O grupo precisa revisar o código, os mapas próprios, o texto e as respostas; preencher nomes e contribuição efetiva em `docs/CONTRIBUICOES.md` e inserir a matriz final no relatório. A declaração oficial deve ser preenchida e assinada por todos, com exportação em `docs/DECLARACAO_IA.pdf`. Esses dados pessoais não são inferidos pelo gerador.

DECLARAÇÃO DE IA: https://docs.google.com/document/d/1sCr8p8y-t-Wttt3G8kXXsjhVLVZ4CMPh/edit?usp=sharing&ouid=112702963052965676955&rtpof=true&sd=true
