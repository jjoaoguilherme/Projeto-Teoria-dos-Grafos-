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


O arquivo real foi conferido: 54.075 vértices e 571.927 arcos válidos, sem linhas rejeitadas nas verificações implementadas. Os atributos completos continuam no TSV e na API.

Os experimentos de BFS, DFS, Dijkstra e Bellman-Ford, as medições de desempenho e escalabilidade, a amostragem estratificada, as visualizações de AVD e a discussão acadêmica já possuem resultados registrados no repositório.

## Análise e Visualização de Dados (AVD) — Parte 2

A análise considera toda a rede de referências entre comunidades do Reddit, composta por 54.075 vértices e 571.927 arestas, sem recorte temporal.

As métricas estruturais globais consideram todo o dataset. Para a análise de alcançabilidade, foi utilizada uma amostragem estratificada de 384 origens, com semente 42. As 10.380 comunidades sem conexões de saída foram tratadas separadamente por censo estrutural.

### Preparação dos dados

Caso a base preparada ainda não esteja disponível, execute:

```powershell
python -m src.parte2.preparar
```

### Reprodução da análise

O módulo `estudo_global.py` possui três modos de execução: planejamento, piloto e execução completa.

**1. Planejamento da amostragem:**

```powershell
python -m src.parte2.estudo_global --modo planejar --comparar-nao-negativas --out out/parte2/reproducao_avd
```

**2. Execução do piloto:**

```powershell
python -m src.parte2.estudo_global --modo piloto --comparar-nao-negativas --out out/parte2/reproducao_avd
```

**3. Execução completa:**

```powershell
python -m src.parte2.estudo_global --modo executar --comparar-nao-negativas --out out/parte2/reproducao_avd
```

O piloto estima o custo computacional da análise. O limite padrão é de 900 segundos para a estimativa operacional, podendo ser ajustado conscientemente por meio de `--limite-segundos`.

O parâmetro `--comparar-nao-negativas` habilita a comparação de alcançabilidade entre o grafo original e sua versão sem arestas negativas, necessária para a sexta visualização.

Os comandos utilizam uma pasta separada para preservar os resultados originais versionados.

### Geração das visualizações

Para regenerar as seis visualizações utilizando os resultados já existentes no repositório:

```powershell
python -m src.parte2.figuras_avd
```

As figuras são exportadas nos formatos PNG e SVG em `out/parte2/figuras_avd/`.

Para gerar as figuras a partir de uma nova execução da análise:

```powershell
python -m src.parte2.figuras_avd --base out/parte2/reproducao_avd --out out/parte2/reproducao_avd/figuras
```

### Visualizações exploratórias

1. Distribuição das comunidades por grau de saída.
2. Concentração cumulativa das referências de saída.
3. Sentimento negativo e alcançabilidade por faixa de conectividade.
4. Participação em ciclos negativos de duas arestas.

### Visualizações explanatórias

5. Distribuição da alcançabilidade por faixa de grau.
6. Alcançabilidade antes e depois da remoção de referências negativas.

## Conferência antes da entrega

O grupo precisa revisar o código, os mapas próprios, o texto e as respostas; preencher nomes e contribuição efetiva em `docs/CONTRIBUICOES.md` e inserir a matriz final no relatório. A declaração oficial deve ser preenchida e assinada por todos, com exportação em `docs/DECLARACAO_IA.pdf`. Esses dados pessoais não são inferidos pelo gerador.

DECLARAÇÃO DE IA: https://docs.google.com/document/d/1sCr8p8y-t-Wttt3G8kXXsjhVLVZ4CMPh/edit?usp=sharing&ouid=112702963052965676955&rtpof=true&sd=true

## Páginas de resultados

Abra `out/parte1/entregas_parte1.html` ou `out/parte2/entregas_parte2.html` no navegador e use os botões Parte 1 / Parte 2. A página da Parte 2 apresenta os relatórios existentes, com filtros, tempos individuais, caminhos de Dijkstra, ciclos de Bellman-Ford e os metadados das sessões. Ela informa os diferentes tamanhos dos grafos e os campos que não foram registrados; não substitui a análise AVD ou a validação dos casos contra o dataset.

