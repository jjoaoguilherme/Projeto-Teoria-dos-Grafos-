# Construção do grafo do Reddit

## Entrada

Copiar o TSV aprovado pelo grupo para `data/dataset_parte2/`. O dataset real não está incluído neste repositório; é necessário disponibilizar a fonte aprovada ou um script de download antes da entrega. Este módulo não presume aprovação nem baixa dados automaticamente.

Colunas obrigatórias: SOURCE_SUBREDDIT, TARGET_SUBREDDIT e LINK_SENTIMENT. Outras colunas são preservadas para exploração e AVD.

## Usar no código

```python
from src.parte2.dados import carregar_dataset
from src.graphs.algorithms import BFS

dados = carregar_dataset('data/dataset_parte2/reddit.tsv')
grafo = dados['grafo']
resultado = BFS(grafo.vertices, grafo.arestas, grafo.vertices[0])
```

O exemplo de BFS pressupõe dataset não vazio. `dados` contém:

- `grafo`: instância da classe Grafo compartilhada; nomes das comunidades são os nós.
- `atributos_arestas`: lista alinhada à ordem de `grafo.arestas`, com linha do TSV e todos os atributos originais. Não indexar atributos apenas pelo par origem/destino: o dataset pode ter arcos paralelos.
- `registros_invalidos`: linhas rejeitadas e respectivos motivos, no modo de registro explícito.
- `relatorio`: contagens, quantidade de nós/arcos, repetições, laços e verificações de escala.

## Regras operacionais

Origem e destino seguem as colunas SOURCE/TARGET, sem criar o arco reverso. Espaços externos nos nomes e sentimentos são removidos para construção; os valores originais continuam nos atributos. Cada registro válido gera um arco, mantendo arcos paralelos e laços. Não há agregação automática nem deduplicação silenciosa.

O peso é LINK_SENTIMENT convertido para inteiro, sem transformação: -1 ou 1. Essa decisão operacional não substitui a justificativa do grupo sobre o significado de caminho mínimo e ciclo negativo no domínio. Dijkstra deverá receber uma versão não negativa, com transformação documentada na etapa de experimentos.

O padrão `invalidos='erro'` interrompe a leitura, sem devolver grafo parcial. Com `invalidos='registrar'`, o grafo usa as linhas válidas e devolve todas as linhas rejeitadas para revisão. O grupo precisa justificar qualquer exclusão no relatório. Cabeçalhos ausentes/repetidos e linhas com quantidade errada de campos são detectados.

A conferência de 20 mil arestas conta registros válidos (arcos), não pares únicos. O relatório informa também pares distintos. Acima de 500 mil arcos há indicação para planejar amostragem; este leitor não faz amostragem nem aumenta os dados artificialmente.

## Terminal

```powershell
python -m src.parte2.dados --arquivo data/dataset_parte2/reddit.tsv
python -m src.parte2.dados --arquivo data/dataset_parte2/reddit.tsv --construir --out out/parte2
```

O primeiro comando preserva a verificação inicial de qualidade sem construir o grafo. O segundo constrói o grafo e exporta resumo_dataset.json, arestas_dataset.csv e registros_invalidos.json. A revisão permissiva exige acrescentar `--invalidos registrar` ao segundo comando.

Esses arquivos são preparação dos dados; não substituem parte2_report.json, experimentos, análise, visualizações e aprovação do dataset. Os atributos completos permanecem disponíveis na API em memória; o CSV de arcos é a representação para algoritmos, não um substituto do TSV original para AVD.

## Testes

`python -m pytest tests/test_dataset_parte2.py -q` utiliza TSVs pequenos criados em pastas temporárias, sem tratá-los como o dataset da entrega. Verifica direção, pesos, atributos, paralelismo, laços, erros, exportação e reutilização de BFS e da recusa do Dijkstra.
