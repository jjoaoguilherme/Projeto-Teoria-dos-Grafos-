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

O caderno complementar `out/parte1/entregas_parte1.html` reúne as figuras, graus, rankings, multiplicidade, métricas por camada, comparação de modelagens, classificação DFS, ciclos negativos e links dos arquivos. Ele abre diretamente no navegador e usa os resultados exportados; a animação e as métricas globais continuam no labirinto interativo. A geração completa também atualiza esse caderno. Para atualizar apenas a página a partir das saídas existentes, execute `python -m src.entregas --out out/parte1`. Mantenha a página junto dos demais arquivos do projeto para que as figuras e os links funcionem.

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

A preparação do dataset aprovado está em `src/parte2/dados.py`, `obter_dataset.py` e `preparar.py`. Obtenção, regras e uso estão em [docs/DATASET_PARTE2.md](docs/DATASET_PARTE2.md).

```powershell
python -m src.parte2.preparar
```

Esse comando baixa o TSV oficial se necessário, confere o hash, valida os registros, constrói o grafo e exporta `resumo_dataset.json`, `arestas_dataset.csv`, `base_avd.csv` e `registros_invalidos.json`. Também gera `docs/preparacao_dataset_parte2.pdf` e atualiza a página da Parte 2. O TSV grande não é versionado; o script e o manifesto `data/dataset_parte2/origem_dataset.json` permitem reproduzir a obtenção.

O arquivo real foi conferido: 54.075 vértices e 571.927 arcos válidos, sem linhas rejeitadas nas verificações implementadas. Os atributos completos continuam no TSV e na API. Os relatórios de BFS/DFS, Dijkstra e dos dois casos pequenos de Bellman-Ford já estão integrados. A documentação/verificação dos recortes dos experimentos, os registros detalhados das buscas, a execução nos três tamanhos, as análises e as figuras finais são as próximas tarefas das demais etapas.

## Conferência antes da entrega

O grupo precisa revisar o código, os mapas próprios, o texto e as respostas; preencher nomes e contribuição efetiva em `docs/CONTRIBUICOES.md` e inserir a matriz final no relatório. A declaração oficial deve ser preenchida e assinada por todos, com exportação em `docs/DECLARACAO_IA.pdf`. Esses dados pessoais não são inferidos pelo gerador.

DECLARAÇÃO DE IA: https://docs.google.com/document/d/1sCr8p8y-t-Wttt3G8kXXsjhVLVZ4CMPh/edit?usp=sharing&ouid=112702963052965676955&rtpof=true&sd=true

## Páginas de resultados

Abra `out/parte1/entregas_parte1.html` ou `out/parte2/entregas_parte2.html` no navegador e use os botões Parte 1 / Parte 2. A página da Parte 2 apresenta os relatórios existentes, com filtros, tempos individuais, caminhos de Dijkstra, ciclos de Bellman-Ford e os metadados das sessões. Ela informa os diferentes tamanhos dos grafos e os campos que não foram registrados; não substitui a análise AVD ou a validação dos casos contra o dataset.

Atualize ambas as páginas a partir das saídas existentes com `python -m src.entregas`. Para atualizar somente a Parte 2, use `python -m src.entregas --parte 2`. Estilos e tabelas são compartilhados em `src/templates/` e incorporados ao HTML final, que funciona sem servidor. Preserve as pastas do projeto para manter os links dos arquivos e das figuras.

## Amostragem para escalabilidade da Parte 2

`src/parte2/amostragem.py` prepara subgrafos induzidos por 10%, 50% e 100% dos vértices, com semente configurável (42 por padrão). As amostras são aninhadas, preservam direção, pesos, laços, arcos paralelos e a ordem original de inserção. As quantidades são arredondadas para cima; proporções que resultem no mesmo tamanho são recusadas. Não há alteração do grafo original.

```python
from src.parte2.amostragem import criar_amostras
from src.parte2.experimentos import medir_algoritmo, exportar_relatorio

# grafo_preparado deve ser um Grafo construído a partir da base do grupo.
# origem deve ser uma das fontes definidas para o experimento.
amostras = criar_amostras(grafo_preparado, semente=42, obrigatorios=[origem])
experimentos = []
for item in amostras:
    grafo = item['grafo']
    experimentos.append(medir_algoritmo(
        'BFS', grafo.vertices, grafo.arestas, origem,
        identificacao={'amostragem': item['metadados']}))
exportar_relatorio(experimentos)
```

Os metadados incluem semente, método, proporções solicitadas/reais, tamanhos originais/obtidos e vértices selecionados/obrigatórios. A reprodução exige os mesmos dados, ordem de entrada e runtime. A amostragem ocorre fora da medição do algoritmo. A lista de obrigatórios condiciona a seleção e deve caber na menor amostra.