Atualize ambas as páginas a partir das saídas existentes com `python -m src.entregas`. Para atualizar somente a Parte 2, use `python -m src.entregas --parte 2`. Estilos e tabelas são compartilhados em `src/templates/` e incorporados ao HTML final, que funciona sem servidor. Preserve as pastas do projeto para manter os links dos arquivos e das figuras.

## Gráficos de desempenho da Parte 2

Para desenhar os gráficos de escalabilidade depois de gerar as medições:
`python -m src.parte2.graficos_escalabilidade --arquivo out/parte2/escalabilidade_report.json`.
O comando exige pelo menos três tamanhos por algoritmo, com origem, base,
limite, semente e amostras consistentes. Exporta `escalabilidade.png` e
`escalabilidade.svg` em `out/parte2/graficos/`, com um painel por algoritmo,
médias, desvio-padrão e quantidade de arcos por amostra.

Os gráficos dos tempos já exportados podem ser gerados com
`python -m src.parte2.visualizações --arquivo out/parte2/parte2_report.json`.
As figuras PNG e SVG ficam em `out/parte2/graficos/`, separadas por quantidade
de vértices e arcos. Cada barra representa a média de uma tarefa; os pontos
mostram execuções individuais e as hastes indicam um desvio-padrão amostral.
As escalas são independentes entre figuras. O comando usa Matplotlib e não
executa novamente os algoritmos nem produz interpretação dos resultados.

## Amostragem para escalabilidade da Parte 2

### Execução registrada em 24/11/2026

Foi utilizado recorte induzido de 2.000 vértices da base preparada, com origem
`subredditdrama` e semente 42. Os tamanhos de 10%, 50% e 100% desse recorte
são 200, 1.000 e 2.000 vértices, com 34, 403 e 1.762 arcos. As quantidades
alcançáveis desde a origem são 8, 40 e 108; esses valores constam no relatório.
A escolha limita o custo das cinco execuções de Bellman-Ford com ciclo negativo
na base original de 54.075 vértices e 571.927 arcos. Os percentuais são do recorte.

As 60 execuções foram salvas em `out/parte2/escalabilidade_report.json`; figuras
PNG/SVG em `out/parte2/graficos/escalabilidade.*`. O consolidado preserva as
sessões e inclui os 25 experimentos em `out/parte2/parte2_report.json`.
`python -m src.parte2.consolidar` recompõe esse arquivo a partir das sessões.

`python -m src.parte2.tabela_complexidades` gera
`out/parte2/comparacao_complexidades.csv`, com tempos, desvios, razões e fatores
de referência V+E, V+E+E·log₂(E+1) e V·E+V+E. São funções de referência
assintóticas das implementações, não contagens de operações nem previsões de
segundos. A tabela fornece números para a comparação escrita pelo grupo.

O executor `src/parte2/escalabilidade.py` conecta as amostras ao medidor dos
quatro algoritmos. Recebe o CSV preparado `origem,destino,peso`, a origem e
pelo menos três proporções explícitas. Exemplo de sintaxe:

```powershell
python -m src.parte2.escalabilidade --arquivo out/parte2/arestas_dataset.csv --origem subredditdrama --proporcoes 0.1 0.5 1.0 --out out/parte2/escalabilidade_report.json
```

`--limite-vertices N` define um recorte-base reproduzível de N vértices;
as proporções serão relativas a esse recorte. Sem esse argumento, serão
relativas à base inteira. `--semente` e `--repeticoes` controlam a seleção e
as medições. Dijkstra recebe `2 - LINK_SENTIMENT`; os demais mantêm os pesos
originais. O relatório registra o hash SHA-256 do CSV, o tamanho original,
o limite, as amostras e a transformação. A preparação fica fora do relógio.

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


## Slides
https://canva.link/gr8kd4akjyiq0ez
